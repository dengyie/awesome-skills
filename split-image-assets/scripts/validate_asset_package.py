import argparse
import json
import sys
from pathlib import Path

from PIL import Image

from split_image_assets_contract import (
    ALLOWED_ASSET_CLASSES,
    ALLOWED_BLOCKING_VALUES,
    ALLOWED_CAPABILITY_CHOICES,
    ALLOWED_CARRIER_GLYPH_POLICIES,
    ALLOWED_CONFIRMATION_SOURCES,
    ALLOWED_CONFIRMATION_STATUSES,
    ALLOWED_DECISION_SOURCES,
    ALLOWED_DELIVERY_CLASSES,
    ALLOWED_GRANULARITY_MODES,
    ALLOWED_LAYER_INDEPENDENCE,
    ALLOWED_OBJECT_TYPES,
    ALLOWED_PAUSE_CATEGORIES,
    ALLOWED_QA_STATUSES,
    ALLOWED_QUALITY_CHECK_STATUSES,
    ALLOWED_QUALITY_TARGET_TIERS,
    ALLOWED_REUSE_STATUSES,
    ALLOWED_ROUTING_ACTIONS,
    ALLOWED_ROUTING_DECISION_SOURCES,
    ALLOWED_SCORE_VALUES,
    ALLOWED_SCOPE_STRATEGIES,
    ALLOWED_TEXT_HANDLING,
    ALLOWED_TEXT_RENDER_CLASSES,
    ALLOWED_TEXT_ROLES,
    ALLOWED_BACKGROUND_EXPECTATIONS,
    NON_DEFAULT_CONFIRMATION_SOURCES,
    ORDINARY_TEXT_ROLES,
    REQUIRED_CONFIRMATION_KEYS,
)


OBJECT_ASSET_ROLES = {"main", "secondary", "group", "background", "shadow"}
REQUIRED_PIPELINE_STAGES = {
    "semantic-analysis",
    "segmentation",
    "alpha-refinement",
    "layer-packaging",
    "qa-review",
}
REQUIRED_OBJECT_QUALITY_CHECKS = {
    "mask_alignment",
    "alpha_edges",
    "background_residue",
    "reuse_readiness",
}
CROP_ONLY_MARKERS = {"bbox", "crop", "manual-estimated crop", "manual-estimated-crop"}
ALLOWED_ROOT_DIRECTORIES = {
    "source",
    "assets",
    "masks",
    "previews",
    "_staging",
    "_archive_intermediate",
}
ALLOWED_ROOT_FILES = {"metadata.json", "qa_report.md", "asset_manifest.json"}
RECONSTRUCTION_MARKERS = {"reconstruct", "reconstructed", "reconstruction", "inpaint", "clean plate"}
HELPER_ONLY_MARKERS = {"pillow", "opencv", "skimage", "threshold"}
REQUIRED_DECISION_FIELDS = {
    "stage",
    "pause_category",
    "question",
    "recommended_answer",
    "decision_effect",
    "decision_source",
    "evidence_ref",
    "blocking",
}
REQUIRED_NONEMPTY_DECISION_FIELDS = REQUIRED_DECISION_FIELDS - {"evidence_ref"}
DECISION_ANSWER_FIELDS = ("recorded_answer", "user_answer")
REQUIRED_ASSET_SUMMARY_FIELDS = {
    "production_ready_assets",
    "draft_candidate_assets",
    "support_only_layers",
    "blocked_assets",
}
REQUIRED_CANDIDATE_COMPARISON_FIELDS = {
    "comparison_id",
    "object_id",
    "candidate_ids",
    "compare_artifact_path",
    "compare_manifest_path",
    "review_focus",
    "risks",
    "selected_candidate_id",
    "selection_reason",
    "created_at",
}
ALLOWED_AUDIT_CODES = {
    "edge-halo",
    "color-residue",
    "detached-fragments",
    "smear-artifact",
    "over-flat-reconstruction",
    "style-mismatch-reconstruction",
    "hard-alpha-risk",
    "support-layer-misclassified",
    "carrier-glyph-cross-contamination",
}
APPROXIMATE_RECONSTRUCTION_ACCEPTANCE_STAGES = {
    "approximate-reconstruction-acceptance",
    "approximate-reconstruction-acceptance-gate",
    "reconstruction-acceptance",
}
AFFIRMATIVE_DECISION_ANSWERS = {"yes", "y", "accept", "accepted", "approve", "approved", "confirm", "confirmed"}
TEXT_ROUTING_CONFIRMATION_STAGES = {
    "asset-value-scoring",
    "asset-routing",
    "asset-routing-confirmation",
    "text-routing",
    "text-routing-confirmation",
}
TEXT_ROUTING_CONFIRMATION_MARKERS = {
    "rebuild downstream",
    "visual asset",
    "text-like object",
    "fidelity-critical",
}


