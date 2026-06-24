import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ALLOWED_QA_STATUSES = {"pass", "needs-review", "blocked"}
ALLOWED_QUALITY_CHECK_STATUSES = {"pass", "needs-review", "blocked", "unknown"}
QUALITY_CHECK_ARGS = {
    "mask_alignment": "mask_alignment",
    "alpha_edges": "alpha_edges",
    "background_residue": "background_residue",
    "reuse_readiness": "reuse_readiness",
}
ALLOWED_GRANULARITY_MODES = {
    "module",
    "component",
    "atomic-layer",
    "production-editable",
    "draft",
}
ALLOWED_CAPABILITY_CHOICES = {
    "install-or-activate-tools",
    "external-professional-outputs",
    "draft-packaging-only",
    "production-capable",
    "unset",
}


def read_metadata(package_dir: Path, parser: argparse.ArgumentParser) -> dict:
    metadata_path = package_dir / "metadata.json"
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        parser.error(f"metadata.json is missing: {metadata_path}")
    except json.JSONDecodeError as exc:
        parser.error(f"metadata.json is not valid JSON: {exc}")
    if not isinstance(metadata, dict):
        parser.error("metadata.json must contain an object")
    return metadata


def write_metadata(package_dir: Path, metadata: dict) -> None:
    (package_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def object_map(metadata: dict, parser: argparse.ArgumentParser) -> dict[str, dict]:
    objects = metadata.get("objects", [])
    if not isinstance(objects, list):
        parser.error("metadata.objects must be a list before review can be recorded")
    mapped: dict[str, dict] = {}
    for item in objects:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            mapped[item["id"]] = item
    return mapped


def selected_objects(metadata: dict, args: argparse.Namespace, parser: argparse.ArgumentParser) -> list[dict]:
    mapped = object_map(metadata, parser)
    if args.all_objects:
        return list(mapped.values())
    if not args.object_id:
        return []
    missing = [object_id for object_id in args.object_id if object_id not in mapped]
    if missing:
        parser.error("unknown object-id for review: " + ", ".join(missing))
    return [mapped[object_id] for object_id in args.object_id]


def has_quality_updates(args: argparse.Namespace) -> bool:
    return any(getattr(args, name) is not None for name in QUALITY_CHECK_ARGS)


def update_analysis(metadata: dict, args: argparse.Namespace) -> None:
    analysis = metadata.setdefault("analysis", {})
    if args.visual_hierarchy:
        analysis["visual_hierarchy"] = args.visual_hierarchy
    if args.recommended_split_plan:
        analysis["recommended_split_plan"] = args.recommended_split_plan


def update_quality_gates(metadata: dict, gates: list[str] | None) -> None:
    if not gates:
        return
    pipeline = metadata.setdefault("extraction_pipeline", {})
    quality_gates = pipeline.setdefault("quality_gates", [])
    for gate in gates:
        if gate not in quality_gates:
            quality_gates.append(gate)


def update_granularity(metadata: dict, args: argparse.Namespace) -> None:
    if not args.granularity_mode and not args.granularity_confirmed and not args.granularity_note:
        return
    granularity = metadata.setdefault("granularity", {})
    if args.granularity_mode:
        granularity["mode"] = args.granularity_mode
    if args.granularity_confirmed:
        granularity["user_confirmed"] = True
    if args.granularity_note:
        existing = granularity.get("notes", "")
        if existing:
            granularity["notes"] = existing.rstrip() + "\n" + args.granularity_note
        else:
            granularity["notes"] = args.granularity_note


def update_decision_log(metadata: dict, args: argparse.Namespace) -> None:
    decision_values = [
        args.decision_stage,
        args.decision_question,
        args.decision_recommended,
        args.decision_answer,
        args.decision_effect,
    ]
    if not any(decision_values):
        return
    if not all(decision_values):
        missing = [
            name
            for name, value in [
                ("--decision-stage", args.decision_stage),
                ("--decision-question", args.decision_question),
                ("--decision-recommended", args.decision_recommended),
                ("--decision-answer", args.decision_answer),
                ("--decision-effect", args.decision_effect),
            ]
            if not value
        ]
        raise ValueError("decision log updates require: " + ", ".join(missing))
    decision_log = metadata.setdefault("decision_log", [])
    if not isinstance(decision_log, list):
        raise ValueError("metadata.decision_log must be a list before recording decisions")
    decision_log.append(
        {
            "stage": args.decision_stage,
            "question": args.decision_question,
            "recommended_answer": args.decision_recommended,
            "user_answer": args.decision_answer,
            "decision_effect": args.decision_effect,
        }
    )


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "yes", "1"}:
        return True
    if normalized in {"false", "no", "0"}:
        return False
    raise ValueError("--production-capable must be true or false")


