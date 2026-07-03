import argparse
import json
import re
import shutil
from pathlib import Path

from PIL import Image

from split_image_assets_contract import (
    ALLOWED_ASSET_CLASSES,
    ALLOWED_DELIVERY_CLASSES,
    ALLOWED_OBJECT_TYPES,
    ALLOWED_REUSE_STATUSES,
    default_object_routing_fields,
)


DEFAULT_STAGES = [
    "semantic-analysis",
    "segmentation",
    "alpha-refinement",
    "layer-packaging",
    "qa-review",
]
DEFAULT_QUALITY_GATES = [
    "mask alignment needs review",
    "alpha edges need review",
    "background residue needs review",
    "reuse readiness needs review",
]
DEFAULT_IMPORTED_MANUAL_REVIEW_FLAGS = [
    "external asset imported; inspect mask alignment and alpha edges"
]
DEFAULT_IMPORTED_QUALITY_CHECKS = {
    "mask_alignment": "needs-review",
    "alpha_edges": "needs-review",
    "background_residue": "needs-review",
    "reuse_readiness": "needs-review",
}
SAFE_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")
ALLOWED_ROLES = {"main", "secondary", "group", "background", "shadow"}
ALLOWED_CONFIDENCE = {"high", "medium", "low"}
ALLOWED_EDGE_COMPLEXITY = {"hard", "soft", "transparent-reflective"}
ALLOWED_EXTRACTION_METHOD = {"exact", "ai-assisted", "manual", "estimated", "unknown"}
def read_metadata(package_dir: Path) -> dict:
    return json.loads((package_dir / "metadata.json").read_text(encoding="utf-8"))


