"""
slice_matrix_frow.py — Matrix 4K F-Row Slicer
Schneidet images/matrix4k.png in 12 F-Tasten-Ausschnitte (F1–F12).

Logik:
  - Bild: 6336×2688 RGB
  - 12 gleich breite Spalten → 528px je Spalte
  - Aus jeder Spalte: zentrierter quadratischer Crop 528×528
  - Lanczos-Resize auf 868×868px (≈52.1pt @1200DPI, 2× Druckauflösung)
  - Output: images/frow/matrix_F{n:02d}.png  (n = 1..12)
"""

import sys
import io
from pathlib import Path
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent
SRC  = REPO / "images" / "matrix4k.png"
OUT  = REPO / "images" / "frow"
OUT.mkdir(parents=True, exist_ok=True)

OUTPUT_SIZE = 868          # px — mind. 434, besser 868
NUM_KEYS    = 12

img = Image.open(SRC)
W, H = img.size
print(f"Quellbild: {W}×{H} {img.mode}")

col_w   = W // NUM_KEYS          # 528 px
crop_sq = min(col_w, H)          # 528 px (quadratisch)
x_off   = (col_w - crop_sq) // 2 # Horizontal-Zentrierung innerhalb der Spalte
y_off   = (H - crop_sq) // 2     # Vertikal-Zentrierung

print(f"Spaltenbreite: {col_w}px  →  Crop: {crop_sq}×{crop_sq}px  →  Output: {OUTPUT_SIZE}×{OUTPUT_SIZE}px")
print()

for n in range(NUM_KEYS):
    x0 = n * col_w + x_off
    y0 = y_off
    x1 = x0 + crop_sq
    y1 = y0 + crop_sq

    tile = img.crop((x0, y0, x1, y1))

    if tile.size != (OUTPUT_SIZE, OUTPUT_SIZE):
        tile = tile.resize((OUTPUT_SIZE, OUTPUT_SIZE), Image.LANCZOS)

    fname = OUT / f"matrix_F{n+1:02d}.png"
    tile.save(fname, "PNG", optimize=True)
    print(f"  F{n+1:>2}: x={x0}-{x1}  y={y0}-{y1}  → {fname.name}")

print(f"\nFertig. {NUM_KEYS} Tiles in {OUT}")
