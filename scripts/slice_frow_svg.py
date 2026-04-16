#!/usr/bin/env python3
"""
slice_frow_svg.py — Slices mond_flach_3_1.svg into 12 individual F-key SVGs.

The source SVG spans the full F1–F12 row as a single artwork.
Each slice is produced by adjusting viewBox/width/height of the root <svg> element.
No path clipping needed — SVG viewBox handles cropping.

Usage:
    py -3 scripts/slice_frow_svg.py

Output: icons/fkey/F1.svg … icons/fkey/F12.svg
"""

import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ── Paths ────────────────────────────────────────────────────────────────────

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG_PATH   = os.path.join(REPO_ROOT, "icons", "mond_flach_3_1.svg")
OUTPUT_DIR = os.path.join(REPO_ROOT, "icons", "fkey")

# ── SVG Dimensions (from viewBox of mond_flach_3_1.svg) ──────────────────────

SVG_WIDTH  = 899.52756   # full artwork width in SVG units
SVG_HEIGHT = 71.811028   # full artwork height in SVG units

# ── F-key positions in PDF pt coordinates (measured from Tigry original) ─────
# Source: Brain DB handoff cb87eefb, measured at 144 DPI
# F-row: y=257.5, h=40.0 pt (all keys same height)
# F1 left edge = x=215.0 pt, F12 right edge = 965.0 pt → total width = 750pt

PDF_F_START      = 215.0   # x of F1 left edge in PDF pt
PDF_F_TOTAL_W    = 750.0   # F12_right (965) - F1_left (215)

# (name, pdf_x_left, pdf_width_pt)
F_KEYS = [
    ("F1",  215.0, 55.0),
    ("F2",  275.0, 55.0),
    ("F3",  332.5, 55.0),
    ("F4",  390.0, 55.0),
    # gap F4→F5 (35pt / 41.98 SVG units)
    ("F5",  480.0, 55.0),
    ("F6",  540.0, 52.5),
    ("F7",  595.0, 55.0),
    ("F8",  652.5, 52.5),
    # gap F8→F9 (37.5pt / 44.98 SVG units)
    ("F9",  742.5, 55.0),
    ("F10", 800.0, 55.0),
    ("F11", 855.0, 55.0),
    ("F12", 910.0, 55.0),
]

# ── Coordinate conversion ─────────────────────────────────────────────────────

SCALE = SVG_WIDTH / PDF_F_TOTAL_W   # SVG units per PDF pt ≈ 1.19937

def pdf_to_svg_x(pdf_x: float) -> float:
    return (pdf_x - PDF_F_START) * SCALE

def pdf_to_svg_w(pdf_w: float) -> float:
    return pdf_w * SCALE

# ── SVG root-element attribute patching ───────────────────────────────────────

# Matches the opening <svg ...> tag (may span multiple lines)
_SVG_TAG_RE = re.compile(r'(<svg\b[^>]*>)', re.DOTALL)

def patch_svg_root(content: str, svg_x: float, svg_w: float) -> str:
    """Replace viewBox, width, height only in the root <svg> element."""
    def _replace(m: re.Match) -> str:
        tag = m.group(1)
        tag = re.sub(r'\bviewBox="[^"]*"',
                     f'viewBox="{svg_x:.6f} 0 {svg_w:.6f} {SVG_HEIGHT:.6f}"', tag)
        tag = re.sub(r'\bwidth="[^"]*"',  f'width="{svg_w:.6f}"',  tag)
        tag = re.sub(r'\bheight="[^"]*"', f'height="{SVG_HEIGHT:.6f}"', tag)
        return tag

    return _SVG_TAG_RE.sub(_replace, content, count=1)

# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Reading {SVG_PATH} …")
    with open(SVG_PATH, "r", encoding="utf-8") as fh:
        source = fh.read()

    print(f"Scale factor: {SCALE:.6f} SVG-units per PDF-pt")
    print(f"Output dir:   {OUTPUT_DIR}\n")

    for name, pdf_x, pdf_w in F_KEYS:
        svg_x = pdf_to_svg_x(pdf_x)
        svg_w = pdf_to_svg_w(pdf_w)

        sliced = patch_svg_root(source, svg_x, svg_w)

        out_path = os.path.join(OUTPUT_DIR, f"{name}.svg")
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(sliced)

        size_kb = os.path.getsize(out_path) / 1024
        print(f"  {name:4s}: viewBox={svg_x:7.2f} 0 {svg_w:.2f} {SVG_HEIGHT:.2f}"
              f"  →  {name}.svg  ({size_kb:.0f} KB)")

    print(f"\nDone. 12 SVGs written to icons/fkey/")

if __name__ == "__main__":
    main()
