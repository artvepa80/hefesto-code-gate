"""Tests for scripts/gen_manifests.py OpenAI package output."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from gen_manifests import build, checks  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
SRC = json.loads((REPO / "hefesto-plugin.source.json").read_text())


class OpenAIPackage(unittest.TestCase):
    def test_mcp_json_and_review_fields(self):
        files = build(SRC)
        mcp = json.loads(files["plugins/hefesto-code-gate/mcp.json"])
        servers = mcp["mcpServers"]
        self.assertEqual(mcp["$schema"], "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json")
        self.assertEqual(list(servers), ["hefesto-core"])
        entry = servers["hefesto-core"]
        self.assertEqual(entry["type"], "streamable-http")
        self.assertEqual(entry["url"], "https://hefestoai.narapallc.com/api/mcp-core")
        self.assertEqual(entry["extensions"]["com.openai"]["auth"]["type"], "none")

        plugin = json.loads(files["plugins/hefesto-code-gate/plugin.json"])
        interface = plugin["extensions"]["com.openai"]["interface"]
        review = plugin["extensions"]["com.openai"]["review"]
        self.assertEqual(interface["termsOfServiceURL"], "https://hefestoai.narapallc.com/terms")
        self.assertFalse(interface["displayName"].endswith("MCP"))
        self.assertEqual(len(review["test_cases"]["positive"]), 5)
        self.assertEqual(len(review["test_cases"]["negative"]), 3)
        self.assertIs(review["commerce"], False)

    def test_source_checks_pass(self):
        self.assertEqual(checks(SRC, None), [])


if __name__ == "__main__":
    unittest.main()
