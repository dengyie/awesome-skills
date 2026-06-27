import argparse
from pathlib import Path

from PIL import Image, ImageChops, ImageOps

from candidate_workflow_lib import (
    ALLOWED_OBJECT_TYPES,
    apply_mask,
    average_rgb,
    dilate_mask,
    ensure_repair_candidate_dir,
    erode_mask,
    load_rgba,
    package_path,
    package_relative,
    read_metadata,
    save_rgba,
    update_object_type,
    utc_timestamp,
    write_json,
    write_metadata,
)


ALLOWED_STRATEGIES = {
    "keep-current-alpha-recolor",
    "tile-subtract",
    "tile-subtract-tight",
    "padded-delivery-variant",
}


def parse_rgb(value: str | None) -> tuple[int, int, int] | None:
    if value is None:
        return None
    cleaned = value.strip().lstrip("#")
    if len(cleaned) != 6:
        raise ValueError("--foreground-color must use RRGGBB")
    return tuple(int(cleaned[index : index + 2], 16) for index in [0, 2, 4])


def recolor_with_alpha(alpha: Image.Image, color: tuple[int, int, int]) -> Image.Image:
    image = Image.new("RGBA", alpha.size, color + (255,))
    image.putalpha(alpha)
    return image


def tile_subtract_candidate(
    glyph: Image.Image,
    carrier_reference: Image.Image | None,
    foreground_color: tuple[int, int, int],
) -> Image.Image:
    alpha = glyph.getchannel("A")
    if carrier_reference is None:
        return recolor_with_alpha(alpha, foreground_color)
    carrier = carrier_reference.resize(glyph.size, Image.Resampling.LANCZOS).convert("RGBA")
    diff = ImageChops.difference(glyph.convert("RGBA"), carrier).convert("L")
    normalized = ImageOps.autocontrast(diff)
    recolored = recolor_with_alpha(alpha, foreground_color)
    recolored_rgb = recolored.convert("RGBA")
    recolored_rgb.putalpha(normalized)
    final = recolored.copy()
    final.putalpha(alpha)
    return final


def padded_variant(image: Image.Image, padding: int) -> Image.Image:
    canvas = Image.new("RGBA", (image.width + padding * 2, image.height + padding * 2), (0, 0, 0, 0))
    canvas.alpha_composite(image, (padding, padding))
    return canvas


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate staged cleanup candidates for hard-edge UI glyph assets."
    )
    parser.add_argument("package_dir", help="Asset package directory.")
    parser.add_argument("--object-id", required=True, help="Target object id.")
    parser.add_argument("--glyph-asset", required=True, help="Package-relative glyph asset path.")
    parser.add_argument(
        "--carrier-reference",
        help="Package-relative carrier or background estimate used for tile-subtract cleanup.",
    )
    parser.add_argument(
        "--foreground-color",
        help="Foreground color as RRGGBB. Defaults to the mean opaque glyph color.",
    )
    parser.add_argument("--tighten-radius", type=int, default=1, help="Alpha tightening radius for tight cleanup.")
    parser.add_argument("--padding", type=int, default=2, help="Transparent padding for delivery variant.")
    parser.add_argument(
        "--object-type",
        choices=sorted(ALLOWED_OBJECT_TYPES),
        default="ui-glyph",
        help="Optional object type to record when the object already exists in metadata.",
    )
    args = parser.parse_args()

    package_dir = Path(args.package_dir).resolve()
    glyph_path = package_path(package_dir, args.glyph_asset, "glyph asset", parser)
    carrier_path = (
        package_path(package_dir, args.carrier_reference, "carrier reference", parser)
        if args.carrier_reference
        else None
    )
    glyph = load_rgba(glyph_path)
    carrier_reference = load_rgba(carrier_path) if carrier_path else None
    alpha = glyph.getchannel("A")

    try:
        foreground_color = parse_rgb(args.foreground_color)
    except ValueError as exc:
        parser.error(str(exc))
    if foreground_color is None:
        foreground_color = average_rgb(glyph, alpha)

    candidate_dir = ensure_repair_candidate_dir(package_dir, args.object_id)
    manifest_candidates: list[dict] = []

    candidates = {
        "keep-current-alpha-recolor": recolor_with_alpha(alpha, foreground_color),
        "tile-subtract": tile_subtract_candidate(glyph, carrier_reference, foreground_color),
        "tile-subtract-tight": recolor_with_alpha(
            erode_mask(alpha, args.tighten_radius),
            foreground_color,
        ),
    }
    candidates["padded-delivery-variant"] = padded_variant(candidates["tile-subtract-tight"], args.padding)

    for strategy, image in candidates.items():
        asset_path = candidate_dir / f"{args.object_id}-{strategy}.png"
        save_rgba(asset_path, image)
        manifest_candidates.append(
            {
                "candidate_id": f"{args.object_id}-{strategy}",
                "asset_path": package_relative(package_dir, asset_path),
                "strategy": strategy,
                "object_type": args.object_type,
                "alpha_policy": "preserve-silhouette"
                if strategy != "tile-subtract-tight"
                else "tighten-silhouette",
                "padding": args.padding if strategy == "padded-delivery-variant" else 0,
            }
        )

    manifest_path = candidate_dir / f"{args.object_id}_ui_glyph_candidates.json"
    write_json(
        manifest_path,
        {
            "object_id": args.object_id,
            "object_type": args.object_type,
            "workflow_type": "ui-hard-edge-glyph-cleanup",
            "glyph_asset_path": args.glyph_asset,
            "carrier_reference_path": args.carrier_reference or "",
            "foreground_color": "#{:02x}{:02x}{:02x}".format(*foreground_color),
            "tighten_radius": args.tighten_radius,
            "padding": args.padding,
            "candidates": manifest_candidates,
            "created_at": utc_timestamp(),
        },
    )

    metadata = read_metadata(package_dir)
    update_object_type(metadata, args.object_id, args.object_type)
    write_metadata(package_dir, metadata)
    print(f"Generated {len(manifest_candidates)} UI glyph cleanup candidates at {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