def update_capability(metadata: dict, args: argparse.Namespace) -> None:
    if (
        args.production_capable is None
        and not args.missing_for_production
        and args.capability_user_choice is None
        and args.capability_note is None
    ):
        return
    capability = metadata.setdefault("capability", {})
    if args.production_capable is not None:
        capability["production_capable"] = parse_bool(args.production_capable)
    if args.missing_for_production is not None:
        capability["missing_for_production"] = args.missing_for_production
    elif "missing_for_production" not in capability:
        capability["missing_for_production"] = []
    if args.capability_user_choice is not None:
        if args.capability_user_choice not in ALLOWED_CAPABILITY_CHOICES:
            raise ValueError(
                "--capability-user-choice must be one of: "
                + ", ".join(sorted(ALLOWED_CAPABILITY_CHOICES))
            )
        capability["user_choice"] = args.capability_user_choice
    if args.capability_note is not None:
        capability["notes"] = args.capability_note


def update_object_checks(objects: list[dict], args: argparse.Namespace) -> None:
    for item in objects:
        quality_checks = item.setdefault("quality_checks", {})
        for arg_name, check_name in QUALITY_CHECK_ARGS.items():
            value = getattr(args, arg_name)
            if value is not None:
                quality_checks[check_name] = value
        if args.confirm_crop_layer:
            item["manual_review_confirmed"] = True
            notes = item.setdefault("manual_review_notes", [])
            for note in args.review_note or ["Manual review confirmed crop-only layer."]:
                if note not in notes:
                    notes.append(note)


def all_required_checks_pass(metadata: dict) -> bool:
    objects = metadata.get("objects", [])
    if not isinstance(objects, list) or not objects:
        return False
    required = set(QUALITY_CHECK_ARGS.values())
    for item in objects:
        if not isinstance(item, dict):
            return False
        quality_checks = item.get("quality_checks")
        if not isinstance(quality_checks, dict):
            return False
        if required - set(quality_checks):
            return False
        for check_name in required:
            if quality_checks.get(check_name) != "pass":
                return False
    return True