def rel_path(package_dir: Path, value: str, errors: list[str], label: str) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} must be a package-relative path")
        return None
    raw_path = Path(value)
    if raw_path.is_absolute():
        errors.append(f"{label} must stay inside the package: {value}")
        return None
    resolved = (package_dir / raw_path).resolve()
    package_root = package_dir.resolve()
    if resolved != package_root and package_root not in resolved.parents:
        errors.append(f"{label} must stay inside the package: {value}")
        return None
    return resolved


def is_affirmative_answer(value: object) -> bool:
    return isinstance(value, str) and value.strip().lower() in AFFIRMATIVE_DECISION_ANSWERS


def has_affirmative_decision(decision_log: list[dict], stages: set[str]) -> bool:
    return any(
        isinstance(entry, dict)
        and str(entry.get("stage", "")).strip() in stages
        and is_affirmative_answer(decision_answer(entry))
        for entry in decision_log
    )


def confirmation_satisfies_promotion(metadata: dict, key: str) -> bool:
    entry = metadata.get("confirmation", {}).get(key, {})
    return (
        isinstance(entry, dict)
        and entry.get("status") == "confirmed"
        and entry.get("source") in NON_DEFAULT_CONFIRMATION_SOURCES
    )


def promotion_confirmation_satisfied(metadata: dict) -> bool:
    return confirmation_satisfies_promotion(metadata, "candidate_promotion") or confirmation_satisfies_promotion(
        metadata, "final_promotion_acceptance"
    )


def load_metadata(package_dir: Path, errors: list[str]) -> dict:
    metadata_path = package_dir / "metadata.json"
    if not metadata_path.exists():
        errors.append("metadata.json is missing")
        return {}
    try:
        return json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"metadata.json is not valid JSON: {exc}")
        return {}


def validate_required_layout(package_dir: Path, errors: list[str]) -> None:
    for directory in ["source", "assets", "masks", "previews"]:
        if not (package_dir / directory).is_dir():
            errors.append(f"required directory is missing: {directory}/")
    for filename in ["metadata.json", "qa_report.md"]:
        if not (package_dir / filename).exists():
            errors.append(f"required file is missing: {filename}")
    root_children = package_dir.iterdir() if package_dir.exists() else []
    for child in root_children:
        if child.is_dir():
            if child.name not in ALLOWED_ROOT_DIRECTORIES and not child.name.startswith("_"):
                errors.append(
                    f"unarchived intermediate directory in package root: {child.name}; "
                    "move external model outputs into _staging/ or _archive_intermediate/"
                )
        elif child.is_file() and child.name not in ALLOWED_ROOT_FILES:
            errors.append(
                f"unexpected file in package root: {child.name}; "
                "move temporary manifests into _staging/ or _archive_intermediate/"
            )


