import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class MuseReverseSshPackageTests(unittest.TestCase):
    def test_required_skill_files_are_present(self):
        required_paths = [
            ROOT / "SKILL.md",
            ROOT / "agents" / "openai.yaml",
            ROOT / "scripts" / "reverse-ssh-keepalive.sh",
            ROOT / "scripts" / "reverse-ssh-boot.service",
            ROOT.parent / "docs" / "usage" / "muse-reverse-ssh.md",
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

        self.assertIn("name: muse-reverse-ssh", frontmatter)
        self.assertIn("reverse SSH tunnel", frontmatter)

        metadata = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Muse Reverse SSH"', metadata)
        self.assertIn("$muse-reverse-ssh", metadata)

    def test_core_safety_and_keepalive_are_documented(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for expected in [
            "GatewayPorts",
            "ExitOnForwardFailure",
            "ServerAliveInterval",
            "PasswordAuthentication no",
            "flock -n",  # still documented: as the thing NOT to use for long-lived supervisors
            "mkdir",  # atomic mkdir lockdir is the recommended single-instance guard
            "StrictHostKeyChecking",
        ]:
            self.assertIn(expected, skill_text)

    def test_boot_service_template_is_consistent(self):
        unit = ROOT / "scripts" / "reverse-ssh-boot.service"
        content = unit.read_text(encoding="utf-8")
        for expected in [
            "reverse-ssh-keepalive.sh",
            "Restart=always",
            "Environment=HOME=",
            "WantedBy=multi-user.target",
        ]:
            self.assertIn(expected, content)

    def test_boot_persistence_is_documented(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for expected in [
            "Boot Persistence",
            "reverse-ssh-boot.service",
            "@reboot",
            "Environment=HOME",
            "Layer 1",
            "Layer 2",
            "Layer 3",
            "autossh",
            "External watchdog",
            "VPS-side detection",
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
            ".keepalive.lockdir",  # atomic mkdir lock, not flock (fd inheritance hazard)
            'mkdir "$LOCKDIR"',
        ]:
            self.assertIn(expected, content)


if __name__ == "__main__":
    unittest.main()
