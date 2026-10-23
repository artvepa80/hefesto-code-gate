"""Tests for scripts/public_audit.py. Trigger phrases are built by
concatenation so this file does not trip the audit itself."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from public_audit import content_hits, path_hits  # noqa: E402

PRIV = "pri" + "vate"
LP = "landing" + "-page/"


class PathRules(unittest.TestCase):
    def test_blocked_paths(self):
        for rel in ["docs/" + "worklog/2026-10-22.md", "notes/team-" + "worklog.md",
                    "HAND" + "OFF.md", "docs/" + "handoffs/x.md", "Work_" + "Log.txt",
                    LP + "index.html", "site/" + LP + "logo.png"]:
            self.assertTrue(path_hits(rel), rel)

    def test_allowed_paths(self):
        for rel in ["README.md", "docs/telemetry-notice.md", "CHANGELOG.md",
                    "plugins/hefesto-code-gate/assets/logo.png"]:
            self.assertEqual(path_hits(rel), [], rel)


class ContentRules(unittest.TestCase):
    def test_blocked_phrases(self):
        for text in [f"See the {PRIV} repo for details", f"Opened {PRIV} PR #12",
                     f"{PRIV.title()} pull request", f"{PRIV}-repository", f"copy {LP}hero.svg"]:
            self.assertTrue(content_hits("README.md", text, []), text)

    def test_clean_text(self):
        for text in ["Privacy policy: https://example.com/privacy",
                     "The repository is public.", "Open a pull request."]:
            self.assertEqual(content_hits("README.md", text, []), [], text)

    def test_private_pattern_not_echoed(self):
        out = content_hits("README.md", "codename-x here", ["codename-x"])
        self.assertEqual(len(out), 1)
        self.assertNotIn("codename-x", out[0])


if __name__ == "__main__":
    unittest.main()
