import argparse
from pathlib import Path

from provider_bridge_lib import build_provider_result, write_provider_result


def parse_artifact(values: list[str]) -> dict[str, str]:
    artifacts: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise ValueError("--artifact must use key=package/relative/path")
        key, raw_path = value.split("=", 1)
        key = key.strip()
        raw_path = raw_path.strip()
        if not key or not raw_path:
            raise ValueError("--artifact must use non-empty key and path")
        artifacts[key] = raw_path
    return artifacts


def main() -> int:
    parser = argparse.ArgumentParser(description="Write a provider bridge result manifest for one object.")
    parser.add_argument("package_dir", help="Asset package directory.")
    parser.add_argument("--provider-id", required=True)
    parser.add_argument("--object-id", required=True)
    parser.add_argument("--status", required=True)
    parser.add_argument("--artifact", action="append", default=[])
    parser.add_argument("--tool-name", required=True)
    parser.add_argument("--tool-role", required=True)
    parser.add_argument("--tool-version", required=True)
    parser.add_argument("--execution-mode", required=True)
    parser.add_argument("--warning", action="append", default=[])
    parser.add_argument("--production-ready-hint", choices=["true", "false"], default="false")
    parser.add_argument("--next-expected-provider", default="")
    parser.add_argument("--note", default="")
    args = parser.parse_args()

    try:
        result = build_provider_result(
            Path(args.package_dir).resolve(),
            args.provider_id,
            args.object_id,
            status=args.status,
            artifacts=parse_artifact(args.artifact),
            tool_name=args.tool_name,
            tool_role=args.tool_role,
            tool_version=args.tool_version,
            execution_mode=args.execution_mode,
            warnings=list(args.warning),
            production_ready_hint=args.production_ready_hint == "true",
            next_expected_provider=args.next_expected_provider,
            notes=args.note,
        )
        path = write_provider_result(Path(args.package_dir).resolve(), result)
    except ValueError as exc:
        parser.error(str(exc))
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
