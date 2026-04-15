#!/usr/bin/env python3
"""
Apply per-group legend colors to vector path legends in GK75-TheWell-v6.pdf.

Groups:
  Alpha legends:    keep #8899AA (no overdraw)
  Modifier legends: → #5A7A90
  F-key legends:    → #4A6070
  Accent legends:   → #2A3540

Classification per legend path:
  1. Find the smallest background path (w>25, h>15) that contains the legend center.
  2. If background fill ≈ #C8D0D8 (accent key) → TARGET_ACCENT
  3. If background fill ≈ #202830 (modifier key, rendered from #1E2830) → TARGET_MODIFIER
  4. If Y center in F-key row (252–312) → TARGET_FKEY
  5. Otherwise → TARGET_ALPHA (no change)

Strategy: overdraw — draw each glyph path again in the target RGB color, on top of
the existing CMYK path. Later PDF operations paint over earlier ones.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import fitz
from pathlib import Path


def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))


def color_dist(c1, c2):
    if c1 is None or c2 is None:
        return 999.0
    return sum((a - b) ** 2 for a, b in zip(c1, c2)) ** 0.5


# --- Legend color threshold ---
# In v6.pdf the CMYK legend color #8899AA renders via ICC as #8999A9
LEGEND_RENDERED = (0x89/255, 0x99/255, 0xA9/255)
LEGEND_TOL = 22/255          # ≈ 22 out of 255 per channel

# --- Key fill colors (as rendered by PyMuPDF after ICC) ---
ACCENT_RENDERED   = hex_to_rgb('#C8D0D8')   # pale ghostly white
ACCENT_TOL        = 35/255

MODIFIER_RENDERED = (0x20/255, 0x28/255, 0x30/255)  # dark teal #202830
MODIFIER_TOL      = 20/255

# F-key row Y range (PyMuPDF coords, y=0 at top)
FKEY_Y0, FKEY_Y1 = 252, 312

# --- Target colors ---
TARGET_ALPHA    = hex_to_rgb('#8899AA')   # keep (no overdraw)
TARGET_MODIFIER = hex_to_rgb('#5A7A90')
TARGET_FKEY     = hex_to_rgb('#4A6070')
TARGET_ACCENT   = hex_to_rgb('#2A3540')


def is_legend_path(path):
    fill = path.get('fill')
    if fill is None:
        return False
    rect = path['rect']
    if (rect.x1 - rect.x0) < 0.5 or (rect.y1 - rect.y0) < 0.5:
        return False  # skip zero-size points
    return color_dist(fill, LEGEND_RENDERED) < LEGEND_TOL


def classify_legend(path, bg_paths):
    """Return target color tuple, or TARGET_ALPHA if no change needed."""
    rect = path['rect']
    cx = (rect.x0 + rect.x1) / 2
    cy = (rect.y0 + rect.y1) / 2

    # Find the smallest background path whose rect contains this legend center
    best_bg = None
    best_area = float('inf')
    for bg in bg_paths:
        br = bg['rect']
        if br.x0 <= cx <= br.x1 and br.y0 <= cy <= br.y1:
            area = (br.x1 - br.x0) * (br.y1 - br.y0)
            if area < best_area:
                best_area = area
                best_bg = bg

    if best_bg is not None:
        bg_fill = best_bg.get('fill')
        if bg_fill is not None:
            if color_dist(bg_fill, ACCENT_RENDERED) < ACCENT_TOL:
                return TARGET_ACCENT
            if color_dist(bg_fill, MODIFIER_RENDERED) < MODIFIER_TOL:
                return TARGET_MODIFIER

    # Y-range fallback for F-keys (fill renders same as alpha after ICC)
    if FKEY_Y0 <= cy <= FKEY_Y1:
        return TARGET_FKEY

    return TARGET_ALPHA


def redraw_path(shape, path, color):
    """Overdraw a get_drawings() path with a new fill color."""
    items = path.get('items', [])
    if not items:
        return False

    for item in items:
        op = item[0]
        if op == 'l':
            shape.draw_line(item[1], item[2])
        elif op == 'c':
            shape.draw_bezier(item[1], item[2], item[3], item[4])
        elif op == 're':
            shape.draw_rect(item[1])
        elif op == 'qu':
            shape.draw_quad(item[1])

    even_odd = path.get('even_odd', True)
    shape.finish(fill=color, color=None, even_odd=even_odd)
    return True


def apply_legend_colors(input_path, output_path):
    pdf = fitz.open(input_path)
    page = pdf[0]

    drawings = page.get_drawings()
    print(f"Total drawings: {len(drawings)}")

    # Separate legend paths from background key-fill paths
    legend_paths = []
    bg_paths = []

    for path in drawings:
        rect = path['rect']
        w = rect.x1 - rect.x0
        h = rect.y1 - rect.y0
        if is_legend_path(path):
            legend_paths.append(path)
        elif path.get('fill') is not None and w > 25 and h > 15:
            bg_paths.append(path)

    print(f"Legend paths: {len(legend_paths)}")
    print(f"Background paths: {len(bg_paths)}")

    # Classify
    groups = {'alpha': [], 'modifier': [], 'fkey': [], 'accent': []}
    for lp in legend_paths:
        target = classify_legend(lp, bg_paths)
        if target == TARGET_MODIFIER:
            groups['modifier'].append((lp, target))
        elif target == TARGET_FKEY:
            groups['fkey'].append((lp, target))
        elif target == TARGET_ACCENT:
            groups['accent'].append((lp, target))
        else:
            groups['alpha'].append((lp, target))

    print(f"\nClassification:")
    for name, items in groups.items():
        print(f"  {name:10s}: {len(items):4d} paths")

    total_to_draw = len(groups['modifier']) + len(groups['fkey']) + len(groups['accent'])
    print(f"\nPaths to overdraw: {total_to_draw}")

    if total_to_draw == 0:
        print("Nothing to overdraw.")
        pdf.save(output_path)
        pdf.close()
        return

    # Overdraw in target colors
    shape = page.new_shape()
    drawn = 0
    for group_name in ('modifier', 'fkey', 'accent'):
        for path, color in groups[group_name]:
            if redraw_path(shape, path, color):
                drawn += 1
    shape.commit()

    print(f"Drew {drawn} paths")

    pdf.save(output_path)
    pdf.close()
    print(f"\nSaved: {output_path}")


if __name__ == '__main__':
    repo_root = Path(__file__).parent.parent
    input_pdf  = repo_root / 'templates' / 'GK75-TheWell-v6.pdf'
    output_pdf = repo_root / 'templates' / 'GK75-TheWell-v6.pdf'

    if len(sys.argv) == 3:
        input_pdf  = Path(sys.argv[1])
        output_pdf = Path(sys.argv[2])

    print(f'Input:  {input_pdf}')
    print(f'Output: {output_pdf}')
    print()

    tmp = str(output_pdf) + '.tmp'
    apply_legend_colors(str(input_pdf), tmp)

    import shutil, os
    if os.path.exists(str(output_pdf)):
        os.remove(str(output_pdf))
    shutil.move(tmp, str(output_pdf))
    print('Done.')
