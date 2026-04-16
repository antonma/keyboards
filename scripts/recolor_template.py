#!/usr/bin/env python3
"""
Keycap Template Color Replacer
===============================
Replaces fill colors in a manufacturer's PDF keycap template with custom color schemes.
Uses pikepdf for proper PDF manipulation that preserves file integrity.

Usage:
    python3 recolor_template.py <input.pdf> <output.pdf> [--scheme the-well]

Requirements:
    pip install pikepdf

The manufacturer template (e.g. GK75-German-Tigry) uses Adobe Illustrator PDF format
with RGB fill colors in content streams. This script:
1. Decompresses all PDF content streams and XObjects
2. Finds RGB fill operations (e.g. "0.961 0.957 0.922 rg")
3. Replaces them with the target color scheme values
4. Recompresses and saves a valid PDF

The output PDF can be opened in:
- Adobe Illustrator (manufacturer's tool)
- Affinity Studio/Designer
- Any PDF viewer
"""

import argparse
import io
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    import pikepdf
except ImportError:
    print("ERROR: pikepdf required. Install with: pip install pikepdf")
    sys.exit(1)


def hex_to_pdf_rgb(hex_color: str) -> str:
    """Convert hex color (#RRGGBB) to PDF RGB float string with 6 decimal places."""
    r = int(hex_color[1:3], 16) / 255.0
    g = int(hex_color[3:5], 16) / 255.0
    b = int(hex_color[5:7], 16) / 255.0
    return f"{r:.6f} {g:.6f} {b:.6f}"


def pdf_rgb_to_hex(r: float, g: float, b: float) -> str:
    """Convert PDF RGB floats to hex color."""
    return f"#{int(round(r*255)):02X}{int(round(g*255)):02X}{int(round(b*255)):02X}"


# =============================================================================
# COLOR SCHEMES
# =============================================================================

# GK75 Tigry template original colors (extracted from PDF)
TEMPLATE_TIGRY = {
    "alpha":      "0.961 0.957 0.922",   # #F5F4EB (white/cream)
    "accent1":    "0.898 0.71 0.486",     # #E4B57B (orange)
    "accent2":    "0.925 0.725 0.525",    # #EBB885 (lighter orange)
    "accent3":    "0.647 0.808 0.765",    # #A4CEC3 (mint/green - Enter)
    "mod1":       "0.549 0.549 0.545",    # #8B8B8A (mid grey)
    "mod2":       "0.51 0.518 0.529",     # #828486 (grey variant)
    "fkey":       "0.42 0.424 0.427",     # #6B6C6C (darker grey)
    "nav1":       "0.329 0.337 0.353",    # #53555A (dark grey)
    "nav2":       "0.298 0.298 0.298",    # #4B4B4B (darkest grey)
    "arrows":     "0.647 0.647 0.647",    # #A4A4A4 (light grey)
    "dolch_red":  "0.667 0.09 0.09",      # #AA1616 (Dolch red accent)
}

# The Well — 呪 color scheme
SCHEME_THE_WELL = {
    "name": "The Well — 呪",
    "description": "Dark horror keycap set inspired by The Ring/Ringu",
    "mapping": {
        # Template color key → target hex
        "alpha":     "#161820",  # Deep black (dark water, TV static)
        "accent1":   "#C8D0D8",  # Ghostly pale white (Sadako's skin)
        "accent2":   "#C8D0D8",  # Ghostly pale white
        "accent3":   "#C8D0D8",  # Ghostly pale white (Enter)
        "mod1":      "#1E2830",  # Dark teal-grey (waterlogged stone)
        "mod2":      "#1E2830",  # Dark teal-grey
        "fkey":      "#1C2228",  # VHS blue-grey (tape distortion)
        "nav1":      "#1A2530",  # Dark teal (deep well wall)
        "nav2":      "#1A2530",  # Dark teal
        "arrows":    "#C8D0D8",  # Ghostly pale white
        "dolch_red": "#3A6A8A",  # AltGr blue (cold water reflection) - night mode variant
    },
    "legend_colors": {
        "alpha_legends":    "#8899AA",  # Ghostly grey
        "modifier_legends": "#5A7A90",  # Muted blue
        "fkey_legends":     "#4A6070",  # Muted steel
        "accent_legends":   "#2A3540",  # Dark charcoal
        "altgr_legends":    "#3A6A8A",  # Deep blue (cold water)
    },
    "special": {
        "spacebar": "#BCC6D0",  # Pale white (well opening, ripples)
        "rotary":   "#161820",  # Same as alphas
    }
}

