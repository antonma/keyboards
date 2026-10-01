import os, sys, math
import fitz
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen

sys.stdout.reconfigure(encoding='utf-8')
OUT = r'D:\repos\GitHub\keyboards\qc\checklist\img'
os.makedirs(OUT, exist_ok=True)

W, H = 1500, 1000
BG = '#F4F1EC'
CREAM, BROWN = '#E8DDC8', '#3A2A1E'
TERRA, TAUPE, ROSE, ESPR, GOLD = '#A85D3E', '#8A7868', '#C89090', '#1A1612', '#D4A574'
GUIDE = '#B9B0A4'
S = 640                      # Standard-Kappenbreite (Bild 1, 3)
LEG = 0.30                   # Legendenhoehe (Cap-Height) relativ zur Kappenbreite
DX, DY = 0.052, 0.070        # Versatz Bluestone-Prototyp (Note 7677a801)

# ---------- Farbe ----------
def hx(c): c = c.lstrip('#'); return [int(c[i:i+2], 16) / 255 for i in (0, 2, 4)]
def tohex(rgb): return '#' + ''.join('%02X' % max(0, min(255, round(v * 255))) for v in rgb)
def _lin(v): return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
def _gam(v): return 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055
WP = (0.95047, 1.0, 1.08883)
def to_lab(c):
    r, g, b = [_lin(v) for v in hx(c)]
    X = 0.4124 * r + 0.3576 * g + 0.1805 * b; Y = 0.2126 * r + 0.7152 * g + 0.0722 * b; Z = 0.0193 * r + 0.1192 * g + 0.9505 * b
    f = lambda t: t ** (1 / 3) if t > 216 / 24389 else (24389 / 27 * t + 16) / 116
    fx, fy, fz = f(X / WP[0]), f(Y / WP[1]), f(Z / WP[2])
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))
def from_lab(L, a, b):
    fy = (L + 16) / 116; fx = fy + a / 500; fz = fy - b / 200
    fi = lambda t: t ** 3 if t ** 3 > 216 / 24389 else (116 * t - 16) / (24389 / 27)
    X, Y, Z = fi(fx) * WP[0], fi(fy) * WP[1], fi(fz) * WP[2]
    r = 3.2406 * X - 1.5372 * Y - 0.4986 * Z; g = -0.9689 * X + 1.8758 * Y + 0.0415 * Z; bb = 0.0557 * X - 0.2040 * Y + 1.0570 * Z
    return tohex([_gam(max(0, v)) for v in (r, g, bb)])
def shade(c, dL):
    L, a, b = to_lab(c); return from_lab(L + dL, a, b)
def dE(c1, c2):
    return math.dist(to_lab(c1), to_lab(c2))

# ---------- Font -> Pfad ----------
FONT = TTFont(r'C:\Windows\Fonts\BRLNSDB.TTF')
GS = FONT.getGlyphSet(); CMAP = FONT.getBestCmap()
_bp = BoundsPen(GS); GS[CMAP[ord('H')]].draw(_bp); CAPH = _bp.bounds[3]
def glyph(ch, cx, cy, h):
    """Glyph ch als Pfad; Cap-Height = h; horizontal Bbox-mittig, vertikal Cap-Height-mittig."""
    g = GS[CMAP[ord(ch)]]
    bp = BoundsPen(GS); g.draw(bp); x0, y0, x1, y1 = bp.bounds
    sc = h / CAPH
    tx = cx - (x0 + x1) / 2 * sc; ty = cy + h / 2
    pen = SVGPathPen(GS, ntos=lambda v: ('%.2f' % v).rstrip('0').rstrip('.'))
    g.draw(TransformPen(pen, (sc, 0, 0, -sc, tx, ty)))
    return pen.getCommands()

# ---------- Bausteine ----------
def rrect(x, y, w, h, r, **kw):
    a = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{r:.2f}" {a}/>'

