"""extract_cherry_coords.py — Extract key bounding boxes from Cherry 135 全五面 PDF

Extracts all fill paths with h≥45pt and w≥45pt (= individual keycap bodies),
clusters them into rows by Y-position, sorts each row by X, then assigns
ISO-DE key IDs and groups using a positional mapping table.

Output: layouts/cherry-135-coordinate-map.json

Usage:
    py -3 scripts/extract_cherry_coords.py
    py -3 scripts/extract_cherry_coords.py --analyze   (print stats, no write)
    py -3 scripts/extract_cherry_coords.py --pdf "templates/135 Cherry 全五面.pdf"
"""

import argparse
import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent
DEFAULT_PDF = REPO / "templates" / "135 Cherry 全五面.pdf"
OUTPUT_MAP  = REPO / "layouts" / "cherry-135-coordinate-map.json"

MIN_KEY_W = 45.0
MIN_KEY_H = 45.0
ROW_CLUSTER_TOL = 20.0   # fills within 20pt Y are in the same row
MAIN_AREA_MAX_Y = 520.0  # top-view keys; fills below this are side/extra views


# ── ISO-DE full keyboard layout table ─────────────────────────────────────────
#
# Each sub-list maps positional index (sorted by X within a row) to
# (key_id, group). Count must match the actual extracted fills per row.
#
# Layout assumes full ISO-DE with separate numpad columns aligned to main rows.
# Groups: alpha, mod, fkey, nav, num, spacebar

ROW_LAYOUTS = [
    # Row 1 (16): ESC F1-F12 PrtSc ScrollLk Pause
    [
        ("esc",      "fkey"), ("f1",     "fkey"), ("f2",  "fkey"), ("f3",  "fkey"),
        ("f4",       "fkey"), ("f5",     "fkey"), ("f6",  "fkey"), ("f7",  "fkey"),
        ("f8",       "fkey"), ("f9",     "fkey"), ("f10", "fkey"), ("f11", "fkey"),
        ("f12",      "fkey"), ("prtsc",  "nav"),  ("scr", "nav"),  ("pause","nav"),
    ],
    # Row 2 (21): ^ 1-0 ß dead_´ Bksp(2u) | Ins Home PgUp | NumLk / * -
    [
        ("grave",    "alpha"), ("1",    "alpha"), ("2",    "alpha"), ("3",    "alpha"),
        ("4",        "alpha"), ("5",    "alpha"), ("6",    "alpha"), ("7",    "alpha"),
        ("8",        "alpha"), ("9",    "alpha"), ("0",    "alpha"), ("ss",   "alpha"),
        ("dead_ac",  "alpha"), ("bksp", "mod"),
        ("ins",      "nav"),   ("home", "nav"),   ("pgup", "nav"),
        ("numlk",    "num"),   ("num_div","num"),  ("num_mul","num"), ("num_sub","num"),
    ],
    # Row 3 (20): Tab(1.5u) Q-Ü +(QWERTY) Enter_top(ISO top) | Del End PgDn | 7 8 9
    # Note: ISO Enter is split into enter_top (row 3) + enter_bot (row 5), both group=accent
    [
        ("tab",      "mod"),   ("q",    "alpha"), ("w",    "alpha"), ("e",    "alpha"),
        ("r",        "alpha"), ("t",    "alpha"), ("z",    "alpha"), ("u",    "alpha"),
        ("i",        "alpha"), ("o",    "alpha"), ("p",    "alpha"), ("ue",   "alpha"),
        ("plus",     "alpha"), ("enter_top", "accent"),
        ("del",      "nav"),   ("end",  "nav"),   ("pgdn", "nav"),
        ("num7",     "num"),   ("num8", "num"),   ("num9", "num"),
    ],
    # Row 4 (1): Numpad + (1u wide, 2u tall — center between rows 3 and 5)
    [
        ("num_add",  "num"),
    ],
    # Row 5 (16): CapsLk(1.8u) A-Ä Enter_bot(ISO bottom, 2.3u) | 4 5 6
    [
        ("caps",     "mod"),   ("a",    "alpha"), ("s",    "alpha"), ("d",    "alpha"),
        ("f",        "alpha"), ("g",    "alpha"), ("h",    "alpha"), ("j",    "alpha"),
        ("k",        "alpha"), ("l",    "alpha"), ("oe",   "alpha"), ("ae",   "alpha"),
        ("enter_bot","accent"),
        ("num4",     "num"),   ("num5", "num"),   ("num6", "num"),
    ],
    # Row 6 (16): LShift(2.3u) < Y-. RShift(2.8u) | Up | 1 2 3
    # Note: no explicit minus key in this row (template omits it or merges into RShift)
    [
        ("lshift",   "mod"),   ("less", "alpha"), ("y",    "alpha"), ("x",    "alpha"),
        ("c",        "alpha"), ("v",    "alpha"), ("b",    "alpha"), ("n",    "alpha"),
        ("m",        "alpha"), ("comma","alpha"),  ("period","alpha"), ("rshift","mod"),
        ("up",       "nav"),
        ("num1",     "num"),   ("num2", "num"),   ("num3", "num"),
    ],
    # Row 7 (1): Numpad Enter (1u wide, 2u tall — center between rows 6 and 8)
    [
        ("num_enter","num"),
    ],
    # Row 8 (13): LCtrl LWin LAlt Space(6.5u) RAlt RWin Menu RCtrl | ← ↓ → | Num0(2u) Num.
    [
        ("lctrl",    "mod"),   ("lwin", "mod"),   ("lalt", "mod"),   ("space","spacebar"),
        ("ralt",     "mod"),   ("rwin", "mod"),   ("menu", "mod"),   ("rctrl","mod"),
        ("left",     "nav"),   ("down", "nav"),   ("right","nav"),
        ("num0",     "num"),   ("num_dot","num"),
    ],
]