# Terminal — 💀 Hacker Retro / Vintage CRT
SCHEME_TERMINAL = {
    "name": "Terminal — Hacker Retro",
    "description": "Vintage CRT/Phosphor terminal aesthetic. Single-accent (phosphor green) on near-black bodies. Inspired by IBM 5151, VT100, hacker-retro renderings.",
    "mapping": {
        # Backgrounds: alle nahezu schwarz mit minimalem Grün-Tint.
        # Zwei sehr nahe Farbtöne damit Mods/F-Keys sich subtil von Alphas absetzen.
        "alpha":     "#0F1410",  # Phosphor-Black (Alpha-Hauptfläche, Spacebar, Enter)
        "accent1":   "#0F1410",  # gleich Alpha (kein Amber-Akzent — Mono-Body)
        "accent2":   "#0F1410",  # gleich Alpha
        "accent3":   "#0F1410",  # Enter — gleich Alpha (Akzent kommt durch Phosphor-Legend)
        "mod1":      "#181D18",  # Mod-Body (Shift, Ctrl, Win, Alt, Tab, Caps, Backspace, Fn)
        "mod2":      "#181D18",  # Mod-Variant — gleich
        "fkey":      "#181D18",  # F-Keys — gleich Mods (KEIN Amber)
        "nav1":      "#181D18",  # Nav-Cluster (Bild↑, Bild↓, Pos1, Ende, Entf)
        "nav2":      "#181D18",  # Nav-Variant
        "arrows":    "#0F1410",  # Pfeiltasten — wie Alphas (Phosphor-Pfeile)
        "dolch_red": "#0F1410",  # AltGr — wie Alphas (Phosphor-Legend macht den Akzent)
    },
    "legend_colors": {
        "alpha_legends":    "#3FFF3F",  # Phosphor Green (Hauptlabels)
        "modifier_legends": "#A8C8A8",  # Pale Grey-Green (Mods dezent, fast weiß)
        "fkey_legends":     "#3FFF3F",  # Phosphor Green (F-Keys leuchten)
        "accent_legends":   "#3FFF3F",  # Phosphor Green (Enter, Esc)
        "altgr_legends":    "#3FFF3F",  # Phosphor Green (AltGr)
        "sub_legends":      "#1F6B1F",  # Dim Phosphor (Sonderzeichen unter Hauptlabel)
    },
    "special": {
        "spacebar":      "#0F1410",  # Phosphor-Black (später >_ Icon in Phosphor)
        "rotary":        "#0F1410",  # gleich Alphas
        "esc_icon":      "skull",    # Skull statt "Esc" Text (in Phosphor-Grün)
        "spacebar_icon": "prompt",   # >_ Prompt-Symbol in Phosphor-Grün
    }
}

