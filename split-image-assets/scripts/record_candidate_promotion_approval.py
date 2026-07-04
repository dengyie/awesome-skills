import argparse
import json
import subprocess
import sys
from pathlib import Path

from candidate_workflow_lib import list_staged_candidate_records, resolve_candidate_comparison


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


def resolve_single_staged_candidate(
    package_dir: Path, object_id: str, provider_id: str, parser: argparse.ArgumentParser
) -> tuple[str, str]:
    candidates = list_staged_candidate_records(package_dir, object_id)
    if provider_id:
        candidates = [
            record for record in candidates if str(record.get("provider_id", "")).strip() == provider_id
        ]
    if len(candidates) == 1:
        return str(candidates[0]["candidate_id"]), str(candidates[0]["relative_asset_path"])
    if not candidates:
        parser.error(
            "candidate promotion approval requires compare evidence or exactly one staged candidate"
        )
    parser.error(
        "candidate promotion approval requires compare evidence with selected_candidate_id or exactly one staged candidate"
    )
    raise AssertionError("unreachable")


def resolve_candidate_id(comparison: dict, parser: argparse.ArgumentParser) -> str:
    selected = str(comparison.get("selected_candidate_id", "")).strip()
    if selected:
        return selected
    candidate_ids = comparison.get("candidate_ids", [])
    if not isinstance(candidate_ids, list) or not all(
        isinstance(item, str) and item.strip() for item in candidate_ids
    ):
        parser.error("comparison candidate_ids must be a list of non-empty strings")
    if len(candidate_ids) == 1:
        return candidate_ids[0]
    parser.error(
        "candidate promotion approval requires compare evidence with selected_candidate_id or exactly one candidate"
    )
    raise AssertionError("unreachable")


def resolve_selection_reason(
    comparison: dict,
    explicit_reason: str,
    decision_answer: str,
    parser: argparse.ArgumentParser,
) -> str:
    reason = explicit_reason.strip() if explicit_reason else ""
    if reason:
        return reason
    recorded = str(comparison.get("selection_reason", "")).strip()
    if recorded:
        return recorded
    if decision_answer.strip().lower() in {"yes", "y", "approve", "approved"}:
        parser.error(
            "--selection-reason is required unless compare evidence already records selection_reason"
        )
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Record candidate promotion approval from compare evidence with a low-burden adapter."
    )
    parser.add_argument("package_dir", help="Asset package directory.")
    parser.add_argument("--object-id", required=True)
    parser.add_argument("--comparison-id", default="")
    parser.add_argument("--provider-id", default="")
    parser.add_argument("--decision-answer", choices=["yes", "no"], required=True)
    parser.add_argument(
        "--decision-source",
        choices=["explicit-user-confirmed", "inferred-from-user"],
        default="explicit-user-confirmed",
    )
    parser.add_argument("--evidence-ref", required=True)
    parser.add_argument("--selection-reason", default="")
    args = parser.parse_args()

    package_dir = Path(args.package_dir).resolve()
    metadata = read_metadata(package_dir)
    target = find_object(metadata, args.object_id)
    if target is None:
        parser.error(f"unknown object-id: {args.object_id}")

    comparison = None
    comparison_id = ""
    candidate_id = ""
    candidate_asset_path = ""
    selection_reason = ""
    candidate_comparisons = target.get("candidate_comparisons", [])
    has_comparisons = isinstance(candidate_comparisons, list) and bool(candidate_comparisons)
    if args.comparison_id or (args.provider_id and has_comparisons) or len(candidate_comparisons) == 1:
        try:
            comparison = resolve_candidate_comparison(
                package_dir, target, args.comparison_id, args.provider_id
            )
        except ValueError as exc:
            parser.error(str(exc))
        comparison_id = str(comparison.get("comparison_id", "")).strip()
        candidate_id = resolve_candidate_id(comparison, parser)
        selection_reason = resolve_selection_reason(
            comparison, args.selection_reason, args.decision_answer, parser
        )
    else:
        candidate_id, candidate_asset_path = resolve_single_staged_candidate(
            package_dir, args.object_id, args.provider_id, parser
        )
        selection_reason = resolve_selection_reason(
            {"selection_reason": ""},
            args.selection_reason,
            args.decision_answer,
            parser,
        )

    if args.decision_answer == "yes":
        if comparison is not None:
            comparison["selected_candidate_id"] = candidate_id
            comparison["selection_reason"] = selection_reason
        write_metadata(package_dir, metadata)

    effect = (
        f"Promote {candidate_id} as the active revision."
        if args.decision_answer == "yes"
        else "Keep the current revision active."
    )
    question = f"Promote {candidate_id} over the current revision?"

    review_script = package_dir.parent / "split-image-assets" / "scripts" / "record_quality_review.py"
    if not review_script.exists():
        review_script = Path(__file__).resolve().parent / "record_quality_review.py"

    result = subprocess.run(
        [
            sys.executable,
            str(review_script),
            str(package_dir),
            "--object-id",
            args.object_id,
            "--decision-stage",
            "final-promotion-acceptance",
            "--decision-question",
            question,
            "--decision-recommended",
            "yes",
            "--decision-answer",
            args.decision_answer,
            "--decision-effect",
            effect,
            "--decision-source",
            args.decision_source,
            "--pause-category",
            "formal-approval",
            "--blocking",
            "true",
            "--evidence-ref",
            args.evidence_ref,
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        parser.error(result.stderr.strip() or "record_quality_review.py failed")

    payload = {
        "object_id": args.object_id,
        "comparison_id": comparison_id,
        "candidate_id": candidate_id,
        "candidate_asset_path": candidate_asset_path,
        "decision_answer": args.decision_answer,
        "selection_reason": selection_reason,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
