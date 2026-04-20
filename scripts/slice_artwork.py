"""
slice_artwork.py — Universal artwork slicer for keycap groups

Replaces slice_frow_png.py and slice_matrix_frow.py.
Reads F-key positions from keycap-coordinate-map.json.

Usage:
    py -3 scripts/slice_artwork.py \\
        --source images/mond-8K.png \\
        --group fkey \\
        --output-dir icons/fkey \\
        [--size 434] \\
        [--strategy moon|matrix|uniform] \\
        [--palette oni|none]

    py -3 scripts/slice_artwork.py --help

Strategies:
    moon     vertical crop on brightest row (moon center detection), then per-key horizontal slice
    matrix   equal-width column split across full image width
    uniform  each key gets equal slice of image width, centered vertically

Output:
    <output-dir>/<KEY_ID>.png   one PNG per key in the group, e.g. F1.png ... F12.png
"""

import argparse
import io
import json
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent
COORD_MAP = REPO / "layouts" / "keycap-coordinate-map.json"
OUTPUT_DPI = 600
PT_PER_INCH = 72.0

# Oni Mask palette ramp (luminance → target color)
ONI_COLOR_MAP = [
    (0,   0x1B, 0x1D, 0x20),
    (10,  0x1B, 0x1D, 0x20),
    (22,  0x22, 0x20, 0x28),
    (35,  0x2A, 0x25, 0x30),
    (60,  0x32, 0x2D, 0x3A),
    (80,  0x3A, 0x35, 0x40),
    (105, 0x60, 0x50, 0x3A),
    (120, 0x8C, 0x7A, 0x50),
    (138, 0xA8, 0x8B, 0x63),
    (146, 0xB5, 0x97, 0x6E),
    (255, 0xC5, 0xA8, 0x80),
]


def load_coord_map() -> dict:
    with open(COORD_MAP, encoding="utf-8") as f:
        return json.load(f)


def keys_for_group(coord_map: dict, group: str) -> list:
    return [k for k in coord_map["keys"] if k["group"] == group]


def apply_oni_palette(arr: np.ndarray) -> np.ndarray:
    f = arr.astype(np.float32)
    lum = 0.2126 * f[:, :, 0] + 0.7152 * f[:, :, 1] + 0.0722 * f[:, :, 2]
    src = np.array([r[0] for r in ONI_COLOR_MAP], dtype=np.float32)
    out = np.stack([
        np.interp(lum, src, np.array([r[1] for r in ONI_COLOR_MAP], dtype=np.float32)),
        np.interp(lum, src, np.array([r[2] for r in ONI_COLOR_MAP], dtype=np.float32)),
        np.interp(lum, src, np.array([r[3] for r in ONI_COLOR_MAP], dtype=np.float32)),
    ], axis=2)
    return np.clip(out, 0, 255).astype(np.uint8)


def find_brightest_row(arr: np.ndarray) -> int:
    lum = 0.2126 * arr[:, :, 0].astype(float) \
        + 0.7152 * arr[:, :, 1].astype(float) \
        + 0.0722 * arr[:, :, 2].astype(float)
    return int(np.argmax(lum.mean(axis=1)))


