#!/usr/bin/env python3
"""
Oni Mask Audit Script
=====================
Analysiert GK75-German-Tigry-original.pdf und GK75-TheWell-omni-mask_v1.pdf
via PDF-Stream-Analyse (pikepdf + PyMuPDF).

Ziel:
  1. Alle Fill-Farben aus beiden PDFs extrahieren (RGB + CMYK)
  2. Bounding-Boxes via PyMuPDF get_drawings() erfassen
  3. Farben auf GK75-Key-Zonen mappen (F-Keys, Alphas, Mods, Spacebar, Pfeile etc.)
  4. Vergleich: Aktuelle Oni-Mask-Farben vs. Ziel-Palette V2

Output:
  - Tabelle: Slot | Aktuelle Farbe | Ziel-Farbe | Match?
  - Slot-Mapping: Tigry-Hex → Key-Klasse
"""

import io
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pathlib import Path
import pikepdf

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

# =============================================================================
# GK75 Key Zone Definitions (PyMuPDF coordinates: y=0 top-left)
# =============================================================================
# Format: name -> (x0, y0, x1, y1) — tolerances included
# From CLAUDE.md + empirische Messungen

KEY_ZONES = {
    # F-Key Zeile (y: 252–312)
    'esc':         (100, 240, 200, 320),
    'f1_f12':      (200, 240, 840, 320),
    # Zahlenzeile (y: 325–378)
    'num_row':     (100, 315, 840, 390),
    'backspace':   (820, 315, 960, 390),
    'entf':        (945, 315, 1030, 390),
    # Tab-Zeile (y: 380–432)
    'tab_row':     (100, 375, 840, 445),
    'tab':         (100, 375, 210, 445),
    'pgup':        (945, 375, 1030, 445),
    # CapsLk-Zeile (y: 435–487)
    'caps_row':    (100, 430, 840, 500),
    'caps':        (100, 430, 225, 500),
    'pgdn':        (945, 430, 1030, 500),
    # Shift-Zeile (y: 491–543)
    'shift_row':   (100, 480, 840, 555),
    'lshift':      (100, 480, 200, 555),
    'rshift':      (780, 480, 900, 555),
    # Bottom-Zeile (y: 545–597)
    'lctrl':       (100, 535, 200, 610),
    'win':         (185, 535, 265, 610),
    'lalt':        (250, 535, 340, 610),
    'spacebar':    (340, 535, 675, 610),
    'ralt':        (660, 535, 735, 610),
    'fn':          (720, 535, 790, 610),
    'rctrl':       (785, 535, 840, 610),
    # Pfeile (rechts von Bottom, y~560-590)
    'arrows':      (840, 490, 960, 615),
    # Nav-Spalte (x: 945–1030, y: 155–500 je nach Zeile)
    'nav_top':     (945, 150, 1030, 240),   # Rotary/POS1
    # Enter (in Tab-Row-Zeile, rechts)
    'enter':       (800, 375, 840, 500),    # approximate Enter position
}

# =============================================================================
# Ziel-Palette V2 (aus Brain DB ADR)
# =============================================================================
TARGET_V2 = {
    'alpha_bg':    '#1B1D20',  # Alphas (Q,W,E...), Zahlenreihe
    'fkey_bg':     '#2A2D32',  # F1-F12
    'mod_bg':      '#6F2D2C',  # Tab, Caps, Shift, Ctrl, Win, Alt, Fn, AltGr, Backspace
    'accent_bg':   '#A88B63',  # Esc, Enter, Spacebar, Pfeile
    'highlight':   '#DDC096',  # Helleres Champagner (optional)
    'body':        '#1B2230',  # Marineblau (zwischen Tasten)
    'legend_blk':  '#A88B63',  # Legend auf Schwarz
    'legend_red':  '#DDC096',  # Legend auf Rot
    'legend_gold': '#1B1D20',  # Legend auf Gold
    'sub_legend':  '#7A6444',  # Sub-Legends
}

# =============================================================================
# Raw-Color extraction via pikepdf (RGB rg operator)
# =============================================================================

def extract_rgb_colors_pikepdf(pdf_path):
    """Extrahiert alle RGB fill colors aus PDF-Streams via pikepdf."""
    pdf = pikepdf.open(pdf_path)
    colors = {}  # hex -> count

    for page in pdf.pages:
        streams = []
        if '/Contents' in page:
            contents = page['/Contents']
            streams.extend(list(contents) if isinstance(contents, pikepdf.Array) else [contents])
        if '/Resources' in page and '/XObject' in page['/Resources']:
            for name, xobj in page['/Resources']['/XObject'].items():
                streams.append(xobj)

        for s in streams:
            try:
                data = s.read_bytes().decode('latin-1')
                for m in re.finditer(r'([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+rg\b', data):
                    r, g, b = float(m.group(1)), float(m.group(2)), float(m.group(3))
                    hex_c = f"#{int(round(r*255)):02X}{int(round(g*255)):02X}{int(round(b*255)):02X}"
                    colors[hex_c] = colors.get(hex_c, 0) + 1
            except Exception:
                pass

    pdf.close()
    return colors


