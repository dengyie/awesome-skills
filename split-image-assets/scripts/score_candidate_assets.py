import argparse
import json
from pathlib import Path

from PIL import ImageFilter

from candidate_workflow_lib import (
    component_count,
    ensure_repair_candidate_dir,
    load_rgba,
    mean_absolute_difference,
    package_path,
    package_relative,
    risk_level,
    utc_timestamp,
    variance_score,
    write_json,
)


REQUIRED_SCORE_KEYS = [
    "edge_touch_risk",
    "detached_fragment_risk",
    "carrier_residue_risk",
    "glyph_residue_risk",
    "border_preservation_score",
    "texture_match_score",
    "flatness_risk",
    "style_mismatch_risk",
]


def parse_candidate(value: str, parser: argparse.ArgumentParser) -> tuple[str, str]:
    if "=" not in value:
        parser.error("--candidate must use candidate_id=package/relative/path.png")
    candidate_id, asset_path = value.split("=", 1)
    candidate_id = candidate_id.strip()
    asset_path = asset_path.strip()
    if not candidate_id or not asset_path:
        parser.error("--candidate must use candidate_id=package/relative/path.png")
    return candidate_id, asset_path


def score_candidate(
    candidate_image,
    reference_image,
    background_reference,
) -> tuple[dict, float]:
    alpha = candidate_image.getchannel("A")
    bbox = alpha.getbbox()
    touches_edge = 1.0 if bbox and (bbox[0] == 0 or bbox[1] == 0 or bbox[2] == candidate_image.width or bbox[3] == candidate_image.height) else 0.0
    detached_components = component_count(alpha)
    detached_risk = min(1.0, max(0, detached_components - 1) / 3.0)

    texture_match_score = 0.5
    border_preservation_score = 0.5
    flatness_risk = 0.5
    style_mismatch_risk = 0.5
    carrier_residue_risk = 0.5
    glyph_residue_risk = 0.5

    if reference_image is not None:
        mae = mean_absolute_difference(candidate_image, reference_image, alpha)
        texture_match_score = max(0.0, 1.0 - mae / 255.0)
        reference_alpha = reference_image.getchannel("A")
        border_band = alpha.filter(ImageFilter.MaxFilter(3))
        border_preservation_score = max(
            0.0,
            1.0 - mean_absolute_difference(candidate_image, reference_image, border_band) / 255.0,
        )
        candidate_variance = variance_score(candidate_image, alpha)
        reference_variance = variance_score(reference_image, reference_alpha)
        if reference_variance <= 0.1:
            flatness_risk = 0.0
        else:
            flatness_risk = min(
                1.0,
                abs(candidate_variance - reference_variance) / max(reference_variance, 1.0),
            )
        style_mismatch_risk = min(1.0, max(0.0, 1.0 - ((texture_match_score + border_preservation_score) / 2.0)))

    if background_reference is not None:
        edge_alpha = alpha.point(lambda value: 255 if 0 < value < 220 else 0)
        residue_gap = mean_absolute_difference(candidate_image, background_reference, edge_alpha)
        residue_risk = max(0.0, 1.0 - residue_gap / 255.0)
        carrier_residue_risk = residue_risk
        glyph_residue_risk = residue_risk

    aggregate_score = (
        (1.0 - touches_edge) * 0.1
        + (1.0 - detached_risk) * 0.1
        + texture_match_score * 0.2
        + border_preservation_score * 0.2
        + (1.0 - flatness_risk) * 0.15
        + (1.0 - style_mismatch_risk) * 0.15
        + (1.0 - carrier_residue_risk) * 0.05
        + (1.0 - glyph_residue_risk) * 0.05
    )

    scores = {
        "edge_touch_risk": {"value": round(touches_edge, 3), "level": risk_level(touches_edge)},
        "detached_fragment_risk": {
            "value": round(detached_risk, 3),
            "level": risk_level(detached_risk),
        },
        "carrier_residue_risk": {
            "value": round(carrier_residue_risk, 3),
            "level": risk_level(carrier_residue_risk),
        },
        "glyph_residue_risk": {
            "value": round(glyph_residue_risk, 3),
            "level": risk_level(glyph_residue_risk),
        },
        "border_preservation_score": {
            "value": round(border_preservation_score, 3),
            "level": risk_level(1.0 - border_preservation_score),
        },
        "texture_match_score": {
            "value": round(texture_match_score, 3),
            "level": risk_level(1.0 - texture_match_score),
        },
        "flatness_risk": {"value": round(flatness_risk, 3), "level": risk_level(flatness_risk)},
        "style_mismatch_risk": {
            "value": round(style_mismatch_risk, 3),
            "level": risk_level(style_mismatch_risk),
        },
    }
    return scores, round(aggregate_score * 100.0, 2)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Score staged repair candidates before compare and promotion."
    )
    parser.add_argument("package_dir", help="Asset package directory.")
    parser.add_argument("--object-id", required=True, help="Target object id.")
    parser.add_argument(
        "--candidate",
        action="append",
        required=True,
        help="Candidate pair in the form candidate_id=package/relative/path.png",
    )
    parser.add_argument("--reference-asset", help="Package-relative current asset or reference candidate.")
    parser.add_argument("--background-reference", help="Package-relative carrier/background estimate.")
    parser.add_argument("--workflow-type", default="generic-repair", help="Workflow type label.")
    parser.add_argument("--score-id", help="Optional score manifest id.")
    args = parser.parse_args()

    package_dir = Path(args.package_dir).resolve()
    reference_image = (
        load_rgba(package_path(package_dir, args.reference_asset, "reference asset", parser))
        if args.reference_asset
        else None
    )
    background_reference = (
        load_rgba(package_path(package_dir, args.background_reference, "background reference", parser))
        if args.background_reference
        else None
    )

    candidates: list[dict] = []
    for value in args.candidate:
        candidate_id, asset_path_value = parse_candidate(value, parser)
        asset_path = package_path(package_dir, asset_path_value, f"candidate {candidate_id}", parser)
        image = load_rgba(asset_path)
        scores, aggregate_score = score_candidate(image, reference_image, background_reference)
        candidates.append(
            {
                "candidate_id": candidate_id,
                "asset_path": asset_path,
                "relative_path": asset_path_value,
                "scores": scores,
                "aggregate_score": aggregate_score,
                "reject_recommendation": aggregate_score < 45.0,
            }
        )

    recommended_candidate_order = [
        item["candidate_id"]
        for item in sorted(candidates, key=lambda item: item["aggregate_score"], reverse=True)
    ]
    auto_rejected_candidate_ids = [
        item["candidate_id"] for item in candidates if item["reject_recommendation"]
    ]
    score_id = args.score_id or f"{args.object_id}-scores"
    manifest_path = ensure_repair_candidate_dir(package_dir, args.object_id) / f"{score_id}.json"
    manifest = {
        "score_id": score_id,
        "object_id": args.object_id,
        "workflow_type": args.workflow_type,
        "required_score_keys": REQUIRED_SCORE_KEYS,
        "candidates": [
            {
                "candidate_id": item["candidate_id"],
                "asset_path": item["relative_path"],
                "scores": item["scores"],
                "aggregate_score": item["aggregate_score"],
                "reject_recommendation": item["reject_recommendation"],
            }
            for item in candidates
        ],
        "recommended_candidate_order": recommended_candidate_order,
        "auto_rejected_candidate_ids": auto_rejected_candidate_ids,
        "created_at": utc_timestamp(),
    }
    write_json(manifest_path, manifest)
    print(json.dumps({"score_manifest_path": package_relative(package_dir, manifest_path), **manifest}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