# ── Extra-area side-view groups (y ≥ MAIN_AREA_MAX_Y) ─────────────────────────
# Row groupings for side/extra keys — assigned view tags only, no ISO-DE IDs yet.
# For MVP, these are recolored as a whole via their y-cluster index.
SIDE_VIEW_GROUPS = ["front", "back", "left", "right", "alternates"]


# ── Extraction ────────────────────────────────────────────────────────────────

def extract_fills(pdf_path: Path) -> list:
    """Return list of (x0, y0, x1, y1, fill_hex) for all keycap-sized fills."""
    import fitz

    def rgb_to_hex(r, g, b):
        return "#{:02X}{:02X}{:02X}".format(round(r * 255), round(g * 255), round(b * 255))

    doc  = fitz.open(str(pdf_path))
    page = doc[0]

    fills = []
    for path in page.get_drawings():
        fill = path.get("fill")
        if not fill or len(fill) < 3:
            continue
        r = path.get("rect")
        if r is None:
            continue
        w = r.x1 - r.x0
        h = r.y1 - r.y0
        if w < MIN_KEY_W or h < MIN_KEY_H:
            continue
        fills.append({
            "x0": round(r.x0, 1), "y0": round(r.y0, 1),
            "x1": round(r.x1, 1), "y1": round(r.y1, 1),
            "cx": round((r.x0 + r.x1) / 2, 1),
            "cy": round((r.y0 + r.y1) / 2, 1),
            "width":  round(w, 1),
            "height": round(h, 1),
            "fill_hex": rgb_to_hex(*fill[:3]),
        })

    doc.close()
    return fills


def cluster_rows(fills: list, tol: float = ROW_CLUSTER_TOL) -> list[list]:
    """Cluster fills by Y-center into rows; each row sorted by X-center."""
    if not fills:
        return []

    by_y = sorted(fills, key=lambda f: f["cy"])
    rows = []
    current_row = [by_y[0]]

    for fill in by_y[1:]:
        if abs(fill["cy"] - current_row[-1]["cy"]) <= tol:
            current_row.append(fill)
        else:
            rows.append(sorted(current_row, key=lambda f: f["cx"]))
            current_row = [fill]
    rows.append(sorted(current_row, key=lambda f: f["cx"]))

    return rows


def width_u(width_px: float, unit_px: float = 51.4) -> float:
    return round(width_px / unit_px, 2)


def assign_ids(main_rows: list[list]) -> list:
    """Assign ISO-DE key IDs + groups using ROW_LAYOUTS positional table."""
    keys = []
    for row_idx, row_fills in enumerate(main_rows):
        if row_idx >= len(ROW_LAYOUTS):
            # Unexpected extra row — assign positional IDs
            for col_idx, f in enumerate(row_fills):
                f["id"]    = f"r{row_idx+1}c{col_idx+1}"
                f["name"]  = f["id"].upper()
                f["group"] = "alpha"
                f["width_u"] = width_u(f["width"])
                keys.append(f)
            continue

        layout = ROW_LAYOUTS[row_idx]
        if len(row_fills) != len(layout):
            print(
                f"  WARN: Row {row_idx+1}: expected {len(layout)} keys, "
                f"got {len(row_fills)} — using positional IDs r{row_idx+1}cN"
            )
            for col_idx, f in enumerate(row_fills):
                f["id"]    = f"r{row_idx+1}c{col_idx+1}"
                f["name"]  = f["id"].upper()
                f["group"] = "alpha"
                f["width_u"] = width_u(f["width"])
                keys.append(f)
            continue

        for f, (key_id, group) in zip(row_fills, layout):
            f["id"]      = key_id
            f["name"]    = key_id.upper()
            f["group"]   = group
            f["width_u"] = width_u(f["width"])
            keys.append(f)

    return keys


