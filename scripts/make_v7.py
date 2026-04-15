#!/usr/bin/env python3
"""
GK75-TheWell-v6 → v7: Modifier/Nav labels uppercase (matches keycap-layouts-iso-de.html)

Changes:
  Esc   → ESC    (#2A3540 on accent key)
  Strg  → STRG   (#5A7A90 on modifier key)  [left]
  Win   → WIN    (#5A7A90)
  Alt   → ALT    (#5A7A90)                  [left + right]
  Fn    → FN     (#5A7A90)
  Pos 1 → POS 1  (#5A7A90 on nav key)
  Entf  → ENTF   (#4A6070 on fkey)

Strategy: redact old label area → insert uppercase text via TextWriter.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import fitz
from pathlib import Path

FONT_PATH = r'C:\Windows\Fonts\seguisym.ttf'


def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))


# Key background fill colors (for redact fill)
ACCENT_FILL   = hex_to_rgb('#C8D0D8')   # Esc
MOD_FILL      = hex_to_rgb('#1E2830')   # Strg, Win, Alt, Fn
NAV_FILL      = hex_to_rgb('#1A2530')   # Pos 1
FKEY_FILL     = hex_to_rgb('#1C2228')   # Entf

# fmt: (name, rect, label, fontsize, legend_hex, bg_fill)
KEYS = [
    ('ESC',    fitz.Rect(123, 254, 175, 306), 'ESC',   11, '#2A3540', ACCENT_FILL),
    ('Strg L', fitz.Rect(123, 545, 189, 597), 'STRG',  11, '#5A7A90', MOD_FILL),
    ('Win',    fitz.Rect(192, 545, 258, 597), 'WIN',   11, '#5A7A90', MOD_FILL),
    ('Alt L',  fitz.Rect(261, 545, 327, 597), 'ALT',   11, '#5A7A90', MOD_FILL),
    ('Alt R',  fitz.Rect(674, 545, 726, 597), 'ALT',   11, '#5A7A90', MOD_FILL),
    ('Fn',     fitz.Rect(729, 545, 781, 597), 'FN',    11, '#5A7A90', MOD_FILL),
    ('POS 1',  fitz.Rect(963, 170, 1015, 223), 'POS 1', 11, '#5A7A90', NAV_FILL),
    ('ENTF',   fitz.Rect(963, 325, 1015, 378), 'ENTF',  13, '#4A6070', FKEY_FILL),
]


def make_v7(input_path: str, output_path: str):
    pdf = fitz.open(input_path)
    page = pdf[0]
    font = fitz.Font(fontfile=FONT_PATH)

    print('Glyph check:')
    for name, _, label, _, _, _ in KEYS:
        missing = [c for c in label if not font.has_glyph(ord(c))]
        print(f'  {name:8s} "{label}": {"OK" if not missing else f"MISSING {missing}"}')
    print()

    # Step 1: Redact all old label areas at once
    for name, r, label, _, _, bg_fill in KEYS:
        inner = fitz.Rect(r.x0 + 5, r.y0 + 5, r.x1 - 5, r.y1 - 5)
        annot = page.add_redact_annot(inner)
        annot.set_colors(fill=bg_fill)
        annot.update()

    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

    # Step 2: Insert new uppercase labels — one TextWriter per legend color
    from collections import defaultdict
    groups = defaultdict(list)
    for entry in KEYS:
        groups[entry[4]].append(entry)   # group by legend_hex

    for legend_hex, entries in groups.items():
        writer = fitz.TextWriter(page.rect)
        for name, r, label, fontsize, _, _ in entries:
            key_cx = (r.x0 + r.x1) / 2
            key_cy = (r.y0 + r.y1) / 2
            text_w = font.text_length(label, fontsize=fontsize)
            x = key_cx - text_w / 2
            y = key_cy + fontsize * 0.35
            writer.append(fitz.Point(x, y), label, font=font, fontsize=fontsize)
            print(f'  {name:8s}: "{label}" at ({x:.0f}, {y:.0f}) size={fontsize}')
        writer.write_text(page, color=hex_to_rgb(legend_hex))

    pdf.save(output_path)
    pdf.close()
    print(f'\nSaved: {output_path}')


if __name__ == '__main__':
    repo_root = Path(__file__).parent.parent
    input_pdf  = repo_root / 'templates' / 'GK75-TheWell-v6.pdf'
    output_pdf = repo_root / 'templates' / 'GK75-TheWell-v7.pdf'

    if len(sys.argv) == 3:
        input_pdf  = Path(sys.argv[1])
        output_pdf = Path(sys.argv[2])

    print(f'Input:  {input_pdf}')
    print(f'Output: {output_pdf}')
    print()

    tmp = str(output_pdf) + '.tmp'
    make_v7(str(input_pdf), tmp)

    import shutil, os
    if os.path.exists(str(output_pdf)):
        os.remove(str(output_pdf))
    shutil.move(tmp, str(output_pdf))
    print('Done.')