def cap_top(cx, cy, s, col, shadow=True):
    """Keycap Draufsicht: Schatten, Mantel (Skirt), Top-Flaeche mit angedeuteter Schale."""
    o = []
    if shadow:
        o.append(rrect(cx - s / 2 + s * .01, cy - s / 2 + s * .035, s, s, s * .15, fill='#3A2A1E', fill_opacity='0.13'))
    o.append(rrect(cx - s / 2, cy - s / 2, s, s, s * .15, fill=shade(col, -7), stroke=shade(col, -22), stroke_width=f'{s*.008:.2f}'))
    i = s * .115
    o.append(rrect(cx - s / 2 + i, cy - s / 2 + i * .8, s - 2 * i, s - 2 * i, s * .12, fill=col, stroke=shade(col, -12), stroke_width=f'{s*.005:.2f}'))
    j = s * .165   # Schale: dezenter heller Innenring
    o.append(rrect(cx - s / 2 + j, cy - s / 2 + j * .86, s - 2 * j, s - 2 * j, s * .10, fill='none', stroke=shade(col, 4), stroke_width=f'{s*.006:.2f}'))
    return '\n'.join(o)

def top_center(cx, cy, s):
    """Mittelpunkt der Top-Flaeche (leicht nach oben versetzt wie der Mantel-Inset)."""
    return cx, cy - s * .115 * .2 / 2 * 2 * .5

def guides(cx, cy, s):
    """Mittelachsen-Hilfslinien (gestrichelt, ausserhalb der Kappe beginnend) — identisch in good+bad."""
    e = s * .5 + 70; d = 'stroke-dasharray="14 10"'
    return (f'<g stroke="{GUIDE}" stroke-width="3" {d} fill="none">'
            f'<line x1="{cx-e:.1f}" y1="{cy:.1f}" x2="{cx+e:.1f}" y2="{cy:.1f}"/>'
            f'<line x1="{cx:.1f}" y1="{cy-e:.1f}" x2="{cx:.1f}" y2="{cy+e:.1f}"/></g>')

def guides_outside(cx, cy, s):
    """Nur Marken ausserhalb der Kappe (Kimme) — damit auf der Kappe nichts gezeichnet ist."""
    a, b = s * .5 + 22, s * .5 + 90
    L = []
    for (x1, y1, x2, y2) in [(cx - b, cy, cx - a, cy), (cx + a, cy, cx + b, cy), (cx, cy - b, cx, cy - a), (cx, cy + a, cx, cy + b)]:
        L.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>')
    return f'<g stroke="{GUIDE}" stroke-width="5" stroke-linecap="round">' + ''.join(L) + '</g>'

def svg(body, w=W, h=H):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n'
            f'<rect width="{w}" height="{h}" fill="{BG}"/>\n{body}\n</svg>\n')

def save(name, s):
    p = os.path.join(OUT, name)
    open(p + '.svg', 'w', encoding='utf-8').write(s)
    doc = fitz.open('svg', s.encode('utf-8'))
    doc[0].get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False).save(p + '.png')
    print('ok', name)

def shift_arrow(cx, cy, h):
    """Shift-Pfeil als gefuellte Form, Hoehe h, Bbox-mittig."""
    w = h * .92; st = w * .42; hh = h * .52
    x0 = cx - w / 2; y0 = cy - h / 2
    pts = [(cx, y0), (x0 + w, y0 + hh), (cx + st / 2, y0 + hh), (cx + st / 2, y0 + h), (cx - st / 2, y0 + h), (cx - st / 2, y0 + hh), (x0, y0 + hh)]
    return 'M' + ' L'.join(f'{x:.2f},{y:.2f}' for x, y in pts) + ' Z'

# ============ Bild 1 ============
CX, CY = W / 2, H / 2
def legend_A(cx, cy, s, col, dx=0, dy=0):
    tcx, tcy = cx, cy - s * .023   # Top-Flaechen-Mitte (Inset oben 0.8*i)
    return f'<path d="{glyph("A", tcx + dx * s, tcy + dy * s, s * LEG)}" fill="{col}"/>'

TCY = CY - S * .023
body_g = guides_outside(CX, TCY, S) + cap_top(CX, CY, S, CREAM) + legend_A(CX, CY, S, BROWN)
body_b = guides_outside(CX, TCY, S) + cap_top(CX, CY, S, CREAM) + legend_A(CX, CY, S, BROWN, DX, DY)
save('good_alpha', svg(body_g)); save('bad_shift_right', svg(body_b))

ah = S * LEG * 1.05
body_i = (guides_outside(CX, TCY, S) + cap_top(CX, CY, S, TERRA) +
          f'<path d="{shift_arrow(CX + DX*S, TCY + DY*S, ah)}" fill="{CREAM}" stroke="{CREAM}" stroke-width="{S*.022:.1f}" stroke-linejoin="round"/>')
save('bad_shift_icon', svg(body_i))

