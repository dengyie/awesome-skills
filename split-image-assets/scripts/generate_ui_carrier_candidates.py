import argparse
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter

from candidate_workflow_lib import (
    ALLOWED_OBJECT_TYPES,
    apply_mask,
    average_rgb,
    border_ring,
    dilate_mask,
    ensure_repair_candidate_dir,
    intersect_mask,
    load_mask,
    load_rgba,
    package_path,
    package_relative,
    read_metadata,
    save_mask,
    save_rgba,
    subtract_mask,
    update_object_type,
    utc_timestamp,
    write_json,
    write_metadata,
)


ALLOWED_STRATEGIES = {
    "inpaint-direct",
    "center-only-rebuild",
    "center-rebuild-with-border-pasteback",
    "manual-texture-reconstruct",
}


def filled_region(size: tuple[int, int], color: tuple[int, int, int]) -> Image.Image:
    return Image.new("RGBA", size, color + (255,))


def preserve_border(base: Image.Image, candidate: Image.Image, border_mask: Image.Image) -> Image.Image:
    pasted = candidate.copy()
    pasted = Image.composite(base, pasted, border_mask)
    return pasted


def make_candidate(
    source_crop: Image.Image,
    carrier_mask: Image.Image,
    glyph_mask: Image.Image,
    strategy: str,
    exclusion_radius: int,
    border_width: int,
) -> Image.Image:
    glyph_exclusion = dilate_mask(glyph_mask, exclusion_radius)
    safe_fill_mask = subtract_mask(carrier_mask, glyph_exclusion)
    carrier_border = border_ring(carrier_mask, border_width)
    carrier_center = subtract_mask(
        subtract_mask(carrier_mask, carrier_border),
        glyph_exclusion,
    )
    fill_color = average_rgb(source_crop, safe_fill_mask if safe_fill_mask.getbbox() else carrier_mask)
    fill_image = filled_region(source_crop.size, fill_color)
    blurred_source = source_crop.filter(ImageFilter.GaussianBlur(max(1, exclusion_radius + 1)))

    if strategy == "inpaint-direct":
        rebuilt = source_crop.copy()
        rebuilt = Image.composite(blurred_source, rebuilt, intersect_mask(carrier_mask, glyph_exclusion))
        return apply_mask(rebuilt, carrier_mask)

    if strategy == "center-only-rebuild":
        rebuilt = source_crop.copy()
        rebuilt = Image.composite(fill_image, rebuilt, carrier_center)
        return apply_mask(rebuilt, carrier_mask)

    if strategy == "center-rebuild-with-border-pasteback":
        rebuilt = source_crop.copy()
        rebuilt = Image.composite(blurred_source, rebuilt, carrier_center)
        rebuilt = preserve_border(source_crop, rebuilt, carrier_border)
        return apply_mask(rebuilt, carrier_mask)

    if strategy == "manual-texture-reconstruct":
        texture_seed = source_crop.filter(ImageFilter.BoxBlur(max(1, border_width)))
        rebuilt = Image.composite(texture_seed, fill_image, carrier_center)
        rebuilt = preserve_border(source_crop, rebuilt, carrier_border)
        return apply_mask(rebuilt, carrier_mask)

    raise ValueError(f"unsupported strategy: {strategy}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate staged reconstruction candidates for UI carrier assets."
    )
    parser.add_argument("package_dir", help="Asset package directory.")
    parser.add_argument("--object-id", required=True, help="Target object id.")
    parser.add_argument("--source-crop", required=True, help="Package-relative source crop path.")
    parser.add_argument("--carrier-mask", required=True, help="Package-relative carrier mask path.")
    parser.add_argument("--glyph-mask", required=True, help="Package-relative glyph mask path.")
    parser.add_argument(
        "--strategy",
        action="append",
        choices=sorted(ALLOWED_STRATEGIES),
        help="Candidate strategy to generate. Defaults to all supported strategies.",
    )
    parser.add_argument(
        "--exclusion-radius",
        action="append",
        type=int,
        help="Glyph exclusion dilation radius in pixels. Repeatable. Defaults to 0 and 2.",
    )
    parser.add_argument("--border-width", type=int, default=2, help="Border width preserved during pasteback.")
    parser.add_argument(
        "--object-type",
        choices=sorted(ALLOWED_OBJECT_TYPES),
        default="ui-carrier",
        help="Optional object type to record when the object already exists in metadata.",
    )
    args = parser.parse_args()

    package_dir = Path(args.package_dir).resolve()
    source_crop_path = package_path(package_dir, args.source_crop, "source crop", parser)
    carrier_mask_path = package_path(package_dir, args.carrier_mask, "carrier mask", parser)
    glyph_mask_path = package_path(package_dir, args.glyph_mask, "glyph mask", parser)

    source_crop = load_rgba(source_crop_path)
    carrier_mask = load_mask(carrier_mask_path, source_crop.size)
    glyph_mask = load_mask(glyph_mask_path, source_crop.size)

    candidate_dir = ensure_repair_candidate_dir(package_dir, args.object_id)
    strategies = args.strategy or [
        "inpaint-direct",
        "center-only-rebuild",
        "center-rebuild-with-border-pasteback",
        "manual-texture-reconstruct",
    ]
    exclusion_radii = args.exclusion_radius or [0, 2]
    manifest_candidates: list[dict] = []

    for strategy in strategies:
        radius_values = exclusion_radii if strategy != "manual-texture-reconstruct" else [max(exclusion_radii)]
        for radius in radius_values:
            candidate_id = f"{args.object_id}-{strategy}-d{radius}"
            asset_path = candidate_dir / f"{candidate_id}.png"
            mask_path = candidate_dir / f"{candidate_id}_mask.png"
            candidate_image = make_candidate(
                source_crop,
                carrier_mask,
                glyph_mask,
                strategy,
                radius,
                args.border_width,
            )
            save_rgba(asset_path, candidate_image)
            save_mask(mask_path, carrier_mask)
            manifest_candidates.append(
                {
                    "candidate_id": candidate_id,
                    "asset_path": package_relative(package_dir, asset_path),
                    "mask_path": package_relative(package_dir, mask_path),
                    "strategy": strategy,
                    "object_type": args.object_type,
                    "exclusion_radius": radius,
                    "center_only": strategy in {
                        "center-only-rebuild",
                        "center-rebuild-with-border-pasteback",
                    },
                    "border_pasteback": strategy == "center-rebuild-with-border-pasteback",
                    "approximate_reconstruction": True,
                }
            )

    manifest_path = candidate_dir / f"{args.object_id}_ui_carrier_candidates.json"
    write_json(
        manifest_path,
        {
            "object_id": args.object_id,
            "object_type": args.object_type,
            "workflow_type": "ui-carrier-reconstruction",
            "source_crop_path": args.source_crop,
            "carrier_mask_path": args.carrier_mask,
            "glyph_mask_path": args.glyph_mask,
            "border_width": args.border_width,
            "candidates": manifest_candidates,
            "created_at": utc_timestamp(),
        },
    )

    metadata = read_metadata(package_dir)
    update_object_type(metadata, args.object_id, args.object_type)
    write_metadata(package_dir, metadata)
    print(f"Generated {len(manifest_candidates)} UI carrier candidates at {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
