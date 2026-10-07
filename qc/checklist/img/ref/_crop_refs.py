"""
Crop reference key/row images from the 300dpi board renders for the QC checklist.

Usage:
    py -3 _crop_refs.py --variant lines
    py -3 _crop_refs.py --variant clean
    py -3 _crop_refs.py --variant qc
    py -3 _crop_refs.py --variant v3      # Werker-QS v3: {set}_v3_c01..c10 + {set}_v3_sharp (Boards Alpine 139 / Hello v1.36)
    py -3 _crop_refs.py --variant plan    # Belegungsplaene {set}_v3_plan_clusters (+ alpine_v3_plan_rows), qs_v3_colors.json

Inputs (in this directory):
    {set}_board_300dpi.png        -- board render with contour lines (designer guide)
    {set}_board_300dpi_clean.png  -- board render without contour lines (checklist)
    {set}_bboxes.json             -- face bboxes [x0,y0,x1,y1] in image px, 1:1 with the board render

Outputs (in this directory):
    {set}_{crop}.png        (variant=clean, no suffix -- used by the checklist v2 rows 1-4, superseded
                              by qc_c1..qc_c4 for that use, kept for other rows/the designer guide)
    {set}_{crop}_lines.png  (variant=lines  -- used by the designer guide)
    {set}_qc_c1..c4.png     (variant=qc     -- checklist v2 rows 1-4 "good" images: at most 2 keys,
                              padded onto a fixed, neutral-gray 3:2 canvas so small icon keys read
                              large instead of shrinking inside a wide row crop)

Crop definitions: see CROPS / QC_CROPS below. Each named crop is a list of "clusters"
(key-id groups). A cluster is cropped as the union bbox of its keys plus a small margin
of a standard 1u key width. Multiple clusters (keys that do not sit in the same row/
neighbourhood) are cropped individually and then montaged side by side at equal height
with a gap, instead of being merged into one huge bbox with dead space in between.
"""
import sys
import io
import os
import json
import argparse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from PIL import Image, ImageDraw, ImageFont
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

# key-id clusters per named crop, per set.
# a crop with >1 cluster is montaged side by side (equal height, 20px gap).
CROPS = {
    'hello': {
        'c1_row': [['key_k', 'key_l', 'key_oe', 'key_ae']],
        'c1_key': [['key_a']],
        'c2_row': [['key_num_1', 'key_num_2', 'key_num_3', 'key_num_4', 'key_num_5']],
        'c2_key': [['key_num_7']],
        'c3_row': [['key_shift_l'], ['key_backspace', 'key_pos1'], ['key_entf'], ['key_arrow_up']],
        'c3_key': [['key_arrow_up']],
        'c4': [['novelty_note', 'novelty_vinyl', 'novelty_eq', 'novelty_dial']],
    },
    'alpine': {
        'c1_row': [['key_k', 'key_l', 'key_oe', 'key_ae']],
        'c1_key': [['key_a']],
        'c2_row': [['key_num_1', 'key_num_2', 'key_num_3', 'key_num_4', 'key_num_5']],
        'c2_key': [['key_num_7']],
        'c3_row': [['key_shift_l'], ['key_tab'], ['key_entf'], ['key_arrow_up'], ['key_f1']],
        'c3_key': [['key_arrow_up']],
        'c4': [['key_esc'], ['key_empty'], ['key_ISO_Enter_r3'], ['key_space_left_third']],
        'check_dash': [['key_dash', 'key_colon']],
    },
}

# qc_c1..c4: checklist-only "good" crops, at most 2 keys, fitted onto a fixed 3:2
# neutral-gray canvas (keys stay large, no CSS letterboxing needed downstream).
# Single-cluster entries use a plain union-bbox crop (fine when the keys are adjacent,
# e.g. K..Oe with L in between -- no dead space). Multi-cluster entries (keys far apart)
# are montaged from tight individual crops so neither key shrinks to fit the gap.
QC_CROPS = {
    'hello': {
        'qc_c1': [['key_k', 'key_oe']],           # K + Oe (L sits between them, shown too)
        'qc_c2': [['key_num_7']],
        'qc_c3': [['key_arrow_up']],                # 1U icon key, centred -- key_shift_l (wide key,
                                                     # icon sits left-aligned) contradicted "centred?"
        'qc_c4': [['novelty_note', 'novelty_vinyl']],
    },
    'alpine': {
        'qc_c1': [['key_k', 'key_oe']],
        'qc_c2': [['key_num_7']],
        'qc_c3': [['key_arrow_up']],                # see README note below on the c3 choice
        'qc_c4': [['key_esc'], ['key_empty']],      # far apart on the board -> montaged, not unioned
    },
}