def append_qa_report(package_dir: Path, args: argparse.Namespace) -> None:
    qa_path = package_dir / "qa_report.md"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = ["", "## Quality Review Update", "", f"- Time: {timestamp}"]
    if args.qa_status:
        lines.append(f"- QA status: {args.qa_status}")
    if args.granularity_mode:
        lines.append(f"- Granularity mode: {args.granularity_mode}")
    if args.granularity_confirmed:
        lines.append("- Granularity confirmed: true")
    if args.granularity_note:
        lines.append(f"- Granularity note: {args.granularity_note}")
    if args.decision_stage:
        lines.append(f"- Decision stage: {args.decision_stage}")
        lines.append(f"- Decision question: {args.decision_question}")
        lines.append(f"- Recommended answer: {args.decision_recommended}")
        lines.append(f"- User answer: {args.decision_answer}")
        lines.append(f"- Decision effect: {args.decision_effect}")
    if args.production_capable is not None:
        lines.append(f"- Production capable: {args.production_capable}")
    if args.missing_for_production:
        lines.append("- Missing for production: " + ", ".join(args.missing_for_production))
    if args.capability_user_choice:
        lines.append(f"- Capability user choice: {args.capability_user_choice}")
    if args.capability_note:
        lines.append(f"- Capability note: {args.capability_note}")
    if args.object_id:
        lines.append("- Objects: " + ", ".join(args.object_id))
    elif args.all_objects:
        lines.append("- Objects: all")
    for note in args.review_note or []:
        lines.append(f"- Note: {note}")
    existing = qa_path.read_text(encoding="utf-8") if qa_path.exists() else ""
    qa_path.write_text(existing.rstrip() + "\n" + "\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Record semantic analysis and manual QA decisions for a split asset package."
    )
    parser.add_argument("package_dir", help="Asset package directory.")
    parser.add_argument("--visual-hierarchy", action="append", help="Semantic layer, repeatable.")
    parser.add_argument("--recommended-split-plan", help="Semantic split plan summary.")
    parser.add_argument("--granularity-mode", choices=sorted(ALLOWED_GRANULARITY_MODES))
    parser.add_argument("--granularity-confirmed", action="store_true")
    parser.add_argument("--granularity-note")
    parser.add_argument("--decision-stage")
    parser.add_argument("--decision-question")
    parser.add_argument("--decision-recommended")
    parser.add_argument("--decision-answer")
    parser.add_argument("--decision-effect")
    parser.add_argument("--production-capable", choices=["true", "false"])
    parser.add_argument("--missing-for-production", action="append")
    parser.add_argument("--capability-user-choice")
    parser.add_argument("--capability-note")
    parser.add_argument("--quality-gate", action="append", help="Pipeline quality gate inspected.")
    parser.add_argument("--object-id", action="append", help="Object id whose quality checks are updated.")
    parser.add_argument("--all-objects", action="store_true", help="Apply quality check updates to all objects.")
    parser.add_argument("--mask-alignment", choices=sorted(ALLOWED_QUALITY_CHECK_STATUSES))
    parser.add_argument("--alpha-edges", choices=sorted(ALLOWED_QUALITY_CHECK_STATUSES))
    parser.add_argument("--background-residue", choices=sorted(ALLOWED_QUALITY_CHECK_STATUSES))
    parser.add_argument("--reuse-readiness", choices=sorted(ALLOWED_QUALITY_CHECK_STATUSES))
    parser.add_argument("--qa-status", choices=sorted(ALLOWED_QA_STATUSES))
    parser.add_argument(
        "--confirm-crop-layer",
        action="store_true",
        help="Record human confirmation that an estimated crop/bbox layer is acceptable.",
    )
    parser.add_argument("--review-note", action="append")
    args = parser.parse_args()

    if args.all_objects and args.object_id:
        parser.error("use either --all-objects or --object-id, not both")
    if has_quality_updates(args) and not args.all_objects and not args.object_id:
        parser.error("quality check updates require --object-id or --all-objects")
    if args.confirm_crop_layer and not args.all_objects and not args.object_id:
        parser.error("--confirm-crop-layer requires --object-id or --all-objects")

    package_dir = Path(args.package_dir).resolve()
    metadata = read_metadata(package_dir, parser)
    targets = selected_objects(metadata, args, parser)

    update_analysis(metadata, args)
    update_granularity(metadata, args)
    try:
        update_decision_log(metadata, args)
        update_capability(metadata, args)
    except ValueError as exc:
        parser.error(str(exc))
    update_quality_gates(metadata, args.quality_gate)
    update_object_checks(targets, args)

    if args.qa_status == "pass" and not all_required_checks_pass(metadata):
        parser.error("cannot set qa-status pass until every required object quality check is pass")
    if args.qa_status:
        metadata.setdefault("qa", {})["status"] = args.qa_status

    write_metadata(package_dir, metadata)
    append_qa_report(package_dir, args)
    print(f"Recorded quality review: {package_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
