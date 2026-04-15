# Keycap Design Workflow — Instructions for Claude Code

## Overview

This repo contains keycap design files for the Keycap-Shop project. The primary design is "The Well — 呪", a dark horror-themed ISO-DE keycap set.

## Key Files

```
docs/
  keycap-layouts-iso-de.html      # Interactive keyboard layout viewer
  the-well-design-document.docx   # English design doc for manufacturer
  the-well-design-document-CN.docx # Chinese translation for manufacturer
  keycap-complete-reference-EN.pdf # Layout reference (8 pages)
scripts/
  recolor_template.py             # PDF color replacement tool
templates/
  GK75-German-Tigry-original.pdf  # Manufacturer template (DO NOT MODIFY)
  GK75-TheWell-v3.pdf             # The Well colorized version
designs/
  the-well/                       # The Well design assets
```

## Color Scheme: The Well — 呪

### Keycap Base Colors (fill)

| Group      | Hex       | PDF RGB                          | Keys                              |
|------------|-----------|----------------------------------|-----------------------------------|
| Alphas     | #161820   | 0.086275 0.094118 0.125490      | A-Z, 0-9, Umlauts, symbols       |
| Modifiers  | #1E2830   | 0.117647 0.156863 0.188235      | Strg, Alt, Win, Fn, Tab, Caps, Shift, ⟵ |
| F-Keys     | #1C2228   | 0.109804 0.133333 0.156863      | F1-F12, Entf                     |
| Navigation | #1A2530   | 0.101961 0.145098 0.188235      | Bild↑, Bild↓, Pos1, Ende        |
| Accents    | #C8D0D8   | 0.784314 0.815686 0.847059      | Esc, ↵ Enter, ↑↓←→              |
| Spacebar   | #BCC6D0   | 0.737255 0.776471 0.815686      | Space 6.5u                       |

### Legend Colors (text)

| Group            | Hex       | Applied to                       |
|------------------|-----------|----------------------------------|
| Alpha legends    | #8899AA   | Main chars on alpha keys         |
| Modifier legends | #5A7A90   | Modifier key labels              |
| F-Key legends    | #4A6070   | F1-F12, Entf labels              |
| Accent legends   | #2A3540   | Esc, Enter, arrow labels         |
| AltGr legends    | #3A6A8A   | ², ³, {, [, ], }, \, @, €, µ, ~, | |

## recolor_template.py — How It Works

The manufacturer sends PDF templates created in Adobe Illustrator. These contain vector keycap shapes with RGB fill colors in the PDF content streams.

### Color replacement process:
1. Open PDF with `pikepdf` (preserves file integrity)
2. Decompress all content streams and XObjects
3. Find RGB fill operations like `0.961 0.957 0.922 rg`
4. Replace with target scheme values: `0.086275 0.094118 0.125490 rg`
5. Save — pikepdf handles recompression and cross-reference tables

### Usage:
```bash
# Analyze colors in a template
python3 scripts/recolor_template.py templates/GK75-original.pdf --analyze output.pdf

# Apply The Well scheme
python3 scripts/recolor_template.py templates/GK75-original.pdf templates/GK75-TheWell.pdf --scheme the-well
```

### Adding a new color scheme:
Edit `recolor_template.py` → `SCHEMES` dict. Map template color keys to target hex values.

### Adding a new manufacturer template:
1. Analyze: `python3 recolor_template.py new-template.pdf dummy.pdf --analyze`
2. Add color values to `TEMPLATE_*` dict in the script
3. Map keys in your scheme's `mapping` dict

## CRITICAL RULES

### DO NOT change:
- Key labels/legends (Esc, Strg, Bild↑, Pos1, Ende, ß, ü, ö, ä — these are German ISO-DE)
- Key positions or sizes (these come from the manufacturer template)
- Hex color codes (these are the exact design spec)
- AltGr characters (², ³, {, [, ], }, \, @, €, µ, ~, |)

### Float precision matters:
- Use 6 decimal places for PDF RGB values
- `#161820` = `0.086275 0.094118 0.125490` (NOT `0.086 0.094 0.125` — that rounds to #15171F)
- Always verify hex roundtrip: `int(round(float_val * 255))` must match target

### Template colors (GK75 Tigry):
```
#F5F4EB = 0.961 0.957 0.922   (Alpha - white/cream)
#E4B57B = 0.898 0.71 0.486    (Accent - orange)
#EBB885 = 0.925 0.725 0.525   (Accent - lighter orange)
#A4CEC3 = 0.647 0.808 0.765   (Accent - mint/Enter)
#8B8B8A = 0.549 0.549 0.545   (Modifier - mid grey)
#828486 = 0.51 0.518 0.529    (Modifier - grey variant)
#6B6C6C = 0.42 0.424 0.427    (F-keys - darker grey)
#53555A = 0.329 0.337 0.353   (Navigation - dark grey)
#4B4B4B = 0.298 0.298 0.298   (Navigation - darkest)
#A4A4A4 = 0.647 0.647 0.647   (Arrows - light grey)
#AA1616 = 0.667 0.09 0.09     (Dolch red accent)
```

## Phase 2: Shine-Through Horror Elements (PENDING manufacturer confirmation)

These require vector artwork per keycap, delivered as separate SVG/AI layer:
- **Hair strands**: F,G,H,J keys — thin translucent lines (~0.3mm)
- **Well ring**: Spacebar — concentric circles
- **Sadako silhouette**: ISO Enter — crouching figure in L-shape
- **Hidden Kanji**: ESC→呪, D→死, Space→井
- **Water drops**: 6-8 random alpha keys — small droplet shapes
- **VHS lines**: F1-F12 — horizontal wavy distortion lines
