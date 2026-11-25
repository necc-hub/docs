import json
import os
from pathlib import Path
import subprocess
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from tools.ci.page_insights import iter_mdx_files


class MaintenanceWorkflowTests(unittest.TestCase):
    def test_page_order_is_stable_for_ascii_case_and_unicode(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("zebra.mdx", "ROADMAP.mdx", "a-guide.mdx", "技能.mdx"):
                (root / name).write_text("", encoding="utf-8")

            paths = [path.relative_to(root).as_posix() for path in iter_mdx_files(root)]

            self.assertEqual(paths, sorted(paths, key=str.casefold))

    def test_python_wrapper_works_when_only_python3_is_available(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "python3").symlink_to(shutil.which("python3"))
            result = subprocess.run(
                [
                    shutil.which("node"),
                    "tools/ci/run_python.mjs",
                    "-c",
                    'print("python3-ok")',
                ],
                cwd=ROOT,
                env={**os.environ, "PATH": directory},
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("python3-ok", result.stdout)

    def test_check_scripts_use_a_python_interpreter_available_on_macos(self):
        scripts = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["scripts"]
        for name, command in scripts.items():
            if name.startswith("insights:") or name in ("check", "check:docs", "check:generated", "test"):
                self.assertNotIn(
                    "python tools/",
                    command,
                    f"{name} must not require an unversioned python executable",
                )

    def test_contributing_workflow_uses_main_without_git_flow(self):
        text = (ROOT / "contributing/workflow.mdx").read_text(encoding="utf-8")
        self.assertNotIn("我们采用 **Git Flow**", text)
        self.assertNotIn("git checkout develop", text)
        self.assertNotIn("master (主分支", text)
        self.assertIn("`main`", text)
        self.assertIn("npm run check", text)

    def test_local_development_uses_locked_local_dependencies(self):
        text = (ROOT / "development.mdx").read_text(encoding="utf-8")
        self.assertIn("npm ci", text)
        self.assertIn("npm run dev", text)
        self.assertIn("npm run check", text)
        self.assertNotIn("npm install -g", text)
        self.assertNotIn("Node.js 18+", text)

    def test_all_maintenance_guides_share_the_same_entrypoints(self):
        guides = (
            "README.md",
            "AGENTS.md",
            ".kimi/skills/nec-docs-maintainer/SKILL.md",
            ".kimi/skills/nec-docs-maintainer/references/ci-checks.md",
            ".kimi/skills/nec-docs-maintainer/references/project-structure.md",
            "contributing.mdx",
            "contributing/workflow.mdx",
            "development.mdx",
        )
        for guide in guides:
            with self.subTest(guide=guide):
                text = (ROOT / guide).read_text(encoding="utf-8")
                self.assertNotIn("npm install -g", text)
                self.assertNotIn("python tools/", text)
                self.assertNotIn("我们采用 **Git Flow**", text)
                self.assertNotIn("git checkout develop", text)


if __name__ == "__main__":
    unittest.main()
