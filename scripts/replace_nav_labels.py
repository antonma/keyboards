#!/usr/bin/env python3
"""
Replace English nav-key labels with German equivalents.

  Home  → Pos 1
  PgUp  → Bild  (two-line, ↑ below)
           ↑
  PgDn  → Bild  (two-line, ↓ below)
           ↓

Key positions (PyMuPDF coordinates, y=0 top-left):
  Home:  x=963-1015, y=170-223   (standalone above rotary)
  PgUp:  x=963-1015, y=380-432
  PgDn:  x=963-1015, y=435-487

Legend color: #5A7A90 (Nav/Modifier legends)
Fill color:   #1A2530 (Navigation base)
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import fitz
from pathlib import Path
from collections import defaultdict

FONT_PATH = r'C:\Windows\Fonts\seguisym.ttf'


def hex_to_rgb(h: str):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))


NAV_FILL   = hex_to_rgb('#1A2530')
NAV_LEGEND = hex_to_rgb('#5A7A90')

# Each entry: name, rect, lines [(text, fontsize)], fill, legend
NAV_KEYS = [
    {
        'name': 'Home',
        'rect': fitz.Rect(963, 170, 1015, 223),
        'lines': [('Pos 1', 11)],
        'fill':   NAV_FILL,
        'legend': NAV_LEGEND,
    },
    {
        'name': 'PgUp',
        'rect': fitz.Rect(963, 380, 1015, 432),
        'lines': [('Bild', 11), ('\u2191', 12)],   # ↑
        'fill':   NAV_FILL,
        'legend': NAV_LEGEND,
    },
    {
        'name': 'PgDn',
        'rect': fitz.Rect(963, 435, 1015, 487),
        'lines': [('Bild', 11), ('\u2193', 12)],   # ↓
        'fill':   NAV_FILL,
        'legend': NAV_LEGEND,
    },
]


def replace_nav_labels(input_path: str, output_path: str):
    pdf = fitz.open(input_path)
    page = pdf[0]
    font = fitz.Font(fontfile=FONT_PATH)

    print('Glyph check:')
    for key in NAV_KEYS:
        for text, _ in key['lines']:
            missing = [c for c in text if not font.has_glyph(ord(c))]
            status = 'OK' if not missing else f'MISSING {missing}'
            print(f"  {key['name']:6s} '{text}': {status}")
    print()

    # Step 1: Redact old label area in each key
    for key in NAV_KEYS:
        r = key['rect']
        label_area = fitz.Rect(r.x0 + 4, r.y0 + 5, r.x1 - 4, r.y1 - 5)
        annot = page.add_redact_annot(label_area)
        annot.set_colors(fill=key['fill'])
        annot.update()

    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

    # Step 2: Insert labels using TextWriter
    writer = fitz.TextWriter(page.rect)

    for key in NAV_KEYS:
        r = key['rect']
        lines = key['lines']
        key_cx = (r.x0 + r.x1) / 2
        key_cy = (r.y0 + r.y1) / 2
        n = len(lines)

        if n == 1:
            # Single line — center in key
            text, fontsize = lines[0]
            tw = font.text_length(text, fontsize=fontsize)
            x = key_cx - tw / 2
            y = key_cy + fontsize * 0.35
            writer.append(fitz.Point(x, y), text, font=font, fontsize=fontsize)
            print(f"  {key['name']:6s}: '{text}' at ({x:.0f}, {y:.0f}) size={fontsize}")
        else:
            # Two lines — center the block vertically in the key
            leading = 3  # px gap between lines
            total_h = sum(fs for _, fs in lines) + leading * (n - 1)
            block_top = key_cy - total_h / 2

            y_cursor = block_top
            for i, (text, fontsize) in enumerate(lines):
                tw = font.text_length(text, fontsize=fontsize)
                x = key_cx - tw / 2
                y = y_cursor + fontsize * 0.85   # baseline within line
                writer.append(fitz.Point(x, y), text, font=font, fontsize=fontsize)
                print(f"  {key['name']:6s} L{i+1}: '{text}' at ({x:.0f}, {y:.0f}) size={fontsize}")
                y_cursor += fontsize + leading

    writer.write_text(page, color=NAV_LEGEND)

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

    tmp = str(output_pdf) + '.tmp'
    replace_nav_labels(str(input_pdf), tmp)

    import shutil, os
    if os.path.exists(str(output_pdf)):
        os.remove(str(output_pdf))
    shutil.move(tmp, str(output_pdf))
    print('Done.')
