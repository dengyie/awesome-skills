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
    def _load_check_environment_module(self):
        module_path = ROOT / "scripts" / "check_extraction_environment.py"
        spec = importlib.util.spec_from_file_location("check_extraction_environment", module_path)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
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
        metadata["objects"] = [
            object_record
        ]
        metadata["audit"] = {}
        metadata_path.write_text(
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
            ROOT / "scripts" / "archive_intermediates.py",
            ROOT / "scripts" / "record_quality_review.py",
            ROOT / "scripts" / "export_asset_manifest.py",
            ROOT / "scripts" / "validate_asset_package.py",
            ROOT / "scripts" / "promote_candidate_asset.py",
            REPO / "docs" / "usage" / "split-image-assets.md",
        ]

        missing = [str(path.relative_to(REPO)) for path in required_paths if not path.exists()]
        self.assertEqual(missing, [])

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
        self.assertIn("GRANULARITY ALIGNMENT GATE", skill_text)
        self.assertIn("CONFIRMATION GATE", skill_text)
        self.assertIn("DO NOT DEFAULT TO ONE-PASS EXTRACTION", skill_text)
        self.assertIn("PROFESSIONAL SEGMENTER FIRST", skill_text)
        self.assertIn("SOURCE-SPACE MASKS ARE NORMAL", skill_text)
        self.assertIn("STAGE INTERMEDIATES", skill_text)
        self.assertIn("tile", skill_text)
        self.assertIn("glyph", skill_text)
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
        ]:
            self.assertIn(expected, usage)

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
                    "--production-capable",
                    "true",
                    "--capability-user-choice",
                    "production-capable",
                    "--capability-note",
                    "SAM2 and rembg external outputs were provided.",
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
                    "manual-acceptance",
                    "--decision-question",
                    "Accept this imported layer as production-ready?",
                    "--decision-recommended",
                    "yes",
                    "--decision-answer",
                    "yes",
                    "--decision-effect",
                    "Allow final pass and downstream reuse.",
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
            self.assertEqual(entry["user_answer"], "yes")

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
            metadata["asset_summary"] = {
                "production_ready_assets": 2,
                "draft_candidate_assets": 0,
                "support_only_layers": 1,
                "blocked_assets": 0,
            }
            metadata["decision_log"] = [
                {
                    "stage": "final-acceptance",
                    "question": "Accept this UI atomic split as production-ready?",
                    "recommended_answer": "yes",
                    "user_answer": "yes",
                    "decision_effect": "Allow qa.status=pass for the validated fixture.",
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
                    "question": "Accept approximate reconstructed candidate after compare?",
                    "recommended_answer": "yes",
                    "user_answer": "yes",
                    "decision_effect": "Allow archived compare evidence to support validation.",
                }
            ]
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
                    "question": "Accept approximate reconstructed carrier after candidate review?",
                    "recommended_answer": "yes",
                    "user_answer": "yes",
                    "decision_effect": "Allow promotion of the chosen candidate after compare evidence.",
                }
            ]
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


if __name__ == "__main__":
    unittest.main()
