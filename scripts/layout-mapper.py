#!/usr/bin/env python3
"""
Keyboard Layout Mapper — Keycap-Konfigurator
Definiert exakte Keycap-Layouts für alle 17 Akko/MonsGeek ISO-DE Modelle.
Erzeugt: layouts/<model>.json + inventory/keycap-inventory.json

Datenquellen:
  - VIA JSON-Files (via-raw/): exakte physische Key-Sizes für 5 Modelle
  - ISO-DE Standard + Hersteller-Spezifikationen für die übrigen 12

Key-Größen aus VIA-Analyse:
  5075B:    Tab=1.75u (!), CapsLk=2u (!), BS=2.25u, LShift=1.25u, RShift=1.75u, Space=6.25u
  M1V5:     Tab=1.5u,      CapsLk=1.75u, BS=2.25u, LShift=1.25u, RShift=1.75u, Space=6.5u (!)
  MU02:     Tab=1.5u,      CapsLk=1.75u, BS=2.25u, LShift=1.25u, RShift=1.75u, Space=6.5u
  5075S:    Tab=1.5u,      CapsLk=1.75u, BS=2u,    LShift=1.25u, RShift=1.75u, Space=6.25u
  5087S:    Tab=1.5u,      CapsLk=1.75u, BS=2u,    LShift=1.25u, RShift=2.75u, Space=6.25u (ISO-DE adaptation)
"""

import json
import os
from pathlib import Path
from copy import deepcopy

# --- Output directories ---
REPO_ROOT = Path(__file__).parent.parent
LAYOUTS_DIR = REPO_ROOT / "layouts"
INVENTORY_DIR = REPO_ROOT / "inventory"


# ===========================================================================
# KEY DEFINITIONS
# ===========================================================================

def k(label, w=1.0, h=1.0, key_type="alpha", shape="standard", note=None):
    """Create a keycap dict."""
    d = {"label": label, "w": w, "h": h, "type": key_type, "shape": shape}
    if note:
        d["note"] = note
    return d

def gap(w):
    return {"gap": w}

# Shorthand constructors
def fn(label, w=1.0):   return k(label, w, key_type="fn")
def mod(label, w=1.0):  return k(label, w, key_type="mod")
def nav(label, w=1.0):  return k(label, w, key_type="nav")
def num(label, w=1.0, h=1.0): return k(label, w, h, key_type="num")
def spc(w=6.25):        return k("Space", w, key_type="space")

# ISO Enter: L-shaped physical keycap (single key spanning 2 rows)
ISO_ENTER = k("Enter", w=1.5, h=2.0, key_type="mod", shape="iso_enter")
# 5075B variant (slightly narrower top, but same physical keycap for sourcing)
ISO_ENTER_5075B = k("Enter", w=1.25, h=2.0, key_type="mod", shape="iso_enter",
                    note="5075B specific: 1.25u top step (vs standard 1.5u)")

# ISO-DE extra key between LShift and Y
ISO_EXTRA = k("< >", w=1.0, key_type="alpha", shape="iso_extra")


# ===========================================================================
# ISO-DE BASE KEY ROWS (reusable building blocks)
# ===========================================================================

# Number row (without Tab/Backspace)
NUMBER_ROW_ALPHA = [
    k("^ °"),           # Zirkumflex / Degree
    k("1 !"),
    k("2 \""),
    k("3 §"),
    k("4 $"),
    k("5 %"),
    k("6 &"),
    k("7 /"),
    k("8 ("),
    k("9 )"),
    k("0 ="),
    k("ß ?"),
    k("´ `"),           # Dead key backtick
]

# QWERTZ alpha keys (without Tab and Enter/+)
QWERTZ_ALPHA = [
    k("Q"), k("W"), k("E"), k("R"), k("T"),
    k("Z"), k("U"), k("I"), k("O"), k("P"),
    k("Ü"), k("+ *"),
]

# Home row alpha (without CapsLk and Enter/#)
ASDF_ALPHA = [
    k("A"), k("S"), k("D"), k("F"), k("G"),
    k("H"), k("J"), k("K"), k("L"),
    k("Ö"), k("Ä"), k("# '"),
]

# Shift row alpha (without shifts)
ZXCV_ALPHA = [
    ISO_EXTRA,
    k("Y"), k("X"), k("C"), k("V"), k("B"),
    k("N"), k("M"), k(", ;"), k(". :"), k("- _"),
]

# Function row
FN_ROW = [fn("F1"), fn("F2"), fn("F3"), fn("F4"), fn("F5"), fn("F6"),
          fn("F7"), fn("F8"), fn("F9"), fn("F10"), fn("F11"), fn("F12")]


