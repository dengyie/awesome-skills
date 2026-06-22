import argparse
import json
import shutil
from pathlib import Path

from PIL import Image


def build_metadata(source_path: Path, package_name: str, width: int, height: int) -> dict:
    return {
        "schema_version": "1.0",
        "package_name": package_name,
        "source": {
            "path": "source/source_original.png",
            "original_path": str(source_path),
            "width": width,
            "height": height,
        },
        "objects": [],
        "previews": {},
        "qa": {
            "status": "needs-review",
            "manual_review_flags": [
                "object inventory has not been completed",
                "asset extraction has not been reviewed",
            ],
        },
    }


def write_qa_report(path: Path, package_name: str) -> None:
    path.write_text(
        "\n".join(
            [
                f"# QA Report: {package_name}",
                "",
                "Final status: needs-review",
                "",
                "## Summary",
                "",
                "- Package initialized.",
                "- Add object assets, masks, previews, and inspection notes before claiming pass.",
                "",
                "## Manual Review Flags",
                "",
                "- object inventory has not been completed",
                "- asset extraction has not been reviewed",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a split image asset package.")
    parser.add_argument("source", help="Source image path.")
    parser.add_argument("output", help="Output asset package directory.")
    parser.add_argument("--package-name", default=None)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    source_path = Path(args.source).resolve()
    output_path = Path(args.output).resolve()
    if not source_path.exists():
        parser.error(f"source image does not exist: {source_path}")

    metadata_path = output_path / "metadata.json"
    if metadata_path.exists() and not args.force:
        parser.error(f"metadata.json already exists; pass --force to overwrite: {metadata_path}")

    for directory in ["source", "assets", "masks", "previews"]:
        (output_path / directory).mkdir(parents=True, exist_ok=True)

    target_source = output_path / "source" / "source_original.png"
    shutil.copy2(source_path, target_source)

    with Image.open(target_source) as image:
        width, height = image.size

    package_name = args.package_name or output_path.name
    metadata = build_metadata(source_path, package_name, width, height)
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_qa_report(output_path / "qa_report.md", package_name)

    print(f"Initialized asset package: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
