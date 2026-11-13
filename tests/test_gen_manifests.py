"""Tests for scripts/gen_manifests.py OpenAI package output."""
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

import jsonschema

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from gen_manifests import build, checks, codex_zip, mcp_manifest  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
SRC = json.loads((REPO / "hefesto-plugin.source.json").read_text())
PLUGIN = REPO / "plugins" / "hefesto-code-gate"
# Vendored from https://agent-plugins.org/schemas/1.0.0/mcp.schema.json
# (Agent Plugins 1.0.0). See tests/fixtures/mcp.schema.source.txt.
MCP_SCHEMA = json.loads((REPO / "tests" / "fixtures" / "mcp.schema.json").read_text())


class OpenAIPackage(unittest.TestCase):
    def test_mcp_json_validates_against_official_schema(self):
        mcp = mcp_manifest(SRC)
        jsonschema.validate(mcp, MCP_SCHEMA)
        servers = mcp["mcpServers"]
        self.assertEqual(mcp["$schema"], "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json")
        self.assertEqual(list(servers), ["hefesto-core"])
        entry = servers["hefesto-core"]
        self.assertEqual(entry["type"], "streamable-http")
        self.assertEqual(entry["url"], "https://hefestoai.narapallc.com/api/mcp-core")
        self.assertNotIn("extensions", entry)
        self.assertNotIn("auth", entry)

    def test_mcp_json_is_not_in_plugin_folder_or_generated_files(self):
        files = build(SRC)
        self.assertNotIn("plugins/hefesto-code-gate/mcp.json", files)
        self.assertFalse((PLUGIN / "mcp.json").exists())

    def test_codex_zip_injects_valid_mcp_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "plugin.zip"
            codex_zip(SRC, out)
            with zipfile.ZipFile(out) as z:
                self.assertIn("mcp.json", z.namelist())
                mcp = json.loads(z.read("mcp.json"))
            jsonschema.validate(mcp, MCP_SCHEMA)
            self.assertNotIn("extensions", mcp["mcpServers"]["hefesto-core"])

    def test_claude_manifest_and_plugin_readme_have_no_remote_server(self):
        claude = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text())
        blob = json.dumps(claude)
        self.assertNotIn("mcp-core", blob)
        self.assertNotIn("mcpServers", blob)
        self.assertNotIn("termsOfServiceURL", blob)
        readme = (PLUGIN / "README.md").read_text()
        self.assertNotIn("mcp-core", readme)
        self.assertNotIn("hosted analyzer", readme)

    def test_openai_review_fields(self):
        files = build(SRC)
        plugin = json.loads(files["plugins/hefesto-code-gate/plugin.json"])
        interface = plugin["extensions"]["com.openai"]["interface"]
        review = plugin["extensions"]["com.openai"]["review"]
        self.assertEqual(interface["termsOfServiceURL"], "https://hefestoai.narapallc.com/terms")
        self.assertFalse(interface["displayName"].endswith("MCP"))
        self.assertIn("Analyze this file with Hefesto and tell me what is real.",
                      interface["defaultPrompt"])
        self.assertEqual(len(review["test_cases"]["positive"]), 5)
        self.assertEqual(len(review["test_cases"]["negative"]), 3)
        self.assertIs(review["commerce"], False)
        for case in review["test_cases"]["negative"]:
            self.assertTrue(case.get("description"))
            self.assertTrue(case.get("expected_behavior"))

    def test_source_checks_pass(self):
        self.assertEqual(checks(SRC, None), [])


if __name__ == "__main__":
    unittest.main()