# ===========================================================================
# COMPLETE ROW BUILDERS
# ===========================================================================

def make_fn_row(extra_right=None, gap_between=True):
    """Esc + F1-F12 + optional right keys."""
    row = [fn("Esc")]
    if gap_between:
        row += [gap(0.5)]
    row += FN_ROW[:4]
    if gap_between:
        row += [gap(0.25)]
    row += FN_ROW[4:8]
    if gap_between:
        row += [gap(0.25)]
    row += FN_ROW[8:12]
    if extra_right:
        row += [gap(0.25)] + list(extra_right)
    return row

def make_number_row(bs_width=2.0, extra_right=None):
    """Number row with backspace."""
    row = list(NUMBER_ROW_ALPHA) + [mod("BS", bs_width)]
    if extra_right:
        row += list(extra_right)
    return row

def make_qwertz_row(tab_width=1.5, iso_enter=True, extra_right=None):
    """QWERTZ row with Tab and ISO Enter."""
    row = [mod("Tab", tab_width)] + list(QWERTZ_ALPHA)
    if iso_enter:
        row += [ISO_ENTER]
    if extra_right:
        row += list(extra_right)
    return row

def make_asdf_row(caps_width=1.75, extra_right=None):
    """Home row (ASDF). ISO Enter is part of the QWERTZ row (spans 2 rows)."""
    row = [mod("Caps", caps_width)] + list(ASDF_ALPHA)
    if extra_right:
        row += list(extra_right)
    return row

def make_shift_row(lshift_width=1.25, rshift_width=2.75, add_up_arrow=False, extra_right=None):
    """Shift row. ISO-DE: LShift=1.25u + <> extra key."""
    row = [mod("LShift", lshift_width)] + list(ZXCV_ALPHA) + [mod("RShift", rshift_width)]
    if add_up_arrow:
        row += [nav("↑")]
    if extra_right:
        row += list(extra_right)
    return row

def make_75pct_bottom(space_width=6.25):
    """
    75% bottom row:
    Ctrl(1.25) Win(1.25) Alt(1.25) | Space | [AltGr Fn Ctrl] + arrow cluster
    Note: arrows split across bottom + end of shift row.
    """
    mods_left  = [mod("Strg", 1.25), mod("Win", 1.25), mod("Alt", 1.25)]
    space_key  = [spc(space_width)]
    mods_right = [mod("AltGr", 1.0), mod("Fn", 1.0), mod("Strg", 1.0)]
    arrows     = [nav("←"), nav("↓"), nav("→")]
    return mods_left + space_key + mods_right + arrows

def make_65pct_bottom(space_width=6.5):
    """65% bottom row with integrated arrow cluster."""
    return [
        mod("Strg", 1.25), mod("Win", 1.25), mod("Alt", 1.25),
        spc(space_width),
        mod("AltGr", 1.0), mod("Fn", 1.0),
        nav("↑"),
        nav("←"), nav("↓"), nav("→"),
    ]

def make_60pct_bottom(space_width=6.25):
    """60% bottom row — no arrows, all mods."""
    return [
        mod("Strg", 1.25), mod("Win", 1.25), mod("Alt", 1.25),
        spc(space_width),
        mod("AltGr", 1.25), mod("Fn", 1.0), mod("Menu", 1.0), mod("Strg", 1.25),
    ]

def make_tkl_bottom():
    """80% TKL bottom row."""
    return [
        mod("Strg", 1.25), mod("Win", 1.25), mod("Alt", 1.25),
        spc(6.25),
        mod("AltGr", 1.25), mod("Win", 1.25), mod("Menu", 1.25), mod("Strg", 1.25),
    ]

def make_fullsize_bottom():
    """100%/96% full bottom row."""
    return make_tkl_bottom()

# --- Nav block (TKL + 100%) ---
def nav_cluster_6():
    """6-key nav cluster: Ins Del / Home End / PgUp PgDn (2 cols × 3 rows)."""
    return [
        nav("Einfg"), nav("Entf"),
        nav("Pos1"), nav("Ende"),
        nav("BildAuf"), nav("BildAb"),
    ]

def arrow_cluster():
    return [nav("↑"), nav("←"), nav("↓"), nav("→")]

# --- Numpad ---
def make_numpad():
    """Standard ISO numpad (17 keys, incl 2u + and 2u Enter)."""
    return [
        # Row: NumLk / * -
        num("NumLk"), num("/"), num("*"), num("-"),
        # Row: 7 8 9 +(2u tall)
        num("7"), num("8"), num("9"), num("+", h=2.0),
        # Row: 4 5 6
        num("4"), num("5"), num("6"),
        # Row: 1 2 3 Enter(2u tall)
        num("1"), num("2"), num("3"), num("Enter", h=2.0),
        # Row: 0(2u wide) .
        num("0", w=2.0), num("."),
    ]


