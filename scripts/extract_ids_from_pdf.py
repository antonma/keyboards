"""
extract_ids_from_pdf.py — Coord-Map aus Antons-template-with-ids.pdf

Liest Key-IDs aus der Affinity-Ebene "key_ids" (Text-Objekte),
matcht sie zu Keycap-Fill-Drawings und schreibt layouts/iso-de-75-anton-coordinate-map.json.
"""

import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import fitz  # PyMuPDF

# ── Konfiguration ─────────────────────────────────────────────────────────────

INPUT_PDF = "templates/Antons-template-with-ids.pdf"
OUTPUT_JSON = "layouts/iso-de-75-anton-coordinate-map.json"

# Soll-Liste 84 Key-IDs (nach Handoff-Spec; count korrigiert auf 84)
EXPECTED_IDS = {
    # fn_row
    "esc", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12",
    # numbers row
    "grave", "num_1", "num_2", "num_3", "num_4", "num_5", "num_6",
    "num_7", "num_8", "num_9", "num_0", "ss", "dead_ac", "bksp",
    # QWERTZ row
    "tab", "q", "w", "e", "r", "t", "z", "u", "i", "o", "p", "ue", "plus", "enter_top",
    # ASDF row
    "caps", "a", "s", "d", "f", "g", "h", "j", "k", "l", "oe", "ae", "hash", "enter_bot",
    # YXCV row
    "lshift", "less", "y", "x", "c", "v", "b", "n", "m", "comma", "period", "dash", "rshift",
    # Spacebar row
    "lctrl", "lwin", "lalt", "space", "ralt", "fn", "rctrl",
    # Nav
    "del", "home", "pgup", "pgdn", "end",
    # Arrows
    "up", "down", "left", "right",
}

# Gruppen-Zuordnung
GROUP_MAP = {
    "esc": "fn_row",
    **{f"f{i}": "fn_row" for i in range(1, 13)},
    "grave": "numbers", "num_1": "numbers", "num_2": "numbers", "num_3": "numbers",
    "num_4": "numbers", "num_5": "numbers", "num_6": "numbers", "num_7": "numbers",
    "num_8": "numbers", "num_9": "numbers", "num_0": "numbers",
    "ss": "numbers", "dead_ac": "numbers", "bksp": "primary_mods",
    "tab": "primary_mods", "caps": "primary_mods",
    "enter_top": "primary_mods", "enter_bot": "primary_mods",
    "lshift": "shifts", "rshift": "shifts",
    "lctrl": "mods_left", "lwin": "mods_left", "lalt": "mods_left",
    "ralt": "mods_right", "fn": "mods_right", "rctrl": "mods_right",
    "space": "spacebar",
    "del": "nav", "home": "nav", "pgup": "nav", "pgdn": "nav", "end": "nav",
    "up": "arrows", "down": "arrows", "left": "arrows", "right": "arrows",
}
# Alle anderen → alphas
ALPHA_IDS = {
    "q", "w", "e", "r", "t", "z", "u", "i", "o", "p", "ue", "plus",
    "a", "s", "d", "f", "g", "h", "j", "k", "l", "oe", "ae", "hash",
    "less", "y", "x", "c", "v", "b", "n", "m", "comma", "period", "dash",
}
for aid in ALPHA_IDS:
    GROUP_MAP[aid] = "alphas"

