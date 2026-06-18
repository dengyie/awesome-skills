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
        self.assertIn(
            "formal versioned release notes currently ship for `production-code-quality-review`",
            releases_readme,
        )
        self.assertIn(
            "`best-project-memory` and `zero-to-website-design` currently publish their ongoing delivery history",
            releases_readme,
        )
        self.assertIn("docs/usage/best-project-memory.md", releases_readme)
        self.assertIn("docs/usage/zero-to-website-design.md", releases_readme)
        self.assertIn("# Skill Matrix", skill_matrix)
        self.assertIn("| Skill | Best when you need | Core outputs | Common pairings | Avoid when |", skill_matrix)
        self.assertIn("`best-project-memory`", skill_matrix)
        self.assertIn("`little-lighthouse-blog-publisher`", skill_matrix)
        self.assertIn("`production-code-quality-review`", skill_matrix)
        self.assertIn("`zero-to-website-design`", skill_matrix)
        self.assertIn("## Common Pairings", skill_matrix)
        self.assertIn("## Fast Routing Prompts", skill_matrix)
        self.assertIn("Little Lighthouse Blog Publisher", readme)
        self.assertIn("docs/usage/little-lighthouse-blog-publisher.md", readme)

        self.assertIn(
            "当前正式按版本维护的发布说明主要覆盖 `production-code-quality-review`", zh_readme
        )
        self.assertIn("Skill Matrix（英文技能总览）", zh_readme)
        self.assertIn("优先看 [`docs/usage/skill-matrix.md`](../usage/skill-matrix.md)", zh_readme)
        self.assertIn(
            "这个目录是 `awesome-skills` 仓库级发布说明入口的中文镜像", zh_releases_readme
        )
        self.assertIn(
            "正式的版本化发布说明目前只覆盖 `production-code-quality-review`",
            zh_releases_readme,
        )
        self.assertIn(
            "`best-project-memory` 和 `zero-to-website-design` 当前主要通过 usage 文档与 `docs/dev/` 阶段文档记录演进",
            zh_releases_readme,
        )


if __name__ == "__main__":
    unittest.main()
