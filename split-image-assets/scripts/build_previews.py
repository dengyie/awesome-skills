import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw


def make_checkerboard(size: tuple[int, int], cell: int = 8) -> Image.Image:
    image = Image.new("RGBA", size, (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], cell):
        for x in range(0, size[0], cell):
            if (x // cell + y // cell) % 2:
                draw.rectangle([x, y, x + cell - 1, y + cell - 1], fill=(210, 210, 210, 255))
    return image


def composite_on_background(asset: Image.Image, background: Image.Image) -> Image.Image:
    asset = asset.convert("RGBA")
    canvas = background.convert("RGBA")
    canvas.alpha_composite(asset, (0, 0))
    return canvas.convert("RGB")


def load_metadata(package_dir: Path) -> dict:
    return json.loads((package_dir / "metadata.json").read_text(encoding="utf-8"))


def save_metadata(package_dir: Path, metadata: dict) -> None:
    (package_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def object_entries(metadata: dict) -> list[dict]:
    return [
        item
        for item in metadata.get("objects", [])
        if item.get("asset_path") and item.get("role") in {"main", "secondary", "group", "shadow"}
    ]


def build_individual_previews(package_dir: Path, metadata: dict) -> list[Image.Image]:
    previews_dir = package_dir / "previews"
    previews_dir.mkdir(parents=True, exist_ok=True)
    preview_records = metadata.setdefault("previews", {})
    rendered_assets: list[Image.Image] = []

    for item in object_entries(metadata):
        asset_path = package_dir / item["asset_path"]
        if not asset_path.exists():
            continue
        with Image.open(asset_path) as opened:
            asset = opened.convert("RGBA")
        object_id = item["id"]
        white = composite_on_background(asset, Image.new("RGBA", asset.size, (255, 255, 255, 255)))
        checker = composite_on_background(asset, make_checkerboard(asset.size))
        white_path = previews_dir / f"{object_id}_whitebg.png"
        checker_path = previews_dir / f"{object_id}_checkerboard.png"
        white.save(white_path)
        checker.save(checker_path)
        preview_records[object_id] = {
            "whitebg": str(white_path.relative_to(package_dir)).replace("\\", "/"),
            "checkerboard": str(checker_path.relative_to(package_dir)).replace("\\", "/"),
        }
        rendered_assets.append(asset)

    return rendered_assets


def centered_paste(canvas: Image.Image, asset: Image.Image, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    box_width = x1 - x0
    box_height = y1 - y0
    scale = min(box_width / asset.width, box_height / asset.height, 1.0)
    resized = asset.resize(
        (max(1, int(asset.width * scale)), max(1, int(asset.height * scale))),
        Image.Resampling.LANCZOS,
    )
    x = x0 + (box_width - resized.width) // 2
    y = y0 + (box_height - resized.height) // 2
    canvas.alpha_composite(resized, (x, y))


def build_overview(package_dir: Path, metadata: dict, assets: list[Image.Image]) -> None:
    previews_dir = package_dir / "previews"
    width = max(240, metadata.get("source", {}).get("width", 240) * 2)
    height = max(180, metadata.get("source", {}).get("height", 180) * 2)
    canvas = make_checkerboard((width, height))
    if assets:
        cell_width = width // len(assets)
        for index, asset in enumerate(assets):
            centered_paste(canvas, asset, (index * cell_width, 0, (index + 1) * cell_width, height))
    path = previews_dir / "overview_decomposition.png"
    canvas.convert("RGB").save(path)
    metadata.setdefault("previews", {})["overview_decomposition"] = str(
        path.relative_to(package_dir)
    ).replace("\\", "/")


def build_sprite_sheet(package_dir: Path, metadata: dict, assets: list[Image.Image]) -> None:
    previews_dir = package_dir / "previews"
    source = metadata.get("source", {})
    cell_width = max(120, int(source.get("width", 120)))
    cell_height = max(90, int(source.get("height", 90)))
    canvas = make_checkerboard((cell_width * 2, cell_height * 2))
    boxes = [
        (0, 0, cell_width, cell_height),
        (cell_width, 0, cell_width * 2, cell_height),
        (0, cell_height, cell_width, cell_height * 2),
        (cell_width, cell_height, cell_width * 2, cell_height * 2),
    ]
    for asset, box in zip(assets[:4], boxes):
        centered_paste(canvas, asset, box)
    path = previews_dir / "sprite_sheet_2x2.png"
    canvas.convert("RGB").save(path)
    metadata.setdefault("previews", {})["sprite_sheet_2x2"] = str(
        path.relative_to(package_dir)
    ).replace("\\", "/")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build inspection previews from existing transparent PNG assets."
    )
    parser.add_argument("package_dir", help="Asset package directory.")
    args = parser.parse_args()

    package_dir = Path(args.package_dir).resolve()
    metadata = load_metadata(package_dir)
    assets = build_individual_previews(package_dir, metadata)
    build_overview(package_dir, metadata, assets)
    build_sprite_sheet(package_dir, metadata, assets)
    save_metadata(package_dir, metadata)
    print(f"Built previews for: {package_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
