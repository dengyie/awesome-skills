import json
import pathlib
import subprocess
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "collect-review-context.py"
REVIEW_ENTRYPOINT = ROOT / "scripts" / "review-entrypoint.py"
INSTALL_SCRIPT = ROOT / "scripts" / "install-local-skill.sh"
UPDATE_SCRIPT = ROOT / "scripts" / "update-local-skill.sh"
VERIFY_RELEASE_SCRIPT = ROOT / "scripts" / "verify-release.sh"


class CollectReviewContextCliTests(unittest.TestCase):
    def test_collect_review_context_reports_changed_files_and_ranges(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "package.json").write_text('{"name":"demo","scripts":{"test":"echo ok"}}\n')
            (repo / "tsconfig.json").write_text('{"compilerOptions":{"strict":true}}\n')
            (repo / "src").mkdir()
            (repo / "src" / "app.ts").write_text("export const ready = false;\n")
            subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "src" / "app.ts").write_text(
                "export const ready = true;\nexport const retries = 3;\n"
            )
            (repo / "Dockerfile").write_text("FROM node:20-alpine\n")

            result = subprocess.run(
                ["python3", str(SCRIPT), "--repo", str(repo)],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)

            self.assertIn("src/app.ts", payload["changed_files"])
            self.assertIn("Dockerfile", payload["changed_files"])
            self.assertIn("typescript", payload["detected_stack"])
            self.assertIn("docker", payload["detected_stack"])
            self.assertIn("src/app.ts", payload["changed_line_ranges"])
            self.assertIn("verification-and-operations.md", payload["suggested_references"])
            self.assertIn("npm test", [item["command"] for item in payload["safe_check_commands"]])

    def test_fixture_typescript_api_change_routes_to_backend_and_security_guidance(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "package.json").write_text('{"name":"demo","scripts":{"test":"echo ok","lint":"echo ok","typecheck":"echo ok","build":"echo ok"}}\n')
            (repo / "tsconfig.json").write_text('{"compilerOptions":{"strict":true}}\n')
            (repo / "src").mkdir()
            (repo / "src" / "api-client.ts").write_text("export const timeoutMs = 1000;\n")
            subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "src" / "api-client.ts").write_text(
                "export const timeoutMs = 2000;\nexport const endpoint = '/admin/users';\n"
            )

            result = subprocess.run(
                ["python3", str(SCRIPT), "--repo", str(repo)],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)

            self.assertIn("typescript", payload["detected_stack"])
            self.assertIn("node", payload["detected_stack"])
            self.assertIn("api_or_network_boundary", payload["risk_flags"])
            self.assertIn("backend-and-integrations.md", payload["suggested_references"])
            self.assertIn("verification-and-operations.md", payload["suggested_references"])
            self.assertIn("npm run typecheck", [item["command"] for item in payload["safe_check_commands"]])

    def test_fixture_database_migration_routes_to_database_reference(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "migrations").mkdir()
            (repo / "migrations" / "001_init.sql").write_text("create table users (id integer primary key);\n")
            subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "migrations" / "002_add_email.sql").write_text(
                "alter table users add column email text not null default '';\n"
            )

            result = subprocess.run(
                ["python3", str(SCRIPT), "--repo", str(repo)],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)

            self.assertIn("database", payload["detected_stack"])
            self.assertIn("database_migration", payload["risk_flags"])
            self.assertIn("database.md", payload["suggested_references"])

    def test_fixture_docker_change_routes_to_verification_and_operations(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "Dockerfile").write_text("FROM node:20-alpine\n")
            subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "Dockerfile").write_text("FROM node:22-alpine\nRUN adduser -D app\n")

            result = subprocess.run(
                ["python3", str(SCRIPT), "--repo", str(repo)],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)

            self.assertIn("docker", payload["detected_stack"])
            self.assertIn("container_or_runtime", payload["risk_flags"])
            self.assertIn("verification-and-operations.md", payload["suggested_references"])
            self.assertIn("docker compose config", [item["command"] for item in payload["safe_check_commands"]])

    def test_review_entrypoint_markdown_outputs_actionable_brief(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "package.json").write_text('{"name":"demo","scripts":{"test":"echo ok"}}\n')
            (repo / "src").mkdir()
            (repo / "src" / "auth.ts").write_text("export const allow = false;\n")
            subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "src" / "auth.ts").write_text("export const allow = true;\n")

            result = subprocess.run(
                ["python3", str(REVIEW_ENTRYPOINT), "--repo", str(repo), "--format", "markdown"],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("# Review Brief", result.stdout)
            self.assertIn("Suggested References", result.stdout)
            self.assertIn("Review mode", result.stdout)
            self.assertIn("Verification Commands", result.stdout)

    def test_review_entrypoint_compact_outputs_single_line_summary(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "package.json").write_text('{"name":"demo"}\n')
            (repo / "src").mkdir()
            (repo / "src" / "app.ts").write_text("export const value = 1;\n")
            subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / "src" / "app.ts").write_text("export const value = 2;\n")

            result = subprocess.run(
                ["python3", str(REVIEW_ENTRYPOINT), "--repo", str(repo), "--format", "compact"],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("review-mode=", result.stdout)
            self.assertIn("changed-files=", result.stdout)
            self.assertNotIn("\n\n", result.stdout)

    def test_install_and_update_scripts_are_present(self):
        self.assertTrue(INSTALL_SCRIPT.exists())
        self.assertTrue(UPDATE_SCRIPT.exists())
        self.assertTrue(VERIFY_RELEASE_SCRIPT.exists())

    def test_verify_release_script_includes_safe_check_and_summary_steps(self):
        script_text = VERIFY_RELEASE_SCRIPT.read_text()

        self.assertIn("run-safe-checks.py", script_text)
        self.assertIn("--format compact", script_text)

    def test_collect_review_context_flattens_untracked_directories(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            nested_dir = repo / "docs" / "golden"
            nested_dir.mkdir(parents=True)
            (nested_dir / "brief.md").write_text("golden\n")
            (repo / "README.md").write_text("demo\n")

            result = subprocess.run(
                ["python3", str(SCRIPT), "--repo", str(repo)],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)

            self.assertIn("docs/golden/brief.md", payload["changed_files"])
            self.assertNotIn("docs/golden", payload["changed_files"])

    def test_collect_review_context_keeps_submodule_directory_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )

            submodule_dir = repo / "vendor" / "shared-lib"
            submodule_dir.mkdir(parents=True)
            (submodule_dir / ".git").write_text("gitdir: ../../.git/modules/shared-lib\n")
            (submodule_dir / "README.md").write_text("nested file\n")

            result = subprocess.run(
                ["python3", str(SCRIPT), "--repo", str(repo)],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)

            self.assertIn("vendor/shared-lib", payload["changed_files"])
            self.assertNotIn("vendor/shared-lib/README.md", payload["changed_files"])


if __name__ == "__main__":
    unittest.main()