def write_metadata(package_dir: Path, metadata: dict) -> None:
    (package_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def copy_into_package(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def image_size(path: Path) -> tuple[int, int]:
    with Image.open(path) as image:
        return image.size


def checked_image_size(path: Path, parser: argparse.ArgumentParser, label: str) -> tuple[int, int]:
    try:
        return image_size(path)
    except OSError as exc:
        parser.error(f"{label} image cannot be opened: {path}: {exc}")


def checked_metadata(package_dir: Path, parser: argparse.ArgumentParser) -> dict:
    try:
        return read_metadata(package_dir)
    except FileNotFoundError:
        parser.error(f"metadata.json is missing: {package_dir / 'metadata.json'}")
    except json.JSONDecodeError as exc:
        parser.error(f"metadata.json is not valid JSON: {exc}")


def source_size(metadata: dict, parser: argparse.ArgumentParser) -> tuple[int, int]:
    source = metadata.get("source")
    if not isinstance(source, dict):
        parser.error("metadata.source must exist before importing source-space masks")
    width = source.get("width")
    height = source.get("height")
    if not isinstance(width, int) or not isinstance(height, int):
        parser.error("metadata.source.width and metadata.source.height are required")
    return width, height


def checked_object_id(value: str, parser: argparse.ArgumentParser) -> str:
    if not SAFE_ID_RE.match(value):
        parser.error("object-id must contain only letters, numbers, underscores, or hyphens")
    return value


def required_string(record: dict, field: str, parser: argparse.ArgumentParser) -> str:
    value = record.get(field)
    if not isinstance(value, str) or not value.strip():
        parser.error(f"manifest object field is required and must be non-empty: {field}")
    return value


def required_int(record: dict, field: str, parser: argparse.ArgumentParser) -> int:
    value = record.get(field)
    if isinstance(value, bool) or not isinstance(value, int):
        parser.error(f"manifest object field is required and must be an integer: {field}")
    return value


def checked_choice(value: str, allowed: set[str], label: str, parser: argparse.ArgumentParser) -> str:
    if value not in allowed:
        parser.error(f"{label} must be one of: {', '.join(sorted(allowed))}")
    return value


def upsert_tool(metadata: dict, name: str, role: str, version: str) -> None:
    pipeline = metadata.setdefault("extraction_pipeline", {})
    tools = pipeline.setdefault("tools", [])
    candidate = {"name": name, "role": role, "version": version}
    if candidate not in tools:
        tools.append(candidate)


def configure_pipeline(metadata: dict, recipe: str) -> None:
    pipeline = metadata.setdefault("extraction_pipeline", {})
    pipeline["recipe"] = recipe
    stages = pipeline.setdefault("stages", [])
    for stage in DEFAULT_STAGES:
        if stage not in stages:
            stages.append(stage)
    quality_gates = pipeline.setdefault("quality_gates", [])
    for gate in DEFAULT_QUALITY_GATES:
        if gate not in quality_gates:
            quality_gates.append(gate)


def preserve_existing_when_default(
    merged: dict,
    record: dict,
    existing: dict,
    field: str,
    default_value,
) -> None:
    if record.get(field) == default_value and field in existing:
        merged[field] = existing[field]


def merge_defaulted_mapping(existing: dict, incoming: dict, defaults: dict) -> dict:
    merged = dict(existing) if isinstance(existing, dict) else {}
    incoming_dict = incoming if isinstance(incoming, dict) else {}
    merged.update(incoming_dict)
    for key, default_value in defaults.items():
        if incoming_dict.get(key) == default_value and key in existing:
            merged[key] = existing[key]
    return merged


def merge_imported_object(existing: dict, record: dict) -> dict:
    merged = dict(existing)
    merged.update(record)

    for field, default_value in [
        ("object_type", "generic-object"),
    ]:
        preserve_existing_when_default(merged, record, existing, field, default_value)

    # A newly imported asset supersedes prior review or promotion evidence for the old pixels.
    merged["manual_review_flags"] = list(record.get("manual_review_flags", DEFAULT_IMPORTED_MANUAL_REVIEW_FLAGS))
    merged["quality_checks"] = dict(record.get("quality_checks", DEFAULT_IMPORTED_QUALITY_CHECKS))
    merged["selected_candidate_id"] = str(record.get("selected_candidate_id", ""))
    merged["repair_history"] = list(record.get("repair_history", []))
    merged["current_asset_revision"] = str(record.get("current_asset_revision", "initial-import"))
    merged["active_reconstruction_method"] = str(record.get("active_reconstruction_method", ""))
    merged["candidate_comparisons"] = []
    merged.pop("manual_review_confirmed", None)
    merged.pop("manual_review_notes", None)
    merged.pop("approximate", None)
    merged.pop("reconstruction_provenance", None)

    routing_defaults = default_object_routing_fields()
    for field_name, defaults in routing_defaults.items():
        existing_value = existing.get(field_name, {})
        incoming_value = record.get(field_name, {})
        if isinstance(existing_value, dict) and isinstance(incoming_value, dict):
            merged[field_name] = merge_defaulted_mapping(existing_value, incoming_value, defaults)

    return merged


def upsert_object(metadata: dict, record: dict) -> None:
    objects = metadata.setdefault("objects", [])
    for index, item in enumerate(objects):
        if isinstance(item, dict) and item.get("id") == record["id"]:
            objects[index] = merge_imported_object(item, record)
            return
    objects.append(record)


def summarize_assets(metadata: dict) -> None:
    summary = {
        "production_ready_assets": 0,
        "accepted_approximate_reconstructions": 0,
        "accepted_generated_reconstructions": 0,
        "draft_candidate_assets": 0,
        "support_only_layers": 0,
        "blocked_assets": 0,
    }
    objects = metadata.get("objects", [])
    if isinstance(objects, list):
        for item in objects:
            if not isinstance(item, dict):
                continue
            reuse_status = item.get("reuse_status")
            asset_class = item.get("asset_class")
            if reuse_status == "production-ready" and asset_class == "atomic":
                summary["production_ready_assets"] += 1
            elif reuse_status == "accepted-approximate-reconstruction":
                summary["accepted_approximate_reconstructions"] += 1
            elif reuse_status == "accepted-generated-reconstruction":
                summary["accepted_generated_reconstructions"] += 1
            elif reuse_status == "draft-candidate":
                summary["draft_candidate_assets"] += 1
            elif reuse_status in {"support-only", "approximate-reconstruction"} or asset_class in {
                "grouped-support",
                "background-support",
                "preview-reference",
            }:
                summary["support_only_layers"] += 1
            elif reuse_status == "blocked":
                summary["blocked_assets"] += 1
    metadata["asset_summary"] = summary


def build_import_plan(
    package_dir: Path,
    metadata: dict,
    parser: argparse.ArgumentParser,
    record: dict,
    recipe: str,
    tool_name: str,
    tool_role: str,
    tool_version: str,
    confidence: str,
    edge_complexity: str,
    extraction_method: str,
) -> None:
    object_id = checked_object_id(required_string(record, "object_id", parser), parser)
    role = checked_choice(required_string(record, "role", parser), ALLOWED_ROLES, "role", parser)
    layer_kind = required_string(record, "layer_kind", parser)
    composition_order = required_int(record, "composition_order", parser)
    semantic_boundary = required_string(record, "semantic_boundary", parser)
    asset_source = Path(required_string(record, "asset", parser)).resolve()
    mask_source = Path(required_string(record, "mask", parser)).resolve()
    mask_source_name = required_string(record, "mask_source", parser)
    alpha_source_name = required_string(record, "alpha_source", parser)
    extraction_method_value = checked_choice(
        str(record.get("extraction_method", extraction_method)),
        ALLOWED_EXTRACTION_METHOD,
        "extraction_method",
        parser,
    )
    asset_class = checked_choice(
        str(record.get("asset_class", "candidate")),
        ALLOWED_ASSET_CLASSES,
        "asset_class",
        parser,
    )
    reuse_status = checked_choice(
        str(record.get("reuse_status", "draft-candidate")),
        ALLOWED_REUSE_STATUSES,
        "reuse_status",
        parser,
    )
    delivery_class = checked_choice(
        str(record.get("delivery_class", "draft-candidate")),
        ALLOWED_DELIVERY_CLASSES,
        "delivery_class",
        parser,
    )
    confidence_value = checked_choice(
        str(record.get("confidence", confidence)),
        ALLOWED_CONFIDENCE,
        "confidence",
        parser,
    )
    edge_complexity_value = checked_choice(
        str(record.get("edge_complexity", edge_complexity)),
        ALLOWED_EDGE_COMPLEXITY,
        "edge_complexity",
        parser,
    )
    object_type = checked_choice(
        str(record.get("object_type", "generic-object")),
        ALLOWED_OBJECT_TYPES,
        "object_type",
        parser,
    )
    asset_target = package_dir / "assets" / f"{object_id}_transparent.png"
    mask_target = package_dir / "masks" / f"mask_{object_id}.png"

    expected_mask_size = source_size(metadata, parser)
    width, height = checked_image_size(asset_source, parser, "asset")
    actual_mask_size = checked_image_size(mask_source, parser, "mask")
    if actual_mask_size != expected_mask_size:
        parser.error(
            "source-space mask dimensions must match metadata.source dimensions: "
            f"{actual_mask_size} != {expected_mask_size}"
        )

    return {
        "asset_source": asset_source,
        "asset_target": asset_target,
        "mask_source": mask_source,
        "mask_target": mask_target,
        "recipe": recipe,
        "tool_name": tool_name,
        "tool_role": tool_role,
        "tool_version": tool_version,
        "object": {
            "id": object_id,
            "role": role,
            "layer_kind": layer_kind,
            "composition_order": composition_order,
            "semantic_boundary": semantic_boundary,
            "asset_path": str(asset_target.relative_to(package_dir)).replace("\\", "/"),
            "mask_path": str(mask_target.relative_to(package_dir)).replace("\\", "/"),
            "mask_source": mask_source_name,
            "alpha_source": alpha_source_name,
            "mask_coordinate_space": "source",
            "width": width,
            "height": height,
            "aspect_ratio": width / height if height else 0,
            "extraction_method": extraction_method_value,
            "confidence": confidence_value,
            "edge_complexity": edge_complexity_value,
            "object_type": object_type,
            "asset_class": asset_class,
            "reuse_status": reuse_status,
            "delivery_class": delivery_class,
            "current_asset_revision": str(record.get("current_asset_revision", "initial-import")),
            "active_reconstruction_method": str(record.get("active_reconstruction_method", "")),
            "selected_candidate_id": str(record.get("selected_candidate_id", "")),
            "generation_source": str(record.get("generation_source", "")),
            "generation_model_or_tool": str(record.get("generation_model_or_tool", "")),
            "generation_version": str(record.get("generation_version", "")),
            "generation_prompt_or_brief_ref": str(record.get("generation_prompt_or_brief_ref", "")),
            "generation_reference_inputs": list(record.get("generation_reference_inputs", []))
            if isinstance(record.get("generation_reference_inputs", []), list)
            else [],
            "repair_history": list(record.get("repair_history", []))
            if isinstance(record.get("repair_history", []), list)
            else [],
            **default_object_routing_fields(),
            "manual_review_flags": list(DEFAULT_IMPORTED_MANUAL_REVIEW_FLAGS),
            "quality_checks": dict(DEFAULT_IMPORTED_QUALITY_CHECKS),
        },
    }


def apply_import_plan(package_dir: Path, metadata: dict, plan: dict) -> None:
    copy_into_package(plan["asset_source"], plan["asset_target"])
    copy_into_package(plan["mask_source"], plan["mask_target"])
    configure_pipeline(metadata, plan["recipe"])
    upsert_tool(metadata, plan["tool_name"], plan["tool_role"], plan["tool_version"])
    upsert_object(metadata, plan["object"])
    summarize_assets(metadata)


def import_record(
    package_dir: Path,
    metadata: dict,
    parser: argparse.ArgumentParser,
    record: dict,
    recipe: str,
    tool_name: str,
    tool_role: str,
    tool_version: str,
    confidence: str,
    edge_complexity: str,
    extraction_method: str,
) -> None:
    apply_import_plan(
        package_dir,
        metadata,
        build_import_plan(
            package_dir,
            metadata,
            parser,
            record,
            recipe,
            tool_name,
            tool_role,
            tool_version,
            confidence,
            edge_complexity,
            extraction_method,
        ),
    )


def load_manifest(path: Path, parser: argparse.ArgumentParser) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        parser.error(f"manifest file does not exist: {path}")
    except json.JSONDecodeError as exc:
        parser.error(f"manifest file is not valid JSON: {exc}")
    if not isinstance(data, dict):
        parser.error("manifest file must contain an object")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import outputs from mature segmentation, matting, or layered-image tools."
    )
    parser.add_argument("package_dir", help="Asset package directory.")
    parser.add_argument("--manifest", help="JSON manifest for batch upstream import.")
    parser.add_argument("--object-id")
    parser.add_argument("--role", choices=sorted(ALLOWED_ROLES))
    parser.add_argument("--layer-kind")
    parser.add_argument("--composition-order", type=int)
    parser.add_argument("--semantic-boundary")
    parser.add_argument("--asset", help="Transparent PNG asset produced externally.")
    parser.add_argument("--mask", help="Source-space mask produced externally.")
    parser.add_argument("--mask-source")
    parser.add_argument("--alpha-source")
    parser.add_argument("--tool-name")
    parser.add_argument("--tool-role")
    parser.add_argument("--tool-version")
    parser.add_argument("--object-type", choices=sorted(ALLOWED_OBJECT_TYPES), default="generic-object")
    parser.add_argument("--asset-class", choices=sorted(ALLOWED_ASSET_CLASSES), default="candidate")
    parser.add_argument(
        "--reuse-status",
        choices=sorted(ALLOWED_REUSE_STATUSES),
        default="draft-candidate",
    )
    parser.add_argument(
        "--delivery-class",
        choices=sorted(ALLOWED_DELIVERY_CLASSES),
        default="draft-candidate",
    )
    parser.add_argument("--recipe", default="grounded-segmentation-matting-repair")
    parser.add_argument("--confidence", default="medium", choices=["high", "medium", "low"])
    parser.add_argument(
        "--edge-complexity",
        default="soft",
        choices=["hard", "soft", "transparent-reflective"],
    )
    parser.add_argument(
        "--extraction-method",
        default="ai-assisted",
        choices=["exact", "ai-assisted", "manual", "estimated", "unknown"],
    )
    args = parser.parse_args()

    package_dir = Path(args.package_dir).resolve()
    metadata = checked_metadata(package_dir, parser)

    if args.manifest:
        manifest = load_manifest(Path(args.manifest).resolve(), parser)
        tool = manifest.get("tool", {})
        if not isinstance(tool, dict):
            parser.error("manifest.tool must be an object")
        for field in ["name", "role", "version"]:
            value = tool.get(field)
            if not isinstance(value, str) or not value.strip():
                parser.error(f"manifest.tool.{field} is required and must be non-empty")
        objects = manifest.get("objects", [])
        if not isinstance(objects, list) or not objects:
            parser.error("manifest.objects must be a non-empty list")
        plans = []
        for record in objects:
            if not isinstance(record, dict):
                parser.error("manifest.objects entries must be objects")
            plans.append(
                build_import_plan(
                    package_dir,
                    metadata,
                    parser,
                    record,
                    str(manifest.get("recipe", args.recipe)),
                    str(tool.get("name", "")),
                    str(tool.get("role", "")),
                    str(tool.get("version", "")),
                    args.confidence,
                    args.edge_complexity,
                    args.extraction_method,
                )
            )
        for plan in plans:
            apply_import_plan(package_dir, metadata, plan)
    else:
        required_args = [
            "object_id",
            "role",
            "layer_kind",
            "composition_order",
            "semantic_boundary",
            "asset",
            "mask",
            "mask_source",
            "alpha_source",
            "tool_name",
            "tool_role",
            "tool_version",
        ]
        missing = [name for name in required_args if getattr(args, name) in (None, "")]
        if missing:
            parser.error("missing required arguments for single-object import: " + ", ".join(missing))
        import_record(
            package_dir,
            metadata,
            parser,
            {
                "object_id": args.object_id,
                "role": args.role,
                "layer_kind": args.layer_kind,
                "composition_order": args.composition_order,
                "semantic_boundary": args.semantic_boundary,
                "asset": args.asset,
                "mask": args.mask,
                "mask_source": args.mask_source,
                "alpha_source": args.alpha_source,
                "object_type": args.object_type,
                "asset_class": args.asset_class,
                "reuse_status": args.reuse_status,
                "delivery_class": args.delivery_class,
            },
            args.recipe,
            args.tool_name,
            args.tool_role,
            args.tool_version,
            args.confidence,
            args.edge_complexity,
            args.extraction_method,
        )

    metadata.setdefault("qa", {})["status"] = "needs-review"
    write_metadata(package_dir, metadata)

    print(f"Imported external asset layer(s) into: {package_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
