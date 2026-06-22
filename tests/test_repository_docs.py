import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class RepositoryDocsTests(unittest.TestCase):
    def test_release_surfaces_describe_repo_scope_and_current_package_coverage(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        zh_readme = (ROOT / "docs" / "zh" / "README.zh-CN.md").read_text(encoding="utf-8")
        skill_matrix = (ROOT / "docs" / "usage" / "skill-matrix.md").read_text(
            encoding="utf-8"
        )
        releases_readme = (ROOT / "docs" / "releases" / "README.md").read_text(
            encoding="utf-8"
        )
        zh_releases_readme = (
            ROOT / "docs" / "zh" / "releases" / "README.zh-CN.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Latest formal package release notes", readme)
        self.assertIn("production-code-quality-review v0.1.6", readme)
        self.assertIn("[Skill Matrix](docs/usage/skill-matrix.md)", readme)
        self.assertIn("It currently ships six Codex skills", readme)

        skills = [
            "best-project-memory",
            "evidence-driven-bugfix",
            "little-lighthouse-blog-publisher",
            "production-code-quality-review",
            "split-image-assets",
            "zero-to-website-design",
        ]
        for skill in skills:
            self.assertIn(f"`{skill}`", readme)
            self.assertIn(f"`{skill}`", skill_matrix)

        self.assertIn("Evidence-Driven Bugfix", readme)
        self.assertIn("Little Lighthouse Blog Publisher", readme)
        self.assertIn("Split Image Assets", readme)

        usage_guides = [
            "docs/usage/best-project-memory.md",
            "docs/usage/evidence-driven-bugfix.md",
            "docs/usage/little-lighthouse-blog-publisher.md",
            "docs/usage/split-image-assets.md",
            "docs/usage/zero-to-website-design.md",
        ]
        for guide in usage_guides:
            self.assertIn(guide, readme)
            self.assertIn(guide, releases_readme)

        self.assertIn("cp -R evidence-driven-bugfix ~/.agents/skills/", readme)
        self.assertIn("cp -R split-image-assets ~/.agents/skills/", readme)
        self.assertIn(
            "python3 -m unittest discover little-lighthouse-blog-publisher/tests -v",
            readme,
        )
        self.assertIn(
            "python3 -m unittest discover split-image-assets/tests -v",
            readme,
        )

        self.assertIn(
            "formal versioned release notes currently ship for `production-code-quality-review`",
            releases_readme,
        )
        self.assertIn(
            "`best-project-memory`, `evidence-driven-bugfix`, `little-lighthouse-blog-publisher`, `split-image-assets`, and `zero-to-website-design` currently publish their ongoing delivery history",
            releases_readme,
        )

        self.assertIn("# Skill Matrix", skill_matrix)
        self.assertIn(
            "| Skill | Best when you need | Core outputs | Common pairings | Avoid when |",
            skill_matrix,
        )
        self.assertIn("docs/usage/evidence-driven-bugfix.md", skill_matrix)
        self.assertIn("docs/usage/split-image-assets.md", skill_matrix)
        self.assertIn("## Common Pairings", skill_matrix)
        self.assertIn("## Fast Routing Prompts", skill_matrix)

        for expected in [
            "`evidence-driven-bugfix`",
            "`little-lighthouse-blog-publisher`",
            "`split-image-assets`",
            "docs/usage/evidence-driven-bugfix.md",
            "docs/usage/little-lighthouse-blog-publisher.md",
            "docs/usage/split-image-assets.md",
            "docs/usage/skill-matrix.md",
        ]:
            self.assertIn(expected, zh_readme)

        for expected in [
            "docs/usage/evidence-driven-bugfix.md",
            "docs/usage/little-lighthouse-blog-publisher.md",
            "docs/usage/split-image-assets.md",
        ]:
            self.assertIn(expected, zh_releases_readme)


if __name__ == "__main__":
    unittest.main()
