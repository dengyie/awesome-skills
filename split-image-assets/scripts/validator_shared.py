import json
from pathlib import Path

from PIL import Image

from package_state_lib import find_plan_object, read_plan_manifest
from split_image_assets_contract import ALLOWED_DECISION_SOURCES, NON_DEFAULT_CONFIRMATION_SOURCES


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
ALLOWED_ROOT_FILES = {"metadata.json", "qa_report.md", "asset_manifest.json", "plan_manifest.json"}
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
    "accepted_approximate_reconstructions",
    "accepted_generated_reconstructions",
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
PASS_READY_REUSE_STATUSES = {
    "production-ready",
    "approximate-reconstruction",
    "accepted-approximate-reconstruction",
    "accepted-generated-reconstruction",
}
GENERATED_EVIDENCE_FIELDS = {
    "generation_source",
    "generation_model_or_tool",
    "generation_version",
    "generation_prompt_or_brief_ref",
    "generation_reference_inputs",
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


def decision_answer(entry: dict) -> str:
    for field_name in DECISION_ANSWER_FIELDS:
        value = entry.get(field_name)
        if isinstance(value, str) and value.strip():
            return value
    return ""


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


def load_plan_manifest(package_dir: Path, errors: list[str]) -> dict | None:
    try:
        return read_plan_manifest(package_dir)
    except json.JSONDecodeError as exc:
        errors.append(f"plan_manifest.json is not valid JSON: {exc}")
        return None
    except ValueError as exc:
        errors.append(str(exc))
        return None


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


def is_generated_delivery_layer(item: dict) -> bool:
    if item.get("delivery_class") == "generated-reconstruction":
        return True
    if item.get("reuse_status") == "accepted-generated-reconstruction":
        return True
    return any(
        isinstance(item.get(field_name), str) and str(item.get(field_name)).strip()
        for field_name in [
            "generation_source",
            "generation_model_or_tool",
            "generation_prompt_or_brief_ref",
        ]
    )


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
            values = [item.get("layer_kind", ""), item.get("object_type", ""), item.get("semantic_boundary", "")]
            text = " ".join(str(value).lower() for value in values)
            if any(marker in text for marker in markers):
                return True
    return False


def requires_candidate_comparison_evidence(item: dict) -> bool:
    selected_candidate_id = str(item.get("selected_candidate_id", "")).strip()
    repair_history = item.get("repair_history", [])
    return bool(selected_candidate_id) or (isinstance(repair_history, list) and bool(repair_history))


def requires_object_type(item: dict) -> bool:
    text = " ".join(
        str(item.get(field_name, "")).lower() for field_name in ["layer_kind", "semantic_boundary", "role", "object_type"]
    )
    return any(marker in text for marker in ["ui", "tile", "glyph", "badge", "logo", "support", "plate"])


def has_carrier_layer(item: dict) -> bool:
    text = " ".join(str(item.get(field_name, "")).lower() for field_name in ["layer_kind", "object_type", "id"])
    return any(marker in text for marker in ["carrier", "tile", "badge", "plate"])


def has_glyph_layer(item: dict) -> bool:
    text = " ".join(str(item.get(field_name, "")).lower() for field_name in ["layer_kind", "object_type", "id"])
    return "glyph" in text


def is_placeholder_only_rebuild(item: dict) -> bool:
    decision_routing = item.get("decision_routing")
    rebuild_intent = item.get("rebuild_intent")
    return (
        isinstance(decision_routing, dict)
        and isinstance(rebuild_intent, dict)
        and decision_routing.get("final_action") == "rebuild_downstream"
        and rebuild_intent.get("rebuildable_downstream") is True
        and item.get("reuse_status") == "support-only"
        and item.get("delivery_class") == "support-only"
        and item.get("asset_class") in {"grouped-support", "background-support", "preview-reference"}
    )


def has_text_routing_confirmation(item: dict, decision_log: list[dict], allow_legacy_unscoped: bool = False) -> bool:
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
        if object_id and object_id in evidence_text and (stage in TEXT_ROUTING_CONFIRMATION_STAGES or semantic_match):
            return True
        if allow_legacy_unscoped and stage in TEXT_ROUTING_CONFIRMATION_STAGES and "text-like object" in evidence_text:
            return True
        if allow_legacy_unscoped and stage in TEXT_ROUTING_CONFIRMATION_STAGES and "rebuild downstream" in evidence_text and "visual asset" in evidence_text:
            return True
    return False


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

