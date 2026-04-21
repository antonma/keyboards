"""
recolor.py — Group-based keycap recolor using coordinate map

Overdraw strategy: draws new filled paths on top of existing paths.
Supports both CMYK (GK75) and RGB (Cherry 135) templates via PyMuPDF.

Two recolor modes:
  solid      — overdraw all fills in group with one flat target colour
  hue_shift  — shift hue+saturation of each fill by the delta between the
               group's median-luminance colour and the target; luminance
               preserved → 3D shading depth intact (useful for Cherry RGB)

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

    # Cherry RGB with hue_shift:
    py -3 scripts/recolor.py \\
        --input     "templates/135 Cherry 全五面.pdf" \\
        --coord-map layouts/cherry-135-coordinate-map.json \\
        --mode      hue_shift \\
        --ops       alpha:body:#161820 mod:body:#1E2830 \\
        --output    templates/cherry-terminal-v2-wip.pdf

    py -3 scripts/recolor.py --help

Notes:
    - Coordinate map field 'color_model' controls driver selection (CMYK/RGB)
    - Color tolerance for source-fill matching: ±30/255 per channel
    - --mode applies to all ops in a single call; mix modes via multiple calls
"""

import argparse
import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent
DEFAULT_COORD_MAP = REPO / "layouts" / "keycap-coordinate-map.json"
COLOR_TOLERANCE = 30


