import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_command(command: list[str], parser: argparse.ArgumentParser, label: str) -> dict:
    result = subprocess.run(
        command,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        parser.error(result.stderr.strip() or f"{label} failed")
    stdout = result.stdout.strip()
    if not stdout:
        return {}
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {"stdout": stdout}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Record compare winner selection and optionally continue into candidate promotion decision."
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
    parser.add_argument(
        "--promotion-answer",
        choices=["skip", "yes", "no"],
        default="skip",
    )
    parser.add_argument(
        "--delivery-class",
        choices=[
            "clean-extraction",
            "approximate-reconstruction",
            "generated-reconstruction",
            "support-only",
            "draft-candidate",
        ],
    )
    parser.add_argument("--repair-note", default="")
    parser.add_argument("--active-reconstruction-method", default="")
    parser.add_argument("--generation-source", default="")
    parser.add_argument("--generation-model-or-tool", default="")
    parser.add_argument("--generation-version", default="")
    parser.add_argument("--generation-prompt-or-brief-ref", default="")
    parser.add_argument("--generation-reference-input", action="append", default=[])
    args = parser.parse_args()

    package_dir = Path(args.package_dir).resolve()
    scripts_dir = Path(__file__).resolve().parent

    selection_command = [
        sys.executable,
        str(scripts_dir / "record_candidate_selection.py"),
        str(package_dir),
        "--object-id",
        args.object_id,
        "--decision-source",
        args.decision_source,
        "--evidence-ref",
        args.evidence_ref,
    ]
    if args.comparison_id:
        selection_command.extend(["--comparison-id", args.comparison_id])
    if args.provider_id:
        selection_command.extend(["--provider-id", args.provider_id])
    if args.candidate_id:
        selection_command.extend(["--candidate-id", args.candidate_id])
    if args.selection_reason:
        selection_command.extend(["--selection-reason", args.selection_reason])

    selection_payload = run_command(selection_command, parser, "record_candidate_selection.py")

    payload = {
        "object_id": args.object_id,
        "selection": selection_payload,
        "promotion_decision": None,
    }
    if args.promotion_answer == "skip":
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    promotion_command = [
        sys.executable,
        str(scripts_dir / "apply_candidate_promotion_decision.py"),
        str(package_dir),
        "--object-id",
        args.object_id,
        "--comparison-id",
        str(selection_payload.get("comparison_id", "")).strip(),
        "--decision-answer",
        args.promotion_answer,
        "--decision-source",
        args.decision_source,
        "--evidence-ref",
        args.evidence_ref,
    ]
    if args.delivery_class:
        promotion_command.extend(["--delivery-class", args.delivery_class])
    if args.repair_note:
        promotion_command.extend(["--repair-note", args.repair_note])
    if args.active_reconstruction_method:
        promotion_command.extend(["--active-reconstruction-method", args.active_reconstruction_method])
    if args.generation_source:
        promotion_command.extend(["--generation-source", args.generation_source])
    if args.generation_model_or_tool:
        promotion_command.extend(["--generation-model-or-tool", args.generation_model_or_tool])
    if args.generation_version:
        promotion_command.extend(["--generation-version", args.generation_version])
    if args.generation_prompt_or_brief_ref:
        promotion_command.extend(["--generation-prompt-or-brief-ref", args.generation_prompt_or_brief_ref])
    for value in args.generation_reference_input:
        promotion_command.extend(["--generation-reference-input", value])

    payload["promotion_decision"] = run_command(
        promotion_command,
        parser,
        "apply_candidate_promotion_decision.py",
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