def slice_moon(img: Image.Image, keys: list, output_dir: Path, out_px: int, palette: str) -> None:
    """Moon strategy: find brightest row, crop vertically, slice each key horizontally."""
    arr = np.array(img.convert("RGB"))
    src_w, src_h = img.size

    if palette == "oni":
        arr = apply_oni_palette(arr)

    moon_row = find_brightest_row(arr)
    print(f"  Moon center row: {moon_row}")

    # Use F-key x-range from coordinate map to determine scale
    x0_min = min(k["x0"] for k in keys)
    x1_max = max(k["x1"] for k in keys)
    pdf_span = x1_max - x0_min
    px_per_pt = src_w / pdf_span

    key_face_pt = keys[0]["width"]  # assume uniform (all F keys = 52.1pt)
    crop_src = round(key_face_pt * px_per_pt)

    y0 = max(0, moon_row - crop_src // 2)
    y1 = min(src_h, y0 + crop_src)
    if y1 - y0 < crop_src:
        y0 = max(0, y1 - crop_src)

    for key in keys:
        key_cx_pt = (key["x0"] + key["x1"]) / 2
        cx_rel_pt = key_cx_pt - x0_min
        cx_px = round(cx_rel_pt * px_per_pt)
        hx0 = max(0, cx_px - crop_src // 2)
        hx1 = min(src_w, hx0 + crop_src)
        if hx1 - hx0 < crop_src:
            hx0 = max(0, hx1 - crop_src)

        tile = arr[y0:y1, hx0:hx1, :]
        pil = Image.fromarray(tile, "RGB").resize((out_px, out_px), Image.LANCZOS)
        out_path = output_dir / f"{key['name']}.png"
        pil.save(out_path, "PNG", dpi=(OUTPUT_DPI, OUTPUT_DPI))
        print(f"  {key['name']:4s}: x[{hx0}:{hx1}] y[{y0}:{y1}]  → {out_path.name}")


def slice_matrix(img: Image.Image, keys: list, output_dir: Path, out_px: int, palette: str) -> None:
    """Matrix strategy: divide image into equal columns."""
    arr = np.array(img.convert("RGB"))
    src_w, src_h = img.size
    n = len(keys)
    col_w = src_w // n
    crop_sq = min(col_w, src_h)
    x_off = (col_w - crop_sq) // 2
    y_off = (src_h - crop_sq) // 2

    for i, key in enumerate(keys):
        x0 = i * col_w + x_off
        y0 = y_off
        x1 = x0 + crop_sq
        y1 = y0 + crop_sq
        tile = arr[y0:y1, x0:x1, :]
        pil = Image.fromarray(tile, "RGB").resize((out_px, out_px), Image.LANCZOS)
        out_path = output_dir / f"{key['name']}.png"
        pil.save(out_path, "PNG", dpi=(OUTPUT_DPI, OUTPUT_DPI))
        print(f"  {key['name']:4s}: x[{x0}:{x1}] y[{y0}:{y1}]  → {out_path.name}")


def slice_uniform(img: Image.Image, keys: list, output_dir: Path, out_px: int, palette: str) -> None:
    """Uniform strategy: divide image into n equal slices, center-crop vertically."""
    arr = np.array(img.convert("RGB"))
    src_w, src_h = img.size
    n = len(keys)
    slice_w = src_w // n
    y0 = max(0, (src_h - slice_w) // 2)
    y1 = min(src_h, y0 + slice_w)

    for i, key in enumerate(keys):
        x0 = i * slice_w
        x1 = x0 + slice_w
        tile = arr[y0:y1, x0:x1, :]
        pil = Image.fromarray(tile, "RGB").resize((out_px, out_px), Image.LANCZOS)
        out_path = output_dir / f"{key['name']}.png"
        pil.save(out_path, "PNG", dpi=(OUTPUT_DPI, OUTPUT_DPI))
        print(f"  {key['name']:4s}: x[{x0}:{x1}] y[{y0}:{y1}]  → {out_path.name}")


def main():
    p = argparse.ArgumentParser(description="Slice artwork PNG into per-key tiles")
    p.add_argument("--source",   required=True, help="Source image path")
    p.add_argument("--group",    required=True, help="Key group (fkey, alpha, mod, accent, nav)")
    p.add_argument("--output-dir", required=True, help="Output directory for key PNGs")
    p.add_argument("--size",     type=int, default=434, help="Output size in px (default 434)")
    p.add_argument("--strategy", choices=["moon", "matrix", "uniform"], default="matrix",
                   help="Slicing strategy (default: matrix)")
    p.add_argument("--palette",  choices=["oni", "none"], default="none",
                   help="Color palette remap (default: none)")
    args = p.parse_args()

    src_path = Path(args.source)
    if not src_path.is_absolute():
        src_path = REPO / src_path
    if not src_path.exists():
        print(f"ERROR: Source not found: {src_path}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = REPO / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    coord_map = load_coord_map()
    keys = keys_for_group(coord_map, args.group)
    if not keys:
        print(f"ERROR: No keys found for group '{args.group}' in coordinate map.", file=sys.stderr)
        print(f"  Available groups: {sorted(set(k['group'] for k in coord_map['keys']))}")
        sys.exit(1)

    img = Image.open(src_path)
    print(f"Source : {src_path.name}  {img.size[0]}×{img.size[1]} {img.mode}")
    print(f"Group  : {args.group}  ({len(keys)} keys)")
    print(f"Output : {output_dir}  ({args.size}×{args.size} px, {args.strategy} strategy)")
    print()

    if args.strategy == "moon":
        slice_moon(img, keys, output_dir, args.size, args.palette)
    elif args.strategy == "matrix":
        slice_matrix(img, keys, output_dir, args.size, args.palette)
    else:
        slice_uniform(img, keys, output_dir, args.size, args.palette)

    print(f"\nDone. {len(keys)} tiles → {output_dir}")


if __name__ == "__main__":
    main()