def validate_metadata_fields(metadata: dict, errors: list[str]) -> None:
    for field in [
        "schema_version",
        "package_name",
        "source",
        "analysis",
        "extraction_pipeline",
        "objects",
        "asset_summary",
        "audit",
        "qa",
    ]:
        if field not in metadata:
            errors.append(f"metadata missing required field: {field}")
    source = metadata.get("source", {})
    if not isinstance(source, dict):
        errors.append("metadata.source must be an object")
        source = {}
    for field in ["path", "width", "height"]:
        if field not in source:
            errors.append(f"metadata.source missing required field: {field}")
    analysis = metadata.get("analysis", {})
    if not isinstance(analysis, dict):
        errors.append("metadata.analysis must be an object")
        analysis = {}
    visual_hierarchy = analysis.get("visual_hierarchy")
    if not isinstance(visual_hierarchy, list) or not visual_hierarchy:
        errors.append("metadata.analysis.visual_hierarchy must include a semantic visual hierarchy")
    split_plan = analysis.get("recommended_split_plan")
    if not isinstance(split_plan, str) or not split_plan.strip():
        errors.append("metadata.analysis.recommended_split_plan must describe semantic layer boundaries")
    granularity = metadata.get("granularity", {})
    if not isinstance(granularity, dict):
        errors.append("metadata.granularity must be an object")
        granularity = {}
    mode = granularity.get("mode")
    if mode not in ALLOWED_GRANULARITY_MODES:
        errors.append("metadata.granularity.mode must record the agreed split granularity")
    user_confirmed = granularity.get("user_confirmed")
    if not isinstance(user_confirmed, bool):
        errors.append("metadata.granularity.user_confirmed must be true or false")
    elif user_confirmed is not True:
        errors.append("metadata.granularity.user_confirmed must be true before validation")
    notes = granularity.get("notes")
    if not isinstance(notes, str):
        errors.append("metadata.granularity.notes must be a string")
    elif not notes.strip():
        errors.append("metadata.granularity.notes must explain the aligned split scope")
    for field_name, allowed in [
        ("scope_strategy", ALLOWED_SCOPE_STRATEGIES),
        ("text_handling", ALLOWED_TEXT_HANDLING),
        ("carrier_glyph_policy", ALLOWED_CARRIER_GLYPH_POLICIES),
        ("background_expectation", ALLOWED_BACKGROUND_EXPECTATIONS),
        ("layer_independence", ALLOWED_LAYER_INDEPENDENCE),
    ]:
        value = granularity.get(field_name, "unset")
        if value not in allowed:
            errors.append(f"metadata.granularity.{field_name} must be one of: {', '.join(sorted(allowed))}")
    decision_log = metadata.get("decision_log", [])
    if not isinstance(decision_log, list):
        errors.append("metadata.decision_log must be a list")
    else:
        for index, entry in enumerate(decision_log):
            if not isinstance(entry, dict):
                errors.append(f"metadata.decision_log[{index}] must be an object")
                continue
            missing = sorted(REQUIRED_DECISION_FIELDS - set(entry))
            if not any(field_name in entry for field_name in DECISION_ANSWER_FIELDS):
                missing.append("recorded_answer")
            if missing:
                errors.append(
                    f"metadata.decision_log[{index}] missing required fields: "
                    + ", ".join(missing)
                )
            for field in REQUIRED_NONEMPTY_DECISION_FIELDS:
                value = entry.get(field)
                if value is not None and (not isinstance(value, str) or not value.strip()):
                    errors.append(f"metadata.decision_log[{index}].{field} must be a non-empty string")
            evidence_ref = entry.get("evidence_ref")
            if evidence_ref is not None and not isinstance(evidence_ref, str):
                errors.append(f"metadata.decision_log[{index}].evidence_ref must be a string")
            if not decision_answer(entry):
                errors.append(
                    f"metadata.decision_log[{index}].recorded_answer must be a non-empty string"
                )
            decision_source = entry.get("decision_source")
            if decision_source not in ALLOWED_DECISION_SOURCES:
                errors.append(
                    f"metadata.decision_log[{index}].decision_source must be one of: "
                    + ", ".join(sorted(ALLOWED_DECISION_SOURCES))
                )
            pause_category = entry.get("pause_category")
            if pause_category not in ALLOWED_PAUSE_CATEGORIES:
                errors.append(
                    f"metadata.decision_log[{index}].pause_category must be one of: "
                    + ", ".join(sorted(ALLOWED_PAUSE_CATEGORIES))
                )
            blocking = entry.get("blocking")
            if blocking not in ALLOWED_BLOCKING_VALUES:
                errors.append(
                    f"metadata.decision_log[{index}].blocking must be one of: "
                    + ", ".join(sorted(ALLOWED_BLOCKING_VALUES))
                )
            if decision_source == "inferred-from-user":
                if not isinstance(evidence_ref, str) or not evidence_ref.strip():
                    errors.append(
                        f"metadata.decision_log[{index}].evidence_ref is required when decision_source=inferred-from-user"
                    )
    qa = metadata.get("qa", {})
    qa_status = qa.get("status") if isinstance(qa, dict) else None
    if qa_status == "pass" and not decision_log:
        errors.append(
            "qa.status pass requires at least one decision_log entry documenting user acceptance"
        )
    confirmation = metadata.get("confirmation", {})
    if not isinstance(confirmation, dict):
        errors.append("metadata.confirmation must be an object")
        confirmation = {}
    missing_confirmation = sorted(REQUIRED_CONFIRMATION_KEYS - set(confirmation))
    if missing_confirmation:
        errors.append(
            "metadata.confirmation missing required gates: " + ", ".join(missing_confirmation)
        )
    else:
        for key in REQUIRED_CONFIRMATION_KEYS:
            entry = confirmation.get(key)
            if not isinstance(entry, dict):
                errors.append(f"metadata.confirmation.{key} must be an object")
                continue
            status = entry.get("status")
            source = entry.get("source")
            notes = entry.get("notes")
            pause_category = entry.get("pause_category", "")
            evidence_ref = entry.get("evidence_ref", "")
            if status not in ALLOWED_CONFIRMATION_STATUSES:
                errors.append(
                    f"metadata.confirmation.{key}.status must be one of: "
                    + ", ".join(sorted(ALLOWED_CONFIRMATION_STATUSES))
                )
            if source not in ALLOWED_CONFIRMATION_SOURCES:
                errors.append(
                    f"metadata.confirmation.{key}.source must be one of: "
                    + ", ".join(sorted(ALLOWED_CONFIRMATION_SOURCES))
                )
            if not isinstance(notes, str):
                errors.append(f"metadata.confirmation.{key}.notes must be a string")
            if not isinstance(evidence_ref, str):
                errors.append(f"metadata.confirmation.{key}.evidence_ref must be a string")
            if status in {"confirmed", "not-required"}:
                if source not in NON_DEFAULT_CONFIRMATION_SOURCES:
                    errors.append(
                        f"metadata.confirmation.{key}.source must come from explicit-user-confirmed or inferred-from-user"
                    )
                if pause_category not in ALLOWED_PAUSE_CATEGORIES:
                    errors.append(
                        f"metadata.confirmation.{key}.pause_category must be one of: "
                        + ", ".join(sorted(ALLOWED_PAUSE_CATEGORIES))
                    )
                if source == "inferred-from-user" and not evidence_ref.strip():
                    errors.append(
                        f"metadata.confirmation.{key}.evidence_ref is required when source=inferred-from-user"
                    )
            if status == "pending" and source != "unset":
                errors.append(
                    f"metadata.confirmation.{key}.source must be unset when status=pending"
                )
            if key == "pilot_object":
                object_id = entry.get("object_id")
                if not isinstance(object_id, str):
                    errors.append("metadata.confirmation.pilot_object.object_id must be a string")
                elif status == "confirmed" and not object_id.strip():
                    errors.append(
                        "metadata.confirmation.pilot_object.object_id must be non-empty when the pilot gate is confirmed"
                    )
    asset_summary = metadata.get("asset_summary")
    if not isinstance(asset_summary, dict):
        errors.append("metadata.asset_summary must be an object")
        asset_summary = {}
    missing_summary = sorted(REQUIRED_ASSET_SUMMARY_FIELDS - set(asset_summary))
    if missing_summary:
        errors.append(
            "metadata.asset_summary missing required fields: " + ", ".join(missing_summary)
        )
    for field in REQUIRED_ASSET_SUMMARY_FIELDS & set(asset_summary):
        value = asset_summary.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            errors.append(f"metadata.asset_summary.{field} must be a non-negative integer")
    audit = metadata.get("audit", {})
    if not isinstance(audit, dict):
        errors.append("metadata.audit must be an object")
    elif audit:
        quality_audit_path = audit.get("quality_audit_path")
        if not isinstance(quality_audit_path, str) or not quality_audit_path.strip():
            errors.append("metadata.audit.quality_audit_path must be a package-relative path")
        elif not quality_audit_path.startswith("_staging/") and not quality_audit_path.startswith(
            "_archive_intermediate/"
        ):
            errors.append(
                "metadata.audit.quality_audit_path must stay in _staging/ or _archive_intermediate/"
            )
        warning_codes = audit.get("warning_codes", [])
        if not isinstance(warning_codes, list) or not all(
            isinstance(code, str) and code in ALLOWED_AUDIT_CODES for code in warning_codes
        ):
            errors.append(
                "metadata.audit.warning_codes must use the supported visual warning taxonomy"
            )
    capability = metadata.get("capability", {})
    if not isinstance(capability, dict):
        errors.append("metadata.capability must be an object")
        capability = {}
    production_capable = capability.get("production_capable")
    if not isinstance(production_capable, bool):
        errors.append("metadata.capability.production_capable must be true or false")
    missing_for_production = capability.get("missing_for_production")
    if not isinstance(missing_for_production, list) or not all(
        isinstance(item, str) and item.strip() for item in missing_for_production
    ):
        errors.append("metadata.capability.missing_for_production must be a list of non-empty strings")
    user_choice = capability.get("user_choice")
    if user_choice not in ALLOWED_CAPABILITY_CHOICES:
        errors.append("metadata.capability.user_choice must record the tooling preflight decision")
    notes = capability.get("notes")
    if not isinstance(notes, str):
        errors.append("metadata.capability.notes must be a string")
    qa_for_capability = metadata.get("qa", {})
    qa_status_for_capability = (
        qa_for_capability.get("status") if isinstance(qa_for_capability, dict) else None
    )
    if qa_status_for_capability == "pass" and user_choice == "unset":
        errors.append(
            "metadata.capability.user_choice must not stay unset when qa.status=pass"
        )
    if qa_status_for_capability == "pass" and production_capable is not True:
        errors.append(
            "qa.status pass requires metadata.capability.production_capable=true; "
            "draft-packaging-only or unrecorded tooling preflight must remain needs-review"
        )
    tooling_confirmation = confirmation.get("tooling_preflight", {}) if isinstance(confirmation, dict) else {}
    if capability.get("user_choice") != "unset":
        if tooling_confirmation.get("status") != "confirmed":
            errors.append("metadata.confirmation.tooling_preflight must be confirmed before validation")
        elif tooling_confirmation.get("source") not in NON_DEFAULT_CONFIRMATION_SOURCES:
            errors.append(
                "metadata.confirmation.tooling_preflight must come from explicit-user-confirmed or inferred-from-user"
            )
    quality_target = metadata.get("quality_target", {})
    if not isinstance(quality_target, dict):
        errors.append("metadata.quality_target must be an object")
    else:
        if quality_target.get("tier") not in ALLOWED_QUALITY_TARGET_TIERS:
            errors.append(
                "metadata.quality_target.tier must be one of: "
                + ", ".join(sorted(ALLOWED_QUALITY_TARGET_TIERS))
            )
        notes = quality_target.get("notes")
        if not isinstance(notes, str):
            errors.append("metadata.quality_target.notes must be a string")
    if qa_status_for_capability == "pass" and quality_target.get("tier") != "visual-acceptance-ready":
        errors.append(
            "qa.status pass requires metadata.quality_target.tier=visual-acceptance-ready"
        )
    if qa_status_for_capability == "pass":
        for key in ["granularity_alignment", "final_acceptance"]:
            entry = confirmation.get(key, {}) if isinstance(confirmation, dict) else {}
            if entry.get("status") != "confirmed":
                errors.append(f"metadata.confirmation.{key} must be confirmed before qa.status=pass")
            elif entry.get("source") not in NON_DEFAULT_CONFIRMATION_SOURCES:
                errors.append(
                    f"metadata.confirmation.{key} must come from explicit-user-confirmed or inferred-from-user before qa.status=pass"
                )
        if not has_affirmative_decision(
            decision_log,
            {"final-acceptance", "final-package-acceptance"},
        ):
            errors.append(
                "qa.status pass requires an affirmative final acceptance decision_log entry"
            )
    qa = metadata.get("qa", {})
    if not isinstance(qa, dict):
        errors.append("metadata.qa must be an object")
        qa = {}
    if "status" not in qa:
        errors.append("metadata.qa missing required field: status")
    elif qa.get("status") not in ALLOWED_QA_STATUSES:
        errors.append("metadata.qa.status must be pass, needs-review, or blocked")