def assign_side_ids(side_rows: list[list]) -> list:
    """Assign side-view entries (positional IDs, view tag from SIDE_VIEW_GROUPS)."""
    sides = []
    for row_idx, row_fills in enumerate(side_rows):
        view = SIDE_VIEW_GROUPS[row_idx] if row_idx < len(SIDE_VIEW_GROUPS) else f"side{row_idx+1}"
        for col_idx, f in enumerate(row_fills):
            f["id"]   = f"{view}_{col_idx+1}"
            f["name"] = f["id"]
            f["view"] = view
            f["group"] = "side"
            f["width_u"] = width_u(f["width"])
            sides.append(f)
    return sides


# ── Build coord map ───────────────────────────────────────────────────────────

def build_coord_map(pdf_path: Path, analyze_only: bool = False) -> dict:
    import fitz

    doc  = fitz.open(str(pdf_path))
    page = doc[0]
    pw   = round(page.rect.width, 1)
    ph   = round(page.rect.height, 1)
    doc.close()

    print(f"PDF: {pdf_path.name}")
    print(f"  Page size : {pw} × {ph} pt")

    all_fills = extract_fills(pdf_path)
    print(f"  Total fills (≥{MIN_KEY_W}pt) : {len(all_fills)}")

    main_fills = [f for f in all_fills if f["cy"] < MAIN_AREA_MAX_Y]
    side_fills = [f for f in all_fills if f["cy"] >= MAIN_AREA_MAX_Y]
    print(f"  Main area (y<{MAIN_AREA_MAX_Y}) : {len(main_fills)}")
    print(f"  Side area (y≥{MAIN_AREA_MAX_Y}) : {len(side_fills)}")

    main_rows = cluster_rows(main_fills)
    side_rows = cluster_rows(side_fills)

    print(f"\n  Main rows : {len(main_rows)}")
    for i, row in enumerate(main_rows):
        print(f"    Row {i+1:2d}: {len(row):3d} keys  y≈{row[0]['cy']:.0f}")

    print(f"\n  Side rows : {len(side_rows)}")
    for i, row in enumerate(side_rows):
        print(f"    Row {i+1:2d}: {len(row):3d} fills y≈{row[0]['cy']:.0f}")

    if analyze_only:
        return {}

    keys  = assign_ids(main_rows)
    sides = assign_side_ids(side_rows)

    coord_map = {
        "keyboard":    "Cherry135",
        "layout":      "ISO-DE",
        "color_model": "RGB",
        "source_pdf":  pdf_path.name,
        "page_width":  pw,
        "page_height": ph,
        "key_count":   len(keys),
        "note": (
            "Auto-extracted via extract_cherry_coords.py. "
            "Verify key IDs against physical layout before first build. "
            "side_views are for 全五面 5-face printing (recolor solid only, MVP)."
        ),
        "keys":       keys,
        "side_views": sides,
    }
    return coord_map


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="Extract Cherry 135 coordinate map from PDF")
    p.add_argument("--pdf",     default=str(DEFAULT_PDF), help="Input PDF path")
    p.add_argument("--output",  default=str(OUTPUT_MAP),  help="Output JSON path")
    p.add_argument("--analyze", action="store_true",       help="Print stats only, no write")
    args = p.parse_args()

    try:
        import fitz
    except ImportError:
        print("ERROR: PyMuPDF not installed. Run: py -3 -m pip install pymupdf", file=sys.stderr)
        sys.exit(1)

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"ERROR: PDF not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    coord_map = build_coord_map(pdf_path, analyze_only=args.analyze)

    if args.analyze:
        print("\n(--analyze mode: no file written)")
        return

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(coord_map, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\nWritten: {out}")
    print(f"  Keys       : {coord_map['key_count']}")
    print(f"  Side views : {len(coord_map['side_views'])}")
    print("Done.")


if __name__ == "__main__":
    main()
