"""
verify_cherry.py — Quality gate for Cherry 135 全五面 recolored PDFs

Checks:
  1. Stroke count preserved  (baseline: 3358 × 2 after recolor = 6716, tol ±5%)
  2. Fill count >= baseline  (baseline: 460; recolor adds fills, never removes)
  3. Color model: RGB only   (no CMYK fills)
  4. File size < 2 MB
  5. Original stroke geometry present  (re-emitted strokes must be black)
  6. Per-key coverage: all keys in key-design.json have at least one fill  (optional)
  7. Palette colors present: all body colors from palette.yaml appear in fills  (optional)

Exit 0 = all checks passed
Exit 1 = one or more checks failed

Usage:
    py -3 scripts/verify_cherry.py templates/terminal-v2-cherry-v2.pdf
    py -3 scripts/verify_cherry.py templates/terminal-v2-cherry-v2.pdf --baseline-strokes 6716
    py -3 scripts/verify_cherry.py templates/terminal-v2-cherry-v2.pdf \\
        --design terminal-v2 \\
        --coord-map layouts/cherry-135-coordinate-map.json

    # Base-kit mode: also verifies non-included keys retain original template color
    py -3 scripts/verify_cherry.py templates/terminal-v2-cherry-v3.pdf \\
        --design terminal-v2 \\
        --include designs/_shared/75-iso-de-base-kit.yaml
"""

import argparse
import io
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent


