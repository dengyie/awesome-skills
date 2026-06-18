import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class LittleLighthouseBlogPublisherPackageTests(unittest.TestCase):
    def test_required_skill_files_are_present(self):
        required_paths = [
            ROOT / "SKILL.md",
            ROOT / "agents" / "openai.yaml",
            ROOT / "references" / "interaction-state-machine.md",
            ROOT / "references" / "package-contract.md",
            ROOT / "references" / "editorial-guidelines.md",
            ROOT / "references" / "asset-guidelines.md",
            ROOT / "references" / "verification-checklist.md",
            ROOT / "references" / "commit-and-memory.md",
        ]

        missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
        self.assertEqual(missing, [])

    def test_skill_frontmatter_and_metadata_are_aligned(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"---\n(.*?)\n---", skill_text, re.DOTALL)
        self.assertIsNotNone(match)
        frontmatter = match.group(1)

        self.assertIn("name: little-lighthouse-blog-publisher", frontmatter)
        self.assertIn("Publish, draft, update, validate, or repair", frontmatter)
        self.assertIn("write files only after explicit final confirmation", skill_text)
        self.assertIn("node scripts/verify-blog-package.mjs <slug>", skill_text)

        metadata = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Little Lighthouse Blog Publisher"', metadata)
        self.assertIn("$little-lighthouse-blog-publisher", metadata)

    def test_references_named_by_skill_exist(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        reference_paths = sorted(set(re.findall(r"`(references/[^`]+\.md)`", skill_text)))

        self.assertEqual(len(reference_paths), 6)
        missing = [path for path in reference_paths if not (ROOT / path).exists()]
        self.assertEqual(missing, [])

    def test_core_publication_contract_is_documented(self):
        package_contract = (ROOT / "references" / "package-contract.md").read_text(
            encoding="utf-8"
        )
        interaction = (ROOT / "references" / "interaction-state-machine.md").read_text(
            encoding="utf-8"
        )
        assets = (ROOT / "references" / "asset-guidelines.md").read_text(encoding="utf-8")
        verification = (ROOT / "references" / "verification-checklist.md").read_text(
            encoding="utf-8"
        )
        commit = (ROOT / "references" / "commit-and-memory.md").read_text(encoding="utf-8")

        for expected in [
            "content/posts/<slug>.md",
            "content/posts/<slug>.meta.json",
            "public/posts/<slug>/thumbnail.png",
            "`published: false` means local draft only",
        ]:
            self.assertIn(expected, package_contract)

        self.assertIn("Do not treat an old or vague", interaction)
        self.assertIn("Never overwrite existing assets without explicit confirmation", assets)
        self.assertIn("node scripts/verify-blog-package.mjs <slug>", verification)
        self.assertIn("production-code-quality-review", commit)


if __name__ == "__main__":
    unittest.main()
