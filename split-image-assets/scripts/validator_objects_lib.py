import json
from pathlib import Path

from package_state_lib import find_plan_object
from split_image_assets_contract import (
    ALLOWED_ASSET_CLASSES,
    ALLOWED_DELIVERY_CLASSES,
    ALLOWED_GENERATION_PROVIDER_CLASSES,
    ALLOWED_OBJECT_TYPES,
    ALLOWED_QUALITY_CHECK_STATUSES,
    ALLOWED_REUSE_STATUSES,
    ALLOWED_ROUTING_ACTIONS,
    ALLOWED_ROUTING_DECISION_SOURCES,
    ALLOWED_SCORE_VALUES,
    ALLOWED_TEXT_RENDER_CLASSES,
    ALLOWED_TEXT_ROLES,
    NON_DEFAULT_CONFIRMATION_SOURCES,
    ORDINARY_TEXT_ROLES,
)
from validator_shared import (
    APPROXIMATE_RECONSTRUCTION_ACCEPTANCE_STAGES,
    GENERATION_ROUTING_CONFIRMATION_STAGES,
    GENERATED_EVIDENCE_FIELDS,
    OBJECT_ASSET_ROLES,
    PASS_READY_REUSE_STATUSES,
    REQUIRED_CANDIDATE_COMPARISON_FIELDS,
    REQUIRED_OBJECT_QUALITY_CHECKS,
    decision_answer,
    has_alpha,
    has_carrier_layer,
    has_glyph_layer,
    has_object_scoped_affirmative_decision,
    has_text_routing_confirmation,
    image_mode,
    image_size,
    is_crop_only_layer,
    is_generated_delivery_layer,
    is_helper_only_layer,
    is_placeholder_only_rebuild,
    is_reconstructed_or_approximate_layer,
    is_ui_like_package,
    promotion_confirmation_satisfied,
    rel_path,
    requires_candidate_comparison_evidence,
    requires_object_type,
)

