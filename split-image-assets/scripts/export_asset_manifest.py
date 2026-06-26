import argparse
import json
import sys
from pathlib import Path


OBJECT_ASSET_ROLES = {"main", "secondary", "group", "background", "shadow"}


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


def package_path(package_dir: Path, value: str, label: str, errors: list[str]) -> Path | None:
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


def quality_status(quality_checks: object) -> str:
    if not isinstance(quality_checks, dict) or not quality_checks:
        return "unknown"
    values = set(quality_checks.values())
    if "blocked" in values:
        return "blocked"
    if "needs-review" in values:
        return "needs-review"
    if "unknown" in values:
        return "unknown"
    if values == {"pass"}:
        return "pass"
    return "unknown"


def layer_record(package_dir: Path, item: dict, errors: list[str]) -> dict | None:
    object_id = item.get("id", "<missing id>")
    asset_path = item.get("asset_path")
    resolved_asset = package_path(package_dir, asset_path, f"{object_id}: asset_path", errors)
    if resolved_asset is None:
        return None
    if not resolved_asset.exists():
        errors.append(f"{object_id}: asset file is missing: {asset_path}")
        return None

    mask_path = item.get("mask_path")
    if mask_path:
        resolved_mask = package_path(package_dir, mask_path, f"{object_id}: mask_path", errors)
        if resolved_mask is None:
            return None
        if not resolved_mask.exists():
            errors.append(f"{object_id}: mask file is missing: {mask_path}")
            return None

    return {
        "id": object_id,
        "role": item.get("role"),
        "layer_kind": item.get("layer_kind"),
        "composition_order": item.get("composition_order"),
        "asset_path": asset_path,
        "mask_path": mask_path,
        "semantic_boundary": item.get("semantic_boundary"),
        "mask_source": item.get("mask_source"),
        "alpha_source": item.get("alpha_source"),
        "asset_class": item.get("asset_class"),
        "reuse_status": item.get("reuse_status"),
        "quality_status": quality_status(item.get("quality_checks")),
        "manual_review_flags": item.get("manual_review_flags", []),
    }


def summarize_layers(layers: list[dict]) -> dict:
    summary = {
        "production_ready_assets": 0,
        "draft_candidate_assets": 0,
        "support_only_layers": 0,
        "blocked_assets": 0,
    }
    for layer in layers:
        asset_class = layer.get("asset_class")
        reuse_status = layer.get("reuse_status")
        if reuse_status == "production-ready" and asset_class == "atomic":
            summary["production_ready_assets"] += 1
        elif reuse_status == "draft-candidate":
            summary["draft_candidate_assets"] += 1
        elif reuse_status == "support-only" or asset_class in {
            "grouped-support",
            "background-support",
            "preview-reference",
        }:
            summary["support_only_layers"] += 1
        elif reuse_status == "blocked":
            summary["blocked_assets"] += 1
    return summary


def build_manifest(package_dir: Path, metadata: dict, errors: list[str]) -> dict:
    objects = metadata.get("objects", [])
    if not isinstance(objects, list):
        errors.append("metadata.objects must be a list")
        objects = []

    layers: list[dict] = []
    for item in objects:
        if not isinstance(item, dict):
            errors.append("metadata.objects entries must be objects")
            continue
        role = item.get("role")
        if role not in OBJECT_ASSET_ROLES:
            object_id = item.get("id", "<missing id>")
            errors.append(
                f"{object_id}: role must be one of: " + ", ".join(sorted(OBJECT_ASSET_ROLES))
            )
            continue
        record = layer_record(package_dir, item, errors)
        if record is not None:
            layers.append(record)

    layers.sort(
        key=lambda layer: (
            layer["composition_order"]
            if isinstance(layer.get("composition_order"), int)
            else 10_000,
            str(layer.get("id") or ""),
        )
    )

    source = metadata.get("source", {}) if isinstance(metadata.get("source"), dict) else {}
    qa = metadata.get("qa", {}) if isinstance(metadata.get("qa"), dict) else {}
    pipeline = (
        metadata.get("extraction_pipeline", {})
        if isinstance(metadata.get("extraction_pipeline"), dict)
        else {}
    )
    return {
        "schema_version": "1.0",
        "package_name": metadata.get("package_name"),
        "source": {
            "path": source.get("path"),
            "width": source.get("width"),
            "height": source.get("height"),
        },
        "qa_status": qa.get("status"),
        "extraction_recipe": pipeline.get("recipe"),
        "asset_summary": summarize_layers(layers),
        "layers": layers,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export a downstream asset manifest from a split image asset package."
    )
    parser.add_argument("package_dir", help="Asset package directory.")
    parser.add_argument(
        "--output",
        default="asset_manifest.json",
        help="Package-relative manifest output path. Defaults to asset_manifest.json.",
    )
    args = parser.parse_args()

    package_dir = Path(args.package_dir).resolve()
    errors: list[str] = []
    if not package_dir.is_dir():
        errors.append(f"package directory does not exist: {package_dir}")
        metadata = {}
    else:
        metadata = load_metadata(package_dir, errors)

    output_path = package_path(package_dir, args.output, "output", errors)
    manifest = build_manifest(package_dir, metadata, errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    assert output_path is not None
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Asset manifest written: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