# ===========================================================================
# LAYOUT DEFINITIONS — all 17 Akko/MonsGeek ISO-DE Modelle
# ===========================================================================

LAYOUTS = {}

# --- Helpers ---
def side_col_4():
    """Right-side column for 75% (4×1u nav keys typical)."""
    return [nav("Entf"), nav("PgAuf"), nav("Pos1"), nav("Ende")]

def register(model_id, meta, rows):
    """Add model to LAYOUTS registry."""
    total_keycaps = sum(
        1 for row in rows for k in row
        if isinstance(k, dict) and "label" in k and k.get("type") != "encoder"
    )
    LAYOUTS[model_id] = {**meta, "total_keycaps": total_keycaps, "rows": rows}


# ---------------------------------------------------------------------------
# 1. FUN60 Pro ISO HE — 60%, ~61 keys
# ---------------------------------------------------------------------------
register(
    "akko-fun60-pro-iso-he",
    {
        "name": "Akko FUN60 Pro ISO HE",
        "vendor": "Akko",
        "form_factor": "60%",
        "approx_keys": 61,
        "iso_de": True,
        "has_encoder": False,
        "via_source": None,
        "sourcing_notes": "BS=2u, LShift=1.25u, RShift=2.75u (full), Space=6.25u. No F-keys, no nav. Standard 60% ISO-DE.",
    },
    rows=[
        make_number_row(bs_width=2.0),
        make_qwertz_row(tab_width=1.5, iso_enter=True),
        make_asdf_row(caps_width=1.75),
        make_shift_row(lshift_width=1.25, rshift_width=2.75),
        make_60pct_bottom(space_width=6.25),
    ]
)

# ---------------------------------------------------------------------------
# 2. MOD68 HE ISO — 65%, 68 keys
# ---------------------------------------------------------------------------
register(
    "akko-mod68-he-iso",
    {
        "name": "Akko MOD68 HE ISO",
        "vendor": "Akko",
        "form_factor": "65%",
        "approx_keys": 68,
        "iso_de": True,
        "has_encoder": False,
        "via_source": None,
        "sourcing_notes": "BS=2u, LShift=1.25u, RShift=1.75u, Space=6.5u. Compact 65% with arrow cluster + 3 right-column nav keys.",
    },
    rows=[
        make_number_row(bs_width=2.0, extra_right=[nav("Entf")]),
        make_qwertz_row(tab_width=1.5, iso_enter=True, extra_right=[nav("BildAuf")]),
        make_asdf_row(caps_width=1.75, extra_right=[nav("BildAb")]),
        make_shift_row(lshift_width=1.25, rshift_width=1.75),
        make_65pct_bottom(space_width=6.5),
    ]
)

# ---------------------------------------------------------------------------
# 3. Black & Gold 3068B Plus ISO DE — 65%, 68 keys
# ---------------------------------------------------------------------------
register(
    "akko-3068b-plus-iso-de",
    {
        "name": "Akko Black & Gold 3068B Plus ISO DE",
        "vendor": "Akko",
        "form_factor": "65%",
        "approx_keys": 68,
        "iso_de": True,
        "has_encoder": False,
        "via_source": None,
        "sourcing_notes": "Same physical layout as MOD68 HE ISO. BS=2u, LShift=1.25u, RShift=1.75u, Space=6.5u.",
    },
    rows=[
        make_number_row(bs_width=2.0, extra_right=[nav("Entf")]),
        make_qwertz_row(tab_width=1.5, iso_enter=True, extra_right=[nav("BildAuf")]),
        make_asdf_row(caps_width=1.75, extra_right=[nav("BildAb")]),
        make_shift_row(lshift_width=1.25, rshift_width=1.75),
        make_65pct_bottom(space_width=6.5),
    ]
)

# ---------------------------------------------------------------------------
# 4. Black & Gold 3068B Plus ISO — 65%, 68 keys (ISO but not DE-specific)
# ---------------------------------------------------------------------------
register(
    "akko-3068b-plus-iso",
    {
        "name": "Akko Black & Gold 3068B Plus ISO",
        "vendor": "Akko",
        "form_factor": "65%",
        "approx_keys": 68,
        "iso_de": True,
        "has_encoder": False,
        "via_source": None,
        "sourcing_notes": "Same physical layout as 3068B Plus ISO DE. ISO keycap sizes identical; legend language may differ.",
    },
    rows=[
        make_number_row(bs_width=2.0, extra_right=[nav("Entf")]),
        make_qwertz_row(tab_width=1.5, iso_enter=True, extra_right=[nav("BildAuf")]),
        make_asdf_row(caps_width=1.75, extra_right=[nav("BildAb")]),
        make_shift_row(lshift_width=1.25, rshift_width=1.75),
        make_65pct_bottom(space_width=6.5),
    ]
)

