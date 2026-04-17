#!/usr/bin/env python3
"""
slice_frow_png.py — Slice mond_flach.png into 12 F-key PNGs at 600 DPI
with Oni Mask color palette remapping.

Workflow:
  1. Vertical crop: detect moon center row, crop to key-face size (52.1pt)
  2. Horizontal slice: 52.1pt centered on each F-key's PDF x-position
  3. Color remap: luminance ramp → Oni palette (grey moon → warm gold,
     neutral clouds → purple tint, background → #1B1D20)
  4. 600 DPI export via LANCZOS upscaling → 434×434 px (square)

Usage:
    py -3 scripts/slice_frow_png.py

Output: icons/fkey/F1.png ... icons/fkey/F12.png (600 DPI, 434×434 px)

Source analysis of mond_flach.png (1376x312):
  - x-scale: 1376 px / 750 PDF-pt = 1.8347 px/pt
  - Moon peak: row 103 (mean lum 46.5) of 312 total rows
  - Key-face crop: 96 px square (= 52.1pt x 1.8347 px/pt), centered on row 103
"""

import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import numpy as np
from PIL import Image

REPO_ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PNG_PATH   = os.path.join(REPO_ROOT, "images", "mond-8K.png")
OUTPUT_DIR = os.path.join(REPO_ROOT, "icons", "fkey")

# ── F-key geometry in PDF pt ───────────────────────────────────────────────────
PDF_F_START   = 215.0   # x of F1 left edge
PDF_F_TOTAL_W = 750.0   # F1_left to F12_right (965 - 215 pt)
PDF_KEY_FACE  = 52.1    # key face size in pt (square: 52.1 × 52.1 pt = 434×434 px @ 600 DPI)

F_KEYS = [
    ("F1",  215.0, 55.0),
    ("F2",  275.0, 55.0),
    ("F3",  332.5, 55.0),
    ("F4",  390.0, 55.0),
    # gap F4 → F5 (35 pt)
    ("F5",  480.0, 55.0),
    ("F6",  540.0, 52.5),
    ("F7",  595.0, 55.0),
    ("F8",  652.5, 52.5),
    # gap F8 → F9 (37.5 pt)
    ("F9",  742.5, 55.0),
    ("F10", 800.0, 55.0),
    ("F11", 855.0, 55.0),
    ("F12", 910.0, 55.0),
]

OUTPUT_DPI  = 600
PT_PER_INCH = 72.0

# ── Color ramp: source luminance (0–255) → Oni Mask palette ───────────────────
#
# Source is near-greyscale (R≈G≈B). Calibrated from pixel analysis:
#   Background    lum  0-10: flat dark #060606–#09090A
#   Clouds dark   lum 22-35: neutral grey #15161B–#28282C
#   Clouds mid    lum 35-80: neutral grey #1E1D21–#2C2B30
#   Moon          lum 100–146: neutral grey #8D897B (peak row 103, lum 46.5 mean)
#
# Anchors: (src_lum, tgt_R, tgt_G, tgt_B)
COLOR_MAP = [
    (  0,  0x1B, 0x1D, 0x20),   # black            → Oni background #1B1D20
    ( 10,  0x1B, 0x1D, 0x20),   # very dark         → Oni background
    ( 22,  0x22, 0x20, 0x28),   # transition        → slight purple
    ( 35,  0x2A, 0x25, 0x30),   # cloud dark        → #2A2530
    ( 60,  0x32, 0x2D, 0x3A),   # cloud mid-dark
    ( 80,  0x3A, 0x35, 0x40),   # cloud bright      → #3A3540
    (105,  0x60, 0x50, 0x3A),   # transition to gold
    (120,  0x8C, 0x7A, 0x50),   # moon medium       → #8C7A50
    (138,  0xA8, 0x8B, 0x63),   # moon bright       → #A88B63
    (146,  0xB5, 0x97, 0x6E),   # moon peak         → warm gold
    (255,  0xC5, 0xA8, 0x80),   # white clamp       → light gold
]


