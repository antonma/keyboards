#!/usr/bin/env python3
"""
build_keycap_coordinate_map.py
==============================
Analysiert GK75-TheWell-omni-mask_2_mond.pdf via PyMuPDF und erstellt
eine vollständige Koordinaten-Karte aller Keycaps als JSON.

Strategie:
  - Hardcoded GK75-ISO-DE Positions-Grid (expected cx/cy per key)
  - Distance-Matching: jeder Expected-Position wird die nächste Fill-Kurve zugeordnet
  - Wenn keine Fill gefunden (z.B. F1-F12 unter Mond-Bildern): synthesized=true

Output: layouts/keycap-coordinate-map.json
"""

import io
import sys
import json
import math
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import fitz  # PyMuPDF

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).parent.parent
PDF_PATH  = REPO_ROOT / 'templates' / 'GK75-TheWell-omni-mask_2_mond.pdf'
OUT_PATH  = REPO_ROOT / 'layouts' / 'keycap-coordinate-map.json'

# ---------------------------------------------------------------------------
# GK75 ISO-DE hardcoded expected key positions
# Format: (id, name, cx, cy, width, height, group)
# Coordinates: PyMuPDF (y=0 top-left), in PDF points
#
# Measured from actual PDF detections + synthesized for F1-F12
# ---------------------------------------------------------------------------
# Base measurements (from detected keys):
#   1u width = 52.1px, 1u height = 52.1px
#   Alpha row pitch (cx-to-cx) = 54.9px ≈ 55px
#   F-key pitch = 53.5px (range F1-F12: x=202→833)
#   Row cy values: frow=280, numrow=351, tabrow=406, homerow=461, shiftrow=517, botrow=571
#
# Widths (u → px):
#   1u=52, 1.25u=65.8, 1.5u=79.7, 1.75u=93.3, 2u=104, 6.5u=340.8
# ---------------------------------------------------------------------------