# Display-Namen
NAME_MAP = {
    "esc": "ESC", "f1": "F1", "f2": "F2", "f3": "F3", "f4": "F4",
    "f5": "F5", "f6": "F6", "f7": "F7", "f8": "F8", "f9": "F9",
    "f10": "F10", "f11": "F11", "f12": "F12",
    "grave": "`", "num_1": "1", "num_2": "2", "num_3": "3", "num_4": "4",
    "num_5": "5", "num_6": "6", "num_7": "7", "num_8": "8", "num_9": "9",
    "num_0": "0", "ss": "ß", "dead_ac": "´", "bksp": "Backspace",
    "tab": "Tab", "q": "Q", "w": "W", "e": "E", "r": "R", "t": "T",
    "z": "Z", "u": "U", "i": "I", "o": "O", "p": "P", "ue": "Ü",
    "plus": "+", "enter_top": "Enter (top)",
    "caps": "Caps Lock", "a": "A", "s": "S", "d": "D", "f": "F",
    "g": "G", "h": "H", "j": "J", "k": "K", "l": "L",
    "oe": "Ö", "ae": "Ä", "hash": "#", "enter_bot": "Enter (bot)",
    "lshift": "Shift L", "less": "<", "y": "Y", "x": "X", "c": "C",
    "v": "V", "b": "B", "n": "N", "m": "M", "comma": ",",
    "period": ".", "dash": "-", "rshift": "Shift R",
    "lctrl": "Ctrl L", "lwin": "Win", "lalt": "Alt L",
    "space": "Space", "ralt": "AltGr", "fn": "Fn", "rctrl": "Ctrl R",
    "del": "Del", "home": "Home", "pgup": "PgUp", "pgdn": "PgDn", "end": "End",
    "up": "↑", "down": "↓", "left": "←", "right": "→",
}

# ── Extraction ────────────────────────────────────────────────────────────────

