from __future__ import annotations

import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


DATA_IMPORT_LINE = 'import { insights } from "/snippets/page-insights-data.jsx";'
IMPORT_LINE = 'import { PageInsights } from "/snippets/page-insights.jsx";'
FRONTMATTER_RE = re.compile(r"^(---\n[\s\S]*?\n---\n)", re.MULTILINE)
DATA_IMPORT_RE = re.compile(
    r'^import\s+\{\s*insights\s*\}\s+from\s+"/(?:generated/page-insights|snippets/page-insights-data)\.(?:js|jsx)";\n?',
    re.MULTILINE,
)
SNIPPET_IMPORT_RE = re.compile(
    r'^import\s+\{\s*PageInsights\s*\}\s+from\s+"/snippets/page-insights\.jsx";\n?',
    re.MULTILINE,
)
PAGE_INSIGHTS_MOUNT_RE = re.compile(
    r"^\s*<PageInsights(?:\s+[^>]*)?\s*/>\s*$",
    re.MULTILINE,
)


def sync_page_insights_mounts(docs_root: Path, insights_path: Path) -> None:
    insights = json.loads(insights_path.read_text(encoding="utf-8"))
    article_paths = {
        f"{slug}.mdx"
        for slug, entry in insights.items()
        if entry.get("pageKind") == "article"
    }

    for path in docs_root.rglob("*.mdx"):
        rel_path = path.relative_to(docs_root).as_posix()
        text = path.read_text(encoding="utf-8")
        wants_mount = rel_path in article_paths
        updated = text

        if wants_mount:
            match = FRONTMATTER_RE.match(updated)
            if not match:
                raise ValueError(f"Article is missing frontmatter: {rel_path}")
            mount_line = f'<PageInsights slug="{rel_path[:-4]}" insights={{insights}} />'
            updated = DATA_IMPORT_RE.sub("", updated)
            updated = SNIPPET_IMPORT_RE.sub("", updated)
            updated = PAGE_INSIGHTS_MOUNT_RE.sub("", updated)
            updated = (
                updated[:match.end()]
                + "\n"
                + DATA_IMPORT_LINE
                + "\n"
                + IMPORT_LINE
                + "\n\n"
                + mount_line
                + "\n\n"
                + updated[match.end():].lstrip("\n")
            )
        else:
            updated = DATA_IMPORT_RE.sub("", updated)
            updated = SNIPPET_IMPORT_RE.sub("", updated)
            updated = PAGE_INSIGHTS_MOUNT_RE.sub("", updated)

        if updated != text:
            path.write_text(updated, encoding="utf-8")


def main() -> int:
    sync_page_insights_mounts(ROOT, ROOT / "generated" / "page-insights.json")
    print("Synchronized page insight mounts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