QC_CANVAS = (1500, 1000)   # exactly 3:2
QC_FILL = 0.94             # fraction of the canvas the (montaged) crop is scaled to fit
QC_BG = (207, 203, 196)    # ~#CFCBC4, neutral mid-gray so light/cream caps stand out
QC_GAP = 40                # px between montaged clusters in the qc variant (on QC_BG)

GAP = 20  # px between montaged clusters (variant lines/clean, on white)


def load_bboxes(set_name):
    with open(os.path.join(HERE, f'{set_name}_bboxes.json'), 'r', encoding='utf-8') as f:
        boxes = json.load(f)
    # synthetic: left third of the spacebar
    if 'key_space' in boxes:
        x0, y0, x1, y1 = boxes['key_space']
        third = (x1 - x0) / 3.0
        boxes['key_space_left_third'] = [x0, y0, x0 + third, y1]
    return boxes


def union_bbox(boxes, key_ids):
    xs0, ys0, xs1, ys1 = [], [], [], []
    for k in key_ids:
        x0, y0, x1, y1 = boxes[k]
        xs0.append(x0); ys0.append(y0); xs1.append(x1); ys1.append(y1)
    return min(xs0), min(ys0), max(xs1), max(ys1)


def crop_cluster(img, boxes, key_ids, pad):
    x0, y0, x1, y1 = union_bbox(boxes, key_ids)
    x0 = max(0, int(round(x0 - pad)))
    y0 = max(0, int(round(y0 - pad)))
    x1 = min(img.width, int(round(x1 + pad)))
    y1 = min(img.height, int(round(y1 + pad)))
    return img.crop((x0, y0, x1, y1))


def montage(crops, gap=GAP, bg=(255, 255, 255)):
    if len(crops) == 1:
        return crops[0]
    target_h = max(c.height for c in crops)
    resized = []
    for c in crops:
        if c.height != target_h:
            w = int(round(c.width * target_h / c.height))
            c = c.resize((w, target_h), Image.LANCZOS)
        resized.append(c)
    total_w = sum(c.width for c in resized) + gap * (len(resized) - 1)
    canvas = Image.new('RGB', (total_w, target_h), bg)
    x = 0
    for c in resized:
        canvas.paste(c, (x, 0))
        x += c.width + gap
    return canvas


