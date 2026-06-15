import importlib.util
import pathlib
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
LIB_PATH = ROOT / "scripts" / "review_skill_lib.py"
GOLDEN_DIR = ROOT / "tests" / "golden"


def load_module():
    spec = importlib.util.spec_from_file_location("review_skill_lib", LIB_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ReviewSkillLibTests(unittest.TestCase):
    def sample_context(self):
        return {
            "repo": "/tmp/demo",
            "base": "main",
            "current_branch": "feature/review",
            "scope_mode": "working_tree",
            "status": {"staged": ["src/app.ts"], "unstaged": [], "untracked": []},
            "changed_files": ["src/app.ts", "Dockerfile"],
            "changed_line_ranges": {
                "src/app.ts": {"added": [{"start": 10, "end": 14}], "deleted": []}
            },
            "detected_stack": ["typescript", "node", "docker"],
            "suggested_references": [
                "review-framework.md",
                "output-contract.md",
                "false-positive-control.md",
                "typescript.md",
                "backend-and-integrations.md",
                "verification-and-operations.md",
            ],
            "risk_flags": ["api_or_network_boundary", "container_or_runtime"],
            "safe_check_commands": [{"command": "npm test", "reason": "Verify regressions."}],
            "review_plan": {
                "mode": "specialist",
                "reviewers": [
                    "correctness",
                    "architecture",
                    "reliability",
                    "security",
                    "tests",
                ],
                "follow_up": ["synthesizer"],
            },
        }

    def test_parse_unified_zero_diff_builds_changed_ranges(self):
        module = load_module()
        diff_text = """diff --git a/src/app.ts b/src/app.ts
index 1111111..2222222 100644
--- a/src/app.ts
+++ b/src/app.ts
@@ -10,0 +11,3 @@ export function run() {
+  const enabled = true;
+  const retries = 3;
+  return enabled && retries > 0;
@@ -20,2 +24,0 @@ export function oldThing() {
-  legacyOne();
-  legacyTwo();
"""

        result = module.parse_unified_zero_diff(diff_text)

        self.assertEqual(
            result["src/app.ts"]["added"],
            [{"start": 11, "end": 13}],
        )
        self.assertEqual(
            result["src/app.ts"]["deleted"],
            [{"start": 20, "end": 21}],
        )

    def test_detect_stack_prefers_specific_references(self):
        module = load_module()
        paths = [
            "package.json",
            "tsconfig.json",
            "src/server.ts",
            "Dockerfile",
            "migrations/001_init.sql",
        ]

        result = module.detect_stack(paths)

        self.assertIn("typescript", result["detected_stack"])
        self.assertIn("node", result["detected_stack"])
        self.assertIn("docker", result["detected_stack"])
        self.assertIn("database", result["detected_stack"])
        self.assertIn("typescript.md", result["suggested_references"])
        self.assertIn("backend-and-integrations.md", result["suggested_references"])
        self.assertIn("review-framework.md", result["suggested_references"])
        self.assertIn("database.md", result["suggested_references"])

    def test_risk_flags_cover_sensitive_surfaces(self):
        module = load_module()
        paths = [
            "src/auth/session.ts",
            "src/payments/stripe.ts",
            "migrations/002_add_accounts.sql",
            ".github/workflows/deploy.yml",
            "Dockerfile",
        ]

        flags = module.derive_risk_flags(paths, diff_text="")

        self.assertIn("auth_or_access_control", flags)
        self.assertIn("payments_or_billing", flags)
        self.assertIn("database_migration", flags)
        self.assertIn("ci_cd_or_deploy", flags)
        self.assertIn("container_or_runtime", flags)

    def test_build_safe_check_commands_matches_detected_stack(self):
        module = load_module()

        commands = module.build_safe_check_commands(
            detected_stack=["typescript", "node", "python", "go", "docker"]
        )

        command_lines = [item["command"] for item in commands]
        self.assertIn("npm test", command_lines)
        self.assertIn("npm run lint", command_lines)
        self.assertIn("npm run typecheck", command_lines)
        self.assertIn("npm run build", command_lines)
        self.assertIn("python3 -m unittest discover", command_lines)
        self.assertIn("go test ./...", command_lines)
        self.assertIn("docker compose config", command_lines)

    def test_expand_repo_paths_flattens_untracked_directories_to_files(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            nested_dir = repo / "tests" / "golden"
            nested_dir.mkdir(parents=True)
            (nested_dir / "review-brief.txt").write_text("golden output\n")
            (repo / "README.md").write_text("demo\n")

            expanded = module.expand_repo_paths(
                repo,
                [
                    "tests/golden",
                    "README.md",
                ],
            )

            self.assertEqual(
                expanded,
                [
                    "tests/golden/review-brief.txt",
                    "README.md",
                ],
            )

    def test_risk_reference_augmentation_prefers_merged_reference_set(self):
        module = load_module()

        references = module.augment_references_for_risks(
            suggested_references=[
                "review-framework.md",
                "output-contract.md",
                "false-positive-control.md",
                "typescript.md",
            ],
            risk_flags=[
                "api_or_network_boundary",
                "auth_or_access_control",
                "container_or_runtime",
            ],
        )

        self.assertIn("backend-and-integrations.md", references)
        self.assertIn("verification-and-operations.md", references)
        self.assertIn("security.md", references)
        self.assertNotIn("api-integrations.md", references)
        self.assertNotIn("observability.md", references)
        self.assertNotIn("testing.md", references)

    def test_select_review_mode_uses_specialists_for_high_risk_changes(self):
        module = load_module()

        plan = module.select_review_mode(
            changed_files=[
                "src/auth/session.ts",
                "src/payments/stripe.ts",
                "migrations/002_add_accounts.sql",
            ],
            risk_flags=[
                "auth_or_access_control",
                "payments_or_billing",
                "database_migration",
            ],
        )

        self.assertEqual(plan["mode"], "specialist")
        self.assertIn("correctness", plan["reviewers"])
        self.assertIn("security", plan["reviewers"])
        self.assertIn("tests", plan["reviewers"])
        self.assertIn("synthesizer", plan["follow_up"])

    def test_build_review_brief_markdown_includes_scope_and_reviewers(self):
        module = load_module()
        context = self.sample_context()

        markdown = module.build_review_brief_markdown(context)

        self.assertIn("# Review Brief", markdown)
        self.assertIn("- Base: `main`", markdown)
        self.assertIn("- Changed files: `src/app.ts`, `Dockerfile`", markdown)
        self.assertIn("- Review mode: `specialist`", markdown)
        self.assertIn("## Suggested References", markdown)
        self.assertIn("- `typescript.md`", markdown)
        self.assertIn("## Verification Commands", markdown)

    def test_build_review_brief_markdown_matches_golden_output(self):
        module = load_module()
        context = self.sample_context()

        markdown = module.build_review_brief_markdown(context)
        expected = (GOLDEN_DIR / "review-brief-markdown.md").read_text()

        self.assertEqual(markdown, expected)

    def test_build_review_brief_compact_matches_golden_output(self):
        module = load_module()
        context = self.sample_context()

        compact = module.build_review_brief_compact(context)
        expected = (GOLDEN_DIR / "review-brief-compact.txt").read_text()

        self.assertEqual(compact, expected)


if __name__ == "__main__":
    unittest.main()
