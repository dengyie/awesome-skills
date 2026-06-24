import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


def collect_staging_entries(staging_dir: Path) -> list[Path]:
    return sorted(staging_dir.iterdir(), key=lambda path: path.name)


def move_entry(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(destination))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Archive active intermediate extraction outputs from _staging into _archive_intermediate."
    )
    parser.add_argument("package_dir", help="Asset package directory.")
    parser.add_argument("--run-id", required=True, help="Archive bucket name, such as a run id or timestamp label.")
    args = parser.parse_args()

    package_dir = Path(args.package_dir).resolve()
    staging_dir = package_dir / "_staging"
    archive_dir = package_dir / "_archive_intermediate" / args.run_id
    if not staging_dir.is_dir():
        parser.error(f"_staging directory is missing: {staging_dir}")
    archive_dir.mkdir(parents=True, exist_ok=True)

    archived_paths: list[str] = []
    for entry in collect_staging_entries(staging_dir):
        destination = archive_dir / entry.name
        move_entry(entry, destination)
        if destination.is_dir():
            for child in sorted(destination.rglob("*")):
                if child.is_file():
                    archived_paths.append(str(child.relative_to(archive_dir)).replace("\\", "/"))
        else:
            archived_paths.append(destination.name)

    manifest = {
        "run_id": args.run_id,
        "archived_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "archived_paths": archived_paths,
    }
    (archive_dir / "archive_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Archived intermediates to: {archive_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