def extract(pdf_path: str) -> dict:
    doc = fitz.open(pdf_path)
    page = doc[0]
    page_rect = page.rect

    # 1. Text-Objekte einlesen (Key-IDs)
    texts = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                txt = span["text"].strip()
                if not txt or txt == "75% ISO DE Layout":
                    continue
                bbox = span["bbox"]
                cx = (bbox[0] + bbox[2]) / 2
                cy = (bbox[1] + bbox[3]) / 2
                texts.append((txt, cx, cy))

    # 2. Filled Drawings einlesen (Keycap-Bodies)
    fills = []
    for d in page.get_drawings():
        if d.get("fill"):
            r = d["rect"]
            fills.append((r.x0, r.y0, r.x1, r.y1, r.width * r.height))

    # 3. Matching: Text-Mittelpunkt → größter enthaltender Fill
    #    Fallback bei Kollision (mehrere Texte → selbe Fill): nearest-center
    import math

    def fill_center(x0, y0, x1, y1):
        return (x0 + x1) / 2, (y0 + y1) / 2

    def dist(cx, cy, x0, y0, x1, y1):
        fcx, fcy = fill_center(x0, y0, x1, y1)
        return math.hypot(cx - fcx, cy - fcy)

    # First pass: largest-containing-fill for each text
    candidates = {}  # txt -> (area, x0, y0, x1, y1)
    for txt, cx, cy in texts:
        containing = [
            (area, x0, y0, x1, y1)
            for x0, y0, x1, y1, area in fills
            if x0 <= cx <= x1 and y0 <= cy <= y1
        ]
        if containing:
            containing.sort(key=lambda x: x[0], reverse=True)
            candidates[txt] = containing[0]  # (area, x0, y0, x1, y1)

    # Detect collisions: multiple texts mapping to the same fill bbox
    fill_to_texts = {}
    for txt, (area, x0, y0, x1, y1) in candidates.items():
        key = (x0, y0, x1, y1)
        fill_to_texts.setdefault(key, []).append(txt)

    text_pos = {txt: (cx, cy) for txt, cx, cy in texts}
    matched = {}
    used_fills = set()  # (x0,y0,x1,y1) already claimed

    # Resolve non-colliding texts first
    for fill_key, txts in fill_to_texts.items():
        if len(txts) == 1:
            matched[txts[0]] = fill_key
            used_fills.add(fill_key)

    # Resolve collisions: closest text to fill-center keeps the fill; others reassign
    for fill_key, txts in fill_to_texts.items():
        if len(txts) <= 1:
            continue
        # ISO-Enter special case: enter_top + enter_bot share one L-shape fill → OK
        if set(txts) == {"enter_top", "enter_bot"}:
            matched["enter_top"] = fill_key
            matched["enter_bot"] = fill_key
            used_fills.add(fill_key)
            continue
        # Sort by distance to fill center; closest keeps the fill
        x0f, y0f, x1f, y1f = fill_key
        ranked = sorted(txts, key=lambda t: dist(text_pos[t][0], text_pos[t][1], x0f, y0f, x1f, y1f))
        winner = ranked[0]
        matched[winner] = fill_key
        used_fills.add(fill_key)
        # Reassign losers to nearest unused fill
        for txt in ranked[1:]:
            cx, cy = text_pos[txt]
            candidates_all = sorted(
                [(area, x0, y0, x1, y1)
                 for x0, y0, x1, y1, area in fills
                 if area > 500 and (x0, y0, x1, y1) not in used_fills],
                key=lambda f: dist(cx, cy, f[1], f[2], f[3], f[4])
            )
            if candidates_all:
                area, x0, y0, x1, y1 = candidates_all[0]
                fk = (x0, y0, x1, y1)
                matched[txt] = fk
                used_fills.add(fk)
                print(f"  [COLLISION] {txt!r}: text at ({cx:.0f},{cy:.0f}) → nearest fill ({x0:.0f},{y0:.0f},{x1:.0f},{y1:.0f})", file=sys.stderr)
            else:
                print(f"  [WARN] No fill for: {txt!r} at ({cx:.0f},{cy:.0f})", file=sys.stderr)

    # 4. Validierung
    found_ids = set(matched.keys())
    unexpected = found_ids - EXPECTED_IDS
    missing = EXPECTED_IDS - found_ids
    duplicates = [t for t in texts if texts.count(t) > 1]  # simple check

    print("── Validierungsreport ──────────────────────────────")
    print(f"  Gefunden:    {len(found_ids)}")
    print(f"  Erwartet:    {len(EXPECTED_IDS)}")
    print(f"  Fehlend:     {sorted(missing) if missing else 'keine'}")
    print(f"  Unerwartete: {sorted(unexpected) if unexpected else 'keine'}")
    print(f"  Duplicates:  {duplicates if duplicates else 'keine'}")

    # ISO-Enter
    if "enter_top" in found_ids and "enter_bot" in found_ids:
        print("  ISO-Enter: enter_top + enter_bot erkannt ✓")

    # 5. Unit-Pixel aus 1u-Alpha-Keys berechnen
    alpha_1u_keys = ["q", "w", "e", "r", "t", "z", "u", "i", "o", "p",
                     "a", "s", "d", "f", "g", "h", "j", "k", "l",
                     "y", "x", "c", "v", "b", "n", "m"]
    widths = [matched[k][2] - matched[k][0] for k in alpha_1u_keys if k in matched]
    unit_px = round(sum(widths) / len(widths), 1) if widths else 53.0

    # 6. Keys bauen und nach Position sortieren
    keys = []
    for kid, (x0, y0, x1, y1) in matched.items():
        w = round(x1 - x0, 1)
        h = round(y1 - y0, 1)
        keys.append({
            "id": kid,
            "name": NAME_MAP.get(kid, kid),
            "group": GROUP_MAP.get(kid, "alphas"),
            "x0": round(x0, 1),
            "y0": round(y0, 1),
            "x1": round(x1, 1),
            "y1": round(y1, 1),
            "cx": round((x0 + x1) / 2, 1),
            "cy": round((y0 + y1) / 2, 1),
            "width": w,
            "height": h,
            "width_u": round(w / unit_px, 2),
        })

    # Sortierung: Zeile (y0-Bucket à 20px) dann x0
    keys.sort(key=lambda k: (round(k["y0"] / 20) * 20, k["x0"]))

    return {
        "keyboard": "75-iso-de",
        "layout": "75-iso-de",
        "source_pdf": "templates/Antons-template-with-ids.pdf",
        "page_width": round(page_rect.width, 1),
        "page_height": round(page_rect.height, 1),
        "unit_px": unit_px,
        "note": "Key-IDs aus Affinity key_ids-Ebene in Antons-template-with-ids.pdf extrahiert",
        "key_count": len(keys),
        "keys": keys,
    }


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    result = extract(INPUT_PDF)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\nCoord-Map geschrieben: {OUTPUT_JSON}")
    print(f"  Keys: {result['key_count']}")
    print(f"  unit_px: {result['unit_px']}")
    print(f"  Seite: {result['page_width']}×{result['page_height']}")