GK75_ISO_DE = [
    # ── F-Row (cy≈280) ────────────────────────────────────────────────────
    # ESC measured directly; F1-F12 synthesized (under moon images)
    ('esc',  'ESC',   149.4, 280.0,  52.1, 52.1, 'accent'),
    ('f1',   'F1',    228.0, 280.0,  52.1, 52.1, 'fkey'),   # synthesized
    ('f2',   'F2',    281.5, 280.0,  52.1, 52.1, 'fkey'),   # synthesized
    ('f3',   'F3',    335.0, 280.0,  52.1, 52.1, 'fkey'),   # synthesized
    ('f4',   'F4',    388.5, 280.0,  52.1, 52.1, 'fkey'),   # synthesized
    ('f5',   'F5',    442.0, 280.0,  52.1, 52.1, 'fkey'),   # synthesized
    ('f6',   'F6',    495.5, 280.0,  52.1, 52.1, 'fkey'),   # synthesized
    ('f7',   'F7',    549.0, 280.0,  52.1, 52.1, 'fkey'),   # synthesized
    ('f8',   'F8',    602.5, 280.0,  52.1, 52.1, 'fkey'),   # synthesized
    ('f9',   'F9',    656.0, 280.0,  52.1, 52.1, 'fkey'),   # synthesized
    ('f10',  'F10',   709.5, 280.0,  52.1, 52.1, 'fkey'),   # synthesized
    ('f11',  'F11',   763.0, 280.0,  52.1, 52.1, 'fkey'),   # synthesized
    ('f12',  'F12',   816.5, 280.0,  52.1, 52.1, 'fkey'),   # synthesized

    # ── Num-Row (cy≈351) ──────────────────────────────────────────────────
    # Pitch: 55px; Backspace is 2u (cx=891 confirmed)
    ('grave',      '^',   149.4, 351.0,  52.1, 52.1, 'alpha'),
    ('num1',       '1',   204.4, 351.0,  52.1, 52.1, 'alpha'),
    ('num2',       '2',   259.4, 351.0,  52.1, 52.1, 'alpha'),
    ('num3',       '3',   314.4, 351.0,  52.1, 52.1, 'alpha'),
    ('num4',       '4',   369.4, 351.0,  52.1, 52.1, 'alpha'),
    ('num5',       '5',   424.4, 351.0,  52.1, 52.1, 'alpha'),
    ('num6',       '6',   479.4, 351.0,  52.1, 52.1, 'alpha'),
    ('num7',       '7',   534.4, 351.0,  52.1, 52.1, 'alpha'),
    ('num8',       '8',   589.4, 351.0,  52.1, 52.1, 'alpha'),
    ('num9',       '9',   644.4, 351.0,  52.1, 52.1, 'alpha'),
    ('num0',       '0',   699.4, 351.0,  52.1, 52.1, 'alpha'),
    ('ss',         'ß',   754.4, 351.0,  52.1, 52.1, 'alpha'),
    ('acute',      '´',   809.4, 351.0,  52.1, 52.1, 'alpha'),
    ('backspace',  '⟵',  891.3, 351.0, 107.2, 52.1, 'mod'),   # 2u
    ('entf',       'ENTF', 988.6, 351.0,  52.1, 52.1, 'fkey'),

    # ── Tab-Row (cy≈406) ──────────────────────────────────────────────────
    ('tab',   '↹',   163.2, 406.0,  79.7, 52.1, 'mod'),    # 1.5u
    ('q',     'Q',   231.9, 406.0,  52.1, 52.1, 'alpha'),
    ('w',     'W',   286.8, 406.0,  52.1, 52.1, 'alpha'),
    ('e',     'E',   341.8, 406.0,  52.1, 52.1, 'alpha'),
    ('r',     'R',   396.7, 406.0,  52.1, 52.1, 'alpha'),
    ('t',     'T',   451.7, 406.0,  52.1, 52.1, 'alpha'),
    ('z',     'Z',   506.6, 406.0,  52.1, 52.1, 'alpha'),
    ('u',     'U',   561.6, 406.0,  52.1, 52.1, 'alpha'),
    ('i',     'I',   616.5, 406.0,  52.1, 52.1, 'alpha'),
    ('o',     'O',   671.5, 406.0,  52.1, 52.1, 'alpha'),
    ('p',     'P',   726.4, 406.0,  52.1, 52.1, 'alpha'),
    ('ue',    'Ü',   781.4, 406.0,  52.1, 52.1, 'alpha'),
    ('plus',  '+',   836.3, 406.0,  52.1, 52.1, 'alpha'),
    # ISO Enter spans tabrow + homerow (tall key)
    ('enter', '↵',   906.4, 434.1,  79.5,107.0, 'accent'),
    ('pgup',  'Bild↑', 988.7, 406.0, 52.1, 52.1, 'nav'),

    # ── Home-Row (cy≈461) ─────────────────────────────────────────────────
    ('caps',  '⇪',   170.1, 461.0,  93.3, 52.1, 'mod'),    # 1.75u
    ('a',     'A',   244.9, 461.0,  52.1, 52.1, 'alpha'),
    ('s',     'S',   300.0, 461.0,  52.1, 52.1, 'alpha'),
    ('d',     'D',   355.1, 461.0,  52.1, 52.1, 'alpha'),
    ('f_key', 'F',   410.0, 461.0,  52.1, 52.1, 'alpha'),
    ('g',     'G',   465.0, 461.0,  52.1, 52.1, 'alpha'),
    ('h',     'H',   519.9, 461.0,  52.1, 52.1, 'alpha'),
    ('j',     'J',   574.8, 461.0,  52.1, 52.1, 'alpha'),
    ('k',     'K',   629.7, 461.0,  52.1, 52.1, 'alpha'),
    ('l',     'L',   684.6, 461.0,  52.1, 52.1, 'alpha'),
    ('oe',    'Ö',   739.5, 461.0,  52.1, 52.1, 'alpha'),
    ('ae',    'Ä',   794.4, 461.0,  52.1, 52.1, 'alpha'),
    ('hash',  '#',   851.2, 461.0,  52.1, 52.1, 'alpha'),
    ('pgdn',  'Bild↓', 988.7, 461.0, 52.1, 52.1, 'nav'),

    # ── Shift-Row (cy≈517) ────────────────────────────────────────────────
    ('lshift', '⇧',   155.8, 517.0,  65.8, 52.1, 'mod'),   # 1.25u
    ('angle',  '<',   217.6, 517.0,  52.1, 52.1, 'alpha'),
    ('y',      'Y',   272.6, 517.0,  52.1, 52.1, 'alpha'),
    ('x',      'X',   327.6, 517.0,  52.1, 52.1, 'alpha'),
    ('c',      'C',   382.6, 517.0,  52.1, 52.1, 'alpha'),
    ('v',      'V',   437.6, 517.0,  52.1, 52.1, 'alpha'),
    ('b',      'B',   492.6, 517.0,  52.1, 52.1, 'alpha'),
    ('n',      'N',   547.6, 517.0,  52.1, 52.1, 'alpha'),
    ('m',      'M',   602.6, 517.0,  52.1, 52.1, 'alpha'),
    ('comma',  ',',   657.6, 517.0,  52.1, 52.1, 'alpha'),
    ('dot',    '.',   712.6, 517.0,  52.1, 52.1, 'alpha'),
    ('dash',   '-',   767.6, 517.0,  52.1, 52.1, 'alpha'),
    ('rshift', '⇧',   843.8, 517.0,  93.4, 52.1, 'mod'),   # 1.75u
    ('up',     '↑',   932.9, 530.4,  52.1, 52.1, 'accent'),

    # ── Bottom-Row (cy≈571) ───────────────────────────────────────────────
    ('lctrl',  'STRG', 156.3, 571.0,  65.8, 52.1, 'mod'),  # 1.25u
    ('win',    'WIN',  225.0, 571.0,  65.8, 52.1, 'mod'),  # 1.25u
    ('lalt',   'ALT',  293.7, 571.0,  65.7, 52.1, 'mod'),  # 1.25u
    ('space',  '',     500.5, 572.1, 340.8, 52.1, 'accent'), # 6.5u
    ('ralt',   'ALT',  699.9, 571.0,  52.1, 52.1, 'mod'),
    ('fn',     'FN',   755.0, 571.0,  52.1, 52.1, 'mod'),
    ('rctrl',  'STRG', 810.1, 571.0,  52.1, 52.1, 'mod'),
    ('left',   '←',    877.7, 585.3,  52.1, 52.1, 'accent'),
    ('down',   '↓',    932.7, 585.3,  52.1, 52.1, 'accent'),
    ('right',  '→',    987.8, 585.3,  52.1, 52.1, 'accent'),

    # ── Nav Column (above F-row, y≈170-222) ──────────────────────────────
    ('enc',    'ENC',   929.4, 196.0,  52.1, 52.1, 'mod'),  # Rotary encoder button
    ('pos1',   'POS 1', 988.6, 196.0,  52.1, 52.1, 'nav'),

    # ── Nav Column (F-row level, y≈251-309) ───────────────────────────────
    ('ende',   'ENDE',  988.6, 280.0,  52.1, 52.1, 'nav'),  # End key
]