# Oni Mask — 🎭 Schwarz-Rot-Gold Samurai
# Verifiziertes Slot-Mapping (2026-04-16, audit_tigry_slots.py):
#   alpha    (#F5F4EB): Alphas, Zahlenreihe, Spacebar, F1-F4, F9-F12  → DUNKEL
#   accent1  (#E5B57C): ESC + alle Pfeiltasten (← ↑ ↓ →)              → GOLD
#   accent2  (#ECB986): Zweites Design F1-Akzent                       → GOLD (passend zu accent1)
#   accent3  (#A5CEC3): ENTER (ISO-DE Mint → einzige Enter-Farbe!)     → GOLD
#   mod1     (#8C8C8B): Rotary/Nav-Taste (rechts F-Key-Zeile)          → ROT
#   mod2     (#828487): ALLE Mods (Tab, Caps, Shift, Ctrl, Win, Alt,   → ROT
#                       Fn, AltGr, Backspace) + F5-F8 + Nav-Cluster
#   fkey     (#6B6C6D): Zweites Design F5-F8 (spiegelt mod2)           → ROT
#   nav1     (#54565A): Nav-Background-Fläche (groß)                   → NAVY (Body)
#   nav2     (#4C4C4C): Keyboard-Hintergrund (allergrößte Fläche)      → NAVY (Body)
#   arrows   (#A5A5A5): Zweites Design Alphas                          → DUNKEL
#   dolch_red(#AA1717): Zweites Design ESC (Dolch-Akzent)              → GOLD
#
# LIMITIERUNG: Spacebar teilt den 'alpha'-Slot mit Alphas →
#   Spacebar wird DUNKEL (nicht Gold wie im V2 ADR).
#   Dies entspricht Antons manueller Referenz-Datei (omni-mask_v1.pdf).
SCHEME_ONI_MASK = {
    "name": "Oni Mask — 鬼",
    "description": "Schwarz-Rot-Gold Samurai. Ideogram V2 K-Means Palette. Verifiziert via PDF-Stream-Analyse 2026-04-16.",
    "mapping": {
        "alpha":     "#1B1D20",   # Alphas, Spacebar, Num row, F1-F4, F9-F12 → Dunkel
        "accent1":   "#A88B63",   # ESC + Pfeiltasten → Gold
        "accent2":   "#A88B63",   # 2nd-Design Akzent → Gold (spiegelt accent1)
        "accent3":   "#A88B63",   # ENTER (einziger Schlüssel in diesem Slot) → Gold
        "mod1":      "#6F2D2C",   # Rotary/Nav-Sondertaste → Rot
        "mod2":      "#6F2D2C",   # Alle Mods + F5-F8 → Rot
        "fkey":      "#6F2D2C",   # 2nd-Design F5-F8 → Rot (spiegelt mod2)
        "nav1":      "#1B2230",   # Nav-Background → Navy (Keyboard-Körper)
        "nav2":      "#1B2230",   # Keyboard-Hintergrund → Navy (Keyboard-Körper)
        "arrows":    "#1B1D20",   # 2nd-Design Alphas → Dunkel (spiegelt alpha)
        "dolch_red": "#A88B63",   # 2nd-Design ESC → Gold (spiegelt accent1)
    },
    "legend_colors": {
        # Legends werden per PyMuPDF overdraw (apply_legend_colors.py) gesetzt,
        # NICHT per recolor_template.py. Diese Werte sind nur Referenz.
        "on_dark":    "#A88B63",   # Gold auf Schwarz (Alphas, F-Keys)
        "on_red":     "#DDC096",   # Champagner auf Rot (Mods)
        "on_gold":    "#1B1D20",   # Schwarz auf Gold (ESC, Enter, Pfeile)
        "sub_legend": "#7A6444",   # Gedämpftes Gold (Sub-Legends)
    },
}

# Add more schemes here as needed
SCHEMES = {
    "the-well": SCHEME_THE_WELL,
    "terminal": SCHEME_TERMINAL,
    "oni-mask": SCHEME_ONI_MASK,
}


def build_color_map(template_colors: dict, scheme: dict) -> dict:
    """Build a bytes→bytes replacement map from template colors to scheme colors."""
    color_map = {}
    for key, target_hex in scheme["mapping"].items():
        if key in template_colors:
            old_val = template_colors[key].encode()
            new_val = hex_to_pdf_rgb(target_hex).encode()
            color_map[old_val + b' rg'] = new_val + b' rg'
    return color_map


def process_stream(stream_obj, color_map: dict) -> int:
    """Process a single PDF stream, replacing colors. Returns count of replacements."""
    replacements = 0
    try:
        raw = stream_obj.read_bytes()
        modified = raw
        for old, new in color_map.items():
            count = modified.count(old)
            if count > 0:
                modified = modified.replace(old, new)
                replacements += count
        if modified != raw:
            stream_obj.write(modified)
    except Exception:
        pass
    return replacements


