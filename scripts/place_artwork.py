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


def keys_for_group(coord_map: dict, group: str, exclude_ids: set = None) -> list:
    keys = [k for k in coord_map["keys"] if k["group"] == group]
    if exclude_ids:
        keys = [k for k in keys if k["id"] not in exclude_ids]
    return keys


def place_tiles(page, keys: list, tiles_dir: Path, use_id: bool = False) -> tuple:
    """Place tiles onto page. use_id=True looks for {key_id}.png, else {key_name}.png."""
    placed = 0
    skipped = 0
    try:
        import fitz
    except ImportError:
        pass  # fitz already imported by caller
    import fitz
    for key in keys:
        fname = f"{key['id']}.png" if use_id else f"{key['name']}.png"
        tile_path = tiles_dir / fname
        if not tile_path.exists():
            label = key["id"] if use_id else key["name"]
            print(f"  SKIP  {label}: {fname} not found")
            skipped += 1
            continue
        rect = fitz.Rect(key["x0"], key["y0"], key["x1"], key["y1"])
        page.insert_image(rect, filename=str(tile_path), overlay=True)
        size_kb = tile_path.stat().st_size // 1024
        label = key["id"] if use_id else key["name"]
        print(f"  PLACE {label}: {rect}  ← {fname} ({size_kb} KB)")
        placed += 1
    return placed, skipped


def place_artwork(input_pdf: Path, tiles_dir: Path, group: str, output_pdf: Path,
                  exclude_ids: set = None) -> int:
    try:
        import fitz
    except ImportError:
        print("ERROR: PyMuPDF not installed. Run: py -3 -m pip install pymupdf", file=sys.stderr)
        sys.exit(1)

    coord_map = load_coord_map()
    keys = keys_for_group(coord_map, group, exclude_ids)
    if not keys:
        print(f"ERROR: No keys for group '{group}'", file=sys.stderr)
        print(f"  Available: {sorted(set(k['group'] for k in coord_map['keys']))}")
        sys.exit(1)

    doc = fitz.open(str(input_pdf))
    page = doc[0]
    placed, skipped = place_tiles(page, keys, tiles_dir, use_id=False)

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_pdf), garbage=4, deflate=True)
    doc.close()
    size_kb = output_pdf.stat().st_size // 1024
    print(f"\nOutput: {output_pdf}  ({size_kb} KB)")
    print(f"Placed: {placed}  Skipped: {skipped}")
    return placed


def place_artwork_keys(input_pdf: Path, tiles_dir: Path, key_ids: list, output_pdf: Path) -> int:
    """Place tiles for specific key IDs (tiles named {key_id}.png)."""
    try:
        import fitz
    except ImportError:
        print("ERROR: PyMuPDF not installed. Run: py -3 -m pip install pymupdf", file=sys.stderr)
        sys.exit(1)

    coord_map = load_coord_map()
    keys_by_id = {k["id"]: k for k in coord_map["keys"]}
    keys = []
    for kid in key_ids:
        if kid not in keys_by_id:
            print(f"  WARN: key '{kid}' not in coordinate map — skipped")
        else:
            keys.append(keys_by_id[kid])

    doc = fitz.open(str(input_pdf))
    page = doc[0]
    placed, skipped = place_tiles(page, keys, tiles_dir, use_id=True)

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
    p.add_argument("--tiles",   required=True, help="Directory with tile PNGs")
    p.add_argument("--output",  required=True, help="Output PDF path")

    target = p.add_mutually_exclusive_group(required=True)
    target.add_argument("--group", help="Key group — tiles named {key_name}.png")
    target.add_argument("--keys",  help="Comma-separated key IDs — tiles named {key_id}.png")

    p.add_argument("--exclude", help="Comma-separated key IDs to skip (only with --group)")
    args = p.parse_args()

    if args.exclude and not args.group:
        p.error("--exclude requires --group")

    def resolve(p_str: str) -> Path:
        path = Path(p_str)
        return path if path.is_absolute() else REPO / path

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
    print(f"  Output : {output_pdf}")
    print()

    if args.keys:
        key_ids = [k.strip() for k in args.keys.split(",") if k.strip()]
        print(f"  Keys   : {key_ids}")
        place_artwork_keys(input_pdf, tiles_dir, key_ids, output_pdf)
    else:
        exclude_ids = set(args.exclude.split(",")) if args.exclude else None
        print(f"  Group  : {args.group}" + (f"  Exclude: {args.exclude}" if args.exclude else ""))
        place_artwork(input_pdf, tiles_dir, args.group, output_pdf, exclude_ids)

    print("\nDone.")


if __name__ == "__main__":
    main()