# Keys that are expected to be missing (under images) → will be synthesized
SYNTHESIZED_IDS = {'f1','f2','f3','f4','f5','f6','f7','f8','f9','f10','f11','f12'}

# ---------------------------------------------------------------------------
# Match threshold: max distance (px) between expected cx/cy and fill cx/cy
# ---------------------------------------------------------------------------
MATCH_THRESHOLD = 25


def hex_from_fill(fill):
    """PyMuPDF fill tuple (r,g,b[,a]) → #RRGGBB."""
    r, g, b = fill[0], fill[1], fill[2]
    return f'#{int(round(r*255)):02X}{int(round(g*255)):02X}{int(round(b*255)):02X}'


def extract_fills(page, min_area=1200):
    """Return list of {x0,y0,x1,y1,cx,cy,w,h,fill_hex,area} for fill paths."""
    fills = []
    for d in page.get_drawings():
        f = d.get('fill')
        if f is None:
            continue
        r = d['rect']
        w = r.x1 - r.x0
        h = r.y1 - r.y0
        area = w * h
        if area < min_area:
            continue
        # Exclude full-page backgrounds and moon-image tiles (h>115).
        # ISO Enter is h≈107 and must pass. Moon images are h≥135.
        if w > 400 or h > 115:
            continue
        fills.append({
            'x0': round(r.x0, 1), 'y0': round(r.y0, 1),
            'x1': round(r.x1, 1), 'y1': round(r.y1, 1),
            'cx': round((r.x0 + r.x1) / 2, 1),
            'cy': round((r.y0 + r.y1) / 2, 1),
            'w':  round(w, 1), 'h': round(h, 1),
            'area': round(area, 1),
            'fill_hex': hex_from_fill(f),
        })
    return fills


