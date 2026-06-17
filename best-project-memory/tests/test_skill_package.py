import pathlib
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class BestProjectMemoryPackageTests(unittest.TestCase):
    def test_required_skill_files_are_present(self):
        required_paths = [
            ROOT / "SKILL.md",
            ROOT / "agents" / "openai.yaml",
            ROOT / "references" / "state-schema.md",
            ROOT / "references" / "surface-contract.md",
            ROOT / "references" / "update-policy.md",
            ROOT / "references" / "update-triggers.md",
            ROOT / "references" / "quality-rules.md",
            ROOT / "references" / "integration-patterns.md",
            ROOT / "references" / "workstream-template.md",
            ROOT / "references" / "snapshot-schema.md",
            ROOT / "references" / "examples.md",
            ROOT / "references" / "handoff-patterns.md",
            ROOT / "scripts" / "init_memory.py",
            ROOT / "scripts" / "append_session.py",
            ROOT / "scripts" / "handoff_pack.py",
            ROOT / "scripts" / "snapshot_state.py",
            ROOT / "scripts" / "sync_workstream.py",
            ROOT / "scripts" / "generate_handoff.py",
            ROOT / "scripts" / "promote_decision.py",
            ROOT / "scripts" / "compact_session.py",
            ROOT / "scripts" / "memory_lint.py",
            ROOT / "scripts" / "stale_todo_check.py",
        ]

        missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
        self.assertEqual(missing, [])

    def test_skill_frontmatter_and_metadata_are_aligned(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"---\n(.*?)\n---", skill_text, re.DOTALL)
        self.assertIsNotNone(match)
        frontmatter = match.group(1)

        self.assertIn("name: best-project-memory", frontmatter)
        self.assertIn("restoring project context", frontmatter)
        self.assertIn("handoffs", skill_text)

        metadata = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Best Project Memory"', metadata)
        self.assertIn("short_description:", metadata)
        self.assertIn("$best-project-memory", metadata)
        self.assertIn("allow_implicit_invocation: true", metadata)

    def test_references_named_by_skill_exist(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        reference_paths = sorted(set(re.findall(r"`(references/[^`]+\.md)`", skill_text)))

        self.assertEqual(len(reference_paths), 8)
        missing = [path for path in reference_paths if not (ROOT / path).exists()]
        self.assertEqual(missing, [])

    def test_v2_contract_references_cover_surface_triggers_quality_and_integration(self):
        surface = (ROOT / "references" / "surface-contract.md").read_text(encoding="utf-8")
        triggers = (ROOT / "references" / "update-triggers.md").read_text(encoding="utf-8")
        quality = (ROOT / "references" / "quality-rules.md").read_text(encoding="utf-8")
        integration = (ROOT / "references" / "integration-patterns.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("workstreams/", surface)
        self.assertIn("snapshots/", surface)
        self.assertIn("Parallel task emerged", triggers)
        self.assertIn("High-quality workstreams", quality)
        self.assertIn("Level 3", integration)

    def test_init_memory_script_supports_v2_governance_dirs_and_templates(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "init_memory.py"),
                    "--repo",
                    str(repo),
                    "--with-governance-dirs",
                    "--default-workstream",
                    "release hardening",
                    "--default-snapshot",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            memory_dir = repo / ".codex-memory"
            self.assertTrue((memory_dir / "workstreams").is_dir())
            self.assertTrue((memory_dir / "snapshots").is_dir())
            self.assertTrue((memory_dir / "workstreams" / "release-hardening.md").exists())
            self.assertTrue((memory_dir / "snapshots" / "initial-snapshot.md").exists())

    def test_init_memory_script_creates_expected_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "init_memory.py"),
                    "--repo",
                    str(repo),
                    "--with-optional-dirs",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            memory_dir = repo / ".codex-memory"
            self.assertTrue((memory_dir / "project-state.md").exists())
            self.assertTrue((memory_dir / "session-log.md").exists())
            self.assertTrue((memory_dir / "decisions.md").exists())
            self.assertTrue((memory_dir / "todo.md").exists())
            self.assertTrue((memory_dir / "phases").is_dir())
            self.assertTrue((memory_dir / "handoffs").is_dir())

    def test_append_session_script_appends_structured_entry(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "init_memory.py"),
                    "--repo",
                    str(repo),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "append_session.py"),
                    "--repo",
                    str(repo),
                    "--task",
                    "Draft package docs",
                    "--actions",
                    "Created references and scripts",
                    "--results",
                    "Skill package is now structured",
                    "--next",
                    "Run validation",
                    "--blockers",
                    "None.",
                    "--timestamp",
                    "2026-06-17 10:30",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            session_log = (repo / ".codex-memory" / "session-log.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("## 2026-06-17 10:30", session_log)
            self.assertIn("- Task: Draft package docs", session_log)
            self.assertIn("- Next: Run validation", session_log)

    def test_handoff_pack_script_writes_handoff_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "init_memory.py"),
                    "--repo",
                    str(repo),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "handoff_pack.py"),
                    "--repo",
                    str(repo),
                    "--slug",
                    "memory-upgrade",
                    "--objective",
                    "Finish packaging the skill",
                    "--current-state",
                    "References and scripts are in place.",
                    "--read-first",
                    "best-project-memory/SKILL.md",
                    "docs/best-project-memory-expansion-design.md",
                    "--next-actions",
                    "Run tests",
                    "Update README",
                    "--validation",
                    "python -m unittest discover best-project-memory/tests -v",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            handoff_dir = repo / ".codex-memory" / "handoffs"
            handoffs = list(handoff_dir.glob("*-memory-upgrade-handoff.md"))
            self.assertEqual(len(handoffs), 1)
            handoff_text = handoffs[0].read_text(encoding="utf-8")
            self.assertIn("## Objective", handoff_text)
            self.assertIn("Finish packaging the skill", handoff_text)
            self.assertIn("Run tests", handoff_text)

    def test_snapshot_state_script_captures_branch_and_updates_project_state(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "checkout", "-b", "feature/memory"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            (repo / "README.md").write_text("demo\n", encoding="utf-8")

            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "init_memory.py"),
                    "--repo",
                    str(repo),
                    "--with-governance-dirs",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "snapshot_state.py"),
                    "--repo",
                    str(repo),
                    "--slug",
                    "working-tree",
                    "--validation-state",
                    "pytest not yet run",
                    "--notes",
                    "captured during test",
                    "--write-project-state",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            snapshots = list((repo / ".codex-memory" / "snapshots").glob("*-working-tree.md"))
            self.assertEqual(len(snapshots), 1)
            snapshot_text = snapshots[0].read_text(encoding="utf-8")
            self.assertIn("- feature/memory", snapshot_text)
            self.assertIn("- README.md", snapshot_text)
            self.assertIn("- pytest not yet run", snapshot_text)

            project_state = (repo / ".codex-memory" / "project-state.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("## Last Verified", project_state)
            self.assertIn("Snapshot:", project_state)

    def test_sync_workstream_script_creates_structured_workstream_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "init_memory.py"),
                    "--repo",
                    str(repo),
                    "--with-governance-dirs",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "sync_workstream.py"),
                    "--repo",
                    str(repo),
                    "--slug",
                    "release hardening",
                    "--objective",
                    "Stabilize package output",
                    "--current-state",
                    "Tests are passing and docs are in progress.",
                    "--blockers",
                    "None.",
                    "--files",
                    "README.md",
                    "best-project-memory/SKILL.md",
                    "--next-actions",
                    "Run full review",
                    "Prepare release notes",
                    "--validation",
                    "unit tests passing",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            workstream_path = (
                repo / ".codex-memory" / "workstreams" / "release-hardening.md"
            )
            self.assertTrue(workstream_path.exists())
            workstream_text = workstream_path.read_text(encoding="utf-8")
            self.assertIn("## Objective", workstream_text)
            self.assertIn("Stabilize package output", workstream_text)
            self.assertIn("- README.md", workstream_text)
            self.assertIn("- [ ] Run full review", workstream_text)

    def test_generate_handoff_script_uses_project_state_and_workstream(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "init_memory.py"),
                    "--repo",
                    str(repo),
                    "--with-governance-dirs",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / ".codex-memory" / "project-state.md").write_text(
                "# Project State\n\n"
                "## Objective\n"
                "- Stabilize release flow\n\n"
                "## Current Focus\n"
                "- Finish package verification\n\n"
                "## Active Blockers\n"
                "- None.\n\n"
                "## Key Artifacts\n"
                "- `README.md`\n",
                encoding="utf-8",
            )
            (repo / ".codex-memory" / "todo.md").write_text(
                "# TODO\n## In Progress\n- [ ] Run full review\n## Next\n- [ ] Prepare release notes\n## Done\n",
                encoding="utf-8",
            )

            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "sync_workstream.py"),
                    "--repo",
                    str(repo),
                    "--slug",
                    "release hardening",
                    "--objective",
                    "Stabilize release flow",
                    "--current-state",
                    "Verification is nearly complete.",
                    "--files",
                    "README.md",
                    "best-project-memory/SKILL.md",
                    "--next-actions",
                    "Run full review",
                    "--validation",
                    "unit tests passing",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "generate_handoff.py"),
                    "--repo",
                    str(repo),
                    "--slug",
                    "release-hardening",
                    "--workstream",
                    "release hardening",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            handoffs = list((repo / ".codex-memory" / "handoffs").glob("*-release-hardening-handoff.md"))
            self.assertEqual(len(handoffs), 1)
            handoff_text = handoffs[0].read_text(encoding="utf-8")
            self.assertIn("Stabilize release flow", handoff_text)
            self.assertIn("Verification is nearly complete.", handoff_text)
            self.assertIn("README.md", handoff_text)
            self.assertIn("Run full review", handoff_text)
            self.assertIn("unit tests passing", handoff_text)

    def test_compact_session_script_compacts_old_entries_and_keeps_recent_history(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "init_memory.py"),
                    "--repo",
                    str(repo),
                    "--with-optional-dirs",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            session_log = repo / ".codex-memory" / "session-log.md"
            session_log.write_text(
                "# Session Log\n"
                "## 2026-06-17 10:00\n"
                "- Task: First task\n"
                "- Actions: Did first thing\n"
                "- Results: First result\n"
                "- Next: First next\n"
                "- Blockers: None.\n"
                "## 2026-06-17 11:00\n"
                "- Task: Second task\n"
                "- Actions: Did second thing\n"
                "- Results: Second result\n"
                "- Next: Second next\n"
                "- Blockers: None.\n"
                "## 2026-06-17 12:00\n"
                "- Task: Third task\n"
                "- Actions: Did third thing\n"
                "- Results: Third result\n"
                "- Next: Third next\n"
                "- Blockers: External dependency\n"
                "## 2026-06-17 13:00\n"
                "- Task: Fourth task\n"
                "- Actions: Did fourth thing\n"
                "- Results: Fourth result\n"
                "- Next: Fourth next\n"
                "- Blockers: None.\n",
                encoding="utf-8",
            )

            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "compact_session.py"),
                    "--repo",
                    str(repo),
                    "--keep-last",
                    "2",
                    "--max-entries",
                    "3",
                    "--phase-slug",
                    "release-hardening",
                    "--title",
                    "Release hardening history",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            compacted_text = session_log.read_text(encoding="utf-8")
            self.assertIn("## Compacted History", compacted_text)
            self.assertIn("- Title: Release hardening history", compacted_text)
            self.assertIn("- Covered entries: 2", compacted_text)
            self.assertIn("Second result", compacted_text)
            self.assertNotIn("## 2026-06-17 10:00", compacted_text)
            self.assertNotIn("## 2026-06-17 11:00", compacted_text)
            self.assertIn("## 2026-06-17 12:00", compacted_text)
            self.assertIn("## 2026-06-17 13:00", compacted_text)

            phase_files = list((repo / ".codex-memory" / "phases").glob("*-release-hardening.md"))
            self.assertEqual(len(phase_files), 1)
            phase_text = phase_files[0].read_text(encoding="utf-8")
            self.assertIn("# Phase Summary", phase_text)
            self.assertIn("Release hardening history", phase_text)
            self.assertIn("Second result", phase_text)

    def test_compact_session_script_dry_run_and_threshold_leave_log_unchanged(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "init_memory.py"),
                    "--repo",
                    str(repo),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            session_log = repo / ".codex-memory" / "session-log.md"
            original = (
                "# Session Log\n"
                "## 2026-06-17 10:00\n"
                "- Task: Demo task\n"
                "- Actions: Demo action\n"
                "- Results: Demo result\n"
                "- Next: Demo next\n"
                "- Blockers: None.\n"
            )
            session_log.write_text(original, encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "compact_session.py"),
                    "--repo",
                    str(repo),
                    "--dry-run",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("No compaction needed", result.stdout)
            self.assertEqual(session_log.read_text(encoding="utf-8"), original)

    def test_promote_decision_script_appends_structured_entry(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "init_memory.py"),
                    "--repo",
                    str(repo),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "promote_decision.py"),
                    "--repo",
                    str(repo),
                    "--title",
                    "Use workstreams for parallel release tracks",
                    "--decision",
                    "Store parallel release state in workstream files.",
                    "--rationale",
                    "Global project state should remain compact.",
                    "--impact",
                    "Release coordination becomes easier to scan.",
                    "--related-files",
                    "best-project-memory/references/state-schema.md",
                    "--source-workstream",
                    "release hardening",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            decisions_text = (repo / ".codex-memory" / "decisions.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("Use workstreams for parallel release tracks", decisions_text)
            self.assertIn("Global project state should remain compact.", decisions_text)
            self.assertIn(".codex-memory/workstreams/release-hardening.md", decisions_text)

    def test_memory_lint_passes_for_well_formed_memory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "init_memory.py"),
                    "--repo",
                    str(repo),
                    "--with-governance-dirs",
                    "--default-workstream",
                    "release hardening",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / ".codex-memory" / "project-state.md").write_text(
                "# Project State\n\n"
                "## Objective\n- Demo\n\n"
                "## Current Phase\n- Phase 4\n\n"
                "## Current Branch\n- feature/demo\n\n"
                "## Last Verified\n- unit tests passing\n\n"
                "## Active Risks\n- None.\n\n"
                "## Active Blockers\n- None.\n\n"
                "## Current Focus\n- Finish quality checks\n\n"
                "## Next Milestone\n- Review package\n\n"
                "## Key Artifacts\n- `README.md`\n",
                encoding="utf-8",
            )
            (repo / ".codex-memory" / "todo.md").write_text(
                "# TODO\n## In Progress\n- [ ] Run review\n## Next\n- [ ] Prepare notes\n## Done\n- [x] Add scripts\n",
                encoding="utf-8",
            )
            (repo / ".codex-memory" / "decisions.md").write_text(
                "# Decisions\n## 2026-06-17 - Demo\n- Decision: Use workstreams.\n- Rationale: Keep state local.\n- Alternatives considered: None.\n- Impact: Easier coordination.\n- Rollback trigger: Revisit if too heavy.\n- Related files: `README.md`\n",
                encoding="utf-8",
            )
            (repo / ".codex-memory" / "session-log.md").write_text(
                "# Session Log\n## 2026-06-17 10:00\n- Task: Demo\n- Actions: Demo\n- Results: Demo\n- Next: Demo\n- Blockers: None.\n",
                encoding="utf-8",
            )
            (repo / ".codex-memory" / "workstreams" / "release-hardening.md").write_text(
                "# Workstream\n\n## Objective\n- Demo\n\n## Current State\n- Demo\n\n## Blockers\n- None.\n\n## Files\n- README.md\n\n## Next Actions\n- [ ] Run review\n\n## Validation\n- unit tests passing\n",
                encoding="utf-8",
            )
            (repo / ".codex-memory" / "handoffs").mkdir(exist_ok=True)
            (repo / ".codex-memory" / "handoffs" / "2026-06-17-demo-handoff.md").write_text(
                "# Handoff\n\n## Objective\n- Demo\n\n## Current State\n- Demo\n\n## Read First\n- README.md\n\n## Exact Next Actions\n- Run review\n\n## Blockers\n- None.\n\n## Validation To Run\n- unit tests passing\n",
                encoding="utf-8",
            )

            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "memory_lint.py"),
                    "--repo",
                    str(repo),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

    def test_memory_lint_errors_when_project_state_references_missing_snapshot(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "init_memory.py"),
                    "--repo",
                    str(repo),
                    "--with-governance-dirs",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / ".codex-memory" / "project-state.md").write_text(
                "# Project State\n\n"
                "## Objective\n- Demo\n\n"
                "## Current Phase\n- Phase 4\n\n"
                "## Current Branch\n- feature/demo\n\n"
                "## Last Verified\n- unit tests passing\n- Snapshot: `2026-06-18-branch-state.md`\n\n"
                "## Active Risks\n- None.\n\n"
                "## Active Blockers\n- None.\n\n"
                "## Current Focus\n- Finish checks\n\n"
                "## Next Milestone\n- Review package\n\n"
                "## Key Artifacts\n- `README.md`\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "memory_lint.py"),
                    "--repo",
                    str(repo),
                ],
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("referenced snapshot does not exist", result.stdout)

    def test_memory_lint_warns_when_session_log_should_be_compacted(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "init_memory.py"),
                    "--repo",
                    str(repo),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            entries = []
            for index in range(9):
                hour = 10 + index
                entries.append(
                    f"## 2026-06-17 {hour:02d}:00\n"
                    f"- Task: Task {index}\n"
                    f"- Actions: Action {index}\n"
                    f"- Results: Result {index}\n"
                    f"- Next: Next {index}\n"
                    "- Blockers: None.\n"
                )
            (repo / ".codex-memory" / "session-log.md").write_text(
                "# Session Log\n" + "".join(entries),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "memory_lint.py"),
                    "--repo",
                    str(repo),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("session-log.md: structured history is getting long", result.stdout)
            self.assertEqual(result.returncode, 0)

    def test_memory_lint_warns_when_latest_snapshot_with_changes_is_not_referenced(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "init_memory.py"),
                    "--repo",
                    str(repo),
                    "--with-governance-dirs",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            (repo / ".codex-memory" / "project-state.md").write_text(
                "# Project State\n\n"
                "## Objective\n- Demo\n\n"
                "## Current Phase\n- Phase 4\n\n"
                "## Current Branch\n- feature/demo\n\n"
                "## Last Verified\n- unit tests passing\n\n"
                "## Active Risks\n- None.\n\n"
                "## Active Blockers\n- None.\n\n"
                "## Current Focus\n- Finish checks\n\n"
                "## Next Milestone\n- Review package\n\n"
                "## Key Artifacts\n- `README.md`\n",
                encoding="utf-8",
            )
            snapshots_dir = repo / ".codex-memory" / "snapshots"
            snapshots_dir.mkdir(exist_ok=True)
            (snapshots_dir / "2026-06-18-branch-state.md").write_text(
                "# Snapshot\n\n"
                "## Captured At\n- 2026-06-18 10:00\n\n"
                "## Branch\n- feature/demo\n\n"
                "## Changed Files\n- README.md\n\n"
                "## Validation State\n- tests pending\n\n"
                "## Notes\n- Demo\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "memory_lint.py"),
                    "--repo",
                    str(repo),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("latest snapshot `2026-06-18-branch-state.md` shows changed files", result.stdout)
            self.assertEqual(result.returncode, 0)

    def test_stale_todo_check_fails_for_vague_items(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = pathlib.Path(temp_dir)
            (repo / ".codex-memory").mkdir()
            (repo / ".codex-memory" / "todo.md").write_text(
                "# TODO\n## In Progress\n- [ ] cleanup\n## Next\n- [ ] keep improving this\n## Done\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "stale_todo_check.py"),
                    "--repo",
                    str(repo),
                ],
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("looks stale or too vague", result.stdout)


if __name__ == "__main__":
    unittest.main()
