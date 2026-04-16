#!/usr/bin/env python3
"""
Tigry Slot Identification via Point-Sampling
=============================================
Für jeden bekannten GK75-Key-Mittelpunkt:
→ Findet den GRÖSSTEN Fill-Pfad, dessen BBox den Punkt enthält.
→ Gibt die Fill-Farbe zurück = Key-Background-Farbe an dieser Position.

Damit können wir eindeutig sagen: "Welcher Tigry-Hex-Wert = welche Taste"
ohne rate work.
"""

import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pathlib import Path
import fitz

# =============================================================================
# Bekannte Key-Mittelpunkte (aus CLAUDE.md + Mittelung)
# Format: 'name': (cx, cy)
# =============================================================================
KEY_CENTERS = {
    # F-Key Zeile (y: 254-306 → cy≈280)
    'ESC':      (149, 280),
    'F1':       (212, 280),
    'F2':       (257, 280),   # approx
    'F5':       (392, 280),
    'F6':       (460, 280),
    'F10':      (648, 280),
    'F12':      (748, 280),

    # Zahlenzeile (y: 325-378 → cy≈351)
    '1':        (175, 351),
    '2':        (220, 351),
    'Q_NUM':    (267, 351),   # 3
    'BACKSPACE':(892, 351),
    'ENTF':     (989, 351),

    # Tab-Zeile (y: 380-432 → cy≈406)
    'TAB':      (163, 406),
    'Q':        (225, 406),
    'W':        (270, 406),
    'ENTER':    (820, 406),   # approximate Enter center (may span 2 rows)
    'PGUP':     (989, 406),

    # CapsLk-Zeile (y: 435-487 → cy≈461)
    'CAPS':     (170, 461),
    'A':        (235, 461),
    'S':        (280, 461),
    'PGDN':     (989, 461),

    # Shift-Zeile (y: 491-543 → cy≈517)
    'LSHIFT':   (156, 517),
    'Z':        (240, 517),
    'X':        (285, 517),
    'RSHIFT':   (844, 517),

    # Bottom-Zeile (y: 545-597 → cy≈571)
    'LCTRL':    (156, 571),
    'WIN':      (225, 571),
    'LALT':     (294, 571),
    'SPACE':    (503, 571),
    'RALT':     (700, 571),
    'FN':       (755, 571),
    'RCTRL':    (813, 571),

    # Pfeile (y≈560-590)
    'LEFT':     (870, 590),
    'DOWN':     (912, 590),
    'RIGHT':    (957, 590),
    'UP':       (912, 560),

    # Nav-Spalte rechts
    'NAV_TOP':  (989, 187),   # POS1 / Rotary area
}

# Erwartete Ziel-Farben pro Taste (ONI MASK V2 ADR)
ONI_TARGETS = {
    'ESC':      '#A88B63',   # Gold
    'F1':       '#2A2D32',   # F-Key dark
    'F2':       '#2A2D32',
    'F5':       '#2A2D32',
    'F6':       '#2A2D32',
    'F10':      '#2A2D32',
    'F12':      '#2A2D32',
    '1':        '#1B1D20',   # Alpha dark
    '2':        '#1B1D20',
    'Q_NUM':    '#1B1D20',
    'BACKSPACE':'#6F2D2C',   # Mod red
    'ENTF':     '#2A2D32',   # F-Key (Entf)
    'TAB':      '#6F2D2C',   # Mod
    'Q':        '#1B1D20',
    'W':        '#1B1D20',
    'ENTER':    '#A88B63',   # Gold
    'PGUP':     '#6F2D2C',   # Mod
    'CAPS':     '#6F2D2C',   # Mod
    'A':        '#1B1D20',
    'S':        '#1B1D20',
    'PGDN':     '#6F2D2C',   # Mod
    'LSHIFT':   '#6F2D2C',   # Mod
    'Z':        '#1B1D20',
    'X':        '#1B1D20',
    'RSHIFT':   '#6F2D2C',   # Mod
    'LCTRL':    '#6F2D2C',   # Mod
    'WIN':      '#6F2D2C',   # Mod
    'LALT':     '#6F2D2C',   # Mod
    'SPACE':    '#A88B63',   # Gold
    'RALT':     '#6F2D2C',   # Mod
    'FN':       '#6F2D2C',   # Mod
    'RCTRL':    '#6F2D2C',   # Mod
    'LEFT':     '#A88B63',   # Gold (Pfeile)
    'DOWN':     '#A88B63',
    'RIGHT':    '#A88B63',
    'UP':       '#A88B63',
    'NAV_TOP':  '#6F2D2C',   # Mod
}


