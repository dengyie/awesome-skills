import pathlib
import sys

TESTS_DIR = pathlib.Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from skill_package_testlib import Image, REPO, ROOT, SplitImageAssetsTestBase, json, pathlib, re, subprocess, sys, tempfile


class SplitImageAssetsPackageTests(SplitImageAssetsTestBase):
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