def load_include_set(include_path: Path) -> set[str]:
    """Load a base-kit YAML and return the set of included key IDs."""
    try:
        import yaml
        with open(include_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except ImportError:
        print("ERROR: PyYAML required for --include. pip install pyyaml", file=sys.stderr)
        sys.exit(1)
    include_groups = data.get("include") or {}
    ids: set[str] = set()
    for group_ids in include_groups.values():
        for kid in (group_ids or []):
            ids.add(str(kid))
    return ids

# Baseline from template analysis (2026-04-21, 7-group full recolor)
BASELINE_FILLS_ORIGINAL = 460       # fills in the original Cherry template
BASELINE_STROKES_ORIGINAL = 3358    # strokes in the original Cherry template
# After a full 7-group recolor: 201 new fills + 2551 new strokes (re-emitted)
# Allow ±5% tolerance on stroke count
STROKE_TOLERANCE_PCT = 5.0
# Cherry PDFs with per-key legends embed font files (JetBrains Mono + Segoe UI Symbol).
# Segoe UI Symbol alone adds ~1.3 MB compressed (full font, no subsetting in PyMuPDF).
# Limit is for raster detection only — a PDF above 4 MB likely contains embedded images.
MAX_FILE_SIZE_KB = 4096


def rgb_float_to_hex(r, g, b) -> str:
    return "#{:02X}{:02X}{:02X}".format(round(r * 255), round(g * 255), round(b * 255))


def analyze(pdf_path: Path) -> dict:
    try:
        import fitz
    except ImportError:
        print("ERROR: PyMuPDF not installed.", file=sys.stderr)
        sys.exit(1)

    doc = fitz.open(str(pdf_path))
    page = doc[0]
    drawings = page.get_drawings()

    fills, strokes = [], []
    cmyk_fills = 0

    for d in drawings:
        has_fill = bool(d.get("fill") and len(d["fill"]) >= 3)
        has_stroke = bool(d.get("color") and len(d["color"]) >= 3)
        cs = d.get("colorspace")

        if has_fill:
            fills.append(d)
            if cs is not None and "cmyk" in str(cs).lower():
                cmyk_fills += 1
        if has_stroke and not has_fill:
            strokes.append(d)

    stroke_colors = set()
    for s in strokes:
        c = s["color"][:3]
        stroke_colors.add(rgb_float_to_hex(*c))

    doc.close()
    size_kb = pdf_path.stat().st_size // 1024

    return {
        "total": len(drawings),
        "fills": len(fills),
        "strokes": len(strokes),
        "cmyk_fills": cmyk_fills,
        "stroke_colors": stroke_colors,
        "size_kb": size_kb,
    }


def check(label: str, passed: bool, detail: str = "") -> bool:
    status = "PASS" if passed else "FAIL"
    line = f"  [{status}] {label}"
    if detail:
        line += f"  — {detail}"
    print(line)
    return passed


def check_per_key_coverage(
    pdf_path: Path,
    design_dir: Path,
    coord_map_path: Path,
    include_set: "set[str] | None" = None,
) -> tuple[int, list]:
    """Strict per-key check: every key in key-design.json has a correctly-colored body fill.

    'Correctly colored' means the topmost large fill (area > 500pt²) in the key bbox
    is NOT the original template color (no beige #C9C1AA-family remains as top fill).
    Palette body colors must appear as the topmost body fill for each key.

    When include_set is provided (base-kit mode), also checks that keys NOT in the
    include set still carry their original template fill_hex (they should be untouched).

    Returns (failures_count, list_of_wrong_key_ids).
    """
    import json
    import colorsys

    key_design_path = design_dir / "key-design.json"
    palette_path    = design_dir / "palette.yaml"
    if not key_design_path.exists():
        print(f"  SKIP Per-key coverage: key-design.json not found in {design_dir}")
        return 0, []
    if not coord_map_path.exists():
        print(f"  SKIP Per-key coverage: coord map not found at {coord_map_path}")
        return 0, []

    with open(key_design_path, encoding="utf-8") as f:
        key_design = json.load(f)
    with open(coord_map_path, encoding="utf-8") as f:
        coord_map = json.load(f)

    # Load expected body colors from palette
    palette_body: dict[str, tuple] = {}
    if palette_path.exists():
        try:
            import yaml
            with open(palette_path, encoding="utf-8") as f:
                raw = yaml.safe_load(f)
        except ImportError:
            raw = {}
            with open(palette_path, encoding="utf-8") as f:
                for line in f:
                    s = line.strip()
                    if s and not s.startswith("#") and ":" in s:
                        k, _, v = s.partition(":")
                        raw[k.strip()] = v.strip().strip('"').strip("'")
        colors = raw.get("colors") or raw
        for k, v in colors.items():
            if k.startswith("body_"):
                h = str(v).lstrip("#")
                palette_body[k] = (int(h[0:2],16)/255, int(h[2:4],16)/255, int(h[4:6],16)/255)

    key_bboxes   = {k["id"]: k for k in coord_map["keys"]}
    key_body_ref = {kid: spec.get("body_color","body_alpha")
                    for kid, spec in key_design.get("keys",{}).items()}

    try:
        import fitz
    except ImportError:
        print("  SKIP Per-key coverage: PyMuPDF not available")
        return 0, []

    doc = fitz.open(str(pdf_path))
    page = doc[0]
    drawings = list(page.get_drawings())
    doc.close()

    def center_in_bbox(rect, key, margin=2.0):
        cx = (rect.x0 + rect.x1) / 2
        cy = (rect.y0 + rect.y1) / 2
        return (key["x0"]-margin) <= cx <= (key["x1"]+margin) and (key["y0"]-margin) <= cy <= (key["y1"]+margin)

    def color_match(c1: tuple, c2: tuple, tol: float = 15/255) -> bool:
        return all(abs(a - b) <= tol for a, b in zip(c1, c2))

    wrong: list[str] = []
    uncovered: list[str] = []
    total_keys = len(key_design.get("keys", {}))

    for key_id, spec in key_design.get("keys", {}).items():
        key_meta = key_bboxes.get(key_id)
        if key_meta is None:
            continue

        # Gather fills in this key's bbox, keep only large ones (body fills)
        body_fills = []
        for i, d in enumerate(drawings):
            if not (d.get("fill") and len(d["fill"]) >= 3 and d.get("rect")):
                continue
            r = d["rect"]
            area = (r.x1 - r.x0) * (r.y1 - r.y0)
            if area < 500:
                continue
            if center_in_bbox(r, key_meta):
                body_fills.append((i, tuple(d["fill"][:3])))

        if not body_fills:
            uncovered.append(key_id)
            continue

        # Topmost large fill (highest stream index) = what the viewer renders on top
        topmost_color = max(body_fills, key=lambda x: x[0])[1]

        # Check it matches the expected palette body color
        body_ref = key_body_ref.get(key_id, "body_alpha")
        expected = palette_body.get(body_ref)
        if expected is not None and not color_match(topmost_color, expected):
            wrong.append(key_id)

    failed = wrong + uncovered
    total_ok = total_keys - len(failed)
    passed = len(failed) == 0
    detail = f"{total_ok}/{total_keys} keys correctly colored"
    if uncovered:
        detail += f"; no fills: {uncovered[:5]}"
    if wrong:
        detail += f"; wrong color: {wrong[:5]}" + (" ..." if len(wrong) > 5 else "")
    check("Per-key body colors match palette (strict)", passed, detail)
    total_failures = 0 if passed else 1

    # Base-kit mode: non-included keys must retain their original template fill_hex
    if include_set is not None:
        non_included = [k for k in coord_map["keys"] if k["id"] not in include_set]
        wrong_originals: list[str] = []
        for key_meta in non_included:
            key_id = key_meta["id"]
            orig_hex = key_meta.get("fill_hex", "")
            if not orig_hex:
                continue
            body_fills = []
            for i, d in enumerate(drawings):
                if not (d.get("fill") and len(d["fill"]) >= 3 and d.get("rect")):
                    continue
                r = d["rect"]
                area = (r.x1 - r.x0) * (r.y1 - r.y0)
                if area < 500:
                    continue
                if center_in_bbox(r, key_meta):
                    body_fills.append((i, tuple(d["fill"][:3])))
            if not body_fills:
                continue
            topmost = max(body_fills, key=lambda x: x[0])[1]
            h = orig_hex.lstrip("#")
            expected = (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255)
            if not color_match(topmost, expected, tol=20 / 255):
                wrong_originals.append(key_id)
        non_ok = len(non_included) - len(wrong_originals)
        non_passed = len(wrong_originals) == 0
        non_detail = f"{non_ok}/{len(non_included)} non-included keys retain original color"
        if wrong_originals:
            non_detail += f"; recolored unexpectedly: {wrong_originals[:5]}"
            if len(wrong_originals) > 5:
                non_detail += " ..."
        check("Non-included keys retain original template color (base-kit)", non_passed, non_detail)
        if not non_passed:
            total_failures += 1

    return total_failures, failed


def check_palette_colors(pdf_path: Path, design_dir: Path) -> int:
    """Check that body colors from palette.yaml appear in the PDF fills."""
    import json

    palette_path = design_dir / "palette.yaml"
    if not palette_path.exists():
        return 0

    try:
        import yaml
        with open(palette_path, encoding="utf-8") as f:
            raw = yaml.safe_load(f)
    except ImportError:
        raw = {}
        with open(palette_path, encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if s and not s.startswith("#") and ":" in s:
                    k, _, v = s.partition(":")
                    v = v.strip().strip('"').strip("'")
                    if v:
                        raw[k.strip()] = v

    colors_raw = raw.get("colors") or raw
    body_colors = {k: v for k, v in colors_raw.items() if k.startswith("body_")}
    if not body_colors:
        return 0

    try:
        import fitz
    except ImportError:
        return 0

    doc = fitz.open(str(pdf_path))
    page = doc[0]
    fill_hexes = set()
    for d in page.get_drawings():
        f = d.get("fill")
        if f and len(f) >= 3:
            fill_hexes.add("#{:02X}{:02X}{:02X}".format(
                round(f[0] * 255), round(f[1] * 255), round(f[2] * 255)))
    doc.close()

    TOL = 10
    failures = 0
    for ref, hex_val in body_colors.items():
        h = str(hex_val).lstrip("#")
        tr, tg, tb = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        found = any(
            all(abs(int(fh[i*2+1:i*2+3], 16) - [tr, tg, tb][i]) <= TOL for i in range(3))
            for fh in fill_hexes
        )
        passed = check(f"Palette color {ref} ({hex_val}) present in fills", found,
                       "" if found else f"nearest miss among {len(fill_hexes)} unique fills")
        if not passed:
            failures += 1
    return failures


def main():
    p = argparse.ArgumentParser(description="Quality gate for Cherry 135 recolored PDFs")
    p.add_argument("pdf", help="Path to the recolored PDF to verify")
    p.add_argument("--baseline-strokes", type=int, default=None,
                   help="Expected stroke count after recolor (default: auto = original × 2)")
    p.add_argument("--baseline-fills", type=int, default=BASELINE_FILLS_ORIGINAL,
                   help=f"Minimum fill count (default: {BASELINE_FILLS_ORIGINAL})")
    p.add_argument("--design", default=None,
                   help="Design name (e.g. terminal-v2) — enables per-key checks 6+7")
    p.add_argument("--coord-map", default=str(REPO / "layouts" / "cherry-135-coordinate-map.json"),
                   help="Coordinate map JSON for per-key coverage check")
    p.add_argument("--include", default=None,
                   help="Path to base-kit YAML (e.g. designs/_shared/75-iso-de-base-kit.yaml). "
                        "Enables base-kit mode: additionally checks non-included keys are untouched.")
    args = p.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.is_absolute():
        pdf_path = REPO / pdf_path
    if not pdf_path.exists():
        print(f"ERROR: File not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    print(f"verify_cherry: {pdf_path.name}")
    print()

    stats = analyze(pdf_path)

    print(f"  Totals  : {stats['total']} drawings  "
          f"({stats['fills']} fills, {stats['strokes']} strokes)")
    print(f"  File    : {stats['size_kb']} KB")
    print()

    failures = 0

    # 1. Stroke count: after full recolor, strokes ≈ original + re-emitted
    #    Minimum: original strokes must be preserved (at least 1× baseline)
    #    Maximum: no more than 2× + tolerance (sanity cap)
    expected_min_strokes = BASELINE_STROKES_ORIGINAL
    expected_max_strokes = BASELINE_STROKES_ORIGINAL * 2 + BASELINE_STROKES_ORIGINAL * STROKE_TOLERANCE_PCT / 100

    if args.baseline_strokes is not None:
        tol = int(args.baseline_strokes * STROKE_TOLERANCE_PCT / 100)
        stroke_ok = abs(stats["strokes"] - args.baseline_strokes) <= tol
        detail = (f"{stats['strokes']} vs expected {args.baseline_strokes} "
                  f"(±{tol})")
    else:
        stroke_ok = expected_min_strokes <= stats["strokes"] <= expected_max_strokes
        detail = (f"{stats['strokes']}  "
                  f"(must be {expected_min_strokes}–{int(expected_max_strokes)})")

    if not check("Stroke count in valid range", stroke_ok, detail):
        failures += 1

    # 2. Fill count: recolor only adds fills, never removes
    fill_ok = stats["fills"] >= args.baseline_fills
    if not check("Fill count >= baseline",
                 fill_ok,
                 f"{stats['fills']} >= {args.baseline_fills}"):
        failures += 1

    # 3. Color model: no CMYK fills
    if not check("No CMYK fills (RGB only)",
                 stats["cmyk_fills"] == 0,
                 f"{stats['cmyk_fills']} CMYK fills found"):
        failures += 1

    # 4. File size (4 MB cap: Fonts add ~1.5 MB; > 4 MB = likely embedded raster)
    if not check("File size < 4 MB",
                 stats["size_kb"] < MAX_FILE_SIZE_KB,
                 f"{stats['size_kb']} KB"):
        failures += 1

    # 5. Re-emitted strokes are black (Cherry bevel lines)
    has_black_strokes = "#000000" in stats["stroke_colors"]
    if not check("Black strokes present (3D bevel lines)",
                 has_black_strokes,
                 f"stroke colors: {sorted(stats['stroke_colors'])}"):
        failures += 1

    # 6+7. Optional per-key checks (require --design)
    if args.design:
        design_dir = REPO / "designs" / args.design
        coord_map_path = Path(args.coord_map)
        if not coord_map_path.is_absolute():
            coord_map_path = REPO / coord_map_path

        # Load include set for base-kit mode
        include_set = None
        if args.include:
            include_path = Path(args.include)
            if not include_path.is_absolute():
                include_path = REPO / include_path
            include_set = load_include_set(include_path)
            print(f"  Base-kit mode: {len(include_set)} included keys, checking untouched remainder")

        print()
        cov_failures, _ = check_per_key_coverage(
            pdf_path, design_dir, coord_map_path, include_set=include_set
        )
        failures += cov_failures
        failures += check_palette_colors(pdf_path, design_dir)

    print()
    if failures == 0:
        print("RESULT: ALL CHECKS PASSED")
        sys.exit(0)
    else:
        print(f"RESULT: {failures} CHECK(S) FAILED — do not push this PDF")
        sys.exit(1)


if __name__ == "__main__":
    main()