def validate_extraction_pipeline(metadata: dict, errors: list[str]) -> None:
    pipeline = metadata.get("extraction_pipeline", {})
    if not isinstance(pipeline, dict):
        errors.append("metadata.extraction_pipeline must be an object")
        return
    recipe = pipeline.get("recipe")
    if not isinstance(recipe, str) or not recipe.strip():
        errors.append("metadata.extraction_pipeline.recipe must name the selected pipeline recipe")
    stages = pipeline.get("stages")
    if not isinstance(stages, list) or not all(isinstance(stage, str) for stage in stages):
        errors.append("metadata.extraction_pipeline.stages must list ordered pipeline stages")
        stages = []
    missing_stages = sorted(REQUIRED_PIPELINE_STAGES - set(stages))
    if missing_stages:
        errors.append(
            "metadata.extraction_pipeline.stages missing required stages: "
            + ", ".join(missing_stages)
        )
    quality_gates = pipeline.get("quality_gates")
    if not isinstance(quality_gates, list) or not quality_gates:
        errors.append("metadata.extraction_pipeline.quality_gates must list segmentation quality gates")
    tools = pipeline.get("tools")
    if not isinstance(tools, list) or not tools:
        errors.append("metadata.extraction_pipeline.tools must record upstream tool provenance")
    else:
        for tool in tools:
            if not isinstance(tool, dict):
                errors.append(
                    "metadata.extraction_pipeline.tools entries must include name, role, and version"
                )
                continue
            for field in ["name", "role", "version"]:
                value = tool.get(field)
                if not isinstance(value, str) or not value.strip():
                    errors.append(
                        "metadata.extraction_pipeline.tools entries must include name, role, and version"
                    )
                    break


