"""
Misst aus den Export-Pixeln (je Design getrennt), ob die Soll-Regeln der Ausrichtung im Release wirklich so umgesetzt sind.
Ergebnis: ../../qs_v3_align_facts.json  (+ Kurzfassung auf stdout)

    py -3 _measure_align_v3.py [--sets hello alpine]

Legende = Pixel, die von der Kappenfarbe abweichen (Kappeninneres, Rand 10 px). 11,811 px/mm (300 dpi).
"""
import sys, io, os, json, argparse
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
PX_MM = 11.811
BOARDS = {
    'alpine': ('alpine_139_board_clean.png', 'alpine_139_bboxes.json'),
    'hello':  ('hello_v136_board_clean.png', 'hello_v136_bboxes.json'),
}


def ib(b):
    return [int(round(v)) for v in b]


def face_color(arr, box):
    x0, y0, x1, y1 = ib(box)
    sub = arr[y0:y1, x0:x1].astype(int)
    nw = sub.min(axis=2) < 250
    return np.median(sub[nw], axis=0)


OTHERS = []     # Bboxen der uebrigen Kappen (werden innerhalb einer Bbox ausgeblendet)


def ink(arr, box, thr=30, m=None):
    x0, y0, x1, y1 = ib(box)
    if m is None:
        m = max(10, int(0.08 * min(x1 - x0, y1 - y0)))     # grosse Eckenradien (ISO-Enter) nicht als Legende zaehlen
    sub = arr[y0:y1, x0:x1].astype(int)
    d = np.abs(sub - face_color(arr, box)).max(axis=2)
    inner = np.zeros(d.shape, bool); inner[m:-m, m:-m] = True
    ok = np.ones(d.shape, bool)
    for o in OTHERS:
        ox0, oy0, ox1, oy1 = ib(o)
        if (ox0, oy0, ox1, oy1) == (x0, y0, x1, y1):
            continue
        ix0, iy0, ix1, iy1 = max(x0, ox0), max(y0, oy0), min(x1, ox1), min(y1, oy1)
        if ix1 > ix0 and iy1 > iy0:
            ok[iy0 - y0:iy1 - y0, ix0 - x0:ix1 - x0] = False
    shape = ndi.binary_erosion((sub.min(axis=2) < 250) & ok, iterations=14)      # Kappenrand/Aussparungskante nicht als Legende zaehlen
    return (d > thr) & shape & inner, sub


def bbox_of(mask):
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def legend(arr, box):
    """Gesamtlegende: bbox relativ zur Kappe (px)."""
    m, _ = ink(arr, box)
    return bbox_of(m)


def stats(vals):
    v = np.array(vals, float)
    return dict(n=len(v), median=round(float(np.median(v)), 2), min=round(float(v.min()), 2), max=round(float(v.max()), 2),
                spread=round(float(v.max() - v.min()), 2))


def mm(px):
    return px / PX_MM


def parts(arr, box):
    """main (dunkel links), sub (dunkel oben rechts), altgr (rot/terracotta) als bbox relativ zur Kappe."""
    x0, y0, x1, y1 = ib(box)
    w, h = x1 - x0, y1 - y0
    m, sub = ink(arr, box)
    r_b = sub[..., 0] - sub[..., 2]
    altgr = m & (r_b > 60)
    dark = m & ~(r_b > 60)
    lab, n = ndi.label(ndi.binary_dilation(dark, iterations=5))
    main_bb = sub_bb = None
    for i in range(1, n + 1):
        mk = (lab == i) & dark
        if not mk.any():
            continue
        bb = bbox_of(mk); cx = (bb[0] + bb[2]) / 2; cy = (bb[1] + bb[3]) / 2
        if cx > .5 * w and cy < .55 * h:
            sub_bb = bb
        elif main_bb is None or bb[2] - bb[0] > main_bb[2] - main_bb[0]:
            main_bb = bb
    a_bb = bbox_of(altgr)
    return dict(main=main_bb, sub=sub_bb, altgr=a_bb, w=w, h=h)


