#!/usr/bin/env python3
"""
GK75-TheWell-v7 → v8: Spacebar water/well motif (SVG vector overlay)

Design: Concentric ellipses on spacebar, light (#BCC6D0) → dark (#1A2530).
        Matches the well-ripple aesthetic from the design document cover image.

Strategy:
  1. Auto-detect spacebar rect from get_drawings() (largest path in bottom row)
  2. Load SVG from assets/spacebar-well.svg
  3. Embed as true PDF vector via show_pdf_page()
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import fitz
from pathlib import Path


# Bottom row Y range in PyMuPDF coords (y=0 at top)
BOTTOM_ROW_Y0 = 535
BOTTOM_ROW_Y1 = 607
MIN_SPACEBAR_WIDTH = 280   # px — spacebar is by far the widest key


def detect_spacebar(page) -> fitz.Rect:
    """Find spacebar rect: largest filled path in the bottom row."""
    drawings = page.get_drawings()
    best = None
    best_w = 0.0

    for path in drawings:
        if path.get('fill') is None:
            continue
        r = path['rect']
        # Must be in bottom row Y band
        cy = (r.y0 + r.y1) / 2
        if not (BOTTOM_ROW_Y0 <= cy <= BOTTOM_ROW_Y1):
            continue
        w = r.x1 - r.x0
        if w > best_w:
            best_w = w
            best = r

    if best is None or best_w < MIN_SPACEBAR_WIDTH:
        raise RuntimeError(
            f"Spacebar not found! (widest bottom-row path: {best_w:.0f}px)\n"
            f"Adjust BOTTOM_ROW_Y0/Y1 or MIN_SPACEBAR_WIDTH."
        )
    return best


def make_v8(input_path: str, output_path: str, svg_path: str):
    pdf = fitz.open(input_path)
    page = pdf[0]

    # 1. Detect spacebar
    spacebar = detect_spacebar(page)
    print(f"Spacebar detected: ({spacebar.x0:.1f}, {spacebar.y0:.1f}, "
          f"{spacebar.x1:.1f}, {spacebar.y1:.1f})  "
          f"[{spacebar.x1 - spacebar.x0:.1f} × {spacebar.y1 - spacebar.y0:.1f} px]")

    # 2. Load SVG
    svg_bytes = Path(svg_path).read_bytes()
    print(f"SVG loaded: {len(svg_bytes)} bytes from {svg_path}")

    # 3. Open SVG as fitz document → convert to PDF bytes → embed as vector
    svg_doc = fitz.open("svg", svg_bytes)
    tmp_pdf_bytes = svg_doc.convert_to_pdf()
    svg_pdf = fitz.open("pdf", tmp_pdf_bytes)

    # show_pdf_page places the SVG page content scaled to fit spacebar_rect (true vector)
    page.show_pdf_page(spacebar, svg_pdf, 0)
    print("SVG embedded into spacebar (true vector)")

    pdf.save(output_path)
    pdf.close()
    print(f"\nSaved: {output_path}")


if __name__ == '__main__':
    repo_root = Path(__file__).parent.parent
    input_pdf  = repo_root / 'templates' / 'GK75-TheWell-v7.pdf'
    output_pdf = repo_root / 'templates' / 'GK75-TheWell-v8.pdf'
    svg_file   = repo_root / 'assets'    / 'spacebar-well.svg'

    if len(sys.argv) == 3:
        input_pdf  = Path(sys.argv[1])
        output_pdf = Path(sys.argv[2])

    print(f'Input:  {input_pdf}')
    print(f'Output: {output_pdf}')
    print(f'SVG:    {svg_file}')
    print()

    tmp = str(output_pdf) + '.tmp'
    make_v8(str(input_pdf), tmp, str(svg_file))

    import shutil, os
    if os.path.exists(str(output_pdf)):
        os.remove(str(output_pdf))
    shutil.move(tmp, str(output_pdf))
    print('Done.')
