"""Packaging contract for the obsidian-doc-router skill folder.

Covers the two-tier router awareness shipped 2026-11-11: SKILL.md frontmatter,
the OpenAI agent interface manifest, usage-guide cross links, and the router
budget/two-tier instructions agents rely on.
"""
import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL = ROOT / "obsidian-doc-router"

FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def skill_text() -> str:
    return (SKILL / "SKILL.md").read_text(encoding="utf-8")


class SkillPackageTests(unittest.TestCase):
    def test_frontmatter_has_name_and_description_only(self):
        m = FRONTMATTER.match(skill_text())
        self.assertIsNotNone(m, "SKILL.md must open with a frontmatter block")
        block = m.group(1)
        self.assertRegex(block, r"(?m)^name: obsidian-doc-router\s*$")
        self.assertIn("description:", block)
        for key in ("display_name", "default_prompt"):
            self.assertNotIn(f"{key}:", block)

    def test_description_keeps_pre_flight_gate_trigger_words(self):
        m = FRONTMATTER.match(skill_text())
        desc = m.group(1).split("description:", 1)[1].lower()
        for token in ("pre-flight", "00.moc/ai-doc-router.md", "sop"):
            self.assertIn(token, desc)

    def test_skill_documents_two_tier_router(self):
        body = skill_text()
        self.assertIn("00.MOC/routers/", body)
        self.assertIn("doc-lookup", body)
        self.assertIn("生产变更速记", body)
        self.assertIn("≤60 行", body)
        self.assertIn("≤40000 B", body)
        self.assertIn("scan-doc-governance --strict", body)

    def test_skill_documents_metadata_triplet(self):
        body = skill_text()
        for key in ("doc_type", "authority", "lifecycle", "canonical_for", "scope"):
            self.assertIn(f"{key}:", body)

    def test_agent_interface_manifest(self):
        path = SKILL / "agents" / "openai.yaml"
        self.assertTrue(path.exists(), "agents/openai.yaml is required")
        body = path.read_text(encoding="utf-8")
        self.assertIn("interface:", body)
        self.assertIn('display_name: "Obsidian Doc Router"', body)
        self.assertIn("$obsidian-doc-router", body)

    def test_usage_guide_links_shared_navigation(self):
        body = (ROOT / "docs" / "usage" / "obsidian-doc-router.md").read_text(encoding="utf-8")
        self.assertIn("skill-matrix.md", body)
        self.assertIn("quickstart.md", body)
        self.assertIn("00.MOC/routers/", body)


if __name__ == "__main__":
    unittest.main()