def image_mode(path: Path, errors: list[str]) -> str | None:
    try:
        with Image.open(path) as image:
            return image.mode
    except OSError as exc:
        errors.append(f"image cannot be opened: {path}: {exc}")
        return None


def image_size(path: Path, errors: list[str]) -> tuple[int, int] | None:
    try:
        with Image.open(path) as image:
            return image.size
    except OSError as exc:
        errors.append(f"image cannot be opened: {path}: {exc}")
        return None


def has_alpha(mode: str) -> bool:
    return mode in {"RGBA", "LA"} or mode == "PA"


def is_crop_only_layer(item: dict) -> bool:
    mask_source = str(item.get("mask_source", "")).strip().lower()
    extraction_method = str(item.get("extraction_method", "")).strip().lower()
    return (
        mask_source in CROP_ONLY_MARKERS
        or "bbox" in mask_source
        or "crop" in mask_source
        or extraction_method in {"estimated", "unknown"}
    )


def is_reconstructed_or_approximate_layer(item: dict) -> bool:
    if item.get("approximate") is True:
        return True
    values = [
        item.get("mask_source", ""),
        item.get("alpha_source", ""),
        item.get("extraction_method", ""),
        item.get("layer_kind", ""),
    ]
    text = " ".join(str(value).lower() for value in values)
    return any(marker in text for marker in RECONSTRUCTION_MARKERS)


