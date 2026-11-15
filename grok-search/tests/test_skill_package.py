import json
import pathlib
import subprocess
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class GrokSearchPackageTests(unittest.TestCase):
    def test_required_skill_files_are_present(self):
        required_paths = [
            ROOT / "SKILL.md",
            ROOT / "agents" / "openai.yaml",
            ROOT / "references" / "planning.md",
            ROOT / "config.example.json",
            ROOT / "package.json",
            ROOT / "scripts" / "search.js",
            ROOT / "scripts" / "fetch.js",
            ROOT / "scripts" / "map.js",
            ROOT / "scripts" / "search.cmd",
            ROOT / "scripts" / "fetch.cmd",
            ROOT / "scripts" / "map.cmd",
            ROOT.parent / "docs" / "usage" / "grok-search.md",
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

        self.assertIn("name: grok-search", frontmatter)
        self.assertIn("search the web", frontmatter)

        metadata = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn("interface:", metadata)
        self.assertIn('display_name: "Grok Search"', metadata)
        self.assertIn('short_description: "Search and read the live web with sourced results"', metadata)
        self.assertIn("$grok-search", metadata)

    def test_script_routing_and_result_reading_are_documented(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for expected in [
            "scripts/fetch.js",
            "scripts/map.js",
            "scripts/search.js",
            "references/planning.md",
            "Every script prints one JSON object",
            "content.full_path",
        ]:
            self.assertIn(expected, skill_text)

    def test_fetch_writes_full_path_when_truncated(self):
        fetch_script = (ROOT / "scripts" / "fetch.js").read_text(encoding="utf-8")
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("full_path: contentInfo.full_output_path", fetch_script)
        self.assertNotIn("--full-path", fetch_script)
        self.assertIn("content.full_path", skill_text)

    def test_usage_guide_reads_current_search_sources(self):
        usage = (ROOT.parent / "docs" / "usage" / "grok-search.md").read_text(encoding="utf-8")

        self.assertIn("sources.items", usage)
        self.assertNotIn("sources.merged", usage)
        self.assertNotIn("sources.grok[]", usage)

    def test_example_config_carries_no_real_credentials(self):
        config = json.loads((ROOT / "config.example.json").read_text(encoding="utf-8"))

        self.assertEqual(config["apiKey"], "your-grok-api-key")
        self.assertEqual(config["tavilyApiKey"], "")
        self.assertEqual(config["firecrawlApiKey"], "")

    def test_node_test_entrypoint_is_declared(self):
        package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))

        self.assertEqual(package["name"], "grok-search")
        self.assertIn("test", package["scripts"])


class InstalledCopyDriftTests(unittest.TestCase):
    """Every install point must carry the committed tree byte for byte.

    The 2026-11-15 Windows report came from exactly this gap: the installed
    copy was behind the repository, so the agent running out of
    ``~/.agents`` saw the old bare ``scripts/fetch.js`` examples and hit the
    WScript error the repository had already documented away. Nothing turned
    red when the copy drifted, so the drift was only found by hand.

    Byte comparison is sound because the install is a literal copy of a
    checkout: ``SKILL.md`` is pinned to LF and ``*.cmd`` to CRLF in
    ``.gitattributes``, so both sides agree on line endings on every platform.
    """

    INSTALL_POINTS = (
        pathlib.Path.home() / ".agents/skills/grok-search",
        pathlib.Path.home() / ".claude/skills/grok-search",
        pathlib.Path.home() / ".codex/skills/grok-search",
        pathlib.Path.home() / ".zcode/skills/grok-search",
        pathlib.Path.home() / ".mirasim/skills/grok-search",
    )

    def tracked_files(self):
        root = ROOT.parent
        try:
            listed = subprocess.run(
                ["git", "-C", str(root), "ls-files", "grok-search"],
                capture_output=True, text=True, check=True,
            ).stdout.split()
        except (OSError, subprocess.CalledProcessError):
            self.skipTest("not a git checkout")
        return [path[len("grok-search/"):] for path in listed if path.startswith("grok-search/")]

    def test_installed_copies_match_the_committed_tree(self):
        tracked = self.tracked_files()
        self.assertGreater(len(tracked), 50, f"tracked file list looks wrong: {len(tracked)}")
        stale = []
        for install in self.INSTALL_POINTS:
            if not install.is_dir():
                continue
            for rel in tracked:
                source = ROOT / rel
                copy = install / rel
                if not copy.is_file() or copy.read_bytes() != source.read_bytes():
                    stale.append(f"{install.parent.parent.name}/{rel}")
        self.assertEqual(stale, [], f"drifted install copies (re-run the copy step): {stale}")


if __name__ == "__main__":
    unittest.main()
