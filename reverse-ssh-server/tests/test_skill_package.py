import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class ReverseSshServerPackageTests(unittest.TestCase):
    def test_required_skill_files_are_present(self):
        required_paths = [
            ROOT / "SKILL.md",
            ROOT / "agents" / "openai.yaml",
            ROOT / "scripts" / "reverse-ssh-keepalive.sh",
            ROOT.parent / "docs" / "usage" / "reverse-ssh-server.md",
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

        self.assertIn("name: reverse-ssh-server", frontmatter)
        self.assertIn("reverse SSH tunnel", frontmatter)

        metadata = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Reverse SSH Server"', metadata)
        self.assertIn("$reverse-ssh-server", metadata)

    def test_core_safety_and_keepalive_are_documented(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for expected in [
            "GatewayPorts",
            "ExitOnForwardFailure",
            "ServerAliveInterval",
            "PasswordAuthentication no",
            "flock -n",
            "StrictHostKeyChecking",
        ]:
            self.assertIn(expected, skill_text)

    def test_keepalive_script_is_valid_shell(self):
        script = ROOT / "scripts" / "reverse-ssh-keepalive.sh"
        content = script.read_text(encoding="utf-8")
        self.assertTrue(content.startswith("#!/bin/bash"))
        for expected in [
            "-R ",
            "ExitOnForwardFailure",
            "ServerAliveInterval",
            "flock -n 9",
        ]:
            self.assertIn(expected, content)


if __name__ == "__main__":
    unittest.main()
