import pathlib
import sys

TESTS_DIR = pathlib.Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from skill_package_testlib import Image, REPO, ROOT, SplitImageAssetsTestBase, json, pathlib, re, subprocess, sys, tempfile


class SplitImageAssetsPackageTests(SplitImageAssetsTestBase):
    def test_record_quality_review_defaults_approximate_reconstruction_to_user_decision(self):
        review_script = (ROOT / "scripts" / "record_quality_review.py").read_text(encoding="utf-8")
        self.assertIn("from split_image_assets_contract import (", review_script)
        review = self._load_script_module("record_quality_review.py")
        self.assertEqual(
            review.DEFAULT_PAUSE_CATEGORY_BY_CONFIRMATION["approximate_reconstruction"],
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
            metadata["confirmation"]["final_acceptance"].update(
                {
                    "status": "confirmed",
                    "source": "explicit-user-confirmed",
                    "pause_category": "formal-approval",
                    "evidence_ref": "",
                }
            )
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
    def test_record_quality_review_rejects_weak_inferred_resource_family_evidence(self):
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
                    "--resource-family",
                    "right-rail-hardware",
                    "--resource-family-confirmed",
                    "--confirmation-key",
                    "granularity_alignment",
                    "--confirmation-status",
                    "confirmed",
                    "--confirmation-source",
                    "inferred-from-user",
                    "--pause-category",
                    "user-decision",
                    "--evidence-ref",
                    "user said continue",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("exact branch", result.stderr)
    def test_record_quality_review_rejects_weak_inferred_resource_family_evidence_via_decision_stage(self):
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
                    "--resource-family",
                    "right-rail-hardware",
                    "--resource-family-confirmed",
                    "--decision-stage",
                    "granularity-alignment",
                    "--decision-question",
                    "Use atomic-layer granularity for the right rail hardware?",
                    "--decision-recommended",
                    "yes",
                    "--decision-answer",
                    "yes",
                    "--decision-effect",
                    "Proceed with atomic-layer packaging for the right rail hardware.",
                    "--decision-source",
                    "inferred-from-user",
                    "--pause-category",
                    "user-decision",
                    "--blocking",
                    "true",
                    "--evidence-ref",
                    "user said continue",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("exact branch", result.stderr)
    def test_record_quality_review_accepts_explicit_resource_family_evidence(self):
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
                    "--resource-family",
                    "right-rail-hardware",
                    "--resource-family-confirmed",
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

            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["granularity"]["resource_family"], "right-rail-hardware")
            self.assertTrue(metadata["granularity"]["resource_family_confirmed"])
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
    def test_record_quality_review_negative_candidate_promotion_keeps_pending_confirmation_unset(self):
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
                    "no",
                    "--decision-effect",
                    "Keep the current revision active.",
                    "--decision-source",
                    "explicit-user-confirmed",
                    "--pause-category",
                    "formal-approval",
                    "--blocking",
                    "true",
                    "--evidence-ref",
                    "chat:promotion-declined",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(
                metadata["confirmation"]["candidate_promotion"]["status"],
                "pending",
            )
            self.assertEqual(
                metadata["confirmation"]["candidate_promotion"]["source"],
                "unset",
            )
            self.assertEqual(
                metadata["confirmation"]["candidate_promotion"]["evidence_ref"],
                "",
            )
            self.assertEqual(metadata["decision_log"][0]["recorded_answer"], "no")
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
    def test_record_quality_review_records_generated_reconstruction_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (255, 0, 0, 255)).save(source)
            output = tmp_path / "package"

            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            self._write_single_object_metadata(output)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "record_quality_review.py"),
                    str(output),
                    "--object-id",
                    "main_object",
                    "--delivery-class",
                    "generated-reconstruction",
                    "--generation-source",
                    "codex-controlled-generation",
                    "--generation-model-or-tool",
                    "gpt-image-1",
                    "--generation-version",
                    "test",
                    "--generation-prompt-or-brief-ref",
                    "_staging/generation_briefs/main_object.json",
                    "--generation-reference-input",
                    "source/source_original.png",
                    "--generation-provider-class",
                    "codex-controlled-generation",
                    "--generation-installed",
                    "true",
                    "--generation-runtime-ready",
                    "true",
                    "--generation-production-ready",
                    "true",
                    "--generation-capability-note",
                    "Controlled generation path is available for this fixture.",
                    "--review-note",
                    "Recorded generated reconstruction evidence.",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
            obj = metadata["objects"][0]
            self.assertEqual(obj["delivery_class"], "generated-reconstruction")
            self.assertEqual(obj["generation_source"], "codex-controlled-generation")
            self.assertEqual(obj["generation_model_or_tool"], "gpt-image-1")
            self.assertEqual(obj["generation_version"], "test")
            self.assertEqual(
                obj["generation_prompt_or_brief_ref"],
                "_staging/generation_briefs/main_object.json",
            )
            self.assertEqual(obj["generation_reference_inputs"], ["source/source_original.png"])
            self.assertEqual(
                metadata["capability"]["generation"],
                {
                    "provider_class": "codex-controlled-generation",
                    "installed": True,
                    "runtime_ready": True,
                    "production_ready": True,
                    "notes": "Controlled generation path is available for this fixture.",
                },
            )
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
    def test_record_quality_review_rejects_legacy_final_promotion_confirmation_key(self):
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
                    "final_promotion_acceptance",
                    "--confirmation-status",
                    "confirmed",
                    "--confirmation-source",
                    "explicit-user-confirmed",
                    "--pause-category",
                    "formal-approval",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("invalid choice", result.stderr)
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
    def test_validate_asset_package_rejects_unresolved_requires_user_confirmation_final_action(self):
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
            metadata["qa"]["status"] = "pass"
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
                "final_action": "unset",
                "decision_source": "explicit-user-confirmed",
            }
            metadata["decision_log"].append(
                {
                    "stage": "asset-routing-confirmation",
                    "pause_category": "user-decision",
                    "question": "Should this text-like object be rebuilt downstream or preserved as a visual asset?",
                    "recommended_answer": "rebuild downstream unless fidelity-critical",
                    "recorded_answer": "keep reviewing",
                    "decision_effect": "Leave the route unresolved until a final action is chosen.",
                    "decision_source": "explicit-user-confirmed",
                    "evidence_ref": "chat:needs-text-routing-resolution",
                    "blocking": "true",
                    "object_id": "main_object",
                }
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
            self.assertIn("final_action", result.stderr)
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
                "accepted_approximate_reconstructions": 0,
                "accepted_generated_reconstructions": 0,
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
            metadata["confirmation"]["candidate_promotion"]["status"] = "confirmed"
            metadata["confirmation"]["candidate_promotion"]["source"] = "explicit-user-confirmed"
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
    def test_validate_asset_package_allows_legacy_non_generated_package_without_plan_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (255, 0, 0, 255)).save(source)
            output = tmp_path / "package"

            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            self._write_ready_validation_package(output)
            (output / "plan_manifest.json").unlink()

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
    def test_validate_asset_package_rejects_generated_delivery_without_plan_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (255, 0, 0, 255)).save(source)
            output = tmp_path / "package"

            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            metadata = self._write_ready_validation_package(output)
            obj = metadata["objects"][0]
            obj["delivery_class"] = "generated-reconstruction"
            obj["reuse_status"] = "accepted-generated-reconstruction"
            obj["generation_source"] = "codex-controlled-generation"
            obj["generation_model_or_tool"] = "gpt-image-1"
            obj["generation_version"] = "test"
            obj["generation_prompt_or_brief_ref"] = "_staging/generation_briefs/main_object.json"
            obj["generation_reference_inputs"] = ["source/source_original.png"]
            obj["manual_review_confirmed"] = True
            metadata["confirmation"]["candidate_promotion"]["status"] = "confirmed"
            metadata["confirmation"]["candidate_promotion"]["source"] = "explicit-user-confirmed"
            metadata["confirmation"]["generation_routing"]["status"] = "confirmed"
            metadata["confirmation"]["generation_routing"]["source"] = "explicit-user-confirmed"
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            (output / "plan_manifest.json").unlink()

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
            self.assertIn("plan_manifest.json", result.stderr)
    def test_validate_asset_package_accepts_generated_delivery_with_plan_manifest_and_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (255, 0, 0, 255)).save(source)
            output = tmp_path / "package"

            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            metadata = self._write_ready_validation_package(output)
            obj = metadata["objects"][0]
            obj["delivery_class"] = "generated-reconstruction"
            obj["reuse_status"] = "accepted-generated-reconstruction"
            obj["generation_source"] = "codex-controlled-generation"
            obj["generation_model_or_tool"] = "gpt-image-1"
            obj["generation_version"] = "test"
            obj["generation_prompt_or_brief_ref"] = "_staging/generation_briefs/main_object.json"
            obj["generation_reference_inputs"] = ["source/source_original.png"]
            obj["manual_review_confirmed"] = True
            metadata["confirmation"]["candidate_promotion"]["status"] = "confirmed"
            metadata["confirmation"]["candidate_promotion"]["source"] = "explicit-user-confirmed"
            metadata["confirmation"]["generation_routing"]["status"] = "confirmed"
            metadata["confirmation"]["generation_routing"]["source"] = "explicit-user-confirmed"
            metadata["decision_log"].append(
                {
                    "stage": "generation-routing",
                    "pause_category": "user-decision",
                    "question": "Route main_object through generated reconstruction?",
                    "recommended_answer": "yes",
                    "recorded_answer": "yes",
                    "decision_effect": "Use generated reconstruction for the promoted object asset.",
                    "decision_source": "explicit-user-confirmed",
                    "evidence_ref": "",
                    "blocking": "true",
                    "object_id": "main_object",
                }
            )
            metadata["capability"]["generation"] = {
                "provider_class": "codex-controlled-generation",
                "installed": True,
                "runtime_ready": True,
                "production_ready": True,
                "notes": "Fixture generated route capability.",
            }
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            self._write_generated_plan_manifest(output)

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
    def test_validate_asset_package_rejects_generated_delivery_without_generated_compare_manifest_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (255, 0, 0, 255)).save(source)
            output = tmp_path / "package"

            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            metadata = self._write_ready_validation_package(output)
            obj = metadata["objects"][0]
            obj["delivery_class"] = "generated-reconstruction"
            obj["reuse_status"] = "accepted-generated-reconstruction"
            obj["generation_source"] = "codex-controlled-generation"
            obj["generation_model_or_tool"] = "gpt-image-1"
            obj["generation_version"] = "test"
            obj["generation_prompt_or_brief_ref"] = "_staging/generation_briefs/main_object.json"
            obj["generation_reference_inputs"] = ["source/source_original.png"]
            obj["manual_review_confirmed"] = True
            obj["selected_candidate_id"] = "generated-v1"
            obj["repair_history"] = [{"candidate_id": "generated-v1"}]
            obj["candidate_comparisons"] = [
                {
                    "comparison_id": "cmp-generated-1",
                    "object_id": "main_object",
                    "candidate_ids": ["generated-v1"],
                    "compare_artifact_path": "_staging/repair_candidates/cmp-generated-1_compare.png",
                    "compare_manifest_path": "_staging/repair_candidates/cmp-generated-1_compare.json",
                    "compare_note": "Generated candidate compare.",
                    "compare_criteria": ["generated edge fidelity"],
                    "review_focus": ["generated fidelity"],
                    "risks": ["prompt drift"],
                    "score_manifest_path": "",
                    "selected_candidate_id": "generated-v1",
                    "selection_reason": "Best generated candidate.",
                    "created_at": "2026-07-04T00:00:00Z",
                }
            ]
            metadata["confirmation"]["candidate_promotion"]["status"] = "confirmed"
            metadata["confirmation"]["candidate_promotion"]["source"] = "explicit-user-confirmed"
            metadata["confirmation"]["generation_routing"]["status"] = "confirmed"
            metadata["confirmation"]["generation_routing"]["source"] = "explicit-user-confirmed"
            metadata["decision_log"].append(
                {
                    "stage": "generation-routing",
                    "pause_category": "user-decision",
                    "question": "Route main_object through generated reconstruction?",
                    "recommended_answer": "yes",
                    "recorded_answer": "yes",
                    "decision_effect": "Use generated reconstruction for the promoted object asset.",
                    "decision_source": "explicit-user-confirmed",
                    "evidence_ref": "",
                    "blocking": "true",
                    "object_id": "main_object",
                }
            )
            metadata["capability"]["generation"] = {
                "provider_class": "codex-controlled-generation",
                "installed": True,
                "runtime_ready": True,
                "production_ready": True,
                "notes": "Fixture generated route capability.",
            }
            (output / "_staging" / "repair_candidates").mkdir(parents=True, exist_ok=True)
            Image.new("RGB", (8, 8), (220, 220, 220)).save(
                output / "_staging" / "repair_candidates" / "cmp-generated-1_compare.png"
            )
            (output / "_staging" / "repair_candidates" / "cmp-generated-1_compare.json").write_text(
                json.dumps(
                    {
                        "comparison_id": "cmp-generated-1",
                        "object_id": "main_object",
                        "candidate_ids": ["generated-v1"],
                        "candidates": [
                            {
                                "candidate_id": "generated-v1",
                                "asset_path": "_staging/repair_candidates/generated-v1.png",
                            }
                        ],
                        "compare_artifact_path": "_staging/repair_candidates/cmp-generated-1_compare.png",
                        "compare_note": "Generated candidate compare.",
                        "compare_criteria": ["generated edge fidelity"],
                        "review_focus": ["generated fidelity"],
                        "risks": ["prompt drift"],
                        "score_manifest_path": "",
                        "created_at": "2026-07-04T00:00:00Z",
                    },
                    indent=2,
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            self._write_generated_plan_manifest(output)

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
            self.assertIn("generated compare manifest must record provider_stage_manifest_path", result.stderr)
    def test_validate_asset_package_rejects_generated_delivery_without_generated_compare_provider_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (255, 0, 0, 255)).save(source)
            output = tmp_path / "package"

            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            metadata = self._write_ready_validation_package(output)
            obj = metadata["objects"][0]
            obj["delivery_class"] = "generated-reconstruction"
            obj["reuse_status"] = "accepted-generated-reconstruction"
            obj["generation_source"] = "codex-controlled-generation"
            obj["generation_model_or_tool"] = "gpt-image-1"
            obj["generation_version"] = "test"
            obj["generation_prompt_or_brief_ref"] = "_staging/generation_briefs/main_object.json"
            obj["generation_reference_inputs"] = ["source/source_original.png"]
            obj["manual_review_confirmed"] = True
            obj["selected_candidate_id"] = "generated-v1"
            obj["repair_history"] = [{"candidate_id": "generated-v1"}]
            obj["candidate_comparisons"] = [
                {
                    "comparison_id": "cmp-generated-2",
                    "object_id": "main_object",
                    "candidate_ids": ["generated-v1"],
                    "compare_artifact_path": "_staging/repair_candidates/cmp-generated-2_compare.png",
                    "compare_manifest_path": "_staging/repair_candidates/cmp-generated-2_compare.json",
                    "compare_note": "Generated candidate compare.",
                    "compare_criteria": ["generated edge fidelity"],
                    "review_focus": ["generated fidelity"],
                    "risks": ["prompt drift"],
                    "score_manifest_path": "",
                    "selected_candidate_id": "generated-v1",
                    "selection_reason": "Best generated candidate.",
                    "created_at": "2026-07-04T00:00:00Z",
                }
            ]
            metadata["confirmation"]["candidate_promotion"]["status"] = "confirmed"
            metadata["confirmation"]["candidate_promotion"]["source"] = "explicit-user-confirmed"
            metadata["confirmation"]["generation_routing"]["status"] = "confirmed"
            metadata["confirmation"]["generation_routing"]["source"] = "explicit-user-confirmed"
            metadata["decision_log"].append(
                {
                    "stage": "generation-routing",
                    "pause_category": "user-decision",
                    "question": "Route main_object through generated reconstruction?",
                    "recommended_answer": "yes",
                    "recorded_answer": "yes",
                    "decision_effect": "Use generated reconstruction for the promoted object asset.",
                    "decision_source": "explicit-user-confirmed",
                    "evidence_ref": "",
                    "blocking": "true",
                    "object_id": "main_object",
                }
            )
            metadata["capability"]["generation"] = {
                "provider_class": "codex-controlled-generation",
                "installed": True,
                "runtime_ready": True,
                "production_ready": True,
                "notes": "Fixture generated route capability.",
            }
            (output / "_staging" / "repair_candidates").mkdir(parents=True, exist_ok=True)
            Image.new("RGB", (8, 8), (220, 220, 220)).save(
                output / "_staging" / "repair_candidates" / "cmp-generated-2_compare.png"
            )
            (output / "_staging" / "repair_candidates" / "cmp-generated-2_compare.json").write_text(
                json.dumps(
                    {
                        "comparison_id": "cmp-generated-2",
                        "object_id": "main_object",
                        "candidate_ids": ["generated-v1"],
                        "candidates": [
                            {
                                "candidate_id": "generated-v1",
                                "asset_path": "_staging/repair_candidates/generated-v1.png",
                                "provider_stage_manifest_path": "_staging/repair_candidates/generated-v1_provider_stage.json",
                                "generation_source": "codex-controlled-generation",
                                "generation_model_or_tool": "gpt-image-1",
                                "generation_version": "test",
                                "generation_prompt_or_brief_ref": "_staging/generation_briefs/main_object.json",
                                "generation_reference_inputs": ["source/source_original.png"],
                            }
                        ],
                        "compare_artifact_path": "_staging/repair_candidates/cmp-generated-2_compare.png",
                        "compare_note": "Generated candidate compare.",
                        "compare_criteria": ["generated edge fidelity"],
                        "review_focus": ["generated fidelity"],
                        "risks": ["prompt drift"],
                        "score_manifest_path": "",
                        "created_at": "2026-07-04T00:00:00Z",
                    },
                    indent=2,
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            self._write_generated_plan_manifest(output)

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
            self.assertIn("generated compare manifest must record provider_id", result.stderr)
    def test_validate_asset_package_rejects_generated_delivery_without_generation_capability_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (255, 0, 0, 255)).save(source)
            output = tmp_path / "package"

            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            metadata = self._write_ready_validation_package(output)
            obj = metadata["objects"][0]
            obj["delivery_class"] = "generated-reconstruction"
            obj["reuse_status"] = "accepted-generated-reconstruction"
            obj["generation_source"] = "codex-controlled-generation"
            obj["generation_model_or_tool"] = "gpt-image-1"
            obj["generation_version"] = "test"
            obj["generation_prompt_or_brief_ref"] = "_staging/generation_briefs/main_object.json"
            obj["generation_reference_inputs"] = ["source/source_original.png"]
            obj["manual_review_confirmed"] = True
            metadata["confirmation"]["candidate_promotion"]["status"] = "confirmed"
            metadata["confirmation"]["candidate_promotion"]["source"] = "explicit-user-confirmed"
            metadata["confirmation"]["generation_routing"]["status"] = "confirmed"
            metadata["confirmation"]["generation_routing"]["source"] = "explicit-user-confirmed"
            metadata["capability"].pop("generation", None)
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            self._write_generated_plan_manifest(output)

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
            self.assertIn("metadata.capability.generation", result.stderr)
    def test_validate_asset_package_rejects_generated_delivery_without_object_scoped_generation_routing_decision(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (255, 0, 0, 255)).save(source)
            output = tmp_path / "package"

            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            metadata = self._write_ready_validation_package(output)
            obj = metadata["objects"][0]
            obj["delivery_class"] = "generated-reconstruction"
            obj["reuse_status"] = "accepted-generated-reconstruction"
            obj["generation_source"] = "codex-controlled-generation"
            obj["generation_model_or_tool"] = "gpt-image-1"
            obj["generation_version"] = "test"
            obj["generation_prompt_or_brief_ref"] = "_staging/generation_briefs/main_object.json"
            obj["generation_reference_inputs"] = ["source/source_original.png"]
            obj["manual_review_confirmed"] = True
            metadata["confirmation"]["candidate_promotion"]["status"] = "confirmed"
            metadata["confirmation"]["candidate_promotion"]["source"] = "explicit-user-confirmed"
            metadata["confirmation"]["generation_routing"]["status"] = "confirmed"
            metadata["confirmation"]["generation_routing"]["source"] = "explicit-user-confirmed"
            metadata["capability"]["generation"] = {
                "provider_class": "codex-controlled-generation",
                "installed": True,
                "runtime_ready": True,
                "production_ready": True,
                "notes": "Fixture generated route capability.",
            }
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            self._write_generated_plan_manifest(output)

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
            self.assertIn("object-scoped generation_routing decision_log", result.stderr)
    def test_validate_asset_package_rejects_generated_delivery_with_pending_generation_routing(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (255, 0, 0, 255)).save(source)
            output = tmp_path / "package"

            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            metadata = self._write_ready_validation_package(output)
            obj = metadata["objects"][0]
            obj["delivery_class"] = "generated-reconstruction"
            obj["reuse_status"] = "accepted-generated-reconstruction"
            obj["generation_source"] = "codex-controlled-generation"
            obj["generation_model_or_tool"] = "gpt-image-1"
            obj["generation_version"] = "test"
            obj["generation_prompt_or_brief_ref"] = "_staging/generation_briefs/main_object.json"
            obj["generation_reference_inputs"] = ["source/source_original.png"]
            obj["manual_review_confirmed"] = True
            metadata["confirmation"]["candidate_promotion"]["status"] = "confirmed"
            metadata["confirmation"]["candidate_promotion"]["source"] = "explicit-user-confirmed"
            metadata["confirmation"]["generation_routing"]["status"] = "pending"
            metadata["confirmation"]["generation_routing"]["source"] = "unset"
            metadata["capability"]["generation"] = {
                "provider_class": "codex-controlled-generation",
                "installed": True,
                "runtime_ready": True,
                "production_ready": True,
                "notes": "Fixture generated route capability.",
            }
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            self._write_generated_plan_manifest(output)

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
            self.assertIn("generation_routing", result.stderr)
    def test_validate_asset_package_allows_generated_only_pass_without_extraction_production_capability(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (255, 0, 0, 255)).save(source)
            output = tmp_path / "package"

            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            metadata = self._write_ready_validation_package(output)
            obj = metadata["objects"][0]
            obj["delivery_class"] = "generated-reconstruction"
            obj["reuse_status"] = "accepted-generated-reconstruction"
            obj["generation_source"] = "codex-controlled-generation"
            obj["generation_model_or_tool"] = "gpt-image-1"
            obj["generation_version"] = "test"
            obj["generation_prompt_or_brief_ref"] = "_staging/generation_briefs/main_object.json"
            obj["generation_reference_inputs"] = ["source/source_original.png"]
            obj["manual_review_confirmed"] = True
            metadata["capability"]["production_capable"] = False
            metadata["capability"]["notes"] = "Generated delivery is the approved production path for this object."
            metadata["confirmation"]["candidate_promotion"]["status"] = "confirmed"
            metadata["confirmation"]["candidate_promotion"]["source"] = "explicit-user-confirmed"
            metadata["confirmation"]["generation_routing"]["status"] = "confirmed"
            metadata["confirmation"]["generation_routing"]["source"] = "explicit-user-confirmed"
            metadata["decision_log"].append(
                {
                    "stage": "generation-routing",
                    "pause_category": "user-decision",
                    "question": "Route main_object through generated reconstruction?",
                    "recommended_answer": "yes",
                    "recorded_answer": "yes",
                    "decision_effect": "Use generated reconstruction for the promoted object asset.",
                    "decision_source": "explicit-user-confirmed",
                    "evidence_ref": "",
                    "blocking": "true",
                    "object_id": "main_object",
                }
            )
            metadata["capability"]["generation"] = {
                "provider_class": "codex-controlled-generation",
                "installed": True,
                "runtime_ready": True,
                "production_ready": True,
                "notes": "Fixture generated route capability.",
            }
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            self._write_generated_plan_manifest(output)

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
            metadata["confirmation"]["candidate_promotion"]["status"] = "confirmed"
            metadata["confirmation"]["candidate_promotion"]["source"] = "explicit-user-confirmed"
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
    def test_record_quality_review_allows_generated_only_pass_without_extraction_production_capability(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            source = tmp_path / "source.png"
            Image.new("RGBA", (4, 3), (255, 0, 0, 255)).save(source)
            output = tmp_path / "package"
            init_result = self._run_init(source, output)
            self.assertEqual(init_result.returncode, 0, init_result.stderr)
            metadata = self._write_ready_validation_package(output)
            obj = metadata["objects"][0]
            obj["delivery_class"] = "generated-reconstruction"
            obj["reuse_status"] = "accepted-generated-reconstruction"
            obj["generation_source"] = "codex-controlled-generation"
            obj["generation_model_or_tool"] = "gpt-image-1"
            obj["generation_version"] = "test"
            obj["generation_prompt_or_brief_ref"] = "_staging/generation_briefs/main_object.json"
            obj["generation_reference_inputs"] = ["source/source_original.png"]
            obj["manual_review_confirmed"] = True
            metadata["qa"]["status"] = "needs-review"
            metadata["capability"]["production_capable"] = False
            metadata["capability"]["notes"] = "Generated delivery is the approved production path for this object."
            metadata["confirmation"]["candidate_promotion"]["status"] = "confirmed"
            metadata["confirmation"]["candidate_promotion"]["source"] = "explicit-user-confirmed"
            metadata["confirmation"]["generation_routing"]["status"] = "confirmed"
            metadata["confirmation"]["generation_routing"]["source"] = "explicit-user-confirmed"
            metadata["decision_log"].append(
                {
                    "stage": "generation-routing",
                    "pause_category": "user-decision",
                    "question": "Route main_object through generated reconstruction?",
                    "recommended_answer": "yes",
                    "recorded_answer": "yes",
                    "decision_effect": "Use generated reconstruction for the promoted object asset.",
                    "decision_source": "explicit-user-confirmed",
                    "evidence_ref": "",
                    "blocking": "true",
                    "object_id": "main_object",
                }
            )
            metadata["capability"]["generation"] = {
                "provider_class": "codex-controlled-generation",
                "installed": True,
                "runtime_ready": True,
                "production_ready": True,
                "notes": "Fixture generated route capability.",
            }
            (output / "metadata.json").write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            self._write_generated_plan_manifest(output)

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

            self.assertEqual(result.returncode, 0, result.stderr)
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



