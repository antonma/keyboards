"""
apply_per_key_design.py — Apply a per-key design spec to a PDF template

Reads:
  - designs/<design>/palette.yaml      (color palette)
  - designs/<design>/fonts.yaml        (font stack)
  - designs/<design>/key-design.json   (per-key spec)

Applies per key:
  1. Body color recolor (via PdfRgbDriver.recolor_key)
  2. Legend text overlay (via PdfRgbDriver.set_legend)

Usage:
    py -3 scripts/apply_per_key_design.py \\
        --design terminal-v2 \\
        --input  "templates/135 Cherry 全五面.pdf" \\
        --output templates/terminal-v2-cherry-v2.pdf

    py -3 scripts/apply_per_key_design.py \\
        --design terminal-v2 \\
        --input  "templates/135 Cherry 全五面.pdf" \\
        --output templates/terminal-v2-cherry-v2.pdf \\
        --mode   luminance_aware_shift \\
        --no-legends
"""

import argparse
import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent
DEFAULT_COORD_MAP = REPO / "layouts" / "cherry-135-coordinate-map.json"


def load_yaml(path: Path) -> dict:
    try:
        import yaml
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except ImportError:
        pass
    # Minimal fallback — only key: value pairs (no nested dicts)
    result = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if ":" in stripped:
                k, _, v = stripped.partition(":")
                v = v.strip().strip('"').strip("'")
                if v:
                    result[k.strip()] = v
    return result


def load_palette(design_dir: Path) -> dict:
    """Return {color_ref: (r, g, b)} from palette.yaml."""
    raw = load_yaml(design_dir / "palette.yaml")
    colors = raw.get("colors") or raw  # handle nested or flat YAML
    palette = {}
    for k, v in colors.items():
        h = str(v).lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        palette[k] = (r / 255.0, g / 255.0, b / 255.0)
    return palette


def load_fonts(design_dir: Path) -> dict:
    """Return {font_ref: resolved_path_str} from fonts.yaml."""
    raw = load_yaml(design_dir / "fonts.yaml")
    fonts_raw = raw.get("fonts") or {}
    result = {}
    for ref, spec in fonts_raw.items():
        if isinstance(spec, dict):
            file_path = spec.get("file", "")
        else:
            file_path = str(spec)
        if file_path:
            p = Path(file_path)
            if not p.is_absolute():
                p = REPO / p
            result[ref] = str(p) if p.exists() else ""
        else:
            result[ref] = ""
    return result


def rgb_tuple_to_hex(r: float, g: float, b: float) -> str:
    return "#{:02X}{:02X}{:02X}".format(round(r * 255), round(g * 255), round(b * 255))


def main():
    p = argparse.ArgumentParser(description="Apply per-key design spec to a Cherry PDF template")
    p.add_argument("--design",     required=True, help="Design name (e.g. terminal-v2)")
    p.add_argument("--input",      required=True, help="Input PDF template path")
    p.add_argument("--output",     required=True, help="Output PDF path")
    p.add_argument("--coord-map",  default=str(DEFAULT_COORD_MAP),
                   help="Coordinate map JSON (default: layouts/cherry-135-coordinate-map.json)")
    p.add_argument("--mode",
                   choices=["solid", "hue_shift", "luminance_aware_shift"],
                   default="luminance_aware_shift",
                   help="Recolor mode (default: luminance_aware_shift)")
    p.add_argument("--no-legends", action="store_true",
                   help="Skip legend text overlay (body color only)")
    p.add_argument("--keys", nargs="+",
                   help="Limit to specific key IDs (default: all keys)")
    args = p.parse_args()

    design_dir = REPO / "designs" / args.design
    if not design_dir.exists():
        print(f"ERROR: Design directory not found: {design_dir}", file=sys.stderr)
        sys.exit(1)

    key_design_path = design_dir / "key-design.json"
    if not key_design_path.exists():
        print(f"ERROR: key-design.json not found in {design_dir}", file=sys.stderr)
        print("  Run: py -3 scripts/generate_key_design.py --design " + args.design, file=sys.stderr)
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

    palette = load_palette(design_dir)
    fonts   = load_fonts(design_dir)

    with open(key_design_path, encoding="utf-8") as f:
        key_design = json.load(f)

    keys_spec: dict = key_design.get("keys", {})
    if args.keys:
        keys_spec = {k: v for k, v in keys_spec.items() if k in args.keys}

    print(f"apply_per_key_design")
    print(f"  Design    : {args.design}")
    print(f"  Input     : {input_pdf}")
    print(f"  Output    : {output_pdf}")
    print(f"  Mode      : {args.mode}")
    print(f"  Keys      : {len(keys_spec)}")
    print(f"  Legends   : {'off' if args.no_legends else 'on'}")
    print()

    try:
        import sys as _sys
        _sys.path.insert(0, str(REPO / "scripts"))
        from template_driver import TemplateDriver
    except ImportError as e:
        print(f"ERROR: Cannot import template_driver: {e}", file=sys.stderr)
        sys.exit(1)

    recolor_count = 0
    legend_count  = 0
    missing_keys  = []

    with TemplateDriver.for_template(input_pdf, coord_map_path) as drv:

        for key_id, spec in keys_spec.items():
            # ── Body color ────────────────────────────────────────────────────
            body_ref = spec.get("body_color", "body_alpha")
            body_rgb = palette.get(body_ref)
            if body_rgb is None:
                print(f"  WARN: palette key '{body_ref}' not found for key '{key_id}'")
                missing_keys.append(key_id)
                continue

            body_hex = rgb_tuple_to_hex(*body_rgb)
            n = drv.recolor_key(key_id, body_hex, mode=args.mode)
            if n == 0:
                missing_keys.append(key_id)
            else:
                recolor_count += n

            # ── Legend text ───────────────────────────────────────────────────
            if args.no_legends:
                continue

            legend_spec = spec.get("legend", {})
            main_raw = legend_spec.get("main")
            sub_raw  = legend_spec.get("sub")

            def resolve_legend(raw: dict | None) -> dict | None:
                if not raw or not raw.get("text"):
                    return None
                color_ref = raw.get("color", "legend_main")
                font_ref  = raw.get("font",  "primary")
                return {
                    "text":      raw["text"],
                    "color":     palette.get(color_ref, (0.32, 0.69, 0.36)),
                    "font_path": fonts.get(font_ref, ""),
                    "size":      raw.get("size", 18),
                }

            main = resolve_legend(main_raw)
            sub  = resolve_legend(sub_raw)

            if main or sub:
                drv.set_legend(key_id, main=main, sub=sub)
                legend_count += 1

        output_pdf.parent.mkdir(parents=True, exist_ok=True)
        drv.export(output_pdf)

    size_kb = output_pdf.stat().st_size // 1024
    print(f"  Recolored : {recolor_count} fill paths across {len(keys_spec) - len(missing_keys)} keys")
    print(f"  Legends   : {legend_count} keys")
    if missing_keys:
        print(f"  No fills found for {len(missing_keys)} keys: {missing_keys[:10]}"
              + (" ..." if len(missing_keys) > 10 else ""))
    print(f"\nOutput: {output_pdf}  ({size_kb} KB)")
    print("Done.")


if __name__ == "__main__":
    main()
