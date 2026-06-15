import json
import pathlib
import subprocess
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "collect-review-context.py"
REVIEW_ENTRYPOINT = ROOT / "scripts" / "review-entrypoint.py"


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


if __name__ == "__main__":
    unittest.main()
