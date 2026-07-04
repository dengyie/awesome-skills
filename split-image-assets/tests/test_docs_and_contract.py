import pathlib
import sys

TESTS_DIR = pathlib.Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from skill_package_testlib import Image, REPO, ROOT, SplitImageAssetsTestBase, json, pathlib, re, subprocess, sys, tempfile


class SplitImageAssetsPackageTests(SplitImageAssetsTestBase):
    def test_required_skill_files_are_present(self):
        required_paths = [
            ROOT / "SKILL.md",
            ROOT / "agents" / "openai.yaml",
            ROOT / "references" / "workflow.md",
            ROOT / "references" / "pipeline-recipes.md",
            ROOT / "references" / "quick-contract.md",
            ROOT / "references" / "asset-package-contract.md",
            ROOT / "references" / "provider-contract.md",
            ROOT / "references" / "default-route-chains.md",
            ROOT / "references" / "qa-standards.md",
            ROOT / "references" / "manual-review.md",
            ROOT / "references" / "confirmation-prompts.md",
            ROOT / "references" / "ui-atomic-split.md",
            ROOT / "references" / "grounded-sam-pipeline.md",
            ROOT / "external_manifest_examples" / "sam2_rembg_manifest.json",
            ROOT / "scripts" / "init_asset_package.py",
            ROOT / "scripts" / "import_external_assets.py",
            ROOT / "scripts" / "build_previews.py",
            ROOT / "scripts" / "build_quality_previews.py",
            ROOT / "scripts" / "audit_visual_quality.py",
            ROOT / "scripts" / "check_extraction_environment.py",
            ROOT / "scripts" / "compare_candidate_assets.py",
            ROOT / "scripts" / "candidate_workflow_lib.py",
            ROOT / "scripts" / "work_item_schema_lib.py",
            ROOT / "scripts" / "package_state_lib.py",
            ROOT / "scripts" / "provider_contract.py",
            ROOT / "scripts" / "provider_registry.py",
            ROOT / "scripts" / "provider_bridge_lib.py",
            ROOT / "scripts" / "generation_brief_lib.py",
            ROOT / "scripts" / "describe_provider_plan.py",
            ROOT / "scripts" / "describe_provider_work_items.py",
            ROOT / "scripts" / "describe_candidate_work_items.py",
            ROOT / "scripts" / "prepare_provider_request.py",
            ROOT / "scripts" / "prepare_generation_brief.py",
            ROOT / "scripts" / "consume_provider_result.py",
            ROOT / "scripts" / "record_provider_result.py",
            ROOT / "scripts" / "archive_intermediates.py",
            ROOT / "scripts" / "generate_ui_carrier_candidates.py",
            ROOT / "scripts" / "generate_ui_glyph_cleanup_candidates.py",
            ROOT / "scripts" / "record_quality_review.py",
            ROOT / "scripts" / "record_candidate_selection.py",
            ROOT / "scripts" / "record_candidate_promotion_approval.py",
            ROOT / "scripts" / "apply_candidate_selection_decision.py",
            ROOT / "scripts" / "apply_candidate_promotion_decision.py",
            ROOT / "scripts" / "score_candidate_assets.py",
            ROOT / "scripts" / "upscale_repair_downscale.py",
            ROOT / "scripts" / "export_asset_manifest.py",
            ROOT / "scripts" / "validate_asset_package.py",
            ROOT / "scripts" / "validator_shared.py",
            ROOT / "scripts" / "validator_metadata_lib.py",
            ROOT / "scripts" / "validator_package_artifacts_lib.py",
            ROOT / "scripts" / "validator_objects_lib.py",
            ROOT / "scripts" / "promote_candidate_asset.py",
            REPO / "docs" / "superpowers" / "split-image-assets" / "README.md",
            REPO / "docs" / "superpowers" / "split-image-assets" / "design.md",
            REPO / "docs" / "superpowers" / "split-image-assets" / "implementation-plan.md",
            REPO / "docs" / "superpowers" / "split-image-assets" / "migration.md",
            REPO / "docs" / "usage" / "split-image-assets.md",
        ]

        missing = [str(path.relative_to(REPO)) for path in required_paths if not path.exists()]
        self.assertEqual(missing, [])
    def test_split_image_assets_canonical_docs_are_directory_scoped(self):
        docs_root = REPO / "docs" / "superpowers" / "split-image-assets"
        readme = (docs_root / "README.md").read_text(encoding="utf-8")
        design = (docs_root / "design.md").read_text(encoding="utf-8")
        plan = (docs_root / "implementation-plan.md").read_text(encoding="utf-8")
        migration = (docs_root / "migration.md").read_text(encoding="utf-8")

        self.assertIn("single documentation entrypoint", readme)
        self.assertIn("Future `split-image-assets` work must converge here first", readme)
        self.assertIn("Recommended Reading Order", readme)
        self.assertIn("single governing design document", design)
        self.assertIn("single implementation plan", plan)
        self.assertIn("documentation-system migration", migration)
        self.assertIn("delivered baseline", design)
        self.assertIn("no new active milestone is open", design)
        self.assertIn("current implementation baseline", plan)

        retired = [
            REPO / "docs" / "superpowers" / "specs" / "2026-06-23-split-image-assets-design.md",
            REPO / "docs" / "superpowers" / "specs" / "2026-06-23-split-image-assets-pipeline-refactor-design.md",
            REPO / "docs" / "superpowers" / "specs" / "2026-06-28-split-image-assets-interaction-framework-design.md",
            REPO / "docs" / "superpowers" / "specs" / "2026-06-28-split-image-assets-asset-value-scoring-design.md",
            REPO / "docs" / "superpowers" / "specs" / "2026-06-29-split-image-assets-usability-redesign-design.md",
            REPO / "docs" / "superpowers" / "plans" / "2026-06-23-split-image-assets.md",
            REPO / "docs" / "superpowers" / "plans" / "2026-06-28-split-image-assets-interaction-framework.md",
            REPO / "docs" / "superpowers" / "plans" / "2026-06-28-split-image-assets-asset-value-scoring-implementation-plan.md",
            REPO / "docs" / "superpowers" / "plans" / "2026-06-29-split-image-assets-usability-redesign-implementation-plan.md",
        ]
        self.assertEqual([path for path in retired if path.exists()], [])
    def test_quick_contract_provides_short_package_contract_view(self):
        quick_contract = (ROOT / "references" / "quick-contract.md").read_text(
            encoding="utf-8"
        )

        for expected in [
            "Quick Contract",
            "three formal stop classes",
            "editability-first",
            "formal state surfaces",
            "qa.status=pass",
            "generated-only pass",
            "promotion or acceptance evidence",
            "generated-reconstruction",
            "production-ready assets",
            "draft candidate assets",
            "support-only layers",
        ]:
            self.assertIn(expected, quick_contract)
    def test_provider_docs_encode_bridge_first_v1_scope_guards(self):
        provider_contract = (ROOT / "references" / "provider-contract.md").read_text(
            encoding="utf-8"
        )
        default_chains = (ROOT / "references" / "default-route-chains.md").read_text(
            encoding="utf-8"
        )

        for expected in [
            "external-professional-outputs",
            "external-generated-outputs",
            "codex-controlled-generation",
            "grounded-sam-bridge",
            "must not write `metadata.json` directly",
            "route default",
            "object_type` override",
        ]:
            self.assertIn(expected, provider_contract + "\n" + default_chains)
    def test_skill_frontmatter_and_core_rules_are_present(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"---\n(.*?)\n---", skill_text, re.DOTALL)
        self.assertIsNotNone(match)
        frontmatter = match.group(1)

        self.assertIn("name: split-image-assets", frontmatter)
        self.assertIn("asset package", frontmatter)
        self.assertIn("not a professional segmenter", skill_text)
        self.assertIn("draft-only packaging", skill_text)
        self.assertIn("ANALYZE BEFORE EXTRACTING", skill_text)
        self.assertIn("REUSABLE ASSETS BEFORE PREVIEWS", skill_text)
        self.assertIn("NEVER HIDE UNCERTAINTY", skill_text)
        self.assertIn("QUALITY-GATED PIPELINE", skill_text)
        self.assertIn("DECISION SYNC BEFORE AMBIGUOUS SPLITS", skill_text)
        self.assertIn("EXTRACTION CAPABILITY GATE", skill_text)
        self.assertIn("PREFLIGHT TOOLING RECOMMENDATION GATE", skill_text)
        self.assertIn("DO NOT START EXTRACTION BEFORE TOOLING PREFLIGHT IS REPORTED AND RECORDED", skill_text)
        self.assertIn("PROGRESS UPDATES ARE COMMENTARY, NOT CONFIRMATION GATES", skill_text)
        self.assertIn("ONLY THREE EVENT TYPES MAY PAUSE EXECUTION", skill_text)
        self.assertIn("Running", skill_text)
        self.assertIn("AwaitingDecision", skill_text)
        self.assertIn("AwaitingExternalBlocker", skill_text)
        self.assertIn("AwaitingApproval", skill_text)
        self.assertIn("NO FORMAL GATE MAY BE SATISFIED BY AGENT DEFAULTING", skill_text)
        self.assertIn("INFERRED-FROM-USER MEANS EVIDENCE-BACKED USER INTENT, NOT AGENT GUESSING", skill_text)
        self.assertIn("GRANULARITY ALIGNMENT GATE", skill_text)
        self.assertIn("CONFIRMATION GATE", skill_text)
        self.assertIn("DO NOT DEFAULT TO ONE-PASS EXTRACTION", skill_text)
        self.assertIn("PROFESSIONAL SEGMENTER FIRST", skill_text)
        self.assertIn("SOURCE-SPACE MASKS ARE NORMAL", skill_text)
        self.assertIn("STAGE INTERMEDIATES", skill_text)
        self.assertIn("tile", skill_text)
        self.assertIn("glyph", skill_text)
        self.assertIn("WHOLE-IMAGE PLANNING BEFORE EXPENSIVE OBJECT WORK", skill_text)
        self.assertIn("GENERATION ROUTING GATE", skill_text)
        self.assertIn("plan_manifest.json", skill_text)
        self.assertIn("default provider chain", skill_text)
        self.assertIn("object_type override", skill_text)
        self.assertIn("describe_provider_plan.py", skill_text)
        self.assertIn("describe_provider_work_items.py", skill_text)
        self.assertIn("describe_candidate_work_items.py", skill_text)
        self.assertIn("prepare_provider_request.py", skill_text)
        self.assertIn("prepare_generation_brief.py", skill_text)
        self.assertIn("consume_provider_result.py", skill_text)
        self.assertIn("record_provider_result.py", skill_text)
        self.assertIn("do not let provider bridge scripts write `metadata.json` directly", skill_text)
        self.assertIn("generated-reconstruction", skill_text)
        self.assertIn("structural-valid", skill_text)
        self.assertIn("usable-draft", skill_text)
        self.assertIn("visual-acceptance-ready", skill_text)
        self.assertIn("object type", skill_text.lower())
        self.assertIn("2x2 sprite sheet is only a preview", skill_text)
        self.assertIn("SEMANTIC LAYERS BEFORE RECTANGLES", skill_text)
        self.assertIn("rectangular crops", skill_text)
    def test_references_named_by_skill_exist(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        reference_paths = sorted(set(re.findall(r"`(references/[^`]+\.md)`", skill_text)))

        self.assertGreaterEqual(len(reference_paths), 4)
        missing = [path for path in reference_paths if not (ROOT / path).exists()]
        self.assertEqual(missing, [])
    def test_usage_doc_mentions_contract_previews_metadata_qa_and_manual_review(self):
        usage = (REPO / "docs" / "usage" / "split-image-assets.md").read_text(
            encoding="utf-8"
        )

        for expected in [
            "asset package",
            "transparent PNG",
            "mask",
            "background_clean.png",
            "operator guide",
            "metadata.json",
            "qa_report.md",
            "sprite_sheet_2x2.png",
            "asset_manifest.json",
            "manual review",
            "does not perform segmentation",
            "professional upstream",
            "production-capable",
            "draft-packaging-only",
            "Preflight Tooling Recommendation Gate",
            "metadata.capability",
            "grill-me style",
            "confirmation",
            "semantic layer hierarchy",
            "Grounded-SAM",
            "Qwen-Image-Layered",
            "rectangular crop",
            "check_extraction_environment.py",
            "Before extraction",
            "source-space",
            "_staging",
            "_archive_intermediate",
            "tile",
            "glyph",
            "record_quality_review.py",
            "record_candidate_selection.py",
            "record_candidate_promotion_approval.py",
            "apply_candidate_selection_decision.py",
            "apply_candidate_promotion_decision.py",
            "archive_intermediates.py",
            "export_asset_manifest.py",
            "describe_provider_plan.py",
            "describe_provider_work_items.py",
            "describe_candidate_work_items.py",
            "prepare_provider_request.py",
            "consume_provider_result.py",
            "record_provider_result.py",
            "prepare_generation_brief.py",
            "provider bridge",
            "_staging/providers/",
            "provider_plan.json",
            "provider_work_items.json",
            "candidate_work_items.json",
            "object_type override",
            "must not write `metadata.json` directly",
            "`qa.status=pass` requires extraction-capable",
            "plan_manifest.json",
            "Generation Routing Gate",
            "generated-reconstruction",
            "accepted generated reconstructions",
            "asset_class",
            "reuse_status",
            "production-ready assets",
            "draft candidate assets",
            "support-only layers",
            "generate_ui_carrier_candidates.py",
            "generate_ui_glyph_cleanup_candidates.py",
            "score_candidate_assets.py",
            "upscale_repair_downscale.py",
            "visual-acceptance-ready",
            "progress updates are commentary",
            "candidate promotion",
            "formal approval",
            "Read What Where",
        ]:
            self.assertIn(expected, usage)
    def test_usage_doc_mentions_conservative_continuous_execution(self):
        usage = (REPO / "docs" / "usage" / "split-image-assets.md").read_text(
            encoding="utf-8"
        ).lower()

        for expected in [
            "default execution model",
            "continue versus stop",
            "progress updates are commentary",
        ]:
            self.assertIn(expected, usage)
    def test_skill_docs_describe_asset_value_scoring_and_text_routing(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        workflow_text = (ROOT / "references" / "workflow.md").read_text(encoding="utf-8")
        contract_text = (ROOT / "references" / "asset-package-contract.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Asset Value Scoring Gate", skill_text)
        self.assertIn("ordinary text", skill_text.lower())
        self.assertIn("rebuild_downstream", workflow_text)
        self.assertIn("text_role", contract_text)
        self.assertIn("recommended_action", contract_text)
    def test_skill_gate_list_matches_allowed_gate_taxonomy(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")

        for expected in [
            "Granularity Alignment Gate",
            "Generation Routing Gate",
            "Pilot Object Gate",
            "Approximate Reconstruction Acceptance Gate",
            "Final Acceptance Gate",
            "Candidate Promotion Acceptance Gate",
        ]:
            self.assertIn(expected, skill_text)

        for retired in [
            "Carrier/Glyph Split Gate",
            "Final Promotion Acceptance Gate",
            "user-decision` first, `formal-approval` when claim escalation is at stake",
        ]:
            self.assertNotIn(retired, skill_text)
    def test_workflow_doc_maps_gate_taxonomy_to_states(self):
        self._assert_text_in_file(
            ROOT / "references" / "workflow.md",
            [
                "tooling_preflight",
                "granularity_alignment",
                "generation_routing",
                "pilot_object",
                "approximate_reconstruction",
                "final_acceptance",
                "candidate_promotion",
                "AwaitingDecision",
                "AwaitingExternalBlocker",
                "AwaitingApproval",
            ],
        )
    def test_ui_atomic_split_uses_canonical_routing_outcomes(self):
        ui_atomic_split = (ROOT / "references" / "ui-atomic-split.md").read_text(
            encoding="utf-8"
        )

        for expected in [
            "extract_asset",
            "rebuild_downstream",
            "requires_user_confirmation",
            "support_only",
            "planned_route",
            "extract",
            "reconstruct",
            "generate",
        ]:
            self.assertIn(expected, ui_atomic_split)

        for retired in [
            "must_extract",
            "skip_for_now",
        ]:
            self.assertNotIn(retired, ui_atomic_split)
    def test_confirmation_prompts_are_limited_to_allowed_stop_classes(self):
        prompts = (ROOT / "references" / "confirmation-prompts.md").read_text(
            encoding="utf-8"
        )

        for expected in [
            "Why This Needs a Human",
            "Recommendation",
            "Options and Impact",
            "What I Will Do After Confirmation",
        ]:
            self.assertIn(expected, prompts)

        self._assert_any_regex_matches(
            prompts,
            [
                r"must not be used for progress-only pauses",
                r"not be used for progress-only pauses",
                r"forbid(?:s)? progress-only pauses",
            ],
        )
    def test_asset_package_contract_separates_formal_state_from_commentary(self):
        contract = (ROOT / "references" / "asset-package-contract.md").read_text(
            encoding="utf-8"
        ).lower()

        for expected in [
            "decision_log",
            "confirmation",
            "formal state",
            "must not contain",
            "progress updates",
            "object-scoped",
        ]:
            self.assertIn(expected, contract)
    def test_usage_doc_includes_allowed_stop_examples(self):
        usage = (REPO / "docs" / "usage" / "split-image-assets.md").read_text(
            encoding="utf-8"
        ).lower()

        for expected in [
            "external blocker",
            "semantic divergence",
            "formal approval",
        ]:
            self.assertIn(expected, usage)
    def test_usage_gate_list_matches_allowed_gate_taxonomy(self):
        usage = (REPO / "docs" / "usage" / "split-image-assets.md").read_text(
            encoding="utf-8"
        )

        for expected in [
            "Preflight Tooling Recommendation Gate",
            "Granularity Alignment Gate",
            "Generation Routing Gate",
            "Pilot Object Gate",
            "Approximate Reconstruction Acceptance Gate",
            "Final Acceptance Gate",
            "Candidate Promotion Acceptance Gate",
        ]:
            self.assertIn(expected, usage)

        for retired in [
            "Carrier/Glyph Split Gate",
            "Final Promotion Acceptance Gate",
        ]:
            self.assertNotIn(retired, usage)



