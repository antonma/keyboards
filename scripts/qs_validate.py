"""QS-Validator für cherry-135-iso-de.pdf
Ausführen VOR jedem Commit:
  py -3 scripts/qs_validate.py

Prüfungen:
  1. Drawing-Count pro Key (≥25 für 1u, ≥30 für Modifier)
  2. Body-Fill vorhanden pro Key
  3. Ghost-Check: leere Zonen pixel-sauber (keine sichtbaren Pfade)
  4. Renderings: Overview 3x + Einzelkeys aller modifizierten Tasten
  5. JSON-Report: qs_report/report.json
"""
import fitz, sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PDF = "templates/cherry-135-iso-de.pdf"
OUT = "d:/tmp/qs_report"
os.makedirs(OUT, exist_ok=True)

PAD = 3   # Padding für Drawing-Count (Pfad-Zentrum darf PAD px ausserhalb bbox liegen)

# ─── Key-Positionen im MODIFIZIERTEN Template ────────────────────────────────
# Jeder Eintrag: (fitz.Rect, key_type)
# key_type → min_drawings: '1u'→25, 'mod'→30, 'wide'→35, 'enter'→40
MODIFIED_KEYS = {
    # Transplantiert aus Alternates-Block
    'AltGr':     (fitz.Rect(682, 406, 734, 458), 'mod'),
    'FN':        (fitz.Rect(750, 406, 802, 458), 'mod'),
    'STRG-R':    (fitz.Rect(884, 406, 936, 458), 'mod'),
    'hash':      (fitz.Rect(824, 299, 876, 350), '1u'),
    'ISO-Enter': (fitz.Rect(864, 245, 943, 351), 'enter'),
    'SHIFT-L':   (fitz.Rect(137, 352, 202, 404), 'mod'),
    'SHIFT-R':   (fitz.Rect(798, 352, 891, 404), 'wide'),
    # Shift-Reihe: alle um dx=-53 verschoben
    'less':      (fitz.Rect(203, 350, 259, 406), '1u'),
    'y':         (fitz.Rect(256, 350, 313, 406), '1u'),
    'x':         (fitz.Rect(310, 350, 367, 406), '1u'),
    'c':         (fitz.Rect(364, 350, 421, 406), '1u'),
    'v':         (fitz.Rect(418, 350, 475, 406), '1u'),
    'b':         (fitz.Rect(472, 350, 529, 406), '1u'),
    'n':         (fitz.Rect(526, 350, 583, 406), '1u'),
    'm':         (fitz.Rect(580, 350, 637, 406), '1u'),
    'comma':     (fitz.Rect(634, 350, 691, 406), '1u'),
    'period':    (fitz.Rect(688, 350, 744, 406), '1u'),
    '-_':        (fitz.Rect(742, 350, 798, 406), '1u'),
}

# Referenz-Keys (unverändert aus Quell-Template — zum Vergleich)
REFERENCE_KEYS = {
    'A-ref':      (fitz.Rect(231, 282, 283, 350), '1u'),
    'STRG-L-ref': (fitz.Rect(137, 406, 202, 458), 'mod'),
    'WIN-ref':    (fitz.Rect(205, 406, 260, 458), 'mod'),
    'ALT-L-ref':  (fitz.Rect(262, 406, 317, 458), 'mod'),
}

THRESHOLDS = {'1u': 25, 'mod': 30, 'wide': 35, 'enter': 40}

# Zonen die LEER sein müssen (kein sichtbarer Inhalt)
# Ghost-Check erfolgt pixel-basiert (render → zähle dunkle Pixel)
EMPTY_ZONES = {
    'MENU-gap':    fitz.Rect(804, 404, 882, 465),  # Lücke wo MENU war
    'right-STRG':  fitz.Rect(937, 404, 992, 465),  # Rechts von STRG
}
GHOST_DARK_THRESHOLD = 0.01   # Max % dunkler Pixel erlaubt (< 0.01% = clean)

# ─── Helpers ─────────────────────────────────────────────────────────────────
def is_near_white(c, thresh=0.9):
    return c and all(v >= thresh for v in c[:3])

def count_drawings(drawings, bbox, pad=PAD):
    bx = fitz.Rect(bbox.x0-pad, bbox.y0-pad, bbox.x1+pad, bbox.y1+pad)
    return sum(
        1 for d in drawings
        if bx.x0 <= (d['rect'].x0+d['rect'].x1)/2 <= bx.x1
        and bx.y0 <= (d['rect'].y0+d['rect'].y1)/2 <= bx.y1
    )

def has_body_fill(drawings, bbox, pad=PAD, min_area=200):
    bx = fitz.Rect(bbox.x0-pad, bbox.y0-pad, bbox.x1+pad, bbox.y1+pad)
    for d in drawings:
        fill = d.get('fill')
        if not fill or is_near_white(fill):
            continue
        r = d['rect']
        if bx.x0 <= (r.x0+r.x1)/2 <= bx.x1 and bx.y0 <= (r.y0+r.y1)/2 <= bx.y1:
            if r.width * r.height > min_area:
                return True
    return False

