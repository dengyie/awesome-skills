import argparse
import json
import subprocess
import sys
from pathlib import Path

from candidate_workflow_lib import list_staged_candidate_records


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


def load_compare_manifest(package_dir: Path, comparison: dict, parser: argparse.ArgumentParser) -> dict:
    compare_manifest_path = str(comparison.get("compare_manifest_path", "")).strip()
    if not compare_manifest_path:
        return {}
    path = (package_dir / compare_manifest_path).resolve()
    if not path.exists():
        parser.error(f"compare manifest is missing: {compare_manifest_path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        parser.error(f"compare manifest is not valid JSON: {exc}")
    if not isinstance(data, dict):
        parser.error("compare manifest must contain an object")
    return data


def _comparison_matches_provider(package_dir: Path, comparison: dict, provider_id: str, parser: argparse.ArgumentParser) -> bool:
    compare_manifest = load_compare_manifest(package_dir, comparison, parser)
    if not compare_manifest:
        return False
    selected_candidate_id = str(comparison.get("selected_candidate_id", "")).strip()
    candidates = compare_manifest.get("candidates", [])
    if not isinstance(candidates, list):
        return False
    provider_matches: list[dict] = []
    for item in candidates:
        if not isinstance(item, dict):
            continue
        if str(item.get("provider_id", "")).strip() != provider_id:
            continue
        provider_matches.append(item)
    if not provider_matches:
        return False
    if selected_candidate_id:
        return any(str(item.get("candidate_id", "")).strip() == selected_candidate_id for item in provider_matches)
    return len(provider_matches) == len(candidates)


def resolve_comparison(
    package_dir: Path,
    target: dict,
    comparison_id: str,
    provider_id: str,
    parser: argparse.ArgumentParser,
) -> dict:
    comparisons = target.get("candidate_comparisons", [])
    if not isinstance(comparisons, list):
        parser.error("target object candidate_comparisons must be a list when present")
    explicit_id = comparison_id.strip() if comparison_id else ""
    if explicit_id:
        comparison = next(
            (
                item
                for item in comparisons
                if isinstance(item, dict) and item.get("comparison_id") == explicit_id
            ),
            None,
        )
        if comparison is None:
            parser.error(f"unknown comparison-id: {explicit_id}")
        if provider_id and not _comparison_matches_provider(package_dir, comparison, provider_id, parser):
            parser.error(f"comparison-id {explicit_id} does not match provider-id: {provider_id}")
        return comparison
    if provider_id:
        matches = [
            item
            for item in comparisons
            if isinstance(item, dict) and _comparison_matches_provider(package_dir, item, provider_id, parser)
        ]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            parser.error(
                f"multiple candidate comparisons match provider-id {provider_id}; supply --comparison-id"
            )
    if len(comparisons) == 1 and isinstance(comparisons[0], dict):
        return comparisons[0]
    parser.error("--comparison-id is required unless exactly one candidate comparison exists")
    raise AssertionError("unreachable")


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
        comparison = resolve_comparison(package_dir, target, args.comparison_id, args.provider_id, parser)
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