def get_color_at_point(drawings, px, py, min_area=300, max_area=30000):
    """
    Findet den KLEINSTEN geeigneten Fill-Pfad, dessen BBox den Punkt enthält.

    min_area: Mindestgröße — schließt Outline-Artefakte aus
    max_area: Maximalgröße — schließt Keyboard-Hintergrund aus

    Ein einzelner GK75-Key ist ~2500–18000 px².
    Keyboard-Hintergrund wäre >100000 px².
    """
    candidates = []
    for d in drawings:
        if d.get('fill') is None:
            continue
        r = d['rect']
        if r.x0 <= px <= r.x1 and r.y0 <= py <= r.y1:
            area = (r.x1 - r.x0) * (r.y1 - r.y0)
            if min_area <= area <= max_area:
                rgb = d['fill']
                hex_c = f"#{int(round(rgb[0]*255)):02X}{int(round(rgb[1]*255)):02X}{int(round(rgb[2]*255)):02X}"
                # Exclude pure black (outlines/text)
                if hex_c not in ('#000000', '#010101'):
                    candidates.append((hex_c, area))

    if not candidates:
        return None, 0
    # Return color of SMALLEST containing bbox (= most specific key background)
    candidates.sort(key=lambda x: x[1])
    return candidates[0]


def hex_close(h1, h2, tol=25):
    """Prüft ob zwei Hex-Farben innerhalb Toleranz liegen (CMYK ICC shift)."""
    if h1 is None or h2 is None:
        return False
    r1, g1, b1 = int(h1[1:3],16), int(h1[3:5],16), int(h1[5:7],16)
    r2, g2, b2 = int(h2[1:3],16), int(h2[3:5],16), int(h2[5:7],16)
    return abs(r1-r2) <= tol and abs(g1-g2) <= tol and abs(b1-b2) <= tol


def analyze_pdf(pdf_path, label, targets=None):
    print(f"\n{'='*70}")
    print(f"  {label}: {Path(pdf_path).name}")
    print(f"{'='*70}")

    doc = fitz.open(pdf_path)
    page = doc[0]
    drawings = page.get_drawings()
    doc.close()

    print(f"\n  Key-Sampling (größter enthaltender Fill-Pfad):")
    print(f"  {'Key':12s}  {'Farbe (ICC-rendered)':12s}  {'Erwartung':12s}  Match")
    print(f"  {'-'*12}  {'-'*12}  {'-'*12}  -----")

    # Tigry-Farben → Key-Klassen sammeln
    tigry_color_to_keys = {}

    mismatches = []
    for key_name, (cx, cy) in KEY_CENTERS.items():
        color, area = get_color_at_point(drawings, cx, cy)
        target = targets.get(key_name, '?') if targets else '?'

        if color:
            tigry_color_to_keys.setdefault(color, []).append(key_name)

        match_str = ''
        if targets and target != '?':
            if color and hex_close(color, target):
                match_str = '✓'
            else:
                match_str = '✗'
                mismatches.append((key_name, color, target))

        print(f"  {key_name:12s}  {color or 'N/A':12s}  {target:12s}  {match_str}")

    return tigry_color_to_keys, mismatches