def run(set_name):
    board, bbf = BOARDS[set_name]
    arr = np.array(Image.open(os.path.join(HERE, board)).convert('RGB'))
    boxes = json.load(open(os.path.join(HERE, bbf), encoding='utf-8'))
    cl = json.load(open(os.path.join(HERE, '..', '..', 'qs_v3_clusters.json'), encoding='utf-8'))
    keys = {k['name']: k for k in cl['sets'][set_name]['keys']}
    OTHERS[:] = list(boxes.values())
    res = {}

    # ---- a) horizontale Mitte: Legendenmitte - Kappenmitte (mm) je Cluster 3, 4, 6, 7
    a = {}
    for cid, cname in [(3, 'F-Reihe'), (4, 'Mod'), (6, 'Navigation'), (7, 'Enter')]:
        per = {}
        for k, v in keys.items():
            if v['cluster'] != cid:
                continue
            bb = legend(arr, boxes[k])
            if bb is None:
                continue
            w = boxes[k][2] - boxes[k][0]
            per[k] = round(mm((bb[0] + bb[2]) / 2 - w / 2), 2)
        a[cname] = dict(stats=stats(list(per.values())), per_key=per,
                        ausreisser={k: v for k, v in per.items() if abs(v) > 0.3})
    res['a_horizontal_mitte_mm'] = a

    # ---- b) linke Spalte: Tab, Caps, linkes Shift, linkes Strg
    names_b = {
        'alpine': ['key_tab_r4_face', 'key_caps_r3_face', 'key_shift_l_r2_face', 'key_ctrl_l_r1_face'],
        'hello': ['key_tab_face', 'key_caps_face', 'key_shift_l_face', 'key_ctrl_l_face'],
    }[set_name]
    b = {}
    for k in names_b:
        bb = legend(arr, boxes[k])
        x0 = boxes[k][0]
        b[k] = dict(face_x0=int(boxes[k][0]), face_w=int(boxes[k][2] - boxes[k][0]),
                    legend_left_abs=int(x0 + bb[0]), legend_right_abs=int(x0 + bb[2]),
                    legend_center_abs=round(x0 + (bb[0] + bb[2]) / 2, 1),
                    legend_left_rel_mm=round(mm(bb[0]), 2), legend_center_rel_mm=round(mm((bb[0] + bb[2]) / 2), 2))
    lefts = [v['legend_left_abs'] for v in b.values()]
    cents = [v['legend_center_abs'] for v in b.values()]
    res['b_linke_spalte'] = dict(per_key=b, spread_left_edge_mm=round(mm(max(lefts) - min(lefts)), 2),
                                 spread_center_mm=round(mm(max(cents) - min(cents)), 2),
                                 face_x0_spread_mm=round(mm(max(v['face_x0'] for v in b.values()) - min(v['face_x0'] for v in b.values())), 2))

    # ---- c) AltGr-Zeichen
    ak = [n for n in keys if any(t in n for t in ('num_2', 'num_3', 'num_7', 'num_8', 'num_9', 'num_0', 'key_ss', 'key_plus', 'key_less', 'key_q', 'key_e_', 'key_e', 'key_m'))
          and 'numpad' not in n]
    ak = [n for n in ak if keys[n]['cluster'] in (1, 2) and 'altgr' in keys[n]]
    c = {}
    for k in ak:
        p = parts(arr, boxes[k])
        if p['altgr'] is None:
            continue
        w = p['w']
        acx = (p['altgr'][0] + p['altgr'][2]) / 2
        e = dict(altgr=keys[k]['altgr'], altgr_cx_minus_face_cx_mm=round(mm(acx - w / 2), 2),
                 face_right_minus_altgr_cx_mm=round(mm(w - acx), 2),
                 altgr_left_from_face_left_mm=round(mm(p['altgr'][0]), 2))
        if p['sub'] is not None:
            scx = (p['sub'][0] + p['sub'][2]) / 2
            e['sub'] = keys[k].get('sub')
            e['altgr_cx_minus_sub_cx_mm'] = round(mm(acx - scx), 2)
            e['sub_cx_minus_face_cx_mm'] = round(mm(scx - w / 2), 2)
            e['face_right_minus_sub_cx_mm'] = round(mm(w - scx), 2)
        e['altgr_top_rel_mm'] = round(mm(p['altgr'][1]), 2); e['altgr_bottom_rel_mm'] = round(mm(p['altgr'][3]), 2)
        e['altgr_center_y_rel_mm'] = round(mm((p['altgr'][1] + p['altgr'][3]) / 2), 2)
        if p['sub'] is not None:
            e['sub_top_rel_mm'] = round(mm(p['sub'][1]), 2); e['sub_bottom_rel_mm'] = round(mm(p['sub'][3]), 2)
        c[k] = e
    def col(key):
        return [v[key] for v in c.values() if key in v]
    res['c_altgr_vertikal'] = dict(top=stats(col('altgr_top_rel_mm')), mitte=stats(col('altgr_center_y_rel_mm')), unterkante=stats(col('altgr_bottom_rel_mm')),
                                   sub_oberkante=stats(col('sub_top_rel_mm')) if col('sub_top_rel_mm') else None,
                                   ohne_2_3_top=stats([v['altgr_top_rel_mm'] for kk, v in c.items() if 'num_2' not in kk and 'num_3' not in kk]),
                                   ohne_2_3_unterkante=stats([v['altgr_bottom_rel_mm'] for kk, v in c.items() if 'num_2' not in kk and 'num_3' not in kk]))
    res['c_altgr'] = dict(per_key=c,
                          zur_kappenmitte=stats(col('altgr_cx_minus_face_cx_mm')),
                          zum_rechten_rand=stats(col('face_right_minus_altgr_cx_mm')),
                          zur_shift_zeichen_mitte=stats(col('altgr_cx_minus_sub_cx_mm')) if col('altgr_cx_minus_sub_cx_mm') else None)

    # ---- d) Cluster 8: Esc/Logo auf der F-Reihen-Linie? Novelty untereinander?
    frow = [k for k, v in keys.items() if v['cluster'] == 3]
    def vert(k):
        bb = legend(arr, boxes[k]); return bb[1], (bb[1] + bb[3]) / 2, bb[3]
    fv = [vert(k) for k in frow]
    f_top = float(np.median([v[0] for v in fv])); f_cen = float(np.median([v[1] for v in fv])); f_bot = float(np.median([v[2] for v in fv]))
    f_face_y0 = sorted(set(int(boxes[k][1]) for k in frow))
    cand = {'alpine': ['key_esc_r6_face', 'key_empty_r6_face', 'key_exit_r6_face'],
            'hello': ['key_esc_face', 'key_hero_1', 'key_hero_2']}[set_name]
    d = dict(f_reihe=dict(face_y0=f_face_y0, legend_top_rel_px=f_top, legend_center_rel_px=f_cen,
                          streuung_top_px=float(np.ptp([v[0] for v in fv])), streuung_center_px=float(np.ptp([v[1] for v in fv]))), esc_logo={})
    for k in cand:
        t, cn, bt = vert(k)
        d['esc_logo'][k] = dict(face_y0=int(boxes[k][1]), legend_top_rel_px=float(t), legend_center_rel_px=float(cn),
                                top_minus_frow_mm=round(mm(t - f_top), 2), center_minus_frow_mm=round(mm(cn - f_cen), 2),
                                bottom_minus_frow_mm=round(mm(bt - f_bot), 2))
    nov = {'alpine': ['key_fancy_1_r6_face', 'key_fancy_2_r6_face', 'key_fancy_3_r6_face'],
           'hello': ['key_note_face', 'key_disk_face', 'key_eq_face', 'key_dial_face', 'key_mic_face', 'key_note_2_face']}[set_name]
    nv = {k: dict(face_y0=int(boxes[k][1]), face_x0=int(boxes[k][0]), legend_center_y_abs=round(boxes[k][1] + vert(k)[1], 1),
                  legend_top_y_abs=round(boxes[k][1] + vert(k)[0], 1), legend_center_x_rel_mm=round(mm((legend(arr, boxes[k])[0] + legend(arr, boxes[k])[2]) / 2 - (boxes[k][2] - boxes[k][0]) / 2), 2)) for k in nov}
    d['novelty'] = dict(per_key=nv, face_y0_streuung_px=float(np.ptp([v['face_y0'] for v in nv.values()])),
                        legend_center_y_streuung_mm=round(mm(float(np.ptp([v['legend_center_y_abs'] for v in nv.values()]))), 2),
                        legend_center_rel_streuung_mm=round(mm(float(np.ptp([v['legend_center_y_abs'] - v['face_y0'] for v in nv.values()]))), 2))
    res['d_cluster8'] = d

    # ---- e) ISO-Kappen laut Bestand
    iso_names = {
        'alpine': {'ISO-Enter': 'key_ISO_Enter_r4_r3_face', 'Shift 1,25U kurz': 'key_1.25u_shift_r2_face', '< > |': 'key_less_r2_face',
                   '# \' ISO 1U': 'key_hash_r3_face', '# \' 1,5U (ANSI)': 'key_hash_r4_face'},
        'hello': {'ISO-Enter': 'key_enter_iso_face', 'Shift 1,25U kurz': 'key_shift_1.25u_face', '< > |': 'key_less_face',
                  '# \' ISO 1U': 'key_hash_face', '# \' 1,5U (ANSI)': 'key_hash_ansi'},
    }[set_name]
    e = {}
    for label, k in iso_names.items():
        b0 = boxes[k]; w = b0[2] - b0[0]; h = b0[3] - b0[1]
        e[label] = dict(name=k, w_px=int(w), h_px=int(h), w_u=round(w / 225.0, 2), h_u=round(h / 225.0, 2), cluster=keys[k]['cluster'], legend=keys[k]['legend'],
                        sub=keys[k].get('sub'), altgr=keys[k].get('altgr'), block='Hauptboard' if b0[1] < 2400 else 'Zusatzkappen (unter dem Board)')
    kiso = iso_names['ISO-Enter']
    bx = ib(boxes[kiso]); fw, fh = bx[2] - bx[0], bx[3] - bx[1]
    sub = arr[bx[1]:bx[3], bx[0]:bx[2]].astype(int)
    oth = np.zeros(sub.shape[:2], bool)
    for o in OTHERS:
        ob = ib(o)
        if ob == bx: continue
        ix0, iy0, ix1, iy1 = max(bx[0], ob[0]), max(bx[1], ob[1]), min(bx[2], ob[2]), min(bx[3], ob[3])
        if ix1 > ix0 and iy1 > iy0: oth[iy0 - bx[1]:iy1 - bx[1], ix0 - bx[0]:ix1 - bx[0]] = True
    shape = (sub.min(axis=2) < 250) & ~oth
    wid = shape.sum(axis=1)
    top_rows = np.where(wid >= .95 * wid.max())[0]; low_rows = np.where((wid <= .92 * wid.max()) & (wid > 20))[0]
    xs_top = np.where(shape[top_rows[len(top_rows) // 2]])[0]
    xs_low = np.where(shape[low_rows[len(low_rows) // 2]])[0]
    L = legend(arr, boxes[kiso])
    lc = (L[0] + L[2]) / 2
    e['_iso_enter_geometrie'] = dict(bbox_w_px=fw, bbox_h_px=fh, oberer_teil_x=[int(xs_top.min()), int(xs_top.max())], unterer_teil_x=[int(xs_low.min()), int(xs_low.max())],
        legenden_mitte_x=round(float(lc), 1), legenden_mitte_minus_bbox_mitte_mm=round(mm(lc - fw / 2), 2),
        legenden_mitte_minus_oberer_teil_mitte_mm=round(mm(lc - (xs_top.min() + xs_top.max()) / 2), 2),
        legenden_mitte_minus_unterer_teil_mitte_mm=round(mm(lc - (xs_low.min() + xs_low.max()) / 2), 2),
        legenden_mitte_y_rel_mm=round(mm((L[1] + L[3]) / 2), 2), oberer_teil_hoehe_mm=round(mm(float(len(top_rows))), 2))
    res['e_iso_kappen'] = e
    return res


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--sets', nargs='+', default=['hello', 'alpine'])
    a = ap.parse_args()
    out = {'hinweis': 'gemessen aus den Export-Pixeln (alpine_139 / hello_v136), 11,811 px/mm; je Design getrennt'}
    for s in a.sets:
        out[s] = run(s)
    p = os.path.join(HERE, '..', '..', 'qs_v3_align_facts.json')
    json.dump(out, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
    for s in a.sets:
        r = out[s]
        print('==', s)
        for n, v in r['a_horizontal_mitte_mm'].items():
            print(' a', n, v['stats'], 'Ausreisser>0.3mm:', v['ausreisser'])
        bb = r['b_linke_spalte']
        print(' b Spalte: Streuung linke Legendenkante', bb['spread_left_edge_mm'], 'mm, Mitte', bb['spread_center_mm'], 'mm, Face-x0', bb['face_x0_spread_mm'])
        for k, v in bb['per_key'].items():
            print('    ', k, v)
        cc = r['c_altgr']
        print(' c zur Kappenmitte', cc['zur_kappenmitte']); print('   zum rechten Rand', cc['zum_rechten_rand']); print('   zur Shift-Zeichen-Mitte', cc['zur_shift_zeichen_mitte'])
        d = r['d_cluster8']
        print(' d F-Reihe', d['f_reihe']); print('   esc/logo', d['esc_logo']); print('   novelty', {k: v for k, v in d['novelty'].items() if k != 'per_key'})
        print(' e', {k: (v['name'], v['w_u'], v['h_u']) for k, v in r['e_iso_kappen'].items() if 'name' in v})
