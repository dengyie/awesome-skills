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
        }
        if include_quality_evidence:
            object_record["quality_checks"] = {
                "mask_alignment": "pass",
                "alpha_edges": "pass",
                "background_residue": "pass",
                "reuse_readiness": "pass",
            }
        metadata["objects"] = [
            object_record
        ]
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
            ROOT / "scripts" / "init_asset_package.py",
            ROOT / "scripts" / "import_external_assets.py",
            ROOT / "scripts" / "build_previews.py",
            ROOT / "scripts" / "build_quality_previews.py",
            ROOT / "scripts" / "check_extraction_environment.py",
            ROOT / "scripts" / "archive_intermediates.py",
            ROOT / "scripts" / "record_quality_review.py",
            ROOT / "scripts" / "export_asset_manifest.py",
            ROOT / "scripts" / "validate_asset_package.py",
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
        self.assertIn("ANALYZE BEFORE EXTRACTING", skill_text)
        self.assertIn("REUSABLE ASSETS BEFORE PREVIEWS", skill_text)
        self.assertIn("NEVER HIDE UNCERTAINTY", skill_text)
        self.assertIn("QUALITY-GATED PIPELINE", skill_text)
        self.assertIn("DECISION SYNC BEFORE AMBIGUOUS SPLITS", skill_text)
        self.assertIn("EXTRACTION CAPABILITY GATE", skill_text)
        self.assertIn("GRANULARITY ALIGNMENT GATE", skill_text)
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
        self.assertIn("recommended_recipe", report)
        self.assertIn("recommended_next_step", report)
        self.assertIn("production_capable", report)
        self.assertIn("missing_for_production", report)
        self.assertIn("Pillow", report["tools"])
        self.assertIn(report["tools"]["Pillow"]["available"], [True, False])
        self.assertIn(report["production_capable"], [True, False])
        self.assertIsInstance(report["missing_for_production"], list)
        self.assertIn("draft", report["recommended_next_step"].lower())

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
            self.assertEqual(metadata["qa"]["status"], "needs-review")
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
                    "--quality-gate",
                    "mask overlay inspected",
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
                    "--qa-status",
                    "pass",
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
                    "manual_review_flags": ["ai-assisted mask reviewed"],
                    "quality_checks": {
                        "mask_alignment": "pass",
                        "alpha_edges": "pass",
                        "background_residue": "pass",
                        "reuse_readiness": "pass",
                    },
                },
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