def load_coord_map(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
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
    return [(k["x0"], k["y0"], k["x1"], k["y1"]) for k in keys_for_group(coord_map, group)]


def rect_contains_center(path_rect, key_rect, margin: float = 2.0) -> bool:
    try:
        import fitz
        pr = path_rect
        cx = (pr.x0 + pr.x1) / 2
        cy = (pr.y0 + pr.y1) / 2
        kx0, ky0, kx1, ky1 = key_rect
        return (kx0 - margin) <= cx <= (kx1 + margin) and (ky0 - margin) <= cy <= (ky1 + margin)
    except Exception:
        return False


def gather_group_paths(page, group: str, coord_map: dict) -> list:
    key_bboxes = group_bboxes(coord_map, group)
    return [
        p for p in page.get_drawings()
        if p.get("fill") and len(p["fill"]) >= 3 and p.get("rect") is not None
        and any(rect_contains_center(p["rect"], kb) for kb in key_bboxes)
    ]


def build_hue_shift_map(paths: list, target_rgb: tuple) -> dict:
    """Map path id → shifted RGB.  Median-luminance fill is the reference colour."""
    import colorsys

    fills = [tuple(p["fill"][:3]) for p in paths]
    if not fills:
        return {}
    sorted_by_lum = sorted(fills, key=lambda c: colorsys.rgb_to_hls(*c)[1])
    ref_rgb = sorted_by_lum[len(sorted_by_lum) // 2]

    def shift(src: tuple) -> tuple:
        rh, rl, rs = colorsys.rgb_to_hls(*ref_rgb)
        th, tl, ts = colorsys.rgb_to_hls(*target_rgb)
        sh, sl, ss = colorsys.rgb_to_hls(*src[:3])
        new_h = (sh + (th - rh)) % 1.0
        new_s = max(0.0, min(1.0, ss + (ts - rs)))
        return colorsys.hls_to_rgb(new_h, sl, new_s)

    return {id(p): shift(tuple(p["fill"][:3])) for p in paths}


def gather_group_stroke_paths(page, group: str, coord_map: dict) -> list:
    """Stroke-only paths within group key bboxes (no fill)."""
    key_bboxes = group_bboxes(coord_map, group)
    return [
        p for p in page.get_drawings()
        if p.get("color") and len(p["color"]) >= 3
        and not (p.get("fill") and len(p.get("fill", [])) >= 3)
        and p.get("rect") is not None
        and any(rect_contains_center(p["rect"], kb) for kb in key_bboxes)
    ]


def re_emit_strokes(page, stroke_paths: list):
    """Re-draw stroke paths on top to restore Z-order after fill overdraw."""
    shape = page.new_shape()
    for path in stroke_paths:
        sc = path.get("color")
        if not sc or len(sc) < 3:
            continue
        for item in path.get("items", []):
            if item[0] == "l":    shape.draw_line(item[1], item[2])
            elif item[0] == "c":  shape.draw_bezier(item[1], item[2], item[3], item[4])
            elif item[0] == "re": shape.draw_rect(item[1])
            elif item[0] == "qu": shape.draw_quad(item[1])
        shape.finish(
            fill=None,
            color=sc[:3],
            width=path.get("width", 0.5),
            even_odd=False,
        )
    shape.commit()


def apply_recolor(doc, group: str, color_hex: str, coord_map: dict,
                  mode: str = "solid", restore_strokes: bool = False) -> int:
    import fitz

    page = doc[0]
    group_paths = gather_group_paths(page, group, coord_map)
    if not group_paths:
        print(f"  WARN: No fill paths found for group '{group}'")
        return 0

    # Gather stroke paths BEFORE overdraw — get_drawings() re-parses the
    # content stream, and freshly committed shapes can trip MuPDF's parser.
    _stroke_paths_snapshot = gather_group_stroke_paths(page, group, coord_map) if restore_strokes else []

    target_rgb = hex_to_rgb_float(color_hex)

    if mode == "hue_shift":
        color_map = build_hue_shift_map(group_paths, target_rgb)
    else:
        color_map = {id(p): target_rgb for p in group_paths}

    shape = page.new_shape()
    count = 0

    for path in group_paths:
        color = color_map.get(id(path))
        if color is None:
            continue
        for item in path.get("items", []):
            if item[0] == "l":    shape.draw_line(item[1], item[2])
            elif item[0] == "c":  shape.draw_bezier(item[1], item[2], item[3], item[4])
            elif item[0] == "re": shape.draw_rect(item[1])
            elif item[0] == "qu": shape.draw_quad(item[1])
        shape.finish(
            fill=color,
            color=None,
            even_odd=path.get("even_odd", True),
        )
        count += 1

    shape.commit()

    # Cherry RGB: re-emit pre-gathered strokes on top.
    if restore_strokes and _stroke_paths_snapshot:
        re_emit_strokes(page, _stroke_paths_snapshot)

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
    p.add_argument("--input",     required=True, help="Input PDF path")
    p.add_argument("--output",    required=True, help="Output PDF path")
    p.add_argument("--group",     help="Key group (alpha, mod, fkey, accent, nav, num, spacebar)")
    p.add_argument("--property",  choices=["body"], default="body",
                   help="What to recolor: body (default)")
    p.add_argument("--color",     help="Target color hex (e.g. #161820)")
    p.add_argument("--ops",       nargs="+",
                   help="Multiple operations: group:property:#RRGGBB ...")
    p.add_argument("--mode",      choices=["solid", "hue_shift"], default="solid",
                   help="solid: flat overdraw (default). hue_shift: preserve 3D shading (Cherry RGB).")
    p.add_argument("--coord-map", default=str(DEFAULT_COORD_MAP),
                   help="Path to coordinate map JSON (default: layouts/keycap-coordinate-map.json)")
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
    coord_map_path = resolve(args.coord_map)

    if not input_pdf.exists():
        print(f"ERROR: Input PDF not found: {input_pdf}", file=sys.stderr)
        sys.exit(1)
    if not coord_map_path.exists():
        print(f"ERROR: Coord map not found: {coord_map_path}", file=sys.stderr)
        sys.exit(1)

    coord_map = load_coord_map(coord_map_path)
    ops = parse_ops(args.ops) if args.ops else [(args.group, args.property, args.color)]
    restore_strokes = coord_map.get("color_model", "CMYK").upper() == "RGB"

    print(f"recolor")
    print(f"  Input     : {input_pdf}")
    print(f"  Output    : {output_pdf}")
    print(f"  Coord map : {coord_map_path.name}")
    print(f"  Mode      : {args.mode}")
    print(f"  Ops       : {len(ops)}")
    print(f"  Restore strokes: {restore_strokes}")
    print()

    import fitz
    doc = fitz.open(str(input_pdf))

    for group, prop, color in ops:
        count = apply_recolor(doc, group, color, coord_map, mode=args.mode,
                              restore_strokes=restore_strokes)
        print(f"  {group:12s} {prop:6s} → {color}  ({count} paths overdrawn)")

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_pdf), garbage=4, deflate=True)
    doc.close()

    size_kb = output_pdf.stat().st_size // 1024
    print(f"\nOutput: {output_pdf}  ({size_kb} KB)")
    print("Done.")


if __name__ == "__main__":
    main()
