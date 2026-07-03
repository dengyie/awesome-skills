import pathlib
import sys

TESTS_DIR = pathlib.Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from skill_package_testlib import Image, REPO, ROOT, SplitImageAssetsTestBase, json, pathlib, re, subprocess, sys, tempfile


class SplitImageAssetsPackageTests(SplitImageAssetsTestBase):
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
        self.assertIn("generation", report)
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
        for capability_key in ["segmentation", "matting", "reconstruction", "generation"]:
            self.assertIn("installed", report[capability_key])
            self.assertIn("runtime_ready", report[capability_key])
            self.assertIn("production_ready", report[capability_key])
        self.assertIn("path_type", report["reconstruction"])
        self.assertIn("quality_impact", report["reconstruction"])
        self.assertIn("provider_classes", report["generation"])
        self.assertIn("codex-controlled-generation", report["generation"]["provider_classes"])
        self.assertIn("external-generated-outputs", report["generation"]["provider_classes"])
        self.assertIn("local-model-runtime", report["generation"]["provider_classes"])
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
    def test_generation_capability_affects_missing_roles_and_messages(self):
        module = self._load_check_environment_module()
        capabilities = {
            "segmentation": {"production_ready": True},
            "matting": {"production_ready": True},
            "reconstruction": {"production_ready": True, "path_type": "dedicated-tool"},
            "generation": {"production_ready": False},
            "environment": {"torch": {"runtime_ready": True}},
        }

        self.assertIn("generated-reconstruction", module.missing_roles(capabilities))
        self.assertTrue(
            any("generated" in message.lower() for message in module.why_it_matters(capabilities))
        )
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
            self.assertTrue((output / "plan_manifest.json").exists())
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            plan_manifest = json.loads((output / "plan_manifest.json").read_text(encoding="utf-8"))
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
                    "generation": {
                        "provider_class": "unset",
                        "installed": False,
                        "runtime_ready": False,
                        "production_ready": False,
                        "notes": "",
                    },
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
                    "generation_routing": {
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
            self.assertEqual(metadata["asset_summary"]["accepted_approximate_reconstructions"], 0)
            self.assertEqual(metadata["asset_summary"]["accepted_generated_reconstructions"], 0)
            self.assertEqual(metadata["asset_summary"]["draft_candidate_assets"], 0)
            self.assertEqual(metadata["asset_summary"]["support_only_layers"], 0)
            self.assertNotIn("final_promotion_acceptance", metadata["confirmation"])
            self.assertEqual(plan_manifest["package_name"], "fixture")
            self.assertEqual(plan_manifest["planning_status"]["status"], "pending")
            self.assertEqual(plan_manifest["route_policy"]["generation_routing_gate"], "pending")
            self.assertTrue(plan_manifest["route_policy"]["planning_required"])
            self.assertEqual(plan_manifest["provider_preferences"]["generation_provider_class"], "unset")
            self.assertEqual(plan_manifest["summary"]["planned_generate"], 0)
            self.assertIn(
                "Final status: needs-review",
                (output / "qa_report.md").read_text(encoding="utf-8"),
            )
    def test_shared_contract_module_defines_confirmation_pause_defaults(self):
        contract = self._load_script_module("split_image_assets_contract.py")
        self.assertEqual(
            contract.DEFAULT_PAUSE_CATEGORY_BY_CONFIRMATION["approximate_reconstruction"],
            "user-decision",
        )
        self.assertEqual(
            contract.DEFAULT_PAUSE_CATEGORY_BY_CONFIRMATION["generation_routing"],
            "user-decision",
        )
        self.assertEqual(
            contract.DEFAULT_PAUSE_CATEGORY_BY_CONFIRMATION["tooling_preflight"],
            "external-blocker",
        )
        self.assertIn("generate", contract.ALLOWED_PLANNED_ROUTES)
        self.assertIn("codex-controlled-generation", contract.ALLOWED_GENERATION_PROVIDER_CLASSES)
    def test_package_state_lib_summarizes_asset_entries_consistently(self):
        module = self._load_script_module("package_state_lib.py")
        summary = module.summarize_asset_entries(
            [
                {"asset_class": "atomic", "reuse_status": "production-ready"},
                {"asset_class": "candidate", "reuse_status": "draft-candidate"},
                {"asset_class": "atomic", "reuse_status": "accepted-generated-reconstruction"},
                {"asset_class": "grouped-support", "reuse_status": "support-only"},
                {"asset_class": "atomic", "reuse_status": "blocked"},
            ]
        )
        self.assertEqual(
            summary,
            {
                "production_ready_assets": 1,
                "accepted_approximate_reconstructions": 0,
                "accepted_generated_reconstructions": 1,
                "draft_candidate_assets": 1,
                "support_only_layers": 1,
                "blocked_assets": 1,
            },
        )
    def test_package_state_lib_reads_and_finds_plan_manifest_objects(self):
        module = self._load_script_module("package_state_lib.py")
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            plan_manifest = {
                "objects": [
                    {"object_id": "a", "planned_route": "extract"},
                    {"object_id": "b", "planned_route": "generate"},
                ]
            }
            module.write_plan_manifest(tmp_path, plan_manifest)
            loaded = module.read_plan_manifest(tmp_path)
            self.assertEqual(loaded, plan_manifest)
            self.assertEqual(module.find_plan_object(loaded, "b"), {"object_id": "b", "planned_route": "generate"})
            self.assertIsNone(module.find_plan_object(loaded, "missing"))
    def test_provider_registry_exposes_default_route_chains(self):
        module = self._load_script_module("provider_registry.py")
        self.assertEqual(
            module.get_default_route_chain("extract"),
            ["grounded-sam-bridge"],
        )
        self.assertEqual(
            module.get_default_route_chain("generate"),
            ["codex-controlled-generation"],
        )
        self.assertEqual(
            module.get_provider_spec("external-generated-outputs")["execution_mode"],
            "external-manifest",
        )
        self.assertEqual(
            module.get_default_provider_chain("extract", "photo-object-matte"),
            ["external-professional-outputs"],
        )
        self.assertEqual(
            module.get_default_provider_chain("extract", "ui-carrier"),
            ["grounded-sam-bridge"],
        )
    def test_provider_contract_validates_request_and_result(self):
        module = self._load_script_module("provider_contract.py")
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            (tmp_path / "source").mkdir()
            (tmp_path / "_staging" / "providers" / "grounded-sam-bridge" / "main_object").mkdir(parents=True)
            (tmp_path / "source" / "source_original.png").write_bytes(b"source")
            request = {
                "schema_version": "1.0",
                "package_name": "fixture",
                "provider_id": "grounded-sam-bridge",
                "provider_role": "segmentation",
                "execution_mode": "bridge",
                "object_id": "main_object",
                "object_type": "ui-carrier",
                "planned_route": "extract",
                "quality_target": "visual-acceptance-ready",
                "source_image": "source/source_original.png",
                "input_refs": {"source_crop": "_staging/providers/grounded-sam-bridge/main_object/crop.png"},
                "expected_outputs": {"asset_png": True, "source_space_mask": True},
                "notes": "",
            }
            result = {
                "schema_version": "1.0",
                "package_name": "fixture",
                "provider_id": "grounded-sam-bridge",
                "provider_role": "segmentation",
                "execution_mode": "bridge",
                "object_id": "main_object",
                "status": "success",
                "artifacts": {
                    "asset_png": "_staging/providers/grounded-sam-bridge/main_object/main_object.png",
                    "source_space_mask": "_staging/providers/grounded-sam-bridge/main_object/main_object_mask.png",
                },
                "provenance": {
                    "tool_name": "Grounded-SAM",
                    "tool_role": "segmentation",
                    "tool_version": "external",
                    "execution_mode": "bridge",
                },
                "warnings": [],
                "production_ready_hint": False,
                "next_expected_provider": "rembg-bridge",
                "notes": "",
            }
            module.validate_provider_request(tmp_path, request)
            module.validate_provider_result(tmp_path, result)
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