def main():
    base = Path(__file__).parent.parent / 'templates'
    tigry_path  = str(base / 'GK75-German-Tigry-original.pdf')
    omni_path   = str(base / 'GK75-TheWell-omni-mask_v1.pdf')

    print("TIGRY SLOT IDENTIFICATION — POINT SAMPLING")
    print(f"(Min-Area-Filter: 200px² — ignoriert kleine Outline-Pfade)")

    # === Tigry Original: kein Ziel-Vergleich, nur Mapping ===
    tigry_map, _ = analyze_pdf(tigry_path, "TIGRY ORIGINAL", targets=None)

    print(f"\n  TIGRY: Farbe → Tasten-Klasse")
    print(f"  {'Tigry-Hex':10s}  Tasten")
    print(f"  {'-'*10}  {'-'*50}")
    for color, keys in sorted(tigry_map.items()):
        print(f"  {color}  {', '.join(keys)}")

    # === Oni Mask v1: Vergleich gegen V2-Ziel ===
    omni_map, mismatches = analyze_pdf(omni_path, "ONI MASK v1 (Antons manuell)", targets=ONI_TARGETS)

    if mismatches:
        print(f"\n  MISMATCHES in omni-mask v1 ({len(mismatches)}):")
        for key, actual, target in mismatches:
            print(f"    {key}: hat {actual}, soll {target}")
    else:
        print(f"\n  ✓ Alle Keys stimmen mit V2-Ziel überein")

    # === SCHEME_ONI_MASK ableiten ===
    print(f"\n{'='*70}")
    print("  SCHEME_ONI_MASK MAPPING ABLEITUNG")
    print(f"{'='*70}")
    print()
    print("  Tigry-Farbe → Key-Typ → ONI-Ziel")
    print(f"  {'-'*60}")

    # Build Tigry-color → ONI-target via key lookup
    TEMPLATE_TIGRY_SLOTS = {
        '#F5F4EB': 'alpha',    '#F4F4EB': 'alpha',
        '#E4B57B': 'accent1',  '#E5B57C': 'accent1',
        '#EBB885': 'accent2',  '#ECB986': 'accent2',
        '#A4CEC3': 'accent3',  '#A5CEC3': 'accent3',
        '#8B8B8A': 'mod1',     '#8C8C8B': 'mod1',
        '#828486': 'mod2',     '#828487': 'mod2',
        '#6B6C6C': 'fkey',     '#6B6C6D': 'fkey',
        '#53555A': 'nav1',     '#54565A': 'nav1',
        '#4B4B4B': 'nav2',     '#4C4C4C': 'nav2',
        '#A4A4A4': 'arrows',   '#A5A5A5': 'arrows',
        '#AA1616': 'dolch_red','#AA1717': 'dolch_red',
    }

    slot_to_oni = {}
    slot_keys = {}  # slot → which keys use it

    for tigry_hex, keys in tigry_map.items():
        slot = TEMPLATE_TIGRY_SLOTS.get(tigry_hex)
        if not slot:
            print(f"  ??? {tigry_hex} — nicht in TEMPLATE_TIGRY_SLOTS: {keys}")
            continue

        # Bestimme ONI-Zielfarbe: Mehrheitsvotum der Keys
        votes = {}
        for k in keys:
            oni = ONI_TARGETS.get(k)
            if oni:
                votes[oni] = votes.get(oni, 0) + 1
        if votes:
            oni_target = max(votes, key=votes.get)
            slot_to_oni[slot] = oni_target
            slot_keys[slot] = keys
            print(f"  {tigry_hex} ({slot:10s}) → {oni_target}  [{', '.join(keys)}]")

    # Restliche Slots (nicht via Point-Sampling gefunden)
    ALL_SLOTS = ['alpha', 'accent1', 'accent2', 'accent3', 'mod1', 'mod2',
                 'fkey', 'nav1', 'nav2', 'arrows', 'dolch_red']

    missing = [s for s in ALL_SLOTS if s not in slot_to_oni]
    if missing:
        print(f"\n  NICHT VERIFIZIERT (kein Sampling-Treffer):")
        for s in missing:
            print(f"    {s} → ??? (manual inspection needed)")

    print(f"\n  {'='*60}")
    print("  SCHEME_ONI_MASK['mapping'] (verifiziert):")
    print()
    print('  SCHEME_ONI_MASK = {')
    print('      "name": "Oni Mask — 鬼",')
    print('      "description": "Schwarz-Rot-Gold Samurai. Ideogram V2 K-Means. Verifiziert via PDF-Stream-Analyse.",')
    print('      "mapping": {')
    for slot in ALL_SLOTS:
        oni = slot_to_oni.get(slot, '???')
        note = ''
        if slot in slot_keys:
            keys_sample = slot_keys[slot][:4]
            note = f'  # {", ".join(keys_sample)}'
        print(f'          "{slot}": "{oni}",{note}')
    print('      },')
    print('      "legend_colors": {')
    print('          # Legends werden per PyMuPDF overdraw gemacht, nicht per recolor_template')
    print('          "on_dark":     "#A88B63",  # Gold auf Schwarz')
    print('          "on_red":      "#DDC096",  # Champagner auf Rot')
    print('          "on_gold":     "#1B1D20",  # Schwarz auf Gold')
    print('          "sub":         "#7A6444",  # Gedämpftes Gold')
    print('      },')
    print('  }')


if __name__ == "__main__":
    main()
