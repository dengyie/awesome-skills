import argparse
import json
import re
import shutil
from pathlib import Path

from PIL import Image


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
SAFE_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")


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


def upsert_object(metadata: dict, record: dict) -> None:
    objects = metadata.setdefault("objects", [])
    for index, item in enumerate(objects):
        if isinstance(item, dict) and item.get("id") == record["id"]:
            objects[index] = record
            return
    objects.append(record)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import outputs from mature segmentation, matting, or layered-image tools."
    )
    parser.add_argument("package_dir", help="Asset package directory.")
    parser.add_argument("--object-id", required=True)
    parser.add_argument("--role", required=True, choices=["main", "secondary", "group", "shadow"])
    parser.add_argument("--layer-kind", required=True)
    parser.add_argument("--composition-order", required=True, type=int)
    parser.add_argument("--semantic-boundary", required=True)
    parser.add_argument("--asset", required=True, help="Transparent PNG asset produced externally.")
    parser.add_argument("--mask", required=True, help="Source-space mask produced externally.")
    parser.add_argument("--mask-source", required=True)
    parser.add_argument("--alpha-source", required=True)
    parser.add_argument("--tool-name", required=True)
    parser.add_argument("--tool-role", required=True)
    parser.add_argument("--tool-version", required=True)
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
    object_id = checked_object_id(args.object_id, parser)
    asset_source = Path(args.asset).resolve()
    mask_source = Path(args.mask).resolve()
    asset_target = package_dir / "assets" / f"{object_id}_transparent.png"
    mask_target = package_dir / "masks" / f"mask_{object_id}.png"

    metadata = checked_metadata(package_dir, parser)
    expected_mask_size = source_size(metadata, parser)
    width, height = checked_image_size(asset_source, parser, "asset")
    actual_mask_size = checked_image_size(mask_source, parser, "mask")
    if actual_mask_size != expected_mask_size:
        parser.error(
            "source-space mask dimensions must match metadata.source dimensions: "
            f"{actual_mask_size} != {expected_mask_size}"
        )

    copy_into_package(asset_source, asset_target)
    copy_into_package(mask_source, mask_target)
    configure_pipeline(metadata, args.recipe)
    upsert_tool(metadata, args.tool_name, args.tool_role, args.tool_version)
    upsert_object(
        metadata,
        {
            "id": object_id,
            "role": args.role,
            "layer_kind": args.layer_kind,
            "composition_order": args.composition_order,
            "semantic_boundary": args.semantic_boundary,
            "asset_path": str(asset_target.relative_to(package_dir)).replace("\\", "/"),
            "mask_path": str(mask_target.relative_to(package_dir)).replace("\\", "/"),
            "mask_source": args.mask_source,
            "alpha_source": args.alpha_source,
            "mask_coordinate_space": "source",
            "width": width,
            "height": height,
            "aspect_ratio": width / height if height else 0,
            "extraction_method": args.extraction_method,
            "confidence": args.confidence,
            "edge_complexity": args.edge_complexity,
            "manual_review_flags": [
                "external asset imported; inspect mask alignment and alpha edges"
            ],
            "quality_checks": {
                "mask_alignment": "needs-review",
                "alpha_edges": "needs-review",
                "background_residue": "needs-review",
                "reuse_readiness": "needs-review",
            },
        },
    )
    metadata.setdefault("qa", {})["status"] = "needs-review"
    write_metadata(package_dir, metadata)

    print(f"Imported external asset layer: {object_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