def extract_cmyk_colors_pikepdf(pdf_path):
    """Extrahiert alle CMYK fill colors aus PDF-Streams via pikepdf."""
    pdf = pikepdf.open(pdf_path)
    colors = {}  # (c,m,y,k) -> count

    for page in pdf.pages:
        streams = []
        if '/Contents' in page:
            contents = page['/Contents']
            streams.extend(list(contents) if isinstance(contents, pikepdf.Array) else [contents])
        if '/Resources' in page and '/XObject' in page['/Resources']:
            for name, xobj in page['/Resources']['/XObject'].items():
                streams.append(xobj)

        for s in streams:
            try:
                data = s.read_bytes().decode('latin-1')
                # CMYK fill operator: c m y k k (4 components + 'k')
                for m in re.finditer(r'([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+k\b', data):
                    c, m2, y, k = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))
                    key = (round(c,3), round(m2,3), round(y,3), round(k,3))
                    colors[key] = colors.get(key, 0) + 1
            except Exception:
                pass

    pdf.close()
    return colors


def cmyk_to_hex_approx(c, m, y, k):
    """Approximate CMYK to RGB hex (no ICC profile)."""
    r = 255 * (1-c) * (1-k)
    g = 255 * (1-m) * (1-k)
    b = 255 * (1-y) * (1-k)
    return f"#{int(round(r)):02X}{int(round(g)):02X}{int(round(b)):02X}"


# =============================================================================
# Position-based analysis via PyMuPDF
# =============================================================================

def analyze_drawings_by_zone(pdf_path):
    """
    Verwendet PyMuPDF get_drawings() um Farben + Positionen zu extrahieren.
    Gruppiert nach Key-Zonen.
    Returns: {zone_name: {hex_color: count}}
    """
    if fitz is None:
        print("PyMuPDF nicht verfügbar — überspringe Positions-Analyse")
        return {}

    doc = fitz.open(pdf_path)
    page = doc[0]
    drawings = page.get_drawings()
    doc.close()

    # Fill-Farben mit Bounding Boxes
    fills_with_rects = []
    for d in drawings:
        if d.get('fill') is not None:
            r_val, g_val, b_val = d['fill'][0], d['fill'][1], d['fill'][2]
            hex_c = f"#{int(round(r_val*255)):02X}{int(round(g_val*255)):02X}{int(round(b_val*255)):02X}"
            rect = d['rect']
            fills_with_rects.append((hex_c, rect, d['rect'].get_area() if hasattr(d['rect'], 'get_area') else (rect.x1-rect.x0)*(rect.y1-rect.y0)))

    # Zone-Zuordnung
    zone_fills = {z: {} for z in KEY_ZONES}
    unclassified = {}

    def rect_in_zone(rect, zone):
        x0z, y0z, x1z, y1z = KEY_ZONES[zone]
        cx = (rect.x0 + rect.x1) / 2
        cy = (rect.y0 + rect.y1) / 2
        return x0z <= cx <= x1z and y0z <= cy <= y1z

    for hex_c, rect, area in fills_with_rects:
        if area < 5:  # Ignore tiny paths (outline artifacts)
            continue
        matched = False
        for zone in KEY_ZONES:
            if rect_in_zone(rect, zone):
                zone_fills[zone][hex_c] = zone_fills[zone].get(hex_c, 0) + 1
                matched = True
                break
        if not matched:
            unclassified[hex_c] = unclassified.get(hex_c, 0) + 1

    return zone_fills, unclassified, fills_with_rects


def dominant_color_per_zone(zone_fills):
    """Gibt die dominante Fill-Farbe pro Zone zurück (häufigste)."""
    result = {}
    for zone, colors in zone_fills.items():
        if colors:
            dominant = max(colors, key=lambda c: colors[c])
            result[zone] = dominant
    return result


# =============================================================================
# Main Audit
# =============================================================================

