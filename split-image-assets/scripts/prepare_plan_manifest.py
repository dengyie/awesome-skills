import argparse
from pathlib import Path

from package_state_lib import read_plan_manifest, write_plan_manifest
from semantic_scope_lib import (
    ALLOWED_RESOURCE_FAMILIES,
    default_scope_selection,
    is_weak_autonomy_evidence,
)


ALLOWED_SELECTION_SOURCES = {
    "unresolved",
    "explicit-user-confirmed",
    "inferred-from-user",
}


def normalize_families(values: list[str]) -> list[str]:
    deduped: list[str] = []
    for value in values:
        family = str(value).strip()
        if not family:
            continue
        if family not in ALLOWED_RESOURCE_FAMILIES:
            raise ValueError(f"candidate_family must be one of: {', '.join(sorted(ALLOWED_RESOURCE_FAMILIES))}")
        if family not in deduped:
            deduped.append(family)
    return deduped


def validate_scope_selection(scope_selection: dict) -> dict:
    candidate_families = normalize_families(scope_selection.get("candidate_families", []))
    selected_family = str(scope_selection.get("selected_family", "")).strip()
    selection_source = str(scope_selection.get("selection_source", "unresolved")).strip() or "unresolved"
    selection_evidence_ref = str(scope_selection.get("selection_evidence_ref", "")).strip()
    selection_notes = str(scope_selection.get("selection_notes", "")).strip()

    if selection_source not in ALLOWED_SELECTION_SOURCES:
        raise ValueError(
            f"selection_source must be one of: {', '.join(sorted(ALLOWED_SELECTION_SOURCES))}"
        )
    if selected_family:
        if selected_family not in ALLOWED_RESOURCE_FAMILIES:
            raise ValueError(
                f"selected_family must be one of: {', '.join(sorted(ALLOWED_RESOURCE_FAMILIES))}"
            )
        if candidate_families and selected_family not in candidate_families:
            raise ValueError("selected_family must be included in scope_selection.candidate_families")
        if selection_source == "unresolved":
            raise ValueError("selection_source is required when selected_family is recorded")
    elif selection_source != "unresolved":
        raise ValueError("selected_family is required when selection_source is not unresolved")

    if selection_source == "inferred-from-user":
        if not selection_evidence_ref:
            raise ValueError("selection_evidence_ref is required for inferred-from-user scope selection")
        if is_weak_autonomy_evidence(selection_evidence_ref):
            raise ValueError("inferred scope selection has insufficient evidence for semantic branch selection")

    validated = default_scope_selection()
    validated["candidate_families"] = candidate_families
    validated["selected_family"] = selected_family
    validated["selection_source"] = selection_source
    validated["selection_evidence_ref"] = selection_evidence_ref
    validated["selection_notes"] = selection_notes
    return validated


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare or update plan_manifest.json scope selection.")
    parser.add_argument("package_dir", help="Asset package directory.")
    parser.add_argument(
        "--candidate-family",
        action="append",
        dest="candidate_families",
        default=None,
        help="Candidate resource family for the package scope. Repeatable.",
    )
    parser.add_argument("--selected-family", default=None, help="Selected package resource family.")
    parser.add_argument(
        "--selection-source",
        default=None,
        help="Selection source: unresolved, explicit-user-confirmed, or inferred-from-user.",
    )
    parser.add_argument(
        "--selection-evidence-ref",
        default=None,
        help="Evidence ref supporting an inferred selection.",
    )
    parser.add_argument("--selection-notes", default=None, help="Optional scope selection notes.")
    parser.add_argument(
        "--clear-candidate-families",
        action="store_true",
        help="Clear scope_selection.candidate_families before applying explicit updates.",
    )
    parser.add_argument(
        "--clear-selection",
        action="store_true",
        help="Clear selected_family, selection_source, selection_evidence_ref, and selection_notes before applying explicit updates.",
    )
    return parser.parse_args()


def apply_scope_selection_update(existing: dict, args: argparse.Namespace) -> dict:
    scope_selection = dict(existing)
    if args.clear_candidate_families:
        scope_selection["candidate_families"] = []
    if args.clear_selection:
        scope_selection["selected_family"] = ""
        scope_selection["selection_source"] = "unresolved"
        scope_selection["selection_evidence_ref"] = ""
        scope_selection["selection_notes"] = ""
    if args.candidate_families is not None:
        scope_selection["candidate_families"] = list(args.candidate_families)
    if args.selected_family is not None:
        scope_selection["selected_family"] = args.selected_family
    if args.selection_source is not None:
        scope_selection["selection_source"] = args.selection_source
    if args.selection_evidence_ref is not None:
        scope_selection["selection_evidence_ref"] = args.selection_evidence_ref
    if args.selection_notes is not None:
        scope_selection["selection_notes"] = args.selection_notes
    return scope_selection


def main() -> int:
    args = parse_args()
    package_dir = Path(args.package_dir).resolve()
    plan_manifest = read_plan_manifest(package_dir)
    if plan_manifest is None:
        raise ValueError("plan_manifest.json must exist before preparing scope selection")

    scope_selection = apply_scope_selection_update(
        dict(plan_manifest.get("scope_selection") or {}),
        args,
    )
    plan_manifest["scope_selection"] = validate_scope_selection(scope_selection)
    write_plan_manifest(package_dir, plan_manifest)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as exc:
        raise SystemExit(str(exc))
