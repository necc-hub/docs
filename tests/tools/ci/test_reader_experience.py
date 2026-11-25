from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]


class ReaderExperienceTests(unittest.TestCase):
    def test_maintenance_script_is_loaded_by_mintlify(self):
        self.assertTrue((ROOT / "scripts/page-maintenance.js").is_file())
        script = (ROOT / "scripts/page-maintenance.js").read_text(encoding="utf-8")
        self.assertIn('repository + "/edit/main/"', script)
        self.assertIn('repository + "/issues/new?"', script)
        self.assertIn("requestAnimationFrame", script)
        self.assertIn("MutationObserver", script)

    def test_mobile_navigation_has_accessible_group_disclosure(self):
        script = (ROOT / "scripts/page-maintenance.js").read_text(encoding="utf-8")
        css = (ROOT / "style.css").read_text(encoding="utf-8")
        self.assertIn("data-mobile-nav-toggle", script)
        self.assertIn("aria-expanded", script)
        self.assertIn("mobile-nav-collapsed", css)

    def test_auxiliary_text_has_readable_contrast(self):
        css = (ROOT / "style.css").read_text(encoding="utf-8")
        tertiary = css.split("--text-tertiary:", 1)[1].split(";", 1)[0].strip()
        background = css.split("--bg-page:", 1)[1].split(";", 1)[0].strip()

        def luminance(color):
            channels = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
            channels = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
            return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]

        contrast = (max(luminance(tertiary), luminance(background)) + 0.05) / (min(luminance(tertiary), luminance(background)) + 0.05)
        self.assertGreaterEqual(contrast, 4.5)


if __name__ == "__main__":
    unittest.main()