def hex_close(h1, h2, tol=20):
    """Prüft ob zwei Hex-Farben innerhalb Toleranz liegen (CMYK ICC shift)."""
    r1, g1, b1 = int(h1[1:3],16), int(h1[3:5],16), int(h1[5:7],16)
    r2, g2, b2 = int(h2[1:3],16), int(h2[3:5],16), int(h2[5:7],16)
    return abs(r1-r2) <= tol and abs(g1-g2) <= tol and abs(b1-b2) <= tol


def print_separator(char='-', width=80):
    print(char * width)


def run_audit():
    base = Path(__file__).parent.parent / 'templates'
    tigry_path = base / 'GK75-German-Tigry-original.pdf'
    omni_path  = base / 'GK75-TheWell-omni-mask_v1.pdf'

    print("=" * 80)
    print("ONI MASK AUDIT — PDF STREAM ANALYSE")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # 1. Tigry Original — RGB + CMYK fills
    # -------------------------------------------------------------------------
    print(f"\n[1] TIGRY ORIGINAL: {tigry_path.name}")
    print_separator()

    tigry_rgb  = extract_rgb_colors_pikepdf(tigry_path)
    tigry_cmyk = extract_cmyk_colors_pikepdf(tigry_path)

    if tigry_rgb:
        print(f"\n  RGB fills ({len(tigry_rgb)} unique):")
        for hex_c, count in sorted(tigry_rgb.items(), key=lambda x: -x[1]):
            print(f"    {hex_c}  ({count}×)")
    else:
        print("  → Keine RGB fills gefunden")

    if tigry_cmyk:
        print(f"\n  CMYK fills ({len(tigry_cmyk)} unique):")
        for (c,m,y,k), count in sorted(tigry_cmyk.items(), key=lambda x: -x[1]):
            approx_hex = cmyk_to_hex_approx(c, m, y, k)
            print(f"    C={c:.3f} M={m:.3f} Y={y:.3f} K={k:.3f}  ≈{approx_hex}  ({count}×)")
    else:
        print("  → Keine CMYK fills gefunden")

    # -------------------------------------------------------------------------
    # 2. Tigry — Positions-Analyse
    # -------------------------------------------------------------------------
    print(f"\n[2] TIGRY POSITIONEN (PyMuPDF Zone-Mapping):")
    print_separator()

    if fitz is not None:
        tigry_zones, tigry_unclass, tigry_all = analyze_drawings_by_zone(tigry_path)
        tigry_dominant = dominant_color_per_zone(tigry_zones)

        print(f"\n  Dominante Fill-Farbe pro Zone:")
        for zone, color in sorted(tigry_dominant.items()):
            print(f"    {zone:15s} → {color}")

        if tigry_unclass:
            print(f"\n  Unklassifiziert (kein Zone-Match):")
            for hex_c, count in sorted(tigry_unclass.items(), key=lambda x: -x[1])[:10]:
                print(f"    {hex_c}  ({count}×)")

        # Tigry-Slot-Tabelle: Farbe → welche Zonen haben diese Farbe?
        color_to_zones = {}
        for zone, color in tigry_dominant.items():
            if color not in color_to_zones:
                color_to_zones[color] = []
            color_to_zones[color].append(zone)

        print(f"\n  Tigry-Farbe → Zonen (konsolidiert):")
        print_separator('-')
        print(f"  {'Hex':8s}  Zonen")
        print_separator('-')
        for color, zones in sorted(color_to_zones.items()):
            print(f"  {color}  {', '.join(zones)}")

    else:
        print("  PyMuPDF nicht verfügbar — bitte installieren: pip install pymupdf")
        tigry_dominant = {}
        tigry_unclass = {}

    # -------------------------------------------------------------------------
    # 3. Oni Mask v1 — RGB + CMYK fills
    # -------------------------------------------------------------------------
    print(f"\n[3] ONI MASK v1 (Antons manuell): {omni_path.name}")
    print_separator()

    omni_rgb  = extract_rgb_colors_pikepdf(omni_path)
    omni_cmyk = extract_cmyk_colors_pikepdf(omni_path)

    if omni_rgb:
        print(f"\n  RGB fills ({len(omni_rgb)} unique):")
        for hex_c, count in sorted(omni_rgb.items(), key=lambda x: -x[1]):
            print(f"    {hex_c}  ({count}×)")
    else:
        print("  → Keine RGB fills gefunden")

    if omni_cmyk:
        print(f"\n  CMYK fills ({len(omni_cmyk)} unique):")
        for (c,m,y,k), count in sorted(omni_cmyk.items(), key=lambda x: -x[1]):
            approx_hex = cmyk_to_hex_approx(c, m, y, k)
            print(f"    C={c:.3f} M={m:.3f} Y={y:.3f} K={k:.3f}  ≈{approx_hex}  ({count}×)")
    else:
        print("  → Keine CMYK fills gefunden")

    # -------------------------------------------------------------------------
    # 4. Oni Mask v1 — Positionen
    # -------------------------------------------------------------------------
    print(f"\n[4] ONI MASK v1 POSITIONEN:")
    print_separator()

    if fitz is not None:
        omni_zones, omni_unclass, omni_all = analyze_drawings_by_zone(omni_path)
        omni_dominant = dominant_color_per_zone(omni_zones)

        print(f"\n  Dominante Fill-Farbe pro Zone:")
        for zone, color in sorted(omni_dominant.items()):
            print(f"    {zone:15s} → {color}")

    # -------------------------------------------------------------------------
    # 5. Vergleich: Oni Mask v1 vs. Ziel-Palette V2
    # -------------------------------------------------------------------------
    print(f"\n[5] VERGLEICH: Oni Mask v1 vs. Ziel-Palette V2")
    print_separator()

    # Erwartetes Zone→Target Mapping (aus ADR V2)
    ZONE_TARGET = {
        'esc':         TARGET_V2['accent_bg'],   # #A88B63 Gold
        'f1_f12':      TARGET_V2['fkey_bg'],     # #2A2D32
        'num_row':     TARGET_V2['alpha_bg'],    # #1B1D20
        'backspace':   TARGET_V2['mod_bg'],      # #6F2D2C
        'entf':        TARGET_V2['fkey_bg'],     # #2A2D32 (Nav-Legende)
        'tab':         TARGET_V2['mod_bg'],      # #6F2D2C
        'tab_row':     TARGET_V2['alpha_bg'],    # #1B1D20 (Buchstaben)
        'pgup':        TARGET_V2['mod_bg'],      # #6F2D2C
        'caps':        TARGET_V2['mod_bg'],      # #6F2D2C
        'caps_row':    TARGET_V2['alpha_bg'],    # #1B1D20
        'pgdn':        TARGET_V2['mod_bg'],      # #6F2D2C
        'lshift':      TARGET_V2['mod_bg'],      # #6F2D2C
        'shift_row':   TARGET_V2['alpha_bg'],    # #1B1D20 (ISO-DE extra key)
        'rshift':      TARGET_V2['mod_bg'],      # #6F2D2C
        'lctrl':       TARGET_V2['mod_bg'],      # #6F2D2C
        'win':         TARGET_V2['mod_bg'],      # #6F2D2C
        'lalt':        TARGET_V2['mod_bg'],      # #6F2D2C
        'spacebar':    TARGET_V2['accent_bg'],   # #A88B63 Gold
        'ralt':        TARGET_V2['mod_bg'],      # #6F2D2C
        'fn':          TARGET_V2['mod_bg'],      # #6F2D2C
        'rctrl':       TARGET_V2['mod_bg'],      # #6F2D2C
        'arrows':      TARGET_V2['accent_bg'],   # #A88B63 Gold
        'enter':       TARGET_V2['accent_bg'],   # #A88B63 Gold
        'nav_top':     TARGET_V2['mod_bg'],      # #6F2D2C
    }

    if fitz is not None:
        print(f"\n  {'Zone':15s}  {'Ist (omni_v1)':10s}  {'Soll (V2)':10s}  Match?")
        print_separator('-')
        mismatches = []
        for zone, target in sorted(ZONE_TARGET.items()):
            actual = omni_dominant.get(zone, 'N/A')
            match = '✓' if actual != 'N/A' and hex_close(actual, target, tol=30) else '✗'
            if match == '✗':
                mismatches.append((zone, actual, target))
            print(f"  {zone:15s}  {actual:10s}  {target:10s}  {match}")

        if mismatches:
            print(f"\n  MISMATCHES ({len(mismatches)}):")
            for zone, actual, target in mismatches:
                print(f"    {zone}: hat {actual}, erwartet {target}")
        else:
            print(f"\n  → Alle Zonen stimmen überein! (tol=30)")

    # -------------------------------------------------------------------------
    # 6. Empfohlenes SCHEME_ONI_MASK Mapping
    # -------------------------------------------------------------------------
    print(f"\n[6] EMPFOHLENES TIGRY→ONI MAPPING (aus Tigry-Zone-Analyse)")
    print_separator()
    print("  Basiert auf: Tigry-Zone-Mapping × Oni-Ziel-Palette V2")
    print()

    # Tigry-Farbe → Key-Klasse (aus Zone-Analyse)
    TIGRY_SLOT_NAMES = {
        'esc':         'accent (Esc)',
        'f1_f12':      'fkey',
        'num_row':     'alpha (Zahlenreihe)',
        'backspace':   'mod (Backspace)',
        'tab':         'mod (Tab)',
        'tab_row':     'alpha (Buchstaben)',
        'enter':       'accent (Enter)',
        'caps':        'mod (CapsLk)',
        'caps_row':    'alpha (Buchstaben)',
        'lshift':      'mod (Shift)',
        'rshift':      'mod (Shift)',
        'lctrl':       'mod (Ctrl)',
        'win':         'mod (Win)',
        'lalt':        'mod (Alt)',
        'spacebar':    'accent (Spacebar)',
        'ralt':        'mod (AltGr)',
        'fn':          'mod (Fn)',
        'arrows':      'accent (Pfeile)',
        'nav_top':     'nav (POS1)',
        'pgup':        'nav (PgUp)',
        'pgdn':        'nav (PgDn)',
        'entf':        'fkey (Entf)',
    }

    if fitz is not None and tigry_dominant:
        # Build Tigry-color → expected Oni color mapping
        seen_tigry = {}
        for zone, tigry_color in sorted(tigry_dominant.items()):
            if zone in ZONE_TARGET:
                oni_target = ZONE_TARGET[zone]
                slot_name = TIGRY_SLOT_NAMES.get(zone, zone)
                if tigry_color not in seen_tigry:
                    seen_tigry[tigry_color] = (oni_target, slot_name)
                    print(f"  Tigry {tigry_color} ({slot_name}) → ONI {oni_target}")

        print(f"\n  Python-Dict für SCHEME_ONI_MASK['mapping']:")
        print()

        # Group Tigry slots by oni target
        tigry_to_oni = {}
        for zone, tigry_color in tigry_dominant.items():
            if zone in ZONE_TARGET:
                oni_target = ZONE_TARGET[zone]
                tigry_to_oni[tigry_color] = oni_target

        # Map back to TEMPLATE_TIGRY slot names
        # (Tigry_hex → which TEMPLATE_TIGRY key?)
        # We need to identify which TEMPLATE_TIGRY slot name corresponds to which hex
        # TEMPLATE_TIGRY values: alpha=#F5F4EB, accent1=#E4B57B, accent2=#EBB885,
        #   accent3=#A4CEC3, mod1=#8B8B8A, mod2=#828486, fkey=#6B6C6C,
        #   nav1=#53555A, nav2=#4B4B4B, arrows=#A4A4A4, dolch_red=#AA1616

        TEMPLATE_TIGRY_HEX = {
            '#F5F4EB': 'alpha',
            '#F4F4EB': 'alpha',  # slight variant
            '#E4B57B': 'accent1',
            '#E5B57C': 'accent1',
            '#EBB885': 'accent2',
            '#ECB986': 'accent2',
            '#A4CEC3': 'accent3',
            '#A5CEC3': 'accent3',
            '#8B8B8A': 'mod1',
            '#8C8C8B': 'mod1',
            '#828486': 'mod2',
            '#828487': 'mod2',
            '#6B6C6C': 'fkey',
            '#6B6C6D': 'fkey',
            '#53555A': 'nav1',
            '#54565A': 'nav1',
            '#4B4B4B': 'nav2',
            '#4C4C4C': 'nav2',
            '#A4A4A4': 'arrows',
            '#A5A5A5': 'arrows',
            '#AA1616': 'dolch_red',
            '#AA1717': 'dolch_red',
        }

        # Build final mapping: TEMPLATE_TIGRY slot → Oni target hex
        slot_to_oni = {}
        for tigry_hex, oni_hex in tigry_to_oni.items():
            slot = TEMPLATE_TIGRY_HEX.get(tigry_hex)
            if slot:
                slot_to_oni[slot] = oni_hex

        # Print Python code
        print("  SCHEME_ONI_MASK = {")
        print('      "name": "Oni Mask — 鬼",')
        print('      "description": "Schwarz-Rot-Gold Samurai. Basiert auf Ideogram V2 K-Means Analyse.",')
        print('      "mapping": {')

        # All slots in order
        all_slots = ['alpha', 'accent1', 'accent2', 'accent3', 'mod1', 'mod2', 'fkey', 'nav1', 'nav2', 'arrows', 'dolch_red']
        for slot in all_slots:
            oni_hex = slot_to_oni.get(slot, '???')
            print(f'          "{slot}": "{oni_hex}",')

        print('      },')
        print('  }')

    print()
    print("=" * 80)
    print("AUDIT ABGESCHLOSSEN")
    print("=" * 80)


if __name__ == "__main__":
    run_audit()