def validate_objects(
    package_dir: Path,
    metadata: dict,
    source_size: tuple[int, int] | None,
    errors: list[str],
    plan_manifest: dict | None = None,
) -> None:
    objects = metadata.get("objects", [])
    if not isinstance(objects, list):
        errors.append("metadata.objects must be a list")
        return
    if not objects:
        errors.append("object inventory must include at least one object asset entry")
        return
    qa = metadata.get("qa", {})
    qa_status = qa.get("status") if isinstance(qa, dict) else None
    granularity = metadata.get("granularity", {}) if isinstance(metadata.get("granularity"), dict) else {}
    decision_log = metadata.get("decision_log", []) if isinstance(metadata.get("decision_log"), list) else []
    capability = metadata.get("capability", {}) if isinstance(metadata.get("capability"), dict) else {}
    generation_capability = capability.get("generation")
    ui_like_package = is_ui_like_package(metadata)
    requires_confirmation_ids = set()
    for item in objects:
        if not isinstance(item, dict):
            continue
        object_id = item.get("id")
        if not isinstance(object_id, str) or not object_id.strip():
            continue
        decision_routing = item.get("decision_routing", {})
        if not isinstance(decision_routing, dict):
            continue
        if decision_routing.get("recommended_action") == "requires_user_confirmation":
            requires_confirmation_ids.add(object_id.strip())
    if ui_like_package:
        for field_name in [
            "scope_strategy",
            "text_handling",
            "carrier_glyph_policy",
            "background_expectation",
            "layer_independence",
        ]:
            if granularity.get(field_name, "unset") == "unset":
                errors.append(
                    f"metadata.granularity.{field_name} must be recorded for UI or dense-composition packages"
                )
        pilot_entry = metadata.get("confirmation", {}).get("pilot_object", {})
        if pilot_entry.get("status") not in {"confirmed", "not-required"}:
            errors.append("metadata.confirmation.pilot_object must be confirmed or explicitly not-required for UI packages")
        elif pilot_entry.get("status") == "confirmed" and pilot_entry.get("source") not in NON_DEFAULT_CONFIRMATION_SOURCES:
            errors.append(
                "metadata.confirmation.pilot_object must come from explicit-user-confirmed or inferred-from-user when confirmed"
            )

    has_carrier = False
    has_glyph = False
    for item in objects:
        if not isinstance(item, dict):
            errors.append("metadata.objects entries must be objects")
            continue
        object_id = item.get("id", "<missing id>")
        role = item.get("role")
        if role not in OBJECT_ASSET_ROLES:
            errors.append(
                f"{object_id}: role must be one of: " + ", ".join(sorted(OBJECT_ASSET_ROLES))
            )
            continue
        object_type = item.get("object_type", "generic-object")
        if object_type not in ALLOWED_OBJECT_TYPES:
            errors.append(
                f"{object_id}: object_type must be one of: " + ", ".join(sorted(ALLOWED_OBJECT_TYPES))
            )
        elif requires_object_type(item) and object_type == "generic-object":
            errors.append(f"{object_id}: object_type must be recorded for UI/logo/support-style assets")
        has_carrier = has_carrier or has_carrier_layer(item)
        has_glyph = has_glyph or has_glyph_layer(item)
        placeholder_only_rebuild = is_placeholder_only_rebuild(item)
        asset_path = item.get("asset_path")
        if placeholder_only_rebuild and not asset_path:
            pass
        elif not asset_path:
            errors.append(f"{object_id}: asset_path is required for role {role}")
        else:
            path = rel_path(package_dir, asset_path, errors, f"{object_id}: asset_path")
            if path is None:
                continue
            if not path.exists():
                errors.append(f"{object_id}: asset file is missing: {asset_path}")
            elif path.suffix.lower() != ".png":
                errors.append(f"{object_id}: asset must be a PNG: {asset_path}")
            else:
                mode = image_mode(path, errors)
                if mode and not has_alpha(mode):
                    errors.append(f"{object_id}: asset PNG must include an alpha channel: {asset_path}")

        mask_path = item.get("mask_path")
        if placeholder_only_rebuild and not mask_path:
            pass
        elif mask_path:
            path = rel_path(package_dir, mask_path, errors, f"{object_id}: mask_path")
            if path is None:
                continue
            if not path.exists():
                errors.append(f"{object_id}: mask file is missing: {mask_path}")
            else:
                mask_size = image_size(path, errors)
                coordinate_space = item.get("mask_coordinate_space", "source")
                if coordinate_space == "source" and source_size and mask_size != source_size:
                    errors.append(
                        f"{object_id}: source-space mask dimensions {mask_size} do not match source {source_size}"
                    )

        confidence = item.get("confidence")
        method = item.get("extraction_method")
        flags = item.get("manual_review_flags", [])
        if (confidence == "low" or method == "ai-assisted") and not flags:
            errors.append(
                f"{object_id}: low-confidence or AI-assisted work needs manual_review_flags"
            )
        asset_class = item.get("asset_class")
        reuse_status = item.get("reuse_status")
        if asset_class not in ALLOWED_ASSET_CLASSES:
            errors.append(
                f"{object_id}: asset_class is required and must be one of: "
                + ", ".join(sorted(ALLOWED_ASSET_CLASSES))
            )
        if reuse_status not in ALLOWED_REUSE_STATUSES:
            errors.append(
                f"{object_id}: reuse_status is required and must be one of: "
                + ", ".join(sorted(ALLOWED_REUSE_STATUSES))
            )
        delivery_class = item.get("delivery_class")
        if delivery_class not in ALLOWED_DELIVERY_CLASSES:
            errors.append(
                f"{object_id}: delivery_class is required and must be one of: "
                + ", ".join(sorted(ALLOWED_DELIVERY_CLASSES))
            )
        capability = metadata.get("capability", {})
        production_capable = (
            capability.get("production_capable") if isinstance(capability, dict) else None
        )
        user_choice = capability.get("user_choice") if isinstance(capability, dict) else None
        if reuse_status == "production-ready" and production_capable is not True:
            if user_choice == "draft-packaging-only":
                errors.append(
                    f"{object_id}: draft-packaging-only packages cannot contain "
                    "production-ready reusable assets"
                )
            else:
                errors.append(
                    f"{object_id}: production-ready reuse_status requires "
                    "metadata.capability.production_capable=true"
                )
        if (
            qa_status == "pass"
            and asset_class in {"atomic", "candidate"}
            and reuse_status not in PASS_READY_REUSE_STATUSES
        ):
            errors.append(
                f"{object_id}: qa.status pass requires atomic reusable layers to be "
                "pass-eligible reuse_status values"
            )
        generated_delivery = is_generated_delivery_layer(item)
        if generated_delivery:
            generation_routing = metadata.get("confirmation", {}).get("generation_routing", {})
            if generation_routing.get("status") not in {"confirmed", "not-required"}:
                errors.append(
                    f"{object_id}: metadata.confirmation.generation_routing must be confirmed or explicitly not-required for generated-route delivery"
                )
            elif generation_routing.get("source") not in NON_DEFAULT_CONFIRMATION_SOURCES:
                errors.append(
                    f"{object_id}: metadata.confirmation.generation_routing must come from explicit-user-confirmed or inferred-from-user"
                )
            if not has_object_scoped_affirmative_decision(
                decision_log,
                GENERATION_ROUTING_CONFIRMATION_STAGES,
                str(object_id),
            ):
                errors.append(
                    f"{object_id}: generated-route delivery requires object-scoped generation_routing decision_log evidence"
                )
            if not isinstance(generation_capability, dict):
                errors.append(
                    f"{object_id}: metadata.capability.generation must be recorded for generated-route delivery"
                )
            else:
                provider_class = generation_capability.get("provider_class", "unset")
                if provider_class not in ALLOWED_GENERATION_PROVIDER_CLASSES:
                    errors.append(
                        f"{object_id}: metadata.capability.generation.provider_class must be one of: "
                        + ", ".join(sorted(ALLOWED_GENERATION_PROVIDER_CLASSES))
                    )
                for field_name in ["installed", "runtime_ready", "production_ready"]:
                    if not isinstance(generation_capability.get(field_name), bool):
                        errors.append(
                            f"{object_id}: metadata.capability.generation.{field_name} must be true or false"
                        )
                generation_notes = generation_capability.get("notes", "")
                if not isinstance(generation_notes, str):
                    errors.append(
                        f"{object_id}: metadata.capability.generation.notes must be a string"
                    )
                if provider_class == "unset":
                    errors.append(
                        f"{object_id}: metadata.capability.generation.provider_class must not stay unset for generated-route delivery"
                    )
                if reuse_status == "accepted-generated-reconstruction" or qa_status == "pass":
                    if generation_capability.get("production_ready") is not True:
                        errors.append(
                            f"{object_id}: accepted generated delivery requires metadata.capability.generation.production_ready=true"
                        )
            if plan_manifest is None:
                errors.append(
                    f"{object_id}: generated-route objects require plan_manifest.json during staged rollout"
                )
            else:
                planned = find_plan_object(plan_manifest, str(object_id))
                if planned is None:
                    errors.append(
                        f"{object_id}: generated-route objects require a matching plan_manifest object entry"
                    )
                else:
                    if planned.get("planned_route") != "generate":
                        errors.append(
                            f"{object_id}: generated-route objects must use planned_route=generate in plan_manifest.json"
                        )
                    for field_name in [
                        "why_not_extract",
                        "why_not_reconstruct",
                        "why_generate",
                        "risk_note",
                    ]:
                        value = planned.get(field_name)
                        if not isinstance(value, str) or not value.strip():
                            errors.append(
                                f"{object_id}: plan_manifest.{field_name} is required for generated-route objects"
                            )
                    if planned.get("protected_approval_required") is True:
                        approval_ref = planned.get("protected_approval_ref")
                        if not isinstance(approval_ref, str) or not approval_ref.strip():
                            errors.append(
                                f"{object_id}: protected generated-route objects require protected_approval_ref in plan_manifest.json"
                            )
                    attempt_budget = planned.get("attempt_budget")
                    attempts_used = planned.get("attempts_used")
                    if isinstance(attempt_budget, int) and isinstance(attempts_used, int) and attempts_used > attempt_budget:
                        attempt_history = planned.get("attempt_history", [])
                        if not isinstance(attempt_history, list) or not attempt_history:
                            errors.append(
                                f"{object_id}: plan_manifest must record attempt_history when attempts_used exceeds attempt_budget"
                            )
            for field_name in GENERATED_EVIDENCE_FIELDS:
                value = item.get(field_name)
                if field_name == "generation_reference_inputs":
                    if not isinstance(value, list) or not value or not all(
                        isinstance(entry, str) and entry.strip() for entry in value
                    ):
                        errors.append(
                            f"{object_id}: {field_name} must be a non-empty list for generated delivery"
                        )
                else:
                    if not isinstance(value, str) or not value.strip():
                        errors.append(
                            f"{object_id}: {field_name} is required for generated delivery"
                        )
            if delivery_class != "generated-reconstruction":
                errors.append(
                    f"{object_id}: generated-route objects must use delivery_class=generated-reconstruction"
                )
            if reuse_status == "accepted-generated-reconstruction":
                if not promotion_confirmation_satisfied(metadata):
                    errors.append(
                        f"{object_id}: accepted generated delivery requires metadata.confirmation.candidate_promotion to be confirmed"
                    )
                if qa_status == "pass" and item.get("manual_review_confirmed") is not True:
                    errors.append(
                        f"{object_id}: generated reconstructed layers cannot support qa.status pass without manual_review_confirmed=true"
                    )
            if qa_status == "pass" and reuse_status != "accepted-generated-reconstruction":
                errors.append(
                    f"{object_id}: generated delivery requires reuse_status=accepted-generated-reconstruction before qa.status pass"
                )
        composition_order = item.get("composition_order")
        if not isinstance(composition_order, int):
            errors.append(f"{object_id}: composition_order is required for layer stacking")
        for field in ["layer_kind", "semantic_boundary", "mask_source", "alpha_source"]:
            value = item.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{object_id}: {field} is required for segmentation quality evidence")
        quality_checks = item.get("quality_checks")
        if not isinstance(quality_checks, dict):
            errors.append(f"{object_id}: quality_checks must record mask, alpha, edge, and reuse checks")
        else:
            missing_checks = sorted(REQUIRED_OBJECT_QUALITY_CHECKS - set(quality_checks))
            if missing_checks:
                errors.append(
                    f"{object_id}: quality_checks missing required checks: "
                    + ", ".join(missing_checks)
                )
            for check_name, check_value in quality_checks.items():
                if check_value not in ALLOWED_QUALITY_CHECK_STATUSES:
                    errors.append(
                        f"{object_id}: quality_checks.{check_name} must be pass, needs-review, blocked, or unknown"
                    )
                if qa_status == "pass" and check_value != "pass":
                    errors.append(
                        f"{object_id}: qa.status cannot be pass when quality_checks.{check_name} is {check_value}"
                    )
        if qa_status == "pass" and is_crop_only_layer(item) and item.get("manual_review_confirmed") is not True:
            errors.append(
                f"{object_id}: crop-only or estimated layers cannot support qa.status pass "
                "without manual_review_confirmed=true"
            )
        if qa_status == "pass" and is_helper_only_layer(item) and item.get("manual_review_confirmed") is not True:
            errors.append(
                f"{object_id}: helper-only extraction sources cannot support qa.status pass "
                "without manual_review_confirmed=true"
            )
        if is_reconstructed_or_approximate_layer(item):
            provenance = item.get("reconstruction_provenance")
            if not isinstance(provenance, str) or not provenance.strip():
                errors.append(
                    f"{object_id}: approximate or reconstructed layers must record "
                    "reconstruction_provenance"
                )
            active_method = item.get("active_reconstruction_method")
            if not isinstance(active_method, str) or not active_method.strip():
                errors.append(
                    f"{object_id}: approximate or reconstructed layers must record "
                    "active_reconstruction_method"
                )
            if delivery_class != "approximate-reconstruction":
                errors.append(
                    f"{object_id}: approximate or reconstructed layers must use "
                    "delivery_class=approximate-reconstruction"
                )
            if reuse_status == "production-ready":
                errors.append(
                    f"{object_id}: approximate or reconstructed layers must not use reuse_status=production-ready"
                )
            if (
                qa_status == "pass"
                and asset_class in {"atomic", "candidate"}
                and reuse_status not in {
                    "approximate-reconstruction",
                    "accepted-approximate-reconstruction",
                }
            ):
                errors.append(
                    f"{object_id}: approximate reconstructed layers require a pass-eligible approximate reuse_status before qa.status pass"
                )
            if str(item.get("selected_candidate_id", "")).strip():
                accepted = any(
                    isinstance(entry, dict)
                    and str(entry.get("stage", "")).strip() in APPROXIMATE_RECONSTRUCTION_ACCEPTANCE_STAGES
                    and decision_answer(entry)
                    for entry in decision_log
                )
                if not accepted:
                    errors.append(
                        f"{object_id}: promoted approximate reconstruction requires an explicit reconstruction acceptance decision"
                    )
                confirmation_entry = metadata.get("confirmation", {}).get("approximate_reconstruction", {})
                if confirmation_entry.get("status") != "confirmed":
                    errors.append(
                        f"{object_id}: metadata.confirmation.approximate_reconstruction must be confirmed before approximate promotion"
                    )
                elif confirmation_entry.get("source") not in NON_DEFAULT_CONFIRMATION_SOURCES:
                    errors.append(
                        f"{object_id}: metadata.confirmation.approximate_reconstruction must come from explicit-user-confirmed or inferred-from-user"
                    )
                if not promotion_confirmation_satisfied(metadata):
                    errors.append(
                        f"{object_id}: metadata.confirmation.candidate_promotion must be confirmed before candidate promotion"
                    )
            if qa_status == "pass" and item.get("manual_review_confirmed") is not True:
                errors.append(
                    f"{object_id}: approximate reconstructed layers cannot support qa.status pass "
                    "without manual_review_confirmed=true"
                )
        if delivery_class == "approximate-reconstruction" and reuse_status == "production-ready":
            errors.append(
                f"{object_id}: delivery_class=approximate-reconstruction cannot be reported as reuse_status=production-ready"
            )
        if reuse_status == "approximate-reconstruction" and delivery_class != "approximate-reconstruction":
            errors.append(
                f"{object_id}: reuse_status=approximate-reconstruction requires delivery_class=approximate-reconstruction"
            )
        if (
            reuse_status == "accepted-approximate-reconstruction"
            and delivery_class != "approximate-reconstruction"
        ):
            errors.append(
                f"{object_id}: reuse_status=accepted-approximate-reconstruction requires delivery_class=approximate-reconstruction"
            )
        if (
            reuse_status == "accepted-generated-reconstruction"
            and delivery_class != "generated-reconstruction"
        ):
            errors.append(
                f"{object_id}: reuse_status=accepted-generated-reconstruction requires delivery_class=generated-reconstruction"
            )
        text_semantics = item.get(
            "text_semantics",
            {"text_role": "non-text", "text_render_class": "non-text"},
        )
        if not isinstance(text_semantics, dict):
            errors.append(f"{object_id}: text_semantics must be an object when present")
            text_semantics = {"text_role": "non-text", "text_render_class": "non-text"}
        text_role = text_semantics.get("text_role", "non-text")
        if text_role not in ALLOWED_TEXT_ROLES:
            errors.append(
                f"{object_id}: text_semantics.text_role must be one of: "
                + ", ".join(sorted(ALLOWED_TEXT_ROLES))
            )
            text_role = "non-text"
        text_render_class = text_semantics.get("text_render_class", "non-text")
        if text_render_class not in ALLOWED_TEXT_RENDER_CLASSES:
            errors.append(
                f"{object_id}: text_semantics.text_render_class must be one of: "
                + ", ".join(sorted(ALLOWED_TEXT_RENDER_CLASSES))
            )
            text_render_class = "non-text"
        value_scoring = item.get(
            "value_scoring",
            {
                "editability_score": "unset",
                "visual_complexity_score": "unset",
                "asset_value_score": "unset",
                "scoring_reason": "",
            },
        )
        if not isinstance(value_scoring, dict):
            errors.append(f"{object_id}: value_scoring must be an object when present")
            value_scoring = {}
        for field_name in [
            "editability_score",
            "visual_complexity_score",
            "asset_value_score",
        ]:
            score_value = value_scoring.get(field_name, "unset")
            if score_value not in ALLOWED_SCORE_VALUES:
                errors.append(
                    f"{object_id}: value_scoring.{field_name} must be one of: "
                    + ", ".join(sorted(ALLOWED_SCORE_VALUES))
                )
        scoring_reason = value_scoring.get("scoring_reason", "")
        if not isinstance(scoring_reason, str):
            errors.append(f"{object_id}: value_scoring.scoring_reason must be a string")
        decision_routing = item.get(
            "decision_routing",
            {
                "recommended_action": "unset",
                "final_action": "unset",
                "decision_source": "unset",
            },
        )
        if not isinstance(decision_routing, dict):
            errors.append(f"{object_id}: decision_routing must be an object when present")
            decision_routing = {}
        recommended_action = decision_routing.get("recommended_action", "unset")
        if recommended_action not in ALLOWED_ROUTING_ACTIONS:
            errors.append(
                f"{object_id}: decision_routing.recommended_action must be one of: "
                + ", ".join(sorted(ALLOWED_ROUTING_ACTIONS))
            )
            recommended_action = "unset"
        final_action = decision_routing.get("final_action", "unset")
        if final_action not in ALLOWED_ROUTING_ACTIONS:
            errors.append(
                f"{object_id}: decision_routing.final_action must be one of: "
                + ", ".join(sorted(ALLOWED_ROUTING_ACTIONS))
            )
            final_action = "unset"
        routing_source = decision_routing.get("decision_source", "unset")
        if routing_source not in ALLOWED_ROUTING_DECISION_SOURCES:
            errors.append(
                f"{object_id}: decision_routing.decision_source must be one of: "
                + ", ".join(sorted(ALLOWED_ROUTING_DECISION_SOURCES))
            )
            routing_source = "unset"
        if (recommended_action != "unset" or final_action != "unset") and routing_source == "unset":
            errors.append(
                f"{object_id}: decision_routing.decision_source is required when routing actions are set"
            )
        rebuild_intent = item.get(
            "rebuild_intent",
            {
                "rebuildable_downstream": False,
                "rebuild_notes": "",
            },
        )
        if not isinstance(rebuild_intent, dict):
            errors.append(f"{object_id}: rebuild_intent must be an object when present")
            rebuild_intent = {}
        rebuildable_downstream = rebuild_intent.get("rebuildable_downstream", False)
        if not isinstance(rebuildable_downstream, bool):
            errors.append(f"{object_id}: rebuild_intent.rebuildable_downstream must be true or false")
        rebuild_notes = rebuild_intent.get("rebuild_notes", "")
        if not isinstance(rebuild_notes, str):
            errors.append(f"{object_id}: rebuild_intent.rebuild_notes must be a string")
        if (
            text_role in ORDINARY_TEXT_ROLES
            and text_render_class != "visual-fidelity-critical"
            and final_action == "extract_asset"
        ):
            errors.append(
                f"{object_id}: ordinary editable text-like content must not default to extract_asset"
            )
        if recommended_action == "requires_user_confirmation" and not has_text_routing_confirmation(
            item,
            decision_log,
            allow_legacy_unscoped=len(requires_confirmation_ids) == 1,
        ):
            errors.append(
                f"{object_id}: requires_user_confirmation must be resolved through a formal decision record"
            )
        if recommended_action == "requires_user_confirmation" and final_action not in {
            "extract_asset",
            "rebuild_downstream",
            "support_only",
        }:
            errors.append(
                f"{object_id}: requires_user_confirmation must resolve decision_routing.final_action before validation"
            )
        if (
            final_action == "rebuild_downstream"
            and asset_class == "atomic"
            and reuse_status == "production-ready"
        ):
            errors.append(
                f"{object_id}: rebuild_downstream cannot publish a production raster asset"
            )
        current_revision = item.get("current_asset_revision")
        if not isinstance(current_revision, str) or not current_revision.strip():
            errors.append(f"{object_id}: current_asset_revision is required")
        selected_candidate_id = item.get("selected_candidate_id")
        if selected_candidate_id is not None and not isinstance(selected_candidate_id, str):
            errors.append(f"{object_id}: selected_candidate_id must be a string when present")
        selected_candidate_id_value = (
            str(selected_candidate_id).strip() if isinstance(selected_candidate_id, str) else ""
        )
        if selected_candidate_id_value:
            if not promotion_confirmation_satisfied(metadata):
                errors.append(
                    f"{object_id}: metadata.confirmation.candidate_promotion must be confirmed before candidate promotion"
                )
        repair_history = item.get("repair_history")
        if repair_history is not None and not isinstance(repair_history, list):
            errors.append(f"{object_id}: repair_history must be a list when present")
        candidate_comparisons = item.get("candidate_comparisons")
        if candidate_comparisons is not None and not isinstance(candidate_comparisons, list):
            errors.append(f"{object_id}: candidate_comparisons must be a list when present")
            candidate_comparisons = []
        if requires_candidate_comparison_evidence(item):
            if not candidate_comparisons:
                errors.append(
                    f"{object_id}: high-risk repair or promoted candidates require candidate_comparisons evidence"
                )
            else:
                selected_candidate_id = str(item.get("selected_candidate_id", "")).strip()
                matching_comparison_found = False
                for index, comparison in enumerate(candidate_comparisons):
                    if not isinstance(comparison, dict):
                        errors.append(f"{object_id}: candidate_comparisons[{index}] must be an object")
                        continue
                    missing = sorted(REQUIRED_CANDIDATE_COMPARISON_FIELDS - set(comparison))
                    if missing:
                        errors.append(
                            f"{object_id}: candidate_comparisons[{index}] missing required fields: "
                            + ", ".join(missing)
                        )
                        continue
                    candidate_ids = comparison.get("candidate_ids")
                    if not isinstance(candidate_ids, list) or not all(
                        isinstance(candidate_id, str) and candidate_id.strip() for candidate_id in candidate_ids
                    ):
                        errors.append(
                            f"{object_id}: candidate_comparisons[{index}].candidate_ids must be a list of non-empty strings"
                        )
                        continue
                    artifact_path = comparison.get("compare_artifact_path")
                    if not isinstance(artifact_path, str):
                        errors.append(
                            f"{object_id}: candidate_comparisons[{index}].compare_artifact_path must be a string"
                        )
                    elif artifact_path:
                        if not artifact_path.startswith("_staging/") and not artifact_path.startswith(
                            "_archive_intermediate/"
                        ):
                            errors.append(
                                f"{object_id}: candidate_comparisons[{index}].compare_artifact_path must stay in _staging/ or _archive_intermediate/"
                            )
                        else:
                            resolved_artifact = rel_path(
                                package_dir,
                                artifact_path,
                                errors,
                                f"{object_id}: candidate_comparisons[{index}].compare_artifact_path",
                            )
                            if resolved_artifact is not None and not resolved_artifact.exists():
                                errors.append(
                                    f"{object_id}: candidate comparison artifact is missing: {artifact_path}"
                                )
                    manifest_path = comparison.get("compare_manifest_path")
                    if not isinstance(manifest_path, str) or not manifest_path.strip():
                        errors.append(
                            f"{object_id}: candidate_comparisons[{index}].compare_manifest_path must be a non-empty string"
                        )
                    elif not manifest_path.startswith("_staging/") and not manifest_path.startswith(
                        "_archive_intermediate/"
                    ):
                        errors.append(
                            f"{object_id}: candidate_comparisons[{index}].compare_manifest_path must stay in _staging/ or _archive_intermediate/"
                        )
                    else:
                        resolved_manifest = rel_path(
                            package_dir,
                            manifest_path,
                            errors,
                            f"{object_id}: candidate_comparisons[{index}].compare_manifest_path",
                        )
                        if resolved_manifest is not None:
                            if not resolved_manifest.exists():
                                errors.append(
                                    f"{object_id}: candidate comparison manifest is missing: {manifest_path}"
                                )
                            else:
                                try:
                                    manifest_data = json.loads(
                                        resolved_manifest.read_text(encoding="utf-8")
                                    )
                                except json.JSONDecodeError as exc:
                                    errors.append(
                                        f"{object_id}: candidate comparison manifest is not valid JSON: {exc}"
                                    )
                                else:
                                    if not isinstance(manifest_data, dict):
                                        errors.append(
                                            f"{object_id}: candidate comparison manifest must contain an object"
                                        )
                                    else:
                                        manifest_criteria = manifest_data.get("compare_criteria")
                                        if not isinstance(manifest_criteria, list) or not manifest_criteria:
                                            errors.append(
                                                f"{object_id}: candidate comparison manifest must record non-empty compare_criteria"
                                            )
                                        candidates_block = manifest_data.get("candidates")
                                        if not isinstance(candidates_block, list) or not candidates_block:
                                            errors.append(
                                                f"{object_id}: candidate comparison manifest must record candidates with asset_path"
                                            )
                                        else:
                                            for manifest_candidate in candidates_block:
                                                if not isinstance(manifest_candidate, dict):
                                                    errors.append(
                                                        f"{object_id}: candidate comparison manifest candidates must be objects"
                                                    )
                                                    continue
                                                asset_candidate_path = manifest_candidate.get("asset_path")
                                                if not isinstance(asset_candidate_path, str) or not asset_candidate_path.strip():
                                                    errors.append(
                                                        f"{object_id}: candidate comparison manifest candidates must include asset_path"
                                                    )
                                        if "review_focus" not in manifest_data:
                                            errors.append(
                                                f"{object_id}: candidate comparison manifest must record review_focus"
                                            )
                                        if "risks" not in manifest_data:
                                            errors.append(
                                                f"{object_id}: candidate comparison manifest must record risks"
                                            )
                                        score_manifest_path = comparison.get("score_manifest_path", "")
                                        if score_manifest_path:
                                            if not isinstance(score_manifest_path, str):
                                                errors.append(
                                                    f"{object_id}: candidate_comparisons[{index}].score_manifest_path must be a string"
                                                )
                                            elif not score_manifest_path.startswith("_staging/") and not score_manifest_path.startswith(
                                                "_archive_intermediate/"
                                            ):
                                                errors.append(
                                                    f"{object_id}: candidate_comparisons[{index}].score_manifest_path must stay in _staging/ or _archive_intermediate/"
                                                )
                                            else:
                                                resolved_score_manifest = rel_path(
                                                    package_dir,
                                                    score_manifest_path,
                                                    errors,
                                                    f"{object_id}: candidate_comparisons[{index}].score_manifest_path",
                                                )
                                                if resolved_score_manifest is not None:
                                                    if not resolved_score_manifest.exists():
                                                        errors.append(
                                                            f"{object_id}: score manifest is missing: {score_manifest_path}"
                                                        )
                                                    else:
                                                        try:
                                                            score_manifest = json.loads(
                                                                resolved_score_manifest.read_text(encoding="utf-8")
                                                            )
                                                        except json.JSONDecodeError as exc:
                                                            errors.append(
                                                                f"{object_id}: score manifest is not valid JSON: {exc}"
                                                            )
                                                        else:
                                                            if not isinstance(score_manifest, dict):
                                                                errors.append(
                                                                    f"{object_id}: score manifest must contain an object"
                                                                )
                                                            else:
                                                                candidates_block = score_manifest.get("candidates")
                                                                if not isinstance(candidates_block, list) or not candidates_block:
                                                                    errors.append(
                                                                        f"{object_id}: score manifest must list scored candidates"
                                                                    )
                                                                else:
                                                                    for scored_candidate in candidates_block:
                                                                        if not isinstance(scored_candidate, dict):
                                                                            errors.append(
                                                                                f"{object_id}: score manifest candidates must be objects"
                                                                            )
                                                                            continue
                                                                        scores = scored_candidate.get("scores")
                                                                        if not isinstance(scores, dict):
                                                                            errors.append(
                                                                                f"{object_id}: score manifest candidates must include scores"
                                                                            )
                                                                            continue
                                                                        for score_key in [
                                                                            "edge_touch_risk",
                                                                            "detached_fragment_risk",
                                                                            "carrier_residue_risk",
                                                                            "glyph_residue_risk",
                                                                            "border_preservation_score",
                                                                            "texture_match_score",
                                                                            "flatness_risk",
                                                                            "style_mismatch_risk",
                                                                        ]:
                                                                            if score_key not in scores:
                                                                                errors.append(
                                                                                    f"{object_id}: score manifest candidates missing {score_key}"
                                                                                )
                    selection_reason = comparison.get("selection_reason")
                    if not isinstance(selection_reason, str):
                        errors.append(
                            f"{object_id}: candidate_comparisons[{index}].selection_reason must be a string"
                        )
                    selected_in_entry = str(comparison.get("selected_candidate_id", "")).strip()
                    if selected_candidate_id and selected_in_entry == selected_candidate_id:
                        matching_comparison_found = True
                        if not selection_reason.strip():
                            errors.append(
                                f"{object_id}: selected candidate comparison must record a non-empty selection_reason"
                            )
                        if selected_candidate_id not in candidate_ids:
                            errors.append(
                                f"{object_id}: selected_candidate_id must appear in the matching candidate comparison"
                            )
                        if not artifact_path and len(candidate_ids) > 1:
                            errors.append(
                                f"{object_id}: multi-candidate promotion requires compare_artifact_path evidence"
                            )
                if selected_candidate_id and not matching_comparison_found:
                    errors.append(
                        f"{object_id}: selected_candidate_id requires a matching candidate comparison record"
                    )

    if ui_like_package and granularity.get("carrier_glyph_policy") == "split" and has_carrier and not has_glyph:
        errors.append(
            "metadata.granularity.carrier_glyph_policy=split requires at least one glyph layer when carrier layers are present"
        )


