"""
Werker-QS v3 (align-2): Gut/Schlecht-Bildpaare + ISO-Gut-Bilder aus den ECHTEN Kappen (Release-Export), je Design getrennt.

    py -3 _make_pairs_v3.py [--sets hello alpine] [--mm 0.8] [--override c02=1.0 alpine.c07.rot=-5]

Quelle je Design: {alpine_139|hello_v136}_board_clean.png + _bboxes.json  (Hello und Alpine werden nie gemischt).
Ausgabe (hier): {set}_v3_cNN_good.png / _bad.png, {set}_v3_iso_iN.png (nur gut), alpine_v3_rows.png,
plus ../../qs_v3_bad_offsets.json (gewaehlter Versatz je Bild).

GUT      = unveraenderte Kappen + gruene Hilfslinie(n) (#1a8a3c).
SCHLECHT = dieselben Kappen, bei GENAU EINER Kappe die Legende versetzt (Legenden-Pixel ausgeschnitten, Luecke mit der
           echten Kappenfarbe gefuellt, versetzt wieder eingesetzt); dieselben Linien in Rot (#c0182a).
Formate: Breite 2000 px, Hoehe passend zum Motiv (flache Kappenreihen ~5:2), schmaler grauer Rand; senkrechte Motive hochkant.
"""
import sys, io, os, json, argparse
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))

BG = (207, 203, 196)             # #CFCBC4
RIM_X, RIM_Y = 50, 70            # grauer Rand (px im Endbild)
MAX_W, MAX_H = 2000, 1800
GAP = 40                         # nativer Abstand bei Montagen (nebeneinander)
ROW_GAP = 34                     # nativer Abstand zwischen Montage-Zeilen
PX_MM = 11.811                   # 300 dpi
GOOD, BAD = (26, 138, 60), (192, 24, 42)      # frueherer Linienstil (nur noch fuer die Kontrastpruefung 'alt')
CORE, RIM = (255, 225, 74), (17, 17, 17)         # einheitlicher Linienstil: gelber Kern #FFE14A mit schwarzem Gegenrand #111
LINE_W = 5                                       # Kern (px im Endbild)
RIM_W = 2                                        # Gegenrand je Seite (px)
OTHERS = []                      # Bboxen aller Kappen des Designs
NO_LINES = False                 # nur fuer Sichtpruefung (--nolines schreibt nach D:/tmp, nie ins Repo)
BOARDS = {
    'alpine': ('alpine_139_board_clean.png', 'alpine_139_bboxes.json'),
    'hello':  ('hello_v136_board_clean.png', 'hello_v136_bboxes.json'),
}


def S(groups, target=None, mv=(0, 1), part='whole', rot=0, line='top', marks=None, mm=0.8, grid=None, canvas=None, line_keys=None, good_only=False, line2=None, cover_others=False):
    return dict(line2=line2, cover_others=cover_others, groups=groups, target=target, mv=mv, part=part, rot=rot, line=line, marks=marks, mm=mm, grid=grid, canvas=canvas, line_keys=line_keys, good_only=good_only)