# ============ Bild 2 (Nahansicht) ============
SZ = 1450; ZCX, ZCY = W / 2, H / 2 + 20
zA = glyph('A', ZCX, ZCY - SZ * .023, SZ * LEG * 1.25)
base2 = cap_top(ZCX, ZCY, SZ, CREAM, shadow=False)
save('good_alpha_sharp', svg(base2 + f'<path d="{zA}" fill="{BROWN}"/>'))

halo = ''.join(f'<path d="{zA}" fill="none" stroke="{BROWN}" stroke-opacity="{op}" stroke-width="{sw}" stroke-linejoin="round"/>'
               for sw, op in [(64 - 6 * k, .03 + .006 * k) for k in range(11)])
ghost = f'<path d="{zA}" transform="translate(14,9)" fill="{BROWN}" fill-opacity="0.30"/>'
# Streumarken: 3 Punkte + 1 Schliere (Tapered Slash, geschlossener Fill-Pfad)
def dot(x, y, r, op=0.8):
    rings = ''.join(f'<circle cx="{x}" cy="{y}" r="{r*(1+k*.14):.1f}" fill="{BROWN}" fill-opacity="{op*.07:.3f}"/>' for k in range(8, 0, -1))
    return rings + f'<circle cx="{x}" cy="{y}" r="{r}" fill="{BROWN}" fill-opacity="{op}"/>'
marks = (dot(1030, 320, 21) + dot(425, 720, 16, .8) + dot(1125, 590, 13, .75) +
         f'<path d="M905,792 C960,764 1030,748 1090,752 C1110,754 1122,760 1128,768 C1105,764 1070,764 1040,768 C995,775 955,790 916,809 C903,810 898,799 905,792 Z" fill="{BROWN}" fill-opacity="0.55"/>')
save('bad_stray_marks', svg(base2 + halo + ghost + f'<path d="{zA}" fill="{BROWN}" fill-opacity="0.93"/>' + marks))

# ============ Bild 3 (Farbabgleich) ============
L0, a0, b0 = to_lab(TERRA)
TERRA_OFF = from_lab(L0 + 8.0, a0 - 3.5, b0 + 4.5)   # heller + Richtung Orange/Gelb
print('Terracotta abweichend', TERRA_OFF, 'dE76 = %.1f' % dE(TERRA, TERRA_OFF))
gap = 90; lx = W / 2 - gap / 2 - S / 2; rx = W / 2 + gap / 2 + S / 2
save('good_color_match', svg(cap_top(lx, CY, S, TERRA) + cap_top(rx, CY, S, TERRA)))
save('bad_color_mismatch', svg(cap_top(lx, CY, S, TERRA) + cap_top(rx, CY, S, TERRA_OFF)))

# ============ Bild 4 (Tray) ============
ROWS = [('QWERT', CREAM, BROWN), ('ASDFG', TAUPE, CREAM), ('ZXCVB', ROSE, BROWN)]
TS, TP = 222, 250
TW, TH = 5 * TP + 60, 3 * TP + 60
tx0, ty0 = (W - TW) / 2, (H - TH) / 2
TRAY, SLOT = '#5E5751', '#4A4540'
def tray(layout):
    o = [rrect(tx0 + 6, ty0 + 14, TW, TH, 34, fill='#3A2A1E', fill_opacity='0.15'),
         rrect(tx0, ty0, TW, TH, 34, fill=TRAY, stroke='#4A4540', stroke_width=4)]
    for r in range(3):
        for c in range(5):
            cx = tx0 + 30 + TP * c + TP / 2; cy = ty0 + 30 + TP * r + TP / 2
            o.append(rrect(cx - TP / 2 + 8, cy - TP / 2 + 8, TP - 16, TP - 16, 30, fill=SLOT))
            cell = layout[r][c]
            if cell is None:
                o[-1] = rrect(cx - TP / 2 + 8, cy - TP / 2 + 8, TP - 16, TP - 16, 30, fill='#3E3935')   # leerer Platz: tiefer
                o.append(rrect(cx - TP / 2 + 20, cy - TP / 2 + 14, TP - 40, 14, 7, fill='#322E2B'))  # Innenschatten
                continue
            ch, col, lc = cell
            o.append(cap_top(cx, cy, TS, col))
            o.append(f'<path d="{glyph(ch, cx, cy - TS*.023, TS*LEG)}" fill="{lc}"/>')
    return '\n'.join(o)
