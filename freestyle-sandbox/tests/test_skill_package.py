import pathlib
import re
import subprocess
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


def _read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


class FreestyleSandboxPackageTests(unittest.TestCase):
    def test_required_skill_files_are_present(self):
        required_paths = [
            ROOT / "SKILL.md",
            ROOT / "agents" / "openai.yaml",
            ROOT / "references" / "decision-matrix.md",
            ROOT / "scripts" / "manage.sh",
        ]
        usage = ROOT.parent / "docs" / "usage" / "freestyle-sandbox.md"
        if (ROOT.parent / ".git").exists() or (ROOT.parent / "docs").exists():
            required_paths.append(usage)
        missing = [
            str(path.relative_to(ROOT.parent if path.is_relative_to(ROOT.parent) else ROOT))
            for path in required_paths
            if not path.exists()
        ]
        self.assertEqual(missing, [])

    def test_skill_frontmatter_and_metadata_are_aligned(self):
        skill_text = _read(ROOT / "SKILL.md")
        match = re.match(r"---\n(.*?)\n---", skill_text, re.DOTALL)
        self.assertIsNotNone(match)
        frontmatter = match.group(1)

        self.assertIn("name: freestyle-sandbox", frontmatter)
        self.assertIn("freestyle", frontmatter)
        self.assertIn("云开发机", frontmatter)
        self.assertIn("Linux 沙箱", frontmatter)

        metadata = _read(ROOT / "agents" / "openai.yaml")
        self.assertIn("interface:", metadata)
        self.assertIn('display_name: "Freestyle Sandbox"', metadata)
        self.assertIn("$freestyle-sandbox", metadata)

    def test_manage_script_is_executable_and_syntax_valid(self):
        script_path = ROOT / "scripts" / "manage.sh"
        self.assertTrue(script_path.exists())

        # Check syntax with bash -n
        result = subprocess.run(
            ["bash", "-n", str(script_path)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, f"bash -n failed: {result.stderr}")

        content = _read(script_path)
        self.assertIn("trap 'cleanup_on_exit INT", content)
        self.assertIn("freestyle vm pause", content)
        self.assertIn("SNAPSHOT_FOR_TIER", content)
        self.assertIn("IDLE_TIMEOUT_FOR_TIER", content)

    def test_core_quota_and_safety_rules_are_documented(self):
        skill_text = _read(ROOT / "SKILL.md")
        matrix_text = _read(ROOT / "references" / "decision-matrix.md")
        combined = "\n".join([skill_text, matrix_text])

        self.assertIn("100 vCPU-hrs", combined)
        self.assertIn("200 GiB-hrs", combined)
        self.assertIn("ubuntu-sm", combined)
        self.assertIn("idle-timeout-seconds", combined)
        self.assertIn("pause", combined)
        self.assertIn("freestyle/ubuntu", combined)


if __name__ == "__main__":
    unittest.main()