def specs(set_name):
    a = set_name == 'alpine'
    r = lambda n, row: f'key_{n}_r{row}_face' if a else f'key_{n}_face'
    sp = {}
    sp['c01'] = S([[r('k', 3), r('l', 3), r('oe', 3)]], r('l', 3))
    sp['c02'] = S([[r('num_6', 5), r('num_7', 5), r('num_8', 5)]], r('num_7', 5), part='sub', mm=1.0)
    sp['c02a'] = S([[r('num_7', 5), r('num_8', 5), r('num_9', 5)]], r('num_8', 5), mv=(1, 0), part='altgr', mm=1.0, line='bottom',
                   marks='sub_center_each' if a else 'center_each')
    sp['c03'] = S([[r('f1', 6), r('f2', 6), r('f3', 6)]], r('f2', 6), marks='center_each')
    sp['c04'] = S([[r('altgr', 1), 'key_fn_r_r1_face' if a else 'key_fn_face', r('menu', 1)]], 'key_fn_r_r1_face' if a else 'key_fn_face',
                  marks='center_each', mm=1.0)
    if a:   # nur Alpine: Zusatzpruefungen links-rechts (Review 2026-10-07)
        sp['c01a'] = S([[r('k', 3), r('l', 3), r('oe', 3)]], r('l', 3), mv=(1, 0), marks='left_each', mm=1.0)
        sp['c04a'] = S([[r('altgr', 1), 'key_fn_r_r1_face', r('menu', 1)]], 'key_fn_r_r1_face', mv=(1, 0), marks='center_each', mm=1.0)
        sp['c06a'] = S([[r('einf', 5), r('pos1', 5), r('bild_up', 5)]], r('pos1', 5), mv=(1, 0), marks='center_each', mm=1.0)
        sp['c09a'] = S([[r('arrow_left', 1), r('arrow_down', 1), r('arrow_right', 1)]], r('arrow_down', 1), mv=(1, 0), line='center', marks='center_each', mm=1.0)
    if not a:   # nur Hello: Zusatzpruefungen links-rechts zentriert (Review 2026-10-07)
        sp['c03a'] = S([[r('f1', 6), r('f2', 6), r('f3', 6)]], r('f2', 6), mv=(1, 0), marks='center_each', mm=1.0)
        sp['c04a'] = S([[r('altgr', 1), 'key_fn_face', r('menu', 1)]], 'key_fn_face', mv=(1, 0), marks='center_each', mm=1.0)
        sp['c06a'] = S([[r('einf', 5), r('pos1', 5), r('bild_up', 5)]], r('pos1', 5), mv=(1, 0), marks='center_each', mm=1.0)
        sp['c09a'] = S([[r('arrow_left', 1), r('arrow_down', 1), r('arrow_right', 1)]], r('arrow_down', 1), mv=(1, 0), line='center', marks='center_each', mm=1.0)
    sp['c05'] = S([[r('shift_r', 2) if a else 'key_shift_r_2.75_face'], ['key_2u_shift_r2_face' if a else 'key_shift_2u_face']],
                  'key_2u_shift_r2_face' if a else 'key_shift_2u_face', mm=1.0)
    left4 = [r('tab', 4), r('caps', 3), r('shift_l', 2), r('ctrl_l', 1)]
    sp['c05a'] = S([left4], r('caps', 3), mv=(1, 0), line=None, marks='vline_left', mm=1.0, canvas='portrait')
    sp['c06'] = S([[r('einf', 5), r('pos1', 5), r('bild_up', 5)]], r('pos1', 5), mv=(0, -1), marks='center_each')
    sp['c07'] = S([[r('ae', 3), r('enter', 3)]], r('enter', 3), mv=(0, 0), rot=-5 if a else -3, line='shaft', marks='center_target', line2='top')
    esc, f1, f2 = r('esc', 6), r('f1', 6), r('f2', 6)
    logo = 'key_empty_r6_face' if a else 'key_hero_1'
    sp['c08'] = S([[esc, f1, f2], [logo]], logo, mv=(1, 0), line='top' if a else 'center', marks='center_target', mm=1.0,
                  line_keys=[esc, f1, f2, logo])
    sp['c09'] = S([[r('arrow_left', 1), r('arrow_down', 1), r('arrow_right', 1)]], r('arrow_down', 1), line='center')
    sp['c10'] = S([[r('numpad_7', 4), r('numpad_8', 4), r('numpad_9', 4)]], r('numpad_8', 4))
    # ---- ISO (nur gut)
    iso_enter = 'key_ISO_Enter_r4_r3_face' if a else 'key_enter_iso_face'
    sp['iso_i1'] = S([[iso_enter]], iso_enter, line='top', marks='center_target', good_only=True, cover_others=True)
    row1 = [r('num_2', 5), r('num_3', 5), r('num_7', 5), r('num_8', 5), r('num_9', 5), r('num_0', 5), r('ss', 5)]
    row2 = [r('q', 4), r('e', 4), r('plus', 4), r('less', 2), r('m', 2)]
    sp['iso_i2'] = S([[k] for k in row1 + row2], None, part='altgr', line='bottom', grid=[row1, row2], good_only=True)
    s125 = 'key_1.25u_shift_r2_face' if a else 'key_shift_1.25u_face'
    shr = 'key_shift_r_r2_face' if a else 'key_shift_r_2.75_face'
    sp['iso_i3'] = S([[s125], [shr]], None, line='top', good_only=True)
    sp['iso_i4'] = S([[r('less', 2)]], None, line=None, good_only=True)
    sp['iso_i5'] = S([[r('hash', 3)]], None, line=None, good_only=True)
    return sp