full = [[(ch, col, lc) for ch in s] for s, col, lc in ROWS]
save('good_tray_full', svg(tray(full)))
bad = [row[:] for row in full]
bad[0][2], bad[2][3] = bad[2][3], bad[0][2]     # E <-> V vertauscht (Farbe passt nicht zur Reihe)
bad[1][3] = None                                # F fehlt
save('bad_tray_gap', svg(tray(bad)))

# ============ Bild 5 (Profil Seitenansicht) ============
U = 285; GAPU = 22; BASE = 612
def moa(x0, w, h, col):
    """MOA: mittelhoch, gleichmaessig, grosse Schulterradien, leicht gewoelbte Oberseite (glatte Kubiken)."""
    ins = w * .10; r = h * .24; dome = h * .07; yb = BASE; yt = BASE - h + dome
    cx = x0 + w / 2
    sl = (x0 + ins, yt + r); sr = (x0 + w - ins, yt + r)
    dl = (sl[0] - x0, sl[1] - yb); n = math.hypot(*dl); dl = (dl[0] / n, dl[1] / n)
    k = r * 0.85; half = w / 2 - ins
    d = (f'M{x0:.1f},{yb:.1f} L{sl[0]:.1f},{sl[1]:.1f} '
         f'C{sl[0]+dl[0]*k:.1f},{sl[1]+dl[1]*k:.1f} {cx-half*.70:.1f},{yt-dome:.1f} {cx:.1f},{yt-dome:.1f} '
         f'C{cx+half*.70:.1f},{yt-dome:.1f} {sr[0]-dl[0]*k:.1f},{sr[1]+dl[1]*k:.1f} {sr[0]:.1f},{sr[1]:.1f} '
         f'L{x0+w:.1f},{yb:.1f} Z')
    return d
def cherry(x0, w, h, col):
    """Fremdprofil (Cherry-artig hoch): hoeher, schraege flache Oberseite, kleine Radien."""
    ins = w * .13; r = w * .05; yb = BASE; ytl = BASE - h; ytr = BASE - h + h * .14
    d = (f'M{x0:.1f},{yb:.1f} L{x0+ins-r*.3:.1f},{ytl+r:.1f} Q{x0+ins:.1f},{ytl:.1f} {x0+ins+r:.1f},{ytl+ (ytr-ytl)*r/(w-2*ins):.1f} '
         f'L{x0+w-ins-r:.1f},{ytr-(ytr-ytl)*r/(w-2*ins):.1f} Q{x0+w-ins:.1f},{ytr:.1f} {x0+w-ins+r*.3:.1f},{ytr+r:.1f} '
         f'L{x0+w:.1f},{yb:.1f} Z')
    return d
def profile_row(odd=False):
    widths = [U, U, U, U * 1.5]
    total = sum(widths) + GAPU * (len(widths) - 1); x = (W - total) / 2
    h = U * .62
    o = []
    # Platte + Schalter
    o.append(rrect((W - total) / 2 - 40, BASE + 42, total + 80, 34, 8, fill='#8E867C'))
    xs = []
    for w in widths:
        xs.append(x); x += w + GAPU
    for x0, w in zip(xs, widths):
        o.append(rrect(x0 + w / 2 - 56, BASE - 4, 112, 50, 6, fill='#4A4540'))
    # Hoehen-Referenzlinie (gestrichelt, identisch in good+bad)
    ref = BASE - h - 3
    o.append(f'<line x1="{(W-total)/2-60:.1f}" y1="{ref:.1f}" x2="{(W+total)/2+60:.1f}" y2="{ref:.1f}" stroke="{GUIDE}" stroke-width="5" stroke-linecap="round"/>')
    for i, (x0, w) in enumerate(zip(xs, widths)):
        col = CREAM
        last = i == len(widths) - 1
        d = cherry(x0, w, h * 1.62, col) if (odd and last) else moa(x0, w, h, col)
        o.append(f'<path d="{d}" transform="translate(6,10)" fill="#3A2A1E" fill-opacity="0.12"/>')
        o.append(f'<path d="{d}" fill="{col}" stroke="{shade(col,-25)}" stroke-width="5" stroke-linejoin="round"/>')
        o.append(rrect(x0 + 6, BASE - 16, w - 12, 12, 4, fill=shade(col, -9)))
    return '\n'.join(o)
save('good_iso_enter', svg(profile_row(False)))
save('bad_iso_enter_profile', svg(profile_row(True)))