def pad_to_canvas(img, canvas_size, fill, bg):
    """Scale img (no stretch, no crop) to fit within `fill` of canvas_size, centered on bg."""
    cw, ch = canvas_size
    scale = min(cw * fill / img.width, ch * fill / img.height)
    w, h = int(round(img.width * scale)), int(round(img.height * scale))
    resized = img.resize((w, h), Image.LANCZOS)
    canvas = Image.new('RGB', canvas_size, bg)
    canvas.paste(resized, ((cw - w) // 2, (ch - h) // 2))
    return canvas


# ======================================================================================
# Werker-QS v3 (Stand 2026-10-05): neue Boards Alpine 139 / Hello v1.36, 10 Cluster nach Legendenart
# ======================================================================================
V3_BOARDS = {
    'alpine': ('alpine_139_board_clean.png', 'alpine_139_bboxes.json'),
    'hello':  ('hello_v136_board_clean.png', 'hello_v136_bboxes.json'),
}
# Gut-Bilder je Cluster. Mehrere Gruppen eines Bildes = Montage (weit auseinander liegende Tasten).
V3_CROPS = {
    'alpine': {
        'c01': [['key_k_r3_face', 'key_oe_r3_face']],
        'c02': [['key_num_7_r5_face']],
        'c03': [['key_f1_r6_face', 'key_f2_r6_face', 'key_f3_r6_face']],
        'c04': [['key_ctrl_l_r1_face', 'key_win_r1_face']],
        'c05': [['key_shift_l_r2_face']],
        'c06': [['key_einf_r5_face', 'key_pos1_r5_face']],
        'c07': [['key_enter_r3_face']],
        'c08': [['key_esc_r6_face'], ['key_empty_r6_face']],
        'c09': [['key_arrow_up_r2_face', 'key_arrow_left_r1_face', 'key_arrow_down_r1_face', 'key_arrow_right_r1_face']],
        'c10': [['key_numpad_7_r4_face', 'key_numpad_8_r4_face', 'key_numpad_9_r4_face']],
    },
    'hello': {
        'c01': [['key_k_face', 'key_oe_face']],
        'c02': [['key_num_7_face']],
        'c03': [['key_f1_face', 'key_f2_face', 'key_f3_face']],
        'c04': [['key_ctrl_l_face', 'key_win_face']],
        'c05': [['key_shift_l_face']],
        'c06': [['key_einf_face', 'key_pos1_face']],
        'c07': [['key_enter_face']],
        'c08': [['key_esc_face'], ['key_hero_1'], ['key_note_face']],
        'c09': [['key_arrow_up_face', 'key_arrow_left_face', 'key_arrow_down_face', 'key_arrow_right_face']],
        'c10': [['key_numpad_7_face', 'key_numpad_8_face', 'key_numpad_9_face']],
    },
}
V3_SHARP = {'alpine': 'key_a_r3_face', 'hello': 'key_a_face'}

CLUSTER_COLORS = {   # Belegungsplan nach Cluster
    1: '#2563EB', 2: '#F97316', 3: '#16A34A', 4: '#9333EA', 5: '#EC4899',
    6: '#06B6D4', 7: '#DC2626', 8: '#A16207', 9: '#84CC16', 10: '#64748B',
}
ROW_COLORS = {       # Belegungsplan nach Reihe (nur Alpine)
    'R6': '#059669', 'R5': '#F97316', 'R4': '#84CC16', 'R3': '#2563EB', 'R2': '#9333EA', 'R1': '#DC2626',
}
ROW_NAMES = {'R6': 'F-Reihe', 'R5': 'Zahlenreihe', 'R4': 'Tab-Reihe', 'R3': 'Caps-Reihe', 'R2': 'Shift-Reihe', 'R1': 'Strg-Reihe'}
PLAN_ALPHA = 0.85
PLAN_WIDTH = 3600


def hex_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def crop_masked(img, boxes, key_ids, pad=3, margin=2):
    """Union-bbox der Tasten; alles ausserhalb der Face-Bboxen (und reines Weiss) -> QC_BG."""
    x0, y0, x1, y1 = [int(round(v)) for v in union_bbox(boxes, key_ids)]
    x0 = max(0, x0 - pad); y0 = max(0, y0 - pad)
    x1 = min(img.width, x1 + pad); y1 = min(img.height, y1 + pad)
    arr = np.array(img.crop((x0, y0, x1, y1)))
    allowed = np.zeros(arr.shape[:2], dtype=bool)
    for k in key_ids:
        bx0, by0, bx1, by1 = [int(round(v)) for v in boxes[k]]
        allowed[max(0, by0 - y0 - margin):max(0, by1 - y0 + margin), max(0, bx0 - x0 - margin):max(0, bx1 - x0 + margin)] = True
    bg = np.array(QC_BG, dtype=arr.dtype)
    arr[~allowed] = bg
    arr[allowed & (arr.min(axis=2) >= 250)] = bg      # Weiss in Luecken/Rundungen -> Grau
    return Image.fromarray(arr)


def sharp_crop(img, box):
    """Buchstabentaste sehr gross: Ausschnitt um die Legende (Tinte), Rest der Kappe als Rand."""
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    keyw = x1 - x0
    arr = np.array(img.crop((x0, y0, x1, y1))).astype(int)
    face = np.median(arr.reshape(-1, 3), axis=0)
    inner = np.zeros(arr.shape[:2], dtype=bool)
    m = int(keyw * .12)
    inner[m:-m, m:-m] = True
    ink = inner & (np.abs(arr - face).max(axis=2) > 60)
    ys, xs = np.where(ink)
    ix0, ix1, iy0, iy1 = xs.min(), xs.max(), ys.min(), ys.max()
    cx, cy = (ix0 + ix1) / 2, (iy0 + iy1) / 2
    half = max(ix1 - ix0, iy1 - iy0) / 2 + keyw * .17
    half = min(half, keyw / 2)
    cx = min(max(cx, half), keyw - half); cy = min(max(cy, half), keyw - half)
    return img.crop((int(x0 + cx - half), int(y0 + cy - half), int(x0 + cx + half), int(y0 + cy + half)))


def run_v3(sets):
    for set_name in sets:
        board, bbf = V3_BOARDS[set_name]
        if not os.path.exists(os.path.join(HERE, board)):
            print(f'[SKIP] {set_name}: missing {board}'); continue
        img = Image.open(os.path.join(HERE, board)).convert('RGB')
        with open(os.path.join(HERE, bbf), 'r', encoding='utf-8') as f:
            boxes = json.load(f)
        for name, clusters in V3_CROPS[set_name].items():
            crops = [crop_masked(img, boxes, ids) for ids in clusters]
            content = montage(crops, gap=QC_GAP, bg=QC_BG)
            out = pad_to_canvas(content, QC_CANVAS, QC_FILL, QC_BG)
            fn = f'{set_name}_v3_{name}.png'
            out.save(os.path.join(HERE, fn))
            print(f'[OK] {fn}  {out.size[0]}x{out.size[1]}px  ({len(clusters)} Gruppe(n), {sum(len(c) for c in clusters)} Tasten)')
        out = pad_to_canvas(sharp_crop(img, boxes[V3_SHARP[set_name]]), QC_CANVAS, QC_FILL, QC_BG)
        fn = f'{set_name}_v3_sharp.png'
        out.save(os.path.join(HERE, fn))
        print(f'[OK] {fn}  {out.size[0]}x{out.size[1]}px  (Legendenausschnitt {V3_SHARP[set_name]})')


def _font(px):
    for f in (r'C:\Windows\Fonts\arialbd.ttf', r'C:\Windows\Fonts\segoeuib.ttf'):
        if os.path.exists(f):
            return ImageFont.truetype(f, px)
    return ImageFont.load_default()


def _tint(arr, region, color, alpha):
    """Faerbt nur Kappen-Hintergrundpixel (Naehe zur Kappenfarbe); Legenden bleiben unveraendert."""
    x0, y0, x1, y1 = region
    sub = arr[y0:y1, x0:x1]
    nonwhite = sub.min(axis=2) < 250
    if not nonwhite.any():
        return
    face = np.median(sub[nonwhite], axis=0)
    dist = np.abs(sub - face).max(axis=2)
    w = alpha * np.clip((64 - dist) / 40.0, 0, 1) * nonwhite
    col = np.array(color, dtype=float)
    sub[:] = sub * (1 - w[..., None]) + col * w[..., None]


def _badge(draw, nonwhite_board, region, text, color, bw, bh, font):
    """Nummern-Plakette in der ersten freien Kappenecke (nur wo wirklich Kappe ist)."""
    x0, y0, x1, y1 = region
    ins = 6
    cands = [(x0 + ins, y1 - ins - bh), (x1 - ins - bw, y1 - ins - bh), (x0 + ins, y0 + ins), (x1 - ins - bw, y0 + ins)]
    pick = cands[0]
    for (bx, by) in cands:
        m = nonwhite_board[by:by + bh, bx:bx + bw]
        if m.size and m.mean() >= .93:
            pick = (bx, by); break
    bx, by = pick
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=bh // 4, fill=(255, 255, 255), outline=hex_rgb(color), width=max(3, bh // 12))
    tw = draw.textlength(text, font=font)
    draw.text((bx + (bw - tw) / 2, by + bh / 2), text, fill=(20, 20, 24), font=font, anchor='lm')


def _corner_rects(region, w, h, ins=6):
    x0, y0, x1, y1 = region
    return {'BL': (x0 + ins, y1 - ins - h, w, h), 'BR': (x1 - ins - w, y1 - ins - h, w, h),
            'TL': (x0 + ins, y0 + ins, w, h), 'TR': (x1 - ins - w, y0 + ins, w, h)}


def _pick_corner(arr0, nonwhite, face_box, region, w, h, order, taken=()):
    """Erste Ecke in `order` mit Kappe unter der Plakette und (fast) ohne Legendentinte; sonst die mit der wenigsten Tinte."""
    fx0, fy0, fx1, fy1 = face_box
    sub = arr0[fy0:fy1, fx0:fx1]
    nw = sub.min(axis=2) < 250
    face = np.median(sub[nw], axis=0)
    rects = _corner_rects(region, w, h)
    best = None
    for c in order:
        if c in taken:
            continue
        rx, ry, rw, rh = rects[c]
        if rx < 0 or ry < 0 or not nonwhite[ry:ry + rh, rx:rx + rw].size:
            continue
        cover = nonwhite[ry:ry + rh, rx:rx + rw].mean()
        ink = (np.abs(arr0[ry:ry + rh, rx:rx + rw] - face).max(axis=2) > 30).mean()
        if cover >= .93 and ink < .01:
            return c, rects[c]
        score = ink + (0 if cover >= .93 else 1)
        if best is None or score < best[0]:
            best = (score, c, rects[c])
    return best[1], best[2]


def _circle(draw, rect, text, font):
    rx, ry, rw, rh = rect
    draw.ellipse([rx, ry, rx + rw, ry + rh], fill=(17, 17, 17), outline=(255, 255, 255), width=max(3, rh // 10))
    tw = draw.textlength(text, font=font)
    draw.text((rx + (rw - tw) / 2, ry + rh / 2), text, fill=(255, 255, 255), font=font, anchor='lm')


def run_plan(sets):
    cl_path = os.path.join(HERE, '..', '..', 'qs_v3_clusters.json')
    with open(cl_path, 'r', encoding='utf-8') as f:
        cl = json.load(f)
    # Farbzuordnung fuer das HTML (Legende). Cluster-Palette ist design-neutral (nur Cluster-Nr./Name/Farbe);
    # die Reihen-Palette gilt nur fuer Alpine und liegt deshalb in einer eigenen Datei.
    colors = {
        'overlay_alpha': PLAN_ALPHA,
        'clusters': {str(c['id']): {'name': c['name'], 'hex': CLUSTER_COLORS[c['id']]} for c in cl['clusters']},
    }
    with open(os.path.join(HERE, '..', '..', 'qs_v3_colors.json'), 'w', encoding='utf-8') as f:
        json.dump(colors, f, ensure_ascii=False, indent=1)
    rows = {'overlay_alpha': PLAN_ALPHA, 'rows': {r: {'name': ROW_NAMES[r], 'hex': h} for r, h in ROW_COLORS.items()}}
    with open(os.path.join(HERE, '..', '..', 'qs_v3_colors_alpine_rows.json'), 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    print('[OK] qs_v3_colors.json, qs_v3_colors_alpine_rows.json')

    for set_name in sets:
        board, bbf = V3_BOARDS[set_name]
        if not os.path.exists(os.path.join(HERE, board)):
            print(f'[SKIP] {set_name}: missing {board}'); continue
        with open(os.path.join(HERE, bbf), 'r', encoding='utf-8') as f:
            boxes = json.load(f)
        keys = {k['name']: k for k in cl['sets'][set_name]['keys'] if k.get('cluster')}
        modes = ['clusters'] + (['rows'] if set_name == 'alpine' else [])
        for mode in modes:
            img = Image.open(os.path.join(HERE, board)).convert('RGB')
            arr = np.array(img).astype(float)
            nonwhite_board = arr.min(axis=2) < 250
            ax0 = min(b[0] for b in boxes.values()) - 60; ay0 = min(b[1] for b in boxes.values()) - 60
            ax1 = max(b[2] for b in boxes.values()) + 60; ay1 = max(b[3] for b in boxes.values()) + 60
            ax0, ay0 = max(0, ax0), max(0, ay0); ax1, ay1 = min(img.width, ax1), min(img.height, ay1)
            scale = PLAN_WIDTH / (ax1 - ax0)
            bh = int(round(40 / scale)); bw = int(round(bh * 1.25)); font = _font(int(bh * .62))
            arr0 = arr.copy()
            cdia = int(round(bh * .92)); cfont = _font(int(cdia * .56))
            badges = []
            circles = []
            for name, b in boxes.items():
                k = keys[name]
                x0, y0, x1, y1 = [int(round(v)) for v in b]
                if mode == 'clusters':
                    regions = [((x0, y0, x1, y1), CLUSTER_COLORS[k['cluster']], str(k['cluster']))]
                else:
                    rows = k['rows']
                    if len(rows) == 1:
                        regions = [((x0, y0, x1, y1), ROW_COLORS[rows[0]], rows[0])]
                    else:   # Zwei-Reihen-Kappe: obere Haelfte = obere Reihe, untere = untere
                        ym = (y0 + y1) // 2
                        regions = [((x0, y0, x1, ym), ROW_COLORS[rows[0]], rows[0]), ((x0, ym, x1, y1), ROW_COLORS[rows[-1]], rows[-1])]
                taken = {}
                for reg, col, txt in regions:
                    _tint(arr, reg, hex_rgb(col), PLAN_ALPHA)
                    if mode == 'rows':
                        c, rect = _pick_corner(arr0, nonwhite_board, (x0, y0, x1, y1), reg, bw, bh, ('BL', 'BR', 'TL', 'TR'))
                        taken[c] = rect
                        badges.append((reg, col, txt, rect))
                    else:
                        badges.append((reg, col, txt, None))
                if mode == 'rows':     # Cluster-Nummer (Block A) als kleiner dunkler Kreis in einer anderen freien Ecke
                    treg = (x0, y0, x1, y1)
                    c, rect = _pick_corner(arr0, nonwhite_board, (x0, y0, x1, y1), treg, cdia, cdia, ('TR', 'BR', 'TL', 'BL'), taken=tuple(taken))
                    circles.append((rect, str(k['cluster'])))
            out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
            d = ImageDraw.Draw(out)
            for reg, col, txt, rect in badges:
                if rect is None:
                    _badge(d, nonwhite_board, reg, txt, col, bw, bh, font)
                else:
                    rx, ry, rw, rh = rect
                    d.rounded_rectangle([rx, ry, rx + rw, ry + rh], radius=rh // 4, fill=(255, 255, 255), outline=hex_rgb(col), width=max(3, rh // 12))
                    tw = d.textlength(txt, font=font)
                    d.text((rx + (rw - tw) / 2, ry + rh / 2), txt, fill=(20, 20, 24), font=font, anchor='lm')
            for rect, txt in circles:
                _circle(d, rect, txt, cfont)
            out = out.crop((ax0, ay0, ax1, ay1))
            out = out.resize((PLAN_WIDTH, int(round(out.height * scale))), Image.LANCZOS)
            fn = f'{set_name}_v3_plan_{mode}.png'
            out.save(os.path.join(HERE, fn), optimize=True)
            print(f'[OK] {fn}  {out.size[0]}x{out.size[1]}px  (Plakette {bw}x{bh} nativ)')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--variant', choices=['lines', 'clean', 'qc', 'v3', 'plan'], required=True)
    ap.add_argument('--sets', nargs='+', default=['hello', 'alpine'])
    args = ap.parse_args()

    if args.variant == 'v3':
        return run_v3(args.sets)
    if args.variant == 'plan':
        return run_plan(args.sets)

    if args.variant == 'qc':
        suffix = ''
        src_suffix = '_board_300dpi_clean.png'  # qc crops are checklist-only -> always clean
    else:
        suffix = '_lines' if args.variant == 'lines' else ''
        src_suffix = '_board_300dpi.png' if args.variant == 'lines' else '_board_300dpi_clean.png'

    for set_name in args.sets:
        src_path = os.path.join(HERE, f'{set_name}{src_suffix}')
        if not os.path.exists(src_path):
            print(f'[SKIP] {set_name}: missing {os.path.basename(src_path)}')
            continue

        img = Image.open(src_path).convert('RGB')
        boxes = load_bboxes(set_name)

        # standard 1u key width for this set
        keyw = boxes['key_a'][2] - boxes['key_a'][0]

        if args.variant == 'qc':
            pad = keyw * 0.015  # tight -- just enough to keep the key's own edge/shadow, no neighbours
            for crop_name, clusters in QC_CROPS[set_name].items():
                crops = [crop_cluster(img, boxes, ids, pad) for ids in clusters]
                content = montage(crops, gap=QC_GAP, bg=QC_BG)
                out_img = pad_to_canvas(content, QC_CANVAS, QC_FILL, QC_BG)
                out_name = f'{set_name}_{crop_name}.png'
                out_path = os.path.join(HERE, out_name)
                out_img.save(out_path)
                print(f'[OK] {out_name}  {out_img.size[0]}x{out_img.size[1]}px  '
                      f'({len(clusters)} cluster{"s" if len(clusters) != 1 else ""})')
            continue

        pad = keyw * 0.06  # 6% margin
        for crop_name, clusters in CROPS[set_name].items():
            crops = [crop_cluster(img, boxes, ids, pad) for ids in clusters]
            out_img = montage(crops)
            out_name = f'{set_name}_{crop_name}{suffix}.png'
            out_path = os.path.join(HERE, out_name)
            out_img.save(out_path)
            print(f'[OK] {out_name}  {out_img.size[0]}x{out_img.size[1]}px  '
                  f'({len(clusters)} cluster{"s" if len(clusters) != 1 else ""})')


if __name__ == '__main__':
    main()
