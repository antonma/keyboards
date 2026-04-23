"""
validate_labels.py — Post-build label validator for per-key-design PDFs

For each key declared in key-design.json, checks that:
  - All declared primary/secondary/tertiary labels are present in the PDF
    at the expected anchor position (±POSITION_TOLERANCE pt)
  - Label bbox is contained within the keycap bbox
  - Phantom text (text in PDF not declared in key-design) is flagged

Output: JSON report in reports/ and summary to stdout.
Exit code: 0 = no errors, 1 = errors found.

Usage:
    py -3 scripts/validate_labels.py --design terminal-v2 \\
        --pdf templates/terminal-v2-anton-v2.pdf

    py -3 scripts/validate_labels.py --design terminal-v2 \\
        --pdf templates/terminal-v2-anton-v2.pdf \\
        --coord-map layouts/iso-de-75-anton-coordinate-map.json
"""

import argparse
import io
import json
import sys
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent
DEFAULT_COORD_MAP = REPO / "layouts" / "iso-de-75-anton-coordinate-map.json"

POSITION_TOLERANCE = 8.0  # pt — anchor must be within this distance
ANCHOR_OFFSET = 8.0       # pt from keycap edge (must match template_driver)
MIN_RATIO = 0.05          # label width / keycap width lower warning bound
MAX_RATIO = 0.90          # label width / keycap width upper warning bound


def load_yaml(path: Path) -> dict:
    try:
        import yaml
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except ImportError:
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


def load_fonts(design_dir: Path) -> dict:
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


def expected_anchor(key: dict, label_type: str, text_w: float, text_h: float) -> tuple[float, float]:
    """Return expected (x, y) baseline anchor for a label type on this key.

    Matches the anchor logic in template_driver.py PdfDriver.set_legend().
    """
    x0, y0, x1, y1 = key["x0"], key["y0"], key["x1"], key["y1"]
    off = ANCHOR_OFFSET

    if label_type == "main":
        if key["id"] == "enter_top":
            cx, cy = key["cx"], key["cy"]
            return (cx - text_w / 2, cy)  # approximate center
        return (x0 + off, y0 + off + text_h * 0.75)
    elif label_type == "sub":
        return (x0 + off, y1 - off)
    elif label_type == "tertiary":
        return (x1 - off - text_w, y1 - off)
    return (key["cx"], key["cy"])


def point_near(px: float, py: float, ex: float, ey: float, tol: float = POSITION_TOLERANCE) -> bool:
    return abs(px - ex) <= tol and abs(py - ey) <= tol


def bbox_inside(inner, outer, margin: float = 4.0) -> bool:
    """Check if inner rect is contained in outer rect (with margin tolerance)."""
    return (inner.x0 >= outer.x0 - margin and inner.y0 >= outer.y0 - margin and
            inner.x1 <= outer.x1 + margin and inner.y1 <= outer.y1 + margin)