# ---------------------------------------------------------------------------
# 5. Black & Gold 3084B Plus ISO-DE — 75%, 84 keys (standard 75%)
# ---------------------------------------------------------------------------
register(
    "akko-3084b-plus-iso-de",
    {
        "name": "Akko Black & Gold 3084B Plus ISO-DE",
        "vendor": "Akko",
        "form_factor": "75%",
        "approx_keys": 84,
        "iso_de": True,
        "has_encoder": False,
        "via_source": None,
        "sourcing_notes": "Standard 75% sizes: Tab=1.5u, CapsLk=1.75u, BS=2u, LShift=1.25u, RShift=1.75u, Space=6.25u. 4-key right column.",
    },
    rows=[
        make_fn_row(extra_right=[nav("Entf")]),
        make_number_row(bs_width=2.0, extra_right=[nav("BildAuf")]),
        make_qwertz_row(tab_width=1.5, iso_enter=True, extra_right=[nav("BildAb")]),
        make_asdf_row(caps_width=1.75, extra_right=[nav("Pos1")]),
        make_shift_row(lshift_width=1.25, rshift_width=1.75, add_up_arrow=True),
        make_75pct_bottom(space_width=6.25),
    ]
)

# ---------------------------------------------------------------------------
# 6. 5075B Plus VIA ISO — 75%, ~84 keys
#    Source: akko-5075b-via-iso.json
#    SPECIAL: Tab=1.75u (!), CapsLk=2u (!), BS=2.25u, Space=6.25u, encoder
# ---------------------------------------------------------------------------
register(
    "akko-5075b-plus-via-iso",
    {
        "name": "Akko 5075B Plus VIA ISO",
        "vendor": "Akko",
        "form_factor": "75%",
        "approx_keys": 84,
        "iso_de": True,
        "has_encoder": True,
        "via_source": "akko-5075b-via-iso.json",
        "sourcing_notes": (
            "NON-STANDARD: Tab=1.75u (needs special cap!), CapsLk=2u (needs special cap!), "
            "BS=2.25u, LShift=1.25u, RShift=1.75u, Space=6.25u. "
            "4-key right column. Encoder knob (no keycap)."
        ),
    },
    rows=[
        make_fn_row(extra_right=[nav("Entf")]),
        make_number_row(bs_width=2.25, extra_right=[nav("BildAuf")]),
        # Tab=1.75u NON-STANDARD
        [mod("Tab", 1.75)] + list(QWERTZ_ALPHA) + [ISO_ENTER_5075B, nav("BildAb")],
        # CapsLk=2u NON-STANDARD (note: row has no # key — absent or layer-mapped on 5075B)
        [mod("Caps", 2.0)] + list(ASDF_ALPHA[:-1]) + [nav("Pos1")],
        make_shift_row(lshift_width=1.25, rshift_width=1.75, add_up_arrow=True),
        make_75pct_bottom(space_width=6.25),
    ]
)

# ---------------------------------------------------------------------------
# 7. Blue on White 5075B Plus ISO — 75%, ~84 keys (same layout as #6)
# ---------------------------------------------------------------------------
register(
    "akko-5075b-plus-blue-on-white-iso",
    {
        "name": "Akko Blue on White 5075B Plus ISO",
        "vendor": "Akko",
        "form_factor": "75%",
        "approx_keys": 84,
        "iso_de": True,
        "has_encoder": True,
        "via_source": "akko-5075b-via-iso.json",
        "sourcing_notes": "Same PCB/layout as 5075B Plus VIA ISO. Tab=1.75u, CapsLk=2u (non-standard). Different colorway only.",
    },
    rows=deepcopy(LAYOUTS["akko-5075b-plus-via-iso"]["rows"])
)

