import argparse
import json
import sys
from pathlib import Path

from PIL import Image


OBJECT_ASSET_ROLES = {"main", "secondary", "group", "shadow"}
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
ALLOWED_QA_STATUSES = {"pass", "needs-review", "blocked"}
ALLOWED_QUALITY_CHECK_STATUSES = {"pass", "needs-review", "blocked", "unknown"}
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
ALLOWED_GRANULARITY_MODES = {"module", "component", "atomic-layer", "production-editable", "draft"}
REQUIRED_DECISION_FIELDS = {
    "stage",
    "question",
    "recommended_answer",
    "user_answer",
    "decision_effect",
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
    decision_log = metadata.get("decision_log", [])
    if not isinstance(decision_log, list):
        errors.append("metadata.decision_log must be a list")
    else:
        for index, entry in enumerate(decision_log):
            if not isinstance(entry, dict):
                errors.append(f"metadata.decision_log[{index}] must be an object")
                continue
            missing = sorted(REQUIRED_DECISION_FIELDS - set(entry))
            if missing:
                errors.append(
                    f"metadata.decision_log[{index}] missing required fields: "
                    + ", ".join(missing)
                )
            for field in REQUIRED_DECISION_FIELDS:
                value = entry.get(field)
                if value is not None and (not isinstance(value, str) or not value.strip()):
                    errors.append(f"metadata.decision_log[{index}].{field} must be a non-empty string")
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


def is_helper_only_layer(item: dict) -> bool:
    values = [item.get("mask_source", ""), item.get("alpha_source", "")]
    text = " ".join(str(value).lower() for value in values)
    return any(marker in text for marker in HELPER_ONLY_MARKERS)


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

    for item in objects:
        if not isinstance(item, dict):
            errors.append("metadata.objects entries must be objects")
            continue
        object_id = item.get("id", "<missing id>")
        role = item.get("role")
        asset_path = item.get("asset_path")
        if role in OBJECT_ASSET_ROLES:
            if not asset_path:
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
        if mask_path:
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
        if role in OBJECT_ASSET_ROLES:
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
                    qa = metadata.get("qa", {})
                    qa_status = qa.get("status") if isinstance(qa, dict) else None
                    if qa_status == "pass" and check_value != "pass":
                        errors.append(
                            f"{object_id}: qa.status cannot be pass when quality_checks.{check_name} is {check_value}"
                        )
            qa = metadata.get("qa", {})
            qa_status = qa.get("status") if isinstance(qa, dict) else None
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
                if qa_status == "pass" and item.get("manual_review_confirmed") is not True:
                    errors.append(
                        f"{object_id}: approximate reconstructed layers cannot support qa.status pass "
                        "without manual_review_confirmed=true"
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


def validate_qa_report(package_dir: Path, errors: list[str]) -> None:
    qa_path = package_dir / "qa_report.md"
    if not qa_path.exists():
        errors.append("qa_report.md is missing")
        return
    text = qa_path.read_text(encoding="utf-8")
    if "Final status:" not in text:
        errors.append("qa_report.md must contain 'Final status:'")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a split image asset package.")
    parser.add_argument("package_dir", help="Asset package directory.")
    args = parser.parse_args()

    package_dir = Path(args.package_dir).resolve()
    errors: list[str] = []
    if not package_dir.is_dir():
        errors.append(f"package directory does not exist: {package_dir}")
    validate_required_layout(package_dir, errors)
    metadata = load_metadata(package_dir, errors)
    validate_metadata_fields(metadata, errors)
    validate_extraction_pipeline(metadata, errors)
    source_size = validate_source(package_dir, metadata, errors)
    validate_objects(package_dir, metadata, source_size, errors)
    validate_previews(package_dir, metadata, errors)
    validate_qa_report(package_dir, errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Package valid: {package_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
