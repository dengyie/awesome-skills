from pathlib import Path

from validator_shared import (
    ALLOWED_ROOT_DIRECTORIES,
    ALLOWED_ROOT_FILES,
    OBJECT_ASSET_ROLES,
    image_size,
    is_placeholder_only_rebuild,
    iter_preview_paths,
    rel_path,
    require_preview_path,
)


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
