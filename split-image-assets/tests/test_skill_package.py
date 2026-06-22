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

    def _write_single_object_metadata(self, package_dir: pathlib.Path) -> dict:
        metadata_path = package_dir / "metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["objects"] = [
            {
                "id": "main_object",
                "role": "main",
                "asset_path": "assets/main_object_transparent.png",
                "mask_path": "masks/mask_main.png",
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
            ROOT / "references" / "asset-package-contract.md",
            ROOT / "references" / "qa-standards.md",
            ROOT / "references" / "manual-review.md",
            ROOT / "scripts" / "init_asset_package.py",
            ROOT / "scripts" / "build_previews.py",
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
        self.assertIn("2x2 sprite sheet is only a preview", skill_text)

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
            "manual review",
            "does not perform segmentation",
        ]:
            self.assertIn(expected, usage)

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
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["package_name"], "fixture")
            self.assertEqual(metadata["source"]["width"], 4)
            self.assertEqual(metadata["source"]["height"], 3)
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


if __name__ == "__main__":
    unittest.main()
