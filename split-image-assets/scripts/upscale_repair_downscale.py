import argparse
from pathlib import Path

from PIL import Image

from candidate_workflow_lib import (
    ensure_repair_candidate_dir,
    ensure_upscale_work_dir,
    load_mask,
    load_rgba,
    package_path,
    package_relative,
    save_mask,
    save_rgba,
    utc_timestamp,
    write_json,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare or finalize an upscale-repair-downscale candidate workflow."
    )
    parser.add_argument("package_dir", help="Asset package directory.")
    parser.add_argument("--object-id", required=True, help="Target object id.")
    parser.add_argument("--source-asset", required=True, help="Package-relative source asset path.")
    parser.add_argument("--source-mask", help="Package-relative source mask path.")
    parser.add_argument("--scale", type=int, choices=[2, 4], default=2, help="Upscale factor.")
    parser.add_argument(
        "--repaired-upscaled-asset",
        help="Package-relative repaired asset in the upscale work area. If omitted, the script only prepares inputs.",
    )
    parser.add_argument("--repaired-upscaled-mask", help="Package-relative repaired mask in the upscale work area.")
    parser.add_argument("--candidate-id", help="Candidate id used for finalized downscaled outputs.")
    args = parser.parse_args()

    package_dir = Path(args.package_dir).resolve()
    source_asset_path = package_path(package_dir, args.source_asset, "source asset", parser)
    source_mask_path = (
        package_path(package_dir, args.source_mask, "source mask", parser) if args.source_mask else None
    )
    source_asset = load_rgba(source_asset_path)
    source_mask = load_mask(source_mask_path, source_asset.size) if source_mask_path else None

    work_dir = ensure_upscale_work_dir(package_dir, args.object_id)
    prepared_asset_path = work_dir / f"{args.object_id}_x{args.scale}_prepared.png"
    prepared_mask_path = work_dir / f"{args.object_id}_x{args.scale}_prepared_mask.png"
    save_rgba(
        prepared_asset_path,
        source_asset.resize(
            (source_asset.width * args.scale, source_asset.height * args.scale),
            Image.Resampling.NEAREST,
        ),
    )
    if source_mask is not None:
        save_mask(
            prepared_mask_path,
            source_mask.resize(
                (source_mask.width * args.scale, source_mask.height * args.scale),
                Image.Resampling.NEAREST,
            ),
        )

    manifest = {
        "object_id": args.object_id,
        "workflow_type": "upscale-repair-downscale",
        "scale": args.scale,
        "prepared_asset_path": package_relative(package_dir, prepared_asset_path),
        "prepared_mask_path": package_relative(package_dir, prepared_mask_path)
        if prepared_mask_path.exists()
        else "",
        "created_at": utc_timestamp(),
    }

    if args.repaired_upscaled_asset:
        repaired_asset_path = package_path(
            package_dir,
            args.repaired_upscaled_asset,
            "repaired upscaled asset",
            parser,
        )
        repaired_asset = load_rgba(repaired_asset_path)
        candidate_id = args.candidate_id or f"{args.object_id}-upscale-x{args.scale}"
        candidate_dir = ensure_repair_candidate_dir(package_dir, args.object_id)
        downscaled_asset_path = candidate_dir / f"{candidate_id}.png"
        downscaled_mask_path = candidate_dir / f"{candidate_id}_mask.png"
        save_rgba(
            downscaled_asset_path,
            repaired_asset.resize(source_asset.size, Image.Resampling.LANCZOS),
        )
        manifest["candidate_id"] = candidate_id
        manifest["repaired_upscaled_asset_path"] = args.repaired_upscaled_asset
        manifest["downscaled_candidate_asset_path"] = package_relative(package_dir, downscaled_asset_path)

        if args.repaired_upscaled_mask:
            repaired_mask_path = package_path(
                package_dir,
                args.repaired_upscaled_mask,
                "repaired upscaled mask",
                parser,
            )
            repaired_mask = load_mask(repaired_mask_path)
            save_mask(
                downscaled_mask_path,
                repaired_mask.resize(source_asset.size, Image.Resampling.NEAREST),
            )
            manifest["repaired_upscaled_mask_path"] = args.repaired_upscaled_mask
            manifest["downscaled_candidate_mask_path"] = package_relative(package_dir, downscaled_mask_path)

    manifest_path = work_dir / f"{args.object_id}_upscale_workflow.json"
    write_json(manifest_path, manifest)
    print(f"Upscale workflow recorded at {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
