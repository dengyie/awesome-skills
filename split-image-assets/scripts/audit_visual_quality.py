import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw


OBJECT_ASSET_ROLES = {"main", "secondary", "group", "background", "shadow"}
SUPPORT_MARKERS = {
    "background",
    "backplate",
    "clean plate",
    "plate",
    "support",
    "panel",
    "chrome",
}
QUALITY_STAGING_DIR = Path("_staging") / "quality"


def load_metadata(package_dir: Path, errors: list[str]) -> dict:
    metadata_path = package_dir / "metadata.json"
    if not metadata_path.exists():
        errors.append("metadata.json is missing")
        return {}
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"metadata.json is not valid JSON: {exc}")
        return {}
    if not isinstance(metadata, dict):
        errors.append("metadata.json must contain an object")
        return {}
    return metadata


def write_metadata(package_dir: Path, metadata: dict) -> None:
    (package_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def package_path(package_dir: Path, value: object, label: str, errors: list[str]) -> Path | None:
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


def object_layers(metadata: dict) -> list[dict]:
    objects = metadata.get("objects", [])
    if not isinstance(objects, list):
        return []
    return [
        item
        for item in objects
        if isinstance(item, dict)
        and item.get("role") in OBJECT_ASSET_ROLES
        and item.get("asset_path")
    ]


def warning(code: str, object_id: str, message: str, details: dict | None = None) -> dict:
    record = {
        "code": code,
        "object_id": object_id,
        "message": message,
    }
    if details:
        record["details"] = details
    return record


def audit_output_path(package_dir: Path) -> Path:
    return package_dir / QUALITY_STAGING_DIR / "quality_audit.json"


def alpha_channel(asset: Image.Image) -> Image.Image | None:
    rgba = asset.convert("RGBA")
    return rgba.getchannel("A")


def count_alpha_values(alpha: Image.Image) -> tuple[int, int, int]:
    values = list(alpha.getdata())
    transparent = sum(1 for value in values if value == 0)
    partial = sum(1 for value in values if 0 < value < 255)
    opaque = sum(1 for value in values if value == 255)
    return transparent, partial, opaque


def touches_canvas_edge(alpha: Image.Image) -> bool:
    width, height = alpha.size
    if width == 0 or height == 0:
        return False
    pixels = alpha.load()
    for x in range(width):
        if pixels[x, 0] > 0 or pixels[x, height - 1] > 0:
            return True
    for y in range(height):
        if pixels[0, y] > 0 or pixels[width - 1, y] > 0:
            return True
    return False


def mask_foreground_ratio(mask: Image.Image) -> float:
    mask_l = mask.convert("L")
    values = list(mask_l.getdata())
    if not values:
        return 0.0
    foreground = sum(1 for value in values if value > 0)
    return foreground / len(values)


def looks_like_support_layer(item: dict) -> bool:
    text = " ".join(
        str(item.get(field, "")).lower()
        for field in ["id", "layer_kind", "semantic_boundary", "mask_source", "alpha_source"]
    )
    return any(marker in text for marker in SUPPORT_MARKERS)


def audit_layer(package_dir: Path, item: dict, warnings: list[dict], errors: list[str]) -> None:
    object_id = str(item.get("id") or "<missing id>")
    asset_path = package_path(package_dir, item.get("asset_path"), f"{object_id}: asset_path", errors)
    if asset_path is None:
        return
    if not asset_path.exists():
        errors.append(f"{object_id}: asset file is missing: {item.get('asset_path')}")
        return

    try:
        with Image.open(asset_path) as opened:
            asset = opened.convert("RGBA")
    except OSError as exc:
        errors.append(f"{object_id}: asset image cannot be opened: {exc}")
        return

    alpha = alpha_channel(asset)
    if alpha is not None:
        transparent, partial, opaque = count_alpha_values(alpha)
        total = max(1, transparent + partial + opaque)
        partial_ratio = partial / total
        if opaque > 0 and partial == 0:
            warnings.append(
                warning(
                    "hard-alpha-risk",
                    object_id,
                    "Alpha contains no partial transparency; inspect for hard cut edges.",
                    {"partial_alpha_ratio": partial_ratio},
                )
            )
        if touches_canvas_edge(alpha):
            warnings.append(
                warning(
                    "detached-fragments",
                    object_id,
                    "Nontransparent pixels touch the asset canvas edge; crop may be loose or clipped.",
                )
            )
        dark_opaque_ratio = sum(
            1
            for red, green, blue, alpha_value in asset.getdata()
            if alpha_value > 0 and red < 24 and green < 24 and blue < 24
        ) / max(1, asset.width * asset.height)
        if dark_opaque_ratio > 0.08:
            warnings.append(
                warning(
                    "color-residue",
                    object_id,
                    "Opaque pixels retain a notable amount of dark color; inspect for fringe or background residue.",
                    {"dark_pixel_ratio": round(dark_opaque_ratio, 4)},
                )
            )

    mask_path = item.get("mask_path")
    if mask_path:
        resolved_mask = package_path(package_dir, mask_path, f"{object_id}: mask_path", errors)
        if resolved_mask is not None and resolved_mask.exists():
            try:
                with Image.open(resolved_mask) as opened:
                    ratio = mask_foreground_ratio(opened)
            except OSError as exc:
                errors.append(f"{object_id}: mask image cannot be opened: {exc}")
            else:
                if ratio > 0.8:
                    warnings.append(
                        warning(
                            "smear-artifact",
                            object_id,
                            "Source-space mask covers most of the source; inspect for whole-image or plate masking.",
                            {"foreground_ratio": ratio},
                        )
                    )

    if item.get("asset_class") == "atomic" and looks_like_support_layer(item):
        warnings.append(
            warning(
                "support-layer-misclassified",
                object_id,
                "Layer looks like a plate/background/support layer but is marked asset_class=atomic.",
            )
        )
    layer_kind = str(item.get("layer_kind", "")).lower()
    semantic_boundary = str(item.get("semantic_boundary", "")).lower()
    if any(marker in layer_kind or marker in semantic_boundary for marker in ["glyph", "icon", "badge"]):
        if looks_like_support_layer(item):
            warnings.append(
                warning(
                    "carrier-glyph-cross-contamination",
                    object_id,
                    "Glyph-like layer still looks mixed with carrier/background semantics; inspect split cleanliness.",
                )
            )
    if item.get("approximate") is True:
        warnings.append(
            warning(
                "over-flat-reconstruction",
                object_id,
                "Approximate or reconstructed layer needs inspection for flattened style or missing detail.",
            )
        )
        warnings.append(
            warning(
                "style-mismatch-reconstruction",
                object_id,
                "Approximate or reconstructed layer may not match the original design language closely enough.",
            )
        )


def make_checkerboard(size: tuple[int, int], cell: int = 8) -> Image.Image:
    image = Image.new("RGBA", size, (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], cell):
        for x in range(0, size[0], cell):
            if (x // cell + y // cell) % 2:
                draw.rectangle([x, y, x + cell - 1, y + cell - 1], fill=(215, 215, 215, 255))
    return image


def paste_thumbnail(canvas: Image.Image, asset: Image.Image, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    box_width = x1 - x0
    box_height = y1 - y0
    scale = min(box_width / max(1, asset.width), box_height / max(1, asset.height), 1.0)
    resized = asset.resize(
        (max(1, int(asset.width * scale)), max(1, int(asset.height * scale))),
        Image.Resampling.LANCZOS,
    )
    x = x0 + (box_width - resized.width) // 2
    y = y0 + (box_height - resized.height) // 2
    canvas.alpha_composite(resized, (x, y))


def build_contact_sheet(
    package_dir: Path, metadata: dict, warnings: list[dict], errors: list[str]
) -> str:
    layers = object_layers(metadata)
    previews_dir = package_dir / QUALITY_STAGING_DIR
    previews_dir.mkdir(parents=True, exist_ok=True)
    cell_width = 180
    cell_height = 160
    columns = 3
    rows = max(1, (len(layers) + columns - 1) // columns)
    canvas = Image.new("RGBA", (cell_width * columns, cell_height * rows), (245, 245, 245, 255))
    draw = ImageDraw.Draw(canvas)
    warning_counts: dict[str, int] = {}
    for item in warnings:
        object_id = str(item.get("object_id", ""))
        warning_counts[object_id] = warning_counts.get(object_id, 0) + 1

    for index, item in enumerate(layers):
        object_id = str(item.get("id") or "<missing id>")
        row = index // columns
        column = index % columns
        left = column * cell_width
        top = row * cell_height
        panel = make_checkerboard((cell_width, cell_height - 28))
        asset_path = package_path(package_dir, item.get("asset_path"), f"{object_id}: asset_path", errors)
        if asset_path is not None and asset_path.exists():
            try:
                with Image.open(asset_path) as opened:
                    paste_thumbnail(panel, opened.convert("RGBA"), (8, 8, cell_width - 8, cell_height - 36))
            except OSError:
                pass
        canvas.alpha_composite(panel, (left, top))
        outline = (210, 40, 40, 255) if warning_counts.get(object_id) else (90, 120, 160, 255)
        draw.rectangle([left, top, left + cell_width - 1, top + cell_height - 1], outline=outline, width=2)
        label = f"{object_id} | warnings: {warning_counts.get(object_id, 0)}"
        draw.text((left + 6, top + cell_height - 23), label[:32], fill=(20, 20, 20, 255))

    path = previews_dir / "qa_audit_contact_sheet.png"
    canvas.convert("RGB").save(path)
    return str(path.relative_to(package_dir)).replace("\\", "/")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Emit warning-only visual quality audit evidence for a split asset package."
    )
    parser.add_argument("package_dir", help="Asset package directory.")
    args = parser.parse_args()

    package_dir = Path(args.package_dir).resolve()
    errors: list[str] = []
    metadata = load_metadata(package_dir, errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    warnings: list[dict] = []
    for item in object_layers(metadata):
        audit_layer(package_dir, item, warnings, errors)

    contact_sheet_path = build_contact_sheet(package_dir, metadata, warnings, errors)
    audit_report_path = audit_output_path(package_dir)
    audit_report_path.parent.mkdir(parents=True, exist_ok=True)
    metadata.setdefault("previews", {})["qa_audit_contact_sheet"] = contact_sheet_path
    metadata["audit"] = {
        "quality_audit_path": str(audit_report_path.relative_to(package_dir)).replace("\\", "/"),
        "status": "warning" if warnings else "ok",
        "warning_count": len(warnings),
        "warning_codes": sorted({item["code"] for item in warnings}),
    }
    write_metadata(package_dir, metadata)

    report = {
        "schema_version": "1.0",
        "status": "warning" if warnings else "ok",
        "warning_count": len(warnings),
        "warnings": warnings,
        "contact_sheet": contact_sheet_path,
        "note": "Warning-only audit. This script does not replace human visual QA or set qa.status=pass.",
    }
    audit_report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Visual quality audit written: {audit_report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
