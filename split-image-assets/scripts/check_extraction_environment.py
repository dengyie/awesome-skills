import argparse
import importlib.util
import json
import sys


TOOL_SPECS = {
    "Pillow": ["PIL"],
    "OpenCV": ["cv2"],
    "Torch": ["torch"],
    "torchvision": ["torchvision"],
    "rembg": ["rembg"],
    "onnxruntime": ["onnxruntime"],
    "SAM2": ["sam2"],
    "segment-anything": ["segment_anything"],
    "GroundingDINO": ["groundingdino"],
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


def production_readiness(tools: dict) -> tuple[bool, list[str]]:
    missing: list[str] = []
    has_runtime = tools["Torch"]["available"]
    has_detector_or_modern_segmenter = tools["SAM2"]["available"] or tools["GroundingDINO"]["available"]
    has_any_segmenter = has_detector_or_modern_segmenter or tools["segment-anything"]["available"]
    has_matting = tools["rembg"]["available"]

    if not has_runtime:
        missing.append("torch runtime")
    if not has_detector_or_modern_segmenter:
        missing.append("SAM2 or grounded detector")
    if not has_any_segmenter:
        missing.append("segmentation model")
    if not has_matting:
        missing.append("matting/refinement")
    return not missing, missing


def upstream_roles(tools: dict) -> dict:
    return {
        "detection": {
            "recommended_tools": ["GroundingDINO", "Grounded-SAM", "grounded prompts"],
            "available": tools["GroundingDINO"]["available"] or tools["SAM2"]["available"],
            "quality_impact": (
                "Missing SAM2 or a grounded detector means object boundaries may need "
                "manual prompts and may be less reliable."
            ),
        },
        "segmentation": {
            "recommended_tools": ["SAM2", "SAM", "Grounded-SAM", "segment-anything"],
            "available": tools["SAM2"]["available"] or tools["segment-anything"]["available"],
            "quality_impact": (
                "Missing a source-space mask generator blocks reliable object masks for "
                "production asset extraction."
            ),
        },
        "alpha_refinement": {
            "recommended_tools": ["rembg", "BiRefNet", "RMBG"],
            "available": tools["rembg"]["available"],
            "quality_impact": (
                "Missing matting/refinement means transparent PNG alpha edges may keep "
                "halos, dark fringes, or background residue."
            ),
        },
        "background_reconstruction": {
            "recommended_tools": ["IOPaint", "LaMa", "inpainting tools", "manual paint repair"],
            "available": False,
            "quality_impact": (
                "Missing an inpainting or manual repair path means background_clean.png "
                "can only be approximate or needs-review."
            ),
        },
        "packaging_qa": {
            "recommended_tools": ["split-image-assets scripts"],
            "available": True,
            "quality_impact": "Packaging and QA evidence can be produced locally by this skill.",
        },
    }


def build_report() -> dict:
    tools = detect_tools()
    recipe, next_step = choose_recipe(tools)
    production_capable, missing_for_production = production_readiness(tools)
    roles = upstream_roles(tools)
    return {
        "python": {
            "executable": sys.executable,
            "version": sys.version.split()[0],
        },
        "tools": tools,
        "production_capable": production_capable,
        "missing_for_production": missing_for_production,
        "upstream_roles": roles,
        "recommended_recipe": recipe,
        "recommended_next_step": next_step,
        "preflight_tooling_recommendation_gate": {
            "must_confirm_before_extraction": True,
            "user_choices": [
                "install or activate a mature segmentation/matting toolchain",
                "provide external segmented assets and masks",
                "continue as draft-only packaging without production extraction claims",
            ],
            "recommended_answer": (
                "For production-quality extraction, install or provide SAM2/Grounded-SAM "
                "plus rembg/BiRefNet/RMBG-style matting."
            ),
        },
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
    status = "yes" if report["production_capable"] else "no"
    print(f"Production capable: {status}")
    if report["missing_for_production"]:
        print("Missing for production: " + ", ".join(report["missing_for_production"]))
    print("Upstream role impact:")
    for role, details in report["upstream_roles"].items():
        status = "available" if details["available"] else "missing"
        print(f"- {role}: {status}; {details['quality_impact']}")
    print(f"Recommended recipe: {report['recommended_recipe']}")
    print(f"Recommended next step: {report['recommended_next_step']}")
    print(
        "Preflight choices: install/activate tools, provide external professional outputs, "
        "or continue as draft-packaging-only."
    )
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
