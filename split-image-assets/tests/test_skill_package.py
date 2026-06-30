import importlib.util
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest

from PIL import Image


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT.parent


class SplitImageAssetsPackageTests(unittest.TestCase):
    def _assert_text_in_file(self, relative_path: pathlib.Path, expected_fragments: list[str]):
        text = relative_path.read_text(encoding="utf-8")
        for fragment in expected_fragments:
            self.assertIn(fragment, text)

    def _assert_any_regex_matches(self, text: str, patterns: list[str]):
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return
        self.fail(f"none of the expected patterns matched: {patterns}")

    def _load_check_environment_module(self):
        module_path = ROOT / "scripts" / "check_extraction_environment.py"
        spec = importlib.util.spec_from_file_location("check_extraction_environment", module_path)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module

    def _load_script_module(self, script_name: str):
        module_path = ROOT / "scripts" / script_name
        spec = importlib.util.spec_from_file_location(script_name.replace(".py", ""), module_path)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        scripts_dir = str((ROOT / "scripts").resolve())
        had_scripts_dir = scripts_dir in sys.path
        if not had_scripts_dir:
            sys.path.insert(0, scripts_dir)
        try:
            spec.loader.exec_module(module)
        finally:
            if not had_scripts_dir:
                sys.path.remove(scripts_dir)
        return module

    def _run_init(self, source: pathlib.Path, output: pathlib.Path, package_name: str = "fixture"):
        return subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "init_asset_package.py"),
                str(source),
                str(output),
                "--package-name",
                package_name,
            ],
            text=True,
            capture_output=True,
            check=False,
        )

    def _write_single_object_metadata(
        self,
        package_dir: pathlib.Path,
        include_analysis: bool = True,
        include_pipeline: bool = True,
        include_quality_evidence: bool = True,
    ) -> dict:
        metadata_path = package_dir / "metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if include_analysis:
            metadata["analysis"] = {
                "visual_hierarchy": [
                    "background",
                    "main object",
                    "inspection layer",
                ],
                "recommended_split_plan": "Keep the main object separate from the background.",
            }
        if include_pipeline:
            metadata["extraction_pipeline"] = {
                "recipe": "grounded-segmentation-matting-repair",
                "stages": [
                    "semantic-analysis",
                    "detection",
                    "segmentation",
                    "alpha-refinement",
                    "background-repair",
                    "layer-packaging",
                    "qa-review",
                ],
                "quality_gates": [
                    "mask provenance recorded",
                    "alpha provenance recorded",
                    "edge quality inspected",
                    "reuse preview inspected",
                ],
                "tools": [
                    {
                        "name": "manual-fixture",
                        "role": "test asset creation",
                        "version": "local",
                    }
                ],
            }
        metadata["granularity"] = {
            "mode": "atomic-layer",
            "user_confirmed": True,
            "notes": "Test fixture confirmed atomic split granularity.",
            "scope_strategy": "unset",
            "text_handling": "unset",
            "carrier_glyph_policy": "unset",
            "background_expectation": "unset",
            "layer_independence": "unset",
        }
        object_record = {
            "id": "main_object",
            "role": "main",
            "layer_kind": "primary-subject",
            "composition_order": 10,
            "semantic_boundary": "The whole red fixture object separated from the background.",
            "asset_path": "assets/main_object_transparent.png",
            "mask_path": "masks/mask_main.png",
            "mask_source": "manual",
            "alpha_source": "manual-rgba",
            "bbox": {"x": 0, "y": 0, "width": 4, "height": 3},
            "width": 4,
            "height": 3,
            "aspect_ratio": 4 / 3,
            "area_ratio": 1.0,
            "extraction_method": "manual",
            "confidence": "high",
            "edge_complexity": "hard",
            "manual_review_flags": [],
            "asset_class": "atomic",
            "reuse_status": "production-ready",
            "delivery_class": "clean-extraction",
            "current_asset_revision": "initial-import",
            "selected_candidate_id": "",
            "repair_history": [],
            "active_reconstruction_method": "",
            "value_scoring": {
                "editability_score": "unset",
                "visual_complexity_score": "unset",
                "asset_value_score": "unset",
                "scoring_reason": "",
            },
            "decision_routing": {
                "recommended_action": "unset",
                "final_action": "unset",
                "decision_source": "unset",
            },
            "rebuild_intent": {
                "rebuildable_downstream": False,
                "rebuild_notes": "",
            },
            "text_semantics": {
                "text_role": "non-text",
                "text_render_class": "non-text",
            },
        }
        if include_quality_evidence:
            object_record["quality_checks"] = {
                "mask_alignment": "pass",
                "alpha_edges": "pass",
                "background_residue": "pass",
                "reuse_readiness": "pass",
            }
        metadata["capability"] = {
            "production_capable": True,
            "missing_for_production": [],
            "user_choice": "production-capable",
            "notes": "Test fixture uses production-capable upstream evidence.",
        }
        metadata["quality_target"] = {
            "tier": "visual-acceptance-ready",
            "notes": "Test fixture targets final visual acceptance.",
        }
        metadata["objects"] = [
            object_record
        ]
        metadata["audit"] = {}
        metadata_path.write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return metadata

    def _write_ready_validation_package(self, output: pathlib.Path) -> dict:
        metadata = self._write_single_object_metadata(output)
        metadata["decision_log"] = [
            {
                "stage": "final-acceptance",
                "pause_category": "formal-approval",
                "question": "Accept this layer?",
                "recommended_answer": "yes",
                "recorded_answer": "yes",
                "decision_effect": "Allow pass.",
                "decision_source": "explicit-user-confirmed",
                "evidence_ref": "",
                "blocking": "true",
            }
        ]
        metadata["confirmation"]["tooling_preflight"].update(
            {
                "status": "confirmed",
                "source": "inferred-from-user",
                "pause_category": "external-blocker",
                "evidence_ref": "chat:tooling-approved",
            }
        )
        metadata["confirmation"]["granularity_alignment"].update(
            {
                "status": "confirmed",
                "source": "explicit-user-confirmed",
                "pause_category": "user-decision",
                "evidence_ref": "",
            }
        )
        metadata["confirmation"]["final_acceptance"].update(
            {
                "status": "confirmed",
                "source": "explicit-user-confirmed",
                "pause_category": "formal-approval",
                "evidence_ref": "",
            }
        )
        metadata["confirmation"]["candidate_promotion"] = {
            "status": "not-required",
            "source": "explicit-user-confirmed",
            "pause_category": "formal-approval",
            "notes": "",
            "evidence_ref": "",
        }
        previews_dir = output / "previews"
        Image.new("RGBA", (4, 3), (240, 240, 240, 255)).save(
            previews_dir / "main_object_whitebg.png"
        )
        Image.new("RGBA", (4, 3), (180, 180, 180, 255)).save(
            previews_dir / "main_object_checkerboard.png"
        )
        Image.new("RGBA", (4, 3), (120, 120, 120, 255)).save(
            previews_dir / "main_object_mask_overlay.png"
        )
        Image.new("RGBA", (4, 3), (200, 200, 255, 255)).save(
            previews_dir / "main_object_alpha_inspection.png"
        )
        Image.new("RGBA", (8, 6), (220, 220, 220, 255)).save(
            previews_dir / "overview_decomposition.png"
        )
        Image.new("RGBA", (8, 6), (210, 210, 210, 255)).save(
            previews_dir / "sprite_sheet_2x2.png"
        )
        metadata["previews"] = {
            "main_object": {
                "whitebg": "previews/main_object_whitebg.png",
                "checkerboard": "previews/main_object_checkerboard.png",
            },
            "quality": {
                "main_object": {
                    "mask_overlay": "previews/main_object_mask_overlay.png",
                    "alpha_inspection": "previews/main_object_alpha_inspection.png",
                }
            },
            "overview_decomposition": "previews/overview_decomposition.png",
            "sprite_sheet_2x2": "previews/sprite_sheet_2x2.png",
        }
        (output / "metadata.json").write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return metadata

    def test_required_skill_files_are_present(self):
        required_paths = [
            ROOT / "SKILL.md",
            ROOT / "agents" / "openai.yaml",
            ROOT / "references" / "workflow.md",
            ROOT / "references" / "pipeline-recipes.md",
            ROOT / "references" / "quick-contract.md",
            ROOT / "references" / "asset-package-contract.md",
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
            ROOT / "scripts" / "archive_intermediates.py",
            ROOT / "scripts" / "generate_ui_carrier_candidates.py",
            ROOT / "scripts" / "generate_ui_glyph_cleanup_candidates.py",
            ROOT / "scripts" / "record_quality_review.py",
            ROOT / "scripts" / "score_candidate_assets.py",
            ROOT / "scripts" / "upscale_repair_downscale.py",
            ROOT / "scripts" / "export_asset_manifest.py",
            ROOT / "scripts" / "validate_asset_package.py",
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
        self.assertIn("single governing design document", design)
        self.assertIn("single implementation plan", plan)
        self.assertIn("documentation-system migration", migration)

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
            "production-ready assets",
            "draft candidate assets",
            "support-only layers",
        ]:
            self.assertIn(expected, quick_contract)

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
            "archive_intermediates.py",
            "export_asset_manifest.py",
            "`qa.status=pass` requires `metadata.capability.production_capable=true`",
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

    def test_check_extraction_environment_reports_capability_gate_json(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "check_extraction_environment.py"),
                "--json",
            ],
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertIn("python", report)
        self.assertIn("tools", report)
        self.assertIn("segmentation", report)
        self.assertIn("matting", report)
        self.assertIn("reconstruction", report)
        self.assertIn("environment", report)
        self.assertIn("recommended_recipe", report)
        self.assertIn("recommended_next_action", report)
        self.assertIn("production_capable", report)
        self.assertIn("missing_for_production", report)
        self.assertIn("upstream_roles", report)
        self.assertIn("preflight_tooling_recommendation_gate", report)
        self.assertIn("Pillow", report["tools"])
        self.assertIn("segmentation", report["upstream_roles"])
        self.assertIn("quality_impact", report["upstream_roles"]["alpha_refinement"])
        self.assertIn("user_choices", report["preflight_tooling_recommendation_gate"])
        self.assertIn(report["tools"]["Pillow"]["available"], [True, False])
        self.assertIn(report["production_capable"], [True, False])
        self.assertIsInstance(report["missing_for_production"], list)
        self.assertIn(
            report["recommended_next_action"],
            ["install-or-activate-tools", "external-professional-outputs", "production-capable"],
        )
        for capability_key in ["segmentation", "matting", "reconstruction"]:
            self.assertIn("installed", report[capability_key])
            self.assertIn("runtime_ready", report[capability_key])
            self.assertIn("production_ready", report[capability_key])
        self.assertIn("path_type", report["reconstruction"])
        self.assertIn("quality_impact", report["reconstruction"])
        self.assertIn("recommended_next_action_detail", report)
        self.assertIn("recommended_installs", report)
        self.assertIn("missing_roles", report)
        self.assertIn("why_it_matters", report)
        self.assertIn("torch", report["environment"])
        self.assertIn("cuda", report["environment"])
        self.assertIn("onnxruntime", report["environment"])

    def test_build_reconstruction_capability_keeps_runtime_only_path_non_production(self):
        module = self._load_check_environment_module()
        reconstruction = module.build_reconstruction_capability(
            {
                "installed": True,
                "runtime_ready": True,
                "version": "2.0",
                "cuda_available": False,
                "cuda_device_count": 0,
            },
            {"installed": True, "runtime_ready": True, "version": "1.0"},
            {"installed": False, "runtime_ready": False, "module": "iopaint"},
            {"installed": False, "runtime_ready": False, "module": "saicinpainting"},
        )
        self.assertFalse(reconstruction["production_ready"])
        self.assertEqual(reconstruction["path_type"], "manual-redraw-only")
        self.assertTrue(reconstruction["manual_redraw_required"])
        self.assertTrue(reconstruction["requires_user_acceptance"])

    def test_build_reconstruction_capability_treats_broken_dedicated_tool_as_manual_only(self):
        module = self._load_check_environment_module()
        reconstruction = module.build_reconstruction_capability(
            {
                "installed": True,
                "runtime_ready": True,
                "version": "2.0",
                "cuda_available": False,
                "cuda_device_count": 0,
            },
            {"installed": True, "runtime_ready": True, "version": "1.0"},
            {"installed": True, "runtime_ready": False, "module": "iopaint", "error": "import failed"},
            {"installed": False, "runtime_ready": False, "module": "saicinpainting"},
        )
        self.assertFalse(reconstruction["production_ready"])
        self.assertEqual(reconstruction["path_type"], "manual-redraw-only")
        self.assertTrue(reconstruction["installed"])
        self.assertIn("not runtime-ready", reconstruction["quality_impact"])

    def test_init_asset_package_creates_standard_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (255, 0, 0, 255)).save(source)
            output = tmp_path / "package"

            result = self._run_init(source, output)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((output / "source" / "source_original.png").exists())
            self.assertTrue((output / "assets").is_dir())
            self.assertTrue((output / "masks").is_dir())
            self.assertTrue((output / "previews").is_dir())
            self.assertTrue((output / "_staging").is_dir())
            self.assertTrue((output / "_archive_intermediate").is_dir())
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["package_name"], "fixture")
            self.assertEqual(metadata["source"]["width"], 4)
            self.assertEqual(metadata["source"]["height"], 3)
            self.assertEqual(metadata["granularity"]["mode"], "unset")
            self.assertFalse(metadata["granularity"]["user_confirmed"])
            self.assertEqual(metadata["granularity"]["scope_strategy"], "unset")
            self.assertEqual(metadata["granularity"]["text_handling"], "unset")
            self.assertEqual(metadata["granularity"]["carrier_glyph_policy"], "unset")
            self.assertEqual(metadata["granularity"]["background_expectation"], "unset")
            self.assertEqual(metadata["granularity"]["layer_independence"], "unset")
            self.assertEqual(
                metadata["capability"],
                {
                    "production_capable": False,
                    "missing_for_production": [],
                    "user_choice": "unset",
                    "notes": "",
                },
            )
            self.assertEqual(
                metadata["quality_target"],
                {
                    "tier": "structural-valid",
                    "notes": "",
                },
            )
            self.assertEqual(
                metadata["confirmation"],
                {
                    "tooling_preflight": {
                        "status": "pending",
                        "source": "unset",
                        "pause_category": "external-blocker",
                        "notes": "",
                        "evidence_ref": "",
                    },
                    "granularity_alignment": {
                        "status": "pending",
                        "source": "unset",
                        "pause_category": "user-decision",
                        "notes": "",
                        "evidence_ref": "",
                    },
                    "pilot_object": {
                        "status": "pending",
                        "source": "unset",
                        "pause_category": "formal-approval",
                        "object_id": "",
                        "notes": "",
                        "evidence_ref": "",
                    },
                    "approximate_reconstruction": {
                        "status": "pending",
                        "source": "unset",
                        "pause_category": "user-decision",
                        "notes": "",
                        "evidence_ref": "",
                    },
                    "final_acceptance": {
                        "status": "pending",
                        "source": "unset",
                        "pause_category": "formal-approval",
                        "notes": "",
                        "evidence_ref": "",
                    },
                    "candidate_promotion": {
                        "status": "pending",
                        "source": "unset",
                        "pause_category": "formal-approval",
                        "notes": "",
                        "evidence_ref": "",
                    },
                },
            )
            self.assertEqual(metadata["decision_log"], [])
            self.assertEqual(metadata["audit"], {})
            self.assertEqual(metadata["qa"]["status"], "needs-review")
            self.assertEqual(metadata["asset_summary"]["production_ready_assets"], 0)
            self.assertEqual(metadata["asset_summary"]["draft_candidate_assets"], 0)
            self.assertEqual(metadata["asset_summary"]["support_only_layers"], 0)
            self.assertIn(
                "Final status: needs-review",
                (output / "qa_report.md").read_text(encoding="utf-8"),
            )

    def test_record_quality_review_defaults_approximate_reconstruction_to_user_decision(self):
        review_script = (ROOT / "scripts" / "record_quality_review.py").read_text(encoding="utf-8")
        self.assertIn("from split_image_assets_contract import (", review_script)
        review = self._load_script_module("record_quality_review.py")
        self.assertEqual(
            review.DEFAULT_PAUSE_CATEGORY_BY_CONFIRMATION["approximate_reconstruction"],
            "user-decision",
        )

    def test_shared_contract_module_defines_confirmation_pause_defaults(self):
        contract = self._load_script_module("split_image_assets_contract.py")
        self.assertEqual(
            contract.DEFAULT_PAUSE_CATEGORY_BY_CONFIRMATION["approximate_reconstruction"],
            "user-decision",
        )
        self.assertEqual(
            contract.DEFAULT_PAUSE_CATEGORY_BY_CONFIRMATION["tooling_preflight"],
            "external-blocker",
        )
        self.assertEqual(
            contract.DEFAULT_PAUSE_CATEGORY_BY_CONFIRMATION["granularity_alignment"],
            "user-decision",
        )

    def test_record_quality_review_uses_shared_confirmation_contract(self):
        contract = self._load_script_module("split_image_assets_contract.py")
        review_script = (ROOT / "scripts" / "record_quality_review.py").read_text(encoding="utf-8")
        self.assertIn("from split_image_assets_contract import (", review_script)
        review = self._load_script_module("record_quality_review.py")
        self.assertEqual(
            review.DEFAULT_PAUSE_CATEGORY_BY_CONFIRMATION,
            contract.DEFAULT_PAUSE_CATEGORY_BY_CONFIRMATION,
        )

    def test_shared_contract_module_defines_asset_routing_taxonomy(self):
        contract = self._load_script_module("split_image_assets_contract.py")

        self.assertIn("rebuild_downstream", contract.ALLOWED_ROUTING_ACTIONS)
        self.assertIn("requires_user_confirmation", contract.ALLOWED_ROUTING_ACTIONS)
        self.assertIn("plain-text", contract.ALLOWED_TEXT_ROLES)
        self.assertIn("decorative-text", contract.ALLOWED_TEXT_ROLES)
        self.assertIn("editable", contract.ALLOWED_TEXT_RENDER_CLASSES)
        self.assertIn("visual-fidelity-critical", contract.ALLOWED_TEXT_RENDER_CLASSES)
        self.assertIn("plain-text", contract.ORDINARY_TEXT_ROLES)
        self.assertIn("button-label", contract.ORDINARY_TEXT_ROLES)

    def test_record_quality_review_and_validator_share_routing_contract(self):
        contract = self._load_script_module("split_image_assets_contract.py")
        review = self._load_script_module("record_quality_review.py")
        validator = self._load_script_module("validate_asset_package.py")

        self.assertEqual(review.ALLOWED_GRANULARITY_MODES, contract.ALLOWED_GRANULARITY_MODES)
        self.assertEqual(review.ALLOWED_TEXT_ROLES, contract.ALLOWED_TEXT_ROLES)
        self.assertEqual(review.ALLOWED_TEXT_RENDER_CLASSES, contract.ALLOWED_TEXT_RENDER_CLASSES)
        self.assertEqual(review.ALLOWED_ROUTING_ACTIONS, contract.ALLOWED_ROUTING_ACTIONS)
        self.assertEqual(review.ALLOWED_OBJECT_TYPES, contract.ALLOWED_OBJECT_TYPES)
        self.assertEqual(review.ALLOWED_QUALITY_TARGET_TIERS, contract.ALLOWED_QUALITY_TARGET_TIERS)
        self.assertEqual(validator.ALLOWED_GRANULARITY_MODES, contract.ALLOWED_GRANULARITY_MODES)
        self.assertEqual(validator.ALLOWED_TEXT_ROLES, contract.ALLOWED_TEXT_ROLES)
        self.assertEqual(
            validator.ALLOWED_TEXT_RENDER_CLASSES,
            contract.ALLOWED_TEXT_RENDER_CLASSES,
        )
        self.assertEqual(validator.ALLOWED_ROUTING_ACTIONS, contract.ALLOWED_ROUTING_ACTIONS)
        self.assertEqual(validator.ALLOWED_OBJECT_TYPES, contract.ALLOWED_OBJECT_TYPES)
        self.assertEqual(
            validator.ALLOWED_QUALITY_TARGET_TIERS,
            contract.ALLOWED_QUALITY_TARGET_TIERS,
        )

    def test_build_previews_creates_inspection_images(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            self._write_single_object_metadata(output)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_previews.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((output / "previews" / "main_object_whitebg.png").exists())
            self.assertTrue((output / "previews" / "main_object_checkerboard.png").exists())
            self.assertTrue((output / "previews" / "overview_decomposition.png").exists())
            self.assertTrue((output / "previews" / "sprite_sheet_2x2.png").exists())
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(
                metadata["previews"]["main_object"]["whitebg"],
                "previews/main_object_whitebg.png",
            )
            self.assertEqual(
                metadata["previews"]["sprite_sheet_2x2"],
                "previews/sprite_sheet_2x2.png",
            )

    def test_init_asset_package_object_schema_supports_value_scoring_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")

            metadata = self._write_single_object_metadata(output)
            obj = metadata["objects"][0]
            self.assertIn("value_scoring", obj)
            self.assertIn("decision_routing", obj)
            self.assertIn("rebuild_intent", obj)
            self.assertIn("text_semantics", obj)

    def test_import_external_assets_supports_manifest_batch_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (6, 6), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            asset_a = tmp_path / "tile.png"
            asset_b = tmp_path / "glyph.png"
            mask_a = tmp_path / "tile_mask.png"
            mask_b = tmp_path / "glyph_mask.png"
            Image.new("RGBA", (2, 2), (80, 100, 120, 255)).save(asset_a)
            Image.new("RGBA", (2, 2), (255, 255, 255, 220)).save(asset_b)
            Image.new("L", (6, 6), 255).save(mask_a)
            Image.new("L", (6, 6), 255).save(mask_b)

            manifest_path = tmp_path / "import_manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "recipe": "grounded-segmentation-matting-repair",
                        "tool": {
                            "name": "SAM2",
                            "role": "segmentation",
                            "version": "external",
                        },
                        "objects": [
                            {
                                "object_id": "status_tile",
                                "role": "secondary",
                                "layer_kind": "icon-tile",
                                "composition_order": 10,
                                "semantic_boundary": "Carrier tile for UI status icon.",
                                "asset": str(asset_a),
                                "mask": str(mask_a),
                                "mask_source": "sam2",
                                "alpha_source": "rembg-refine",
                            },
                            {
                                "object_id": "status_glyph",
                                "role": "secondary",
                                "layer_kind": "glyph",
                                "composition_order": 20,
                                "semantic_boundary": "Foreground glyph for UI status icon.",
                                "asset": str(asset_b),
                                "mask": str(mask_b),
                                "mask_source": "sam2",
                                "alpha_source": "rembg-refine",
                            },
                        ],
                    },
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "import_external_assets.py"),
                    str(output),
                    "--manifest",
                    str(manifest_path),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(len(metadata["objects"]), 2)
            self.assertEqual(metadata["objects"][0]["id"], "status_tile")
            self.assertEqual(metadata["objects"][1]["id"], "status_glyph")
            self.assertEqual(metadata["extraction_pipeline"]["tools"][0]["name"], "SAM2")
            self.assertEqual(metadata["objects"][0]["asset_class"], "candidate")
            self.assertEqual(metadata["objects"][0]["reuse_status"], "draft-candidate")

    def test_import_external_assets_rejects_manifest_without_tool_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (6, 6), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            asset = tmp_path / "tile.png"
            mask = tmp_path / "tile_mask.png"
            Image.new("RGBA", (2, 2), (80, 100, 120, 255)).save(asset)
            Image.new("L", (6, 6), 255).save(mask)

            manifest_path = tmp_path / "import_manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "recipe": "grounded-segmentation-matting-repair",
                        "tool": {"name": "", "role": "segmentation", "version": "external"},
                        "objects": [
                            {
                                "object_id": "status_tile",
                                "role": "secondary",
                                "layer_kind": "icon-tile",
                                "composition_order": 10,
                                "semantic_boundary": "Carrier tile.",
                                "asset": str(asset),
                                "mask": str(mask),
                                "mask_source": "sam2",
                                "alpha_source": "rembg-refine",
                            }
                        ],
                    },
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "import_external_assets.py"),
                    str(output),
                    "--manifest",
                    str(manifest_path),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("manifest.tool.name", result.stderr)
            self.assertFalse((output / "assets" / "status_tile_transparent.png").exists())

    def test_import_external_assets_batch_import_fails_before_partial_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (6, 6), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            asset_a = tmp_path / "tile.png"
            asset_b = tmp_path / "glyph.png"
            mask_a = tmp_path / "tile_mask.png"
            mask_b = tmp_path / "glyph_mask.png"
            Image.new("RGBA", (2, 2), (80, 100, 120, 255)).save(asset_a)
            Image.new("RGBA", (2, 2), (255, 255, 255, 220)).save(asset_b)
            Image.new("L", (6, 6), 255).save(mask_a)
            Image.new("L", (2, 2), 255).save(mask_b)

            manifest_path = tmp_path / "import_manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "recipe": "grounded-segmentation-matting-repair",
                        "tool": {
                            "name": "SAM2",
                            "role": "segmentation",
                            "version": "external",
                        },
                        "objects": [
                            {
                                "object_id": "status_tile",
                                "role": "secondary",
                                "layer_kind": "icon-tile",
                                "composition_order": 10,
                                "semantic_boundary": "Carrier tile.",
                                "asset": str(asset_a),
                                "mask": str(mask_a),
                                "mask_source": "sam2",
                                "alpha_source": "rembg-refine",
                            },
                            {
                                "object_id": "status_glyph",
                                "role": "secondary",
                                "layer_kind": "glyph",
                                "composition_order": 20,
                                "semantic_boundary": "Foreground glyph.",
                                "asset": str(asset_b),
                                "mask": str(mask_b),
                                "mask_source": "sam2",
                                "alpha_source": "rembg-refine",
                            },
                        ],
                    },
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "import_external_assets.py"),
                    str(output),
                    "--manifest",
                    str(manifest_path),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source-space mask dimensions", result.stderr)
            self.assertFalse((output / "assets" / "status_tile_transparent.png").exists())
            self.assertFalse((output / "assets" / "status_glyph_transparent.png").exists())

    def test_archive_intermediates_moves_staging_files_and_writes_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            staging_dir = output / "_staging" / "sam-run"
            staging_dir.mkdir(parents=True)
            (staging_dir / "candidate_mask.png").write_bytes(b"mask")
            (output / "_staging" / "sam_subset_manifest.json").write_text("{}", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "archive_intermediates.py"),
                    str(output),
                    "--run-id",
                    "sam-subset-001",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            archive_root = output / "_archive_intermediate" / "sam-subset-001"
            self.assertTrue((archive_root / "sam-run" / "candidate_mask.png").exists())
            self.assertTrue((archive_root / "sam_subset_manifest.json").exists())
            self.assertFalse(any((output / "_staging").iterdir()))
            manifest = json.loads((archive_root / "archive_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["run_id"], "sam-subset-001")
            self.assertIn("sam-run/candidate_mask.png", manifest["archived_paths"])

    def test_archive_intermediates_updates_audit_metadata_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (6, 6), (20, 20, 20, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 4), (255, 0, 0, 255)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (6, 6), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0]["asset_class"] = "candidate"
            metadata["objects"][0]["reuse_status"] = "draft-candidate"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            audit_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "audit_visual_quality.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(audit_result.returncode, 0, audit_result.stderr)

            archive_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "archive_intermediates.py"),
                    str(output),
                    "--run-id",
                    "audit-001",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(archive_result.returncode, 0, archive_result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(
                metadata["audit"]["quality_audit_path"],
                "_archive_intermediate/audit-001/quality/quality_audit.json",
            )
            self.assertEqual(
                metadata["previews"]["qa_audit_contact_sheet"],
                "_archive_intermediate/audit-001/quality/qa_audit_contact_sheet.png",
            )

    def test_archive_intermediates_updates_candidate_comparison_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (6, 6), (20, 20, 20, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 4), (255, 0, 0, 255)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (6, 6), 255).save(output / "masks" / "mask_main.png")
            self._write_single_object_metadata(output)
            candidate_dir = output / "_staging" / "repair_candidates"
            candidate_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (4, 4), (0, 255, 0, 255)).save(candidate_dir / "candidate_a.png")
            Image.new("RGBA", (4, 4), (0, 0, 255, 255)).save(candidate_dir / "candidate_b.png")

            compare_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "compare_candidate_assets.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate",
                    "candidate-a=_staging/repair_candidates/candidate_a.png",
                    "--candidate",
                    "candidate-b=_staging/repair_candidates/candidate_b.png",
                    "--compare-note",
                    "Archive compare evidence after creation.",
                    "--compare-criterion",
                    "edge cleanliness",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(compare_result.returncode, 0, compare_result.stderr)

            archive_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "archive_intermediates.py"),
                    str(output),
                    "--run-id",
                    "compare-001",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(archive_result.returncode, 0, archive_result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            comparison = metadata["objects"][0]["candidate_comparisons"][0]
            self.assertTrue(
                comparison["compare_artifact_path"].startswith(
                    "_archive_intermediate/compare-001/repair_candidates/"
                )
            )
            self.assertTrue(comparison["compare_artifact_path"].endswith("_compare.png"))
            self.assertTrue(
                comparison["compare_manifest_path"].startswith(
                    "_archive_intermediate/compare-001/repair_candidates/"
                )
            )
            self.assertTrue(comparison["compare_manifest_path"].endswith("_compare.json"))

    def test_compare_candidate_assets_writes_artifact_and_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (6, 6), (20, 20, 20, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 4), (255, 0, 0, 255)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (6, 6), 255).save(output / "masks" / "mask_main.png")
            self._write_single_object_metadata(output)
            candidate_dir = output / "_staging" / "repair_candidates"
            candidate_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (4, 4), (0, 255, 0, 255)).save(candidate_dir / "candidate_a.png")
            Image.new("RGBA", (4, 4), (0, 0, 255, 255)).save(candidate_dir / "candidate_b.png")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "compare_candidate_assets.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate",
                    "candidate-a=_staging/repair_candidates/candidate_a.png",
                    "--candidate",
                    "candidate-b=_staging/repair_candidates/candidate_b.png",
                    "--compare-note",
                    "Compare edge cleanliness and carrier shape fidelity.",
                    "--compare-criterion",
                    "edge cleanliness",
                    "--compare-criterion",
                    "shape fidelity",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            comparisons = metadata["objects"][0]["candidate_comparisons"]
            self.assertEqual(len(comparisons), 1)
            self.assertEqual(comparisons[0]["candidate_ids"], ["candidate-a", "candidate-b"])
            self.assertTrue((output / comparisons[0]["compare_artifact_path"]).exists())
            self.assertTrue((output / comparisons[0]["compare_manifest_path"]).exists())
            self.assertEqual(comparisons[0]["compare_criteria"], ["edge cleanliness", "shape fidelity"])

    def test_compare_candidate_assets_requires_criterion(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (6, 6), (20, 20, 20, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 4), (255, 0, 0, 255)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (6, 6), 255).save(output / "masks" / "mask_main.png")
            self._write_single_object_metadata(output)
            candidate_dir = output / "_staging" / "repair_candidates"
            candidate_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (4, 4), (0, 255, 0, 255)).save(candidate_dir / "candidate_a.png")
            Image.new("RGBA", (4, 4), (0, 0, 255, 255)).save(candidate_dir / "candidate_b.png")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "compare_candidate_assets.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate",
                    "candidate-a=_staging/repair_candidates/candidate_a.png",
                    "--candidate",
                    "candidate-b=_staging/repair_candidates/candidate_b.png",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--compare-criterion", result.stderr)

    def test_score_candidate_assets_writes_required_scores(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (8, 8), (20, 20, 20, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 4), (255, 0, 0, 255)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (8, 8), 255).save(output / "masks" / "mask_main.png")
            self._write_single_object_metadata(output)
            candidate_dir = output / "_staging" / "repair_candidates"
            candidate_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (4, 4), (255, 0, 0, 255)).save(candidate_dir / "candidate_a.png")
            Image.new("RGBA", (4, 4), (200, 0, 0, 255)).save(candidate_dir / "candidate_b.png")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "score_candidate_assets.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate",
                    "candidate-a=_staging/repair_candidates/candidate_a.png",
                    "--candidate",
                    "candidate-b=_staging/repair_candidates/candidate_b.png",
                    "--reference-asset",
                    "assets/main_object_transparent.png",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            manifest_path = output / report["score_manifest_path"]
            self.assertTrue(manifest_path.exists())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(
                manifest["required_score_keys"],
                [
                    "edge_touch_risk",
                    "detached_fragment_risk",
                    "carrier_residue_risk",
                    "glyph_residue_risk",
                    "border_preservation_score",
                    "texture_match_score",
                    "flatness_risk",
                    "style_mismatch_risk",
                ],
            )
            self.assertEqual(len(manifest["candidates"]), 2)
            self.assertIn("scores", manifest["candidates"][0])

    def test_compare_candidate_assets_records_score_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (8, 8), (20, 20, 20, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 4), (255, 0, 0, 255)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (8, 8), 255).save(output / "masks" / "mask_main.png")
            self._write_single_object_metadata(output)
            candidate_dir = output / "_staging" / "repair_candidates"
            candidate_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (4, 4), (255, 0, 0, 255)).save(candidate_dir / "candidate_a.png")
            Image.new("RGBA", (4, 4), (200, 0, 0, 255)).save(candidate_dir / "candidate_b.png")

            score_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "score_candidate_assets.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate",
                    "candidate-a=_staging/repair_candidates/candidate_a.png",
                    "--candidate",
                    "candidate-b=_staging/repair_candidates/candidate_b.png",
                    "--reference-asset",
                    "assets/main_object_transparent.png",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(score_result.returncode, 0, score_result.stderr)
            score_report = json.loads(score_result.stdout)

            compare_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "compare_candidate_assets.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate",
                    "candidate-a=_staging/repair_candidates/candidate_a.png",
                    "--candidate",
                    "candidate-b=_staging/repair_candidates/candidate_b.png",
                    "--compare-note",
                    "Use scores to narrow the repair shortlist.",
                    "--compare-criterion",
                    "border preservation",
                    "--score-manifest",
                    score_report["score_manifest_path"],
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(compare_result.returncode, 0, compare_result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            comparison = metadata["objects"][0]["candidate_comparisons"][0]
            self.assertTrue(comparison["score_manifest_path"].endswith(".json"))
            compare_manifest = json.loads(
                (output / comparison["compare_manifest_path"]).read_text(encoding="utf-8")
            )
            self.assertEqual(compare_manifest["score_manifest_path"], comparison["score_manifest_path"])
            self.assertIn("aggregate_score", compare_manifest["candidates"][0])

    def test_import_external_assets_records_tool_provenance_and_layer_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            external_asset = tmp_path / "sam2_main.png"
            external_mask = tmp_path / "sam2_mask.png"
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(external_asset)
            Image.new("L", (4, 3), 255).save(external_mask)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "import_external_assets.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--role",
                    "main",
                    "--layer-kind",
                    "primary-subject",
                    "--composition-order",
                    "10",
                    "--semantic-boundary",
                    "Main subject mask produced by SAM2.",
                    "--asset",
                    str(external_asset),
                    "--mask",
                    str(external_mask),
                    "--mask-source",
                    "sam2",
                    "--alpha-source",
                    "rembg-refine",
                    "--tool-name",
                    "SAM2",
                    "--tool-role",
                    "segmentation",
                    "--tool-version",
                    "external",
                    "--recipe",
                    "grounded-segmentation-matting-repair",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((output / "assets" / "main_object_transparent.png").exists())
            self.assertTrue((output / "masks" / "mask_main_object.png").exists())
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["extraction_pipeline"]["recipe"], "grounded-segmentation-matting-repair")
            self.assertEqual(metadata["extraction_pipeline"]["tools"][0]["name"], "SAM2")
            self.assertEqual(metadata["objects"][0]["composition_order"], 10)
            self.assertEqual(metadata["objects"][0]["mask_source"], "sam2")
            self.assertEqual(metadata["objects"][0]["quality_checks"]["mask_alignment"], "needs-review")

    def test_import_external_assets_resets_stale_review_and_promotion_state_on_reimport(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            external_asset = tmp_path / "sam2_main.png"
            external_mask = tmp_path / "sam2_mask.png"
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(external_asset)
            Image.new("L", (4, 3), 255).save(external_mask)

            base_args = [
                sys.executable,
                str(ROOT / "scripts" / "import_external_assets.py"),
                str(output),
                "--object-id",
                "main_object",
                "--role",
                "main",
                "--layer-kind",
                "primary-subject",
                "--composition-order",
                "10",
                "--semantic-boundary",
                "Main subject mask produced by SAM2.",
                "--asset",
                str(external_asset),
                "--mask",
                str(external_mask),
                "--mask-source",
                "sam2",
                "--alpha-source",
                "rembg-refine",
                "--tool-name",
                "SAM2",
                "--tool-role",
                "segmentation",
                "--tool-version",
                "external",
                "--recipe",
                "grounded-segmentation-matting-repair",
            ]
            first_import = subprocess.run(
                base_args,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(first_import.returncode, 0, first_import.stderr)

            metadata_path = output / "metadata.json"
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            obj = metadata["objects"][0]
            obj["manual_review_confirmed"] = True
            obj["manual_review_notes"] = ["Human approved this crop after visual inspection."]
            obj["candidate_comparisons"] = [
                {
                    "comparison_id": "cmp-1",
                    "object_id": "main_object",
                    "candidate_ids": ["candidate-a"],
                    "compare_artifact_path": "_staging/compare_candidate_assets/cmp-1.png",
                    "compare_manifest_path": "_staging/compare_candidate_assets/cmp-1.json",
                    "review_focus": "Preserve approved repair evidence.",
                    "risks": ["edge-halo"],
                    "selected_candidate_id": "candidate-a",
                    "selection_reason": "Candidate A preserved the silhouette best.",
                    "created_at": "2026-06-29T00:00:00Z",
                }
            ]
            obj["selected_candidate_id"] = "candidate-a"
            obj["repair_history"] = [{"candidate_id": "candidate-a", "note": "Promoted"}]
            obj["current_asset_revision"] = "candidate-a"
            obj["active_reconstruction_method"] = "upscale_repair_downscale"
            obj["manual_review_flags"] = [
                "existing review flag",
                "external asset imported; inspect mask alignment and alpha edges",
            ]
            obj["quality_checks"] = {
                "mask_alignment": "pass",
                "alpha_edges": "pass",
                "background_residue": "pass",
                "reuse_readiness": "pass",
            }
            metadata_path.write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            replacement_asset = tmp_path / "sam2_main_v2.png"
            Image.new("RGBA", (4, 3), (0, 255, 0, 128)).save(replacement_asset)

            second_import = subprocess.run(
                [
                    *base_args[:14],
                    str(replacement_asset),
                    *base_args[15:],
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(second_import.returncode, 0, second_import.stderr)

            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            obj = metadata["objects"][0]
            self.assertNotIn("manual_review_confirmed", obj)
            self.assertNotIn("manual_review_notes", obj)
            self.assertEqual(obj["selected_candidate_id"], "")
            self.assertEqual(obj["repair_history"], [])
            self.assertEqual(obj["current_asset_revision"], "initial-import")
            self.assertEqual(obj["active_reconstruction_method"], "")
            self.assertEqual(
                obj["quality_checks"],
                {
                    "mask_alignment": "needs-review",
                    "alpha_edges": "needs-review",
                    "background_residue": "needs-review",
                    "reuse_readiness": "needs-review",
                },
            )
            self.assertEqual(obj["candidate_comparisons"], [])
            self.assertEqual(
                obj["manual_review_flags"],
                ["external asset imported; inspect mask alignment and alpha edges"],
            )
            self.assertEqual(obj["asset_class"], "candidate")
            self.assertEqual(obj["reuse_status"], "draft-candidate")
            self.assertEqual(obj["delivery_class"], "draft-candidate")

    def test_import_external_assets_requires_source_space_mask(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            external_asset = tmp_path / "sam2_main.png"
            tight_bbox_mask = tmp_path / "tight_bbox_mask.png"
            Image.new("RGBA", (2, 2), (255, 0, 0, 128)).save(external_asset)
            Image.new("L", (2, 2), 255).save(tight_bbox_mask)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "import_external_assets.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--role",
                    "main",
                    "--layer-kind",
                    "primary-subject",
                    "--composition-order",
                    "10",
                    "--semantic-boundary",
                    "Main subject mask produced by SAM2.",
                    "--asset",
                    str(external_asset),
                    "--mask",
                    str(tight_bbox_mask),
                    "--mask-source",
                    "sam2",
                    "--alpha-source",
                    "rembg-refine",
                    "--tool-name",
                    "SAM2",
                    "--tool-role",
                    "segmentation",
                    "--tool-version",
                    "external",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source-space mask", result.stderr)

    def test_record_quality_review_closes_manual_review_gap_after_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            external_asset = tmp_path / "sam2_main.png"
            external_mask = tmp_path / "sam2_mask.png"
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(external_asset)
            Image.new("L", (4, 3), 255).save(external_mask)

            import_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "import_external_assets.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--role",
                    "main",
                    "--layer-kind",
                    "primary-subject",
                    "--composition-order",
                    "10",
                    "--semantic-boundary",
                    "Main subject mask produced by SAM2.",
                    "--asset",
                    str(external_asset),
                    "--mask",
                    str(external_mask),
                    "--mask-source",
                    "sam2",
                    "--alpha-source",
                    "rembg-refine",
                    "--tool-name",
                    "SAM2",
                    "--tool-role",
                    "segmentation",
                    "--tool-version",
                    "external",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(import_result.returncode, 0, import_result.stderr)

            tooling_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_quality_review.py"),
                    str(output),
                    "--confirmation-key",
                    "tooling_preflight",
                    "--confirmation-status",
                    "confirmed",
                    "--confirmation-source",
                    "explicit-user-confirmed",
                    "--pause-category",
                    "external-blocker",
                    "--confirmation-note",
                    "External professional outputs were approved.",
                    "--production-capable",
                    "true",
                    "--capability-user-choice",
                    "production-capable",
                    "--capability-note",
                    "SAM2 and rembg external outputs were provided.",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(tooling_result.returncode, 0, tooling_result.stderr)

            granularity_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_quality_review.py"),
                    str(output),
                    "--granularity-mode",
                    "atomic-layer",
                    "--granularity-confirmed",
                    "--granularity-note",
                    "User approved isolated reusable object layers.",
                    "--confirmation-key",
                    "granularity_alignment",
                    "--confirmation-status",
                    "confirmed",
                    "--confirmation-source",
                    "explicit-user-confirmed",
                    "--pause-category",
                    "user-decision",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(granularity_result.returncode, 0, granularity_result.stderr)

            preview_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_previews.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(preview_result.returncode, 0, preview_result.stderr)
            quality_preview_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_quality_previews.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(quality_preview_result.returncode, 0, quality_preview_result.stderr)

            review_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_quality_review.py"),
                    str(output),
                    "--visual-hierarchy",
                    "background",
                    "--visual-hierarchy",
                    "main object",
                    "--recommended-split-plan",
                    "Keep the main object separate from the background.",
                    "--quality-target-tier",
                    "visual-acceptance-ready",
                    "--quality-target-note",
                    "Imported layer is ready for final visual acceptance.",
                    "--quality-gate",
                    "mask overlay inspected",
                    "--object-id",
                    "main_object",
                    "--asset-class",
                    "atomic",
                    "--reuse-status",
                    "production-ready",
                    "--mask-alignment",
                    "pass",
                    "--alpha-edges",
                    "pass",
                    "--background-residue",
                    "pass",
                    "--reuse-readiness",
                    "pass",
                    "--qa-status",
                    "pass",
                    "--decision-stage",
                    "final-acceptance",
                    "--decision-question",
                    "Accept this imported layer as production-ready?",
                    "--decision-recommended",
                    "yes",
                    "--decision-answer",
                    "yes",
                    "--decision-effect",
                    "Allow final pass and downstream reuse.",
                    "--decision-source",
                    "explicit-user-confirmed",
                    "--pause-category",
                    "formal-approval",
                    "--blocking",
                    "true",
                    "--review-note",
                    "Manual inspection accepted the imported layer.",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(review_result.returncode, 0, review_result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["analysis"]["visual_hierarchy"], ["background", "main object"])
            self.assertEqual(metadata["qa"]["status"], "pass")
            self.assertEqual(metadata["objects"][0]["quality_checks"]["reuse_readiness"], "pass")
            self.assertEqual(metadata["objects"][0]["asset_class"], "atomic")
            self.assertEqual(metadata["objects"][0]["reuse_status"], "production-ready")
            self.assertIn(
                "Manual inspection accepted the imported layer.",
                (output / "qa_report.md").read_text(encoding="utf-8"),
            )

    def test_record_quality_review_rejects_pass_when_target_checks_are_not_all_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0]["quality_checks"]["alpha_edges"] = "needs-review"
            metadata["qa"]["status"] = "needs-review"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_quality_review.py"),
                    str(output),
                    "--qa-status",
                    "pass",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("cannot set qa-status pass", result.stderr)

    def test_record_quality_review_rejects_pass_until_confirmation_and_preview_gates_are_satisfied(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["capability"] = {
                "production_capable": True,
                "missing_for_production": [],
                "user_choice": "production-capable",
                "notes": "User approved production-capable tooling.",
            }
            metadata["quality_target"] = {
                "tier": "visual-acceptance-ready",
                "notes": "Targeting final acceptance.",
            }
            metadata["decision_log"] = [
                {
                    "stage": "final-acceptance",
                    "pause_category": "formal-approval",
                    "question": "Accept this extracted layer?",
                    "recommended_answer": "yes",
                    "recorded_answer": "yes",
                    "decision_effect": "Allow pass after verification.",
                    "decision_source": "explicit-user-confirmed",
                    "evidence_ref": "",
                    "blocking": "true",
                }
            ]
            metadata["qa"]["status"] = "needs-review"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_quality_review.py"),
                    str(output),
                    "--qa-status",
                    "pass",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("tooling_preflight", result.stderr)
            self.assertIn("build_previews.py", result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["qa"]["status"], "needs-review")

    def test_record_quality_review_records_granularity_alignment(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_quality_review.py"),
                    str(output),
                    "--granularity-mode",
                    "atomic-layer",
                    "--granularity-confirmed",
                    "--granularity-note",
                    "User asked for atomic UI assets with live text deferred.",
                    "--scope-strategy",
                    "high-signal-subset",
                    "--text-handling",
                    "rebuild-downstream",
                    "--carrier-glyph-policy",
                    "split",
                    "--background-expectation",
                    "approximate-accepted",
                    "--layer-independence",
                    "animation-ready",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["granularity"]["mode"], "atomic-layer")
            self.assertTrue(metadata["granularity"]["user_confirmed"])
            self.assertIn("atomic UI assets", metadata["granularity"]["notes"])
            self.assertEqual(metadata["granularity"]["scope_strategy"], "high-signal-subset")
            self.assertEqual(metadata["granularity"]["text_handling"], "rebuild-downstream")
            self.assertEqual(metadata["granularity"]["carrier_glyph_policy"], "split")
            self.assertEqual(metadata["granularity"]["background_expectation"], "approximate-accepted")
            self.assertEqual(metadata["granularity"]["layer_independence"], "animation-ready")

    def test_record_quality_review_records_text_routing_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            self._write_single_object_metadata(output)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_quality_review.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--text-role",
                    "plain-text",
                    "--text-render-class",
                    "editable",
                    "--editability-score",
                    "high",
                    "--visual-complexity-score",
                    "low",
                    "--asset-value-score",
                    "low",
                    "--scoring-reason",
                    "Ordinary editable text.",
                    "--recommended-action",
                    "rebuild_downstream",
                    "--final-action",
                    "rebuild_downstream",
                    "--routing-decision-source",
                    "explicit-user-confirmed",
                    "--rebuildable-downstream",
                    "true",
                    "--rebuild-notes",
                    "Do not export a raster asset.",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            obj = metadata["objects"][0]
            self.assertEqual(obj["text_semantics"]["text_role"], "plain-text")
            self.assertEqual(obj["decision_routing"]["final_action"], "rebuild_downstream")
            self.assertTrue(obj["rebuild_intent"]["rebuildable_downstream"])

    def test_record_quality_review_rejects_routing_action_without_decision_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            self._write_single_object_metadata(output)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_quality_review.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--recommended-action",
                    "extract_asset",
                    "--final-action",
                    "extract_asset",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--routing-decision-source", result.stderr)

    def test_record_quality_review_records_confirmation_decision_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_quality_review.py"),
                    str(output),
                    "--decision-stage",
                    "semantic-split-plan",
                    "--decision-question",
                    "Split icon into tile and glyph?",
                    "--decision-recommended",
                    "yes",
                    "--decision-answer",
                    "yes",
                    "--decision-effect",
                    "Create separate carrier and glyph layers.",
                    "--decision-source",
                    "explicit-user-confirmed",
                    "--pause-category",
                    "user-decision",
                    "--blocking",
                    "true",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(len(metadata["decision_log"]), 1)
            entry = metadata["decision_log"][0]
            self.assertEqual(entry["stage"], "semantic-split-plan")
            self.assertEqual(entry["recommended_answer"], "yes")
            self.assertEqual(entry["recorded_answer"], "yes")
            self.assertEqual(entry["decision_source"], "explicit-user-confirmed")
            self.assertEqual(entry["pause_category"], "user-decision")
            self.assertEqual(entry["blocking"], "true")

    def test_record_quality_review_rejects_formal_gate_without_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_quality_review.py"),
                    str(output),
                    "--decision-stage",
                    "final-acceptance",
                    "--decision-question",
                    "Accept this package for pass?",
                    "--decision-recommended",
                    "yes",
                    "--decision-answer",
                    "yes",
                    "--decision-effect",
                    "Allow qa.status pass.",
                    "--pause-category",
                    "formal-approval",
                    "--blocking",
                    "true",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--decision-source", result.stderr)

    def test_record_quality_review_records_object_scoped_decision_log_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            self._write_single_object_metadata(output)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_quality_review.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--decision-stage",
                    "asset-value-scoring",
                    "--decision-question",
                    "Should this text-like object be rebuilt downstream or preserved as a visual asset?",
                    "--decision-recommended",
                    "rebuild downstream unless fidelity-critical",
                    "--decision-answer",
                    "preserve as visual asset",
                    "--decision-effect",
                    "Keep main_object as a visual asset after text review.",
                    "--decision-source",
                    "explicit-user-confirmed",
                    "--pause-category",
                    "user-decision",
                    "--blocking",
                    "true",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["decision_log"][0]["object_id"], "main_object")

    def test_record_quality_review_rejects_inferred_formal_gate_without_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_quality_review.py"),
                    str(output),
                    "--decision-stage",
                    "granularity-alignment",
                    "--decision-question",
                    "Use atomic-layer granularity?",
                    "--decision-recommended",
                    "yes",
                    "--decision-answer",
                    "yes",
                    "--decision-effect",
                    "Proceed with atomic-layer packaging.",
                    "--decision-source",
                    "inferred-from-user",
                    "--pause-category",
                    "user-decision",
                    "--blocking",
                    "true",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--evidence-ref", result.stderr)

    def test_record_quality_review_records_candidate_promotion_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_quality_review.py"),
                    str(output),
                    "--decision-stage",
                    "final-promotion-acceptance",
                    "--decision-question",
                    "Promote candidate v2 over the current revision?",
                    "--decision-recommended",
                    "yes",
                    "--decision-answer",
                    "yes",
                    "--decision-effect",
                    "Promote candidate v2 as the active revision.",
                    "--decision-source",
                    "explicit-user-confirmed",
                    "--pause-category",
                    "formal-approval",
                    "--blocking",
                    "true",
                    "--evidence-ref",
                    "chat:promotion-approved",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(
                metadata["confirmation"]["candidate_promotion"]["status"],
                "confirmed",
            )
            self.assertEqual(
                metadata["confirmation"]["candidate_promotion"]["pause_category"],
                "formal-approval",
            )
            self.assertEqual(metadata["decision_log"][0]["recorded_answer"], "yes")
            self.assertEqual(
                metadata["decision_log"][0]["evidence_ref"],
                "chat:promotion-approved",
            )

    def test_record_quality_review_records_confirmation_gate_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_quality_review.py"),
                    str(output),
                    "--decision-stage",
                    "granularity-alignment",
                    "--decision-question",
                    "Target atomic-layer granularity?",
                    "--decision-recommended",
                    "yes",
                    "--decision-answer",
                    "yes",
                    "--decision-effect",
                    "Proceed with atomic-layer plan.",
                    "--decision-source",
                    "inferred-from-user",
                    "--pause-category",
                    "user-decision",
                    "--blocking",
                    "true",
                    "--evidence-ref",
                    "chat:granularity-approved",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(
                metadata["confirmation"]["granularity_alignment"]["status"],
                "confirmed",
            )
            self.assertEqual(
                metadata["confirmation"]["granularity_alignment"]["source"],
                "inferred-from-user",
            )
            self.assertEqual(
                metadata["confirmation"]["granularity_alignment"]["evidence_ref"],
                "chat:granularity-approved",
            )

    def test_record_quality_review_rejects_confirmation_gate_without_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_quality_review.py"),
                    str(output),
                    "--confirmation-key",
                    "pilot_object",
                    "--confirmation-status",
                    "confirmed",
                    "--confirmation-object-id",
                    "status_glyph",
                    "--pause-category",
                    "formal-approval",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--confirmation-source", result.stderr)

    def test_record_quality_review_rejects_confirmation_gate_with_unset_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_quality_review.py"),
                    str(output),
                    "--confirmation-key",
                    "pilot_object",
                    "--confirmation-status",
                    "confirmed",
                    "--confirmation-source",
                    "unset",
                    "--confirmation-object-id",
                    "status_glyph",
                    "--pause-category",
                    "formal-approval",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("explicit-user-confirmed or inferred-from-user", result.stderr)

    def test_record_quality_review_rejects_pending_confirmation_with_non_unset_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_quality_review.py"),
                    str(output),
                    "--confirmation-key",
                    "pilot_object",
                    "--confirmation-status",
                    "pending",
                    "--confirmation-source",
                    "explicit-user-confirmed",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must be unset", result.stderr)

    def test_record_quality_review_records_tooling_preflight_capability(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_quality_review.py"),
                    str(output),
                    "--production-capable",
                    "false",
                    "--missing-for-production",
                    "SAM2 or grounded detector",
                    "--missing-for-production",
                    "matting/refinement",
                    "--capability-user-choice",
                    "draft-packaging-only",
                    "--capability-note",
                    "User chose draft package after tooling preflight.",
                    "--decision-stage",
                    "tooling-preflight",
                    "--decision-question",
                    "Install tools, provide external outputs, or continue draft-only?",
                    "--decision-recommended",
                    "Install or provide SAM2/Grounded-SAM plus rembg/BiRefNet/RMBG.",
                    "--decision-answer",
                    "continue draft-packaging-only",
                    "--decision-effect",
                    "Package must remain needs-review and cannot claim production extraction.",
                    "--decision-source",
                    "explicit-user-confirmed",
                    "--pause-category",
                    "external-blocker",
                    "--blocking",
                    "true",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertFalse(metadata["capability"]["production_capable"])
            self.assertEqual(metadata["capability"]["user_choice"], "draft-packaging-only")
            self.assertIn("matting/refinement", metadata["capability"]["missing_for_production"])
            self.assertEqual(metadata["decision_log"][0]["stage"], "tooling-preflight")
            self.assertEqual(metadata["confirmation"]["tooling_preflight"]["status"], "confirmed")

    def test_record_quality_review_rejects_pass_without_decision_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            self._write_single_object_metadata(output)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_quality_review.py"),
                    str(output),
                    "--all-objects",
                    "--mask-alignment",
                    "pass",
                    "--alpha-edges",
                    "pass",
                    "--background-residue",
                    "pass",
                    "--reuse-readiness",
                    "pass",
                    "--qa-status",
                    "pass",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("decision_log", result.stderr)

    def test_record_quality_review_rejects_confirmation_key_without_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_quality_review.py"),
                    str(output),
                    "--confirmation-key",
                    "pilot_object",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--confirmation-status", result.stderr)

    def test_record_quality_review_rejects_pass_for_draft_only_capability(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            self._write_single_object_metadata(output)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_quality_review.py"),
                    str(output),
                    "--production-capable",
                    "false",
                    "--capability-user-choice",
                    "draft-packaging-only",
                    "--capability-note",
                    "User chose draft package after tooling preflight.",
                    "--all-objects",
                    "--mask-alignment",
                    "pass",
                    "--alpha-edges",
                    "pass",
                    "--background-residue",
                    "pass",
                    "--reuse-readiness",
                    "pass",
                    "--qa-status",
                    "pass",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("production-capable", result.stderr)

    def test_record_quality_review_can_confirm_crop_only_layer_after_manual_inspection(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0]["mask_source"] = "bbox"
            metadata["objects"][0]["extraction_method"] = "estimated"
            metadata["objects"][0]["manual_review_confirmed"] = False
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_quality_review.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--confirm-crop-layer",
                    "--review-note",
                    "Human confirmed this estimated crop is acceptable for production reuse.",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertTrue(metadata["objects"][0]["manual_review_confirmed"])
            self.assertIn(
                "Human confirmed this estimated crop",
                metadata["objects"][0]["manual_review_notes"][0],
            )

    def test_build_quality_previews_creates_mask_overlay_and_records_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            self._write_single_object_metadata(output)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_quality_previews.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((output / "previews" / "main_object_mask_overlay.png").exists())
            self.assertTrue((output / "previews" / "main_object_alpha_inspection.png").exists())
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(
                metadata["previews"]["quality"]["main_object"]["mask_overlay"],
                "previews/main_object_mask_overlay.png",
            )

    def test_import_external_assets_rejects_invalid_metadata_before_copying_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            external_asset = tmp_path / "sam2_main.png"
            external_mask = tmp_path / "sam2_mask.png"
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(external_asset)
            Image.new("L", (4, 3), 255).save(external_mask)
            (output / "metadata.json").write_text("{bad json", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "import_external_assets.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--role",
                    "main",
                    "--layer-kind",
                    "primary-subject",
                    "--composition-order",
                    "10",
                    "--semantic-boundary",
                    "Main subject mask produced by SAM2.",
                    "--asset",
                    str(external_asset),
                    "--mask",
                    str(external_mask),
                    "--mask-source",
                    "sam2",
                    "--alpha-source",
                    "rembg-refine",
                    "--tool-name",
                    "SAM2",
                    "--tool-role",
                    "segmentation",
                    "--tool-version",
                    "external",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("Traceback", result.stderr)
            self.assertFalse((output / "assets" / "main_object_transparent.png").exists())
            self.assertFalse((output / "masks" / "mask_main_object.png").exists())

    def test_import_external_assets_rejects_object_id_path_segments(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            external_asset = tmp_path / "sam2_main.png"
            external_mask = tmp_path / "sam2_mask.png"
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(external_asset)
            Image.new("L", (4, 3), 255).save(external_mask)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "import_external_assets.py"),
                    str(output),
                    "--object-id",
                    "../outside",
                    "--role",
                    "main",
                    "--layer-kind",
                    "primary-subject",
                    "--composition-order",
                    "10",
                    "--semantic-boundary",
                    "Main subject mask produced by SAM2.",
                    "--asset",
                    str(external_asset),
                    "--mask",
                    str(external_mask),
                    "--mask-source",
                    "sam2",
                    "--alpha-source",
                    "rembg-refine",
                    "--tool-name",
                    "SAM2",
                    "--tool-role",
                    "segmentation",
                    "--tool-version",
                    "external",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("object-id", result.stderr)
            self.assertFalse((output / "outside_transparent.png").exists())

    def test_import_external_assets_rejects_unsafe_object_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            external_asset = tmp_path / "sam2_main.png"
            external_mask = tmp_path / "sam2_mask.png"
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(external_asset)
            Image.new("L", (4, 3), 255).save(external_mask)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "import_external_assets.py"),
                    str(output),
                    "--object-id",
                    "../escape",
                    "--role",
                    "main",
                    "--layer-kind",
                    "primary-subject",
                    "--composition-order",
                    "10",
                    "--semantic-boundary",
                    "Main subject mask produced by SAM2.",
                    "--asset",
                    str(external_asset),
                    "--mask",
                    str(external_mask),
                    "--mask-source",
                    "sam2",
                    "--alpha-source",
                    "rembg-refine",
                    "--tool-name",
                    "SAM2",
                    "--tool-role",
                    "segmentation",
                    "--tool-version",
                    "external",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((tmp_path / "escape_transparent.png").exists())
            self.assertIn("object-id", result.stderr)

    def test_build_quality_previews_fails_when_no_quality_previews_are_generated(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            metadata["objects"] = [
                {
                    "id": "main_object",
                    "asset_path": "assets/missing.png",
                    "mask_path": "masks/missing.png",
                }
            ]
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_quality_previews.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("No quality previews generated", result.stderr)

    def test_build_quality_previews_skips_placeholder_only_rebuild_downstream_objects(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0]["text_semantics"] = {
                "text_role": "plain-text",
                "text_render_class": "editable",
            }
            metadata["objects"][0]["value_scoring"] = {
                "editability_score": "high",
                "visual_complexity_score": "low",
                "asset_value_score": "low",
                "scoring_reason": "Ordinary UI label.",
            }
            metadata["objects"][0]["decision_routing"] = {
                "recommended_action": "rebuild_downstream",
                "final_action": "rebuild_downstream",
                "decision_source": "explicit-user-confirmed",
            }
            metadata["objects"][0]["rebuild_intent"] = {
                "rebuildable_downstream": True,
                "rebuild_notes": "Keep only a placeholder record for downstream rebuild.",
            }
            metadata["objects"][0]["asset_class"] = "grouped-support"
            metadata["objects"][0]["reuse_status"] = "support-only"
            metadata["objects"][0]["delivery_class"] = "support-only"
            metadata["objects"][0]["asset_path"] = ""
            metadata["objects"][0]["mask_path"] = ""
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_quality_previews.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata.get("previews", {}).get("quality", {}), {})

    def test_build_quality_previews_fails_when_any_eligible_object_is_missing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)

            secondary = json.loads(json.dumps(metadata["objects"][0]))
            secondary["id"] = "secondary_01"
            secondary["role"] = "secondary"
            secondary["composition_order"] = 20
            secondary["asset_path"] = "assets/missing_secondary.png"
            secondary["mask_path"] = "masks/missing_secondary.png"
            metadata["objects"].append(secondary)
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_quality_previews.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("secondary_01: missing files for quality preview", result.stderr)
            self.assertIn("Built only 1 of 2 quality preview sets", result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertIn("main_object", metadata["previews"]["quality"])
            self.assertNotIn("secondary_01", metadata["previews"]["quality"])

    def test_build_quality_previews_rejects_paths_outside_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            outside_asset = tmp_path / "outside_asset.png"
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(outside_asset)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0]["asset_path"] = str(outside_asset)
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_quality_previews.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must stay inside the package", result.stderr)

    def test_build_previews_rejects_asset_paths_outside_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            outside_asset = tmp_path / "outside_asset.png"
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(outside_asset)
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0]["asset_path"] = str(outside_asset)
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_previews.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must stay inside the package", result.stderr)

    def test_validate_asset_package_accepts_complete_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["confirmation"]["tooling_preflight"]["status"] = "confirmed"
            metadata["confirmation"]["tooling_preflight"]["source"] = "inferred-from-user"
            metadata["confirmation"]["tooling_preflight"]["evidence_ref"] = "chat:tooling-approved"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            preview_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_previews.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(preview_result.returncode, 0, preview_result.stderr)
            quality_preview_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_quality_previews.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(quality_preview_result.returncode, 0, quality_preview_result.stderr)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_asset_package.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Package valid", result.stdout)

    def test_validate_asset_package_accepts_explicit_decision_without_evidence_ref(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["decision_log"] = [
                {
                    "stage": "final-acceptance",
                    "pause_category": "formal-approval",
                    "question": "Accept this layer?",
                    "recommended_answer": "yes",
                    "recorded_answer": "yes",
                    "decision_effect": "Allow pass.",
                    "decision_source": "explicit-user-confirmed",
                    "evidence_ref": "",
                    "blocking": "true",
                }
            ]
            metadata["confirmation"]["tooling_preflight"].update(
                {
                    "status": "confirmed",
                    "source": "inferred-from-user",
                    "pause_category": "external-blocker",
                    "evidence_ref": "chat:tooling-approved",
                }
            )
            metadata["confirmation"]["granularity_alignment"].update(
                {
                    "status": "confirmed",
                    "source": "explicit-user-confirmed",
                    "pause_category": "user-decision",
                    "evidence_ref": "",
                }
            )
            metadata["confirmation"]["final_acceptance"].update(
                {
                    "status": "confirmed",
                    "source": "explicit-user-confirmed",
                    "pause_category": "formal-approval",
                    "evidence_ref": "",
                }
            )
            metadata["confirmation"]["candidate_promotion"] = {
                "status": "not-required",
                "source": "explicit-user-confirmed",
                "pause_category": "formal-approval",
                "notes": "",
                "evidence_ref": "",
            }
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(preview_result.returncode, 0, preview_result.stderr)
            quality_preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_quality_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(quality_preview_result.returncode, 0, quality_preview_result.stderr)

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_asset_package.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Package valid", result.stdout)

    def test_validate_asset_package_rejects_plain_text_extract_asset_without_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_ready_validation_package(output)
            metadata["objects"][0]["text_semantics"] = {
                "text_role": "plain-text",
                "text_render_class": "editable",
            }
            metadata["objects"][0]["value_scoring"] = {
                "editability_score": "high",
                "visual_complexity_score": "low",
                "asset_value_score": "low",
                "scoring_reason": "Ordinary UI label.",
            }
            metadata["objects"][0]["decision_routing"] = {
                "recommended_action": "rebuild_downstream",
                "final_action": "extract_asset",
                "decision_source": "explicit-user-confirmed",
            }
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_asset_package.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("ordinary editable text-like content", result.stderr)

    def test_validate_asset_package_accepts_plain_text_rebuild_downstream(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_ready_validation_package(output)
            metadata["objects"][0]["text_semantics"] = {
                "text_role": "plain-text",
                "text_render_class": "editable",
            }
            metadata["objects"][0]["value_scoring"] = {
                "editability_score": "high",
                "visual_complexity_score": "low",
                "asset_value_score": "low",
                "scoring_reason": "Ordinary UI label.",
            }
            metadata["objects"][0]["decision_routing"] = {
                "recommended_action": "rebuild_downstream",
                "final_action": "rebuild_downstream",
                "decision_source": "explicit-user-confirmed",
            }
            metadata["objects"][0]["rebuild_intent"] = {
                "rebuildable_downstream": True,
                "rebuild_notes": "Do not export this as a production raster asset.",
            }
            metadata["objects"][0]["asset_class"] = "grouped-support"
            metadata["objects"][0]["reuse_status"] = "support-only"
            metadata["objects"][0]["delivery_class"] = "support-only"
            metadata["objects"][0]["asset_path"] = ""
            metadata["objects"][0]["mask_path"] = ""
            metadata["previews"] = {}
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_asset_package.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Package valid", result.stdout)

    def test_validate_asset_package_accepts_visual_fidelity_critical_wordmark_extract_asset(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_ready_validation_package(output)
            metadata["objects"][0]["text_semantics"] = {
                "text_role": "logo-wordmark",
                "text_render_class": "visual-fidelity-critical",
            }
            metadata["objects"][0]["value_scoring"] = {
                "editability_score": "low",
                "visual_complexity_score": "high",
                "asset_value_score": "high",
                "scoring_reason": "Brand wordmark with custom letterforms.",
            }
            metadata["objects"][0]["decision_routing"] = {
                "recommended_action": "extract_asset",
                "final_action": "extract_asset",
                "decision_source": "explicit-user-confirmed",
            }
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_asset_package.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Package valid", result.stdout)

    def test_validate_asset_package_rejects_requires_user_confirmation_without_decision_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_ready_validation_package(output)
            metadata["decision_log"] = []
            metadata["objects"][0]["text_semantics"] = {
                "text_role": "decorative-text",
                "text_render_class": "styled-editable",
            }
            metadata["objects"][0]["value_scoring"] = {
                "editability_score": "medium",
                "visual_complexity_score": "high",
                "asset_value_score": "medium",
                "scoring_reason": "Stylized heading with ambiguous preservation needs.",
            }
            metadata["objects"][0]["decision_routing"] = {
                "recommended_action": "requires_user_confirmation",
                "final_action": "extract_asset",
                "decision_source": "explicit-user-confirmed",
            }
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_asset_package.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("requires_user_confirmation", result.stderr)

    def test_validate_asset_package_rejects_unrelated_decision_for_ambiguous_text_route(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_ready_validation_package(output)
            metadata["decision_log"] = [
                {
                    "stage": "final-acceptance",
                    "pause_category": "formal-approval",
                    "question": "Accept this extracted layer?",
                    "recommended_answer": "yes",
                    "recorded_answer": "yes",
                    "decision_effect": "Allow final pass after visual QA.",
                    "decision_source": "explicit-user-confirmed",
                    "evidence_ref": "",
                    "blocking": "true",
                    "object_id": "main_object",
                }
            ]
            metadata["objects"][0]["text_semantics"] = {
                "text_role": "decorative-text",
                "text_render_class": "styled-editable",
            }
            metadata["objects"][0]["value_scoring"] = {
                "editability_score": "medium",
                "visual_complexity_score": "high",
                "asset_value_score": "medium",
                "scoring_reason": "Stylized heading with ambiguous preservation needs.",
            }
            metadata["objects"][0]["decision_routing"] = {
                "recommended_action": "requires_user_confirmation",
                "final_action": "extract_asset",
                "decision_source": "explicit-user-confirmed",
            }
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_asset_package.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("requires_user_confirmation", result.stderr)

    def test_validate_asset_package_accepts_confirmed_ambiguous_text_route(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_ready_validation_package(output)
            metadata["decision_log"] = [
                {
                    "stage": "asset-value-scoring",
                    "pause_category": "user-decision",
                    "question": "Should this text-like object be rebuilt downstream or preserved as a visual asset?",
                    "recommended_answer": "rebuild downstream unless fidelity-critical",
                    "recorded_answer": "preserve as visual asset",
                    "decision_effect": "Keep main_object as a visual asset after text-like object review.",
                    "decision_source": "explicit-user-confirmed",
                    "evidence_ref": "",
                    "blocking": "true",
                    "object_id": "main_object",
                }
            ]
            metadata["objects"][0]["text_semantics"] = {
                "text_role": "decorative-text",
                "text_render_class": "styled-editable",
            }
            metadata["objects"][0]["value_scoring"] = {
                "editability_score": "medium",
                "visual_complexity_score": "high",
                "asset_value_score": "medium",
                "scoring_reason": "Stylized heading with ambiguous preservation needs.",
            }
            metadata["objects"][0]["decision_routing"] = {
                "recommended_action": "requires_user_confirmation",
                "final_action": "extract_asset",
                "decision_source": "explicit-user-confirmed",
            }
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_asset_package.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Package valid", result.stdout)

    def test_validate_asset_package_rejects_unscoped_confirmation_for_second_ambiguous_object(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (6, 4), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (6, 4), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("RGBA", (6, 4), (0, 0, 255, 128)).save(
                output / "assets" / "secondary_object_transparent.png"
            )
            Image.new("L", (6, 4), 255).save(output / "masks" / "mask_main.png")
            Image.new("L", (6, 4), 255).save(output / "masks" / "mask_secondary.png")
            metadata = self._write_ready_validation_package(output)
            metadata["objects"][0]["id"] = "status_tile"
            metadata["objects"][0]["layer_kind"] = "control"
            metadata["objects"][0]["semantic_boundary"] = "Carrier tile for the left status control."
            metadata["objects"][0]["asset_path"] = "assets/main_object_transparent.png"
            metadata["objects"][0]["mask_path"] = "masks/mask_main.png"
            metadata["objects"][0]["object_type"] = "ui-carrier"
            metadata["objects"][0]["text_semantics"] = {
                "text_role": "decorative-text",
                "text_render_class": "styled-editable",
            }
            metadata["objects"][0]["value_scoring"] = {
                "editability_score": "medium",
                "visual_complexity_score": "high",
                "asset_value_score": "medium",
                "scoring_reason": "Styled status label with fidelity tradeoffs.",
            }
            metadata["objects"][0]["decision_routing"] = {
                "recommended_action": "requires_user_confirmation",
                "final_action": "extract_asset",
                "decision_source": "explicit-user-confirmed",
            }

            secondary = json.loads(json.dumps(metadata["objects"][0]))
            secondary["id"] = "status_glyph"
            secondary["role"] = "secondary"
            secondary["composition_order"] = 20
            secondary["layer_kind"] = "label"
            secondary["semantic_boundary"] = "Outlined glyph text for the right status control."
            secondary["asset_path"] = "assets/secondary_object_transparent.png"
            secondary["mask_path"] = "masks/mask_secondary.png"
            secondary["object_type"] = "ui-glyph"
            metadata["objects"].append(secondary)
            metadata["decision_log"] = [
                {
                    "stage": "asset-value-scoring",
                    "pause_category": "user-decision",
                    "question": "Should this text-like object be rebuilt downstream or preserved as a visual asset?",
                    "recommended_answer": "rebuild downstream unless fidelity-critical",
                    "recorded_answer": "preserve as visual asset",
                    "decision_effect": "Keep status_tile as a visual asset after review.",
                    "decision_source": "explicit-user-confirmed",
                    "evidence_ref": "",
                    "blocking": "true",
                    "object_id": "status_tile",
                }
            ]
            metadata["previews"]["status_tile"] = metadata["previews"].pop("main_object")
            metadata["previews"]["status_glyph"] = {
                "whitebg": "previews/status_glyph_whitebg.png",
                "checkerboard": "previews/status_glyph_checkerboard.png",
            }
            metadata["previews"]["quality"]["status_tile"] = metadata["previews"]["quality"].pop(
                "main_object"
            )
            metadata["previews"]["quality"]["status_glyph"] = {
                "mask_overlay": "previews/status_glyph_mask_overlay.png",
                "alpha_inspection": "previews/status_glyph_alpha_inspection.png",
            }
            Image.new("RGBA", (6, 4), (200, 200, 200, 255)).save(
                output / "previews" / "status_glyph_whitebg.png"
            )
            Image.new("RGBA", (6, 4), (160, 160, 160, 255)).save(
                output / "previews" / "status_glyph_checkerboard.png"
            )
            Image.new("RGBA", (6, 4), (120, 120, 120, 255)).save(
                output / "previews" / "status_glyph_mask_overlay.png"
            )
            Image.new("RGBA", (6, 4), (220, 220, 255, 255)).save(
                output / "previews" / "status_glyph_alpha_inspection.png"
            )
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_asset_package.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("status_glyph: requires_user_confirmation", result.stderr)

    def test_validate_asset_package_rejects_routing_action_without_decision_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_ready_validation_package(output)
            metadata["objects"][0]["text_semantics"] = {
                "text_role": "logo-wordmark",
                "text_render_class": "visual-fidelity-critical",
            }
            metadata["objects"][0]["value_scoring"] = {
                "editability_score": "low",
                "visual_complexity_score": "high",
                "asset_value_score": "high",
                "scoring_reason": "Brand wordmark with custom letterforms.",
            }
            metadata["objects"][0]["decision_routing"] = {
                "recommended_action": "extract_asset",
                "final_action": "extract_asset",
                "decision_source": "unset",
            }
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_asset_package.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("decision_routing.decision_source", result.stderr)

    def test_validate_asset_package_accepts_ui_atomic_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (8, 8), (20, 30, 40, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            asset_specs = {
                "status_row_02_icon_tile": ((2, 2), (80, 100, 120, 255)),
                "status_row_02_icon_glyph": ((2, 2), (255, 255, 255, 200)),
                "right_metrics_plate": ((8, 8), (30, 40, 50, 255)),
            }
            for object_id, (size, color) in asset_specs.items():
                Image.new("RGBA", size, color).save(output / "assets" / f"{object_id}_transparent.png")
                mask = Image.new("L", (8, 8), 0)
                for x in range(2):
                    for y in range(2):
                        mask.putpixel((x + 3, y + 3), 255)
                if object_id == "right_metrics_plate":
                    mask = Image.new("L", (8, 8), 255)
                mask.save(output / "masks" / f"mask_{object_id}.png")

            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            metadata["analysis"] = {
                "visual_hierarchy": [
                    "background clean plate",
                    "right metrics support plate",
                    "status row icon tile",
                    "status row icon glyph",
                ],
                "recommended_split_plan": (
                    "Keep UI support plates separate from foreground glyphs; text is rebuilt downstream."
                ),
            }
            metadata["granularity"] = {
                "mode": "atomic-layer",
                "user_confirmed": True,
                "notes": "Atomic UI fixture splits carrier tile and foreground glyph.",
                "scope_strategy": "high-signal-subset",
                "text_handling": "rebuild-downstream",
                "carrier_glyph_policy": "split",
                "background_expectation": "approximate-accepted",
                "layer_independence": "animation-ready",
            }
            metadata["extraction_pipeline"] = {
                "recipe": "grounded-segmentation-matting-repair",
                "stages": [
                    "semantic-analysis",
                    "segmentation",
                    "alpha-refinement",
                    "background-repair",
                    "layer-packaging",
                    "qa-review",
                ],
                "quality_gates": ["mask overlay inspected", "alpha inspection inspected"],
                "tools": [
                    {"name": "SAM", "role": "segmentation", "version": "fixture"},
                    {"name": "manual paint", "role": "background reconstruction", "version": "fixture"},
                ],
            }
            metadata["objects"] = [
                {
                    "id": "right_metrics_plate",
                    "role": "group",
                    "layer_kind": "support-plate",
                    "composition_order": 10,
                    "semantic_boundary": "Approximate right metrics support plate reconstructed behind glyphs.",
                    "asset_path": "assets/right_metrics_plate_transparent.png",
                    "mask_path": "masks/mask_right_metrics_plate.png",
                    "mask_source": "inpaint reconstruction",
                    "alpha_source": "reconstructed rgba",
                    "mask_coordinate_space": "source",
                    "width": 8,
                    "height": 8,
                    "aspect_ratio": 1.0,
                    "extraction_method": "manual",
                    "confidence": "high",
                    "edge_complexity": "hard",
                    "object_type": "flat-support-plate",
                    "asset_class": "grouped-support",
                    "reuse_status": "support-only",
                    "delivery_class": "approximate-reconstruction",
                    "current_asset_revision": "support-plate-v1",
                    "selected_candidate_id": "",
                    "repair_history": [],
                    "active_reconstruction_method": "manual support plate redraw",
                    "approximate": True,
                    "reconstruction_provenance": "Manual fixture clean plate reconstructed from surrounding UI.",
                    "manual_review_confirmed": True,
                    "manual_review_flags": ["ai-assisted mask reviewed"],
                    "quality_checks": {
                        "mask_alignment": "pass",
                        "alpha_edges": "pass",
                        "background_residue": "pass",
                        "reuse_readiness": "pass",
                    },
                },
                {
                    "id": "status_row_02_icon_tile",
                    "role": "secondary",
                    "layer_kind": "icon-tile",
                    "composition_order": 20,
                    "semantic_boundary": "Carrier tile behind the row status glyph.",
                    "asset_path": "assets/status_row_02_icon_tile_transparent.png",
                    "mask_path": "masks/mask_status_row_02_icon_tile.png",
                    "mask_source": "sam",
                    "alpha_source": "rgba-alpha",
                    "mask_coordinate_space": "source",
                    "width": 2,
                    "height": 2,
                    "aspect_ratio": 1.0,
                    "extraction_method": "ai-assisted",
                    "confidence": "high",
                    "edge_complexity": "hard",
                    "object_type": "ui-carrier",
                    "asset_class": "atomic",
                    "reuse_status": "production-ready",
                    "delivery_class": "clean-extraction",
                    "current_asset_revision": "tile-v1",
                    "selected_candidate_id": "",
                    "repair_history": [],
                    "active_reconstruction_method": "",
                    "manual_review_flags": ["ai-assisted mask reviewed"],
                    "quality_checks": {
                        "mask_alignment": "pass",
                        "alpha_edges": "pass",
                        "background_residue": "pass",
                        "reuse_readiness": "pass",
                    },
                },
                {
                    "id": "status_row_02_icon_glyph",
                    "role": "secondary",
                    "layer_kind": "glyph",
                    "composition_order": 30,
                    "semantic_boundary": "Foreground glyph separated from its tile carrier.",
                    "asset_path": "assets/status_row_02_icon_glyph_transparent.png",
                    "mask_path": "masks/mask_status_row_02_icon_glyph.png",
                    "mask_source": "sam",
                    "alpha_source": "rgba-alpha",
                    "mask_coordinate_space": "source",
                    "width": 2,
                    "height": 2,
                    "aspect_ratio": 1.0,
                    "extraction_method": "ai-assisted",
                    "confidence": "high",
                    "edge_complexity": "hard",
                    "object_type": "ui-glyph",
                    "asset_class": "atomic",
                    "reuse_status": "production-ready",
                    "delivery_class": "clean-extraction",
                    "current_asset_revision": "glyph-v1",
                    "selected_candidate_id": "",
                    "repair_history": [],
                    "active_reconstruction_method": "",
                    "manual_review_flags": ["ai-assisted mask reviewed"],
                    "quality_checks": {
                        "mask_alignment": "pass",
                        "alpha_edges": "pass",
                        "background_residue": "pass",
                        "reuse_readiness": "pass",
                    },
                },
            ]
            metadata["capability"] = {
                "production_capable": True,
                "missing_for_production": [],
                "user_choice": "production-capable",
                "notes": "UI atomic fixture uses production-capable upstream evidence.",
            }
            metadata["quality_target"] = {
                "tier": "visual-acceptance-ready",
                "notes": "UI atomic fixture is intended to support final visual acceptance.",
            }
            metadata["asset_summary"] = {
                "production_ready_assets": 2,
                "draft_candidate_assets": 0,
                "support_only_layers": 1,
                "blocked_assets": 0,
            }
            metadata["confirmation"]["tooling_preflight"]["status"] = "confirmed"
            metadata["confirmation"]["tooling_preflight"]["source"] = "inferred-from-user"
            metadata["confirmation"]["tooling_preflight"]["evidence_ref"] = "chat:tooling-approved"
            metadata["confirmation"]["granularity_alignment"]["status"] = "confirmed"
            metadata["confirmation"]["granularity_alignment"]["source"] = "explicit-user-confirmed"
            metadata["confirmation"]["pilot_object"]["status"] = "not-required"
            metadata["confirmation"]["pilot_object"]["source"] = "inferred-from-user"
            metadata["confirmation"]["pilot_object"]["evidence_ref"] = "chat:pilot-waived"
            metadata["confirmation"]["approximate_reconstruction"]["status"] = "confirmed"
            metadata["confirmation"]["approximate_reconstruction"]["source"] = "explicit-user-confirmed"
            metadata["confirmation"]["final_acceptance"]["status"] = "confirmed"
            metadata["confirmation"]["final_acceptance"]["source"] = "explicit-user-confirmed"
            metadata["confirmation"]["candidate_promotion"]["status"] = "not-required"
            metadata["confirmation"]["candidate_promotion"]["source"] = "explicit-user-confirmed"
            metadata["decision_log"] = [
                {
                    "stage": "final-acceptance",
                    "pause_category": "formal-approval",
                    "question": "Accept this UI atomic split as production-ready?",
                    "recommended_answer": "yes",
                    "recorded_answer": "yes",
                    "decision_effect": "Allow qa.status=pass for the validated fixture.",
                    "decision_source": "explicit-user-confirmed",
                    "evidence_ref": "chat:ui-final-acceptance",
                    "blocking": "true",
                }
            ]
            metadata["qa"]["status"] = "pass"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(preview_result.returncode, 0, preview_result.stderr)
            quality_preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_quality_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(quality_preview_result.returncode, 0, quality_preview_result.stderr)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_asset_package.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_validate_asset_package_requires_ui_granularity_axes(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (8, 8), (20, 20, 20, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            Image.new("RGBA", (2, 2), (0, 120, 255, 255)).save(
                output / "assets" / "status_tile_transparent.png"
            )
            Image.new("RGBA", (2, 2), (255, 255, 255, 200)).save(
                output / "assets" / "status_glyph_transparent.png"
            )
            Image.new("L", (8, 8), 255).save(output / "masks" / "mask_status_tile.png")
            Image.new("L", (8, 8), 255).save(output / "masks" / "mask_status_glyph.png")
            metadata = self._write_single_object_metadata(output)
            metadata["analysis"] = {
                "visual_hierarchy": ["ui panel", "status tile", "status glyph"],
                "recommended_split_plan": "Split the carrier tile and glyph; rebuild text downstream.",
            }
            metadata["granularity"].update(
                {
                    "scope_strategy": "unset",
                    "text_handling": "unset",
                    "carrier_glyph_policy": "unset",
                    "background_expectation": "unset",
                    "layer_independence": "unset",
                }
            )
            metadata["objects"] = [
                {
                    "id": "status_tile",
                    "role": "secondary",
                    "layer_kind": "icon-tile",
                    "composition_order": 10,
                    "semantic_boundary": "Carrier tile for UI status icon.",
                    "asset_path": "assets/status_tile_transparent.png",
                    "mask_path": "masks/mask_status_tile.png",
                    "mask_source": "sam2",
                    "alpha_source": "manual-rgba",
                    "mask_coordinate_space": "source",
                    "width": 2,
                    "height": 2,
                    "aspect_ratio": 1.0,
                    "area_ratio": 0.0625,
                    "extraction_method": "manual",
                    "confidence": "high",
                    "edge_complexity": "hard",
                    "manual_review_flags": [],
                    "asset_class": "atomic",
                    "reuse_status": "production-ready",
                    "delivery_class": "clean-extraction",
                    "current_asset_revision": "tile-v1",
                    "selected_candidate_id": "",
                    "repair_history": [],
                    "active_reconstruction_method": "",
                    "quality_checks": {
                        "mask_alignment": "pass",
                        "alpha_edges": "pass",
                        "background_residue": "pass",
                        "reuse_readiness": "pass",
                    },
                },
                {
                    "id": "status_glyph",
                    "role": "secondary",
                    "layer_kind": "glyph",
                    "composition_order": 20,
                    "semantic_boundary": "Foreground glyph for UI status icon.",
                    "asset_path": "assets/status_glyph_transparent.png",
                    "mask_path": "masks/mask_status_glyph.png",
                    "mask_source": "sam2",
                    "alpha_source": "manual-rgba",
                    "mask_coordinate_space": "source",
                    "width": 2,
                    "height": 2,
                    "aspect_ratio": 1.0,
                    "area_ratio": 0.0625,
                    "extraction_method": "manual",
                    "confidence": "high",
                    "edge_complexity": "hard",
                    "manual_review_flags": [],
                    "asset_class": "atomic",
                    "reuse_status": "production-ready",
                    "delivery_class": "clean-extraction",
                    "current_asset_revision": "glyph-v1",
                    "selected_candidate_id": "",
                    "repair_history": [],
                    "active_reconstruction_method": "",
                    "quality_checks": {
                        "mask_alignment": "pass",
                        "alpha_edges": "pass",
                        "background_residue": "pass",
                        "reuse_readiness": "pass",
                    },
                },
            ]
            metadata["decision_log"] = [
                {
                    "stage": "granularity-alignment",
                    "question": "Split carrier and glyph with downstream text rebuild?",
                    "recommended_answer": "yes",
                    "user_answer": "yes",
                    "decision_effect": "Allow atomic UI decomposition.",
                }
            ]
            metadata["qa"]["status"] = "pass"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(preview_result.returncode, 0, preview_result.stderr)
            quality_preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_quality_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(quality_preview_result.returncode, 0, quality_preview_result.stderr)

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_asset_package.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("metadata.granularity.scope_strategy", result.stderr)
            self.assertIn("metadata.granularity.text_handling", result.stderr)

    def test_validate_asset_package_requires_glyph_when_carrier_glyph_policy_is_split(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (8, 8), (20, 20, 20, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            Image.new("RGBA", (2, 2), (0, 120, 255, 255)).save(
                output / "assets" / "status_tile_transparent.png"
            )
            Image.new("L", (8, 8), 255).save(output / "masks" / "mask_status_tile.png")
            metadata = self._write_single_object_metadata(output)
            metadata["analysis"] = {
                "visual_hierarchy": ["ui panel", "status tile"],
                "recommended_split_plan": "Carrier and glyph must split when present.",
            }
            metadata["granularity"].update(
                {
                    "scope_strategy": "high-signal-subset",
                    "text_handling": "rebuild-downstream",
                    "carrier_glyph_policy": "split",
                    "background_expectation": "approximate-accepted",
                    "layer_independence": "animation-ready",
                }
            )
            metadata["objects"] = [
                {
                    "id": "status_tile",
                    "role": "secondary",
                    "layer_kind": "icon-tile",
                    "composition_order": 10,
                    "semantic_boundary": "Carrier tile for UI status icon.",
                    "asset_path": "assets/status_tile_transparent.png",
                    "mask_path": "masks/mask_status_tile.png",
                    "mask_source": "sam2",
                    "alpha_source": "manual-rgba",
                    "mask_coordinate_space": "source",
                    "width": 2,
                    "height": 2,
                    "aspect_ratio": 1.0,
                    "area_ratio": 0.0625,
                    "extraction_method": "manual",
                    "confidence": "high",
                    "edge_complexity": "hard",
                    "manual_review_flags": [],
                    "asset_class": "atomic",
                    "reuse_status": "production-ready",
                    "delivery_class": "clean-extraction",
                    "current_asset_revision": "tile-v1",
                    "selected_candidate_id": "",
                    "repair_history": [],
                    "active_reconstruction_method": "",
                    "quality_checks": {
                        "mask_alignment": "pass",
                        "alpha_edges": "pass",
                        "background_residue": "pass",
                        "reuse_readiness": "pass",
                    },
                }
            ]
            metadata["decision_log"] = [
                {
                    "stage": "semantic-split-plan",
                    "question": "Split carrier and glyph?",
                    "recommended_answer": "yes",
                    "user_answer": "yes",
                    "decision_effect": "Require separate layers.",
                }
            ]
            metadata["qa"]["status"] = "pass"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(preview_result.returncode, 0, preview_result.stderr)
            quality_preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_quality_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(quality_preview_result.returncode, 0, quality_preview_result.stderr)

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_asset_package.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("carrier_glyph_policy=split", result.stderr)

    def test_validate_asset_package_requires_inspection_previews(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            self._write_single_object_metadata(output)
            quality_preview_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_quality_previews.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(quality_preview_result.returncode, 0, quality_preview_result.stderr)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_asset_package.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("inspection preview", result.stderr)
            self.assertIn("build_previews.py", result.stderr)

    def test_validate_asset_package_requires_quality_previews(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            self._write_single_object_metadata(output)
            preview_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_previews.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(preview_result.returncode, 0, preview_result.stderr)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_asset_package.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("quality preview", result.stderr)
            self.assertIn("build_quality_previews.py", result.stderr)

    def test_export_asset_manifest_writes_sorted_downstream_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("RGBA", (4, 3), (0, 0, 255, 128)).save(
                output / "assets" / "secondary_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            Image.new("L", (4, 3), 200).save(output / "masks" / "mask_secondary.png")
            metadata = self._write_single_object_metadata(output)
            metadata["objects"].append(
                {
                    "id": "secondary_object",
                    "role": "secondary",
                    "layer_kind": "secondary-object",
                    "composition_order": 5,
                    "semantic_boundary": "Blue secondary fixture object.",
                    "asset_path": "assets/secondary_transparent.png",
                    "mask_path": "masks/mask_secondary.png",
                    "mask_source": "manual",
                    "alpha_source": "manual-rgba",
                    "extraction_method": "manual",
                    "confidence": "high",
                    "edge_complexity": "hard",
                    "asset_class": "atomic",
                    "reuse_status": "production-ready",
                    "manual_review_flags": [],
                    "quality_checks": {
                        "mask_alignment": "pass",
                        "alpha_edges": "pass",
                        "background_residue": "pass",
                        "reuse_readiness": "pass",
                    },
                }
            )
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "export_asset_manifest.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            manifest_path = output / "asset_manifest.json"
            self.assertTrue(manifest_path.exists())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["schema_version"], "1.0")
            self.assertEqual(manifest["package_name"], "fixture")
            self.assertEqual(manifest["qa_status"], "needs-review")
            self.assertEqual(
                [layer["id"] for layer in manifest["layers"]],
                ["secondary_object", "main_object"],
            )
            self.assertEqual(manifest["layers"][0]["asset_path"], "assets/secondary_transparent.png")
            self.assertEqual(manifest["layers"][0]["mask_path"], "masks/mask_secondary.png")
            self.assertEqual(manifest["layers"][0]["quality_status"], "pass")
            self.assertEqual(manifest["layers"][0]["asset_class"], "atomic")
            self.assertEqual(manifest["layers"][0]["reuse_status"], "production-ready")
            self.assertEqual(manifest["asset_summary"]["production_ready_assets"], 2)
            self.assertEqual(manifest["asset_summary"]["draft_candidate_assets"], 0)
            self.assertEqual(manifest["asset_summary"]["support_only_layers"], 0)

    def test_export_asset_manifest_skips_placeholder_only_rebuild_downstream_objects(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0]["text_semantics"] = {
                "text_role": "plain-text",
                "text_render_class": "editable",
            }
            metadata["objects"][0]["value_scoring"] = {
                "editability_score": "high",
                "visual_complexity_score": "low",
                "asset_value_score": "low",
                "scoring_reason": "Ordinary UI label.",
            }
            metadata["objects"][0]["decision_routing"] = {
                "recommended_action": "rebuild_downstream",
                "final_action": "rebuild_downstream",
                "decision_source": "explicit-user-confirmed",
            }
            metadata["objects"][0]["rebuild_intent"] = {
                "rebuildable_downstream": True,
                "rebuild_notes": "Keep only a placeholder record for downstream rebuild.",
            }
            metadata["objects"][0]["asset_class"] = "grouped-support"
            metadata["objects"][0]["reuse_status"] = "support-only"
            metadata["objects"][0]["delivery_class"] = "support-only"
            metadata["objects"][0]["asset_path"] = ""
            metadata["objects"][0]["mask_path"] = ""
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "export_asset_manifest.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((output / "asset_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["layers"], [])

    def test_export_asset_manifest_rejects_unknown_object_role(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0]["role"] = "mystery"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "export_asset_manifest.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("role must be one of", result.stderr)
            self.assertFalse((output / "asset_manifest.json").exists())

    def test_audit_visual_quality_writes_warning_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (6, 6), (20, 20, 20, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 4), (255, 0, 0, 255)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (6, 6), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0]["asset_class"] = "candidate"
            metadata["objects"][0]["reuse_status"] = "draft-candidate"
            metadata["qa"]["status"] = "needs-review"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "audit_visual_quality.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            audit_path = output / "_staging" / "quality" / "quality_audit.json"
            contact_sheet_path = output / "_staging" / "quality" / "qa_audit_contact_sheet.png"
            self.assertTrue(audit_path.exists())
            self.assertTrue(contact_sheet_path.exists())
            audit = json.loads(audit_path.read_text(encoding="utf-8"))
            self.assertEqual(audit["status"], "warning")
            warning_codes = {warning["code"] for warning in audit["warnings"]}
            self.assertIn("hard-alpha-risk", warning_codes)
            self.assertIn("detached-fragments", warning_codes)
            self.assertIn("smear-artifact", warning_codes)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(
                metadata["audit"]["quality_audit_path"],
                "_staging/quality/quality_audit.json",
            )

    def test_audit_visual_quality_emits_edge_halo_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (6, 6), (20, 20, 20, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            halo_asset = Image.new("RGBA", (4, 4), (0, 0, 0, 0))
            for x in range(4):
                for y in range(4):
                    halo_asset.putpixel((x, y), (10, 10, 10, 120 if x in {0, 3} or y in {0, 3} else 255))
            halo_asset.save(output / "assets" / "main_object_transparent.png")
            Image.new("L", (6, 6), 200).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0]["asset_class"] = "candidate"
            metadata["objects"][0]["reuse_status"] = "draft-candidate"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "audit_visual_quality.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            audit = json.loads(
                (output / "_staging" / "quality" / "quality_audit.json").read_text(encoding="utf-8")
            )
            warning_codes = {warning["code"] for warning in audit["warnings"]}
            self.assertIn("edge-halo", warning_codes)

    def test_promote_candidate_asset_updates_revision_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (6, 6), (20, 20, 20, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 4), (255, 0, 0, 255)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (6, 6), 255).save(output / "masks" / "mask_main.png")
            self._write_single_object_metadata(output)
            candidate_dir = output / "_staging" / "repair_candidates"
            candidate_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (4, 4), (0, 255, 0, 255)).save(candidate_dir / "candidate_v2.png")
            Image.new("L", (6, 6), 255).save(candidate_dir / "candidate_v2_mask.png")
            compare_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "compare_candidate_assets.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate",
                    "candidate-v2=_staging/repair_candidates/candidate_v2.png",
                    "--compare-note",
                    "Only one viable candidate after manual cleanup.",
                    "--compare-criterion",
                    "single viable candidate rationale",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(compare_result.returncode, 0, compare_result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            comparison_id = metadata["objects"][0]["candidate_comparisons"][0]["comparison_id"]

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "promote_candidate_asset.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate-asset",
                    "_staging/repair_candidates/candidate_v2.png",
                    "--candidate-mask",
                    "_staging/repair_candidates/candidate_v2_mask.png",
                    "--candidate-id",
                    "candidate-v2",
                    "--comparison-id",
                    comparison_id,
                    "--delivery-class",
                    "approximate-reconstruction",
                    "--active-reconstruction-method",
                    "manual carrier redraw",
                    "--repair-note",
                    "Promote the cleaner carrier candidate after comparison.",
                    "--selection-reason",
                    "Cleaner interior edge and better carrier silhouette.",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            obj = metadata["objects"][0]
            self.assertEqual(obj["selected_candidate_id"], "candidate-v2")
            self.assertEqual(obj["current_asset_revision"], "candidate-v2")
            self.assertEqual(obj["delivery_class"], "approximate-reconstruction")
            self.assertEqual(obj["active_reconstruction_method"], "manual carrier redraw")
            self.assertTrue(obj["approximate"])
            self.assertEqual(obj["reuse_status"], "approximate-reconstruction")
            self.assertEqual(obj["repair_history"][0]["candidate_id"], "candidate-v2")
            self.assertEqual(metadata["asset_summary"]["production_ready_assets"], 0)
            self.assertEqual(metadata["asset_summary"]["support_only_layers"], 1)
            self.assertEqual(obj["candidate_comparisons"][0]["selected_candidate_id"], "candidate-v2")
            self.assertEqual(
                obj["candidate_comparisons"][0]["selection_reason"],
                "Cleaner interior edge and better carrier silhouette.",
            )
            qa_report = (output / "qa_report.md").read_text(encoding="utf-8")
            self.assertIn("Selection reason: Cleaner interior edge and better carrier silhouette.", qa_report)

    def test_promote_candidate_asset_rejects_target_asset_path_outside_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (6, 6), (20, 20, 20, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 4), (255, 0, 0, 255)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (6, 6), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            outside_asset = tmp_path / "outside_target.png"
            metadata["objects"][0]["asset_path"] = str(outside_asset)
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            candidate_dir = output / "_staging" / "repair_candidates"
            candidate_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (4, 4), (0, 255, 0, 255)).save(candidate_dir / "candidate_v2.png")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "promote_candidate_asset.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate-asset",
                    "_staging/repair_candidates/candidate_v2.png",
                    "--candidate-id",
                    "candidate-v2",
                    "--delivery-class",
                    "clean-extraction",
                    "--repair-note",
                    "Reject unsafe target path.",
                    "--selection-reason",
                    "Invalid target path should be blocked.",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("target asset_path must stay inside the package", result.stderr)

    def test_promote_candidate_asset_rejects_candidate_mask_outside_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (6, 6), (20, 20, 20, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 4), (255, 0, 0, 255)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (6, 6), 255).save(output / "masks" / "mask_main.png")
            self._write_single_object_metadata(output)
            candidate_dir = output / "_staging" / "repair_candidates"
            candidate_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (4, 4), (0, 255, 0, 255)).save(candidate_dir / "candidate_v2.png")
            outside_mask = tmp_path / "outside_mask.png"
            Image.new("L", (6, 6), 255).save(outside_mask)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "promote_candidate_asset.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate-asset",
                    "_staging/repair_candidates/candidate_v2.png",
                    "--candidate-mask",
                    str(outside_mask),
                    "--candidate-id",
                    "candidate-v2",
                    "--delivery-class",
                    "clean-extraction",
                    "--repair-note",
                    "Reject unsafe candidate mask path.",
                    "--selection-reason",
                    "Invalid mask path should be blocked.",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("candidate mask must stay inside the package", result.stderr)

    def test_promote_candidate_asset_requires_repair_candidate_staging_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (6, 6), (20, 20, 20, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 4), (255, 0, 0, 255)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (6, 6), 255).save(output / "masks" / "mask_main.png")
            self._write_single_object_metadata(output)
            non_candidate_dir = output / "_staging" / "misc"
            non_candidate_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (4, 4), (0, 255, 0, 255)).save(non_candidate_dir / "candidate_v2.png")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "promote_candidate_asset.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate-asset",
                    "_staging/misc/candidate_v2.png",
                    "--candidate-id",
                    "candidate-v2",
                    "--delivery-class",
                    "clean-extraction",
                    "--repair-note",
                    "Reject non-standard candidate staging path.",
                    "--selection-reason",
                    "Candidate must come from the repair candidate staging path.",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("_staging/repair_candidates/", result.stderr)

    def test_promote_candidate_asset_requires_selection_reason(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (6, 6), (20, 20, 20, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 4), (255, 0, 0, 255)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (6, 6), 255).save(output / "masks" / "mask_main.png")
            self._write_single_object_metadata(output)
            candidate_dir = output / "_staging" / "repair_candidates"
            candidate_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (4, 4), (0, 255, 0, 255)).save(candidate_dir / "candidate_v2.png")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "promote_candidate_asset.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate-asset",
                    "_staging/repair_candidates/candidate_v2.png",
                    "--candidate-id",
                    "candidate-v2",
                    "--delivery-class",
                    "clean-extraction",
                    "--repair-note",
                    "Try to promote without rationale.",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)

    def test_promote_candidate_asset_direct_promotion_writes_compare_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (6, 6), (20, 20, 20, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 4), (255, 0, 0, 255)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (6, 6), 255).save(output / "masks" / "mask_main.png")
            self._write_single_object_metadata(output)
            candidate_dir = output / "_staging" / "repair_candidates"
            candidate_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (4, 4), (0, 255, 0, 255)).save(candidate_dir / "candidate_v2.png")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "promote_candidate_asset.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate-asset",
                    "_staging/repair_candidates/candidate_v2.png",
                    "--candidate-id",
                    "candidate-v2",
                    "--delivery-class",
                    "clean-extraction",
                    "--repair-note",
                    "Directly promote the single available candidate.",
                    "--selection-reason",
                    "Only one candidate survived review and it matches the current scope.",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            metadata["confirmation"]["tooling_preflight"]["status"] = "confirmed"
            metadata["confirmation"]["tooling_preflight"]["source"] = "explicit-user-confirmed"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            comparison = metadata["objects"][0]["candidate_comparisons"][0]
            self.assertTrue(comparison["compare_manifest_path"].endswith("_compare.json"))
            compare_manifest = json.loads(
                (output / comparison["compare_manifest_path"]).read_text(encoding="utf-8")
            )
            self.assertEqual(compare_manifest["candidate_ids"], ["candidate-v2"])
            self.assertEqual(
                compare_manifest["compare_criteria"],
                ["single-candidate direct promotion"],
            )

            preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(preview_result.returncode, 0, preview_result.stderr)
            quality_preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_quality_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(quality_preview_result.returncode, 0, quality_preview_result.stderr)

            validate_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_asset_package.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(validate_result.returncode, 0, validate_result.stderr)

    def test_validate_asset_package_requires_candidate_compare_explainability(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0]["selected_candidate_id"] = "candidate-v2"
            metadata["objects"][0]["repair_history"] = [{"candidate_id": "candidate-v2"}]
            metadata["objects"][0]["candidate_comparisons"] = [
                {
                    "comparison_id": "cmp-1",
                    "object_id": "main_object",
                    "candidate_ids": ["candidate-v2", "candidate-v3"],
                    "compare_artifact_path": "",
                    "selected_candidate_id": "candidate-v2",
                    "selection_reason": "",
                    "created_at": "2026-06-26T00:00:00Z",
                }
            ]
            metadata["decision_log"] = [
                {
                    "stage": "final-acceptance",
                    "question": "Accept this promoted candidate?",
                    "recommended_answer": "yes",
                    "user_answer": "yes",
                    "decision_effect": "Allow pass after validation.",
                }
            ]
            metadata["qa"]["status"] = "pass"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(preview_result.returncode, 0, preview_result.stderr)
            quality_preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_quality_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(quality_preview_result.returncode, 0, quality_preview_result.stderr)

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_asset_package.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("compare_manifest_path", result.stderr)
            self.assertIn("selected_candidate_id requires a matching candidate comparison record", result.stderr)

    def test_validate_asset_package_rejects_promotion_without_compare_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0]["selected_candidate_id"] = "candidate-v2"
            metadata["objects"][0]["repair_history"] = [{"candidate_id": "candidate-v2"}]
            metadata["objects"][0]["candidate_comparisons"] = [
                {
                    "comparison_id": "cmp-1",
                    "object_id": "main_object",
                    "candidate_ids": ["candidate-v2", "candidate-v3"],
                    "compare_artifact_path": "_staging/repair_candidates/cmp-1_compare.png",
                    "selected_candidate_id": "candidate-v2",
                    "selection_reason": "Best edge cleanup.",
                    "created_at": "2026-06-27T00:00:00Z",
                }
            ]
            metadata["decision_log"] = [
                {
                    "stage": "final-acceptance",
                    "question": "Accept this promoted candidate?",
                    "recommended_answer": "yes",
                    "user_answer": "yes",
                    "decision_effect": "Allow pass after validation.",
                }
            ]
            metadata["qa"]["status"] = "pass"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(preview_result.returncode, 0, preview_result.stderr)
            quality_preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_quality_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(quality_preview_result.returncode, 0, quality_preview_result.stderr)

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_asset_package.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("compare_manifest_path", result.stderr)

    def test_validate_asset_package_rejects_promoted_approximate_reconstruction_without_acceptance(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0]["delivery_class"] = "approximate-reconstruction"
            metadata["objects"][0]["reuse_status"] = "approximate-reconstruction"
            metadata["objects"][0]["approximate"] = True
            metadata["objects"][0]["reconstruction_provenance"] = "manual redraw path"
            metadata["objects"][0]["active_reconstruction_method"] = "manual redraw path"
            metadata["objects"][0]["manual_review_confirmed"] = True
            metadata["objects"][0]["selected_candidate_id"] = "candidate-v2"
            metadata["objects"][0]["repair_history"] = [{"candidate_id": "candidate-v2"}]
            metadata["objects"][0]["candidate_comparisons"] = [
                {
                    "comparison_id": "cmp-1",
                    "object_id": "main_object",
                    "candidate_ids": ["candidate-v2"],
                    "compare_artifact_path": "",
                    "compare_manifest_path": "",
                    "selected_candidate_id": "candidate-v2",
                    "selection_reason": "Only viable candidate.",
                    "created_at": "2026-06-27T00:00:00Z",
                }
            ]
            metadata["decision_log"] = [
                {
                    "stage": "final-acceptance",
                    "question": "Accept this promoted candidate?",
                    "recommended_answer": "yes",
                    "user_answer": "yes",
                    "decision_effect": "Allow pass after validation.",
                }
            ]
            metadata["qa"]["status"] = "needs-review"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(preview_result.returncode, 0, preview_result.stderr)
            quality_preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_quality_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(quality_preview_result.returncode, 0, quality_preview_result.stderr)

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_asset_package.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("reconstruction acceptance decision", result.stderr)

    def test_validate_asset_package_accepts_archived_compare_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (6, 6), (20, 20, 20, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 4), (255, 0, 0, 255)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (6, 6), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0]["asset_class"] = "grouped-support"
            metadata["objects"][0]["reuse_status"] = "approximate-reconstruction"
            metadata["objects"][0]["delivery_class"] = "approximate-reconstruction"
            metadata["objects"][0]["approximate"] = True
            metadata["objects"][0]["reconstruction_provenance"] = "archived compare flow"
            metadata["objects"][0]["active_reconstruction_method"] = "manual redraw archived compare flow"
            metadata["objects"][0]["manual_review_confirmed"] = True
            metadata["granularity"].update(
                {
                    "scope_strategy": "high-signal-subset",
                    "text_handling": "rebuild-downstream",
                    "carrier_glyph_policy": "split",
                    "background_expectation": "approximate-accepted",
                    "layer_independence": "animation-ready",
                }
            )
            metadata["decision_log"] = [
                {
                    "stage": "approximate-reconstruction-acceptance",
                    "pause_category": "user-decision",
                    "question": "Accept approximate reconstructed candidate after compare?",
                    "recommended_answer": "yes",
                    "recorded_answer": "yes",
                    "decision_effect": "Allow archived compare evidence to support validation.",
                    "decision_source": "explicit-user-confirmed",
                    "evidence_ref": "chat:archived-reconstruction-accepted",
                    "blocking": "true",
                }
            ]
            metadata["confirmation"]["tooling_preflight"]["status"] = "confirmed"
            metadata["confirmation"]["tooling_preflight"]["source"] = "inferred-from-user"
            metadata["confirmation"]["tooling_preflight"]["evidence_ref"] = "chat:tooling-approved"
            metadata["confirmation"]["approximate_reconstruction"]["status"] = "confirmed"
            metadata["confirmation"]["approximate_reconstruction"]["source"] = "explicit-user-confirmed"
            metadata["confirmation"]["final_promotion_acceptance"]["status"] = "confirmed"
            metadata["confirmation"]["final_promotion_acceptance"]["source"] = "explicit-user-confirmed"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            candidate_dir = output / "_staging" / "repair_candidates"
            candidate_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (4, 4), (0, 255, 0, 255)).save(candidate_dir / "candidate_a.png")
            Image.new("RGBA", (4, 4), (0, 0, 255, 255)).save(candidate_dir / "candidate_b.png")
            Image.new("L", (6, 6), 255).save(candidate_dir / "candidate_a_mask.png")
            Image.new("L", (6, 6), 255).save(candidate_dir / "candidate_b_mask.png")

            compare_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "compare_candidate_assets.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate",
                    "candidate-a=_staging/repair_candidates/candidate_a.png",
                    "--candidate",
                    "candidate-b=_staging/repair_candidates/candidate_b.png",
                    "--compare-note",
                    "Archive compare evidence and keep validation green.",
                    "--compare-criterion",
                    "shape fidelity",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(compare_result.returncode, 0, compare_result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            comparison_id = metadata["objects"][0]["candidate_comparisons"][0]["comparison_id"]

            promote_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "promote_candidate_asset.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate-asset",
                    "_staging/repair_candidates/candidate_a.png",
                    "--candidate-mask",
                    "_staging/repair_candidates/candidate_a_mask.png",
                    "--candidate-id",
                    "candidate-a",
                    "--comparison-id",
                    comparison_id,
                    "--delivery-class",
                    "approximate-reconstruction",
                    "--active-reconstruction-method",
                    "manual redraw archived compare flow",
                    "--repair-note",
                    "Promote candidate before archiving compare evidence.",
                    "--selection-reason",
                    "Candidate A preserved the carrier best.",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(promote_result.returncode, 0, promote_result.stderr)
            archive_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "archive_intermediates.py"),
                    str(output),
                    "--run-id",
                    "archived-compare-001",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(archive_result.returncode, 0, archive_result.stderr)
            review_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_quality_review.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--mask-alignment",
                    "pass",
                    "--alpha-edges",
                    "pass",
                    "--background-residue",
                    "pass",
                    "--reuse-readiness",
                    "pass",
                    "--decision-stage",
                    "final-promotion-acceptance",
                    "--decision-question",
                    "Promote candidate-a before archiving compare evidence?",
                    "--decision-recommended",
                    "yes",
                    "--decision-answer",
                    "yes",
                    "--decision-effect",
                    "Candidate A becomes the archived approved revision.",
                    "--decision-source",
                    "explicit-user-confirmed",
                    "--pause-category",
                    "formal-approval",
                    "--blocking",
                    "true",
                    "--evidence-ref",
                    "chat:archived-candidate-approved",
                    "--review-note",
                    "Archived compare evidence reviewed.",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(review_result.returncode, 0, review_result.stderr)
            preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(preview_result.returncode, 0, preview_result.stderr)
            quality_preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_quality_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(quality_preview_result.returncode, 0, quality_preview_result.stderr)
            validate_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_asset_package.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(validate_result.returncode, 0, validate_result.stderr)

    def test_validate_asset_package_rejects_pass_without_visual_acceptance_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (6, 6), (20, 20, 20, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 4), (255, 0, 0, 255)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (6, 6), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["quality_target"]["tier"] = "usable-draft"
            metadata["qa"]["status"] = "pass"
            metadata["decision_log"] = [
                {
                    "stage": "final-promotion-acceptance",
                    "question": "Accept current layer?",
                    "recommended_answer": "yes",
                    "user_answer": "yes",
                    "decision_effect": "Allow pass.",
                }
            ]
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(preview_result.returncode, 0, preview_result.stderr)
            quality_preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_quality_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(quality_preview_result.returncode, 0, quality_preview_result.stderr)

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_asset_package.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("quality_target.tier=visual-acceptance-ready", result.stderr)

    def test_validate_asset_package_requires_object_type_for_ui_like_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (6, 6), (20, 20, 20, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 4), (255, 0, 0, 255)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (6, 6), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["analysis"]["visual_hierarchy"] = ["ui panel", "status tile", "status glyph"]
            metadata["objects"][0]["layer_kind"] = "glyph"
            metadata["objects"][0]["semantic_boundary"] = "UI glyph in status tile."
            metadata["objects"][0]["object_type"] = "generic-object"
            metadata["decision_log"] = [
                {
                    "stage": "granularity-alignment",
                    "question": "Split UI tile and glyph?",
                    "recommended_answer": "yes",
                    "user_answer": "yes",
                    "decision_effect": "Use atomic UI split.",
                }
            ]
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(preview_result.returncode, 0, preview_result.stderr)
            quality_preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_quality_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(quality_preview_result.returncode, 0, quality_preview_result.stderr)

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_asset_package.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("object_type must be recorded", result.stderr)

    def test_validate_asset_package_requires_confirmation_gates_for_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["qa"]["status"] = "pass"
            metadata["decision_log"] = [
                {
                    "stage": "final-acceptance",
                    "question": "Accept this layer?",
                    "recommended_answer": "yes",
                    "user_answer": "yes",
                    "decision_effect": "Allow pass.",
                    "decision_source": "explicit-user-confirmed",
                }
            ]
            metadata["confirmation"]["tooling_preflight"]["status"] = "confirmed"
            metadata["confirmation"]["tooling_preflight"]["source"] = "explicit-user-confirmed"
            metadata["confirmation"]["final_acceptance"]["status"] = "confirmed"
            metadata["confirmation"]["final_acceptance"]["source"] = "explicit-user-confirmed"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(preview_result.returncode, 0, preview_result.stderr)
            quality_preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_quality_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(quality_preview_result.returncode, 0, quality_preview_result.stderr)

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_asset_package.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("granularity_alignment", result.stderr)

    def test_validate_asset_package_requires_pilot_gate_for_ui_packages(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (8, 8), (20, 20, 20, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (2, 2), (255, 255, 255, 200)).save(
                output / "assets" / "status_glyph_transparent.png"
            )
            Image.new("L", (8, 8), 255).save(output / "masks" / "mask_status_glyph.png")
            metadata = self._write_single_object_metadata(output)
            metadata["analysis"] = {
                "visual_hierarchy": ["ui panel", "status tile", "status glyph"],
                "recommended_split_plan": "Split tile and glyph after pilot approval.",
            }
            metadata["objects"] = [
                {
                    "id": "status_glyph",
                    "role": "secondary",
                    "layer_kind": "glyph",
                    "composition_order": 10,
                    "semantic_boundary": "UI status glyph.",
                    "asset_path": "assets/status_glyph_transparent.png",
                    "mask_path": "masks/mask_status_glyph.png",
                    "mask_source": "sam",
                    "alpha_source": "rgba-alpha",
                    "width": 2,
                    "height": 2,
                    "aspect_ratio": 1.0,
                    "area_ratio": 0.1,
                    "extraction_method": "ai-assisted",
                    "confidence": "high",
                    "edge_complexity": "hard",
                    "object_type": "ui-glyph",
                    "asset_class": "atomic",
                    "reuse_status": "production-ready",
                    "delivery_class": "clean-extraction",
                    "current_asset_revision": "glyph-v1",
                    "selected_candidate_id": "",
                    "repair_history": [],
                    "active_reconstruction_method": "",
                    "manual_review_flags": [],
                    "quality_checks": {
                        "mask_alignment": "pass",
                        "alpha_edges": "pass",
                        "background_residue": "pass",
                        "reuse_readiness": "pass",
                    },
                }
            ]
            metadata["granularity"].update(
                {
                    "scope_strategy": "high-signal-subset",
                    "text_handling": "rebuild-downstream",
                    "carrier_glyph_policy": "split",
                    "background_expectation": "approximate-accepted",
                    "layer_independence": "animation-ready",
                }
            )
            metadata["decision_log"] = [
                {
                    "stage": "granularity-alignment",
                    "question": "Use atomic-layer granularity?",
                    "recommended_answer": "yes",
                    "user_answer": "yes",
                    "decision_effect": "Proceed.",
                    "decision_source": "explicit-user-confirmed",
                }
            ]
            metadata["confirmation"]["tooling_preflight"]["status"] = "confirmed"
            metadata["confirmation"]["tooling_preflight"]["source"] = "explicit-user-confirmed"
            metadata["confirmation"]["granularity_alignment"]["status"] = "confirmed"
            metadata["confirmation"]["granularity_alignment"]["source"] = "explicit-user-confirmed"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(preview_result.returncode, 0, preview_result.stderr)
            quality_preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_quality_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(quality_preview_result.returncode, 0, quality_preview_result.stderr)

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_asset_package.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("pilot_object", result.stderr)

    def test_validate_asset_package_rejects_agent_defaulted_final_acceptance_for_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["qa"]["status"] = "pass"
            metadata["decision_log"] = [
                {
                    "stage": "final-acceptance",
                    "question": "Accept this layer?",
                    "recommended_answer": "yes",
                    "user_answer": "yes",
                    "decision_effect": "Allow pass.",
                    "decision_source": "agent-defaulted",
                }
            ]
            metadata["confirmation"]["tooling_preflight"]["status"] = "confirmed"
            metadata["confirmation"]["tooling_preflight"]["source"] = "inferred-from-user"
            metadata["confirmation"]["granularity_alignment"]["status"] = "confirmed"
            metadata["confirmation"]["granularity_alignment"]["source"] = "inferred-from-user"
            metadata["confirmation"]["final_acceptance"]["status"] = "confirmed"
            metadata["confirmation"]["final_acceptance"]["source"] = "agent-defaulted"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(preview_result.returncode, 0, preview_result.stderr)
            quality_preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_quality_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(quality_preview_result.returncode, 0, quality_preview_result.stderr)

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_asset_package.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("final_acceptance must come from explicit-user-confirmed or inferred-from-user", result.stderr)

    def test_validate_asset_package_requires_evidence_for_inferred_confirmation(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["qa"]["status"] = "pass"
            metadata["decision_log"] = [
                {
                    "stage": "final-acceptance",
                    "pause_category": "formal-approval",
                    "question": "Accept this layer?",
                    "recommended_answer": "yes",
                    "recorded_answer": "yes",
                    "decision_effect": "Allow pass.",
                    "decision_source": "inferred-from-user",
                    "evidence_ref": "",
                    "blocking": "true",
                }
            ]
            metadata["confirmation"]["tooling_preflight"].update(
                {
                    "status": "confirmed",
                    "source": "inferred-from-user",
                    "pause_category": "external-blocker",
                    "evidence_ref": "",
                }
            )
            metadata["confirmation"]["granularity_alignment"].update(
                {
                    "status": "confirmed",
                    "source": "explicit-user-confirmed",
                    "pause_category": "user-decision",
                    "evidence_ref": "",
                }
            )
            metadata["confirmation"]["final_acceptance"].update(
                {
                    "status": "confirmed",
                    "source": "inferred-from-user",
                    "pause_category": "formal-approval",
                    "evidence_ref": "",
                }
            )
            metadata["confirmation"]["candidate_promotion"] = {
                "status": "not-required",
                "source": "explicit-user-confirmed",
                "pause_category": "formal-approval",
                "notes": "",
                "evidence_ref": "chat:not-promoting",
            }
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(preview_result.returncode, 0, preview_result.stderr)
            quality_preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_quality_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(quality_preview_result.returncode, 0, quality_preview_result.stderr)

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_asset_package.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("evidence_ref", result.stderr)

    def test_validate_asset_package_rejects_pending_confirmation_with_non_unset_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["confirmation"]["tooling_preflight"]["source"] = "explicit-user-confirmed"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_asset_package.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("status=pending", result.stderr)

    def test_validate_asset_package_requires_candidate_promotion_for_promoted_revision(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["qa"]["status"] = "pass"
            metadata["objects"][0]["selected_candidate_id"] = "candidate-v2"
            metadata["objects"][0]["repair_history"] = ["candidate-v2 promoted after compare"]
            metadata["decision_log"] = [
                {
                    "stage": "final-acceptance",
                    "pause_category": "formal-approval",
                    "question": "Accept this layer?",
                    "recommended_answer": "yes",
                    "recorded_answer": "yes",
                    "decision_effect": "Allow pass.",
                    "decision_source": "explicit-user-confirmed",
                    "evidence_ref": "chat:accepted-final",
                    "blocking": "true",
                }
            ]
            metadata["confirmation"]["tooling_preflight"].update(
                {
                    "status": "confirmed",
                    "source": "explicit-user-confirmed",
                    "pause_category": "external-blocker",
                    "evidence_ref": "chat:tooling-clear",
                }
            )
            metadata["confirmation"]["granularity_alignment"].update(
                {
                    "status": "confirmed",
                    "source": "explicit-user-confirmed",
                    "pause_category": "user-decision",
                    "evidence_ref": "chat:granularity",
                }
            )
            metadata["confirmation"]["final_acceptance"].update(
                {
                    "status": "confirmed",
                    "source": "explicit-user-confirmed",
                    "pause_category": "formal-approval",
                    "evidence_ref": "chat:accepted-final",
                }
            )
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(preview_result.returncode, 0, preview_result.stderr)
            quality_preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_quality_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(quality_preview_result.returncode, 0, quality_preview_result.stderr)

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_asset_package.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("candidate_promotion", result.stderr)

    def test_generate_ui_carrier_candidates_emits_manifest_and_updates_object_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (8, 8), (40, 50, 60, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            source_crop = output / "_staging" / "tile_source.png"
            carrier_mask = output / "masks" / "mask_main.png"
            glyph_mask = output / "_staging" / "glyph_mask.png"
            Image.new("RGBA", (8, 8), (120, 140, 180, 255)).save(source_crop)
            Image.new("L", (8, 8), 255).save(carrier_mask)
            Image.new("L", (8, 8), 0).save(glyph_mask)
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0]["mask_path"] = "masks/mask_main.png"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "generate_ui_carrier_candidates.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--source-crop",
                    "_staging/tile_source.png",
                    "--carrier-mask",
                    "masks/mask_main.png",
                    "--glyph-mask",
                    "_staging/glyph_mask.png",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest_path = output / "_staging" / "repair_candidates" / "main_object" / "main_object_ui_carrier_candidates.json"
            self.assertTrue(manifest_path.exists())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            strategies = {item["strategy"] for item in manifest["candidates"]}
            self.assertIn("center-rebuild-with-border-pasteback", strategies)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["objects"][0]["object_type"], "ui-carrier")

    def test_generate_ui_glyph_cleanup_candidates_emits_padded_variant(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (8, 8), (20, 20, 20, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            glyph_asset = output / "assets" / "main_object_transparent.png"
            Image.new("RGBA", (4, 4), (255, 255, 255, 220)).save(glyph_asset)
            self._write_single_object_metadata(output)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "generate_ui_glyph_cleanup_candidates.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--glyph-asset",
                    "assets/main_object_transparent.png",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest_path = output / "_staging" / "repair_candidates" / "main_object" / "main_object_ui_glyph_candidates.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            strategies = {item["strategy"] for item in manifest["candidates"]}
            self.assertIn("padded-delivery-variant", strategies)

    def test_generate_ui_glyph_cleanup_candidates_tile_subtract_differs_from_plain_recolor(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (8, 8), (20, 20, 20, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            glyph_asset = output / "assets" / "main_object_transparent.png"
            carrier_asset = output / "assets" / "carrier_reference.png"
            glyph = Image.new("RGBA", (4, 4), (255, 255, 255, 0))
            glyph.putpixel((1, 1), (240, 240, 240, 255))
            glyph.putpixel((2, 1), (220, 220, 220, 255))
            glyph.putpixel((1, 2), (200, 200, 200, 255))
            glyph.putpixel((2, 2), (180, 180, 180, 255))
            glyph.save(glyph_asset)
            Image.new("RGBA", (4, 4), (80, 120, 200, 255)).save(carrier_asset)
            self._write_single_object_metadata(output)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "generate_ui_glyph_cleanup_candidates.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--glyph-asset",
                    "assets/main_object_transparent.png",
                    "--carrier-reference",
                    "assets/carrier_reference.png",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            candidate_dir = output / "_staging" / "repair_candidates" / "main_object"
            recolor = Image.open(
                candidate_dir / "main_object-keep-current-alpha-recolor.png"
            ).convert("RGBA")
            subtract = Image.open(
                candidate_dir / "main_object-tile-subtract.png"
            ).convert("RGBA")
            self.assertNotEqual(recolor.getchannel("A").tobytes(), subtract.getchannel("A").tobytes())

    def test_upscale_repair_downscale_prepares_and_finalizes_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (8, 8), (20, 20, 20, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            asset_path = output / "assets" / "main_object_transparent.png"
            mask_path = output / "masks" / "mask_main.png"
            Image.new("RGBA", (4, 4), (255, 0, 0, 255)).save(asset_path)
            Image.new("L", (4, 4), 255).save(mask_path)
            self._write_single_object_metadata(output)

            prep_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "upscale_repair_downscale.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--source-asset",
                    "assets/main_object_transparent.png",
                    "--source-mask",
                    "masks/mask_main.png",
                    "--scale",
                    "2",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(prep_result.returncode, 0, prep_result.stderr)
            prepared_asset = output / "_staging" / "upscale_work" / "main_object" / "main_object_x2_prepared.png"
            prepared_mask = output / "_staging" / "upscale_work" / "main_object" / "main_object_x2_prepared_mask.png"
            self.assertTrue(prepared_asset.exists())
            self.assertTrue(prepared_mask.exists())

            finalize_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "upscale_repair_downscale.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--source-asset",
                    "assets/main_object_transparent.png",
                    "--source-mask",
                    "masks/mask_main.png",
                    "--scale",
                    "2",
                    "--repaired-upscaled-asset",
                    "_staging/upscale_work/main_object/main_object_x2_prepared.png",
                    "--repaired-upscaled-mask",
                    "_staging/upscale_work/main_object/main_object_x2_prepared_mask.png",
                    "--candidate-id",
                    "main-object-upscaled",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(finalize_result.returncode, 0, finalize_result.stderr)
            self.assertTrue(
                (
                    output
                    / "_staging"
                    / "repair_candidates"
                    / "main_object"
                    / "main-object-upscaled.png"
                ).exists()
            )

    def test_record_quality_review_requires_target_for_object_type_update(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_quality_review.py"),
                    str(output),
                    "--object-type",
                    "ui-glyph",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("object-targeted updates require --object-id or --all-objects", result.stderr)

    def test_compare_candidate_assets_rejects_score_manifest_missing_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (8, 8), (20, 20, 20, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 4), (255, 0, 0, 255)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (8, 8), 255).save(output / "masks" / "mask_main.png")
            self._write_single_object_metadata(output)
            candidate_dir = output / "_staging" / "repair_candidates"
            candidate_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (4, 4), (255, 0, 0, 255)).save(candidate_dir / "candidate_a.png")
            Image.new("RGBA", (4, 4), (200, 0, 0, 255)).save(candidate_dir / "candidate_b.png")

            score_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "score_candidate_assets.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate",
                    "candidate-a=_staging/repair_candidates/candidate_a.png",
                    "--reference-asset",
                    "assets/main_object_transparent.png",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(score_result.returncode, 0, score_result.stderr)
            score_report = json.loads(score_result.stdout)

            compare_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "compare_candidate_assets.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate",
                    "candidate-a=_staging/repair_candidates/candidate_a.png",
                    "--candidate",
                    "candidate-b=_staging/repair_candidates/candidate_b.png",
                    "--compare-note",
                    "Reject stale score manifest coverage.",
                    "--compare-criterion",
                    "score completeness",
                    "--score-manifest",
                    score_report["score_manifest_path"],
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(compare_result.returncode, 0)
            self.assertIn("score manifest is missing entries for compare candidates", compare_result.stderr)

    def test_candidate_compare_and_promote_end_to_end_flow(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (6, 6), (20, 20, 20, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 4), (255, 0, 0, 255)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (6, 6), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0]["asset_class"] = "grouped-support"
            metadata["objects"][0]["reuse_status"] = "approximate-reconstruction"
            metadata["objects"][0]["delivery_class"] = "approximate-reconstruction"
            metadata["objects"][0]["approximate"] = True
            metadata["objects"][0]["reconstruction_provenance"] = "manual redraw candidate flow"
            metadata["objects"][0]["active_reconstruction_method"] = "manual redraw candidate flow"
            metadata["objects"][0]["manual_review_confirmed"] = True
            metadata["granularity"].update(
                {
                    "scope_strategy": "high-signal-subset",
                    "text_handling": "rebuild-downstream",
                    "carrier_glyph_policy": "split",
                    "background_expectation": "approximate-accepted",
                    "layer_independence": "animation-ready",
                }
            )
            metadata["decision_log"] = [
                {
                    "stage": "reconstruction-acceptance",
                    "pause_category": "user-decision",
                    "question": "Accept approximate reconstructed carrier after candidate review?",
                    "recommended_answer": "yes",
                    "recorded_answer": "yes",
                    "decision_effect": "Allow promotion of the chosen candidate after compare evidence.",
                    "decision_source": "explicit-user-confirmed",
                    "evidence_ref": "chat:reconstruction-accepted",
                    "blocking": "true",
                }
            ]
            metadata["confirmation"]["tooling_preflight"]["status"] = "confirmed"
            metadata["confirmation"]["tooling_preflight"]["source"] = "inferred-from-user"
            metadata["confirmation"]["tooling_preflight"]["evidence_ref"] = "chat:tooling-approved"
            metadata["confirmation"]["approximate_reconstruction"]["status"] = "confirmed"
            metadata["confirmation"]["approximate_reconstruction"]["source"] = "explicit-user-confirmed"
            metadata["confirmation"]["final_promotion_acceptance"]["status"] = "confirmed"
            metadata["confirmation"]["final_promotion_acceptance"]["source"] = "explicit-user-confirmed"
            metadata["qa"]["status"] = "needs-review"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            candidate_dir = output / "_staging" / "repair_candidates"
            candidate_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (4, 4), (0, 255, 0, 255)).save(candidate_dir / "candidate_a.png")
            Image.new("RGBA", (4, 4), (0, 0, 255, 255)).save(candidate_dir / "candidate_b.png")
            Image.new("L", (6, 6), 255).save(candidate_dir / "candidate_a_mask.png")
            Image.new("L", (6, 6), 255).save(candidate_dir / "candidate_b_mask.png")

            compare_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "compare_candidate_assets.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate",
                    "candidate-a=_staging/repair_candidates/candidate_a.png",
                    "--candidate",
                    "candidate-b=_staging/repair_candidates/candidate_b.png",
                    "--compare-note",
                    "Compare support-plate redraw fidelity.",
                    "--compare-criterion",
                    "shape fidelity",
                    "--compare-criterion",
                    "edge cleanliness",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(compare_result.returncode, 0, compare_result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            comparison_id = metadata["objects"][0]["candidate_comparisons"][0]["comparison_id"]

            promote_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "promote_candidate_asset.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate-asset",
                    "_staging/repair_candidates/candidate_a.png",
                    "--candidate-mask",
                    "_staging/repair_candidates/candidate_a_mask.png",
                    "--candidate-id",
                    "candidate-a",
                    "--comparison-id",
                    comparison_id,
                    "--delivery-class",
                    "approximate-reconstruction",
                    "--active-reconstruction-method",
                    "manual redraw candidate flow",
                    "--repair-note",
                    "Promote best reconstruction candidate after comparison.",
                    "--selection-reason",
                    "Candidate A preserved panel silhouette more faithfully.",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(promote_result.returncode, 0, promote_result.stderr)

            review_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_quality_review.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--mask-alignment",
                    "pass",
                    "--alpha-edges",
                    "pass",
                    "--background-residue",
                    "pass",
                    "--reuse-readiness",
                    "pass",
                    "--decision-stage",
                    "final-promotion-acceptance",
                    "--decision-question",
                    "Promote candidate-a as the current reconstruction revision?",
                    "--decision-recommended",
                    "yes",
                    "--decision-answer",
                    "yes",
                    "--decision-effect",
                    "Candidate A becomes the current revision after compare review.",
                    "--decision-source",
                    "explicit-user-confirmed",
                    "--pause-category",
                    "formal-approval",
                    "--blocking",
                    "true",
                    "--evidence-ref",
                    "chat:candidate-a-promoted",
                    "--review-note",
                    "Compare and promotion evidence reviewed.",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(review_result.returncode, 0, review_result.stderr)
            preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(preview_result.returncode, 0, preview_result.stderr)
            quality_preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_quality_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(quality_preview_result.returncode, 0, quality_preview_result.stderr)

            validate_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_asset_package.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(validate_result.returncode, 0, validate_result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            obj = metadata["objects"][0]
            self.assertEqual(obj["selected_candidate_id"], "candidate-a")
            self.assertEqual(
                obj["candidate_comparisons"][0]["selection_reason"],
                "Candidate A preserved panel silhouette more faithfully.",
            )
            qa_report = (output / "qa_report.md").read_text(encoding="utf-8")
            self.assertIn("Candidate Promotion", qa_report)

    def test_export_asset_manifest_rejects_asset_paths_outside_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            outside_asset = tmp_path / "outside_asset.png"
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(outside_asset)
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0]["asset_path"] = str(outside_asset)
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "export_asset_manifest.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must stay inside the package", result.stderr)
            self.assertFalse((output / "asset_manifest.json").exists())

    def test_validate_asset_package_rejects_object_without_alpha(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGB", (4, 3), (255, 0, 0)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            self._write_single_object_metadata(output)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_asset_package.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("alpha", result.stderr.lower())

    def test_validate_asset_package_rejects_empty_object_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_asset_package.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("object inventory", result.stderr.lower())

    def test_validate_asset_package_rejects_unknown_object_role(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0]["role"] = "mystery"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_asset_package.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("role must be one of", result.stderr)

    def test_validate_asset_package_requires_visual_hierarchy_analysis(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            self._write_single_object_metadata(output, include_analysis=False)
            preview_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_previews.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(preview_result.returncode, 0, preview_result.stderr)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_asset_package.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("visual hierarchy", result.stderr.lower())

    def test_validate_asset_package_requires_granularity_alignment_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata.pop("granularity")
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_asset_package.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("metadata.granularity", result.stderr)

    def test_validate_asset_package_rejects_malformed_decision_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["decision_log"] = [{"stage": "granularity"}]
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            preview_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_previews.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(preview_result.returncode, 0, preview_result.stderr)
            quality_preview_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_quality_previews.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(quality_preview_result.returncode, 0, quality_preview_result.stderr)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_asset_package.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("decision_log", result.stderr)

    def test_validate_asset_package_blocks_draft_packaging_only_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["qa"]["status"] = "pass"
            metadata["capability"] = {
                "production_capable": False,
                "missing_for_production": ["SAM2 or grounded detector", "matting/refinement"],
                "user_choice": "draft-packaging-only",
                "notes": "User chose draft packaging after tooling preflight.",
            }
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            preview_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_previews.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(preview_result.returncode, 0, preview_result.stderr)
            quality_preview_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_quality_previews.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(quality_preview_result.returncode, 0, quality_preview_result.stderr)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_asset_package.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("draft-packaging-only", result.stderr)
            self.assertIn("qa.status pass", result.stderr)

    def test_validate_asset_package_blocks_unrecorded_tooling_preflight_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["qa"]["status"] = "pass"
            metadata["capability"] = {
                "production_capable": False,
                "missing_for_production": [],
                "user_choice": "unset",
                "notes": "",
            }
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            preview_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_previews.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(preview_result.returncode, 0, preview_result.stderr)
            quality_preview_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_quality_previews.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(quality_preview_result.returncode, 0, quality_preview_result.stderr)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_asset_package.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("production_capable=true", result.stderr)

    def test_validate_asset_package_blocks_pass_when_capability_choice_is_unset(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["qa"]["status"] = "pass"
            metadata["capability"]["user_choice"] = "unset"
            metadata["decision_log"] = [
                {
                    "stage": "final-acceptance",
                    "question": "Accept this production-ready layer?",
                    "recommended_answer": "yes",
                    "user_answer": "yes",
                    "decision_effect": "Allow qa.status=pass.",
                }
            ]
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(preview_result.returncode, 0, preview_result.stderr)
            quality_preview_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_quality_previews.py"), str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(quality_preview_result.returncode, 0, quality_preview_result.stderr)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_asset_package.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("metadata.capability.user_choice", result.stderr)

    def test_validate_asset_package_requires_asset_class_and_reuse_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0].pop("asset_class")
            metadata["objects"][0].pop("reuse_status")
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_asset_package.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("asset_class", result.stderr)
            self.assertIn("reuse_status", result.stderr)

    def test_validate_asset_package_blocks_draft_only_production_ready_asset(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["capability"] = {
                "production_capable": False,
                "missing_for_production": ["matting/refinement"],
                "user_choice": "draft-packaging-only",
                "notes": "Draft-only package.",
            }
            metadata["qa"]["status"] = "needs-review"
            metadata["objects"][0]["asset_class"] = "atomic"
            metadata["objects"][0]["reuse_status"] = "production-ready"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_asset_package.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("draft-packaging-only", result.stderr)
            self.assertIn("production-ready", result.stderr)

    def test_validate_asset_package_rejects_unconfirmed_granularity_alignment(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["granularity"]["mode"] = "unset"
            metadata["granularity"]["user_confirmed"] = False
            metadata["granularity"]["notes"] = ""
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            preview_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_previews.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(preview_result.returncode, 0, preview_result.stderr)
            quality_preview_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_quality_previews.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(quality_preview_result.returncode, 0, quality_preview_result.stderr)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_asset_package.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("granularity", result.stderr.lower())
            self.assertIn("confirmed", result.stderr.lower())

    def test_validate_asset_package_rejects_paths_outside_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            outside_asset = tmp_path / "outside_asset.png"
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(outside_asset)
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0]["asset_path"] = str(outside_asset)
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_asset_package.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must stay inside the package", result.stderr)

    def test_validate_asset_package_checks_nested_quality_preview_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["previews"] = {
                "quality": {
                    "main_object": {
                        "mask_overlay": "previews/missing_overlay.png",
                    }
                }
            }
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_asset_package.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("preview file is missing", result.stderr)

    def test_validate_asset_package_requires_extraction_pipeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            self._write_single_object_metadata(output, include_pipeline=False)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_asset_package.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("extraction_pipeline", result.stderr)

    def test_validate_asset_package_requires_object_quality_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            self._write_single_object_metadata(output, include_quality_evidence=False)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_asset_package.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("quality_checks", result.stderr)

    def test_validate_asset_package_requires_composition_order_for_layers(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0].pop("composition_order")
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_asset_package.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("composition_order", result.stderr)

    def test_validate_asset_package_requires_structured_tool_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["extraction_pipeline"]["tools"] = ["sam2"]
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_asset_package.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("tools entries must include name, role, and version", result.stderr)

    def test_validate_asset_package_blocks_pass_status_when_quality_checks_are_not_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["qa"]["status"] = "pass"
            metadata["objects"][0]["quality_checks"]["alpha_edges"] = "needs-review"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_asset_package.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("qa.status cannot be pass", result.stderr)

    def test_validate_asset_package_blocks_crop_only_pass_without_manual_confirmation(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["qa"]["status"] = "pass"
            metadata["objects"][0]["mask_source"] = "manual-estimated crop"
            metadata["objects"][0]["extraction_method"] = "estimated"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            preview_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_previews.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(preview_result.returncode, 0, preview_result.stderr)
            quality_preview_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_quality_previews.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(quality_preview_result.returncode, 0, quality_preview_result.stderr)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_asset_package.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("crop-only", result.stderr)
            self.assertIn("manual_review_confirmed", result.stderr)

    def test_validate_asset_package_blocks_helper_only_pass_without_manual_confirmation(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["qa"]["status"] = "pass"
            metadata["objects"][0]["mask_source"] = "OpenCV threshold"
            metadata["objects"][0]["alpha_source"] = "Pillow crop alpha"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            preview_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_previews.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(preview_result.returncode, 0, preview_result.stderr)
            quality_preview_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_quality_previews.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(quality_preview_result.returncode, 0, quality_preview_result.stderr)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_asset_package.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("helper-only", result.stderr)
            self.assertIn("manual_review_confirmed", result.stderr)

    def test_validate_asset_package_rejects_unarchived_intermediate_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            (output / "external-sam-assets").mkdir()
            (output / "sam_subset_manifest.json").write_text("{}", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_asset_package.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("_staging", result.stderr)
            self.assertIn("_archive_intermediate", result.stderr)

    def test_validate_asset_package_requires_reconstruction_provenance_for_approximate_layers(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0]["id"] = "background_clean"
            metadata["objects"][0]["role"] = "group"
            metadata["objects"][0]["layer_kind"] = "background"
            metadata["objects"][0]["semantic_boundary"] = "Approximate reconstructed background clean plate."
            metadata["objects"][0]["asset_path"] = "assets/main_object_transparent.png"
            metadata["objects"][0]["mask_path"] = "masks/mask_main.png"
            metadata["objects"][0]["mask_source"] = "inpaint reconstruction"
            metadata["objects"][0]["alpha_source"] = "reconstructed rgba"
            metadata["objects"][0]["extraction_method"] = "estimated"
            metadata["objects"][0]["approximate"] = True
            metadata["qa"]["status"] = "pass"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            preview_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_previews.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(preview_result.returncode, 0, preview_result.stderr)
            quality_preview_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_quality_previews.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(quality_preview_result.returncode, 0, quality_preview_result.stderr)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_asset_package.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("reconstruction_provenance", result.stderr)
            self.assertIn("approximate", result.stderr)

    def test_validate_asset_package_requires_delivery_class_for_approximate_reconstruction(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0]["approximate"] = True
            metadata["objects"][0]["reconstruction_provenance"] = "manual redraw candidate"
            metadata["objects"][0]["active_reconstruction_method"] = ""
            metadata["objects"][0]["delivery_class"] = "clean-extraction"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            preview_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_previews.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(preview_result.returncode, 0, preview_result.stderr)
            quality_preview_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_quality_previews.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(quality_preview_result.returncode, 0, quality_preview_result.stderr)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_asset_package.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("delivery_class=approximate-reconstruction", result.stderr)
            self.assertIn("active_reconstruction_method", result.stderr)

    def test_validate_asset_package_rejects_non_object_analysis_without_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["analysis"] = "not a dict"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_asset_package.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("Traceback", result.stderr)
            self.assertIn("metadata.analysis must be an object", result.stderr)

    def test_validate_asset_package_rejects_malformed_metadata_sections_without_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            metadata["analysis"] = {
                "visual_hierarchy": ["background", "main object"],
                "recommended_split_plan": "Keep the main object separate from the background.",
            }
            metadata["extraction_pipeline"] = {
                "recipe": "grounded-segmentation-matting-repair",
                "stages": [
                    "semantic-analysis",
                    "segmentation",
                    "alpha-refinement",
                    "layer-packaging",
                    "qa-review",
                ],
                "quality_gates": ["mask provenance recorded"],
                "tools": [{"name": "manual-fixture", "role": "test", "version": "local"}],
            }
            metadata["source"] = None
            metadata["objects"] = ["not an object"]
            metadata["qa"] = None
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_asset_package.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("Traceback", result.stderr)
            self.assertIn("metadata.source must be an object", result.stderr)
            self.assertIn("metadata.qa must be an object", result.stderr)
            self.assertIn("metadata.objects entries must be objects", result.stderr)

    def test_validate_asset_package_rejects_non_object_decision_routing_without_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            Image.new("RGBA", (4, 3), (255, 0, 0, 128)).save(
                output / "assets" / "main_object_transparent.png"
            )
            Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
            metadata = self._write_single_object_metadata(output)
            metadata["analysis"] = {
                "visual_hierarchy": ["ui panel", "status glyph"],
                "recommended_split_plan": "Review text routing object by object.",
            }
            metadata["objects"][0]["decision_routing"] = "bad-string"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_asset_package.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("Traceback", result.stderr)
            self.assertIn("decision_routing must be an object", result.stderr)


if __name__ == "__main__":
    unittest.main()
