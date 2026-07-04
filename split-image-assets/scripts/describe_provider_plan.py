import argparse
import json
from pathlib import Path

from provider_bridge_lib import build_provider_plan_summary, write_provider_plan_summary


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Write a provider-plan summary for the current package plan_manifest."
    )
    parser.add_argument("package_dir", help="Asset package directory.")
    parser.add_argument("--object-id", help="Optional object id filter.", default="")
    args = parser.parse_args()

    try:
        package_dir = Path(args.package_dir).resolve()
        summary = build_provider_plan_summary(package_dir, args.object_id)
        path = write_provider_plan_summary(package_dir, summary)
    except ValueError as exc:
        parser.error(str(exc))

    payload = {
        "provider_plan_path": str(path.relative_to(package_dir)).replace("\\", "/"),
        "object_count": len(summary["objects"]),
        "objects": summary["objects"],
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
