import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from candidate_workflow_lib import resolve_candidate_comparison


def read_metadata(package_dir: Path) -> dict:
    return json.loads((package_dir / "metadata.json").read_text(encoding="utf-8"))


def write_metadata(package_dir: Path, metadata: dict) -> None:
    (package_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def find_object(metadata: dict, object_id: str) -> dict | None:
    objects = metadata.get("objects", [])
    if not isinstance(objects, list):
        return None
    for item in objects:
        if isinstance(item, dict) and item.get("id") == object_id:
            return item
    return None


def resolve_candidate_id(
    comparison: dict,
    explicit_candidate_id: str,
    parser: argparse.ArgumentParser,
) -> str:
    candidate_ids = comparison.get("candidate_ids", [])
    if not isinstance(candidate_ids, list) or not all(
        isinstance(item, str) and item.strip() for item in candidate_ids
    ):
        parser.error("comparison candidate_ids must be a list of non-empty strings")
    candidate_id = explicit_candidate_id.strip() if explicit_candidate_id else ""
    if candidate_id:
        if candidate_id not in candidate_ids:
            parser.error(f"--candidate-id {candidate_id} is not part of the selected comparison")
        return candidate_id
    selected = str(comparison.get("selected_candidate_id", "")).strip()
    if selected:
        return selected
    if len(candidate_ids) == 1:
        return candidate_ids[0]
    parser.error(
        "--candidate-id is required unless compare evidence already selects a candidate or references exactly one candidate"
    )
    raise AssertionError("unreachable")


def resolve_selection_reason(
    comparison: dict,
    explicit_reason: str,
    parser: argparse.ArgumentParser,
) -> str:
    reason = explicit_reason.strip() if explicit_reason else ""
    if reason:
        return reason
    recorded = str(comparison.get("selection_reason", "")).strip()
    if recorded:
        return recorded
    parser.error(
        "--selection-reason is required unless compare evidence already records selection_reason"
    )
    raise AssertionError("unreachable")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Record selected compare candidate and selection rationale with a low-burden adapter."
    )
    parser.add_argument("package_dir", help="Asset package directory.")
    parser.add_argument("--object-id", required=True)
    parser.add_argument("--comparison-id", default="")
    parser.add_argument("--provider-id", default="")
    parser.add_argument("--candidate-id", default="")
    parser.add_argument("--selection-reason", default="")
    parser.add_argument(
        "--decision-source",
        choices=["explicit-user-confirmed", "inferred-from-user"],
        default="explicit-user-confirmed",
    )
    parser.add_argument("--evidence-ref", required=True)
    args = parser.parse_args()

    package_dir = Path(args.package_dir).resolve()
    metadata = read_metadata(package_dir)
    target = find_object(metadata, args.object_id)
    if target is None:
        parser.error(f"unknown object-id: {args.object_id}")

    try:
        comparison = resolve_candidate_comparison(
            package_dir, target, args.comparison_id, args.provider_id
        )
    except ValueError as exc:
        parser.error(str(exc))

    comparison_id = str(comparison.get("comparison_id", "")).strip()
    candidate_id = resolve_candidate_id(comparison, args.candidate_id, parser)
    selection_reason = resolve_selection_reason(comparison, args.selection_reason, parser)

    review_script = package_dir.parent / "split-image-assets" / "scripts" / "record_quality_review.py"
    if not review_script.exists():
        review_script = Path(__file__).resolve().parent / "record_quality_review.py"

    question = f"Select {candidate_id} as the chosen compare candidate?"
    effect = f"Record {candidate_id} as the selected candidate for later approval and promotion."
    result = subprocess.run(
        [
            sys.executable,
            str(review_script),
            str(package_dir),
            "--object-id",
            args.object_id,
            "--selected-candidate-id",
            candidate_id,
            "--decision-stage",
            "candidate-selection",
            "--decision-question",
            question,
            "--decision-recommended",
            candidate_id,
            "--decision-answer",
            candidate_id,
            "--decision-effect",
            effect,
            "--decision-source",
            args.decision_source,
            "--pause-category",
            "user-decision",
            "--blocking",
            "false",
            "--evidence-ref",
            args.evidence_ref,
            "--review-note",
            f"Selected compare candidate {candidate_id}: {selection_reason}",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        parser.error(result.stderr.strip() or "record_quality_review.py failed")

    metadata = read_metadata(package_dir)
    target = find_object(metadata, args.object_id)
    if target is None:
        parser.error(f"unknown object-id after review update: {args.object_id}")
    comparisons = target.get("candidate_comparisons", [])
    if not isinstance(comparisons, list):
        parser.error("target object candidate_comparisons must be a list when present")
    latest = next(
        (
            item
            for item in comparisons
            if isinstance(item, dict) and item.get("comparison_id") == comparison_id
        ),
        None,
    )
    if latest is None:
        parser.error(f"comparison disappeared after review update: {comparison_id}")
    latest["selected_candidate_id"] = candidate_id
    latest["selection_reason"] = selection_reason
    latest["selected_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    target["selected_candidate_id"] = candidate_id
    write_metadata(package_dir, metadata)

    payload = {
        "object_id": args.object_id,
        "comparison_id": comparison_id,
        "candidate_id": candidate_id,
        "selection_reason": selection_reason,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