def decision_answer(entry: dict) -> str:
    for field_name in DECISION_ANSWER_FIELDS:
        value = entry.get(field_name)
        if isinstance(value, str) and value.strip():
            return value
    return ""


def is_helper_only_layer(item: dict) -> bool:
    values = [item.get("mask_source", ""), item.get("alpha_source", "")]
    text = " ".join(str(value).lower() for value in values)
    return any(marker in text for marker in HELPER_ONLY_MARKERS)


def is_ui_like_package(metadata: dict) -> bool:
    markers = {
        "ui",
        "panel",
        "badge",
        "tile",
        "glyph",
        "control",
        "label",
        "frame",
        "menu",
        "tab",
        "checkbox",
        "toggle",
        "chart",
        "chrome",
        "support-plate",
    }
    analysis = metadata.get("analysis", {})
    if isinstance(analysis, dict):
        hierarchy = analysis.get("visual_hierarchy", [])
        if isinstance(hierarchy, list):
            for entry in hierarchy:
                text = str(entry).lower()
                if any(marker in text for marker in markers):
                    return True
    objects = metadata.get("objects", [])
    if isinstance(objects, list):
        for item in objects:
            if not isinstance(item, dict):
                continue
            text = " ".join(
                str(item.get(field, "")).lower() for field in ["layer_kind", "semantic_boundary", "id"]
            )
            if any(marker in text for marker in markers):
                return True
    return False