def pixel_dark_pct(page, bbox, dark_threshold=230):
    """Rendert bbox und gibt Anteil dunkler Pixel zurück."""
    pix = page.get_pixmap(matrix=fitz.Matrix(4, 4), clip=bbox)
    n_total = pix.width * pix.height
    n_dark = sum(
        1 for i in range(n_total)
        if any(pix.samples[i*pix.n + c] < dark_threshold for c in range(min(3, pix.n)))
    )
    return 100.0 * n_dark / max(n_total, 1)

def render_key(page, bbox, outfile, scale=8, margin=10):
    clip = fitz.Rect(bbox.x0-margin, bbox.y0-margin,
                     bbox.x1+margin, bbox.y1+margin)
    page.get_pixmap(matrix=fitz.Matrix(scale, scale), clip=clip).save(outfile)

# ─── Laden ───────────────────────────────────────────────────────────────────
doc  = fitz.open(PDF)
page = doc[0]
drws = page.get_drawings()
print(f"PDF: {PDF}")
print(f"Total drawings: {len(drws)}")
print()

all_results = {}
failures = []
warnings = []

# ─── 1. Drawing-Count + Body-Fill ────────────────────────────────────────────
def run_checks(key_dict, section):
    print(f"── {section} " + "─"*(55-len(section)))
    print(f"  {'Key':<14} {'Type':<8} {'Count':>6} {'Min':>5} {'Fill':>6}  Result")
    for key_id, (rect, ktype) in key_dict.items():
        cnt  = count_drawings(drws, rect)
        mn   = THRESHOLDS.get(ktype, 25)
        fill = has_body_fill(drws, rect)
        ok   = cnt >= mn and fill
        sym  = "✓" if ok else "✗"
        info = []
        if cnt < mn:  info.append(f"count={cnt}<{mn}")
        if not fill:  info.append("no-fill")
        note = "  ← " + ", ".join(info) if info else ""
        print(f"  {key_id:<14} {ktype:<8} {cnt:>6} {mn:>5} {'✓' if fill else '✗':>6}  {sym}{note}")
        all_results[key_id] = {
            'section': section,
            'rect': list(rect), 'type': ktype,
            'count': cnt, 'min': mn,
            'has_fill': fill, 'passed': ok
        }
        if not ok:
            failures.append(key_id)
    print()

run_checks(MODIFIED_KEYS,  "MODIFIZIERT")
run_checks(REFERENCE_KEYS, "REFERENZ (unverändert, nur Vergleich)")

# ─── 2. Ghost-Check (pixel-basiert) ──────────────────────────────────────────
print("── Ghost-Check (pixel-basiert) " + "─"*30)
ghost_results = {}
for zone, bbox in EMPTY_ZONES.items():
    pct = pixel_dark_pct(page, bbox)
    ok  = pct <= GHOST_DARK_THRESHOLD
    sym = "✓" if ok else "✗"
    print(f"  {zone:<20}: {pct:.4f}% dark  {sym}")
    ghost_results[zone] = {'dark_pct': pct, 'passed': ok}
    if not ok:
        failures.append(f"ghost:{zone}")
print()

# ─── 3. Renderings ───────────────────────────────────────────────────────────
print("── Renderings ──────────────────────────────────────────────────────")

for key_id, (rect, _) in {**MODIFIED_KEYS, **REFERENCE_KEYS}.items():
    passed = all_results.get(key_id, {}).get('passed', True)
    tag    = "_FAIL" if not passed else ""
    render_key(page, rect, f"{OUT}/{key_id}{tag}.png")

# Overview + Detail-Renders
page.get_pixmap(matrix=fitz.Matrix(3, 3),
                clip=fitz.Rect(100, 130, 1000, 480)).save(f"{OUT}/overview_3x.png")
page.get_pixmap(matrix=fitz.Matrix(4, 4),
                clip=fitz.Rect(110, 338, 960, 415)).save(f"{OUT}/shiftrow_4x.png")
page.get_pixmap(matrix=fitz.Matrix(4, 4),
                clip=fitz.Rect(620, 390, 960, 470)).save(f"{OUT}/mods_4x.png")
print(f"  Gespeichert in: {OUT}/")
print()

# ─── 4. Zusammenfassung ───────────────────────────────────────────────────────
print("══ QS-Ergebnis ══════════════════════════════════════════════════════")
if not failures:
    print("  ✓ ALLE Kriterien bestanden — bereit für Commit")
    status = "PASS"
else:
    print(f"  ✗ {len(failures)} FEHLER — KEIN COMMIT")
    for f in failures:
        print(f"    • {f}")
    status = "FAIL"

if warnings:
    print(f"\n  ⚠  {len(warnings)} Hinweise:")
    for w in warnings:
        print(f"    • {w}")

# JSON-Report
report = {
    'pdf': PDF, 'status': status,
    'total_drawings': len(drws),
    'keys': all_results,
    'ghost_zones': ghost_results,
    'failures': failures,
    'warnings': warnings,
}
with open(f"{OUT}/report.json", 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, default=str)
print(f"\n  Report: {OUT}/report.json")

doc.close()
sys.exit(0 if status == "PASS" else 1)
