"""
Crop reference key/row images from the 300dpi board renders for the QC checklist.

Usage:
    py -3 _crop_refs.py --variant lines
    py -3 _crop_refs.py --variant clean
    py -3 _crop_refs.py --variant qc

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

from PIL import Image

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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--variant', choices=['lines', 'clean', 'qc'], required=True)
    ap.add_argument('--sets', nargs='+', default=['hello', 'alpine'])
    args = ap.parse_args()

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
