"""
generate_key_design.py — Generate key-design.json for a given design

Reads:
  - designs/<design>/palette.yaml  (color references)
  - designs/<design>/fonts.yaml    (font references)
  - layouts/cherry-135-coordinate-map.json  (key IDs, groups, positions)

Writes:
  - designs/<design>/key-design.json

The output JSON specifies per-key:
  - body_color:       palette color reference key
  - legend.main:      primary legend   (topleft anchor)
  - legend.sub:       secondary legend (bottomleft anchor, optional)
  - legend.tertiary:  AltGr legend     (bottomright anchor, optional)

Script is idempotent: running again only adds keys that are not yet present.
Existing entries are NOT overwritten, so manual corrections survive re-runs.

Usage:
    py -3 scripts/generate_key_design.py --design terminal-v2
    py -3 scripts/generate_key_design.py --design terminal-v2 --force
    py -3 scripts/generate_key_design.py --design terminal-v2 --dry-run
    py -3 scripts/generate_key_design.py --design sakura-drift \\
        --include designs/_shared/75-iso-de-base-kit.yaml
"""

import argparse
import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent
DEFAULT_COORD_MAP = REPO / "layouts" / "cherry-135-coordinate-map.json"


def load_include_set(include_path: Path) -> set[str]:
    """Load a base-kit YAML and return the set of key IDs to generate.

    Handles YAML integer keys (1, 2 ... 0) by converting to str.
    """
    try:
        import yaml
        with open(include_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except ImportError:
        print("ERROR: PyYAML required for --include. Install with: pip install pyyaml",
              file=sys.stderr)
        sys.exit(1)

    include_groups = data.get("include") or {}
    ids: set[str] = set()
    for group_ids in include_groups.values():
        for kid in (group_ids or []):
            ids.add(str(kid))
    return ids

# ── ISO-DE legend table ────────────────────────────────────────────────────────
# key_id → (main_text, sub_text_or_None, font_ref, tertiary_text_or_None)
# font_ref: "primary" = JetBrains Mono, "icon" = Segoe UI Symbol (for arrows/symbols)
# tertiary: AltGr character, rendered bottomright; None = no AltGr layer

ISO_DE_LEGENDS: dict[str, tuple[str, str | None, str, str | None]] = {
    # F-key row
    "esc":  ("ESC",  None,  "primary", None),
    "f1":   ("F1",   None,  "primary", None),
    "f2":   ("F2",   None,  "primary", None),
    "f3":   ("F3",   None,  "primary", None),
    "f4":   ("F4",   None,  "primary", None),
    "f5":   ("F5",   None,  "primary", None),
    "f6":   ("F6",   None,  "primary", None),
    "f7":   ("F7",   None,  "primary", None),
    "f8":   ("F8",   None,  "primary", None),
    "f9":   ("F9",   None,  "primary", None),
    "f10":  ("F10",  None,  "primary", None),
    "f11":  ("F11",  None,  "primary", None),
    "f12":  ("F12",  None,  "primary", None),

    # Number row — Anton coord-map IDs (iso-de-75-anton-coordinate-map.json)
    # ISO-DE QWERTZ ground truth, per Handoff 9bb89869
    "grave":   ("^",  "°",  "primary", None),
    "num_1":   ("1",  "!",  "primary", None),
    "num_2":   ("2",  '"',  "primary", "²"),   # U+00B2
    "num_3":   ("3",  "§",  "primary", "³"),   # U+00B3
    "num_4":   ("4",  "$",  "primary", None),
    "num_5":   ("5",  "%",  "primary", None),
    "num_6":   ("6",  "&",  "primary", None),
    "num_7":   ("7",  "/",  "primary", "{"),
    "num_8":   ("8",  "(",  "primary", "["),
    "num_9":   ("9",  ")",  "primary", "]"),
    "num_0":   ("0",  "=",  "primary", "}"),
    "ss":      ("ß",  "?",  "primary", "\\"),
    "dead_ac": ("´",  "`",  "primary", None),
    "hash":    ("#",  "'",  "primary", None),   # apostrophe as secondary
    "dash":    ("-",  "_",  "primary", None),

    # Legacy IDs (cherry-135-coordinate-map.json uses bare digits)
    "1":  ("1",  "!",  "primary", None),
    "2":  ("2",  '"',  "primary", "²"),
    "3":  ("3",  "§",  "primary", "³"),
    "4":  ("4",  "$",  "primary", None),
    "5":  ("5",  "%",  "primary", None),
    "6":  ("6",  "&",  "primary", None),
    "7":  ("7",  "/",  "primary", "{"),
    "8":  ("8",  "(",  "primary", "["),
    "9":  ("9",  ")",  "primary", "]"),
    "0":  ("0",  "=",  "primary", "}"),

    # QWERTZ alpha rows — AltGr tertiaries where applicable
    "q":   ("Q",  None, "primary", "@"),
    "w":   ("W",  None, "primary", None),
    "e":   ("E",  None, "primary", "€"),   # U+20AC
    "r":   ("R",  None, "primary", None),
    "t":   ("T",  None, "primary", None),
    "z":   ("Z",  None, "primary", None),
    "u":   ("U",  None, "primary", None),
    "i":   ("I",  None, "primary", None),
    "o":   ("O",  None, "primary", None),
    "p":   ("P",  None, "primary", None),
    "ue":  ("Ü",  None, "primary", None),
    "plus":("+",  "*",  "primary", "~"),

    "a":   ("A",  None, "primary", None),
    "s":   ("S",  None, "primary", None),
    "d":   ("D",  None, "primary", None),
    "f":   ("F",  None, "primary", None),
    "g":   ("G",  None, "primary", None),
    "h":   ("H",  None, "primary", None),
    "j":   ("J",  None, "primary", None),
    "k":   ("K",  None, "primary", None),
    "l":   ("L",  None, "primary", None),
    "oe":  ("Ö",  None, "primary", None),
    "ae":  ("Ä",  None, "primary", None),
    "less":("<",  ">",  "primary", "|"),

    "y":      ("Y",  None, "primary", None),
    "x":      ("X",  None, "primary", None),
    "c":      ("C",  None, "primary", None),
    "v":      ("V",  None, "primary", None),
    "b":      ("B",  None, "primary", None),
    "n":      ("N",  None, "primary", None),
    "m":      ("M",  None, "primary", "µ"),   # U+00B5
    "comma":  (",",  ";",  "primary", None),
    "period": (".",  ":",  "primary", None),

    # Modifier keys — canonical ISO-DE symbols (CLAUDE.md)
    "bksp":   ("⟵",    None, "icon",    None),  # U+27F5
    "tab":    ("↹",    None, "icon",    None),  # U+21B9
    "caps":   ("⇪",    None, "icon",    None),  # U+21EA
    "lshift": ("⇧",    None, "icon",    None),  # U+21E7
    "rshift": ("⇧",    None, "icon",    None),
    "lctrl":  ("STRG", None, "primary", None),
    "rctrl":  ("STRG", None, "primary", None),
    "lwin":   ("WIN",  None, "primary", None),
    "rwin":   ("WIN",  None, "primary", None),
    "lalt":   ("ALT",   None, "primary", None),
    "ralt":   ("ALTGR", None, "primary", None),  # 6-char "ALT GR" → 5-char "ALTGR" (fits 1u @ 14pt)
    "fn":     ("FN",   None, "primary", None),
    "menu":   ("MENU", None, "primary", None),

    # Accent keys (Enter top/bottom halves + alt enter)
    "enter_top":     ("↵", None, "icon",    None),  # U+21B5; centered exception in anchor system
    "enter_bot":     ("",  None, "primary", None),
    "alt_enter_iso": ("↵", None, "icon",    None),

    # Spacebar
    "space":        ("", None, "primary", None),
    "alt_space_7u": ("", None, "primary", None),

    # Navigation cluster
    "prtsc":  ("PRT SC", None, "primary", None),
    "scr":    ("SCR LK", None, "primary", None),
    "pause":  ("PAUSE",  None, "primary", None),
    "ins":    ("EINFG",  None, "primary", None),
    # Compat keys (Antons-template Alternates-Block)
    "prt_sc": ("DRUCK",  None, "primary", None),
    "scr_lk": ("ROLL",   None, "primary", None),  # 6 chars ROLLEN → 4 chars ROLL (fits 1u @ 18pt)
    "home":   ("POS 1",  None, "primary", None),
    "pgup":   ("Bild↑",  None, "primary", None),  # single-line per ADR
    "del":    ("ENTF",   None, "primary", None),
    "end":    ("ENDE",   None, "primary", None),
    "pgdn":   ("Bild↓",  None, "primary", None),  # single-line per ADR
    "up":     ("↑",      None, "icon",    None),
    "left":   ("←",      None, "icon",    None),
    "down":   ("↓",      None, "icon",    None),
    "right":  ("→",      None, "icon",    None),

    # Numpad
    "numlk":    ("NUM LK", None, "primary", None),
    "num_div":  ("/",      None, "primary", None),
    "num_mul":  ("*",      None, "primary", None),
    "num_sub":  ("-",      None, "primary", None),
    "num7":     ("7",      None, "primary", None),
    "num8":     ("8",      None, "primary", None),
    "num9":     ("9",      None, "primary", None),
    "num_add":  ("+",      None, "primary", None),
    "num4":     ("4",      None, "primary", None),
    "num5":     ("5",      None, "primary", None),
    "num6":     ("6",      None, "primary", None),
    "num1":     ("1",      None, "primary", None),
    "num2":     ("2",      None, "primary", None),
    "num3":     ("3",      None, "primary", None),
    "num_enter":("↵",      None, "icon",    None),
    "num0":     ("0",      None, "primary", None),
    "num_dot":  (".",      None, "primary", None),
}

# ── Body color assignment ──────────────────────────────────────────────────────
# Group default, then per-id overrides

GROUP_BODY_COLOR: dict[str, str] = {
    # cherry-135 group names
    "alpha":    "body_alpha",
    "fkey":     "body_alpha",
    "nav":      "body_alpha",
    "num":      "body_alpha",
    "mod":      "body_mod",
    "accent":   "body_mod",
    "spacebar": "body_mod",
    # 75-iso-de (Antons-template) group names
    "fn_row":       "body_alpha",
    "numbers":      "body_alpha",
    "alphas":       "body_alpha",
    "arrows":       "body_alpha",
    "primary_mods": "body_mod",
    "shifts":       "body_mod",
    "mods_left":    "body_mod",
    "mods_right":   "body_mod",
    "compat":       "body_alpha",
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

# Groups where ALL text-labeled primary legends get a fixed size (Anton: alle gleich groß).
# 14pt = largest size that fits 5-char labels on 1u keys (51.4pt) with 4pt offset.
# Icon-labeled keys (tab/caps/shift/bksp/enter) are excluded — they use their own size.
MOD_PRIMARY_GROUPS: frozenset[str] = frozenset({
    "mods_left", "mods_right", "nav", "compat",
    # cherry-135 equivalents
    "mod", "accent",
})
MOD_PRIMARY_SIZE = 14


# ── Build key spec ─────────────────────────────────────────────────────────────

def build_key_spec(key: dict) -> dict:
    key_id = key["id"]
    group = key["group"]

    body_color = ID_BODY_OVERRIDE.get(key_id) or GROUP_BODY_COLOR.get(group, "body_alpha")

    legend_row = ISO_DE_LEGENDS.get(key_id)
    if legend_row is None:
        # Unknown key — blank spec, Anton fills manually
        main_text, sub_text, font_ref, tertiary_text = ("", None, "primary", None)
    else:
        if len(legend_row) == 4:
            main_text, sub_text, font_ref, tertiary_text = legend_row
        else:
            main_text, sub_text, font_ref = legend_row
            tertiary_text = None

    # Fixed size for mod/nav/compat text labels so all Steuerungstasten look uniform.
    # Icon-based labels (font_ref == "icon") keep their own size (16pt).
    if font_ref == "primary" and group in MOD_PRIMARY_GROUPS:
        main_size = MOD_PRIMARY_SIZE
    elif font_ref == "primary":
        main_size = 18
    else:
        main_size = 16  # icon

    spec: dict = {
        "body_color": body_color,
        "legend": {
            "main": {
                "text": main_text,
                "color": FONT_LEGEND_COLOR.get(font_ref, "legend_main"),
                "font":  font_ref,
                "size":  main_size,
            }
        },
    }

    if sub_text is not None:
        spec["legend"]["sub"] = {
            "text":  sub_text,
            "color": SUB_LEGEND_COLOR,
            "font":  "secondary",
            "size":  12,
        }

    if tertiary_text is not None:
        spec["legend"]["tertiary"] = {
            "text":  tertiary_text,
            "color": SUB_LEGEND_COLOR,
            "font":  "secondary",
            "size":  10,
        }

    return spec


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="Generate key-design.json for a design")
    p.add_argument("--design",    required=True, help="Design name (e.g. terminal-v2)")
    p.add_argument("--coord-map", default=str(DEFAULT_COORD_MAP),
                   help="Path to coordinate map JSON")
    p.add_argument("--include", default=None,
                   help="Path to base-kit YAML (e.g. designs/_shared/75-iso-de-base-kit.yaml). "
                        "Only keys listed there are written to key-design.json; "
                        "all others are omitted (they stay original-beige in the template).")
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

    # Load include set if provided
    include_set: set[str] | None = None
    include_file_name: str | None = None
    if args.include:
        include_path = Path(args.include)
        if not include_path.is_absolute():
            include_path = REPO / include_path
        if not include_path.exists():
            print(f"ERROR: Include file not found: {include_path}", file=sys.stderr)
            sys.exit(1)
        include_set = load_include_set(include_path)
        include_file_name = include_path.name
        print(f"  Include   : {len(include_set)} keys from {include_file_name}")

    output_path = design_dir / "key-design.json"

    existing: dict = {}
    if output_path.exists() and not args.force:
        with open(output_path, encoding="utf-8") as f:
            existing = json.load(f).get("keys", {})
        print(f"  Existing entries: {len(existing)} (use --force to overwrite)")

    keys_out: dict = {}
    added, skipped, excluded = 0, 0, 0

    for key in coord_map["keys"]:
        key_id = key["id"]
        if include_set is not None and key_id not in include_set:
            excluded += 1
            continue
        if key_id in existing and not args.force:
            keys_out[key_id] = existing[key_id]
            skipped += 1
        else:
            keys_out[key_id] = build_key_spec(key)
            added += 1

    result = {
        "version":    1,
        "design":     args.design,
        "coord_map":  coord_map_path.name,
        "include_file": include_file_name,
        "keys":       keys_out,
    }

    print(f"generate_key_design")
    print(f"  Design    : {args.design}")
    print(f"  Coord map : {coord_map_path.name}")
    if include_set is not None:
        print(f"  Mode      : base-kit ({len(include_set)} include, {excluded} excluded/beige)")
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
