import ipaddress
import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


def _package_text_files():
    paths = [ROOT / "SKILL.md", ROOT / "agents" / "openai.yaml"]
    paths.extend(sorted((ROOT / "references").glob("*.md")))
    return paths


def _read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


class CueSandboxPackageTests(unittest.TestCase):
    def test_required_skill_files_are_present(self):
        required_paths = [
            ROOT / "SKILL.md",
            ROOT / "agents" / "openai.yaml",
            ROOT / "references" / "ssh.md",
            ROOT / "references" / "easytier.md",
            ROOT / "references" / "probe.md",
            ROOT.parent / "docs" / "usage" / "cue-sandbox.md",
        ]
        missing = [
            str(path.relative_to(ROOT.parent))
            for path in required_paths
            if not path.exists()
        ]
        self.assertEqual(missing, [])

    def test_skill_frontmatter_and_metadata_are_aligned(self):
        skill_text = _read(ROOT / "SKILL.md")
        match = re.match(r"---\n(.*?)\n---", skill_text, re.DOTALL)
        self.assertIsNotNone(match)
        frontmatter = match.group(1)

        self.assertIn("name: cue-sandbox", frontmatter)
        self.assertIn("mesh-cue", frontmatter)
        self.assertIn("EasyTier", frontmatter)

        metadata = _read(ROOT / "agents" / "openai.yaml")
        self.assertIn("interface:", metadata)
        self.assertIn('display_name: "Cue Sandbox Access"', metadata)
        self.assertIn("$cue-sandbox", metadata)

    def test_core_safety_rules_are_documented(self):
        skill_text = _read(ROOT / "SKILL.md")
        ssh_text = _read(ROOT / "references" / "ssh.md")
        probe_text = _read(ROOT / "references" / "probe.md")
        easytier_text = _read(ROOT / "references" / "easytier.md")
        combined = "\n".join([skill_text, ssh_text, probe_text, easytier_text])
        for expected in [
            "GatewayPorts clientspecified",
            "PasswordAuthentication no",
            "id_rsa",
            "AGENT_DISABLE_WEB_SSH=false",
            "easytier-mango-mesh.service",
            "ping_group_range",
            "_static_ips",
            "releases/latest",
            "references/ssh.md",
            "references/easytier.md",
            "references/probe.md",
        ]:
            self.assertIn(expected, combined)

    def test_placeholders_are_used_for_operator_secrets(self):
        easytier_text = _read(ROOT / "references" / "easytier.md")
        ssh_text = _read(ROOT / "references" / "ssh.md")
        probe_text = _read(ROOT / "references" / "probe.md")
        skill_text = _read(ROOT / "SKILL.md")

        self.assertIn('network_secret = "<从 EasyTier 手册模板抄，禁止手编或改大小写>"', easytier_text)
        self.assertIn("<TENCENT_HUB>", easytier_text)
        self.assertIn("<HK_HUB>", easytier_text)
        self.assertIn("<INDIA_PUBLIC_IP>", ssh_text)
        self.assertIn("<KOMARI_ENDPOINT>", probe_text)
        self.assertIn("<KOMARI_ENDPOINT>", skill_text)
        self.assertIn("<HUB_OVERLAY>", skill_text)

    def test_overlay_pool_is_not_the_public_7019(self):
        probe_text = _read(ROOT / "references" / "probe.md")
        skill_text = _read(ROOT / "SKILL.md")
        self.assertIn("stratum+tcp://10.144.144.2:7019", probe_text)
        self.assertIn("不是公网 7019", skill_text)
        self.assertNotRegex(probe_text, r"stratum\+tcp://(?!10\.144\.144\.2)\d")

    def test_no_private_key_or_token_material(self):
        forbidden = [
            "BEGIN OPENSSH PRIVATE KEY",
            "BEGIN RSA PRIVATE KEY",
            "BEGIN EC PRIVATE KEY",
            "M4ngo#Mesh_SecKey",
            "SHA256:",
        ]
        uuid_re = re.compile(
            r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
            re.I,
        )
        hex32_re = re.compile(r"\b[0-9a-f]{32}\b", re.I)
        for path in _package_text_files():
            text = _read(path)
            for needle in forbidden:
                self.assertNotIn(needle, text, path)
            self.assertEqual([], uuid_re.findall(text), path)
            self.assertEqual([], hex32_re.findall(text), path)

    def test_no_public_ipv4_literals(self):
        ip_re = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
        allowed_private = (
            ipaddress.ip_network("10.0.0.0/8"),
            ipaddress.ip_network("127.0.0.0/8"),
            ipaddress.ip_network("0.0.0.0/32"),
        )
        for path in _package_text_files():
            for match in ip_re.findall(_read(path)):
                addr = ipaddress.ip_address(match)
                self.assertTrue(
                    any(addr in net for net in allowed_private),
                    f"{path}: public IPv4 literal {match}",
                )

    def test_usage_guide_links_shared_navigation(self):
        usage = _read(ROOT.parent / "docs" / "usage" / "cue-sandbox.md")
        self.assertIn("skill-matrix.md", usage)
        self.assertIn("quickstart.md", usage)
        self.assertIn("cue-sandbox", usage)
        self.assertIn("GatewayPorts", usage)
