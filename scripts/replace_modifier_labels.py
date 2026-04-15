#!/usr/bin/env python3
"""
Replace English modifier-key labels with Cherry ISO-DE symbols.

v6 → v6 in-place (or specify input/output):
  Tab   → ↹  (U+21B9)
  CapsLk → ⇪  (U+21EA)
  Shift  → ⇧  (U+21E7)  [both left and right]
  ←     → ⟵  (U+27F5)  [Backspace]
  Del   → Entf          [regular text]

Strategy:
  1. Identify each key's bounding box (PyMuPDF coordinates)
  2. Add a redaction annotation over the label area, filled with the key's background color
  3. Apply redactions (removes old glyph paths and text under the rect)
  4. Insert new text centered in the key using Segoe UI Symbol (has all required glyphs)

Font: C:\\Windows\\Fonts\\seguisym.ttf  (Segoe UI Symbol – contains ↹ ⇪ ⇧ ⟵)
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import fitz  # PyMuPDF
from pathlib import Path

# =============================================================================
# KEY DEFINITIONS  (PyMuPDF coordinate system: y=0 is top-left)
# Positions extracted via get_drawings() analysis of GK75-TheWell-v6.pdf
# =============================================================================

# Legend colors (RGB 0-1)
def hex_to_rgb(h: str):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))

MOD_LEGEND  = hex_to_rgb('#5A7A90')  # modifier legends
MOD_FILL    = hex_to_rgb('#1E2830')  # modifier base fill
FKEY_LEGEND = hex_to_rgb('#4A6070')  # f-key / del legends

KEYS_TO_REPLACE = [
    {
        'name': 'Tab',
        'rect': fitz.Rect(123, 380, 203, 432),  # 80w × 52h
        'new_label': '\u21b9',                   # ↹
        'fill': MOD_FILL,
        'legend': MOD_LEGEND,
        'fontsize': 20,
    },
    {
        'name': 'CapsLk',
        'rect': fitz.Rect(123, 435, 217, 487),  # 94w × 52h
        'new_label': '\u21ea',                   # ⇪
        'fill': MOD_FILL,
        'legend': MOD_LEGEND,
        'fontsize': 20,
    },
    {
        'name': 'Left Shift',
        'rect': fitz.Rect(123, 491, 189, 543),  # 66w × 52h
        'new_label': '\u21e7',                   # ⇧
        'fill': MOD_FILL,
        'legend': MOD_LEGEND,
        'fontsize': 20,
    },
    {
        'name': 'Right Shift',
        'rect': fitz.Rect(797, 491, 890, 543),  # 93w × 52h
        'new_label': '\u21e7',                   # ⇧
        'fill': MOD_FILL,
        'legend': MOD_LEGEND,
        'fontsize': 20,
    },
    {
        'name': 'Backspace',
        'rect': fitz.Rect(838, 325, 945, 378),  # 107w × 53h
        'new_label': '\u27f5',                   # ⟵
        'fill': MOD_FILL,
        'legend': MOD_LEGEND,
        'fontsize': 22,
    },
    {
        'name': 'Delete',
        'rect': fitz.Rect(963, 325, 1015, 378),  # 52w × 53h
        'new_label': 'Entf',
        'fill': MOD_FILL,
        'legend': FKEY_LEGEND,
        'fontsize': 13,
    },
]

FONT_PATH = r'C:\Windows\Fonts\seguisym.ttf'


def replace_labels(input_path: str, output_path: str):
    pdf = fitz.open(input_path)
    page = pdf[0]

    font = fitz.Font(fontfile=FONT_PATH)

    # Verify all glyphs are available
    print('Glyph check:')
    for key in KEYS_TO_REPLACE:
        label = key['new_label']
        missing = [c for c in label if not font.has_glyph(ord(c))]
        status = 'OK' if not missing else f'MISSING {missing}'
        print(f"  {key['name']:12s} '{label}': {status}")
    print()

    # Step 1: Add redaction annotations over label areas
    for key in KEYS_TO_REPLACE:
        r = key['rect']
        # Redact only the inner label area (avoid key edges/highlights)
        # Shrink by 6px on each side to preserve key outline effects
        label_area = fitz.Rect(
            r.x0 + 5, r.y0 + 6,
            r.x1 - 5, r.y1 - 6
        )
        annot = page.add_redact_annot(label_area)
        # Fill with key background color
        fill = key['fill']
        annot.set_colors(fill=fill)
        annot.update()

    # Apply redactions (this removes underlying content in the annotated rects)
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

    # Step 2: Insert new labels centered in each key using TextWriter
    # (insert_text with fontfile doesn't handle high Unicode correctly;
    #  TextWriter does.)
    tw = fitz.TextWriter(page.rect)

    for key in KEYS_TO_REPLACE:
        r = key['rect']
        label = key['new_label']
        fontsize = key['fontsize']
        color = key['legend']

        # Calculate text width to center it
        text_w = font.text_length(label, fontsize=fontsize)
        key_cx = (r.x0 + r.x1) / 2
        key_cy = (r.y0 + r.y1) / 2

        # Baseline: center vertically (baseline ~35% of fontsize above center)
        x = key_cx - text_w / 2
        y = key_cy + fontsize * 0.35

        tw.append(fitz.Point(x, y), label, font=font, fontsize=fontsize)
        print(f"  {key['name']:12s}: '{label}' at ({x:.0f}, {y:.0f}), size={fontsize}")

    # Write all text in one pass — color is per-writer, so split by legend color
    # Group by legend color
    from collections import defaultdict
    groups = defaultdict(list)
    for key in KEYS_TO_REPLACE:
        groups[key['legend']].append(key)

    for legend_color, group_keys in groups.items():
        writer = fitz.TextWriter(page.rect)
        for key in group_keys:
            r = key['rect']
            label = key['new_label']
            fontsize = key['fontsize']
            text_w = font.text_length(label, fontsize=fontsize)
            x = (r.x0 + r.x1) / 2 - text_w / 2
            y = (r.y0 + r.y1) / 2 + fontsize * 0.35
            writer.append(fitz.Point(x, y), label, font=font, fontsize=fontsize)
        writer.write_text(page, color=legend_color)

    pdf.save(output_path)
    pdf.close()
    print(f'\nSaved: {output_path}')


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

    # Work on a temp copy first, then overwrite
    tmp = str(output_pdf) + '.tmp'
    replace_labels(str(input_pdf), tmp)

    import shutil, os
    if os.path.exists(str(output_pdf)):
        os.remove(str(output_pdf))
    shutil.move(tmp, str(output_pdf))
    print('Done.')
