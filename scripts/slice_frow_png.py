#!/usr/bin/env python3
"""
slice_frow_png.py — Slice mond_flach.png into 12 F-key PNGs at 600 DPI
with Oni Mask color palette remapping.

Usage:
    py -3 scripts/slice_frow_png.py

Output: icons/fkey/F1.png ... icons/fkey/F12.png (600 DPI)

Color mapping calibrated from pixel analysis of mond_flach.png:
  Background (lum 0-10):   very dark near-neutral  → Oni #1B1D20
  Clouds dark (lum 22-35): dark neutral-grey        → Oni #2A2530 (purple tint)
  Clouds mid  (lum 35-80): dark grey                → Oni #3A3540 (purple tint)
  Moon medium (lum ~120):  neutral grey #8C897B     → Oni #8C7A50 (warm gold)
  Moon bright (lum ~138):  neutral grey #8D897B     → Oni #A88B63 (warm gold)
"""

import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import numpy as np
from PIL import Image

REPO_ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PNG_PATH   = os.path.join(REPO_ROOT, "icons", "mond_flach.png")
OUTPUT_DIR = os.path.join(REPO_ROOT, "icons", "fkey")

# ── F-key positions in PDF pt (same source as slice_frow_svg.py) ──────────────
PDF_F_START   = 215.0   # x of F1 left edge in PDF pt
PDF_F_TOTAL_W = 750.0   # F1_left to F12_right (965 - 215 pt)

F_KEYS = [
    ("F1",  215.0, 55.0),
    ("F2",  275.0, 55.0),
    ("F3",  332.5, 55.0),
    ("F4",  390.0, 55.0),
    # gap between F4 and F5 (35 pt)
    ("F5",  480.0, 55.0),
    ("F6",  540.0, 52.5),
    ("F7",  595.0, 55.0),
    ("F8",  652.5, 52.5),
    # gap between F8 and F9 (37.5 pt)
    ("F9",  742.5, 55.0),
    ("F10", 800.0, 55.0),
    ("F11", 855.0, 55.0),
    ("F12", 910.0, 55.0),
]

OUTPUT_DPI  = 600
PT_PER_INCH = 72.0

# ── Color ramp: source luminance (0–255) → Oni Mask palette ───────────────────
#
# The source PNG is near-greyscale (R≈G≈B), so luminance alone drives the
# target color. Anchors are (src_lum, tgt_R, tgt_G, tgt_B).
#
COLOR_MAP = [
    (  0,  0x1B, 0x1D, 0x20),   # pure black      → Oni background #1B1D20
    ( 10,  0x1B, 0x1D, 0x20),   # very dark        → Oni background
    ( 22,  0x22, 0x20, 0x28),   # dark → transition (slight purple)
    ( 35,  0x2A, 0x25, 0x30),   # cloud dark       → #2A2530
    ( 60,  0x32, 0x2D, 0x3A),   # cloud mid-dark
    ( 80,  0x3A, 0x35, 0x40),   # cloud bright     → #3A3540
    (105,  0x60, 0x50, 0x3A),   # transition to moon gold
    (120,  0x8C, 0x7A, 0x50),   # moon medium      → #8C7A50
    (138,  0xA8, 0x8B, 0x63),   # moon bright      → #A88B63
    (146,  0xB5, 0x97, 0x6E),   # moon peak        → warm gold
    (255,  0xC5, 0xA8, 0x80),   # white clamp      → light gold
]


def apply_oni_palette(arr: np.ndarray) -> np.ndarray:
    """Remap image colors to Oni Mask palette via per-pixel luminance interpolation."""
    f = arr.astype(np.float32)

    # Rec.709 luminance in 0–255 scale
    lum = 0.2126 * f[:, :, 0] + 0.7152 * f[:, :, 1] + 0.0722 * f[:, :, 2]

    src_lum = np.array([row[0] for row in COLOR_MAP], dtype=np.float32)
    tgt_r   = np.array([row[1] for row in COLOR_MAP], dtype=np.float32)
    tgt_g   = np.array([row[2] for row in COLOR_MAP], dtype=np.float32)
    tgt_b   = np.array([row[3] for row in COLOR_MAP], dtype=np.float32)

    out = np.stack([
        np.interp(lum, src_lum, tgt_r),
        np.interp(lum, src_lum, tgt_g),
        np.interp(lum, src_lum, tgt_b),
    ], axis=2)

    return np.clip(out, 0, 255).astype(np.uint8)


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    img = Image.open(PNG_PATH).convert("RGB")
    src_w, src_h = img.size
    print(f"Source : {PNG_PATH}")
    print(f"  Size : {src_w} x {src_h} px")

    # Scale: source pixels per PDF pt (x-direction is the reference)
    px_per_pt = src_w / PDF_F_TOTAL_W
    print(f"  Scale: {px_per_pt:.4f} px/pt  (750 pt → {src_w} px)")

    # Output upscale factor: source pixels → 600 DPI pixels
    # 1 PDF pt = 1/72 inch; at 600 DPI that is 600/72 output pixels.
    out_scale = (OUTPUT_DPI / PT_PER_INCH) / px_per_pt
    out_h = round(src_h * out_scale)
    print(f"  Output scale : x{out_scale:.4f}  → {OUTPUT_DPI} DPI")
    print(f"  Output height: {out_h} px  ({out_h / OUTPUT_DPI * 25.4:.1f} mm)\n")

    # Apply palette to entire image once (faster than per-slice)
    print("Applying Oni Mask palette ...")
    arr_oni = apply_oni_palette(np.array(img))
    print()

    for name, pdf_x, pdf_w in F_KEYS:
        # Crop x-region in source (full height)
        x0 = round((pdf_x - PDF_F_START) * px_per_pt)
        x1 = round((pdf_x - PDF_F_START + pdf_w) * px_per_pt)
        x0 = max(0, min(x0, src_w))
        x1 = max(0, min(x1, src_w))

        crop = arr_oni[0:src_h, x0:x1]

        # Target width at 600 DPI; height keeps source aspect ratio
        out_w = round(pdf_w * OUTPUT_DPI / PT_PER_INCH)

        pil_crop = Image.fromarray(crop, "RGB")
        pil_out  = pil_crop.resize((out_w, out_h), Image.LANCZOS)

        out_path = os.path.join(OUTPUT_DIR, f"{name}.png")
        pil_out.save(out_path, "PNG", dpi=(OUTPUT_DPI, OUTPUT_DPI))

        size_kb = os.path.getsize(out_path) / 1024
        print(f"  {name:4s}: src [{x0}:{x1}] {x1-x0}x{src_h}px"
              f"  →  {out_w}x{out_h}px @ {OUTPUT_DPI} DPI  ({size_kb:.0f} KB)")

    print(f"\nDone. 12 PNGs written to icons/fkey/")


if __name__ == "__main__":
    main()
