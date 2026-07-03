import argparse
import json
from pathlib import Path

from generation_brief_lib import build_generation_brief, write_generation_brief


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Write a package-owned generation brief and reference-input manifest for one generate-route object."
    )
    parser.add_argument("package_dir", help="Asset package directory.")
    parser.add_argument("--object-id", required=True)
    parser.add_argument("--source-crop", default="")
    parser.add_argument("--rough-mask", default="")
    parser.add_argument("--rough-localization", default="")
    parser.add_argument("--neighbor-context", default="")
    parser.add_argument("--style-constraint", action="append", default=[])
    parser.add_argument("--must-keep", action="append", default=[])
    parser.add_argument("--must-avoid", action="append", default=[])
    parser.add_argument("--reference-input", action="append", default=[])
    parser.add_argument("--why-not-extract", default="")
    parser.add_argument("--why-not-reconstruct", default="")
    parser.add_argument("--why-generate", default="")
    parser.add_argument("--risk-note", default="")
    args = parser.parse_args()

    package_dir = Path(args.package_dir).resolve()
    try:
        brief, reference_manifest = build_generation_brief(
            package_dir,
            args.object_id,
            source_crop=args.source_crop,
            rough_mask=args.rough_mask,
            rough_localization=args.rough_localization,
            neighbor_context=args.neighbor_context,
            style_constraints=list(args.style_constraint),
            must_keep=list(args.must_keep),
            must_avoid=list(args.must_avoid),
            reference_inputs=list(args.reference_input),
            why_not_extract=args.why_not_extract,
            why_not_reconstruct=args.why_not_reconstruct,
            why_generate=args.why_generate,
            risk_note=args.risk_note,
        )
        brief_path, references_path = write_generation_brief(
            package_dir,
            args.object_id,
            brief,
            reference_manifest,
        )
    except ValueError as exc:
        parser.error(str(exc))

    print(
        json.dumps(
            {
                "generation_brief_path": str(brief_path.relative_to(package_dir)).replace("\\", "/"),
                "reference_inputs_path": str(references_path.relative_to(package_dir)).replace("\\", "/"),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
