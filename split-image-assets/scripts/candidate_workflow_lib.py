import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter, ImageStat
from split_image_assets_contract import ALLOWED_OBJECT_TYPES


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_metadata(package_dir: Path) -> dict:
    return json.loads((package_dir / "metadata.json").read_text(encoding="utf-8"))


def write_metadata(package_dir: Path, metadata: dict) -> None:
    (package_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def load_provider_stage_manifest(
    candidate_asset_path: Path,
    candidate_id: str,
) -> dict:
    manifest_path = candidate_asset_path.parent / f"{candidate_id}_provider_stage.json"
    if not manifest_path.exists():
        return {}
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("provider stage manifest must contain an object")
    return data


def package_path(
    package_dir: Path,
    value: str,
    label: str,
    parser: argparse.ArgumentParser,
    *,
    must_exist: bool = True,
) -> Path:
    if not isinstance(value, str) or not value.strip():
        parser.error(f"{label} must be a package-relative path")
    raw_path = Path(value)
    if raw_path.is_absolute():
        parser.error(f"{label} must stay inside the package: {value}")
    resolved = (package_dir / raw_path).resolve()
    package_root = package_dir.resolve()
    if resolved != package_root and package_root not in resolved.parents:
        parser.error(f"{label} must stay inside the package: {value}")
    if must_exist and not resolved.exists():
        parser.error(f"{label} is missing: {resolved}")
    return resolved


def package_relative(package_dir: Path, path: Path) -> str:
    return str(path.relative_to(package_dir)).replace("\\", "/")


def require_repair_candidate_path(
    path: Path,
    package_dir: Path,
    label: str,
    parser: argparse.ArgumentParser,
) -> None:
    expected_root = (package_dir / "_staging" / "repair_candidates").resolve()
    if path != expected_root and expected_root not in path.parents:
        parser.error(f"{label} must be staged under _staging/repair_candidates/: {path}")


def ensure_repair_candidate_dir(package_dir: Path, object_id: str) -> Path:
    path = package_dir / "_staging" / "repair_candidates" / object_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_upscale_work_dir(package_dir: Path, object_id: str) -> Path:
    path = package_dir / "_staging" / "upscale_work" / object_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_rgba(path: Path) -> Image.Image:
    with Image.open(path) as image:
        return image.convert("RGBA")


def load_mask(path: Path, size: tuple[int, int] | None = None) -> Image.Image:
    with Image.open(path) as image:
        mask = image.convert("L")
    if size and mask.size != size:
        mask = mask.resize(size, Image.Resampling.NEAREST)
    return mask


def save_rgba(path: Path, image: Image.Image) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGBA").save(path)


def save_mask(path: Path, mask: Image.Image) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mask.convert("L").save(path)


def dilate_mask(mask: Image.Image, radius: int) -> Image.Image:
    if radius <= 0:
        return mask.copy()
    kernel = max(3, radius * 2 + 1)
    return mask.filter(ImageFilter.MaxFilter(kernel))


def erode_mask(mask: Image.Image, radius: int) -> Image.Image:
    if radius <= 0:
        return mask.copy()
    kernel = max(3, radius * 2 + 1)
    return mask.filter(ImageFilter.MinFilter(kernel))


def subtract_mask(base: Image.Image, subtracted: Image.Image) -> Image.Image:
    return ImageChops.subtract(base, subtracted)


def intersect_mask(a: Image.Image, b: Image.Image) -> Image.Image:
    return ImageChops.darker(a, b)


def mask_union(a: Image.Image, b: Image.Image) -> Image.Image:
    return ImageChops.lighter(a, b)


def alpha_bbox(mask: Image.Image) -> tuple[int, int, int, int] | None:
    return mask.getbbox()


def average_rgb(image: Image.Image, mask: Image.Image) -> tuple[int, int, int]:
    rgba = image.convert("RGBA")
    alpha_mask = mask.convert("L")
    stat = ImageStat.Stat(rgba, alpha_mask)
    if not stat.count[0]:
        return (128, 128, 128)
    return tuple(int(round(value)) for value in stat.mean[:3])


def colorize_with_alpha(mask: Image.Image, color: tuple[int, int, int]) -> Image.Image:
    color_image = Image.new("RGBA", mask.size, color + (255,))
    color_image.putalpha(mask.convert("L"))
    return color_image


def apply_mask(image: Image.Image, mask: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    masked = rgba.copy()
    masked.putalpha(mask.convert("L"))
    return masked


def border_ring(mask: Image.Image, border_width: int) -> Image.Image:
    return subtract_mask(mask, erode_mask(mask, border_width))


def update_object_type(metadata: dict, object_id: str, object_type: str) -> None:
    if object_type not in ALLOWED_OBJECT_TYPES:
        return
    objects = metadata.get("objects", [])
    if not isinstance(objects, list):
        return
    for item in objects:
        if isinstance(item, dict) and item.get("id") == object_id:
            item["object_type"] = object_type
            break


def component_count(mask: Image.Image, threshold: int = 32) -> int:
    width, height = mask.size
    pixels = mask.load()
    seen: set[tuple[int, int]] = set()
    count = 0
    for y in range(height):
        for x in range(width):
            if (x, y) in seen or pixels[x, y] <= threshold:
                continue
            count += 1
            stack = [(x, y)]
            seen.add((x, y))
            while stack:
                cx, cy = stack.pop()
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx = cx + dx
                    ny = cy + dy
                    if nx < 0 or ny < 0 or nx >= width or ny >= height:
                        continue
                    if (nx, ny) in seen or pixels[nx, ny] <= threshold:
                        continue
                    seen.add((nx, ny))
                    stack.append((nx, ny))
    return count


def mean_absolute_difference(
    image_a: Image.Image,
    image_b: Image.Image,
    mask: Image.Image | None = None,
) -> float:
    a = image_a.convert("RGBA")
    b = image_b.convert("RGBA").resize(a.size, Image.Resampling.LANCZOS)
    diff = ImageChops.difference(a, b).convert("L")
    if mask is not None:
        stat = ImageStat.Stat(diff, mask.convert("L"))
    else:
        stat = ImageStat.Stat(diff)
    return float(stat.mean[0]) if stat.mean else 0.0


def variance_score(image: Image.Image, mask: Image.Image | None = None) -> float:
    grayscale = image.convert("RGBA").convert("L")
    stat = ImageStat.Stat(grayscale, mask.convert("L") if mask is not None else None)
    return float(stat.var[0]) if stat.var else 0.0


def risk_level(value: float) -> str:
    if value >= 0.67:
        return "high"
    if value >= 0.34:
        return "medium"
    return "low"
