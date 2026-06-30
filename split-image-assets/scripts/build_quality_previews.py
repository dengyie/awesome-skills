import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw


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


def read_metadata(package_dir: Path) -> dict:
    return json.loads((package_dir / "metadata.json").read_text(encoding="utf-8"))


def write_metadata(package_dir: Path, metadata: dict) -> None:
    (package_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


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


def make_checkerboard(size: tuple[int, int], cell: int = 8) -> Image.Image:
    image = Image.new("RGBA", size, (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], cell):
        for x in range(0, size[0], cell):
            if (x // cell + y // cell) % 2:
                draw.rectangle([x, y, x + cell - 1, y + cell - 1], fill=(210, 210, 210, 255))
    return image


def mask_overlay(source: Image.Image, mask: Image.Image) -> Image.Image:
    base = source.convert("RGBA")
    mask_l = mask.convert("L").resize(base.size)
    color = Image.new("RGBA", base.size, (255, 0, 90, 115))
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    overlay.alpha_composite(color)
    overlay.putalpha(mask_l.point(lambda value: min(160, value)))
    base.alpha_composite(overlay)
    return base.convert("RGB")


def alpha_inspection(asset: Image.Image) -> Image.Image:
    asset = asset.convert("RGBA")
    checker = make_checkerboard(asset.size)
    checker.alpha_composite(asset)
    return checker.convert("RGB")


def build_for_object(
    package_dir: Path, source: Image.Image, item: dict, preview_records: dict, errors: list[str]
) -> bool:
    if is_placeholder_only_rebuild(item):
        return False
    object_id = item.get("id")
    asset_path = item.get("asset_path")
    mask_path = item.get("mask_path")
    if not object_id or not asset_path or not mask_path:
        errors.append(f"{object_id or '<missing id>'}: asset_path and mask_path are required")
        return False

    asset_file = package_path(package_dir, asset_path, f"{object_id}: asset_path", errors)
    mask_file = package_path(package_dir, mask_path, f"{object_id}: mask_path", errors)
    if asset_file is None or mask_file is None:
        return False
    missing = [str(path) for path in [asset_file, mask_file] if not path.exists()]
    if missing:
        errors.append(f"{object_id}: missing files for quality preview: {', '.join(missing)}")
        return False

    previews_dir = package_dir / "previews"
    previews_dir.mkdir(parents=True, exist_ok=True)
    with Image.open(asset_file) as asset, Image.open(mask_file) as mask:
        overlay = mask_overlay(source, mask)
        alpha = alpha_inspection(asset)

    overlay_path = previews_dir / f"{object_id}_mask_overlay.png"
    alpha_path = previews_dir / f"{object_id}_alpha_inspection.png"
    overlay.save(overlay_path)
    alpha.save(alpha_path)
    preview_records[object_id] = {
        "mask_overlay": str(overlay_path.relative_to(package_dir)).replace("\\", "/"),
        "alpha_inspection": str(alpha_path.relative_to(package_dir)).replace("\\", "/"),
    }
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build segmentation-quality previews from source, masks, and alpha assets."
    )
    parser.add_argument("package_dir", help="Asset package directory.")
    args = parser.parse_args()

    package_dir = Path(args.package_dir).resolve()
    metadata = read_metadata(package_dir)
    errors: list[str] = []
    source = metadata.get("source", {})
    source_value = source.get("path", "source/source_original.png") if isinstance(source, dict) else ""
    source_path = package_path(package_dir, source_value, "metadata.source.path", errors)
    if source_path is None:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    with Image.open(source_path) as opened:
        source = opened.convert("RGBA")

    preview_records = metadata.setdefault("previews", {}).setdefault("quality", {})
    generated = 0
    eligible_objects = 0
    for item in metadata.get("objects", []):
        if isinstance(item, dict):
            if not is_placeholder_only_rebuild(item):
                eligible_objects += 1
            if build_for_object(package_dir, source, item, preview_records, errors):
                generated += 1

    write_metadata(package_dir, metadata)
    if generated == 0 and eligible_objects == 0:
        print(f"Built quality previews for: {package_dir}")
        return 0
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        if generated == 0:
            print("ERROR: No quality previews generated", file=sys.stderr)
        else:
            print(
                f"ERROR: Built only {generated} of {eligible_objects} quality preview sets",
                file=sys.stderr,
            )
        return 1
    print(f"Built quality previews for: {package_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
