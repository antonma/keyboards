"""
generate_key_design.py — Generate key-design.json for a given design

Reads:
  - designs/<design>/palette.yaml  (color references)
  - designs/<design>/fonts.yaml    (font references)
  - layouts/cherry-135-coordinate-map.json  (key IDs, groups, positions)

Writes:
  - designs/<design>/key-design.json

The output JSON specifies per-key:
  - body_color:   palette color reference key
  - legend.main:  primary legend (text, color ref, font ref, size)
  - legend.sub:   secondary legend (optional — number row shift chars, etc.)

Script is idempotent: running again only adds keys that are not yet present.
Existing entries are NOT overwritten, so manual corrections survive re-runs.

Usage:
    py -3 scripts/generate_key_design.py --design terminal-v2
    py -3 scripts/generate_key_design.py --design terminal-v2 --force
    py -3 scripts/generate_key_design.py --design terminal-v2 --dry-run
"""

import argparse
import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent
DEFAULT_COORD_MAP = REPO / "layouts" / "cherry-135-coordinate-map.json"

# ── ISO-DE legend table ────────────────────────────────────────────────────────
# key_id → (main_text, sub_text_or_None, font_ref)
# font_ref: "primary" = JetBrains Mono, "icon" = Segoe UI Symbol (for arrows/symbols)