def requires_candidate_comparison_evidence(item: dict) -> bool:
    if str(item.get("selected_candidate_id", "")).strip():
        return True
    repair_history = item.get("repair_history")
    if not isinstance(repair_history, list) or not repair_history:
        return False
    return any(
        isinstance(entry, dict) and str(entry.get("candidate_id", "")).strip()
        for entry in repair_history
    )


def requires_object_type(item: dict) -> bool:
    text = " ".join(str(item.get(field, "")).lower() for field in ["layer_kind", "semantic_boundary", "id"])
    return any(
        marker in text
        for marker in {"tile", "glyph", "badge", "logo", "illustration", "plate", "icon", "checkbox"}
    )


def has_carrier_layer(item: dict) -> bool:
    text = " ".join(str(item.get(field, "")).lower() for field in ["layer_kind", "semantic_boundary", "id"])
    return any(marker in text for marker in {"carrier", "tile", "badge", "capsule", "icon-tile"})


def has_glyph_layer(item: dict) -> bool:
    text = " ".join(str(item.get(field, "")).lower() for field in ["layer_kind", "semantic_boundary", "id"])
    return "glyph" in text


def is_placeholder_only_rebuild(item: dict) -> bool:
    if not isinstance(item, dict):
        return False
    decision_routing = item.get("decision_routing")
    rebuild_intent = item.get("rebuild_intent")
    if not isinstance(decision_routing, dict) or not isinstance(rebuild_intent, dict):
        return False
    return (
        decision_routing.get("final_action") == "rebuild_downstream"
        and rebuild_intent.get("rebuildable_downstream") is True
        and item.get("reuse_status") == "support-only"
        and item.get("delivery_class") == "support-only"
        and item.get("asset_class") in {"grouped-support", "background-support", "preview-reference"}
    )


def has_text_routing_confirmation(
    item: dict, decision_log: list[dict], allow_legacy_unscoped: bool = False
) -> bool:
    object_id = str(item.get("id", "")).strip().lower()
    for entry in decision_log:
        if not isinstance(entry, dict):
            continue
        if entry.get("decision_source") not in ALLOWED_DECISION_SOURCES:
            continue
        entry_object_id = str(entry.get("object_id", "")).strip().lower()
        stage = str(entry.get("stage", "")).strip().lower()
        if object_id and entry_object_id:
            if object_id == entry_object_id and stage in TEXT_ROUTING_CONFIRMATION_STAGES:
                return True
            continue
        evidence_text = " ".join(
            str(entry.get(field, "")).lower()
            for field in [
                "stage",
                "question",
                "recommended_answer",
                "recorded_answer",
                "decision_effect",
                "evidence_ref",
            ]
        )
        semantic_match = any(marker in evidence_text for marker in TEXT_ROUTING_CONFIRMATION_MARKERS)
        if object_id and object_id in evidence_text and (
            stage in TEXT_ROUTING_CONFIRMATION_STAGES or semantic_match
        ):
            return True
        if allow_legacy_unscoped and stage in TEXT_ROUTING_CONFIRMATION_STAGES and "text-like object" in evidence_text:
            return True
        if allow_legacy_unscoped and stage in TEXT_ROUTING_CONFIRMATION_STAGES and "rebuild downstream" in evidence_text and "visual asset" in evidence_text:
            return True
    return False


def validate_source(package_dir: Path, metadata: dict, errors: list[str]) -> tuple[int, int] | None:
    source = metadata.get("source", {})
    if not isinstance(source, dict):
        source = {}
    source_path = source.get("path", "source/source_original.png")
    path = rel_path(package_dir, source_path, errors, "metadata.source.path")
    if path is None:
        return None
    if not path.exists():
        errors.append(f"source backup is missing: {source_path}")
        return None
    size = image_size(path, errors)
    expected = (source.get("width"), source.get("height"))
    if size and all(isinstance(value, int) for value in expected) and size != expected:
        errors.append(f"source dimensions do not match metadata: {size} != {expected}")
    return size


