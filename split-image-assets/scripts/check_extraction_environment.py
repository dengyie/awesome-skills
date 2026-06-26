import argparse
import importlib.util
import json
import sys


def _probe_torch_runtime() -> dict:
    if importlib.util.find_spec("torch") is None:
        return {
            "installed": False,
            "runtime_ready": False,
            "version": None,
            "cuda_available": False,
            "cuda_device_count": 0,
        }
    try:
        import torch  # type: ignore
    except Exception as exc:  # pragma: no cover - defensive runtime probe
        return {
            "installed": True,
            "runtime_ready": False,
            "version": None,
            "cuda_available": False,
            "cuda_device_count": 0,
            "error": str(exc),
        }
    cuda_available = False
    cuda_device_count = 0
    try:
        cuda_available = bool(torch.cuda.is_available())
        cuda_device_count = int(torch.cuda.device_count()) if cuda_available else 0
    except Exception as exc:  # pragma: no cover - defensive runtime probe
        return {
            "installed": True,
            "runtime_ready": True,
            "version": getattr(torch, "__version__", "unknown"),
            "cuda_available": False,
            "cuda_device_count": 0,
            "error": str(exc),
        }
    return {
        "installed": True,
        "runtime_ready": True,
        "version": getattr(torch, "__version__", "unknown"),
        "cuda_available": cuda_available,
        "cuda_device_count": cuda_device_count,
    }


def _probe_runtime(module_name: str) -> dict:
    installed = importlib.util.find_spec(module_name) is not None
    if not installed:
        return {"installed": False, "runtime_ready": False}
    try:
        module = __import__(module_name)
    except Exception as exc:  # pragma: no cover - defensive runtime probe
        return {"installed": True, "runtime_ready": False, "error": str(exc)}
    return {
        "installed": True,
        "runtime_ready": True,
        "version": getattr(module, "__version__", "unknown"),
    }


def _probe_first_runtime(module_names: list[str]) -> dict:
    for module_name in module_names:
        if importlib.util.find_spec(module_name) is None:
            continue
        result = _probe_runtime(module_name)
        result["module"] = module_name
        return result
    return {
        "installed": False,
        "runtime_ready": False,
        "module": module_names[0] if module_names else "unknown",
    }


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
    "IOPaint": ["iopaint", "lama_cleaner"],
    "LaMa": ["saicinpainting", "lama_cleaner"],
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


def choose_recipe(capabilities: dict) -> tuple[str, str]:
    has_segmentation = capabilities["segmentation"]["production_ready"]
    has_matting = capabilities["matting"]["production_ready"]
    has_reconstruction = capabilities["reconstruction"]["production_ready"]
    has_runtime = capabilities["environment"]["python"]["runtime_ready"] and capabilities["environment"][
        "torch"
    ]["runtime_ready"]
    if has_segmentation and has_matting and has_reconstruction and has_runtime:
        return (
            "grounded-segmentation-matting-repair",
            "production-capable",
        )
    if has_segmentation and has_runtime:
        return (
            "grounded-segmentation-matting-repair",
            "external-professional-outputs",
        )
    if has_matting:
        return (
            "external-mask-plus-matting",
            "external-professional-outputs",
        )
    return (
        "external-assets-required",
        "install-or-activate-tools",
    )


def production_readiness(capabilities: dict) -> tuple[bool, list[str]]:
    missing: list[str] = []
    environment = capabilities["environment"]
    segmentation = capabilities["segmentation"]
    matting = capabilities["matting"]
    reconstruction = capabilities["reconstruction"]

    if not environment["torch"]["runtime_ready"]:
        missing.append("torch runtime")
    if not segmentation["tooling"]["groundingdino"]["installed"] and not segmentation["tooling"]["sam2"]["installed"]:
        missing.append("SAM2 or grounded detector")
    if not segmentation["production_ready"]:
        missing.append("segmentation model")
    if not matting["production_ready"]:
        missing.append("matting/refinement")
    if not reconstruction["production_ready"]:
        if reconstruction["path_type"] == "manual-redraw-only":
            missing.append("dedicated reconstruction tool or accepted manual redraw path")
        else:
            missing.append("dedicated reconstruction tool")
    return not missing, missing


