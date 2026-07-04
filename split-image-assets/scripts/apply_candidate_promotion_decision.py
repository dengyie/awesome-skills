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
        description="Apply a compare-to-promotion decision by recording approval and optionally promoting."
    )
    parser.add_argument("package_dir", help="Asset package directory.")
    parser.add_argument("--object-id", required=True)
    parser.add_argument("--comparison-id", default="")
    parser.add_argument("--decision-answer", choices=["yes", "no"], required=True)
    parser.add_argument(
        "--decision-source",
        choices=["explicit-user-confirmed", "inferred-from-user"],
        default="explicit-user-confirmed",
    )
    parser.add_argument("--evidence-ref", required=True)
    parser.add_argument("--selection-reason", default="")
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

    approval_command = [
        sys.executable,
        str(scripts_dir / "record_candidate_promotion_approval.py"),
        str(package_dir),
        "--object-id",
        args.object_id,
        "--decision-answer",
        args.decision_answer,
        "--decision-source",
        args.decision_source,
        "--evidence-ref",
        args.evidence_ref,
    ]
    if args.comparison_id:
        approval_command.extend(["--comparison-id", args.comparison_id])
    if args.selection_reason:
        approval_command.extend(["--selection-reason", args.selection_reason])

    approval_payload = run_command(approval_command, parser, "record_candidate_promotion_approval.py")

    payload = {
        "object_id": args.object_id,
        "decision_answer": args.decision_answer,
        "approval": approval_payload,
        "promotion": None,
    }

    if args.decision_answer == "no":
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    if not args.delivery_class:
        parser.error("--delivery-class is required when --decision-answer is yes")
    if not args.repair_note.strip():
        parser.error("--repair-note is required when --decision-answer is yes")

    promote_command = [
        sys.executable,
        str(scripts_dir / "promote_candidate_asset.py"),
        str(package_dir),
        "--object-id",
        args.object_id,
        "--delivery-class",
        args.delivery_class,
        "--repair-note",
        args.repair_note,
    ]
    if args.comparison_id:
        promote_command.extend(["--comparison-id", args.comparison_id])
    if args.active_reconstruction_method:
        promote_command.extend(["--active-reconstruction-method", args.active_reconstruction_method])
    if args.generation_source:
        promote_command.extend(["--generation-source", args.generation_source])
    if args.generation_model_or_tool:
        promote_command.extend(["--generation-model-or-tool", args.generation_model_or_tool])
    if args.generation_version:
        promote_command.extend(["--generation-version", args.generation_version])
    if args.generation_prompt_or_brief_ref:
        promote_command.extend(["--generation-prompt-or-brief-ref", args.generation_prompt_or_brief_ref])
    for value in args.generation_reference_input:
        promote_command.extend(["--generation-reference-input", value])

    promotion_payload = run_command(promote_command, parser, "promote_candidate_asset.py")
    payload["promotion"] = promotion_payload or {"status": "promoted"}
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