def recolor_pdf(input_path: str, output_path: str, scheme_name: str = "the-well") -> dict:
    """
    Recolor a manufacturer PDF template with a custom color scheme.
    
    Returns dict with stats about what was changed.
    """
    if scheme_name not in SCHEMES:
        raise ValueError(f"Unknown scheme '{scheme_name}'. Available: {list(SCHEMES.keys())}")
    
    scheme = SCHEMES[scheme_name]
    color_map = build_color_map(TEMPLATE_TIGRY, scheme)
    
    pdf = pikepdf.open(input_path)
    total_replacements = 0
    
    for page in pdf.pages:
        # Process page content streams
        if '/Contents' in page:
            contents = page['/Contents']
            streams = list(contents) if isinstance(contents, pikepdf.Array) else [contents]
            for s in streams:
                total_replacements += process_stream(s, color_map)
        
        # Process Form XObjects (many Illustrator PDFs use these)
        if '/Resources' in page and '/XObject' in page['/Resources']:
            for name, xobj in page['/Resources']['/XObject'].items():
                total_replacements += process_stream(xobj, color_map)
    
    pdf.save(output_path)
    pdf.close()
    
    # Verify output
    verify_pdf = pikepdf.open(output_path)
    output_colors = set()
    for page in verify_pdf.pages:
        for source in _get_all_streams(page):
            try:
                data = source.read_bytes().decode('latin-1')
                for m in re.finditer(r'([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+rg\b', data):
                    r, g, b = float(m.group(1)), float(m.group(2)), float(m.group(3))
                    output_colors.add(pdf_rgb_to_hex(r, g, b))
            except Exception:
                pass
    verify_pdf.close()
    
    return {
        "scheme": scheme_name,
        "scheme_display_name": scheme["name"],
        "replacements": total_replacements,
        "output_colors": sorted(output_colors),
        "input": input_path,
        "output": output_path,
    }


def _get_all_streams(page):
    """Get all content streams and XObject streams from a page."""
    streams = []
    if '/Contents' in page:
        contents = page['/Contents']
        streams.extend(list(contents) if isinstance(contents, pikepdf.Array) else [contents])
    if '/Resources' in page and '/XObject' in page['/Resources']:
        for name, xobj in page['/Resources']['/XObject'].items():
            streams.append(xobj)
    return streams


def extract_colors(pdf_path: str) -> dict:
    """Extract all unique fill colors from a PDF. Useful for analyzing new templates."""
    pdf = pikepdf.open(pdf_path)
    colors = set()
    
    for page in pdf.pages:
        for source in _get_all_streams(page):
            try:
                data = source.read_bytes().decode('latin-1')
                for m in re.finditer(r'([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+rg\b', data):
                    r, g, b = float(m.group(1)), float(m.group(2)), float(m.group(3))
                    hex_c = pdf_rgb_to_hex(r, g, b)
                    colors.add((hex_c, m.group(0)))
            except Exception:
                pass
    
    pdf.close()
    return {hex_c: raw for hex_c, raw in sorted(colors)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recolor keycap manufacturer PDF templates")
    parser.add_argument("input", help="Input PDF path (manufacturer template)")
    parser.add_argument("output", help="Output PDF path")
    parser.add_argument("--scheme", default="the-well", choices=list(SCHEMES.keys()),
                       help="Color scheme to apply (default: the-well)")
    parser.add_argument("--analyze", action="store_true",
                       help="Just analyze and print colors in the input PDF")
    
    args = parser.parse_args()
    
    if args.analyze:
        print(f"Analyzing colors in: {args.input}\n")
        colors = extract_colors(args.input)
        for hex_c, raw in colors.items():
            print(f"  {hex_c}  ←  {raw} rg")
        print(f"\nTotal unique fill colors: {len(colors)}")
    else:
        print(f"Recoloring: {args.input}")
        print(f"Scheme: {args.scheme}")
        print(f"Output: {args.output}\n")
        
        result = recolor_pdf(args.input, args.output, args.scheme)
        
        print(f"✓ {result['replacements']} color replacements made")
        print(f"✓ Output colors: {result['output_colors']}")
        print(f"✓ Saved to: {result['output']}")