def build_reconstruction_capability(
    torch_runtime: dict,
    onnx_runtime: dict,
    iopaint_runtime: dict,
    lama_runtime: dict,
) -> dict:
    dedicated_installed = bool(iopaint_runtime["installed"] or lama_runtime["installed"])
    dedicated_runtime_ready = bool(iopaint_runtime["runtime_ready"] or lama_runtime["runtime_ready"])
    if dedicated_runtime_ready:
        path_type = "dedicated-tool"
        quality_impact = (
            "Dedicated reconstruction tooling is available, but repaired layers still need review evidence "
            "and honest approximate-reconstruction labeling when hidden pixels are inferred."
        )
    elif dedicated_installed:
        path_type = "manual-redraw-only"
        quality_impact = (
            "A dedicated reconstruction tool appears installed but not runtime-ready. Do not claim a "
            "production reconstruction path until that tool actually runs; fall back to manual redraw "
            "or approximate reconstruction only in the meantime."
        )
    else:
        path_type = "manual-redraw-only"
        quality_impact = (
            "No dedicated reconstruction tool is runtime-ready. Background/carrier repair falls back to manual "
            "redraw or approximate reconstruction only, which requires explicit user acceptance and must not be "
            "treated as automatic production capability."
        )

    return {
        "installed": dedicated_installed,
        "runtime_ready": dedicated_runtime_ready,
        "production_ready": dedicated_runtime_ready,
        "path_type": path_type,
        "manual_redraw_required": path_type == "manual-redraw-only",
        "requires_user_acceptance": path_type != "dedicated-tool",
        "tooling": {
            "iopaint": iopaint_runtime,
            "lama": lama_runtime,
            "torch": {
                "installed": torch_runtime["installed"],
                "runtime_ready": torch_runtime["runtime_ready"],
                "note": "Environment support only; not sufficient for reconstruction production readiness.",
            },
            "onnxruntime": {
                "installed": onnx_runtime["installed"],
                "runtime_ready": onnx_runtime["runtime_ready"],
                "note": "Environment support only; not sufficient for reconstruction production readiness.",
            },
            "manual_redraw_path": {
                "installed": True,
                "runtime_ready": False,
                "production_ready": False,
                "acceptance_required": True,
                "note": "Human redraw path only. This is not an automatic runtime capability and needs explicit acceptance.",
            },
        },
        "quality_impact": quality_impact,
    }


def build_capabilities(tools: dict) -> dict:
    torch_runtime = _probe_torch_runtime()
    onnx_runtime = _probe_runtime("onnxruntime")
    rembg_runtime = _probe_runtime("rembg")
    sam2_runtime = _probe_runtime("sam2")
    groundingdino_runtime = _probe_runtime("groundingdino")
    segment_anything_runtime = _probe_runtime("segment_anything")
    iopaint_runtime = _probe_first_runtime(["iopaint", "lama_cleaner"])
    lama_runtime = _probe_first_runtime(["saicinpainting", "lama_cleaner"])

    segmentation_production_ready = bool(
        torch_runtime["runtime_ready"]
        and (
            sam2_runtime["runtime_ready"]
            or groundingdino_runtime["runtime_ready"]
            or segment_anything_runtime["runtime_ready"]
        )
    )
    matting_production_ready = bool(
        rembg_runtime["runtime_ready"]
        or onnx_runtime["runtime_ready"]
    )
    reconstruction = build_reconstruction_capability(
        torch_runtime, onnx_runtime, iopaint_runtime, lama_runtime
    )
    return {
        "segmentation": {
            "installed": any(
                [
                    sam2_runtime["installed"],
                    groundingdino_runtime["installed"],
                    segment_anything_runtime["installed"],
                ]
            ),
            "runtime_ready": segmentation_production_ready,
            "production_ready": segmentation_production_ready,
            "tooling": {
                "sam2": sam2_runtime,
                "groundingdino": groundingdino_runtime,
                "segment_anything": segment_anything_runtime,
            },
        },
        "matting": {
            "installed": bool(rembg_runtime["installed"]),
            "runtime_ready": bool(rembg_runtime["runtime_ready"] or onnx_runtime["runtime_ready"]),
            "production_ready": matting_production_ready,
            "tooling": {
                "rembg": rembg_runtime,
                "onnxruntime": onnx_runtime,
            },
        },
        "reconstruction": {
            **reconstruction,
        },
        "environment": {
            "python": {
                "installed": True,
                "runtime_ready": True,
                "version": sys.version.split()[0],
                "executable": sys.executable,
            },
            "torch": torch_runtime,
            "onnxruntime": onnx_runtime,
            "cuda": {
                "installed": torch_runtime["installed"],
                "runtime_ready": torch_runtime["runtime_ready"],
                "available": torch_runtime["cuda_available"],
                "device_count": torch_runtime["cuda_device_count"],
            },
        },
    }


