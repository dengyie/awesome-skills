import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]

SKILLS = sorted(
    path.name
    for path in ROOT.iterdir()
    if path.is_dir() and (path / "SKILL.md").exists()
)

USAGE_GUIDES = [
    "docs/usage/best-project-memory.md",
    "docs/usage/evidence-driven-bugfix.md",
    "docs/usage/little-lighthouse-blog-publisher.md",
    "docs/usage/split-image-assets.md",
    "docs/usage/zero-to-website-design.md",
]

LANDING_FILES = [
    ROOT / "README.md",
    ROOT / "docs" / "usage" / "quickstart.md",
    ROOT / "docs" / "usage" / "skill-matrix.md",
    ROOT / "docs" / "zh" / "README.zh-CN.md",
    ROOT / "docs" / "zh" / "quickstart.zh-CN.md",
]

LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def _iter_repo_relative_links(path: pathlib.Path) -> list[pathlib.Path]:
    links = []
    for raw_target in LINK_PATTERN.findall(_read(path)):
        target = raw_target.strip().strip("<>")
        if (
            not target
            or target.startswith("#")
            or "://" in target
            or target.startswith("mailto:")
        ):
            continue
        target = target.split("#", 1)[0]
        links.append((path.parent / target).resolve())
    return links


class RepositoryDocsTests(unittest.TestCase):
    def test_readme_is_a_short_landing_page(self):
        readme = _read(ROOT / "README.md")

        self.assertIn("## Choose a Skill", readme)
        self.assertIn("[Skill Matrix](docs/usage/skill-matrix.md)", readme)
        self.assertIn("[Quickstart](docs/usage/quickstart.md)", readme)
        self.assertIn("[中文说明](docs/zh/README.zh-CN.md)", readme)
        self.assertIn("## Recommended Starting Points", readme)
        self.assertIn("## Install", readme)
        self.assertIn("## Docs", readme)
        self.assertIn("## For Maintainers", readme)

        self.assertNotIn("Latest formal package release notes", readme)
        self.assertNotIn("Review context collection", readme)
        self.assertNotIn("cp -R evidence-driven-bugfix ~/.agents/skills/", readme)

        for skill in SKILLS:
            self.assertIn(f"`{skill}`", readme)

    def test_quickstart_is_repository_level(self):
        quickstart = _read(ROOT / "docs" / "usage" / "quickstart.md")

        self.assertIn("# Quickstart", quickstart)
        self.assertIn("Install one skill", quickstart)
        self.assertIn("[Skill Matrix](skill-matrix.md)", quickstart)
        self.assertIn("[Troubleshooting](troubleshooting.md)", quickstart)

        self.assertNotIn("production-code-quality-review is designed", quickstart)
        self.assertNotIn("collect-review-context.py", quickstart)
        self.assertNotIn("review-entrypoint.py", quickstart)

    def test_zh_quickstart_is_repository_level(self):
        zh_quickstart = _read(ROOT / "docs" / "zh" / "quickstart.zh-CN.md")

        self.assertIn("# 快速开始", zh_quickstart)
        self.assertIn("../usage/skill-matrix.md", zh_quickstart)
        self.assertIn("cp -R <skill-folder> ~/.agents/skills/", zh_quickstart)

        self.assertNotIn("production-code-quality-review/scripts/install-local-skill.sh", zh_quickstart)
        self.assertNotIn("collect-review-context.py", zh_quickstart)
        self.assertNotIn("review-entrypoint.py", zh_quickstart)

    def test_skill_matrix_uses_shared_routing_fields(self):
        skill_matrix = _read(ROOT / "docs" / "usage" / "skill-matrix.md")

        self.assertIn("# Skill Matrix", skill_matrix)
        self.assertIn("| Skill | When to use | Best for | Avoid when | Typical outputs | Docs |", skill_matrix)
        self.assertIn("## Pick By Problem Type", skill_matrix)
        self.assertIn("## Prompt Starters", skill_matrix)

        for skill in SKILLS:
            self.assertIn(f"`{skill}`", skill_matrix)

        for guide in USAGE_GUIDES:
            self.assertIn(guide, skill_matrix)

    def test_usage_guides_link_back_to_shared_navigation(self):
        for guide in USAGE_GUIDES:
            body = _read(ROOT / guide)
            self.assertIn("skill-matrix.md", body, guide)
            self.assertIn("quickstart.md", body, guide)

    def test_zh_readme_mirrors_top_level_landing_sections(self):
        zh_readme = _read(ROOT / "docs" / "zh" / "README.zh-CN.md")

        for heading in [
            "## 仓库定位",
            "## 选择 Skill",
            "## 推荐起点",
            "## 安装",
            "## 文档导航",
            "## 仓库结构",
            "## 维护者入口",
        ]:
            self.assertIn(heading, zh_readme)

        self.assertIn("../usage/skill-matrix.md", zh_readme)
        self.assertIn("quickstart.zh-CN.md", zh_readme)
        self.assertIn("review-workflows.zh-CN.md", zh_readme)
        self.assertIn("../../README.md", zh_readme)

        for skill in SKILLS:
            self.assertIn(f"`{skill}`", zh_readme)

    def test_repository_layout_lists_all_skill_packages(self):
        readme = _read(ROOT / "README.md")
        zh_readme = _read(ROOT / "docs" / "zh" / "README.zh-CN.md")

        for skill in SKILLS:
            self.assertIn(f"{skill}/", readme)
            self.assertIn(f"{skill}/", zh_readme)

    def test_landing_links_resolve(self):
        for path in LANDING_FILES:
            for target in _iter_repo_relative_links(path):
                self.assertTrue(target.exists(), f"{path} links to missing target: {target}")


if __name__ == "__main__":
    unittest.main()