def ib(box):
    return [int(round(v)) for v in box]


def face_color(arr, box):
    x0, y0, x1, y1 = ib(box)
    sub = arr[y0:y1, x0:x1].astype(int)
    nw = sub.min(axis=2) < 250
    return np.median(sub[nw], axis=0).astype(np.uint8)


def ink_mask(arr, box, thr, m=10):
    """Legende = Pixel, die von der Kappenfarbe abweichen (nur Kappeninneres)."""
    x0, y0, x1, y1 = ib(box)
    sub = arr[y0:y1, x0:x1].astype(int)
    face = face_color(arr, box).astype(int)
    nw = sub.min(axis=2) < 250
    d = np.abs(sub - face).max(axis=2)
    inner = np.zeros(d.shape, bool)
    inner[m:-m, m:-m] = True
    ok = np.ones(d.shape, bool)
    for o in OTHERS:                      # Kappen, die in diese Bbox ragen (z. B. # in der ISO-Enter-Aussparung)
        ox0, oy0, ox1, oy1 = ib(o)
        if (ox0, oy0, ox1, oy1) == (x0, y0, x1, y1):
            continue
        ix0, iy0, ix1, iy1 = max(x0, ox0), max(y0, oy0), min(x1, ox1), min(y1, oy1)
        if ix1 > ix0 and iy1 > iy0:
            ok[iy0 - y0:iy1 - y0, ix0 - x0:ix1 - x0] = False
    shape = ndi.binary_erosion(nw & ok, iterations=14)          # Rand/Aussparungskante nicht als Legende zaehlen
    return (d > thr) & shape & inner, sub


def legend_part(arr, box, part, others=()):
    """tight bbox (Board-Koordinaten) + Rechteck inkl. Rand zum Ausschneiden. part: whole | sub | altgr."""
    x0, y0, x1, y1 = ib(box)
    w, h = x1 - x0, y1 - y0
    m = max(10, int(0.08 * min(w, h)))
    strong, sub = ink_mask(arr, box, 30, m)
    soft, _ = ink_mask(arr, box, 10, m)
    rb = sub[..., 0] - sub[..., 2]
    if part == 'altgr':
        strong = strong & (rb > 60)
        near = ndi.binary_dilation(strong, iterations=4)
        soft = soft & (rb > 20) & near
    elif part == 'sub':
        strong = strong & ~(rb > 60)
        lab, n = ndi.label(ndi.binary_dilation(strong, iterations=5))
        cand = []
        for i in range(1, n + 1):
            ys, xs = np.where((lab == i) & strong)
            if len(xs) == 0:
                continue
            if xs.mean() > .5 * w and ys.mean() < .5 * h:
                cand.append(i)
        assert len(cand) == 1, f'sub-Zeichen nicht eindeutig ({len(cand)})'
        region = ndi.binary_dilation(lab == cand[0], iterations=3)
        strong = strong & region
        soft = soft & region & ~(rb > 60)
    ys, xs = np.where(strong)
    tight = (x0 + xs.min(), y0 + ys.min(), x0 + xs.max() + 1, y0 + ys.max() + 1)
    ys2, xs2 = np.where(soft)
    pad = 3
    rect = (x0 + xs2.min() - pad, y0 + ys2.min() - pad, x0 + xs2.max() + 1 + pad, y0 + ys2.max() + 1 + pad)
    return dict(tight=tight, rect=rect, strong=strong, origin=(x0, y0))


def rotate_patch(patch, deg, face):
    h, w = patch.shape[:2]
    big = Image.fromarray(patch).resize((w * 4, h * 4), Image.BICUBIC)
    big = big.rotate(deg, resample=Image.BICUBIC, fillcolor=tuple(int(v) for v in face))
    return np.array(big.resize((w, h), Image.LANCZOS))


def crop_group(arr, boxes, keys, pad=3):
    ux0 = min(boxes[k][0] for k in keys); uy0 = min(boxes[k][1] for k in keys)
    ux1 = max(boxes[k][2] for k in keys); uy1 = max(boxes[k][3] for k in keys)
    o = (int(round(ux0)) - pad, int(round(uy0)) - pad)
    return arr[o[1]:int(round(uy1)) + pad, o[0]:int(round(ux1)) + pad].copy(), o