# ---------------------------------------------------------------------------
# 8. MonsGeek M1 V5 VIA ISO — 75%, ~82 keys
#    Source: monsgeek-m1v5-via-iso.json
#    SPECIAL: Space=6.5u (!), encoder
# ---------------------------------------------------------------------------
register(
    "monsgeek-m1v5-via-iso",
    {
        "name": "MonsGeek M1 V5 VIA ISO",
        "vendor": "MonsGeek",
        "form_factor": "75%",
        "approx_keys": 82,
        "iso_de": True,
        "has_encoder": True,
        "via_source": "monsgeek-m1v5-via-iso.json",
        "sourcing_notes": (
            "Standard Tab=1.5u, CapsLk=1.75u, BS=2.25u, LShift=1.25u, RShift=1.75u. "
            "NON-STANDARD: Space=6.5u (needs special spacebar!). "
            "4-key right column. Encoder knob (no keycap)."
        ),
    },
    rows=[
        make_fn_row(extra_right=[nav("Entf")]),
        make_number_row(bs_width=2.25, extra_right=[nav("BildAuf")]),
        make_qwertz_row(tab_width=1.5, iso_enter=True, extra_right=[nav("BildAb")]),
        make_asdf_row(caps_width=1.75, extra_right=[nav("Pos1")]),
        make_shift_row(lshift_width=1.25, rshift_width=1.75, add_up_arrow=True),
        make_75pct_bottom(space_width=6.5),
    ]
)

# ---------------------------------------------------------------------------
# 9. MU01 Mountain Seclusion — 75%, ~84 keys (wood housing)
# ---------------------------------------------------------------------------
register(
    "akko-mu01-iso-de",
    {
        "name": "Akko MU01 Mountain Seclusion ISO-DE",
        "vendor": "Akko",
        "form_factor": "75%",
        "approx_keys": 84,
        "iso_de": True,
        "has_encoder": True,
        "via_source": None,
        "sourcing_notes": "Wood housing 75%. Standard 75% layout. Tab=1.5u, CapsLk=1.75u, BS=2.25u, Space=6.5u (estimated, same platform as MU02).",
    },
    rows=[
        make_fn_row(extra_right=[nav("Entf")]),
        make_number_row(bs_width=2.25, extra_right=[nav("BildAuf")]),
        make_qwertz_row(tab_width=1.5, iso_enter=True, extra_right=[nav("BildAb")]),
        make_asdf_row(caps_width=1.75, extra_right=[nav("Pos1")]),
        make_shift_row(lshift_width=1.25, rshift_width=1.75, add_up_arrow=True),
        make_75pct_bottom(space_width=6.5),
    ]
)

# ---------------------------------------------------------------------------
# 10. MU02 Mountain Seclusion ISO-DE — 75%, ~75 keys (wood housing)
#     Source: akko-mu02-via-iso.json
#     Confirmed: Tab=1.5u, CapsLk=1.75u, Space=6.5u, BS=2.25u, encoder
# ---------------------------------------------------------------------------
register(
    "akko-mu02-iso-de",
    {
        "name": "Akko MU02 Mountain Seclusion ISO-DE",
        "vendor": "Akko",
        "form_factor": "75%",
        "approx_keys": 75,
        "iso_de": True,
        "has_encoder": True,
        "via_source": "akko-mu02-via-iso.json",
        "sourcing_notes": "Wood housing. VIA confirmed: Tab=1.5u, CapsLk=1.75u, BS=2.25u, LShift=1.25u, RShift=1.75u, Space=6.5u. Same physical layout as M1 V5.",
    },
    rows=deepcopy(LAYOUTS["monsgeek-m1v5-via-iso"]["rows"])
)

# ---------------------------------------------------------------------------
# 11. MOD 007B HE ISO — 75%, ~82 keys (premium aluminium)
# ---------------------------------------------------------------------------
register(
    "akko-mod007b-he-iso",
    {
        "name": "Akko MOD 007B HE ISO",
        "vendor": "Akko",
        "form_factor": "75%",
        "approx_keys": 82,
        "iso_de": True,
        "has_encoder": False,
        "via_source": None,
        "sourcing_notes": "Premium alu 75%. No encoder. Standard sizes: Tab=1.5u, CapsLk=1.75u, BS=2.25u, LShift=1.25u, RShift=1.75u, Space=6.25u.",
    },
    rows=[
        make_fn_row(extra_right=[nav("Entf")]),
        make_number_row(bs_width=2.25, extra_right=[nav("BildAuf")]),
        make_qwertz_row(tab_width=1.5, iso_enter=True, extra_right=[nav("BildAb")]),
        make_asdf_row(caps_width=1.75, extra_right=[nav("Pos1")]),
        make_shift_row(lshift_width=1.25, rshift_width=1.75, add_up_arrow=True),
        make_75pct_bottom(space_width=6.25),
    ]
)

# ---------------------------------------------------------------------------
# 12. MOD 007 HE Year of Dragon — 75%, ~82 keys (same layout as MOD007B)
# ---------------------------------------------------------------------------
register(
    "akko-mod007-year-of-dragon-iso",
    {
        "name": "Akko MOD 007 HE Year of Dragon ISO",
        "vendor": "Akko",
        "form_factor": "75%",
        "approx_keys": 82,
        "iso_de": True,
        "has_encoder": False,
        "via_source": None,
        "sourcing_notes": "Premium alu 75%. Special edition. Same layout as MOD 007B HE ISO.",
    },
    rows=deepcopy(LAYOUTS["akko-mod007b-he-iso"]["rows"])
)