ISO_DE_LEGENDS: dict[str, tuple[str, str | None, str]] = {
    # F-key row
    "esc":  ("ESC",  None,  "primary"),
    "f1":   ("F1",   None,  "primary"),
    "f2":   ("F2",   None,  "primary"),
    "f3":   ("F3",   None,  "primary"),
    "f4":   ("F4",   None,  "primary"),
    "f5":   ("F5",   None,  "primary"),
    "f6":   ("F6",   None,  "primary"),
    "f7":   ("F7",   None,  "primary"),
    "f8":   ("F8",   None,  "primary"),
    "f9":   ("F9",   None,  "primary"),
    "f10":  ("F10",  None,  "primary"),
    "f11":  ("F11",  None,  "primary"),
    "f12":  ("F12",  None,  "primary"),

    # Number row (alpha group, ISO-DE)
    # sub = shifted character shown smaller below/above main legend
    "grave":   ("^",   "°",   "primary"),
    "1":       ("1",   None,  "primary"),   # ! omitted by design decision
    "2":       ("2",   '"',   "primary"),
    "3":       ("3",   "§",   "primary"),
    "4":       ("4",   "$",   "primary"),
    "5":       ("5",   "%",   "primary"),
    "6":       ("6",   "&",   "primary"),
    "7":       ("7",   "/",   "primary"),
    "8":       ("8",   "(",   "primary"),
    "9":       ("9",   ")",   "primary"),
    "0":       ("0",   "=",   "primary"),
    "ss":      ("ß",   "?",   "primary"),
    "dead_ac": ("´",   "`",   "primary"),

    # QWERTZ alpha rows
    "q":   ("Q",   None, "primary"),
    "w":   ("W",   None, "primary"),
    "e":   ("E",   None, "primary"),
    "r":   ("R",   None, "primary"),
    "t":   ("T",   None, "primary"),
    "z":   ("Z",   None, "primary"),
    "u":   ("U",   None, "primary"),
    "i":   ("I",   None, "primary"),
    "o":   ("O",   None, "primary"),
    "p":   ("P",   None, "primary"),
    "ue":  ("Ü",   None, "primary"),
    "plus":("+",   "*",  "primary"),

    "a":   ("A",   None, "primary"),
    "s":   ("S",   None, "primary"),
    "d":   ("D",   None, "primary"),
    "f":   ("F",   None, "primary"),
    "g":   ("G",   None, "primary"),
    "h":   ("H",   None, "primary"),
    "j":   ("J",   None, "primary"),
    "k":   ("K",   None, "primary"),
    "l":   ("L",   None, "primary"),
    "oe":  ("Ö",   None, "primary"),
    "ae":  ("Ä",   None, "primary"),
    "less":("<",   ">",  "primary"),

    "y":      ("Y",   None, "primary"),
    "x":      ("X",   None, "primary"),
    "c":      ("C",   None, "primary"),
    "v":      ("V",   None, "primary"),
    "b":      ("B",   None, "primary"),
    "n":      ("N",   None, "primary"),
    "m":      ("M",   None, "primary"),
    "comma":  (",",   ";",  "primary"),
    "period": (".",   ":",  "primary"),

    # Modifier keys — canonical ISO-DE symbols (CLAUDE.md)
    "bksp":   ("⟵",   None, "icon"),    # U+27F5 LONG LEFTWARDS ARROW
    "tab":    ("↹",   None, "icon"),    # U+21B9 LEFTWARDS ARROW TO BAR OVER RIGHTWARDS ARROW TO BAR
    "caps":   ("⇪",   None, "icon"),    # U+21EA UPWARDS WHITE ARROW FROM BAR
    "lshift": ("⇧",   None, "icon"),    # U+21E7 UPWARDS WHITE ARROW
    "rshift": ("⇧",   None, "icon"),
    "lctrl":  ("STRG", None, "primary"),
    "rctrl":  ("STRG", None, "primary"),
    "lwin":   ("WIN",  None, "primary"),
    "rwin":   ("WIN",  None, "primary"),
    "lalt":   ("ALT",  None, "primary"),
    "ralt":   ("ALT GR", None, "primary"),
    "menu":   ("MENU", None, "primary"),

    # Accent keys (Enter top/bottom halves + alt enter)
    "enter_top": ("↵",  None, "icon"),  # U+21B5 DOWNWARDS ARROW WITH CORNER LEFTWARDS
    "enter_bot": ("",   None, "primary"),  # bottom half carries no text
    "alt_enter_iso": ("↵", None, "icon"),

    # Spacebar
    "space":       ("",  None, "primary"),
    "alt_space_7u":("",  None, "primary"),

    # Navigation cluster
    "prtsc": ("PRT SC", None, "primary"),
    "scr":   ("SCR LK", None, "primary"),
    "pause": ("PAUSE",  None, "primary"),
    "ins":   ("INS",    None, "primary"),
    "home":  ("POS 1",  None, "primary"),    # canonical German Home = POS 1
    "pgup":  ("Bild\n↑", None, "primary"),  # Bild↑ two-line
    "del":   ("ENTF",   None, "primary"),    # canonical German Delete = ENTF
    "end":   ("ENDE",   None, "primary"),
    "pgdn":  ("Bild\n↓", None, "primary"),  # Bild↓ two-line
    "up":    ("↑",      None, "icon"),
    "left":  ("←",      None, "icon"),
    "down":  ("↓",      None, "icon"),
    "right": ("→",      None, "icon"),

    # Numpad
    "numlk":    ("NUM\nLK",  None, "primary"),
    "num_div":  ("/",        None, "primary"),
    "num_mul":  ("*",        None, "primary"),
    "num_sub":  ("-",        None, "primary"),
    "num7":     ("7",        None, "primary"),
    "num8":     ("8",        None, "primary"),
    "num9":     ("9",        None, "primary"),
    "num_add":  ("+",        None, "primary"),
    "num4":     ("4",        None, "primary"),
    "num5":     ("5",        None, "primary"),
    "num6":     ("6",        None, "primary"),
    "num1":     ("1",        None, "primary"),
    "num2":     ("2",        None, "primary"),
    "num3":     ("3",        None, "primary"),
    "num_enter":("↵",        None, "icon"),
    "num0":     ("0",        None, "primary"),
    "num_dot":  (".",        None, "primary"),
}

# ── Body color assignment ──────────────────────────────────────────────────────
# Group default, then per-id overrides

GROUP_BODY_COLOR: dict[str, str] = {
    "alpha":    "body_alpha",
    "fkey":     "body_alpha",
    "nav":      "body_alpha",
    "num":      "body_alpha",
    "mod":      "body_mod",
    "accent":   "body_mod",
    "spacebar": "body_mod",
}