def apply_oni_palette(arr: np.ndarray) -> np.ndarray:
    """Remap image colors to Oni Mask palette via per-pixel luminance ramp."""
    f = arr.astype(np.float32)
    lum = 0.2126 * f[:, :, 0] + 0.7152 * f[:, :, 1] + 0.0722 * f[:, :, 2]

    src_lum = np.array([r[0] for r in COLOR_MAP], dtype=np.float32)
    tgt_r   = np.array([r[1] for r in COLOR_MAP], dtype=np.float32)
    tgt_g   = np.array([r[2] for r in COLOR_MAP], dtype=np.float32)
    tgt_b   = np.array([r[3] for r in COLOR_MAP], dtype=np.float32)

    out = np.stack([
        np.interp(lum, src_lum, tgt_r),
        np.interp(lum, src_lum, tgt_g),
        np.interp(lum, src_lum, tgt_b),
    ], axis=2)
    return np.clip(out, 0, 255).astype(np.uint8)


def find_moon_center_row(arr: np.ndarray) -> int:
    """Return the row index with the highest mean luminance (moon peak)."""
    lum = 0.2126 * arr[:, :, 0].astype(float) \
        + 0.7152 * arr[:, :, 1].astype(float) \
        + 0.0722 * arr[:, :, 2].astype(float)
    return int(np.argmax(lum.mean(axis=1)))


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    img = Image.open(PNG_PATH).convert("RGB")
    src_w, src_h = img.size
    print(f"Source : {PNG_PATH}")
    print(f"  Size : {src_w} x {src_h} px")

    # x-scale: source pixels per PDF pt
    px_per_pt = src_w / PDF_F_TOTAL_W
    print(f"  Scale: {px_per_pt:.4f} px/pt  ({PDF_F_TOTAL_W:.0f} pt -> {src_w} px)")

    # Square key-face size in source pixels
    crop_src = round(PDF_KEY_FACE * px_per_pt)     # ~96 px (52.1pt × 1.8347)

    # Vertical crop: centered on moon peak row
    arr = np.array(img)
    moon_row = find_moon_center_row(arr)
    y0 = max(0, moon_row - crop_src // 2)
    y1 = min(src_h, y0 + crop_src)
    if y1 - y0 < crop_src:                         # clamp if near bottom edge
        y0 = max(0, y1 - crop_src)
    print(f"  Moon center row : {moon_row}")
    print(f"  Vertical crop   : rows {y0}–{y1}  ({y1-y0} px = {PDF_KEY_FACE} pt)")

    # Square output size at 600 DPI
    out_px = round(PDF_KEY_FACE * OUTPUT_DPI / PT_PER_INCH)   # 52.1pt → 434 px
    out_scale = OUTPUT_DPI / PT_PER_INCH / px_per_pt
    print(f"  Output scale    : x{out_scale:.4f}  ({OUTPUT_DPI} DPI)")
    print(f"  Output size     : {out_px}×{out_px} px  ({PDF_KEY_FACE/PT_PER_INCH*25.4:.1f}×{PDF_KEY_FACE/PT_PER_INCH*25.4:.1f} mm)\n")

    # Apply palette to full image once, then crop
    print("Applying Oni Mask palette ...")
    arr_oni = apply_oni_palette(arr)
    print()

    for name, pdf_x, pdf_w in F_KEYS:
        # Horizontal crop: 52.1pt centered on this key's face
        key_center_pt = pdf_x + pdf_w / 2
        cx0 = round((key_center_pt - PDF_KEY_FACE / 2 - PDF_F_START) * px_per_pt)
        cx1 = cx0 + crop_src
        cx0 = max(0, min(cx0, src_w - crop_src))
        cx1 = cx0 + crop_src

        key_crop = arr_oni[y0:y1, cx0:cx1, :]     # square crop in source

        pil_crop = Image.fromarray(key_crop, "RGB")
        pil_out  = pil_crop.resize((out_px, out_px), Image.LANCZOS)

        out_path = os.path.join(OUTPUT_DIR, f"{name}.png")
        pil_out.save(out_path, "PNG", dpi=(OUTPUT_DPI, OUTPUT_DPI))

        size_kb = os.path.getsize(out_path) / 1024
        print(f"  {name:4s}: src x[{cx0}:{cx1}] y[{y0}:{y1}]  {crop_src}x{crop_src}px"
              f"  ->  {out_px}x{out_px}px @ {OUTPUT_DPI} DPI  ({size_kb:.0f} KB)")

    print(f"\nDone. 12 PNGs @ {OUTPUT_DPI} DPI ({out_px}x{out_px} px) written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