def mask_outside(c, o, boxes, keys, cover_others=False):
    allowed = np.zeros(c.shape[:2], bool)
    for k in keys:
        bx0, by0, bx1, by1 = ib(boxes[k])
        allowed[max(0, by0 - o[1] - 2):by1 - o[1] + 2, max(0, bx0 - o[0] - 2):bx1 - o[0] + 2] = True
    for k2, b2 in (boxes.items() if cover_others else []):   # andere Kappen, die in die Bbox ragen (z. B. # in der ISO-Enter-Aussparung), grau abdecken
        if k2 in keys:
            continue
        bx0, by0, bx1, by1 = ib(b2)
        x0_, y0_, x1_, y1_ = max(0, bx0 - o[0] - 1), max(0, by0 - o[1] - 1), min(c.shape[1], bx1 - o[0] + 1), min(c.shape[0], by1 - o[1] + 1)
        if x1_ > x0_ and y1_ > y0_:
            allowed[y0_:y1_, x0_:x1_] = False
    c = c.copy()
    c[~allowed] = BG
    c[allowed & (c.min(axis=2) >= 250)] = BG
    return c


def layout(crops, grid_rows):
    """Positionen (px,py) der Crops im Content; eine Zeile nebeneinander oder Raster."""
    pos = []
    if grid_rows is None:
        x = 0
        for c in crops:
            pos.append((x, 0)); x += c.shape[1] + GAP
        cw = x - GAP; ch = max(c.shape[0] for c in crops)
        return pos, cw, ch
    idx = 0; y = 0; cw = 0
    for row in grid_rows:
        x = 0; rh = 0
        for _ in row:
            c = crops[idx]; pos.append((x, y)); x += c.shape[1] + GAP; rh = max(rh, c.shape[0]); idx += 1
        cw = max(cw, x - GAP); y += rh + ROW_GAP
    return pos, cw, y - ROW_GAP