# alt_mod* keys are physically modifier-sized keycaps despite being in alpha group
ID_BODY_OVERRIDE: dict[str, str] = {
    # These are alternate modifier-sized blanks in the kit
    "alt_mod1": "body_mod",
    "alt_mod2": "body_mod",
    "alt_mod3": "body_mod",
    "alt_mod4": "body_mod",
    "alt_mod5": "body_mod",
    "alt_mod6": "body_mod",
    # alt_shift and alt_mod variants in mod group already handled by group default
}

# Legend color by font ref (for legend_color reference)
FONT_LEGEND_COLOR: dict[str, str] = {
    "primary": "legend_main",
    "icon":    "legend_main",
}

SUB_LEGEND_COLOR = "legend_dim"


# ── Build key spec ─────────────────────────────────────────────────────────────

def build_key_spec(key: dict) -> dict:
    key_id = key["id"]
    group = key["group"]

    body_color = ID_BODY_OVERRIDE.get(key_id) or GROUP_BODY_COLOR.get(group, "body_alpha")

    legend_row = ISO_DE_LEGENDS.get(key_id)
    if legend_row is None:
        # Unknown key — blank spec, Anton fills manually
        main_text, sub_text, font_ref = ("", None, "primary")
    else:
        main_text, sub_text, font_ref = legend_row

    spec: dict = {
        "body_color": body_color,
        "legend": {
            "main": {
                "text": main_text,
                "color": FONT_LEGEND_COLOR.get(font_ref, "legend_main"),
                "font":  font_ref,
                "size":  18 if font_ref == "primary" else 16,
            }
        },
    }

    if sub_text is not None:
        spec["legend"]["sub"] = {
            "text":  sub_text,
            "color": SUB_LEGEND_COLOR,
            "font":  "primary",
            "size":  12,
        }

    return spec


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="Generate key-design.json for a design")
    p.add_argument("--design",    required=True, help="Design name (e.g. terminal-v2)")
    p.add_argument("--coord-map", default=str(DEFAULT_COORD_MAP),
                   help="Path to coordinate map JSON")
    p.add_argument("--force",   action="store_true",
                   help="Overwrite existing entries (default: keep existing)")
    p.add_argument("--dry-run", action="store_true",
                   help="Print what would be written, do not save")
    args = p.parse_args()

    design_dir = REPO / "designs" / args.design
    if not design_dir.exists():
        print(f"ERROR: Design directory not found: {design_dir}", file=sys.stderr)
        sys.exit(1)

    coord_map_path = Path(args.coord_map)
    if not coord_map_path.is_absolute():
        coord_map_path = REPO / coord_map_path
    if not coord_map_path.exists():
        print(f"ERROR: Coord map not found: {coord_map_path}", file=sys.stderr)
        sys.exit(1)

    with open(coord_map_path, encoding="utf-8") as f:
        coord_map = json.load(f)

    output_path = design_dir / "key-design.json"

    existing: dict = {}
    if output_path.exists() and not args.force:
        with open(output_path, encoding="utf-8") as f:
            existing = json.load(f).get("keys", {})
        print(f"  Existing entries: {len(existing)} (use --force to overwrite)")

    keys_out: dict = {}
    added, skipped = 0, 0

    for key in coord_map["keys"]:
        key_id = key["id"]
        if key_id in existing and not args.force:
            keys_out[key_id] = existing[key_id]
            skipped += 1
        else:
            keys_out[key_id] = build_key_spec(key)
            added += 1

    result = {
        "version":  1,
        "design":   args.design,
        "coord_map": coord_map_path.name,
        "keys":     keys_out,
    }

    print(f"generate_key_design")
    print(f"  Design    : {args.design}")
    print(f"  Coord map : {coord_map_path.name}")
    print(f"  Keys      : {len(keys_out)} total ({added} generated, {skipped} kept)")
    if args.dry_run:
        print("\n[dry-run] Not writing output.")
        print(json.dumps(result, ensure_ascii=False, indent=2)[:2000])
        return

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"  Output    : {output_path}")
    print("Done.")


if __name__ == "__main__":
    main()
