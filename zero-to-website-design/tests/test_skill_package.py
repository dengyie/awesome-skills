import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class ZeroToWebsiteDesignPackageTests(unittest.TestCase):
    def test_required_skill_files_are_present(self):
        required_paths = [
            ROOT / "SKILL.md",
            ROOT / "agents" / "openai.yaml",
            ROOT / "references" / "intake-brief.md",
            ROOT / "references" / "concept-generation.md",
            ROOT / "references" / "visual-provenance.md",
            ROOT / "references" / "design-system-docs.md",
            ROOT / "references" / "implementation-map.md",
            ROOT / "references" / "route-acceptance.md",
            ROOT / "references" / "visual-qa-checklist.md",
            ROOT / "references" / "historical-mock-pass.md",
            ROOT / "references" / "framework-first-delivery.md",
            ROOT / "references" / "production-delivery.md",
            ROOT / "assets" / "templates" / "design-system-master.md",
            ROOT / "assets" / "templates" / "implementation-plan.md",
            ROOT / "assets" / "templates" / "asset-and-data-spec.md",
            ROOT / "assets" / "templates" / "page-spec.md",
            ROOT / "assets" / "templates" / "visual-source-map.md",
            ROOT / "assets" / "templates" / "visual-source-inventory.md",
            ROOT / "assets" / "templates" / "mock-asset-pass.md",
            ROOT / "assets" / "templates" / "qa-report.md",
        ]

        missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]

        self.assertEqual(missing, [])

    def test_skill_frontmatter_and_metadata_are_aligned(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"---\n(.*?)\n---", skill_text, re.DOTALL)
        self.assertIsNotNone(match)
        frontmatter = match.group(1)

        self.assertIn("name: zero-to-website-design", frontmatter)
        self.assertIn("complete website", frontmatter)
        self.assertIn("reference images", frontmatter)

        metadata = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Zero-To-Website Design"', metadata)
        self.assertIn("short_description:", metadata)
        self.assertIn("website", metadata.lower())
        self.assertIn("$zero-to-website-design", metadata)
        self.assertIn("allow_implicit_invocation: true", metadata)

    def test_references_named_by_skill_exist(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        reference_paths = sorted(set(re.findall(r"`(references/[^`]+\.md)`", skill_text)))

        self.assertGreaterEqual(len(reference_paths), 8)
        missing = [path for path in reference_paths if not (ROOT / path).exists()]

        self.assertEqual(missing, [])

    def test_templates_named_by_skill_exist(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        template_paths = sorted(set(re.findall(r"`(assets/templates/[^`]+\.md)`", skill_text)))

        self.assertEqual(len(template_paths), 8)
        missing = [path for path in template_paths if not (ROOT / path).exists()]

        self.assertEqual(missing, [])

    def test_visual_provenance_contract_names_statuses_and_sources(self):
        provenance = (ROOT / "references" / "visual-provenance.md").read_text(
            encoding="utf-8"
        )

        for status in [
            "exploratory",
            "candidate",
            "approved-direction",
            "binding-route",
            "temporary-binding",
            "obsolete",
        ]:
            self.assertIn(f"`{status}`", provenance)

        for source_method in [
            "user-upload",
            "imagegen",
            "figma-export",
            "live-screenshot",
            "manual-design",
            "existing-project-mockup",
            "existing-project-screenshot",
            "other",
        ]:
            self.assertIn(f"`{source_method}`", provenance)

    def test_skill_and_usage_docs_include_historical_mock_and_framework_ready_language(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        usage_text = (ROOT.parent / "docs" / "usage" / "zero-to-website-design.md").read_text(
            encoding="utf-8"
        )
        route_acceptance = (ROOT / "references" / "route-acceptance.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("historical mock", skill_text.lower())
        self.assertIn("framework-first", skill_text.lower())
        self.assertIn("Historical-Mock Path", usage_text)
        self.assertIn("temporary-binding", usage_text)
        self.assertIn("Framework Ready", route_acceptance)
        self.assertIn("Visual Delivery Ready", route_acceptance)

    def test_templates_are_scaffolds_without_todo_markers(self):
        templates_dir = ROOT / "assets" / "templates"
        template_files = sorted(templates_dir.glob("*.md"))

        self.assertEqual(len(template_files), 8)
        for template in template_files:
            text = template.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("# "), template.name)
            self.assertNotIn("TODO", text.upper(), template.name)


if __name__ == "__main__":
    unittest.main()
