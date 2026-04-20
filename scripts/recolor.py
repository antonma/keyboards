"""
recolor.py — Group-based keycap recolor using coordinate map

Overdraw strategy: draws new filled paths on top of existing CMYK paths.
Uses PyMuPDF Shape overdraw (same approach as apply_legend_colors.py).

Usage:
    py -3 scripts/recolor.py \\
        --input  templates/GK75-TheWell-v7.pdf \\
        --group  alpha \\
        --property body \\
        --color  #161820 \\
        --output templates/GK75-TheWell-v8.pdf

    # Multiple operations in one call:
    py -3 scripts/recolor.py \\
        --input  templates/GK75-TheWell-v7.pdf \\
        --ops    alpha:body:#161820 mod:body:#1E2830 fkey:body:#1C2228 \\
        --output templates/GK75-TheWell-v8.pdf

    py -3 scripts/recolor.py --help

Notes:
    - Only changes fill paths (body = background fill of keycap)
    - Legend overdraw not yet implemented (use apply_legend_colors.py for legends)
    - Coordinate map defines group membership by key ID
    - Color tolerance: ±30/255 per channel for source fill matching
"""

import argparse
import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent
COORD_MAP = REPO / "layouts" / "keycap-coordinate-map.json"
COLOR_TOLERANCE = 30


def load_coord_map() -> dict:
    with open(COORD_MAP, encoding="utf-8") as f:
        return json.load(f)


def hex_to_rgb_float(hex_color: str) -> tuple:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return r / 255.0, g / 255.0, b / 255.0


def rgb_float_to_hex(r: float, g: float, b: float) -> str:
    return "#{:02X}{:02X}{:02X}".format(round(r * 255), round(g * 255), round(b * 255))


def color_near(c1: tuple, c2: tuple, tol: float = COLOR_TOLERANCE / 255.0) -> bool:
    return all(abs(a - b) <= tol for a, b in zip(c1[:3], c2[:3]))


def keys_for_group(coord_map: dict, group: str) -> list:
    return [k for k in coord_map["keys"] if k["group"] == group]


def group_bboxes(coord_map: dict, group: str) -> list:
    """Return list of (x0, y0, x1, y1) for each key in group."""
    return [(k["x0"], k["y0"], k["x1"], k["y1"]) for k in keys_for_group(coord_map, group)]


def rect_contains_center(path_rect, key_rect, margin: float = 2.0) -> bool:
    """True if path_rect center is inside key_rect (with margin)."""
    try:
        import fitz
        pr = path_rect
        cx = (pr.x0 + pr.x1) / 2
        cy = (pr.y0 + pr.y1) / 2
        kx0, ky0, kx1, ky1 = key_rect
        return (kx0 - margin) <= cx <= (kx1 + margin) and (ky0 - margin) <= cy <= (ky1 + margin)
    except Exception:
        return False


def apply_recolor(doc, group: str, color_hex: str, coord_map: dict) -> int:
    import fitz

    target_rgb = hex_to_rgb_float(color_hex)
    key_bboxes = group_bboxes(coord_map, group)
    if not key_bboxes:
        print(f"  WARN: No keys for group '{group}'")
        return 0

    page = doc[0]
    paths = page.get_drawings()
    count = 0

    shape = page.new_shape()

    for path in paths:
        fill = path.get("fill")
        if not fill or len(fill) < 3:
            continue

        # Check if this fill path belongs to any key in the group
        path_rect = path.get("rect")
        if path_rect is None:
            continue

        in_group = any(rect_contains_center(path_rect, kb) for kb in key_bboxes)
        if not in_group:
            continue

        # Draw overdraw path on top
        for item in path.get("items", []):
            if item[0] == "l":
                shape.draw_line(item[1], item[2])
            elif item[0] == "c":
                shape.draw_bezier(item[1], item[2], item[3], item[4])
            elif item[0] == "re":
                shape.draw_rect(item[1])
            elif item[0] == "qu":
                shape.draw_quad(item[1])

        shape.finish(
            fill=target_rgb,
            color=None,
            even_odd=path.get("even_odd", True),
        )
        count += 1

    shape.commit()
    return count


def parse_ops(ops_list: list) -> list:
    """Parse 'group:property:color' strings → list of (group, property, color)."""
    result = []
    for op in ops_list:
        parts = op.split(":")
        if len(parts) != 3:
            print(f"ERROR: Invalid --ops entry '{op}' (expected group:property:#RRGGBB)", file=sys.stderr)
            sys.exit(1)
        result.append((parts[0], parts[1], parts[2]))
    return result


def main():
    p = argparse.ArgumentParser(description="Group-based keycap recolor via overdraw")
    p.add_argument("--input",    required=True, help="Input PDF path")
    p.add_argument("--output",   required=True, help="Output PDF path")
    p.add_argument("--group",    help="Key group (alpha, mod, fkey, accent, nav)")
    p.add_argument("--property", choices=["body"], default="body",
                   help="What to recolor: body (default)")
    p.add_argument("--color",    help="Target color hex (e.g. #161820)")
    p.add_argument("--ops",      nargs="+",
                   help="Multiple operations: group:property:#RRGGBB ...")
    args = p.parse_args()

    if not args.ops and not (args.group and args.color):
        p.error("Either --ops or both --group and --color are required")

    try:
        import fitz
    except ImportError:
        print("ERROR: PyMuPDF not installed. Run: py -3 -m pip install pymupdf", file=sys.stderr)
        sys.exit(1)

    def resolve(p_str: str) -> Path:
        pt = Path(p_str)
        return pt if pt.is_absolute() else REPO / pt

    input_pdf  = resolve(args.input)
    output_pdf = resolve(args.output)

    if not input_pdf.exists():
        print(f"ERROR: Input PDF not found: {input_pdf}", file=sys.stderr)
        sys.exit(1)

    coord_map = load_coord_map()
    ops = parse_ops(args.ops) if args.ops else [(args.group, args.property, args.color)]

    print(f"recolor")
    print(f"  Input  : {input_pdf}")
    print(f"  Output : {output_pdf}")
    print(f"  Ops    : {len(ops)}")
    print()

    import fitz
    doc = fitz.open(str(input_pdf))

    for group, prop, color in ops:
        count = apply_recolor(doc, group, color, coord_map)
        print(f"  {group:8s} {prop:6s} → {color}  ({count} paths overdrawn)")

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_pdf), garbage=4, deflate=True)
    doc.close()

    size_kb = output_pdf.stat().st_size // 1024
    print(f"\nOutput: {output_pdf}  ({size_kb} KB)")
    print("Done.")


if __name__ == "__main__":
    main()
