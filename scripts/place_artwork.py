"""
place_artwork.py — Place sliced artwork PNGs into a PDF keycap template

Reads key positions from keycap-coordinate-map.json and places
each <KEY_NAME>.png from the source directory onto the matching key face.

Usage:
    py -3 scripts/place_artwork.py \\
        --input  templates/GK75-TheWell-v7.pdf \\
        --tiles  icons/fkey \\
        --group  fkey \\
        --output templates/GK75-TheWell-v8.pdf

    py -3 scripts/place_artwork.py --help

Notes:
    - Tiles must be named <KEY_NAME>.png  (e.g. F1.png, F2.png ...)
    - Missing tiles are skipped with a warning (no error)
    - Uses PyMuPDF insert_image with clip rect from coordinate map
    - Preserves CMYK stroke paths (no redaction, pure overlay)
"""

import argparse
import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent
COORD_MAP = REPO / "layouts" / "keycap-coordinate-map.json"


def load_coord_map() -> dict:
    with open(COORD_MAP, encoding="utf-8") as f:
        return json.load(f)


def keys_for_group(coord_map: dict, group: str) -> list:
    return [k for k in coord_map["keys"] if k["group"] == group]


def place_artwork(input_pdf: Path, tiles_dir: Path, group: str, output_pdf: Path) -> int:
    try:
        import fitz
    except ImportError:
        print("ERROR: PyMuPDF not installed. Run: py -3 -m pip install pymupdf", file=sys.stderr)
        sys.exit(1)

    coord_map = load_coord_map()
    keys = keys_for_group(coord_map, group)
    if not keys:
        print(f"ERROR: No keys for group '{group}'", file=sys.stderr)
        print(f"  Available: {sorted(set(k['group'] for k in coord_map['keys']))}")
        sys.exit(1)

    doc = fitz.open(str(input_pdf))
    page = doc[0]

    placed = 0
    skipped = 0
    for key in keys:
        tile_path = tiles_dir / f"{key['name']}.png"
        if not tile_path.exists():
            print(f"  SKIP  {key['name']:6s}: {tile_path.name} not found")
            skipped += 1
            continue

        rect = fitz.Rect(key["x0"], key["y0"], key["x1"], key["y1"])
        page.insert_image(rect, filename=str(tile_path), overlay=True)
        size_kb = tile_path.stat().st_size // 1024
        print(f"  PLACE {key['name']:6s}: {rect}  ← {tile_path.name} ({size_kb} KB)")
        placed += 1

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_pdf), garbage=4, deflate=True)
    doc.close()

    size_kb = output_pdf.stat().st_size // 1024
    print(f"\nOutput: {output_pdf}  ({size_kb} KB)")
    print(f"Placed: {placed}  Skipped: {skipped}")
    return placed


def main():
    p = argparse.ArgumentParser(description="Place artwork tiles into PDF template")
    p.add_argument("--input",   required=True, help="Input PDF path")
    p.add_argument("--tiles",   required=True, help="Directory with <KEY_NAME>.png tiles")
    p.add_argument("--group",   required=True, help="Key group (fkey, alpha, mod, accent, nav)")
    p.add_argument("--output",  required=True, help="Output PDF path")
    args = p.parse_args()

    def resolve(p_str: str) -> Path:
        p = Path(p_str)
        return p if p.is_absolute() else REPO / p

    input_pdf  = resolve(args.input)
    tiles_dir  = resolve(args.tiles)
    output_pdf = resolve(args.output)

    if not input_pdf.exists():
        print(f"ERROR: Input PDF not found: {input_pdf}", file=sys.stderr)
        sys.exit(1)
    if not tiles_dir.exists():
        print(f"ERROR: Tiles dir not found: {tiles_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"place_artwork")
    print(f"  Input  : {input_pdf}")
    print(f"  Tiles  : {tiles_dir}")
    print(f"  Group  : {args.group}")
    print(f"  Output : {output_pdf}")
    print()

    place_artwork(input_pdf, tiles_dir, args.group, output_pdf)
    print("\nDone.")


if __name__ == "__main__":
    main()
