import argparse
import json
from pathlib import Path

from provider_bridge_lib import (
    build_provider_plan_summary,
    build_provider_work_item_status,
    write_provider_plan_summary,
    write_provider_work_item_status,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Write provider work-item status for the current package plan and bridge artifacts."
    )
    parser.add_argument("package_dir", help="Asset package directory.")
    parser.add_argument("--object-id", help="Optional object id filter.", default="")
    args = parser.parse_args()

    try:
        package_dir = Path(args.package_dir).resolve()
        provider_plan = build_provider_plan_summary(package_dir, args.object_id)
        provider_plan_path = write_provider_plan_summary(package_dir, provider_plan)
        status = build_provider_work_item_status(package_dir, args.object_id)
        status_path = write_provider_work_item_status(package_dir, status)
    except ValueError as exc:
        parser.error(str(exc))

    payload = {
        "provider_plan_path": str(provider_plan_path.relative_to(package_dir)).replace("\\", "/"),
        "provider_work_items_path": str(status_path.relative_to(package_dir)).replace("\\", "/"),
        "object_count": len(status["objects"]),
        "objects": status["objects"],
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
