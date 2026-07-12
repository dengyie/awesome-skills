import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class CodexAgentWorktreeSetupPackageTests(unittest.TestCase):
    def test_required_skill_files_are_present(self):
        required_paths = [
            ROOT / "SKILL.md",
            ROOT / "agents" / "openai.yaml",
            ROOT.parent / "docs" / "usage" / "codex-agent-worktree-setup.md",
        ]
        missing = [
            str(path.relative_to(ROOT.parent))
            for path in required_paths
            if not path.exists()
        ]
        self.assertEqual(missing, [])

    def test_skill_frontmatter_and_metadata_are_aligned(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"---\n(.*?)\n---", skill_text, re.DOTALL)
        self.assertIsNotNone(match)
        frontmatter = match.group(1)

        self.assertIn("name: codex-agent-worktree-setup", frontmatter)
        self.assertIn("isolated branch-bound worktrees", frontmatter)

        metadata_path = ROOT / "agents" / "openai.yaml"
        self.assertTrue(metadata_path.exists(), "agents/openai.yaml")
        metadata = metadata_path.read_text(encoding="utf-8")
        self.assertIn('display_name: "Codex Agent Worktree Setup"', metadata)
        self.assertIn("$codex-agent-worktree-setup", metadata)

    def test_main_worktree_and_detached_head_safety_are_documented(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for expected in [
            "Never develop directly in a primary `main` or `master` worktree.",
            "If the primary worktree has uncommitted changes, stop",
            "If the worktree is dirty, stop",
            "target branch is already checked out in another worktree",
        ]:
            self.assertIn(expected, skill_text)


if __name__ == "__main__":
    unittest.main()
