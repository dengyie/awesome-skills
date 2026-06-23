import argparse
import importlib.util
import json
import sys


TOOL_SPECS = {
    "Pillow": ["PIL"],
    "OpenCV": ["cv2"],
    "Torch": ["torch"],
    "rembg": ["rembg"],
    "SAM2": ["sam2"],
    "segment-anything": ["segment_anything"],
}


def module_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def detect_tools() -> dict:
    tools = {}
    for label, modules in TOOL_SPECS.items():
        found_module = next((module for module in modules if module_available(module)), None)
        tools[label] = {
            "available": found_module is not None,
            "module": found_module or modules[0],
        }
    return tools


def choose_recipe(tools: dict) -> tuple[str, str]:
    has_segmentation = tools["SAM2"]["available"] or tools["segment-anything"]["available"]
    has_matting = tools["rembg"]["available"]
    has_runtime = tools["Torch"]["available"]
    if has_segmentation and has_matting and has_runtime:
        return (
            "grounded-segmentation-matting-repair",
            "Run the quality pipeline locally, but keep draft-only status until previews and manual review pass.",
        )
    if has_segmentation and has_runtime:
        return (
            "grounded-segmentation-matting-repair",
            "Local segmentation may be possible; provide alpha refinement externally or keep draft-only status.",
        )
    if has_matting:
        return (
            "external-mask-plus-matting",
            "Provide external masks before matting; keep draft-only status until segmentation evidence exists.",
        )
    return (
        "external-assets-required",
        "No local mature segmentation stack detected; ask the user to install tools, provide external cutouts/masks, or proceed draft-only.",
    )


def build_report() -> dict:
    tools = detect_tools()
    recipe, next_step = choose_recipe(tools)
    return {
        "python": {
            "executable": sys.executable,
            "version": sys.version.split()[0],
        },
        "tools": tools,
        "recommended_recipe": recipe,
        "recommended_next_step": next_step,
        "capability_gate": {
            "must_confirm_before_extraction": True,
            "choices": [
                "install or activate a mature segmentation/matting toolchain",
                "provide external segmented assets and masks",
                "continue as draft-only packaging without production extraction claims",
            ],
        },
    }


def print_text_report(report: dict) -> None:
    print("Extraction capability gate")
    print(f"Python: {report['python']['version']} ({report['python']['executable']})")
    print("Tools:")
    for name, details in report["tools"].items():
        status = "available" if details["available"] else "missing"
        print(f"- {name}: {status} ({details['module']})")
    print(f"Recommended recipe: {report['recommended_recipe']}")
    print(f"Recommended next step: {report['recommended_next_step']}")
    print("If required tools are missing, do not claim production extraction.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check local optional extraction tool availability without installing anything."
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    report = build_report()
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_text_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
