import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw
from candidate_workflow_lib import load_provider_stage_manifest
from package_state_lib import find_plan_object, read_plan_manifest


def read_metadata(package_dir: Path) -> dict:
    return json.loads((package_dir / "metadata.json").read_text(encoding="utf-8"))


def write_metadata(package_dir: Path, metadata: dict) -> None:
    (package_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def package_path(package_dir: Path, value: str, label: str, parser: argparse.ArgumentParser) -> Path:
    if not isinstance(value, str) or not value.strip():
        parser.error(f"{label} must be a package-relative path")
    raw_path = Path(value)
    if raw_path.is_absolute():
        parser.error(f"{label} must stay inside the package: {value}")
    resolved = (package_dir / raw_path).resolve()
    package_root = package_dir.resolve()
    if resolved != package_root and package_root not in resolved.parents:
        parser.error(f"{label} must stay inside the package: {value}")
    return resolved


def require_repair_candidate_path(path: Path, package_dir: Path, label: str, parser: argparse.ArgumentParser) -> None:
    expected_root = (package_dir / "_staging" / "repair_candidates").resolve()
    if path != expected_root and expected_root not in path.parents:
        parser.error(f"{label} must be staged under _staging/repair_candidates/: {path}")


def parse_candidate_arg(value: str, parser: argparse.ArgumentParser) -> tuple[str, str]:
    if "=" not in value:
        parser.error("--candidate must use candidate_id=package/relative/path.png")
    candidate_id, asset_path = value.split("=", 1)
    candidate_id = candidate_id.strip()
    asset_path = asset_path.strip()
    if not candidate_id or not asset_path:
        parser.error("--candidate must use candidate_id=package/relative/path.png")
    return candidate_id, asset_path


def auto_discover_generated_candidates(
    package_dir: Path,
    object_id: str,
    provider_id: str = "",
) -> list[tuple[str, str, str]]:
    candidate_dir = package_dir / "_staging" / "repair_candidates" / object_id
    if not candidate_dir.exists():
        return []
    discovered: list[tuple[str, str, str]] = []
    for asset_path in sorted(candidate_dir.glob("*.png")):
        if asset_path.name.endswith("_mask.png"):
            continue
        candidate_id = asset_path.stem
        provider_stage_path = asset_path.with_name(f"{candidate_id}_provider_stage.json")
        if not provider_stage_path.exists():
            continue
        try:
            provider_stage = load_provider_stage_manifest(asset_path, candidate_id)
        except ValueError:
            continue
        candidate_provider_id = str(provider_stage.get("provider_id", "")).strip()
        if provider_id and candidate_provider_id != provider_id:
            continue
        discovered.append(
            (
                candidate_id,
                str(asset_path.relative_to(package_dir)).replace("\\", "/"),
                candidate_provider_id,
            )
        )
    return discovered


def candidate_records_for_manifest(candidates: list[dict]) -> list[dict]:
    records = []
    for item in candidates:
        record = {
            "candidate_id": item["candidate_id"],
            "asset_path": item["relative_path"],
            "score_manifest_path": item.get("score_manifest_path", ""),
            "scores": item.get("scores"),
            "aggregate_score": item.get("aggregate_score"),
        }
        provider_stage = item.get("provider_stage_manifest", {})
        if provider_stage:
            record["provider_stage_manifest_path"] = item.get("provider_stage_manifest_path", "")
            record["provider_id"] = provider_stage.get("provider_id", "")
            record["provider_request_path"] = provider_stage.get("provider_request_path", "")
            record["provider_result_path"] = provider_stage.get("provider_result_path", "")
            for field_name in [
                "generation_source",
                "generation_model_or_tool",
                "generation_version",
                "generation_prompt_or_brief_ref",
                "generation_reference_inputs",
            ]:
                record[field_name] = provider_stage.get(field_name, [] if field_name == "generation_reference_inputs" else "")
        records.append(record)
    return records


def make_checkerboard(size: tuple[int, int], cell: int = 8) -> Image.Image:
    image = Image.new("RGBA", size, (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], cell):
        for x in range(0, size[0], cell):
            if (x // cell + y // cell) % 2:
                draw.rectangle([x, y, x + cell - 1, y + cell - 1], fill=(220, 220, 220, 255))
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


def build_compare_contact_sheet(candidates: list[dict], output_path: Path) -> None:
    cell_width = 220
    cell_height = 190
    columns = max(1, len(candidates))
    canvas = Image.new("RGBA", (cell_width * columns, cell_height), (245, 245, 245, 255))
    draw = ImageDraw.Draw(canvas)
    for index, candidate in enumerate(candidates):
        left = index * cell_width
        panel = make_checkerboard((cell_width, cell_height - 30))
        with Image.open(candidate["asset_path"]) as opened:
            paste_thumbnail(panel, opened.convert("RGBA"), (10, 10, cell_width - 10, cell_height - 45))
        canvas.alpha_composite(panel, (left, 0))
        draw.rectangle([left, 0, left + cell_width - 1, cell_height - 1], outline=(100, 120, 150, 255), width=2)
        draw.text((left + 8, cell_height - 22), candidate["candidate_id"][:28], fill=(20, 20, 20, 255))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output_path)


def append_qa_report(
    package_dir: Path,
    object_id: str,
    comparison_id: str,
    compare_note: str,
    compare_criteria: list[str],
) -> None:
    qa_path = package_dir / "qa_report.md"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "",
        "## Candidate Comparison",
        "",
        f"- Time: {timestamp}",
        f"- Object: {object_id}",
        f"- Comparison id: {comparison_id}",
        f"- Criteria: {', '.join(compare_criteria)}",
    ]
    if compare_note:
        lines.append(f"- Note: {compare_note}")
    existing = qa_path.read_text(encoding="utf-8") if qa_path.exists() else ""
    qa_path.write_text(existing.rstrip() + "\n" + "\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate candidate comparison evidence for staged repair candidates."
    )
    parser.add_argument("package_dir", help="Asset package directory.")
    parser.add_argument("--object-id", required=True, help="Target object id.")
    parser.add_argument(
        "--candidate",
        action="append",
        help="Candidate pair in the form candidate_id=package/relative/path.png",
    )
    parser.add_argument("--compare-note", default="", help="Short note about the comparison context.")
    parser.add_argument("--compare-criterion", action="append", help="Criterion used in the comparison.")
    parser.add_argument("--review-focus", action="append", help="Focus area for human review.")
    parser.add_argument("--risk", action="append", help="Known risk to watch during comparison.")
    parser.add_argument("--provider-id", help="Restrict generated candidate auto-discovery to one provider id.")
    parser.add_argument(
        "--score-manifest",
        help="Package-relative candidate score manifest from score_candidate_assets.py.",
    )
    parser.add_argument("--comparison-id", help="Explicit comparison id. Defaults to object id plus timestamp.")
    args = parser.parse_args()

    package_dir = Path(args.package_dir).resolve()
    metadata = read_metadata(package_dir)
    target = next(
        (
            item
            for item in metadata.get("objects", [])
            if isinstance(item, dict) and item.get("id") == args.object_id
        ),
        None,
    )
    if target is None:
        parser.error(f"unknown object-id: {args.object_id}")
    plan_manifest = read_plan_manifest(package_dir)
    plan_object = find_plan_object(plan_manifest, args.object_id) if isinstance(plan_manifest, dict) else None
    require_generated_stage_evidence = (
        isinstance(plan_object, dict) and str(plan_object.get("planned_route", "")).strip() == "generate"
    )
    generated_route = require_generated_stage_evidence

    candidate_args = list(args.candidate or [])
    if not candidate_args:
        if generated_route:
            discovered = auto_discover_generated_candidates(
                package_dir, args.object_id, args.provider_id or ""
            )
            if not args.provider_id and discovered:
                provider_ids = {provider_id for _, _, provider_id in discovered if provider_id}
                if len(provider_ids) > 1:
                    preferred_provider = ""
                    if isinstance(plan_manifest, dict):
                        preferences = plan_manifest.get("provider_preferences", {})
                        if isinstance(preferences, dict):
                            preferred_provider = str(
                                preferences.get("generation_provider_class", "")
                            ).strip()
                    if preferred_provider and preferred_provider in provider_ids:
                        discovered = [
                            item for item in discovered if item[2] == preferred_provider
                        ]
                    else:
                        parser.error(
                            "multiple generated compare providers discovered; supply --provider-id"
                        )
            candidate_args = [
                f"{candidate_id}={relative_path}"
                for candidate_id, relative_path, _ in discovered
            ]
        if not candidate_args:
            parser.error("at least one --candidate is required unless generated candidates can be auto-discovered")

    score_manifest_data = None
    score_by_candidate: dict[str, dict] = {}
    score_manifest_path_rel = ""
    if args.score_manifest:
        score_manifest_path = package_path(package_dir, args.score_manifest, "score manifest", parser)
        try:
            score_manifest_data = json.loads(score_manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            parser.error(f"score manifest is not valid JSON: {exc}")
        if not isinstance(score_manifest_data, dict):
            parser.error("score manifest must contain an object")
        candidates_block = score_manifest_data.get("candidates")
        if not isinstance(candidates_block, list):
            parser.error("score manifest must contain candidates")
        score_manifest_path_rel = str(score_manifest_path.relative_to(package_dir)).replace("\\", "/")
        for entry in candidates_block:
            if not isinstance(entry, dict):
                parser.error("score manifest candidates must be objects")
            candidate_id = entry.get("candidate_id")
            if isinstance(candidate_id, str) and candidate_id.strip():
                score_by_candidate[candidate_id] = entry

    candidates: list[dict] = []
    requested_candidate_ids: list[str] = []
    for value in candidate_args:
        candidate_id, relative_path = parse_candidate_arg(value, parser)
        requested_candidate_ids.append(candidate_id)
        asset_path = package_path(package_dir, relative_path, f"candidate {candidate_id}", parser)
        require_repair_candidate_path(asset_path, package_dir, f"candidate {candidate_id}", parser)
        if not asset_path.exists():
            parser.error(f"candidate asset is missing: {asset_path}")
        score_entry = score_by_candidate.get(candidate_id, {})
        provider_stage_manifest = {}
        provider_stage_manifest_path = ""
        try:
            provider_stage_manifest = load_provider_stage_manifest(asset_path, candidate_id)
        except ValueError as exc:
            parser.error(str(exc))
        if provider_stage_manifest:
            provider_stage_manifest_path = str(
                (asset_path.parent / f"{candidate_id}_provider_stage.json").relative_to(package_dir)
            ).replace("\\", "/")
        elif require_generated_stage_evidence:
            parser.error(
                f"generated compare candidates require provider stage evidence: {candidate_id}"
            )
        candidates.append(
            {
                "candidate_id": candidate_id,
                "relative_path": relative_path,
                "asset_path": asset_path,
                "score_manifest_path": score_manifest_path_rel,
                "scores": score_entry.get("scores"),
                "aggregate_score": score_entry.get("aggregate_score"),
                "provider_stage_manifest": provider_stage_manifest,
                "provider_stage_manifest_path": provider_stage_manifest_path,
            }
        )

    if args.score_manifest:
        missing_score_candidates = [
            candidate_id for candidate_id in requested_candidate_ids if candidate_id not in score_by_candidate
        ]
        if missing_score_candidates:
            parser.error(
                "score manifest is missing entries for compare candidates: "
                + ", ".join(missing_score_candidates)
            )

    if not args.compare_criterion:
        parser.error("at least one --compare-criterion is required")

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    comparison_id = args.comparison_id or (
        f"{args.object_id}-compare-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    )
    compare_artifact_path = (
        package_dir / "_staging" / "repair_candidates" / f"{comparison_id}_compare.png"
    )
    compare_manifest_path = (
        package_dir / "_staging" / "repair_candidates" / f"{comparison_id}_compare.json"
    )
    build_compare_contact_sheet(candidates, compare_artifact_path)
    compare_manifest_path.write_text(
        json.dumps(
            {
                "comparison_id": comparison_id,
                "object_id": args.object_id,
                "candidate_ids": [item["candidate_id"] for item in candidates],
                "candidates": candidate_records_for_manifest(candidates),
                "compare_artifact_path": str(compare_artifact_path.relative_to(package_dir)).replace("\\", "/"),
                "compare_note": args.compare_note,
                "compare_criteria": args.compare_criterion or [],
                "review_focus": args.review_focus or (["generated fidelity"] if generated_route else []),
                "risks": args.risk or (["prompt drift"] if generated_route else []),
                "score_manifest_path": score_manifest_path_rel,
                "recommended_candidate_order": score_manifest_data.get("recommended_candidate_order", [])
                if isinstance(score_manifest_data, dict)
                else [],
                "auto_rejected_candidate_ids": score_manifest_data.get("auto_rejected_candidate_ids", [])
                if isinstance(score_manifest_data, dict)
                else [],
                "created_at": timestamp,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    comparisons = target.setdefault("candidate_comparisons", [])
    if not isinstance(comparisons, list):
        parser.error("target object candidate_comparisons must be a list when present")
    comparisons.append(
        {
            "comparison_id": comparison_id,
            "object_id": args.object_id,
            "candidate_ids": [item["candidate_id"] for item in candidates],
            "compare_artifact_path": str(compare_artifact_path.relative_to(package_dir)).replace("\\", "/"),
            "compare_manifest_path": str(compare_manifest_path.relative_to(package_dir)).replace("\\", "/"),
            "compare_note": args.compare_note,
            "compare_criteria": args.compare_criterion or [],
            "review_focus": args.review_focus or (["generated fidelity"] if generated_route else []),
            "risks": args.risk or (["prompt drift"] if generated_route else []),
            "score_manifest_path": score_manifest_path_rel,
            "selected_candidate_id": "",
            "selection_reason": "",
            "created_at": timestamp,
        }
    )
    write_metadata(package_dir, metadata)
    append_qa_report(package_dir, args.object_id, comparison_id, args.compare_note, args.compare_criterion or [])
    print(f"Candidate comparison written: {compare_artifact_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
