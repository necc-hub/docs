from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.ci.page_insights import build_record, iter_mdx_files, render_report, resolve_slug_from_rel_path


OUTPUT_DIR = ROOT / "generated"
OVERRIDES_PATH = OUTPUT_DIR / "page-insights.overrides.json"


def load_overrides(path: Path) -> dict:
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8").strip()
    return json.loads(raw or "{}")


def generate_outputs(
    docs_root: Path,
    output_dir: Path,
    overrides_path: Path,
    check: bool = False,
) -> list[str]:
    overrides = load_overrides(overrides_path)
    records: dict[str, dict] = {}

    for mdx_path in iter_mdx_files(docs_root):
        rel_path = mdx_path.relative_to(docs_root).as_posix()
        slug = resolve_slug_from_rel_path(rel_path)
        record = build_record(rel_path=rel_path, text=mdx_path.read_text(encoding="utf-8"))
        record.update(overrides.get(slug, {}))
        records[slug] = record

    data_module_path = docs_root / "snippets" / "page-insights-data.jsx"
    serialized = json.dumps(records, ensure_ascii=False, indent=2)
    report_path = output_dir / "page-insights-report.md"
    report = render_report(records)
    outputs = {
        output_dir / "page-insights.json": serialized + "\n",
        data_module_path: f"export const insights = {serialized};\n",
        report_path: report,
    }
    stale = [
        path.relative_to(docs_root).as_posix()
        for path, content in outputs.items()
        if not path.is_file() or path.read_text(encoding="utf-8") != content
    ]
    if not check:
        output_dir.mkdir(parents=True, exist_ok=True)
        data_module_path.parent.mkdir(parents=True, exist_ok=True)
        for path, content in outputs.items():
            path.write_text(content, encoding="utf-8")
    return stale


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Report stale outputs without modifying files")
    args = parser.parse_args()
    if not args.check:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        if not OVERRIDES_PATH.exists():
            OVERRIDES_PATH.write_text("{}\n", encoding="utf-8")
    stale = generate_outputs(ROOT, OUTPUT_DIR, OVERRIDES_PATH, check=args.check)
    if stale and args.check:
        print("Run npm run insights:generate to update: " + ", ".join(stale), file=sys.stderr)
        return 1
    if args.check:
        print("Page insights are up to date")
    else:
        print("Generated page insights at generated/page-insights.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