def build(arr, boxes, sp, off_px, rot_deg):
    groups = sp['groups']
    target = sp['target']
    allkeys = [k for g in groups for k in g]
    gof = {k: i for i, g in enumerate(groups) for k in g}
    crops, origins = zip(*[crop_group(arr, boxes, g) for g in groups])
    crops, origins = list(crops), list(origins)
    grid_rows = sp['grid']
    pos, cw, ch = layout([mask_outside(c, o, boxes, g, sp['cover_others']) for c, o, g in zip(crops, origins, groups)], grid_rows)

    if sp['part'] in ('sub', 'altgr'):
        meas = {k: legend_part(arr, boxes[k], sp['part']) for k in allkeys}
    else:
        meas = {k: legend_part(arr, boxes[k], 'whole') for k in allkeys}

    def content_xy(k, xn, yn):          # Board -> Content
        g = gof[k]
        return pos[g][0] + xn - origins[g][0], pos[g][1] + yn - origins[g][1]

    # ---- Linien (Content-Koordinaten)
    lines = []                           # (x0, y0, x1, y1) in Content-px (Rechteck-Mitte)
    lk = sp['line_keys'] or allkeys
    kind = sp['line']
    if kind in ('top', 'center', 'bottom'):
        rows = {}
        for k in lk:
            tt = meas[k]['tight']
            val = tt[1] if kind == 'top' else (tt[3] if kind == 'bottom' else (tt[1] + tt[3]) / 2)
            _, yc = content_xy(k, 0, val)
            g = gof[k]
            rows.setdefault(pos[g][1], []).append((yc, g))
        for ry, items in rows.items():
            yc = float(np.median([i[0] for i in items]))
            gs = [i[1] for i in items] if sp['line_keys'] is None else list(range(len(groups)))
            x0 = min(pos[g][0] for g in gs) - 12
            x1 = max(pos[g][0] + crops[g].shape[1] for g in gs) + 12
            lines.append(('h', yc, x0, x1, kind))
    elif kind == 'shaft':
        st = meas[target]['strong']
        rws = st.sum(axis=1)
        sel = np.where(rws >= .7 * rws.max())[0]
        yn = meas[target]['origin'][1] + float(sel.mean()) + .5
        _, yc = content_xy(target, 0, yn)
        bx0, _, bx1, _ = boxes[target]
        xa, _ = content_xy(target, bx0 - 14, 0); xb, _ = content_xy(target, bx1 + 14, 0)
        lines.append(('h', yc, xa, xb, 'shaft'))
    if sp['line2'] == 'top':               # zweite Linie: Legenden-Oberkante ueber die ganze Gruppe
        yt = float(np.median([content_xy(k, 0, meas[k]['tight'][1])[1] for k in allkeys]))
        xa = min(pos[g][0] for g in range(len(groups))) - 12
        xb = max(pos[g][0] + crops[g].shape[1] for g in range(len(groups))) + 12
        lines.append(('h', yt, xa, xb, 'top'))
    # ---- Marken
    marks = sp['marks']
    if marks in ('center_each', 'sub_center_each'):
        for k in allkeys:
            bx0, by0, bx1, by1 = boxes[k]
            if marks == 'sub_center_each':
                sp_ = legend_part(arr, boxes[k], 'sub')['tight']
                xn = (sp_[0] + sp_[2]) / 2
            else:
                xn = (bx0 + bx1) / 2
            xc, y0 = content_xy(k, xn, by0 - 16); _, y1 = content_xy(k, xn, by1 + 16)
            lines.append(('v', xc, y0, y1, 'v'))
    elif marks == 'center_target':
        tt = meas[target]['tight']
        bx0, by0, bx1, by1 = boxes[target]
        xn = (tt[0] + tt[2]) / 2
        xc, y0 = content_xy(target, xn, by0 - 16); _, y1 = content_xy(target, xn, by1 + 16)
        lines.append(('v', xc, y0, y1, 'v'))
    elif marks == 'left_each':           # je Taste eine Linie an der linken Soll-Kante (Median des Abstands Legende-Kappenkante)
        off = float(np.median([meas[k]['tight'][0] - boxes[k][0] for k in allkeys]))
        for k in allkeys:
            bx0, by0, bx1, by1 = boxes[k]
            xc, y0 = content_xy(k, bx0 + off, by0 - 16); _, y1 = content_xy(k, bx0 + off, by1 + 16)
            lines.append(('v', xc, y0, y1, 'v'))
    elif marks == 'vline_left':
        xn = float(np.median([meas[k]['tight'][0] for k in allkeys]))
        xc, y0 = content_xy(allkeys[0], xn, boxes[allkeys[0]][1] - 16)
        _, y1 = content_xy(allkeys[-1], xn, boxes[allkeys[-1]][3] + 16)
        lines.append(('v', xc, y0, y1, 'v'))

    # ---- Skalierung / Canvas
    s = min((MAX_W - 2 * RIM_X) / cw, (MAX_H - 2 * RIM_Y) / ch)
    if sp['canvas'] == 'portrait':
        s = (MAX_H - 2 * 60) / ch
        W, H = int(round(cw * s + 2 * 60)), MAX_H
        rx, ry = 60, 60
    else:
        W, H = int(round(cw * s + 2 * RIM_X)), int(round(ch * s + 2 * RIM_Y))
        rx, ry = RIM_X, RIM_Y

    def make_content(cs):
        m = np.zeros((ch, cw, 3), np.uint8); m[:] = BG
        for c, (px, py) in zip(cs, pos):
            m[py:py + c.shape[0], px:px + c.shape[1]] = c
        return m

    good_cs = [mask_outside(c, o, boxes, g, sp['cover_others']) for c, o, g in zip(crops, origins, groups)]

    bad_cs = None
    info = dict(target=target, part=sp['part'], keys=allkeys, line=kind, marks=marks, scale=round(s, 3), canvas=[W, H])
    if target is not None and not sp['good_only']:
        bad_raw = [c.copy() for c in crops]
        gi = gof[target]
        lp = legend_part(arr, boxes[target], sp['part'])
        face = face_color(arr, boxes[target])
        rx0, ry0, rx1, ry1 = lp['rect']
        ox, oy = origins[gi]
        cx0, cy0, cx1, cy1 = rx0 - ox, ry0 - oy, rx1 - ox, ry1 - oy
        dx = int(sp['mv'][0] * off_px); dy = int(sp['mv'][1] * off_px)
        crop = bad_raw[gi]
        patch = crop[cy0:cy1, cx0:cx1].copy()
        tgt = (cx0 + dx, cy0 + dy, cx1 + dx, cy1 + dy)
        orig_ref = crops[gi]
        chk = np.abs(orig_ref[tgt[1]:tgt[3], tgt[0]:tgt[2]].astype(int) - face.astype(int)).max(axis=2) > 14
        own = np.zeros_like(chk)
        sx0, sy0 = max(cx0, tgt[0]) - tgt[0], max(cy0, tgt[1]) - tgt[1]
        sx1, sy1 = min(cx1, tgt[2]) - tgt[0], min(cy1, tgt[3]) - tgt[1]
        if sx1 > sx0 and sy1 > sy0:
            own[sy0:sy1, sx0:sx1] = True
        kx0, ky0, kx1, ky1 = ib(boxes[target])
        assert tgt[0] + ox >= kx0 + 8 and tgt[2] + ox <= kx1 - 8 and tgt[1] + oy >= ky0 + 8 and tgt[3] + oy <= ky1 - 8, 'Legende wuerde abgeschnitten'
        assert not (chk & ~own).any(), 'Ziel nicht frei (Ueberlappung mit anderer Legende)'
        crop[cy0:cy1, cx0:cx1] = face
        if rot_deg:
            patch = rotate_patch(patch, rot_deg, face)
        crop[tgt[1]:tgt[3], tgt[0]:tgt[2]] = patch
        bad_cs = [mask_outside(c, o, boxes, g, sp['cover_others']) for c, o, g in zip(bad_raw, origins, groups)]
        info.update(dx_px=dx, dy_px=dy, rot_deg=rot_deg)

    def rl(c):                          # WCAG relative Luminanz
        v = np.array(c, float) / 255.0
        v = np.where(v <= 0.03928, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)
        return float(0.2126 * v[..., 0] + 0.7152 * v[..., 1] + 0.0722 * v[..., 2]) if v.ndim == 1 else 0.2126 * v[..., 0] + 0.7152 * v[..., 1] + 0.0722 * v[..., 2]

    def contrast(c1, px):               # c1 gegen Pixelarray (n,3) -> Kontrastverhaeltnis je Pixel
        l1 = rl(c1); l2 = rl(px)
        hi = np.maximum(l1, l2); lo = np.minimum(l1, l2)
        return (hi + .05) / (lo + .05)

    def segments():
        """(x0, y0, x1, y1) je Linie im Endbild (Mittelpunktskoordinaten des Kerns, Breite LINE_W)."""
        out = []
        for kind_, c0, a, b, lk_ in lines:
            if kind_ == 'h':
                y = ry + c0 * s
                if lk_ == 'top':
                    y -= LINE_W / 2 + RIM_W + 1       # knapp UEBER der Legenden-Oberkante, verdeckt die Legende nicht
                elif lk_ == 'bottom':
                    y += LINE_W / 2 + RIM_W + 1       # knapp UNTER der Legenden-Unterkante
                out.append((max(4, rx + a * s), y, min(W - 4, rx + b * s), y))
            else:
                x = rx + c0 * s
                if sp['marks'] in ('vline_left', 'left_each') and lk_ == 'v':
                    x -= LINE_W / 2 + RIM_W + 1
                out.append((x, ry + a * s, x, ry + b * s))
        return out

    def render(cs, col=None):
        im = Image.fromarray(make_content(cs)).resize((int(round(cw * s)), int(round(ch * s))), Image.LANCZOS)
        cv = Image.new('RGB', (W, H), BG)
        cv.paste(im, (rx, ry))
        if NO_LINES:
            return cv
        d = ImageDraw.Draw(cv)
        segs = segments()
        for grow, colr in ((LINE_W / 2 + RIM_W, RIM), (LINE_W / 2, CORE)):      # erst alle Raender, dann alle Kerne (saubere Kreuzungen)
            for x0, y0, x1, y1 in segs:
                d.rectangle([x0 - (grow if x0 == x1 else 0), y0 - (grow if y0 == y1 else 0), x1 + (grow if x0 == x1 else 0), y1 + (grow if y0 == y1 else 0)], fill=colr)
        return cv

    def line_contrast(cs):
        """Kontrast unter den Linien (10. Perzentil ueber die Pixel auf der Linienmitte, inkl. Gegenrand): neu und alter Stil."""
        if not lines:
            return None
        base = np.array(Image.fromarray(make_content(cs)).resize((int(round(cw * s)), int(round(ch * s))), Image.LANCZOS))
        canvas = np.zeros((H, W, 3), np.uint8); canvas[:] = BG
        canvas[ry:ry + base.shape[0], rx:rx + base.shape[1]] = base
        px = []
        for x0, y0, x1, y1 in segments():
            if x0 == x1:
                px.append(canvas[int(y0):int(y1), int(round(x0))])
            else:
                px.append(canvas[int(round(y0)), int(x0):int(x1)])
        px = np.concatenate(px).astype(float)
        eff = np.maximum(contrast(CORE, px), contrast(RIM, px))
        return dict(neu_p10=round(float(np.percentile(eff, 10)), 1), neu_min=round(float(eff.min()), 1),
                    kern_p10=round(float(np.percentile(contrast(CORE, px), 10)), 1), rand_p10=round(float(np.percentile(contrast(RIM, px), 10)), 1),
                    alt_gruen_p10=round(float(np.percentile(contrast(GOOD, px), 10)), 1), alt_rot_p10=round(float(np.percentile(contrast(BAD, px), 10)), 1))

    spread = None
    if kind in ('top', 'center', 'bottom') and not grid_rows:
        vals = [(meas[k]['tight'][1] if kind == 'top' else (meas[k]['tight'][3] if kind == 'bottom' else (meas[k]['tight'][1] + meas[k]['tight'][3]) / 2)) for k in lk]
        spread = round(float(np.ptp(vals)), 1)
    info['line_spread_px'] = spread
    info['linienkontrast'] = line_contrast(good_cs)
    return render(good_cs), (render(bad_cs) if bad_cs else None), info