def validate_objects(
    package_dir: Path, metadata: dict, source_size: tuple[int, int] | None, errors: list[str]
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
            and reuse_status != "production-ready"
        ):
            errors.append(
                f"{object_id}: qa.status pass requires atomic reusable layers to be "
                "reuse_status=production-ready"
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


def iter_preview_paths(previews: object) -> list[str]:
    paths: list[str] = []
    if isinstance(previews, dict):
        for value in previews.values():
            if isinstance(value, str):
                paths.append(value)
            elif isinstance(value, dict):
                paths.extend(iter_preview_paths(value))
    return paths


def require_preview_path(
    package_dir: Path,
    previews: dict,
    keys: list[str],
    errors: list[str],
    label: str,
    action: str,
) -> None:
    value: object = previews
    for key in keys:
        if not isinstance(value, dict):
            value = None
            break
        value = value.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} is required; run {action}")
        return
    path = rel_path(package_dir, value, errors, label)
    if path is not None and not path.exists():
        errors.append(f"{label} file is missing: {value}")


def validate_previews(package_dir: Path, metadata: dict, errors: list[str]) -> None:
    previews = metadata.get("previews", {})
    if not isinstance(previews, dict):
        errors.append("metadata.previews must be an object")
        previews = {}

    objects = metadata.get("objects", [])
    object_layers = [
        item
        for item in objects
        if isinstance(item, dict)
        and item.get("role") in OBJECT_ASSET_ROLES
        and isinstance(item.get("id"), str)
        and item.get("id").strip()
        and not is_placeholder_only_rebuild(item)
    ]
    if object_layers:
        require_preview_path(
            package_dir,
            previews,
            ["overview_decomposition"],
            errors,
            "overview inspection preview",
            "build_previews.py",
        )
        require_preview_path(
            package_dir,
            previews,
            ["sprite_sheet_2x2"],
            errors,
            "sprite sheet inspection preview",
            "build_previews.py",
        )
    for item in object_layers:
        object_id = item["id"]
        require_preview_path(
            package_dir,
            previews,
            [object_id, "whitebg"],
            errors,
            f"{object_id}: white-background inspection preview",
            "build_previews.py",
        )
        require_preview_path(
            package_dir,
            previews,
            [object_id, "checkerboard"],
            errors,
            f"{object_id}: checkerboard inspection preview",
            "build_previews.py",
        )
        require_preview_path(
            package_dir,
            previews,
            ["quality", object_id, "mask_overlay"],
            errors,
            f"{object_id}: mask overlay quality preview",
            "build_quality_previews.py",
        )
        require_preview_path(
            package_dir,
            previews,
            ["quality", object_id, "alpha_inspection"],
            errors,
            f"{object_id}: alpha inspection quality preview",
            "build_quality_previews.py",
        )

    for preview_path in iter_preview_paths(previews):
        path = rel_path(package_dir, preview_path, errors, "preview path")
        if path is None:
            continue
        if not path.exists():
            errors.append(f"preview file is missing: {preview_path}")
    audit = metadata.get("audit", {})
    if isinstance(audit, dict) and audit.get("quality_audit_path"):
        audit_path = rel_path(package_dir, audit.get("quality_audit_path"), errors, "quality audit path")
        if audit_path is not None and not audit_path.exists():
            errors.append(f"quality audit file is missing: {audit.get('quality_audit_path')}")


def validate_qa_report(package_dir: Path, errors: list[str]) -> None:
    qa_path = package_dir / "qa_report.md"
    if not qa_path.exists():
        errors.append("qa_report.md is missing")
        return
    text = qa_path.read_text(encoding="utf-8")
    if "Final status:" not in text:
        errors.append("qa_report.md must contain 'Final status:'")


def collect_validation_errors(package_dir: Path, metadata: dict | None = None) -> list[str]:
    errors: list[str] = []
    if not package_dir.is_dir():
        errors.append(f"package directory does not exist: {package_dir}")
        return errors

    candidate_metadata = metadata if isinstance(metadata, dict) else load_metadata(package_dir, errors)
    validate_required_layout(package_dir, errors)
    validate_metadata_fields(candidate_metadata, errors)
    validate_extraction_pipeline(candidate_metadata, errors)
    source_size = validate_source(package_dir, candidate_metadata, errors)
    validate_objects(package_dir, candidate_metadata, source_size, errors)
    validate_previews(package_dir, candidate_metadata, errors)
    validate_qa_report(package_dir, errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a split image asset package.")
    parser.add_argument("package_dir", help="Asset package directory.")
    args = parser.parse_args()

    package_dir = Path(args.package_dir).resolve()
    errors = collect_validation_errors(package_dir)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Package valid: {package_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