def build_map(pdf_path):
    doc  = fitz.open(str(pdf_path))
    page = doc[0]
    page_w = round(page.rect.width, 1)
    page_h = round(page.rect.height, 1)
    print(f"PDF: {pdf_path.name}  ({page_w}×{page_h} pt)")

    fills = extract_fills(page)
    print(f"Keycap-Kandidaten nach Filter: {len(fills)}")
    doc.close()

    # Build result
    result_keys = []
    used_fill_indices = set()

    for (kid, name, ecx, ecy, ew, eh, egroup) in GK75_ISO_DE:
        best_idx  = None
        best_dist = MATCH_THRESHOLD

        for i, f in enumerate(fills):
            if i in used_fill_indices:
                continue
            dist = math.sqrt((f['cx'] - ecx)**2 + (f['cy'] - ecy)**2)
            if dist < best_dist:
                best_dist = dist
                best_idx  = i

        if best_idx is not None:
            f = fills[best_idx]
            used_fill_indices.add(best_idx)
            # Use actual detected coordinates
            x0, y0, x1, y1 = f['x0'], f['y0'], f['x1'], f['y1']
            cx, cy = f['cx'], f['cy']
            w, h    = f['w'], f['h']
            fill_hex = f['fill_hex']
            synthesized = False
        else:
            # Synthesize from expected position
            x0 = round(ecx - ew / 2, 1)
            y0 = round(ecy - eh / 2, 1)
            x1 = round(ecx + ew / 2, 1)
            y1 = round(ecy + eh / 2, 1)
            cx, cy = round(ecx, 1), round(ecy, 1)
            w, h    = ew, eh
            fill_hex = None
            synthesized = True

        key = {
            'id':          kid,
            'name':        name,
            'group':       egroup,
            'x0': x0, 'y0': y0, 'x1': x1, 'y1': y1,
            'cx': cx,   'cy': cy,
            'width': w,  'height': h,
            'width_u': round(w / 52.1, 2),
            'fill_hex':    fill_hex,
            'synthesized': synthesized,
        }
        result_keys.append(key)

    # Report unmatched fills (not assigned to any key)
    unmatched = [fills[i] for i in range(len(fills)) if i not in used_fill_indices]

    return result_keys, unmatched, page_w, page_h


def print_table(keys):
    synth_marker = lambda k: '*' if k['synthesized'] else ' '
    print(f"\n{'':1s}  {'ID':20s}  {'Name':6s}  {'Group':7s}  {'X0':6s} {'Y0':6s} {'X1':6s} {'Y1':6s}  {'W×H':11s}  {'Color':8s}")
    print('-' * 105)
    for k in keys:
        color = k['fill_hex'] or '(synth)'
        print(f"{synth_marker(k)}  {k['id']:20s}  {k['name']:6s}  {k['group']:7s}  "
              f"{k['x0']:6.1f} {k['y0']:6.1f} {k['x1']:6.1f} {k['y1']:6.1f}  "
              f"{k['width']:5.1f}×{k['height']:5.1f}  {color}")


def main():
    if not PDF_PATH.exists():
        print(f"ERROR: {PDF_PATH} nicht gefunden")
        sys.exit(1)

    keys, unmatched, page_w, page_h = build_map(PDF_PATH)

    print_table(keys)

    n_synth = sum(1 for k in keys if k['synthesized'])
    n_found = len(keys) - n_synth
    print(f"\n{len(keys)} Keys total: {n_found} gefunden, {n_synth} synthetisiert")

    if unmatched:
        print(f"\n{len(unmatched)} nicht zugeordnete Fills:")
        for f in sorted(unmatched, key=lambda x: x['cy']):
            print(f"  cx={f['cx']:.0f} cy={f['cy']:.0f}  {f['w']:.0f}×{f['h']:.0f}  {f['fill_hex']}")

    # Write JSON
    output = {
        'keyboard':   'GK75',
        'layout':     'ISO-DE',
        'source_pdf': PDF_PATH.name,
        'page_width':  page_w,
        'page_height': page_h,
        'key_count':  len(keys),
        'note': 'F1-F12 sind synthetisiert (unter Mond-Bildern; fill_hex=null). '
                'Alle anderen Koordinaten aus PDF-Fill-Pfaden gemessen.',
        'keys': keys,
    }

    OUT_PATH.parent.mkdir(exist_ok=True)
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Gespeichert: {OUT_PATH}")

    from collections import Counter
    groups = Counter(k['group'] for k in keys)
    print(f"Gruppen: {dict(sorted(groups.items()))}")


if __name__ == '__main__':
    main()
