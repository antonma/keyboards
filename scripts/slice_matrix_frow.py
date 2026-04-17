"""
slice_matrix_frow.py — Matrix F-Row Slicer
Schneidet ein Matrix-Artwork in 12 F-Tasten-Ausschnitte (F1–F12).

Usage:
  py -3 scripts/slice_matrix_frow.py [source_image]

  source_image  Pfad zum Quellbild (default: images/matrix4k.png)
                Bekannte Quellen:
                  images/matrix4k.png       6336×2688  → frow/
                  images/matrix-hor-8k.png  12288×4096 → frow-8k/

Logik:
  - Bild in 12 gleich breite Spalten teilen
  - Aus jeder Spalte: zentrierter quadratischer Crop (Spaltenbreite × Spaltenbreite)
  - Lanczos-Resize auf 868×868px (≈52.1pt @1200DPI, 2× Druckauflösung)
  - Output: images/frow[-8k]/matrix_F{n:02d}.png  (n = 1..12)
"""

import sys
import io
from pathlib import Path
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent

# Source: CLI-Arg oder Default
if len(sys.argv) > 1:
    SRC = Path(sys.argv[1])
    if not SRC.is_absolute():
        SRC = REPO / SRC
else:
    SRC = REPO / "images" / "matrix4k.png"

# Output-Ordner: frow-8k für 8K-Quellen, sonst frow
out_name = "frow-8k" if "8k" in SRC.stem.lower() else "frow"
OUT = REPO / "images" / out_name
OUT.mkdir(parents=True, exist_ok=True)

OUTPUT_SIZE = 868          # px — mind. 434, besser 868
NUM_KEYS    = 12

img = Image.open(SRC)
W, H = img.size
print(f"Quellbild: {SRC.name}  {W}×{H} {img.mode}")
print(f"Output:    {OUT}")

col_w   = W // NUM_KEYS
crop_sq = min(col_w, H)
x_off   = (col_w - crop_sq) // 2
y_off   = (H - crop_sq) // 2

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
    sz = fname.stat().st_size // 1024
    print(f"  F{n+1:>2}: x={x0}-{x1}  y={y0}-{y1}  → {fname.name}  ({sz} KB)")

print(f"\nFertig. {NUM_KEYS} Tiles in {OUT}")
