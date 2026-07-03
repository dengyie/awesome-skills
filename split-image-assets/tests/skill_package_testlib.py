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


class SplitImageAssetsTestBase(unittest.TestCase):
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
        Image.new("RGBA", (4, 3), (255, 0, 0, 255)).save(
            output / "assets" / "main_object_transparent.png"
        )
        Image.new("L", (4, 3), 255).save(output / "masks" / "mask_main.png")
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
    def _write_generated_plan_manifest(
        self,
        output: pathlib.Path,
        object_id: str = "main_object",
        protected_approval_required: bool = False,
        protected_approval_ref: str = "",
    ) -> dict:
        plan_manifest = {
            "schema_version": "1.0",
            "package_name": "fixture",
            "source": {
                "path": "source/source_original.png",
                "width": 4,
                "height": 3,
            },
            "quality_target": {
                "tier": "visual-acceptance-ready",
                "notes": "Generated route fixture.",
            },
            "planning_status": {
                "status": "completed",
                "notes": "Fixture planning complete.",
            },
            "route_policy": {
                "planning_required": True,
                "generation_routing_gate": "confirmed",
                "plan_manifest_rollout_stage": "phase3-test",
                "notes": "",
            },
            "provider_preferences": {
                "generation_provider_class": "codex-controlled-generation",
                "segmentation_provider_class": "unset",
            },
            "objects": [
                {
                    "object_id": object_id,
                    "object_type": "ui-carrier",
                    "planned_route": "generate",
                    "route_signals": {
                        "recoverability_low": True,
                        "object_is_reconstruction_like": True,
                        "quality_target_high": True,
                        "segmentation_cost_unfavorable": True,
                    },
                    "route_score": 4,
                    "route_reason": "Fixture object is generation-routed.",
                    "needs_user_confirmation": False,
                    "attempt_budget": 1,
                    "attempts_used": 1,
                    "attempt_history": ["pilot generated candidate"],
                    "token_budget_hint": "low",
                    "pilot_group": "fixture-group",
                    "promotion_requirement": "object approval required",
                    "protected_policy": "none" if not protected_approval_required else "primary-brand-logo",
                    "protected_approval_required": protected_approval_required,
                    "protected_approval_ref": protected_approval_ref,
                    "why_not_extract": "Hidden pixels are missing.",
                    "why_not_reconstruct": "Local reconstruction would stay too approximate.",
                    "why_generate": "Constrained generation is the cleaner truthful route.",
                    "risk_note": "Needs explicit generated-delivery evidence.",
                }
            ],
            "batch_groups": [],
            "summary": {
                "planned_extract": 0,
                "planned_reconstruct": 0,
                "planned_generate": 1,
                "planned_rebuild_downstream": 0,
                "planned_support_only": 0,
            },
        }
        (output / "plan_manifest.json").write_text(
            json.dumps(plan_manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return plan_manifest
