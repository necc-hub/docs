import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools.ci.check_docs import check_page_insights_artifacts
from tools.ci.generate_page_insights import generate_outputs
from tools.ci.inject_page_insights import sync_page_insights_mounts
from tools.ci.page_insights import (
    build_summary,
    classify_page_kind,
    compute_length_band,
    compute_reading_minutes,
    extract_page_features,
    parse_frontmatter_and_body,
)


class PageInsightsTests(unittest.TestCase):
    def setUp(self):
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        self.tmp_path = Path(temporary_directory.name)

    def test_parse_frontmatter_and_body_splits_mdx_document(self):
        text = """---
title: "Community"
description: "About page"
toc: false
---

## Intro

NEC community intro paragraph.
"""

        frontmatter, body = parse_frontmatter_and_body(text)

        self.assertEqual(frontmatter["title"], "Community")
        self.assertEqual(frontmatter["description"], "About page")
        self.assertIn("## Intro", body)

    def test_classify_page_kind_marks_article_when_text_dominates(self):
        text = """---
title: "关于 NEC 社区"
description: "intro"
toc: false
---

## 社区起源

NEC 社区成立于常州工学院，围绕机器人竞赛沉淀工程实践经验。

## 核心价值

我们强调开源、新手友好与工程实践。
"""

        features = extract_page_features("community/about.mdx", text)

        self.assertEqual(classify_page_kind(features), "article")

    def test_classify_page_kind_marks_index_when_cards_dominate(self):
        text = """---
title: "NEC 10 日集训"
description: "overview"
---

<CardGroup cols={2}>
  <Card title="Day 1" href="/training/day01-onboarding">Desc</Card>
  <Card title="Day 2" href="/training/day02-mechanical-basics">Desc</Card>
</CardGroup>
"""

        features = extract_page_features("training/index.mdx", text)

        self.assertEqual(classify_page_kind(features), "index")

    def test_classify_page_kind_marks_index_for_card_heavy_index_page(self):
        text = """---
title: "NEC 10 日集训"
description: "overview"
---

本集训面向 NEC 2027 赛季新成员，帮助你建立机器人竞赛所需的全局认知与基础实践能力。

## 十日学习地图

<CardGroup cols={2}>
  <Card title="Day 1" href="/training/day01-onboarding">Desc</Card>
  <Card title="Day 2" href="/training/day02-mechanical-basics">Desc</Card>
</CardGroup>
"""

        features = extract_page_features("training/index.mdx", text)

        self.assertEqual(classify_page_kind(features), "index")

    def test_classify_page_kind_marks_stub_for_tiny_page(self):
        text = """---
title: "维护者"
description: "short page"
---

联系人列表。
"""

        features = extract_page_features("community/maintainers.mdx", text)

        self.assertEqual(classify_page_kind(features), "stub")

    def test_compute_reading_minutes_weights_code_and_tables_lightly(self):
        minutes = compute_reading_minutes(
            text_chars=900,
            english_words=60,
            code_chars=300,
            table_chars=240,
        )

        self.assertEqual(minutes, 4)

    def test_compute_length_band_marks_short_and_long(self):
        self.assertEqual(compute_length_band(text_chars=120, reading_minutes=1), "short")
        self.assertEqual(compute_length_band(text_chars=5200, reading_minutes=16), "long")
        self.assertEqual(compute_length_band(text_chars=900, reading_minutes=3), "normal")

    def test_build_summary_uses_frontmatter_description(self):
        summary = build_summary(
            {
                "title": "Claude Code",
                "description": "在 NEC 文档站点中使用 Claude Code 进行 AI 辅助写作与维护",
            }
        )

        self.assertEqual(summary, "在 NEC 文档站点中使用 Claude Code 进行 AI 辅助写作与维护")

    def test_build_summary_trims_frontmatter_description(self):
        summary = build_summary({"description": "  NEC 社区文档摘要。\n"})

        self.assertEqual(summary, "NEC 社区文档摘要。")

    def test_resolve_slug_from_rel_path_removes_mdx_suffix(self):
        from tools.ci.page_insights import resolve_slug_from_rel_path

        self.assertEqual(resolve_slug_from_rel_path("community/about.mdx"), "community/about")

    def test_generate_outputs_writes_json_and_report(self):
        docs_root = self.tmp_path / "docs"
        docs_root.mkdir()
        (docs_root / "community").mkdir()
        (docs_root / "community" / "about.mdx").write_text(
            """---
title: "关于 NEC 社区"
description: "intro"
---

## 社区起源

NEC 社区面向机器人竞赛与真实工程项目。

## 社区支持

社区提供文档和答疑支持。
""",
            encoding="utf-8",
        )
        output_dir = docs_root / "generated"
        overrides_path = output_dir / "page-insights.overrides.json"
        output_dir.mkdir()
        overrides_path.write_text("{}", encoding="utf-8")

        generate_outputs(docs_root=docs_root, output_dir=output_dir, overrides_path=overrides_path)

        data = json.loads((output_dir / "page-insights.json").read_text(encoding="utf-8"))
        data_module = (docs_root / "snippets" / "page-insights-data.jsx").read_text(encoding="utf-8")
        report = (output_dir / "page-insights-report.md").read_text(encoding="utf-8")

        self.assertTrue(data_module.startswith("export const insights = {"))
        self.assertNotIn("export default", data_module)
        self.assertEqual(data["community/about"]["pageKind"], "article")
        self.assertGreaterEqual(data["community/about"]["readingMinutes"], 1)
        self.assertIn("## 超长页", report)
        self.assertIn("community/about", report)

    def test_generate_outputs_applies_manual_override(self):
        docs_root = self.tmp_path / "docs"
        docs_root.mkdir()
        (docs_root / "page.mdx").write_text(
            """---
title: "Page"
description: "desc"
---

This page is short.
""",
            encoding="utf-8",
        )
        output_dir = docs_root / "generated"
        output_dir.mkdir()
        overrides_path = output_dir / "page-insights.overrides.json"
        overrides_path.write_text(
            '{"page":{"pageKind":"article","summary":"人工摘要","hideReadingTime":true}}',
            encoding="utf-8",
        )

        generate_outputs(docs_root=docs_root, output_dir=output_dir, overrides_path=overrides_path)

        data = json.loads((output_dir / "page-insights.json").read_text(encoding="utf-8"))
        self.assertEqual(data["page"]["summary"], "人工摘要")
        self.assertIs(data["page"]["hideReadingTime"], True)
        self.assertEqual(data["page"]["pageKind"], "article")

    def test_sync_page_insights_mounts_injects_article_and_skips_index(self):
        docs_root = self.tmp_path / "docs"
        docs_root.mkdir()
        generated = docs_root / "generated"
        generated.mkdir()
        (generated / "page-insights.json").write_text(
            """
{
  "community/about": {"pageKind": "article"},
  "training/index": {"pageKind": "index"}
}
""".strip(),
            encoding="utf-8",
        )
        community = docs_root / "community"
        training = docs_root / "training"
        community.mkdir()
        training.mkdir()
        (community / "about.mdx").write_text(
            """---
title: "About"
description: "desc"
---

## Intro

Body
""",
            encoding="utf-8",
        )
        (training / "index.mdx").write_text(
            """---
title: "Index"
description: "desc"
---

<CardGroup cols={2}></CardGroup>
""",
            encoding="utf-8",
        )

        sync_page_insights_mounts(docs_root, generated / "page-insights.json")

        article_text = (community / "about.mdx").read_text(encoding="utf-8")
        index_text = (training / "index.mdx").read_text(encoding="utf-8")

        self.assertIn('import { insights } from "/snippets/page-insights-data.jsx";', article_text)
        self.assertIn('import { PageInsights } from "/snippets/page-insights.jsx";', article_text)
        self.assertIn('<PageInsights slug="community/about" insights={insights} />', article_text)
        self.assertIn('---\n\nimport { insights }', article_text)
        self.assertIn(' />\n\n## Intro', article_text)
        self.assertNotIn("page-insights.js", index_text)
        self.assertNotIn("page-insights.jsx", index_text)

    def test_generate_outputs_check_reports_stale_files_without_writing(self):
        docs_root = self.tmp_path / "docs"
        docs_root.mkdir()
        page = docs_root / "page.mdx"
        page.write_text(
            """---
title: "Page"
description: "first"
---

## First section

Substantive body text for this article, with enough detail to classify as an article.

## Second section

More substantive body text for the second section of this article.
""",
            encoding="utf-8",
        )
        output_dir = docs_root / "generated"
        output_dir.mkdir()
        overrides_path = output_dir / "page-insights.overrides.json"
        overrides_path.write_text("{}", encoding="utf-8")
        generate_outputs(docs_root=docs_root, output_dir=output_dir, overrides_path=overrides_path)
        original_json = (output_dir / "page-insights.json").read_text(encoding="utf-8")
        page.write_text(page.read_text(encoding="utf-8").replace('"first"', '"second"'), encoding="utf-8")

        stale = generate_outputs(
            docs_root=docs_root,
            output_dir=output_dir,
            overrides_path=overrides_path,
            check=True,
        )

        self.assertIn("generated/page-insights.json", stale)
        self.assertEqual((output_dir / "page-insights.json").read_text(encoding="utf-8"), original_json)

    def test_sync_page_insights_check_reports_missing_mount_without_writing(self):
        docs_root = self.tmp_path / "docs"
        docs_root.mkdir()
        generated = docs_root / "generated"
        generated.mkdir()
        (generated / "page-insights.json").write_text(
            '{"page": {"pageKind": "article"}}',
            encoding="utf-8",
        )
        page = docs_root / "page.mdx"
        original_text = """---
title: "Page"
description: "desc"
---

## Heading

Body
"""
        page.write_text(original_text, encoding="utf-8")

        stale = sync_page_insights_mounts(
            docs_root,
            generated / "page-insights.json",
            check=True,
        )

        self.assertEqual(stale, ["page.mdx"])
        self.assertEqual(page.read_text(encoding="utf-8"), original_text)

    def test_generate_command_exits_successfully_after_writing_outdated_outputs(self):
        from tools.ci import generate_page_insights

        docs_root = self.tmp_path / "docs"
        docs_root.mkdir()
        (docs_root / "page.mdx").write_text(
            """---
title: "Page"
description: "desc"
---

## First section

Substantive body text for this article, long enough to keep a normal page kind.

## Second section

More substantive body text for this article.
""",
            encoding="utf-8",
        )
        output_dir = docs_root / "generated"
        overrides_path = output_dir / "page-insights.overrides.json"

        with (
            patch.object(generate_page_insights, "ROOT", docs_root),
            patch.object(generate_page_insights, "OUTPUT_DIR", output_dir),
            patch.object(generate_page_insights, "OVERRIDES_PATH", overrides_path),
            patch.object(sys, "argv", ["generate_page_insights.py"]),
        ):
            exit_code = generate_page_insights.main()

        self.assertEqual(exit_code, 0)
        self.assertTrue((output_dir / "page-insights.json").is_file())

    def test_sync_command_exits_successfully_after_writing_missing_mounts(self):
        from tools.ci import inject_page_insights

        docs_root = self.tmp_path / "docs"
        docs_root.mkdir()
        generated = docs_root / "generated"
        generated.mkdir()
        (generated / "page-insights.json").write_text(
            '{"page": {"pageKind": "article"}}',
            encoding="utf-8",
        )
        page = docs_root / "page.mdx"
        page.write_text(
            """---
title: "Page"
description: "desc"
---

## Heading

Body
""",
            encoding="utf-8",
        )

        with (
            patch.object(inject_page_insights, "ROOT", docs_root),
            patch.object(sys, "argv", ["inject_page_insights.py"]),
        ):
            exit_code = inject_page_insights.main()

        self.assertEqual(exit_code, 0)
        self.assertIn("<PageInsights", page.read_text(encoding="utf-8"))

    def test_check_page_insights_artifacts_requires_generated_files(self):
        errors = check_page_insights_artifacts(self.tmp_path)

        self.assertIn("缺少生成文件: generated/page-insights.json", errors)
        self.assertIn("缺少生成文件: snippets/page-insights-data.jsx", errors)
        self.assertIn("缺少生成文件: generated/page-insights-report.md", errors)
        self.assertIn("缺少生成文件: generated/page-insights.overrides.json", errors)


if __name__ == "__main__":
    unittest.main()