def run(sets, mm, overrides, outdir=None):
    out_json = {}
    for set_name in sets:
        board, bbf = BOARDS[set_name]
        arr = np.array(Image.open(os.path.join(HERE, board)).convert('RGB'))
        with open(os.path.join(HERE, bbf), 'r', encoding='utf-8') as f:
            boxes = json.load(f)
        OTHERS[:] = list(boxes.values())
        out_json[set_name] = {}
        for cid, sp in specs(set_name).items():
            m = overrides.get(f'{set_name}.{cid}', overrides.get(cid, sp['mm'] if sp['mm'] != 0.8 else mm))
            off_px = int(round(m * PX_MM))
            rd = sp['rot']
            if rd:
                rd = overrides.get(f'{set_name}.{cid}.rot', overrides.get(f'{cid}.rot', rd))
            good, bad, info = build(arr, boxes, sp, off_px, rd)
            tag = f'{set_name}_v3_{cid}'
            if NO_LINES:
                good.save(f'D:/tmp/nolines_{tag}_good.png')
                if bad: bad.save(f'D:/tmp/nolines_{tag}_bad.png')
            elif bad is None:
                good.save(os.path.join(HERE, f'{tag}.png'))
            else:
                good.save(os.path.join(HERE, f'{tag}_good.png')); bad.save(os.path.join(HERE, f'{tag}_bad.png'))
            if bad is not None:
                info['offset_mm'] = None if sp['rot'] else m
                info['offset_px'] = None if sp['rot'] else off_px
            out_json[set_name][cid] = info
            print(f'[OK] {tag}  ' + (f'Versatz {m} mm = {off_px} px  rot {rd}  ' if bad is not None else 'nur gut  ') + f'canvas {info["canvas"]}  s={info["scale"]}  kontrast={info["linienkontrast"]}')
    return out_json


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--sets', nargs='+', default=['hello', 'alpine'])
    ap.add_argument('--mm', type=float, default=0.8)
    ap.add_argument('--nolines', action='store_true')
    ap.add_argument('--override', nargs='*', default=[], help='z.B. c02=1.0 alpine.c09=1.0 c07.rot=-5')
    a = ap.parse_args()
    ov = {}
    for o in a.override:
        k, v = o.split('=')
        ov[k] = float(v)
    NO_LINES = a.nolines
    res = run(a.sets, a.mm, ov)
    if a.nolines:
        sys.exit(0)
    p = os.path.join(HERE, '..', '..', 'qs_v3_bad_offsets.json')
    old = json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}
    for s_, v in res.items():
        old[s_] = v
    json.dump(old, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
    src = os.path.join(HERE, 'alpine_v3_plan_rows.png')
    if 'alpine' in a.sets and os.path.exists(src):
        im = Image.open(src)
        im = im.resize((2400, int(round(im.height * 2400 / im.width))), Image.LANCZOS)
        im.save(os.path.join(HERE, 'alpine_v3_rows.png'), optimize=True)
        print('[OK] alpine_v3_rows.png', im.size)
