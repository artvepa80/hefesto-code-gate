"""SKILL.md frontmatter must parse with yaml.safe_load as a single-line string."""
import re
import unittest
from pathlib import Path

import yaml

PLUGIN = Path(__file__).resolve().parent.parent / "plugins" / "hefesto-code-gate"


class SkillFrontmatter(unittest.TestCase):
    def test_each_description_is_a_single_line_string(self):
        skills = sorted((PLUGIN / "skills").glob("*/SKILL.md"))
        self.assertEqual(len(skills), 5)
        for path in skills:
            with self.subTest(skill=path.parent.name):
                text = path.read_text()
                match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
                self.assertIsNotNone(match, path)
                data = yaml.safe_load(match.group(1))
                desc = data["description"]
                self.assertIsInstance(desc, str, path)
                self.assertNotIn("\n", desc, path)
                raw = next(ln for ln in match.group(1).splitlines()
                           if ln.startswith("description:"))
                value = raw.split(":", 1)[1].strip()
                self.assertFalse(value.startswith((">-", ">", "|")), raw)