# ============ Bild 6 (Sub-Legenden Eckposition, Set: v2 Block A Zeile 2) ============
def sub_legend(cx, cy, s, col, ch, dxr, dyr, size_ratio=0.155):
    """Kleine Eck-Legende (Shift-/AltGr-Sub) relativ zur Top-Flaechen-Mitte (cx,cy)."""
    return f'<path d="{glyph(ch, cx + dxr * s, cy + dyr * s, s * size_ratio)}" fill="{col}"/>'

def main_legend(cx, cy, s, col, ch, dxr=-0.16, dyr=0.0, size_ratio=LEG):
    return f'<path d="{glyph(ch, cx + dxr * s, cy + dyr * s, s * size_ratio)}" fill="{col}"/>'

CORNER_TR = (0.275, -0.255)
CORNER_BR = (0.275, 0.255)
CORNER_BL = (-0.275, 0.255)

body_sub_good = (guides_outside(CX, TCY, S) + cap_top(CX, CY, S, CREAM) +
                  main_legend(CX, TCY, S, BROWN, '7') +
                  sub_legend(CX, TCY, S, BROWN, '/', *CORNER_TR) +
                  sub_legend(CX, TCY, S, BROWN, '{', *CORNER_BR))
save('good_sub_corner', svg(body_sub_good))

body_sub_bad = (guides_outside(CX, TCY, S) + cap_top(CX, CY, S, CREAM) +
                 main_legend(CX, TCY, S, BROWN, '7') +
                 sub_legend(CX, TCY, S, BROWN, '/', *CORNER_BL) +   # falsch: unten links statt oben rechts
                 sub_legend(CX, TCY, S, BROWN, '{', *CORNER_BR))
save('bad_sub_wrong_corner', svg(body_sub_bad))

# ============ Bild 7 (rotiertes Motiv, Block A Zeile 4) ============
# Eigenes Motiv (Achtelnote) statt Shift-Pfeil, damit es sich von bad_shift_icon (Zeile 3)
# unterscheidet; Rotation deutlich (18 deg statt 9) + gestrichelte Soll-Achse (vertikal) zur
# Verdeutlichung, dass das Motiv von der Achse abweicht.
ROT_DEG = 18

def music_note(cx, cy, h):
    """Achtelnote (Notenkopf + Hals + Fähnchen) als SVG-Fragment, Bbox mittig, Hoehe h."""
    rx, ry = h * .20, h * .145
    head_cx, head_cy = cx - h * .10, cy + h * .33
    stem_x = head_cx + rx * .78
    stem_top = cy - h * .50
    stem_w = h * .075
    flag = (f'M{stem_x - stem_w/2:.1f},{stem_top:.1f} '
            f'C{stem_x + h*.30:.1f},{stem_top + h*.06:.1f} {stem_x + h*.34:.1f},{stem_top + h*.30:.1f} '
            f'{stem_x + h*.08:.1f},{stem_top + h*.42:.1f} '
            f'C{stem_x + h*.20:.1f},{stem_top + h*.22:.1f} {stem_x + h*.14:.1f},{stem_top + h*.10:.1f} '
            f'{stem_x - stem_w/2:.1f},{stem_top + h*.14:.1f} Z')
    return (f'<g transform="rotate(-18 {head_cx:.1f} {head_cy:.1f})">'
            f'<ellipse cx="{head_cx:.1f}" cy="{head_cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{CREAM}"/>'
            f'</g>'
            f'<rect x="{stem_x - stem_w/2:.1f}" y="{stem_top:.1f}" width="{stem_w:.1f}" height="{head_cy - stem_top:.1f}" fill="{CREAM}"/>'
            f'<path d="{flag}" fill="{CREAM}"/>')

def dashed_axis(cx, cy, s):
    """Duenne gestrichelte vertikale Soll-Achse (aufrecht) zum Rotationsvergleich."""
    e = s * .5 + 40
    return (f'<line x1="{cx:.1f}" y1="{cy-e:.1f}" x2="{cx:.1f}" y2="{cy+e:.1f}" '
            f'stroke="{GUIDE}" stroke-width="3" stroke-dasharray="10 8"/>')

ah2 = S * LEG * 1.35
rot_icon = f'<g transform="rotate({ROT_DEG} {CX} {TCY})">{music_note(CX, TCY, ah2)}</g>'
body_rot = guides_outside(CX, TCY, S) + cap_top(CX, CY, S, TAUPE) + dashed_axis(CX, TCY, S) + rot_icon
save('bad_rotated', svg(body_rot))
