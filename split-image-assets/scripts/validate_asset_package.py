import argparse
import json
import sys
from pathlib import Path

from PIL import Image


OBJECT_ASSET_ROLES = {"main", "secondary", "group", "shadow"}


def rel_path(package_dir: Path, value: str) -> Path:
    return (package_dir / value).resolve()


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


def validate_metadata_fields(metadata: dict, errors: list[str]) -> None:
    for field in ["schema_version", "package_name", "source", "objects", "qa"]:
        if field not in metadata:
            errors.append(f"metadata missing required field: {field}")
    source = metadata.get("source", {})
    for field in ["path", "width", "height"]:
        if field not in source:
            errors.append(f"metadata.source missing required field: {field}")
    qa = metadata.get("qa", {})
    if "status" not in qa:
        errors.append("metadata.qa missing required field: status")


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


def validate_source(package_dir: Path, metadata: dict, errors: list[str]) -> tuple[int, int] | None:
    source_path = metadata.get("source", {}).get("path", "source/source_original.png")
    path = rel_path(package_dir, source_path)
    if not path.exists():
        errors.append(f"source backup is missing: {source_path}")
        return None
    size = image_size(path, errors)
    expected = (metadata.get("source", {}).get("width"), metadata.get("source", {}).get("height"))
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
        object_id = item.get("id", "<missing id>")
        role = item.get("role")
        asset_path = item.get("asset_path")
        if role in OBJECT_ASSET_ROLES:
            if not asset_path:
                errors.append(f"{object_id}: asset_path is required for role {role}")
            else:
                path = rel_path(package_dir, asset_path)
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
            path = rel_path(package_dir, mask_path)
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


def iter_preview_paths(previews: object) -> list[str]:
    paths: list[str] = []
    if isinstance(previews, dict):
        for value in previews.values():
            if isinstance(value, str):
                paths.append(value)
            elif isinstance(value, dict):
                paths.extend(str(child) for child in value.values() if isinstance(child, str))
    return paths


def validate_previews(package_dir: Path, metadata: dict, errors: list[str]) -> None:
    for preview_path in iter_preview_paths(metadata.get("previews", {})):
        path = rel_path(package_dir, preview_path)
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
