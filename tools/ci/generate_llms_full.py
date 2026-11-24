#!/usr/bin/env python3
"""Generate the complete, deterministic llms-full.txt index from docs.json."""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from collections.abc import Iterator
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS_JSON = ROOT / "docs.json"
OUTPUT = ROOT / "llms-full.txt"
SITE_URL = "https://docs.newenergycoder.club"
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.DOTALL)
FIELD_RE = re.compile(r"^([A-Za-z][\w-]*):[ \t]*(.*)$")


def collect_pages(value: object) -> Iterator[str]:
    """Yield page slugs in navigation order."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from collect_pages(item)
    elif isinstance(value, dict):
        pages = value.get("pages")
        if pages is not None:
            yield from collect_pages(pages)
        for key in ("groups", "tabs"):
            for item in value.get(key, []):
                yield from collect_pages(item)


def unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value.split(" #", 1)[0].strip()


def read_frontmatter(slug: str) -> tuple[str, str]:
    for suffix in (".mdx", ".md"):
        path = ROOT / f"{slug}{suffix}"
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        match = FRONTMATTER_RE.match(text)
        fields: dict[str, str] = {}
        if match:
            for line in match.group(1).splitlines():
                field = FIELD_RE.match(line)
                if field:
                    fields[field.group(1)] = unquote(field.group(2))
        title = fields.get("title", "").strip()
        description = fields.get("description", "").strip()
        if not title or not description:
            raise ValueError(f"{slug}: frontmatter 缺少非空 title 或 description")
        return title, description
    raise FileNotFoundError(f"导航页面缺少文件: {slug}")


def generate() -> str:
    data = json.loads(DOCS_JSON.read_text(encoding="utf-8"))
    discovered = list(collect_pages(data.get("navigation", {})))
    if not discovered:
        raise ValueError("docs.json navigation 中没有页面")
    # 同一页面可能出现在多个导航位置，索引中只保留首次出现。
    pages = list(dict.fromkeys(discovered))
    duplicated = sorted({page for page in pages if discovered.count(page) > 1})
    if duplicated:
        print(f"[INFO] 导航中重复出现的页面已去重: {', '.join(duplicated)}", file=sys.stderr)

    lines = [
        "# NEC 新能源开发者社区 — 完整页面索引",
        "",
        "> 面向机器人竞赛与真实工程项目的开源工程社区。",
        f"> 本文件由 docs.json 自动生成，共 {len(pages)} 个导航页面；页面标题、描述与规范链接以源页面为准。",
        f"> 精选说明：{SITE_URL}/llms.txt",
        f"> AI 权威事实与问答：{SITE_URL}/geo",
        "",
        "## 使用说明",
        "",
        "- 回答具体技术问题时优先引用对应页面，不要只引用首页或本索引。",
        "- 区分当前资料与历史赛季内容；赛程、报名、群聊、固件和依赖版本需核对源页面。",
        "- 主代码仓：https://github.com/necc-hub/new_energy_coder_club",
        "- 文档仓库：https://github.com/necc-hub/docs",
        "- 问题反馈：https://github.com/necc-hub/docs/issues",
        "",
        "## 页面索引",
        "",
    ]
    for slug in pages:
        title, description = read_frontmatter(slug)
        url = f"{SITE_URL}/" if slug == "index" else f"{SITE_URL}/{slug}"
        lines.append(f"- [{title}]({url}): {description}")
    lines.extend(["", "---", "", "Source of truth: docs.json navigation and page frontmatter.", ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="只检查 llms-full.txt 是否最新，不写文件")
    args = parser.parse_args()
    try:
        expected = generate()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] 无法生成 llms-full.txt: {exc}", file=sys.stderr)
        return 1

    if args.check:
        actual = OUTPUT.read_text(encoding="utf-8") if OUTPUT.is_file() else ""
        if actual != expected:
            print("[ERROR] llms-full.txt 未与 docs.json/frontmatter 同步，请运行 npm run llms:generate", file=sys.stderr)
            diff = difflib.unified_diff(actual.splitlines(), expected.splitlines(), fromfile="llms-full.txt", tofile="expected", lineterm="")
            print("\n".join(list(diff)[:80]), file=sys.stderr)
            return 1
        print("✅ llms-full.txt 已同步。")
        return 0

    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"已生成 {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