# ---------------------------------------------------------------------------
# 13. 5075B Plus VIA ISO (standard version, same PCB as #6) — kept separate
#     for clarity; this is the same product as #6 without "Blue on White"
# NOTE: already covered by #6. Kept as alias entry.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 14. Black & Gold 5087S ISO DE — 80% TKL, 87 keys
#     VIA source: akko-5087s-via-ansi.json (ANSI), adapted for ISO-DE
#     BS=2u, LShift=1.25u (ISO), RShift=2.75u, Space=6.25u
# ---------------------------------------------------------------------------
register(
    "akko-5087s-iso-de",
    {
        "name": "Akko Black & Gold 5087S ISO DE",
        "vendor": "Akko",
        "form_factor": "80% TKL",
        "approx_keys": 87,
        "iso_de": True,
        "has_encoder": False,
        "via_source": "akko-5087s-via-ansi.json",
        "sourcing_notes": (
            "Standard TKL sizes: Tab=1.5u, CapsLk=1.75u, BS=2u, LShift=1.25u, RShift=2.75u, Space=6.25u. "
            "VIA file is ANSI — ISO-DE layout derived from matrix structure. "
            "Full 6-key nav cluster (Einfg/Entf/Pos1/Ende/BildAuf/BildAb) + 4 arrows."
        ),
    },
    rows=[
        make_fn_row(extra_right=[nav("Druck"), nav("Rollen"), nav("Pause")]),
        make_number_row(bs_width=2.0, extra_right=[nav("Einfg"), nav("Pos1"), nav("BildAuf")]),
        make_qwertz_row(tab_width=1.5, iso_enter=True, extra_right=[nav("Entf"), nav("Ende"), nav("BildAb")]),
        make_asdf_row(caps_width=1.75),
        make_shift_row(lshift_width=1.25, rshift_width=2.75, add_up_arrow=True),
        make_tkl_bottom() + [nav("←"), nav("↓"), nav("→")],
    ]
)

# ---------------------------------------------------------------------------
# 15. Black & Gold 5098B — 96% compact, ~98 keys
# ---------------------------------------------------------------------------
register(
    "akko-5098b",
    {
        "name": "Akko Black & Gold 5098B",
        "vendor": "Akko",
        "form_factor": "96%",
        "approx_keys": 98,
        "iso_de": True,
        "has_encoder": False,
        "via_source": None,
        "sourcing_notes": (
            "96% compact: TKL + compact numpad merged into single block. "
            "Standard key sizes. BS=2u, LShift=1.25u, RShift=2.75u, Space=6.25u. "
            "Numpad: + and Enter are 2u tall (standard)."
        ),
    },
    rows=[
        # Fn row + numpad top
        make_fn_row(extra_right=[nav("Druck"), nav("Entf")]) + [num("NumLk"), num("/"), num("*"), num("-")],
        # Number row + numpad row 1
        make_number_row(bs_width=2.0, extra_right=[nav("Einfg"), nav("Pos1"), nav("BildAuf")]) + [num("7"), num("8"), num("9"), num("+", h=2.0)],
        # QWERTZ row + numpad row 2
        make_qwertz_row(tab_width=1.5, iso_enter=True, extra_right=[nav("Entf"), nav("Ende"), nav("BildAb")]) + [num("4"), num("5"), num("6")],
        # Home row + numpad row 3
        make_asdf_row(caps_width=1.75) + [num("1"), num("2"), num("3"), num("Enter", h=2.0)],
        # Shift row + numpad row 4 (Up + 0 + .)
        make_shift_row(lshift_width=1.25, rshift_width=2.75, add_up_arrow=True) + [num("0", w=2.0), num(".")],
        # Bottom row + arrows
        make_fullsize_bottom() + [nav("←"), nav("↓"), nav("→")],
    ]
)

# ---------------------------------------------------------------------------
# 16. 5098B with Screen — 96%, ~98 keys (same layout as 5098B)
# ---------------------------------------------------------------------------
register(
    "akko-5098b-screen",
    {
        "name": "Akko 5098B with Screen",
        "vendor": "Akko",
        "form_factor": "96%",
        "approx_keys": 98,
        "iso_de": True,
        "has_encoder": False,
        "via_source": None,
        "sourcing_notes": "Same layout as 5098B. Additional small display on keyboard body (not a keycap).",
    },
    rows=deepcopy(LAYOUTS["akko-5098b"]["rows"])
)

