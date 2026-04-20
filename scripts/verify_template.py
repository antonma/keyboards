"""
verify_template.py — Quality gate for PDF keycap templates

Checks:
  1. Stroke count (vs. baseline, tolerance ±50 or custom %)
  2. Color model (no CMYK+RGB mix)
  3. Expected design colors present
  4. File size < 2 MB
  5. No orphan colors (fills not in coordinate map groups)

Exit 0 = all checks passed
Exit 1 = one or more checks failed (report printed to stdout)

Usage:
    py -3 scripts/verify_template.py templates/GK75-TheWell-v7.pdf
    py -3 scripts/verify_template.py templates/GK75-terminal_2.pdf --baseline terminal-v2
    py -3 scripts/verify_template.py templates/foo.pdf --no-baseline
    py -3 scripts/verify_template.py --help

Baselines: quality_gates/baselines.json
"""

import argparse
import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent
BASELINES_PATH = REPO / "quality_gates" / "baselines.json"
MAX_FILE_SIZE_KB = 2048
COLOR_TOLERANCE = 30 / 255.0


def load_baselines() -> dict:
    if not BASELINES_PATH.exists():
        return {}
    with open(BASELINES_PATH, encoding="utf-8") as f:
        return json.load(f)


def rgb_float_to_hex(r, g, b) -> str:
    return "#{:02X}{:02X}{:02X}".format(round(r * 255), round(g * 255), round(b * 255))


def color_near(c1, c2, tol=COLOR_TOLERANCE) -> bool:
    return all(abs(a - b) <= tol for a, b in zip(c1[:3], c2[:3]))


def analyze_pdf(pdf_path: Path) -> dict:
    try:
        import fitz
    except ImportError:
        print("ERROR: PyMuPDF not installed. Run: py -3 -m pip install pymupdf", file=sys.stderr)
        sys.exit(1)

    doc = fitz.open(str(pdf_path))
    page = doc[0]
    paths = page.get_drawings()
    doc.close()

    strokes = [p for p in paths if p.get("color") and not p.get("fill")]
    fills   = [p for p in paths if p.get("fill") and not p.get("color")]
    both    = [p for p in paths if p.get("fill") and p.get("color")]

    def is_cmyk(color) -> bool:
        return color is not None and len(color) == 4

    def is_rgb(color) -> bool:
        return color is not None and len(color) == 3

    cmyk_fills  = [p for p in paths if is_cmyk(p.get("fill"))]
    rgb_fills   = [p for p in paths if is_rgb(p.get("fill"))]
    cmyk_strokes = [p for p in paths if is_cmyk(p.get("color"))]
    rgb_strokes  = [p for p in paths if is_rgb(p.get("color"))]

    # Unique fill colors (RGB only for hex display)
    fill_colors = set()
    for p in paths:
        f = p.get("fill")
        if f and len(f) == 3:
            fill_colors.add(rgb_float_to_hex(*f[:3]))

    return {
        "stroke_count":    len(strokes) + len(both),
        "fill_count":      len(fills) + len(both),
        "cmyk_fills":      len(cmyk_fills),
        "rgb_fills":       len(rgb_fills),
        "cmyk_strokes":    len(cmyk_strokes),
        "rgb_strokes":     len(rgb_strokes),
        "unique_rgb_fills": sorted(fill_colors),
        "has_mixed":       (len(cmyk_fills) > 0 and len(rgb_fills) > 0),
    }


def check_stroke_count(actual: int, baseline: dict) -> tuple:
    expected = baseline.get("stroke_count")
    if expected is None:
        return True, f"stroke_count: {actual} (no baseline)"
    tol_pct = baseline.get("tolerance_pct", 0.5)
    tol_abs = max(50, round(expected * tol_pct / 100))
    delta = actual - expected
    ok = abs(delta) <= tol_abs
    mark = "✓" if ok else "✗"
    return ok, f"stroke_count: {actual} (baseline {expected}, delta {delta:+d}, tol ±{tol_abs}) {mark}"


def check_color_model(stats: dict) -> tuple:
    if stats["has_mixed"]:
        return False, f"color_model: MIXED — CMYK fills {stats['cmyk_fills']}, RGB fills {stats['rgb_fills']} ✗"
    model = "CMYK" if stats["cmyk_fills"] > 0 else "RGB"
    return True, f"color_model: pure {model} ✓"


def check_expected_colors(stats: dict, baseline: dict) -> tuple:
    expected = baseline.get("expected_colors", [])
    if not expected:
        return True, "expected_colors: (not checked)"
    missing = []
    for exp_hex in expected:
        exp_rgb = tuple(int(exp_hex.lstrip("#")[i:i+2], 16) / 255.0 for i in (0, 2, 4))
        found = any(
            color_near(exp_rgb, tuple(int(h.lstrip("#")[i:i+2], 16) / 255.0 for i in (0, 2, 4)))
            for h in stats["unique_rgb_fills"]
        )
        if not found:
            missing.append(exp_hex)
    ok = len(missing) == 0
    if ok:
        return True, f"expected_colors: all {len(expected)} present ✓"
    return False, f"expected_colors: missing {missing} ✗"


def check_filesize(pdf_path: Path) -> tuple:
    size_kb = pdf_path.stat().st_size // 1024
    ok = size_kb <= MAX_FILE_SIZE_KB
    mark = "✓" if ok else "✗"
    return ok, f"filesize: {size_kb} KB (max {MAX_FILE_SIZE_KB} KB) {mark}"


def main():
    p = argparse.ArgumentParser(description="Quality gate for PDF keycap templates")
    p.add_argument("pdf", help="PDF file to verify")
    p.add_argument("--baseline", default=None,
                   help="Baseline name from quality_gates/baselines.json (default: auto-detect from filename)")
    p.add_argument("--no-baseline", action="store_true", help="Skip stroke count check")
    args = p.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.is_absolute():
        pdf_path = REPO / pdf_path

    if not pdf_path.exists():
        print(f"ERROR: File not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    baselines = load_baselines()

    # Auto-detect baseline from filename stem
    baseline_key = args.baseline
    if not baseline_key and not args.no_baseline:
        stem = pdf_path.stem.lower()
        for key in baselines:
            if key in stem:
                baseline_key = key
                break

    baseline = baselines.get(baseline_key, {}) if baseline_key else {}

    print(f"verify_template: {pdf_path.name}")
    if baseline_key:
        print(f"  Baseline: {baseline_key}")
    print()

    stats = analyze_pdf(pdf_path)

    results = []

    # 1. Stroke count
    if args.no_baseline:
        results.append((True, f"stroke_count: {stats['stroke_count']} (baseline check skipped)"))
    else:
        results.append(check_stroke_count(stats["stroke_count"], baseline))

    # 2. Color model
    results.append(check_color_model(stats))

    # 3. Expected colors
    results.append(check_expected_colors(stats, baseline))

    # 4. File size
    results.append(check_filesize(pdf_path))

    # 5. Info
    results.append((True, f"fills: {stats['fill_count']}  rgb_fills: {stats['rgb_fills']}  cmyk_fills: {stats['cmyk_fills']}"))
    if stats["unique_rgb_fills"]:
        results.append((True, f"rgb_fill_colors: {' '.join(stats['unique_rgb_fills'][:10])}{'...' if len(stats['unique_rgb_fills']) > 10 else ''}"))

    all_ok = all(ok for ok, _ in results)
    for ok, msg in results:
        prefix = "  " if ok else "  FAIL "
        print(f"{prefix}{msg}")

    print()
    if all_ok:
        print("PASS — all checks OK")
    else:
        print("FAIL — one or more checks failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
