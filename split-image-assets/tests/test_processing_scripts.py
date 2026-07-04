import pathlib
import shutil
import sys

TESTS_DIR = pathlib.Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from skill_package_testlib import Image, REPO, ROOT, SplitImageAssetsTestBase, json, pathlib, re, subprocess, sys, tempfile


class SplitImageAssetsPackageTests(SplitImageAssetsTestBase):
    def test_prepare_provider_request_writes_bridge_request_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            self._write_generated_plan_manifest(output)
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0]["object_type"] = "ui-carrier"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            planning_dir = output / "_staging" / "planning"
            planning_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (2, 2), (255, 0, 0, 255)).save(planning_dir / "main_object_crop.png")
            Image.new("L", (4, 3), 255).save(planning_dir / "main_object_mask.png")
            self._write_generation_brief(output)
            metadata_before = json.loads((output / "metadata.json").read_text(encoding="utf-8"))

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "prepare_provider_request.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--provider-id",
                    "codex-controlled-generation",
                    "--input-ref",
                    "source_crop=_staging/planning/main_object_crop.png",
                    "--input-ref",
                    "rough_mask=_staging/planning/main_object_mask.png",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            request_path = output / "_staging" / "providers" / "codex-controlled-generation" / "main_object" / "request.json"
            self.assertTrue(request_path.exists())
            request = json.loads(request_path.read_text(encoding="utf-8"))
            self.assertEqual(request["provider_id"], "codex-controlled-generation")
            self.assertEqual(request["planned_route"], "generate")
            self.assertEqual(request["input_refs"]["source_crop"], "_staging/planning/main_object_crop.png")
            metadata_after = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata_after, metadata_before)
    def test_prepare_provider_request_selects_default_provider_when_omitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            self._write_generated_plan_manifest(output)
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0]["object_type"] = "ui-carrier"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            self._write_generation_brief(output)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "prepare_provider_request.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            request = json.loads(
                (
                    output
                    / "_staging"
                    / "providers"
                    / "codex-controlled-generation"
                    / "main_object"
                    / "request.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(request["provider_id"], "codex-controlled-generation")
    def test_prepare_provider_request_applies_object_type_override_when_omitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            plan_manifest = {
                "schema_version": "1.0",
                "package_name": "fixture",
                "source": {"path": "source/source_original.png", "width": 4, "height": 3},
                "quality_target": {"tier": "visual-acceptance-ready", "notes": ""},
                "planning_status": {"status": "completed", "notes": ""},
                "route_policy": {"planning_required": True, "generation_routing_gate": "confirmed"},
                "provider_preferences": {"generation_provider_class": "unset"},
                "objects": [
                    {
                        "object_id": "main_object",
                        "object_type": "photo-object-matte",
                        "planned_route": "extract",
                    }
                ],
                "summary": {},
            }
            (output / "plan_manifest.json").write_text(
                json.dumps(plan_manifest, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            self._write_single_object_metadata(output)
            self._set_candidate_promotion_confirmation(output)
            self._set_candidate_promotion_confirmation(output)
            self._set_candidate_promotion_confirmation(output)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "prepare_provider_request.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            request = json.loads(
                (
                    output
                    / "_staging"
                    / "providers"
                    / "external-professional-outputs"
                    / "main_object"
                    / "request.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(request["provider_id"], "external-professional-outputs")
    def test_prepare_provider_request_prefers_generation_provider_from_plan_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            plan_manifest = self._write_generated_plan_manifest(output)
            plan_manifest["provider_preferences"]["generation_provider_class"] = "external-generated-outputs"
            (output / "plan_manifest.json").write_text(
                json.dumps(plan_manifest, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            self._write_single_object_metadata(output)
            self._set_candidate_promotion_confirmation(output)
            self._set_candidate_promotion_confirmation(output)
            self._set_candidate_promotion_confirmation(output)
            self._write_generation_brief(output)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "prepare_provider_request.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            request = json.loads(
                (
                    output
                    / "_staging"
                    / "providers"
                    / "external-generated-outputs"
                    / "main_object"
                    / "request.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(request["provider_id"], "external-generated-outputs")
    def test_prepare_generation_brief_writes_brief_and_reference_inputs_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            self._write_generated_plan_manifest(output)
            planning_dir = output / "_staging" / "planning"
            planning_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (2, 2), (255, 0, 0, 255)).save(planning_dir / "main_object_crop.png")
            Image.new("L", (4, 3), 255).save(planning_dir / "main_object_mask.png")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "prepare_generation_brief.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--reference-input",
                    "source/source_original.png",
                    "--style-constraint",
                    "match existing dashboard palette",
                    "--must-keep",
                    "outer silhouette",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            brief = json.loads((output / payload["generation_brief_path"]).read_text(encoding="utf-8"))
            references = json.loads((output / payload["reference_inputs_path"]).read_text(encoding="utf-8"))
            self.assertEqual(brief["object_id"], "main_object")
            self.assertEqual(brief["source_crop"], "_staging/planning/main_object_crop.png")
            self.assertEqual(brief["rough_mask"], "_staging/planning/main_object_mask.png")
            self.assertIn("match existing dashboard palette", brief["style_constraints"])
            self.assertEqual(references["reference_inputs"], ["source/source_original.png"])
    def test_prepare_generation_brief_rejects_non_generate_plan_object(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            plan_manifest = {
                "schema_version": "1.0",
                "package_name": "fixture",
                "source": {"path": "source/source_original.png", "width": 4, "height": 3},
                "quality_target": {"tier": "visual-acceptance-ready", "notes": ""},
                "planning_status": {"status": "completed", "notes": ""},
                "route_policy": {"planning_required": True, "generation_routing_gate": "confirmed"},
                "provider_preferences": {"generation_provider_class": "unset"},
                "objects": [
                    {
                        "object_id": "main_object",
                        "object_type": "ui-carrier",
                        "planned_route": "extract",
                    }
                ],
                "summary": {},
            }
            (output / "plan_manifest.json").write_text(
                json.dumps(plan_manifest, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "prepare_generation_brief.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("planned_route=generate", result.stderr)
    def test_prepare_provider_request_rejects_generate_route_without_prepared_brief(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            self._write_generated_plan_manifest(output)
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0]["object_type"] = "ui-carrier"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "prepare_provider_request.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("prepare_generation_brief.py", result.stderr)
    def test_prepare_provider_request_auto_includes_generation_brief_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            self._write_generated_plan_manifest(output)
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0]["object_type"] = "ui-carrier"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            self._write_generation_brief(output)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "prepare_provider_request.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            request = json.loads(
                (
                    output
                    / "_staging"
                    / "providers"
                    / "codex-controlled-generation"
                    / "main_object"
                    / "request.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(
                request["input_refs"]["generation_brief"],
                "_staging/generation_briefs/main_object.json",
            )
            self.assertEqual(
                request["input_refs"]["reference_inputs"],
                "_staging/generation_briefs/main_object_reference_inputs.json",
            )
    def test_prepare_provider_request_prefers_segmentation_provider_from_plan_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            plan_manifest = {
                "schema_version": "1.0",
                "package_name": "fixture",
                "source": {"path": "source/source_original.png", "width": 4, "height": 3},
                "quality_target": {"tier": "visual-acceptance-ready", "notes": ""},
                "planning_status": {"status": "completed", "notes": ""},
                "route_policy": {"planning_required": True, "generation_routing_gate": "confirmed"},
                "provider_preferences": {
                    "generation_provider_class": "unset",
                    "segmentation_provider_class": "external-professional-outputs",
                },
                "objects": [
                    {
                        "object_id": "main_object",
                        "object_type": "ui-carrier",
                        "planned_route": "extract",
                    }
                ],
                "summary": {},
            }
            (output / "plan_manifest.json").write_text(
                json.dumps(plan_manifest, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            self._write_single_object_metadata(output)
            self._set_candidate_promotion_confirmation(output)
            self._set_candidate_promotion_confirmation(output)
            self._set_candidate_promotion_confirmation(output)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "prepare_provider_request.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            request = json.loads(
                (
                    output
                    / "_staging"
                    / "providers"
                    / "external-professional-outputs"
                    / "main_object"
                    / "request.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(request["provider_id"], "external-professional-outputs")
    def test_prepare_provider_request_falls_back_when_preference_is_unsupported(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            plan_manifest = {
                "schema_version": "1.0",
                "package_name": "fixture",
                "source": {"path": "source/source_original.png", "width": 4, "height": 3},
                "quality_target": {"tier": "visual-acceptance-ready", "notes": ""},
                "planning_status": {"status": "completed", "notes": ""},
                "route_policy": {"planning_required": True, "generation_routing_gate": "confirmed"},
                "provider_preferences": {
                    "generation_provider_class": "unset",
                    "segmentation_provider_class": "codex-controlled-generation",
                },
                "objects": [
                    {
                        "object_id": "main_object",
                        "object_type": "ui-carrier",
                        "planned_route": "extract",
                    }
                ],
                "summary": {},
            }
            (output / "plan_manifest.json").write_text(
                json.dumps(plan_manifest, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            self._write_single_object_metadata(output)
            self._set_candidate_promotion_confirmation(output)
            self._set_candidate_promotion_confirmation(output)
            self._set_candidate_promotion_confirmation(output)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "prepare_provider_request.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            request = json.loads(
                (
                    output
                    / "_staging"
                    / "providers"
                    / "grounded-sam-bridge"
                    / "main_object"
                    / "request.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(request["provider_id"], "grounded-sam-bridge")
    def test_describe_provider_plan_writes_provider_plan_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            plan_manifest = {
                "schema_version": "1.0",
                "package_name": "fixture",
                "source": {"path": "source/source_original.png", "width": 4, "height": 3},
                "quality_target": {"tier": "visual-acceptance-ready", "notes": ""},
                "planning_status": {"status": "completed", "notes": ""},
                "route_policy": {"planning_required": True, "generation_routing_gate": "confirmed"},
                "provider_preferences": {
                    "generation_provider_class": "external-generated-outputs",
                    "segmentation_provider_class": "unset",
                },
                "objects": [
                    {
                        "object_id": "hero_logo",
                        "object_type": "outlined-illustration-logo",
                        "planned_route": "extract",
                    },
                    {
                        "object_id": "reconstructed_badge",
                        "object_type": "ui-carrier",
                        "planned_route": "generate",
                    },
                    {
                        "object_id": "live_text",
                        "object_type": "generic-object",
                        "planned_route": "rebuild_downstream",
                    },
                ],
                "summary": {},
            }
            (output / "plan_manifest.json").write_text(
                json.dumps(plan_manifest, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            self._write_single_object_metadata(output)
            self._set_candidate_promotion_confirmation(output)
            self._set_candidate_promotion_confirmation(output)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "describe_provider_plan.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["provider_plan_path"], "_staging/providers/provider_plan.json")
            self.assertEqual(payload["object_count"], 3)
            provider_plan = json.loads(
                (output / payload["provider_plan_path"]).read_text(encoding="utf-8")
            )
            by_object_id = {entry["object_id"]: entry for entry in provider_plan["objects"]}
            self.assertEqual(by_object_id["hero_logo"]["selected_provider_id"], "external-professional-outputs")
            self.assertEqual(by_object_id["hero_logo"]["selection_source"], "object-type-override")
            self.assertEqual(by_object_id["reconstructed_badge"]["selected_provider_id"], "external-generated-outputs")
            self.assertEqual(by_object_id["reconstructed_badge"]["selection_source"], "plan-preference")
            self.assertEqual(by_object_id["live_text"]["selected_provider_id"], "")
            self.assertEqual(by_object_id["live_text"]["selection_source"], "route-default")
    def test_describe_provider_plan_records_invalid_preference_status_and_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            plan_manifest = {
                "schema_version": "1.0",
                "package_name": "fixture",
                "source": {"path": "source/source_original.png", "width": 4, "height": 3},
                "quality_target": {"tier": "visual-acceptance-ready", "notes": ""},
                "planning_status": {"status": "completed", "notes": ""},
                "route_policy": {"planning_required": True, "generation_routing_gate": "confirmed"},
                "provider_preferences": {
                    "generation_provider_class": "unset",
                    "segmentation_provider_class": "local-model-runtime",
                },
                "objects": [
                    {
                        "object_id": "main_object",
                        "object_type": "ui-carrier",
                        "planned_route": "extract",
                    }
                ],
                "summary": {},
            }
            (output / "plan_manifest.json").write_text(
                json.dumps(plan_manifest, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            self._write_single_object_metadata(output)
            self._set_candidate_promotion_confirmation(output)
            self._set_candidate_promotion_confirmation(output)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "describe_provider_plan.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            entry = payload["objects"][0]
            self.assertEqual(entry["preferred_provider_status"], "invalid-provider-id")
            self.assertEqual(entry["selected_provider_id"], "grounded-sam-bridge")
            self.assertEqual(entry["selection_source"], "route-default")
            self.assertIn("external-professional-outputs", entry["alternative_provider_chain"])
    def test_describe_provider_plan_filters_single_object(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            plan_manifest = self._write_generated_plan_manifest(output)
            plan_manifest["objects"].append(
                {
                    "object_id": "secondary",
                    "object_type": "ui-glyph",
                    "planned_route": "extract",
                }
            )
            (output / "plan_manifest.json").write_text(
                json.dumps(plan_manifest, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            self._write_single_object_metadata(output)
            self._set_candidate_promotion_confirmation(output)
            self._set_candidate_promotion_confirmation(output)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "describe_provider_plan.py"),
                    str(output),
                    "--object-id",
                    "secondary",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["object_count"], 1)
            self.assertEqual(payload["objects"][0]["object_id"], "secondary")
    def test_describe_provider_work_items_recommends_prepare_generation_brief(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            self._write_generated_plan_manifest(output)
            self._write_single_object_metadata(output)
            self._set_candidate_promotion_confirmation(output)
            self._set_candidate_promotion_confirmation(output)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "describe_provider_work_items.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["provider_work_items_path"], "_staging/providers/provider_work_items.json")
            entry = payload["objects"][0]
            self.assertEqual(entry["next_action"], "prepare-generation-brief")
            self.assertIn("prepare_generation_brief.py", entry["recommended_command"])
    def test_describe_provider_work_items_recommends_prepare_provider_request_after_brief(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            self._write_generated_plan_manifest(output)
            self._write_single_object_metadata(output)
            self._set_candidate_promotion_confirmation(output)
            self._set_candidate_promotion_confirmation(output)
            self._write_generation_brief(output)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "describe_provider_work_items.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            entry = json.loads(result.stdout)["objects"][0]
            self.assertEqual(entry["next_action"], "prepare-provider-request")
            self.assertEqual(entry["selected_provider_id"], "codex-controlled-generation")
            self.assertIn("prepare_provider_request.py", entry["recommended_command"])
    def test_describe_provider_work_items_recommends_await_provider_result_after_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            self._write_generated_plan_manifest(output)
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0]["object_type"] = "ui-carrier"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            self._write_generation_brief(output)
            request_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "prepare_provider_request.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(request_result.returncode, 0, request_result.stderr)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "describe_provider_work_items.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            entry = json.loads(result.stdout)["objects"][0]
            self.assertEqual(entry["next_action"], "await-provider-result")
            self.assertTrue(entry["request_ready"])
            self.assertFalse(entry["result_ready"])
            self.assertIn("record_provider_result.py", entry["recommended_command"])
    def test_describe_provider_work_items_recommends_consume_provider_result_when_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            plan_manifest = {
                "schema_version": "1.0",
                "package_name": "fixture",
                "source": {"path": "source/source_original.png", "width": 4, "height": 3},
                "quality_target": {"tier": "visual-acceptance-ready", "notes": ""},
                "planning_status": {"status": "completed", "notes": ""},
                "route_policy": {"planning_required": True, "generation_routing_gate": "confirmed"},
                "provider_preferences": {
                    "generation_provider_class": "unset",
                    "segmentation_provider_class": "unset",
                },
                "objects": [
                    {
                        "object_id": "main_object",
                        "object_type": "ui-carrier",
                        "planned_route": "extract",
                    }
                ],
                "summary": {},
            }
            (output / "plan_manifest.json").write_text(
                json.dumps(plan_manifest, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            self._write_single_object_metadata(output)
            self._set_candidate_promotion_confirmation(output)
            request_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "prepare_provider_request.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(request_result.returncode, 0, request_result.stderr)
            provider_dir = output / "_staging" / "providers" / "grounded-sam-bridge" / "main_object"
            provider_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (2, 2), (255, 0, 0, 255)).save(provider_dir / "main_object.png")
            Image.new("L", (4, 3), 255).save(provider_dir / "main_object_mask.png")
            record_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_provider_result.py"),
                    str(output),
                    "--provider-id",
                    "grounded-sam-bridge",
                    "--object-id",
                    "main_object",
                    "--status",
                    "success",
                    "--artifact",
                    "asset_png=_staging/providers/grounded-sam-bridge/main_object/main_object.png",
                    "--artifact",
                    "source_space_mask=_staging/providers/grounded-sam-bridge/main_object/main_object_mask.png",
                    "--tool-name",
                    "Grounded-SAM",
                    "--tool-role",
                    "segmentation",
                    "--tool-version",
                    "external",
                    "--execution-mode",
                    "bridge",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(record_result.returncode, 0, record_result.stderr)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "describe_provider_work_items.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            entry = json.loads(result.stdout)["objects"][0]
            self.assertEqual(entry["next_action"], "consume-provider-result")
            self.assertEqual(entry["inferred_consume_mode"], "import-extract")
            self.assertIn("consume_provider_result.py", entry["recommended_command"])
    def test_describe_provider_work_items_reports_no_provider_run_required_for_rebuild_downstream(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            plan_manifest = {
                "schema_version": "1.0",
                "package_name": "fixture",
                "source": {"path": "source/source_original.png", "width": 4, "height": 3},
                "quality_target": {"tier": "visual-acceptance-ready", "notes": ""},
                "planning_status": {"status": "completed", "notes": ""},
                "route_policy": {"planning_required": True, "generation_routing_gate": "confirmed"},
                "provider_preferences": {
                    "generation_provider_class": "unset",
                    "segmentation_provider_class": "unset",
                },
                "objects": [
                    {
                        "object_id": "live_text",
                        "object_type": "generic-object",
                        "planned_route": "rebuild_downstream",
                    }
                ],
                "summary": {},
            }
            (output / "plan_manifest.json").write_text(
                json.dumps(plan_manifest, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            self._write_single_object_metadata(output)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "describe_provider_work_items.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            entry = json.loads(result.stdout)["objects"][0]
            self.assertEqual(entry["next_action"], "no-provider-run-required")
            self.assertEqual(entry["selected_provider_id"], "")
            self.assertEqual(entry["recommended_command"], "")
    def test_describe_candidate_work_items_reports_candidate_stage_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            self._write_generated_plan_manifest(output)
            self._write_single_object_metadata(output)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "describe_candidate_work_items.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["candidate_work_items_path"], "_staging/repair_candidates/candidate_work_items.json")
            self.assertEqual(payload["objects"][0]["next_action"], "candidate-stage-empty")
    def test_describe_candidate_work_items_recommends_compare_for_multiple_candidates_without_comparison(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            self._write_generated_plan_manifest(output)
            self._write_single_object_metadata(output)
            candidate_dir = output / "_staging" / "repair_candidates" / "main_object"
            candidate_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (4, 3), (255, 0, 0, 255)).save(candidate_dir / "candidate-a.png")
            Image.new("RGBA", (4, 3), (0, 255, 0, 255)).save(candidate_dir / "candidate-b.png")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "describe_candidate_work_items.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            entry = json.loads(result.stdout)["objects"][0]
            self.assertEqual(entry["next_action"], "compare-candidates")
            self.assertIn("compare_candidate_assets.py", entry["recommended_command"])
    def test_describe_candidate_work_items_recommends_promote_single_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            self._write_generated_plan_manifest(output)
            self._write_single_object_metadata(output)
            candidate_dir = output / "_staging" / "repair_candidates" / "main_object"
            candidate_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (4, 3), (255, 0, 0, 255)).save(candidate_dir / "candidate-a.png")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "describe_candidate_work_items.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            entry = json.loads(result.stdout)["objects"][0]
            self.assertEqual(entry["next_action"], "record-candidate-promotion-approval")
            self.assertEqual(entry["recommended_delivery_class"], "generated-reconstruction")
            self.assertIn("apply_candidate_promotion_decision.py", entry["recommended_command"])
    def test_describe_candidate_work_items_recommends_promote_single_candidate_after_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            self._write_generated_plan_manifest(output)
            metadata = self._write_single_object_metadata(output)
            metadata["confirmation"]["candidate_promotion"]["status"] = "confirmed"
            metadata["confirmation"]["candidate_promotion"]["source"] = "explicit-user-confirmed"
            metadata["confirmation"]["candidate_promotion"]["evidence_ref"] = "chat:promotion-approved"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            candidate_dir = output / "_staging" / "repair_candidates" / "main_object"
            candidate_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (4, 3), (255, 0, 0, 255)).save(candidate_dir / "candidate-a.png")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "describe_candidate_work_items.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            entry = json.loads(result.stdout)["objects"][0]
            self.assertEqual(entry["next_action"], "promote-single-candidate")
            self.assertIn("promote_candidate_asset.py", entry["recommended_command"])
    def test_describe_candidate_work_items_recommends_promote_selected_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            self._write_generated_plan_manifest(output)
            metadata = self._write_single_object_metadata(output)
            candidate_dir = output / "_staging" / "repair_candidates" / "main_object"
            candidate_dir.mkdir(parents=True, exist_ok=True)
            candidate_path = candidate_dir / "candidate-a.png"
            Image.new("RGBA", (4, 3), (255, 0, 0, 255)).save(candidate_path)
            compare_manifest_path = output / "_staging" / "repair_candidates" / "cmp-1_compare.json"
            compare_manifest_path.write_text(
                json.dumps(
                    {
                        "comparison_id": "cmp-1",
                        "object_id": "main_object",
                        "candidate_ids": ["candidate-a"],
                        "candidates": [
                            {
                                "candidate_id": "candidate-a",
                                "asset_path": "_staging/repair_candidates/main_object/candidate-a.png",
                            }
                        ],
                    },
                    indent=2,
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            metadata["objects"][0]["candidate_comparisons"] = [
                {
                    "comparison_id": "cmp-1",
                    "object_id": "main_object",
                    "candidate_ids": ["candidate-a"],
                    "compare_artifact_path": "",
                    "compare_manifest_path": "_staging/repair_candidates/cmp-1_compare.json",
                    "compare_note": "",
                    "compare_criteria": ["shape fidelity"],
                    "review_focus": [],
                    "risks": [],
                    "score_manifest_path": "",
                    "selected_candidate_id": "candidate-a",
                    "selection_reason": "Best candidate after comparison.",
                    "created_at": "2026-07-04T00:00:00Z",
                }
            ]
            metadata["confirmation"]["candidate_promotion"]["status"] = "confirmed"
            metadata["confirmation"]["candidate_promotion"]["source"] = "explicit-user-confirmed"
            metadata["confirmation"]["candidate_promotion"]["evidence_ref"] = "chat:promotion-approved"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "describe_candidate_work_items.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            entry = json.loads(result.stdout)["objects"][0]
            self.assertEqual(entry["next_action"], "promote-selected-candidate")
            self.assertEqual(entry["comparison_selected_candidate_id"], "candidate-a")
            self.assertIn("--comparison-id cmp-1", entry["recommended_command"])
            self.assertNotIn("--candidate-id", entry["recommended_command"])
            self.assertNotIn("--selection-reason", entry["recommended_command"])
            self.assertEqual(entry["candidate_promotion_status"], "confirmed")
    def test_describe_candidate_work_items_requests_promotion_approval_for_selected_candidate_when_pending(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            self._write_generated_plan_manifest(output)
            metadata = self._write_single_object_metadata(output)
            candidate_dir = output / "_staging" / "repair_candidates" / "main_object"
            candidate_dir.mkdir(parents=True, exist_ok=True)
            candidate_path = candidate_dir / "candidate-a.png"
            Image.new("RGBA", (4, 3), (255, 0, 0, 255)).save(candidate_path)
            compare_manifest_path = output / "_staging" / "repair_candidates" / "cmp-1_compare.json"
            compare_manifest_path.write_text(
                json.dumps(
                    {
                        "comparison_id": "cmp-1",
                        "object_id": "main_object",
                        "candidate_ids": ["candidate-a"],
                        "candidates": [
                            {
                                "candidate_id": "candidate-a",
                                "asset_path": "_staging/repair_candidates/main_object/candidate-a.png",
                            }
                        ],
                    },
                    indent=2,
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            metadata["objects"][0]["candidate_comparisons"] = [
                {
                    "comparison_id": "cmp-1",
                    "object_id": "main_object",
                    "candidate_ids": ["candidate-a"],
                    "compare_artifact_path": "",
                    "compare_manifest_path": "_staging/repair_candidates/cmp-1_compare.json",
                    "compare_note": "",
                    "compare_criteria": ["shape fidelity"],
                    "review_focus": [],
                    "risks": [],
                    "score_manifest_path": "",
                    "selected_candidate_id": "candidate-a",
                    "selection_reason": "Best candidate after comparison.",
                    "created_at": "2026-07-04T00:00:00Z",
                }
            ]
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "describe_candidate_work_items.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            entry = json.loads(result.stdout)["objects"][0]
            self.assertEqual(entry["next_action"], "record-candidate-promotion-approval")
            self.assertEqual(entry["candidate_promotion_status"], "pending")
            self.assertIn("apply_candidate_promotion_decision.py", entry["recommended_command"])
            self.assertIn("--comparison-id cmp-1", entry["recommended_command"])
            self.assertIn("--delivery-class generated-reconstruction", entry["recommended_command"])
    def test_record_candidate_promotion_approval_records_confirmed_gate_from_selected_comparison(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0]["candidate_comparisons"] = [
                {
                    "comparison_id": "cmp-1",
                    "object_id": "main_object",
                    "candidate_ids": ["candidate-a"],
                    "compare_artifact_path": "_staging/repair_candidates/cmp-1_compare.png",
                    "compare_manifest_path": "_staging/repair_candidates/cmp-1_compare.json",
                    "compare_note": "",
                    "compare_criteria": ["shape fidelity"],
                    "review_focus": [],
                    "risks": [],
                    "score_manifest_path": "",
                    "selected_candidate_id": "candidate-a",
                    "selection_reason": "Best candidate after comparison.",
                    "created_at": "2026-07-04T00:00:00Z",
                }
            ]
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_candidate_promotion_approval.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--comparison-id",
                    "cmp-1",
                    "--decision-answer",
                    "yes",
                    "--evidence-ref",
                    "chat:promotion-approved",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["candidate_id"], "candidate-a")
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["confirmation"]["candidate_promotion"]["status"], "confirmed")
            self.assertEqual(metadata["decision_log"][-1]["stage"], "final-promotion-acceptance")
    def test_record_candidate_promotion_approval_fills_single_candidate_selection(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0]["candidate_comparisons"] = [
                {
                    "comparison_id": "cmp-1",
                    "object_id": "main_object",
                    "candidate_ids": ["candidate-a"],
                    "compare_artifact_path": "_staging/repair_candidates/cmp-1_compare.png",
                    "compare_manifest_path": "_staging/repair_candidates/cmp-1_compare.json",
                    "compare_note": "",
                    "compare_criteria": ["shape fidelity"],
                    "review_focus": [],
                    "risks": [],
                    "score_manifest_path": "",
                    "selected_candidate_id": "",
                    "selection_reason": "",
                    "created_at": "2026-07-04T00:00:00Z",
                }
            ]
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_candidate_promotion_approval.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--comparison-id",
                    "cmp-1",
                    "--decision-answer",
                    "yes",
                    "--selection-reason",
                    "Only viable candidate in the compare set.",
                    "--evidence-ref",
                    "chat:promotion-approved",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            comparison = metadata["objects"][0]["candidate_comparisons"][0]
            self.assertEqual(comparison["selected_candidate_id"], "candidate-a")
            self.assertEqual(comparison["selection_reason"], "Only viable candidate in the compare set.")
    def test_record_candidate_promotion_approval_rejects_multi_candidate_compare_without_selected_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0]["candidate_comparisons"] = [
                {
                    "comparison_id": "cmp-1",
                    "object_id": "main_object",
                    "candidate_ids": ["candidate-a", "candidate-b"],
                    "compare_artifact_path": "_staging/repair_candidates/cmp-1_compare.png",
                    "compare_manifest_path": "_staging/repair_candidates/cmp-1_compare.json",
                    "compare_note": "",
                    "compare_criteria": ["shape fidelity"],
                    "review_focus": [],
                    "risks": [],
                    "score_manifest_path": "",
                    "selected_candidate_id": "",
                    "selection_reason": "",
                    "created_at": "2026-07-04T00:00:00Z",
                }
            ]
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_candidate_promotion_approval.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--comparison-id",
                    "cmp-1",
                    "--decision-answer",
                    "yes",
                    "--selection-reason",
                    "Need a real winner first.",
                    "--evidence-ref",
                    "chat:promotion-approved",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("selected_candidate_id or exactly one candidate", result.stderr)
    def test_apply_candidate_promotion_decision_records_approval_and_promotes(self):
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
            compare_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "compare_candidate_assets.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate",
                    "candidate-a=_staging/repair_candidates/candidate_a.png",
                    "--compare-note",
                    "Single-candidate compare for direct promotion.",
                    "--compare-criterion",
                    "single viable candidate",
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
                    str(ROOT / "scripts" / "apply_candidate_promotion_decision.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--comparison-id",
                    comparison_id,
                    "--decision-answer",
                    "yes",
                    "--selection-reason",
                    "Only viable candidate in the compare set.",
                    "--evidence-ref",
                    "chat:promotion-approved",
                    "--delivery-class",
                    "clean-extraction",
                    "--repair-note",
                    "Promote the selected compare candidate.",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["decision_answer"], "yes")
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["confirmation"]["candidate_promotion"]["status"], "confirmed")
            self.assertEqual(metadata["objects"][0]["selected_candidate_id"], "candidate-a")
    def test_apply_candidate_promotion_decision_records_decline_without_promoting(self):
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
            compare_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "compare_candidate_assets.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate",
                    "candidate-a=_staging/repair_candidates/candidate_a.png",
                    "--compare-note",
                    "Single-candidate compare for direct promotion.",
                    "--compare-criterion",
                    "single viable candidate",
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
                    str(ROOT / "scripts" / "apply_candidate_promotion_decision.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--comparison-id",
                    comparison_id,
                    "--decision-answer",
                    "no",
                    "--evidence-ref",
                    "chat:promotion-declined",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["confirmation"]["candidate_promotion"]["status"], "pending")
            self.assertEqual(metadata["objects"][0]["selected_candidate_id"], "")
    def test_apply_candidate_promotion_decision_rejects_yes_without_delivery_class(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0]["candidate_comparisons"] = [
                {
                    "comparison_id": "cmp-1",
                    "object_id": "main_object",
                    "candidate_ids": ["candidate-a"],
                    "compare_artifact_path": "_staging/repair_candidates/cmp-1_compare.png",
                    "compare_manifest_path": "_staging/repair_candidates/cmp-1_compare.json",
                    "compare_note": "",
                    "compare_criteria": ["shape fidelity"],
                    "review_focus": [],
                    "risks": [],
                    "score_manifest_path": "",
                    "selected_candidate_id": "candidate-a",
                    "selection_reason": "Best candidate after comparison.",
                    "created_at": "2026-07-04T00:00:00Z",
                }
            ]
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "apply_candidate_promotion_decision.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--comparison-id",
                    "cmp-1",
                    "--decision-answer",
                    "yes",
                    "--evidence-ref",
                    "chat:promotion-approved",
                    "--repair-note",
                    "Promote the selected compare candidate.",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--delivery-class is required when --decision-answer is yes", result.stderr)
    def test_describe_candidate_work_items_awaits_candidate_selection_after_compare(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            self._write_generated_plan_manifest(output)
            metadata = self._write_single_object_metadata(output)
            candidate_dir = output / "_staging" / "repair_candidates" / "main_object"
            candidate_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (4, 3), (255, 0, 0, 255)).save(candidate_dir / "candidate-a.png")
            Image.new("RGBA", (4, 3), (0, 255, 0, 255)).save(candidate_dir / "candidate-b.png")
            metadata["objects"][0]["candidate_comparisons"] = [
                {
                    "comparison_id": "cmp-1",
                    "object_id": "main_object",
                    "candidate_ids": ["candidate-a", "candidate-b"],
                    "compare_artifact_path": "_staging/repair_candidates/cmp-1_compare.png",
                    "compare_manifest_path": "_staging/repair_candidates/cmp-1_compare.json",
                    "compare_note": "",
                    "compare_criteria": ["shape fidelity"],
                    "review_focus": [],
                    "risks": [],
                    "score_manifest_path": "",
                    "selected_candidate_id": "",
                    "selection_reason": "",
                    "created_at": "2026-07-04T00:00:00Z",
                }
            ]
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "describe_candidate_work_items.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            entry = json.loads(result.stdout)["objects"][0]
            self.assertEqual(entry["next_action"], "await-candidate-selection")
    def test_describe_candidate_work_items_reports_no_work_after_promotion(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            self._write_generated_plan_manifest(output)
            metadata = self._write_single_object_metadata(output)
            metadata["objects"][0]["selected_candidate_id"] = "candidate-a"
            metadata["objects"][0]["current_asset_revision"] = "candidate-a"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "describe_candidate_work_items.py"),
                    str(output),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            entry = json.loads(result.stdout)["objects"][0]
            self.assertEqual(entry["next_action"], "no-candidate-work-required")
    def test_record_provider_result_writes_bridge_result_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            provider_dir = output / "_staging" / "providers" / "grounded-sam-bridge" / "main_object"
            provider_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (2, 2), (255, 0, 0, 255)).save(provider_dir / "main_object.png")
            Image.new("L", (4, 3), 255).save(provider_dir / "main_object_mask.png")
            metadata_before = json.loads((output / "metadata.json").read_text(encoding="utf-8"))

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_provider_result.py"),
                    str(output),
                    "--provider-id",
                    "grounded-sam-bridge",
                    "--object-id",
                    "main_object",
                    "--status",
                    "success",
                    "--artifact",
                    "asset_png=_staging/providers/grounded-sam-bridge/main_object/main_object.png",
                    "--artifact",
                    "source_space_mask=_staging/providers/grounded-sam-bridge/main_object/main_object_mask.png",
                    "--tool-name",
                    "Grounded-SAM",
                    "--tool-role",
                    "segmentation",
                    "--tool-version",
                    "external",
                    "--execution-mode",
                    "bridge",
                    "--next-expected-provider",
                    "rembg-bridge",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            result_path = output / "_staging" / "providers" / "grounded-sam-bridge" / "main_object" / "result.json"
            self.assertTrue(result_path.exists())
            provider_result = json.loads(result_path.read_text(encoding="utf-8"))
            self.assertEqual(provider_result["status"], "success")
            self.assertEqual(provider_result["provenance"]["tool_name"], "Grounded-SAM")
            metadata_after = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata_after, metadata_before)
    def test_consume_provider_result_imports_extract_asset(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            provider_dir = output / "_staging" / "providers" / "grounded-sam-bridge" / "main_object"
            provider_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (2, 2), (255, 0, 0, 255)).save(provider_dir / "main_object.png")
            Image.new("L", (4, 3), 255).save(provider_dir / "main_object_mask.png")
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_provider_result.py"),
                    str(output),
                    "--provider-id",
                    "grounded-sam-bridge",
                    "--object-id",
                    "main_object",
                    "--status",
                    "success",
                    "--artifact",
                    "asset_png=_staging/providers/grounded-sam-bridge/main_object/main_object.png",
                    "--artifact",
                    "source_space_mask=_staging/providers/grounded-sam-bridge/main_object/main_object_mask.png",
                    "--tool-name",
                    "Grounded-SAM",
                    "--tool-role",
                    "segmentation",
                    "--tool-version",
                    "external",
                    "--execution-mode",
                    "bridge",
                ],
                text=True,
                capture_output=True,
                check=True,
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "consume_provider_result.py"),
                    str(output),
                    "--provider-id",
                    "grounded-sam-bridge",
                    "--object-id",
                    "main_object",
                    "--mode",
                    "import-extract",
                    "--role",
                    "main",
                    "--layer-kind",
                    "primary-subject",
                    "--composition-order",
                    "10",
                    "--semantic-boundary",
                    "Imported from provider bridge result.",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["objects"][0]["mask_source"], "grounded-sam-bridge")
            self.assertEqual(metadata["extraction_pipeline"]["tools"][0]["name"], "Grounded-SAM")
    def test_consume_provider_result_infers_single_provider_and_extract_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            self._write_single_object_metadata(output)
            provider_dir = output / "_staging" / "providers" / "grounded-sam-bridge" / "main_object"
            provider_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (2, 2), (255, 0, 0, 255)).save(provider_dir / "main_object.png")
            Image.new("L", (4, 3), 255).save(provider_dir / "main_object_mask.png")
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_provider_result.py"),
                    str(output),
                    "--provider-id",
                    "grounded-sam-bridge",
                    "--object-id",
                    "main_object",
                    "--status",
                    "success",
                    "--artifact",
                    "asset_png=_staging/providers/grounded-sam-bridge/main_object/main_object.png",
                    "--artifact",
                    "source_space_mask=_staging/providers/grounded-sam-bridge/main_object/main_object_mask.png",
                    "--tool-name",
                    "Grounded-SAM",
                    "--tool-role",
                    "segmentation",
                    "--tool-version",
                    "external",
                    "--execution-mode",
                    "bridge",
                ],
                text=True,
                capture_output=True,
                check=True,
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "consume_provider_result.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["objects"][0]["mask_source"], "grounded-sam-bridge")
            self.assertEqual(metadata["objects"][0]["role"], "main")
            self.assertEqual(metadata["objects"][0]["composition_order"], 10)
            self.assertEqual(metadata["objects"][0]["object_type"], "generic-object")
    def test_consume_provider_result_stages_generated_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            self._write_generated_plan_manifest(output)
            self._write_generation_brief(output)
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "prepare_provider_request.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            provider_dir = output / "_staging" / "providers" / "codex-controlled-generation" / "main_object"
            provider_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (2, 2), (255, 0, 0, 255)).save(provider_dir / "candidate.png")
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_provider_result.py"),
                    str(output),
                    "--provider-id",
                    "codex-controlled-generation",
                    "--object-id",
                    "main_object",
                    "--status",
                    "success",
                    "--artifact",
                    "candidate_png=_staging/providers/codex-controlled-generation/main_object/candidate.png",
                    "--tool-name",
                    "gpt-image-1",
                    "--tool-role",
                    "generation",
                    "--tool-version",
                    "host-managed",
                    "--execution-mode",
                    "host-managed",
                ],
                text=True,
                capture_output=True,
                check=True,
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "consume_provider_result.py"),
                    str(output),
                    "--provider-id",
                    "codex-controlled-generation",
                    "--object-id",
                    "main_object",
                    "--mode",
                    "stage-candidate",
                    "--candidate-id",
                    "generated-v1",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(
                (
                    output
                    / "_staging"
                    / "repair_candidates"
                    / "main_object"
                    / "generated-v1.png"
                ).exists()
            )
            provider_stage = json.loads(
                (
                    output
                    / "_staging"
                    / "repair_candidates"
                    / "main_object"
                    / "generated-v1_provider_stage.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(provider_stage["generation_source"], "codex-controlled-generation")
            self.assertEqual(provider_stage["generation_model_or_tool"], "gpt-image-1")
            self.assertEqual(provider_stage["generation_version"], "host-managed")
            self.assertEqual(
                provider_stage["generation_prompt_or_brief_ref"],
                "_staging/generation_briefs/main_object.json",
            )
            self.assertEqual(provider_stage["generation_reference_inputs"], ["source/source_original.png"])
    def test_consume_provider_result_uses_provider_manifest_when_manifest_flag_is_omitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (6, 6), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            provider_dir = output / "_staging" / "providers" / "external-professional-outputs" / "main_object"
            provider_dir.mkdir(parents=True, exist_ok=True)
            asset = tmp_path / "tile.png"
            mask = tmp_path / "tile_mask.png"
            Image.new("RGBA", (2, 2), (80, 100, 120, 255)).save(asset)
            Image.new("L", (6, 6), 255).save(mask)
            manifest_path = provider_dir / "provider_manifest.json"
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
                                "object_id": "main_object",
                                "role": "main",
                                "layer_kind": "primary-subject",
                                "composition_order": 10,
                                "semantic_boundary": "Imported via provider manifest bridge.",
                                "asset": str(asset),
                                "mask": str(mask),
                                "mask_source": "sam2",
                                "alpha_source": "rembg-refine",
                            }
                        ],
                    },
                    indent=2,
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_provider_result.py"),
                    str(output),
                    "--provider-id",
                    "external-professional-outputs",
                    "--object-id",
                    "main_object",
                    "--status",
                    "success",
                    "--artifact",
                    "provider_manifest=_staging/providers/external-professional-outputs/main_object/provider_manifest.json",
                    "--tool-name",
                    "SAM2",
                    "--tool-role",
                    "segmentation",
                    "--tool-version",
                    "external",
                    "--execution-mode",
                    "external-manifest",
                ],
                text=True,
                capture_output=True,
                check=True,
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "consume_provider_result.py"),
                    str(output),
                    "--provider-id",
                    "external-professional-outputs",
                    "--object-id",
                    "main_object",
                    "--mode",
                    "import-manifest",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["objects"][0]["id"], "main_object")
            self.assertEqual(metadata["extraction_pipeline"]["tools"][0]["name"], "SAM2")
    def test_consume_provider_result_infers_single_provider_and_manifest_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (6, 6), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)

            provider_dir = output / "_staging" / "providers" / "external-professional-outputs" / "main_object"
            provider_dir.mkdir(parents=True, exist_ok=True)
            asset = tmp_path / "tile.png"
            mask = tmp_path / "tile_mask.png"
            Image.new("RGBA", (2, 2), (80, 100, 120, 255)).save(asset)
            Image.new("L", (6, 6), 255).save(mask)
            manifest_path = provider_dir / "provider_manifest.json"
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
                                "object_id": "main_object",
                                "role": "main",
                                "layer_kind": "primary-subject",
                                "composition_order": 10,
                                "semantic_boundary": "Imported via inferred provider manifest bridge.",
                                "asset": str(asset),
                                "mask": str(mask),
                                "mask_source": "sam2",
                                "alpha_source": "rembg-refine",
                            }
                        ],
                    },
                    indent=2,
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_provider_result.py"),
                    str(output),
                    "--provider-id",
                    "external-professional-outputs",
                    "--object-id",
                    "main_object",
                    "--status",
                    "success",
                    "--artifact",
                    "provider_manifest=_staging/providers/external-professional-outputs/main_object/provider_manifest.json",
                    "--tool-name",
                    "SAM2",
                    "--tool-role",
                    "segmentation",
                    "--tool-version",
                    "external",
                    "--execution-mode",
                    "external-manifest",
                ],
                text=True,
                capture_output=True,
                check=True,
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "consume_provider_result.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["objects"][0]["id"], "main_object")
            self.assertEqual(metadata["extraction_pipeline"]["tools"][0]["name"], "SAM2")
    def test_consume_provider_result_rejects_ambiguous_staged_provider_results_without_provider_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (6, 6), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            self._write_generated_plan_manifest(output)
            self._write_single_object_metadata(output)

            bridge_dir = output / "_staging" / "providers" / "grounded-sam-bridge" / "main_object"
            bridge_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (2, 2), (255, 0, 0, 255)).save(bridge_dir / "main_object.png")
            Image.new("L", (6, 6), 255).save(bridge_dir / "main_object_mask.png")
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_provider_result.py"),
                    str(output),
                    "--provider-id",
                    "grounded-sam-bridge",
                    "--object-id",
                    "main_object",
                    "--status",
                    "success",
                    "--artifact",
                    "asset_png=_staging/providers/grounded-sam-bridge/main_object/main_object.png",
                    "--artifact",
                    "source_space_mask=_staging/providers/grounded-sam-bridge/main_object/main_object_mask.png",
                    "--tool-name",
                    "Grounded-SAM",
                    "--tool-role",
                    "segmentation",
                    "--tool-version",
                    "external",
                    "--execution-mode",
                    "bridge",
                ],
                text=True,
                capture_output=True,
                check=True,
            )

            external_dir = output / "_staging" / "providers" / "external-professional-outputs" / "main_object"
            external_dir.mkdir(parents=True, exist_ok=True)
            manifest_path = external_dir / "provider_manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "recipe": "grounded-segmentation-matting-repair",
                        "tool": {
                            "name": "SAM2",
                            "role": "segmentation",
                            "version": "external",
                        },
                        "objects": [],
                    },
                    indent=2,
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_provider_result.py"),
                    str(output),
                    "--provider-id",
                    "external-professional-outputs",
                    "--object-id",
                    "main_object",
                    "--status",
                    "success",
                    "--artifact",
                    "provider_manifest=_staging/providers/external-professional-outputs/main_object/provider_manifest.json",
                    "--tool-name",
                    "SAM2",
                    "--tool-role",
                    "segmentation",
                    "--tool-version",
                    "external",
                    "--execution-mode",
                    "external-manifest",
                ],
                text=True,
                capture_output=True,
                check=True,
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "consume_provider_result.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("multiple staged provider results exist for main_object", result.stderr)
    def test_consume_provider_result_prefers_plan_selected_provider_when_multiple_results_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (6, 6), (10, 20, 30, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            plan_manifest = self._write_generated_plan_manifest(output)
            plan_manifest["provider_preferences"]["generation_provider_class"] = "external-generated-outputs"
            (output / "plan_manifest.json").write_text(
                json.dumps(plan_manifest, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            self._write_single_object_metadata(output)
            self._write_generation_brief(output)
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "prepare_provider_request.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                ],
                text=True,
                capture_output=True,
                check=True,
            )

            codex_dir = output / "_staging" / "providers" / "codex-controlled-generation" / "main_object"
            codex_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (2, 2), (255, 0, 0, 255)).save(codex_dir / "candidate_a.png")
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_provider_result.py"),
                    str(output),
                    "--provider-id",
                    "codex-controlled-generation",
                    "--object-id",
                    "main_object",
                    "--status",
                    "success",
                    "--artifact",
                    "candidate_png=_staging/providers/codex-controlled-generation/main_object/candidate_a.png",
                    "--tool-name",
                    "Codex Gen",
                    "--tool-role",
                    "generation",
                    "--tool-version",
                    "host",
                    "--execution-mode",
                    "host-managed",
                ],
                text=True,
                capture_output=True,
                check=True,
            )

            external_dir = output / "_staging" / "providers" / "external-generated-outputs" / "main_object"
            external_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (2, 2), (0, 255, 0, 255)).save(external_dir / "candidate_b.png")
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_provider_result.py"),
                    str(output),
                    "--provider-id",
                    "external-generated-outputs",
                    "--object-id",
                    "main_object",
                    "--status",
                    "success",
                    "--artifact",
                    "candidate_png=_staging/providers/external-generated-outputs/main_object/candidate_b.png",
                    "--tool-name",
                    "External Gen",
                    "--tool-role",
                    "generation",
                    "--tool-version",
                    "external",
                    "--execution-mode",
                    "external-manifest",
                ],
                text=True,
                capture_output=True,
                check=True,
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "consume_provider_result.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate-id",
                    "preferred-generated-candidate",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            stage_manifest = json.loads(
                (
                    output
                    / "_staging"
                    / "repair_candidates"
                    / "main_object"
                    / "preferred-generated-candidate_provider_stage.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(stage_manifest["provider_id"], "external-generated-outputs")
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
    def test_compare_candidate_assets_records_provider_stage_evidence_for_generated_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (8, 8), (20, 20, 20, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            self._write_single_object_metadata(output)
            self._write_generated_plan_manifest(output)
            self._write_generation_brief(output)
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "prepare_provider_request.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            provider_dir = output / "_staging" / "providers" / "codex-controlled-generation" / "main_object"
            provider_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (4, 4), (255, 0, 0, 255)).save(provider_dir / "candidate_a.png")
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_provider_result.py"),
                    str(output),
                    "--provider-id",
                    "codex-controlled-generation",
                    "--object-id",
                    "main_object",
                    "--status",
                    "success",
                    "--artifact",
                    "candidate_png=_staging/providers/codex-controlled-generation/main_object/candidate_a.png",
                    "--tool-name",
                    "gpt-image-1",
                    "--tool-role",
                    "generation",
                    "--tool-version",
                    "test-version",
                    "--execution-mode",
                    "host-managed",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "consume_provider_result.py"),
                    str(output),
                    "--provider-id",
                    "codex-controlled-generation",
                    "--object-id",
                    "main_object",
                    "--mode",
                    "stage-candidate",
                    "--candidate-id",
                    "candidate-a",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            shutil.copy2(
                output / "_staging" / "repair_candidates" / "main_object" / "candidate-a.png",
                output / "_staging" / "repair_candidates" / "main_object" / "candidate-b.png",
            )
            shutil.copy2(
                output / "_staging" / "repair_candidates" / "main_object" / "candidate-a_provider_stage.json",
                output / "_staging" / "repair_candidates" / "main_object" / "candidate-b_provider_stage.json",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "compare_candidate_assets.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate",
                    "candidate-a=_staging/repair_candidates/main_object/candidate-a.png",
                    "--candidate",
                    "candidate-b=_staging/repair_candidates/main_object/candidate-b.png",
                    "--compare-note",
                    "Compare generated candidates with provider evidence.",
                    "--compare-criterion",
                    "generated edge fidelity",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            manifest_rel = metadata["objects"][0]["candidate_comparisons"][0]["compare_manifest_path"]
            manifest = json.loads((output / manifest_rel).read_text(encoding="utf-8"))
            candidate_record = manifest["candidates"][0]
            self.assertEqual(
                candidate_record["provider_stage_manifest_path"],
                "_staging/repair_candidates/main_object/candidate-a_provider_stage.json",
            )
            self.assertEqual(candidate_record["generation_source"], "codex-controlled-generation")
            self.assertEqual(candidate_record["generation_model_or_tool"], "gpt-image-1")
            self.assertEqual(candidate_record["generation_version"], "test-version")
    def test_compare_candidate_assets_rejects_generated_candidates_without_provider_stage_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (8, 8), (20, 20, 20, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            self._write_single_object_metadata(output)
            self._write_generated_plan_manifest(output)
            candidate_dir = output / "_staging" / "repair_candidates" / "main_object"
            candidate_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (4, 4), (255, 0, 0, 255)).save(candidate_dir / "candidate-a.png")
            Image.new("RGBA", (4, 4), (0, 255, 0, 255)).save(candidate_dir / "candidate-b.png")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "compare_candidate_assets.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate",
                    "candidate-a=_staging/repair_candidates/main_object/candidate-a.png",
                    "--candidate",
                    "candidate-b=_staging/repair_candidates/main_object/candidate-b.png",
                    "--compare-note",
                    "Reject generated compare without provider evidence.",
                    "--compare-criterion",
                    "generated edge fidelity",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("generated compare candidates require provider stage evidence", result.stderr)
    def test_compare_candidate_assets_auto_discovers_generated_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (8, 8), (20, 20, 20, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            self._write_single_object_metadata(output)
            self._write_generated_plan_manifest(output)
            self._write_generation_brief(output)
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "prepare_provider_request.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            provider_dir = output / "_staging" / "providers" / "codex-controlled-generation" / "main_object"
            provider_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (4, 4), (255, 0, 0, 255)).save(provider_dir / "candidate_a.png")
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_provider_result.py"),
                    str(output),
                    "--provider-id",
                    "codex-controlled-generation",
                    "--object-id",
                    "main_object",
                    "--status",
                    "success",
                    "--artifact",
                    "candidate_png=_staging/providers/codex-controlled-generation/main_object/candidate_a.png",
                    "--tool-name",
                    "gpt-image-1",
                    "--tool-role",
                    "generation",
                    "--tool-version",
                    "test-version",
                    "--execution-mode",
                    "host-managed",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "consume_provider_result.py"),
                    str(output),
                    "--provider-id",
                    "codex-controlled-generation",
                    "--object-id",
                    "main_object",
                    "--mode",
                    "stage-candidate",
                    "--candidate-id",
                    "candidate-a",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            shutil.copy2(
                output / "_staging" / "repair_candidates" / "main_object" / "candidate-a.png",
                output / "_staging" / "repair_candidates" / "main_object" / "candidate-b.png",
            )
            shutil.copy2(
                output / "_staging" / "repair_candidates" / "main_object" / "candidate-a_provider_stage.json",
                output / "_staging" / "repair_candidates" / "main_object" / "candidate-b_provider_stage.json",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "compare_candidate_assets.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--compare-note",
                    "Auto-discover generated candidates.",
                    "--compare-criterion",
                    "generated edge fidelity",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            comparison = metadata["objects"][0]["candidate_comparisons"][0]
            self.assertEqual(comparison["candidate_ids"], ["candidate-a", "candidate-b"])
            compare_manifest = json.loads((output / comparison["compare_manifest_path"]).read_text(encoding="utf-8"))
            self.assertEqual(compare_manifest["review_focus"], ["generated fidelity"])
            self.assertEqual(compare_manifest["risks"], ["prompt drift"])
    def test_compare_candidate_assets_auto_discovery_prefers_plan_selected_provider(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (8, 8), (20, 20, 20, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            plan_manifest = self._write_generated_plan_manifest(output)
            plan_manifest["provider_preferences"]["generation_provider_class"] = "external-generated-outputs"
            (output / "plan_manifest.json").write_text(
                json.dumps(plan_manifest, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            self._write_single_object_metadata(output)
            self._write_generation_brief(output)
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "prepare_provider_request.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--provider-id",
                    "codex-controlled-generation",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "prepare_provider_request.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--provider-id",
                    "external-generated-outputs",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            codex_provider_dir = output / "_staging" / "providers" / "codex-controlled-generation" / "main_object"
            external_provider_dir = output / "_staging" / "providers" / "external-generated-outputs" / "main_object"
            codex_provider_dir.mkdir(parents=True, exist_ok=True)
            external_provider_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (4, 4), (255, 0, 0, 255)).save(codex_provider_dir / "candidate_codex.png")
            Image.new("RGBA", (4, 4), (0, 255, 0, 255)).save(external_provider_dir / "candidate_external.png")
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_provider_result.py"),
                    str(output),
                    "--provider-id",
                    "codex-controlled-generation",
                    "--object-id",
                    "main_object",
                    "--status",
                    "success",
                    "--artifact",
                    "candidate_png=_staging/providers/codex-controlled-generation/main_object/candidate_codex.png",
                    "--tool-name",
                    "gpt-image-1",
                    "--tool-role",
                    "generation",
                    "--tool-version",
                    "codex",
                    "--execution-mode",
                    "host-managed",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "consume_provider_result.py"),
                    str(output),
                    "--provider-id",
                    "codex-controlled-generation",
                    "--object-id",
                    "main_object",
                    "--mode",
                    "stage-candidate",
                    "--candidate-id",
                    "candidate-codex",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_provider_result.py"),
                    str(output),
                    "--provider-id",
                    "external-generated-outputs",
                    "--object-id",
                    "main_object",
                    "--status",
                    "success",
                    "--artifact",
                    "candidate_png=_staging/providers/external-generated-outputs/main_object/candidate_external.png",
                    "--tool-name",
                    "external-gen",
                    "--tool-role",
                    "generation",
                    "--tool-version",
                    "external",
                    "--execution-mode",
                    "external-manifest",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "consume_provider_result.py"),
                    str(output),
                    "--provider-id",
                    "external-generated-outputs",
                    "--object-id",
                    "main_object",
                    "--mode",
                    "stage-candidate",
                    "--candidate-id",
                    "candidate-external",
                ],
                text=True,
                capture_output=True,
                check=True,
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "compare_candidate_assets.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--compare-note",
                    "Auto-discover generated candidates with provider preference.",
                    "--compare-criterion",
                    "generated edge fidelity",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            comparison = metadata["objects"][0]["candidate_comparisons"][0]
            self.assertEqual(comparison["candidate_ids"], ["candidate-external"])
    def test_compare_candidate_assets_auto_discovery_rejects_multi_provider_candidates_without_preference(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (8, 8), (20, 20, 20, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            plan_manifest = self._write_generated_plan_manifest(output)
            plan_manifest["provider_preferences"]["generation_provider_class"] = "unset"
            (output / "plan_manifest.json").write_text(
                json.dumps(plan_manifest, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            self._write_single_object_metadata(output)
            candidate_dir = output / "_staging" / "repair_candidates" / "main_object"
            candidate_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (4, 4), (255, 0, 0, 255)).save(candidate_dir / "candidate-a.png")
            Image.new("RGBA", (4, 4), (0, 255, 0, 255)).save(candidate_dir / "candidate-b.png")
            (candidate_dir / "candidate-a_provider_stage.json").write_text(
                json.dumps({"provider_id": "codex-controlled-generation"}, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            (candidate_dir / "candidate-b_provider_stage.json").write_text(
                json.dumps({"provider_id": "external-generated-outputs"}, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "compare_candidate_assets.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--compare-note",
                    "Reject mixed providers without explicit choice.",
                    "--compare-criterion",
                    "generated edge fidelity",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("multiple generated compare providers discovered", result.stderr)
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
            self.assertEqual(manifest["asset_summary"]["accepted_approximate_reconstructions"], 0)
            self.assertEqual(manifest["asset_summary"]["accepted_generated_reconstructions"], 0)
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
            self._set_candidate_promotion_confirmation(output)
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
    def test_promote_candidate_asset_resolves_candidate_asset_from_compare_manifest(self):
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
            self._set_candidate_promotion_confirmation(output)
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
                    "Compare candidate shapes.",
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

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "promote_candidate_asset.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate-id",
                    "candidate-a",
                    "--comparison-id",
                    comparison_id,
                    "--delivery-class",
                    "clean-extraction",
                    "--repair-note",
                    "Promote using compare manifest candidate path.",
                    "--selection-reason",
                    "Candidate A best matches the expected silhouette.",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["objects"][0]["selected_candidate_id"], "candidate-a")
    def test_promote_candidate_asset_resolves_single_candidate_id_from_compare_manifest(self):
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
            self._set_candidate_promotion_confirmation(output)
            candidate_dir = output / "_staging" / "repair_candidates"
            candidate_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (4, 4), (0, 255, 0, 255)).save(candidate_dir / "candidate_a.png")
            compare_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "compare_candidate_assets.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate",
                    "candidate-a=_staging/repair_candidates/candidate_a.png",
                    "--compare-note",
                    "Single-candidate compare for direct promotion.",
                    "--compare-criterion",
                    "single viable candidate",
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
                    "--comparison-id",
                    comparison_id,
                    "--delivery-class",
                    "clean-extraction",
                    "--repair-note",
                    "Promote single compare candidate.",
                    "--selection-reason",
                    "Only viable candidate in the compare set.",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["objects"][0]["selected_candidate_id"], "candidate-a")
    def test_promote_candidate_asset_uses_selected_candidate_from_comparison_record(self):
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
            self._set_candidate_promotion_confirmation(output)
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
                    "Compare candidate shapes.",
                    "--compare-criterion",
                    "shape fidelity",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(compare_result.returncode, 0, compare_result.stderr)
            metadata_path = output / "metadata.json"
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            metadata["objects"][0]["candidate_comparisons"][0]["selected_candidate_id"] = "candidate-b"
            metadata["objects"][0]["candidate_comparisons"][0]["selection_reason"] = "Candidate B has the cleaner final silhouette."
            metadata_path.write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            comparison_id = metadata["objects"][0]["candidate_comparisons"][0]["comparison_id"]

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "promote_candidate_asset.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--comparison-id",
                    comparison_id,
                    "--delivery-class",
                    "clean-extraction",
                    "--repair-note",
                    "Promote the selected compare candidate.",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            obj = metadata["objects"][0]
            self.assertEqual(obj["selected_candidate_id"], "candidate-b")
            self.assertEqual(obj["candidate_comparisons"][0]["selection_reason"], "Candidate B has the cleaner final silhouette.")
    def test_promote_candidate_asset_rejects_pending_candidate_promotion_confirmation(self):
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
            metadata_path = output / "metadata.json"
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
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

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("candidate_promotion must be confirmed or not-required", result.stderr)
    def test_promote_candidate_asset_allows_confirmed_candidate_promotion_confirmation(self):
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
            metadata["confirmation"]["candidate_promotion"]["status"] = "confirmed"
            metadata["confirmation"]["candidate_promotion"]["source"] = "explicit-user-confirmed"
            metadata["confirmation"]["candidate_promotion"]["evidence_ref"] = "chat:promotion-approved"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            candidate_dir = output / "_staging" / "repair_candidates"
            candidate_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (4, 4), (0, 255, 0, 255)).save(candidate_dir / "candidate_a.png")
            compare_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "compare_candidate_assets.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate",
                    "candidate-a=_staging/repair_candidates/candidate_a.png",
                    "--compare-note",
                    "Single-candidate compare for direct promotion.",
                    "--compare-criterion",
                    "single viable candidate",
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
                    "--comparison-id",
                    comparison_id,
                    "--delivery-class",
                    "clean-extraction",
                    "--repair-note",
                    "Promote single compare candidate.",
                    "--selection-reason",
                    "Only viable candidate in the compare set.",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
    def test_promote_candidate_asset_allows_not_required_candidate_promotion_confirmation(self):
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
            metadata["confirmation"]["candidate_promotion"]["status"] = "not-required"
            metadata["confirmation"]["candidate_promotion"]["source"] = "explicit-user-confirmed"
            metadata["confirmation"]["candidate_promotion"]["evidence_ref"] = "chat:promotion-not-required"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            candidate_dir = output / "_staging" / "repair_candidates"
            candidate_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (4, 4), (0, 255, 0, 255)).save(candidate_dir / "candidate_a.png")
            compare_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "compare_candidate_assets.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate",
                    "candidate-a=_staging/repair_candidates/candidate_a.png",
                    "--compare-note",
                    "Single-candidate compare for direct promotion.",
                    "--compare-criterion",
                    "single viable candidate",
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
                    "--comparison-id",
                    comparison_id,
                    "--delivery-class",
                    "clean-extraction",
                    "--repair-note",
                    "Promote single compare candidate without extra approval.",
                    "--selection-reason",
                    "Only viable candidate in the compare set.",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
    def test_promote_candidate_asset_uses_selection_reason_from_comparison_record(self):
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
            self._set_candidate_promotion_confirmation(output)
            candidate_dir = output / "_staging" / "repair_candidates"
            candidate_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (4, 4), (0, 255, 0, 255)).save(candidate_dir / "candidate_a.png")
            compare_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "compare_candidate_assets.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate",
                    "candidate-a=_staging/repair_candidates/candidate_a.png",
                    "--compare-note",
                    "Single-candidate compare for direct promotion.",
                    "--compare-criterion",
                    "single viable candidate",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(compare_result.returncode, 0, compare_result.stderr)
            metadata_path = output / "metadata.json"
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            metadata["objects"][0]["candidate_comparisons"][0]["selected_candidate_id"] = "candidate-a"
            metadata["objects"][0]["candidate_comparisons"][0]["selection_reason"] = "Only viable candidate in the compare set."
            metadata_path.write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            comparison_id = metadata["objects"][0]["candidate_comparisons"][0]["comparison_id"]

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "promote_candidate_asset.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--comparison-id",
                    comparison_id,
                    "--delivery-class",
                    "clean-extraction",
                    "--repair-note",
                    "Promote single compare candidate.",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            qa_report = (output / "qa_report.md").read_text(encoding="utf-8")
            self.assertIn("Selection reason: Only viable candidate in the compare set.", qa_report)
    def test_promote_candidate_asset_requires_selected_candidate_when_comparison_has_multiple_candidates(self):
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
            self._set_candidate_promotion_confirmation(output)
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
                    "Compare candidate shapes.",
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

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "promote_candidate_asset.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--comparison-id",
                    comparison_id,
                    "--delivery-class",
                    "clean-extraction",
                    "--repair-note",
                    "Reject implicit multi-candidate promotion.",
                    "--selection-reason",
                    "A choice is required first.",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--candidate-id is required when --comparison-id references multiple candidates", result.stderr)
    def test_promote_candidate_asset_requires_selection_reason_when_comparison_record_has_none(self):
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
            self._set_candidate_promotion_confirmation(output)
            candidate_dir = output / "_staging" / "repair_candidates"
            candidate_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (4, 4), (0, 255, 0, 255)).save(candidate_dir / "candidate_a.png")
            compare_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "compare_candidate_assets.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate",
                    "candidate-a=_staging/repair_candidates/candidate_a.png",
                    "--compare-note",
                    "Single-candidate compare for direct promotion.",
                    "--compare-criterion",
                    "single viable candidate",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(compare_result.returncode, 0, compare_result.stderr)
            metadata_path = output / "metadata.json"
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            metadata["objects"][0]["candidate_comparisons"][0]["selected_candidate_id"] = "candidate-a"
            metadata_path.write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            comparison_id = metadata["objects"][0]["candidate_comparisons"][0]["comparison_id"]

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "promote_candidate_asset.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--comparison-id",
                    comparison_id,
                    "--delivery-class",
                    "clean-extraction",
                    "--repair-note",
                    "Reject promotion without rationale.",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--selection-reason is required unless --comparison-id references a comparison with selection_reason", result.stderr)
    def test_promote_candidate_asset_generated_reconstruction_uses_provider_stage_evidence(self):
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
            self._set_candidate_promotion_confirmation(output)
            self._write_generated_plan_manifest(output)
            self._write_generation_brief(output)
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "prepare_provider_request.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            provider_dir = output / "_staging" / "providers" / "codex-controlled-generation" / "main_object"
            provider_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (4, 4), (0, 255, 0, 255)).save(provider_dir / "candidate.png")
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_provider_result.py"),
                    str(output),
                    "--provider-id",
                    "codex-controlled-generation",
                    "--object-id",
                    "main_object",
                    "--status",
                    "success",
                    "--artifact",
                    "candidate_png=_staging/providers/codex-controlled-generation/main_object/candidate.png",
                    "--tool-name",
                    "gpt-image-1",
                    "--tool-role",
                    "generation",
                    "--tool-version",
                    "test-version",
                    "--execution-mode",
                    "host-managed",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "consume_provider_result.py"),
                    str(output),
                    "--provider-id",
                    "codex-controlled-generation",
                    "--object-id",
                    "main_object",
                    "--mode",
                    "stage-candidate",
                    "--candidate-id",
                    "generated-v2",
                ],
                text=True,
                capture_output=True,
                check=True,
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "promote_candidate_asset.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate-asset",
                    "_staging/repair_candidates/main_object/generated-v2.png",
                    "--candidate-id",
                    "generated-v2",
                    "--delivery-class",
                    "generated-reconstruction",
                    "--repair-note",
                    "Promote generated candidate using staged provider evidence.",
                    "--selection-reason",
                    "Generated candidate is the accepted reconstruction result.",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            obj = metadata["objects"][0]
            self.assertEqual(obj["generation_source"], "codex-controlled-generation")
            self.assertEqual(obj["generation_model_or_tool"], "gpt-image-1")
            self.assertEqual(obj["generation_version"], "test-version")
            self.assertEqual(
                obj["generation_prompt_or_brief_ref"],
                "_staging/generation_briefs/main_object.json",
            )
            self.assertEqual(obj["generation_reference_inputs"], ["source/source_original.png"])
            compare_manifest = json.loads(
                (
                    output
                    / "_staging"
                    / "repair_candidates"
                    / "manual-generated-v2_compare.json"
                ).read_text(encoding="utf-8")
            )
            candidate_record = compare_manifest["candidates"][0]
            self.assertEqual(
                candidate_record["provider_stage_manifest_path"],
                "_staging/repair_candidates/main_object/generated-v2_provider_stage.json",
            )
            self.assertEqual(candidate_record["generation_source"], "codex-controlled-generation")
    def test_promote_candidate_asset_generated_reconstruction_can_use_compare_manifest_evidence_without_stage_manifest(self):
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
            self._set_candidate_promotion_confirmation(output)
            self._write_generated_plan_manifest(output)
            self._write_generation_brief(output)
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "prepare_provider_request.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            provider_dir = output / "_staging" / "providers" / "codex-controlled-generation" / "main_object"
            provider_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (4, 4), (0, 255, 0, 255)).save(provider_dir / "candidate_a.png")
            Image.new("RGBA", (4, 4), (0, 0, 255, 255)).save(provider_dir / "candidate_b.png")
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_provider_result.py"),
                    str(output),
                    "--provider-id",
                    "codex-controlled-generation",
                    "--object-id",
                    "main_object",
                    "--status",
                    "success",
                    "--artifact",
                    "candidate_png=_staging/providers/codex-controlled-generation/main_object/candidate_a.png",
                    "--tool-name",
                    "gpt-image-1",
                    "--tool-role",
                    "generation",
                    "--tool-version",
                    "test-version",
                    "--execution-mode",
                    "host-managed",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "consume_provider_result.py"),
                    str(output),
                    "--provider-id",
                    "codex-controlled-generation",
                    "--object-id",
                    "main_object",
                    "--mode",
                    "stage-candidate",
                    "--candidate-id",
                    "candidate-a",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            shutil.copy2(
                output / "_staging" / "repair_candidates" / "main_object" / "candidate-a.png",
                output / "_staging" / "repair_candidates" / "main_object" / "candidate-b.png",
            )
            shutil.copy2(
                output / "_staging" / "repair_candidates" / "main_object" / "candidate-a_provider_stage.json",
                output / "_staging" / "repair_candidates" / "main_object" / "candidate-b_provider_stage.json",
            )
            compare_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "compare_candidate_assets.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate",
                    "candidate-a=_staging/repair_candidates/main_object/candidate-a.png",
                    "--candidate",
                    "candidate-b=_staging/repair_candidates/main_object/candidate-b.png",
                    "--compare-note",
                    "Compare generated candidates.",
                    "--compare-criterion",
                    "generated edge fidelity",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(compare_result.returncode, 0, compare_result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            comparison_id = metadata["objects"][0]["candidate_comparisons"][0]["comparison_id"]
            (output / "_staging" / "repair_candidates" / "main_object" / "candidate-a_provider_stage.json").unlink()

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "promote_candidate_asset.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate-id",
                    "candidate-a",
                    "--comparison-id",
                    comparison_id,
                    "--delivery-class",
                    "generated-reconstruction",
                    "--repair-note",
                    "Promote from compare manifest evidence only.",
                    "--selection-reason",
                    "Candidate A is the accepted generated result.",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            obj = metadata["objects"][0]
            self.assertEqual(obj["generation_source"], "codex-controlled-generation")
            self.assertEqual(obj["generation_model_or_tool"], "gpt-image-1")
    def test_promote_candidate_asset_generated_reconstruction_requires_evidence_when_stage_manifest_is_missing(self):
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
            self._set_candidate_promotion_confirmation(output)
            candidate_dir = output / "_staging" / "repair_candidates" / "main_object"
            candidate_dir.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA", (4, 4), (0, 255, 0, 255)).save(candidate_dir / "generated-v3.png")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "promote_candidate_asset.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--candidate-asset",
                    "_staging/repair_candidates/main_object/generated-v3.png",
                    "--candidate-id",
                    "generated-v3",
                    "--delivery-class",
                    "generated-reconstruction",
                    "--repair-note",
                    "Reject generated promotion without evidence.",
                    "--selection-reason",
                    "Generated delivery evidence is required.",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("generated-reconstruction promotion requires generation_source", result.stderr)
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
            metadata["confirmation"]["candidate_promotion"]["status"] = "confirmed"
            metadata["confirmation"]["candidate_promotion"]["source"] = "explicit-user-confirmed"
            metadata["confirmation"]["candidate_promotion"]["evidence_ref"] = "chat:promotion-approved"
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
            self._set_candidate_promotion_confirmation(output)
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
            self._set_candidate_promotion_confirmation(output)
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
            self._set_candidate_promotion_confirmation(output)
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
            self._set_candidate_promotion_confirmation(output)
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
            metadata["confirmation"]["candidate_promotion"]["status"] = "confirmed"
            metadata["confirmation"]["candidate_promotion"]["source"] = "explicit-user-confirmed"
            metadata["confirmation"]["candidate_promotion"]["evidence_ref"] = "chat:promote-candidate"
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