# ---------------------------------------------------------------------------
# 17. Black & Gold 5108B Plus ISO — 100% full-size, 108 keys
# ---------------------------------------------------------------------------
register(
    "akko-5108b-plus-iso",
    {
        "name": "Akko Black & Gold 5108B Plus ISO",
        "vendor": "Akko",
        "form_factor": "100%",
        "approx_keys": 108,
        "iso_de": True,
        "has_encoder": False,
        "via_source": None,
        "sourcing_notes": (
            "Full ISO-DE keyboard. Standard sizes. BS=2u, LShift=1.25u, RShift=2.75u, Space=6.25u. "
            "Full 6-key nav cluster + 4 arrows + full numpad. "
            "Numpad +: 2u tall; Numpad Enter: 2u tall; Numpad 0: 2u wide."
        ),
    },
    rows=[
        make_fn_row(extra_right=[nav("Druck"), nav("Rollen"), nav("Pause")]),
        make_number_row(bs_width=2.0, extra_right=[nav("Einfg"), nav("Pos1"), nav("BildAuf"), num("NumLk"), num("/"), num("*"), num("-")]),
        make_qwertz_row(tab_width=1.5, iso_enter=True, extra_right=[nav("Entf"), nav("Ende"), nav("BildAb"), num("7"), num("8"), num("9"), num("+", h=2.0)]),
        make_asdf_row(caps_width=1.75, extra_right=[num("4"), num("5"), num("6")]),
        make_shift_row(lshift_width=1.25, rshift_width=2.75, add_up_arrow=True, extra_right=[num("1"), num("2"), num("3"), num("Enter", h=2.0)]),
        make_fullsize_bottom() + [nav("←"), nav("↓"), nav("→"), num("0", w=2.0), num(".")],
    ]
)


# ===========================================================================
# OUTPUT: Individual Layout JSON Files
# ===========================================================================

def key_to_dict(key):
    """Clean up key dict for output."""
    if isinstance(key, dict) and "gap" in key:
        return key
    return {k: v for k, v in key.items() if v is not None}

def write_layout_json(model_id: str, layout: dict):
    """Write a single layout JSON file."""
    vendor = layout["vendor"].lower().replace(" ", "-")
    out_dir = LAYOUTS_DIR / vendor
    out_dir.mkdir(parents=True, exist_ok=True)

    # Build output structure
    out = {
        "id": model_id,
        "name": layout["name"],
        "vendor": layout["vendor"],
        "form_factor": layout["form_factor"],
        "approx_keys": layout["approx_keys"],
        "total_keycaps": layout["total_keycaps"],
        "iso_de": layout["iso_de"],
        "has_encoder": layout["has_encoder"],
        "via_source": layout.get("via_source"),
        "sourcing_notes": layout.get("sourcing_notes", ""),
        "rows": [],
    }

    profile_names = ["R1", "R2", "R3", "R4", "R5", "R5"]  # extra for bottom row ext
    for i, row in enumerate(layout["rows"]):
        row_out = {
            "row_index": i,
            "kle_profile": profile_names[min(i, len(profile_names)-1)],
            "keys": [key_to_dict(key) for key in row],
        }
        out["rows"].append(row_out)

    out_path = out_dir / f"{model_id}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    return out_path


# ===========================================================================
# INVENTORY DERIVATION
# ===========================================================================

def keycap_signature(key: dict) -> tuple:
    """
    Unique identifier for a keycap TYPE.
    For inventory: what matters is (label, w, h, shape).
    """
    return (
        key.get("label", ""),
        key.get("w", 1.0),
        key.get("h", 1.0),
        key.get("shape", "standard"),
    )

def derive_inventory(layouts: dict) -> dict:
    """
    Union of all keycaps across all models.
    Returns: {signature: {keycap_info + models_list}}
    """
    inventory = {}

    for model_id, layout in layouts.items():
        for row_i, row in enumerate(layout["rows"]):
            for key in row:
                if not isinstance(key, dict) or "label" not in key:
                    continue
                if key.get("type") == "encoder":
                    continue

                sig = keycap_signature(key)
                if sig not in inventory:
                    inventory[sig] = {
                        "label": key["label"],
                        "w": key.get("w", 1.0),
                        "h": key.get("h", 1.0),
                        "type": key.get("type", "alpha"),
                        "shape": key.get("shape", "standard"),
                        "models": [],
                        "model_count": 0,
                    }
                if model_id not in inventory[sig]["models"]:
                    inventory[sig]["models"].append(model_id)
                    inventory[sig]["model_count"] += 1

    return inventory

