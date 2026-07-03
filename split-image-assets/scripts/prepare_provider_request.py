import argparse
from pathlib import Path

from provider_bridge_lib import build_provider_request, write_provider_request


def parse_input_ref(values: list[str]) -> dict[str, str]:
    refs: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise ValueError("--input-ref must use key=package/relative/path")
        key, raw_path = value.split("=", 1)
        key = key.strip()
        raw_path = raw_path.strip()
        if not key or not raw_path:
            raise ValueError("--input-ref must use non-empty key and path")
        refs[key] = raw_path
    return refs


def main() -> int:
    parser = argparse.ArgumentParser(description="Write a provider bridge request manifest for one object.")
    parser.add_argument("package_dir", help="Asset package directory.")
    parser.add_argument("--object-id", required=True)
    parser.add_argument("--provider-id", required=True)
    parser.add_argument("--input-ref", action="append", default=[])
    parser.add_argument("--note", default="")
    args = parser.parse_args()

    try:
        request = build_provider_request(
            Path(args.package_dir).resolve(),
            args.object_id,
            args.provider_id,
            input_refs=parse_input_ref(args.input_ref),
            notes=args.note,
        )
        path = write_provider_request(Path(args.package_dir).resolve(), request)
    except ValueError as exc:
        parser.error(str(exc))
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
