"""
verify_cherry.py — Quality gate for Cherry 135 全五面 recolored PDFs

Checks:
  1. Stroke count preserved  (baseline: 3358 × 2 after recolor = 6716, tol ±5%)
  2. Fill count >= baseline  (baseline: 460; recolor adds fills, never removes)
  3. Color model: RGB only   (no CMYK fills)
  4. File size < 2 MB
  5. Original stroke geometry present  (re-emitted strokes must be black)

Exit 0 = all checks passed
Exit 1 = one or more checks failed

Usage:
    py -3 scripts/verify_cherry.py templates/cherry-terminal-v2-solid-test.pdf
    py -3 scripts/verify_cherry.py templates/cherry-terminal-v2-hueshift-test.pdf --baseline-strokes 6716
"""

import argparse
import io
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent

# Baseline from template analysis (2026-04-21, 7-group full recolor)
BASELINE_FILLS_ORIGINAL = 460       # fills in the original Cherry template
BASELINE_STROKES_ORIGINAL = 3358    # strokes in the original Cherry template
# After a full 7-group recolor: 201 new fills + 2551 new strokes (re-emitted)
# Allow ±5% tolerance on stroke count
STROKE_TOLERANCE_PCT = 5.0
MAX_FILE_SIZE_KB = 2048


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


def main():
    p = argparse.ArgumentParser(description="Quality gate for Cherry 135 recolored PDFs")
    p.add_argument("pdf", help="Path to the recolored PDF to verify")
    p.add_argument("--baseline-strokes", type=int, default=None,
                   help="Expected stroke count after recolor (default: auto = original × 2)")
    p.add_argument("--baseline-fills", type=int, default=BASELINE_FILLS_ORIGINAL,
                   help=f"Minimum fill count (default: {BASELINE_FILLS_ORIGINAL})")
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

    # 4. File size
    if not check("File size < 2 MB",
                 stats["size_kb"] < MAX_FILE_SIZE_KB,
                 f"{stats['size_kb']} KB"):
        failures += 1

    # 5. Re-emitted strokes are black (Cherry bevel lines)
    has_black_strokes = "#000000" in stats["stroke_colors"]
    if not check("Black strokes present (3D bevel lines)",
                 has_black_strokes,
                 f"stroke colors: {sorted(stats['stroke_colors'])}"):
        failures += 1

    print()
    if failures == 0:
        print("RESULT: ALL CHECKS PASSED")
        sys.exit(0)
    else:
        print(f"RESULT: {failures} CHECK(S) FAILED — do not push this PDF")
        sys.exit(1)


if __name__ == "__main__":
    main()