def main():
    p = argparse.ArgumentParser(description="Validate labels in a per-key-design PDF")
    p.add_argument("--design",    required=True, help="Design name (e.g. terminal-v2)")
    p.add_argument("--pdf",       required=True, help="PDF to validate")
    p.add_argument("--coord-map", default=str(DEFAULT_COORD_MAP))
    args = p.parse_args()

    design_dir = REPO / "designs" / args.design
    key_design_path = design_dir / "key-design.json"

    def resolve(s: str) -> Path:
        pt = Path(s)
        return pt if pt.is_absolute() else REPO / pt

    pdf_path = resolve(args.pdf)
    coord_map_path = resolve(args.coord_map)

    for rq in [key_design_path, pdf_path, coord_map_path]:
        if not rq.exists():
            print(f"ERROR: not found: {rq}", file=sys.stderr)
            sys.exit(1)

    with open(coord_map_path, encoding="utf-8") as f:
        coord_map = json.load(f)
    key_by_id = {k["id"]: k for k in coord_map["keys"]}

    with open(key_design_path, encoding="utf-8") as f:
        key_design = json.load(f)
    keys_spec: dict = key_design.get("keys", {})

    fonts = load_fonts(design_dir)

    try:
        import fitz
    except ImportError:
        print("ERROR: PyMuPDF required. pip install pymupdf", file=sys.stderr)
        sys.exit(1)

    font_cache: dict = {}

    def get_font(font_ref: str):
        font_path = fonts.get(font_ref, "")
        cache_key = font_path or "__helv__"
        if cache_key not in font_cache:
            font_cache[cache_key] = (
                fitz.Font(fontfile=font_path) if font_path else fitz.Font("helv")
            )
        return font_cache[cache_key]

    doc = fitz.open(str(pdf_path))
    page = doc[0]

    # Extract all text blocks from the PDF with their bboxes and positions
    pdf_texts = []
    for block in page.get_text("rawdict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span.get("text", "").strip()
                if not text:
                    continue
                origin = span.get("origin", (0, 0))  # baseline point
                bbox = fitz.Rect(span.get("bbox", (0, 0, 0, 0)))
                pdf_texts.append({
                    "text": text,
                    "origin": origin,
                    "bbox": bbox,
                })

    errors = []
    warnings = []

    # Track which PDF text spans were matched (for phantom detection)
    matched_span_indices = set()

    for key_id, spec in keys_spec.items():
        key = key_by_id.get(key_id)
        if key is None:
            warnings.append(f"key '{key_id}' in key-design.json not found in coord-map — skipped")
            continue

        key_rect = fitz.Rect(key["x0"], key["y0"], key["x1"], key["y1"])
        key_w = key["x1"] - key["x0"]
        legend = spec.get("legend", {})

        for label_type in ("main", "sub", "tertiary"):
            label_spec = legend.get(label_type)
            if not label_spec:
                continue
            declared_text = label_spec.get("text", "")
            if not declared_text:
                continue

            font_ref = label_spec.get("font", "primary")
            size = float(label_spec.get("size", 18))
            font = get_font(font_ref)
            text_w = font.text_length(declared_text, fontsize=size)
            text_h = size

            ex, ey = expected_anchor(key, label_type, text_w, text_h)

            # Find matching span in PDF
            found = False
            for idx, span in enumerate(pdf_texts):
                if declared_text not in span["text"] and span["text"] not in declared_text:
                    continue
                ox, oy = span["origin"]
                if point_near(ox, oy, ex, ey):
                    # Check bbox containment
                    if not bbox_inside(span["bbox"], key_rect):
                        errors.append({
                            "key": key_id,
                            "label_type": label_type,
                            "text": declared_text,
                            "error": "label_outside_keycap",
                            "detail": f"bbox {span['bbox']} outside key {key_rect}",
                        })
                    matched_span_indices.add(idx)
                    found = True
                    break

            if not found:
                errors.append({
                    "key": key_id,
                    "label_type": label_type,
                    "text": declared_text,
                    "error": "missing_label",
                    "detail": f"expected near ({ex:.1f},{ey:.1f}), not found in PDF",
                })
                continue

            # Width ratio warning
            ratio = text_w / key_w if key_w > 0 else 0
            if ratio < MIN_RATIO or ratio > MAX_RATIO:
                warnings.append(
                    f"key '{key_id}' {label_type} '{declared_text}': "
                    f"width ratio {ratio:.2f} outside [{MIN_RATIO},{MAX_RATIO}]"
                )

    # Phantom detection: text in PDF inside a key bbox but not declared
    for idx, span in enumerate(pdf_texts):
        if idx in matched_span_indices:
            continue
        span_rect = span["bbox"]
        # Check if it falls inside any key
        for key in coord_map["keys"]:
            key_rect = fitz.Rect(key["x0"], key["y0"], key["x1"], key["y1"])
            if key_rect.contains(span_rect.tl) and key_rect.contains(span_rect.br):
                key_id = key["id"]
                spec = keys_spec.get(key_id, {})
                legend = spec.get("legend", {})
                declared_texts = [
                    legend.get(lt, {}).get("text", "")
                    for lt in ("main", "sub", "tertiary")
                    if legend.get(lt)
                ]
                if span["text"] not in declared_texts:
                    errors.append({
                        "key": key_id,
                        "label_type": "phantom",
                        "text": span["text"],
                        "error": "phantom_label",
                        "detail": f"text '{span['text']}' at {span['origin']} not declared in key-design.json",
                    })
                break

    doc.close()

    total_keys = len(keys_spec)
    missing  = sum(1 for e in errors if e["error"] == "missing_label")
    phantom  = sum(1 for e in errors if e["error"] == "phantom_label")
    outside  = sum(1 for e in errors if e["error"] == "label_outside_keycap")

    report = {
        "design": args.design,
        "pdf": str(pdf_path),
        "coord_map": str(coord_map_path),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total_keys": total_keys,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "missing_labels": missing,
            "phantom_labels": phantom,
            "outside_keycap": outside,
            "total_errors": len(errors),
            "total_warnings": len(warnings),
        },
    }

    reports_dir = REPO / "reports"
    reports_dir.mkdir(exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    report_path = reports_dir / f"label-validation-{args.design}-{ts}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"validate_labels")
    print(f"  Design     : {args.design}")
    print(f"  PDF        : {pdf_path.name}")
    print(f"  Total keys : {total_keys}")
    print(f"  Errors     : {len(errors)}  (missing={missing}, phantom={phantom}, outside={outside})")
    print(f"  Warnings   : {len(warnings)}")
    print(f"  Report     : {report_path}")

    if errors:
        print("\nERRORS:")
        for e in errors[:20]:
            print(f"  [{e['error']}] key={e['key']} type={e['label_type']} "
                  f"text={repr(e['text'])}: {e['detail']}")
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more (see report)")
        sys.exit(1)

    print("\nAll declared labels validated OK.")
    sys.exit(0)


if __name__ == "__main__":
    main()
