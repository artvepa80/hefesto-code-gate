"""Tests for scripts/check_plugin_file_types.py."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from check_plugin_file_types import collect_findings  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
PLUGIN = REPO / "plugins" / "hefesto-code-gate"


class LivePlugin(unittest.TestCase):
    def test_plugin_directory_passes(self):
        self.assertEqual(collect_findings(PLUGIN), [])


class SyntheticTree(unittest.TestCase):
    def _write(self, root: Path, rel: str, data: bytes) -> None:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def test_ico_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root, "favicon.ico", b"\x00\x00\x01\x00")
            hits = collect_findings(root)
            self.assertTrue(any("favicon.ico" in h and "not accepted" in h for h in hits), hits)

    def test_svg_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root, "SKILL.md", b"---\nname: x\n---\n")
            self._write(root, "assets/logo.svg", b"<svg></svg>")
            hits = collect_findings(root)
            self.assertTrue(any("logo.svg" in h and "not accepted" in h for h in hits), hits)

    def test_shell_script_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root, "scripts/run.sh", b"#!/bin/sh\necho hi\n")
            hits = collect_findings(root)
            self.assertTrue(any("run.sh" in h for h in hits), hits)

    def test_shebang_on_text_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root, "notes.txt", b"#!/bin/sh\necho hi\n")
            hits = collect_findings(root)
            self.assertTrue(any("shebang" in h for h in hits), hits)

    def test_package_manager_yaml_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root, "pnpm-workspace.yaml", b"packages: []\n")
            hits = collect_findings(root)
            self.assertTrue(any("package-manager" in h for h in hits), hits)

    def test_license_and_markdown_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root, "LICENSE", b"MIT\n")
            self._write(root, "README.md", b"# Hi\n")
            self._write(root, "data.json", b"{}\n")
            self._write(root, "ok.yaml", b"a: 1\n")
            self.assertEqual(collect_findings(root), [])

    def test_nul_in_text_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root, "notes.md", b"hello\x00world")
            hits = collect_findings(root)
            self.assertTrue(any("NUL" in h for h in hits), hits)


if __name__ == "__main__":
    unittest.main()
