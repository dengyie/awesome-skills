import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw


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


def candidate_records_for_manifest(candidates: list[dict]) -> list[dict]:
    return [
        {
            "candidate_id": item["candidate_id"],
            "asset_path": item["relative_path"],
        }
        for item in candidates
    ]


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
        required=True,
        help="Candidate pair in the form candidate_id=package/relative/path.png",
    )
    parser.add_argument("--compare-note", default="", help="Short note about the comparison context.")
    parser.add_argument("--compare-criterion", action="append", help="Criterion used in the comparison.")
    parser.add_argument("--review-focus", action="append", help="Focus area for human review.")
    parser.add_argument("--risk", action="append", help="Known risk to watch during comparison.")
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

    candidates: list[dict] = []
    for value in args.candidate:
        candidate_id, relative_path = parse_candidate_arg(value, parser)
        asset_path = package_path(package_dir, relative_path, f"candidate {candidate_id}", parser)
        require_repair_candidate_path(asset_path, package_dir, f"candidate {candidate_id}", parser)
        if not asset_path.exists():
            parser.error(f"candidate asset is missing: {asset_path}")
        candidates.append(
            {
                "candidate_id": candidate_id,
                "relative_path": relative_path,
                "asset_path": asset_path,
            }
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
                "review_focus": args.review_focus or [],
                "risks": args.risk or [],
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
            "review_focus": args.review_focus or [],
            "risks": args.risk or [],
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