def write_inventory(inventory: dict):
    """Write keycap inventory as structured JSON."""
    INVENTORY_DIR.mkdir(parents=True, exist_ok=True)

    # Group by type and size
    by_type = {}
    for sig, info in inventory.items():
        t = info["type"]
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(info)

    # Sort within each type
    for t in by_type:
        by_type[t].sort(key=lambda x: (-x["model_count"], x["label"], x["w"]))

    # Non-standard sizes summary
    non_standard = {
        "unique_widths": sorted(set(v["w"] for v in inventory.values())),
        "unique_heights": sorted(set(v["h"] for v in inventory.values())),
        "iso_enter_variants": [
            {"sig": list(sig), **info}
            for sig, info in inventory.items()
            if info["shape"] == "iso_enter"
        ],
        "large_keys": [
            {"label": v["label"], "w": v["w"], "h": v["h"], "models": v["models"]}
            for v in inventory.values()
            if v["w"] >= 1.5 or v["h"] > 1.0
        ],
    }

    # Sort large keys by width desc
    non_standard["large_keys"].sort(key=lambda x: (-x["w"], -x["h"], x["label"]))

    # Space bar variants (critical for sourcing)
    space_variants = {
        v["w"]: v["models"]
        for v in inventory.values()
        if v["label"] == "Space"
    }

    # Full inventory list (sorted by type, then width, then label)
    all_keycaps = sorted(
        inventory.values(),
        key=lambda x: (x["type"], -x["w"], x["label"])
    )

    out = {
        "_meta": {
            "generated": "2026-04-14",
            "models_covered": len(LAYOUTS),
            "total_unique_keycap_types": len(inventory),
            "note": "Union of all keycap types across all 17 Akko/MonsGeek ISO-DE models.",
        },
        "summary": {
            "total_unique_types": len(inventory),
            "unique_widths_u": non_standard["unique_widths"],
            "iso_enter_shapes": [i["shape"] for i in non_standard["iso_enter_variants"]],
            "space_bar_variants_u": sorted(space_variants.keys()),
            "space_bar_by_width": {
                f"{w}u": models for w, models in sorted(space_variants.items())
            },
            "non_standard_highlights": [
                {"issue": "Tab=1.75u (non-standard)", "models": ["akko-5075b-plus-via-iso", "akko-5075b-plus-blue-on-white-iso"]},
                {"issue": "CapsLk=2u (non-standard)", "models": ["akko-5075b-plus-via-iso", "akko-5075b-plus-blue-on-white-iso"]},
                {"issue": "Space=6.5u (non-standard)", "models": ["monsgeek-m1v5-via-iso", "akko-mu02-iso-de", "akko-mu01-iso-de"]},
            ],
        },
        "by_type": by_type,
        "non_standard_sizes": non_standard,
        "all_keycaps": all_keycaps,
    }

    # Summary statistics
    print("\n=== KEYCAP INVENTORY SUMMARY ===")
    print(f"Models covered:          {len(LAYOUTS)}")
    print(f"Total unique cap types:  {len(inventory)}")
    print(f"Unique widths (u):       {non_standard['unique_widths']}")
    print(f"Space bar variants:      {sorted(space_variants.keys())} u")
    print(f"\n--- NON-STANDARD SIZES (sourcing challenges) ---")
    for issue in out["summary"]["non_standard_highlights"]:
        print(f"  [!] {issue['issue']}")
        for m in issue["models"]:
            print(f"       -> {m}")
    print()

    out_path = INVENTORY_DIR / "keycap-inventory.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    # Also write a compact CSV for quick reference
    csv_path = INVENTORY_DIR / "keycap-inventory.csv"
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("label,width_u,height_u,type,shape,model_count,models\n")
        for item in all_keycaps:
            models_str = "|".join(item["models"])
            f.write(f'"{item["label"]}",{item["w"]},{item["h"]},{item["type"]},{item["shape"]},{item["model_count"]},"{models_str}"\n')

    return out_path, csv_path


# ===========================================================================
# MAIN
# ===========================================================================

if __name__ == "__main__":
    print("=== Keyboard Layout Mapper ===")
    print(f"Writing layout files to: {LAYOUTS_DIR}")

    layout_files = []
    for model_id, layout in LAYOUTS.items():
        path = write_layout_json(model_id, layout)
        layout_files.append(path)
        print(f"  [OK] {model_id} -> {path.name}")

    print(f"\nTotal layouts written: {len(layout_files)}")

    print("\nDeriving keycap inventory...")
    inventory = derive_inventory(LAYOUTS)

    inv_json, inv_csv = write_inventory(inventory)
    print(f"  [OK] {inv_json}")
    print(f"  [OK] {inv_csv}")

    print("\nDone.")