def upstream_roles(capabilities: dict) -> dict:
    return {
        "detection": {
            "recommended_tools": ["GroundingDINO", "Grounded-SAM", "grounded prompts"],
            "available": capabilities["segmentation"]["tooling"]["groundingdino"]["runtime_ready"]
            or capabilities["segmentation"]["tooling"]["sam2"]["runtime_ready"],
            "quality_impact": (
                "Missing SAM2 or a grounded detector means object boundaries may need "
                "manual prompts and may be less reliable."
            ),
        },
        "segmentation": {
            "recommended_tools": ["SAM2", "SAM", "Grounded-SAM", "segment-anything"],
            "available": capabilities["segmentation"]["production_ready"],
            "quality_impact": (
                "Missing a source-space mask generator blocks reliable object masks for "
                "production asset extraction."
            ),
        },
        "alpha_refinement": {
            "recommended_tools": ["rembg", "BiRefNet", "RMBG"],
            "available": capabilities["matting"]["production_ready"],
            "quality_impact": (
                "Missing matting/refinement means transparent PNG alpha edges may keep "
                "halos, dark fringes, or background residue."
            ),
        },
        "background_reconstruction": {
            "recommended_tools": ["IOPaint", "LaMa", "inpainting tools", "manual paint repair"],
            "available": capabilities["reconstruction"]["production_ready"],
            "quality_impact": capabilities["reconstruction"]["quality_impact"],
        },
        "packaging_qa": {
            "recommended_tools": ["split-image-assets scripts"],
            "available": True,
            "quality_impact": "Packaging and QA evidence can be produced locally by this skill.",
        },
    }


def build_report() -> dict:
    tools = detect_tools()
    capabilities = build_capabilities(tools)
    recipe, next_action = choose_recipe(capabilities)
    production_capable, missing_for_production = production_readiness(capabilities)
    roles = upstream_roles(capabilities)
    return {
        "python": {
            "executable": sys.executable,
            "version": sys.version.split()[0],
        },
        "tools": tools,
        "segmentation": capabilities["segmentation"],
        "matting": capabilities["matting"],
        "reconstruction": capabilities["reconstruction"],
        "environment": capabilities["environment"],
        "production_capable": production_capable,
        "missing_for_production": missing_for_production,
        "upstream_roles": roles,
        "recommended_recipe": recipe,
        "recommended_next_action": next_action,
        "recommended_next_step": next_action,
        "recommended_next_action_detail": (
            "Dedicated reconstruction tooling is installed but not runtime-ready; manual redraw required or approximate reconstruction only until that tool actually runs."
            if capabilities["reconstruction"]["path_type"] == "manual-redraw-only"
            and capabilities["reconstruction"]["installed"]
            else (
                "Dedicated reconstruction tooling is missing; manual redraw required or approximate reconstruction only."
                if capabilities["reconstruction"]["path_type"] == "manual-redraw-only"
                else "Dedicated reconstruction tooling is available before claiming production extraction."
            )
        ),
        "preflight_tooling_recommendation_gate": {
            "must_confirm_before_extraction": True,
            "user_choices": [
                "install-or-activate-tools",
                "external-professional-outputs",
                "draft-packaging-only",
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
    print("Capability summary:")
    for name in ["segmentation", "matting", "reconstruction"]:
        details = report[name]
        print(
            f"- {name}: installed={details['installed']} runtime_ready={details['runtime_ready']} "
            f"production_ready={details['production_ready']}"
        )
    status = "yes" if report["production_capable"] else "no"
    print(f"Production capable: {status}")
    if report["missing_for_production"]:
        print("Missing for production: " + ", ".join(report["missing_for_production"]))
    print("Upstream role impact:")
    for role, details in report["upstream_roles"].items():
        status = "available" if details["available"] else "missing"
        print(f"- {role}: {status}; {details['quality_impact']}")
    print(f"Recommended recipe: {report['recommended_recipe']}")
    print(f"Recommended next action: {report['recommended_next_action']}")
    print(f"Recommended next action detail: {report['recommended_next_action_detail']}")
    print(
        "Preflight choices: install-or-activate-tools, external-professional-outputs, "
        "or draft-packaging-only."
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
