"""
Werker-QS v3 (align-2): erzeugt je Design ein eigenes Dokument (HTML) aus qs_v3_content.json + den Bildern.

    py -3 _build_checklist_v3.py            # beide Designs, jeweils eigene Datei
    py -3 _build_checklist_v3.py --sets hello

Hello und Alpine werden nie gemischt: jedes Dokument verwendet nur {set}_v3_* Bilder und den Inhalt seines Designs.
Seitenaufteilung: Jede Zeile wird zuerst einzeln gerendert und gemessen (Edge + PyMuPDF), dann greedy auf Seiten gepackt.
PDF/Vorschau erzeugt _render_checklist_v3.py.
"""
import sys, io, os, json, html, argparse, subprocess, tempfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from PIL import Image
import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, 'img', 'ref')
EDGE = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
E = html.escape
SET_NAME = {'hello': 'Hello', 'alpine': 'Alpine'}
PT_MM = 25.4 / 72

CSS = """
  @page { size: A4 landscape; margin: 0; }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; background: #fff; color: #111;
    font-family: "Segoe UI", "Microsoft YaHei", "Noto Sans", Arial, "PingFang SC", "Noto Sans SC", sans-serif; }
  .page { width: 297mm; height: 208.6mm; padding: 5mm 8mm; display: flex; flex-direction: column;
          page-break-after: always; break-after: page; position: relative; }
  .page:last-child { page-break-after: auto; break-after: auto; }

  .header { display: flex; align-items: baseline; justify-content: space-between;
            border-bottom: 3px solid #111; padding-bottom: 0.6mm; margin-bottom: 1mm; }
  .header .title-en { font-size: 17pt; font-weight: 800; }
  .header .title-cn { font-size: 11pt; font-weight: 700; margin-left: 3mm; }
  .header .fields { font-size: 10pt; font-weight: 600; white-space: nowrap; }
  .header .fields .lab-cn { font-size: 9pt; font-weight: 500; color: #444; }
  .header .fields span.blank, .header .fields span.preset { display: inline-block; min-width: 18mm;
            border-bottom: 1.5px solid #111; margin: 0 3mm 0 1mm; }
  .header .fields span.preset { font-weight: 800; }

  .block-title { display: flex; align-items: baseline; gap: 3mm; background: #111; color: #fff;
                 padding: 0.5mm 3mm; border-radius: 2mm; margin-bottom: 0.8mm; }
  .block-title .en { font-size: 12.5pt; font-weight: 800; letter-spacing: 0.2pt; }
  .block-title .cn { font-size: 11pt; font-weight: 700; }
  .block-title .cont { margin-left: auto; font-size: 8.5pt; font-weight: 600; opacity: .85; }
  .hint { font-size: 8pt; color: #444; line-height: 1.15; margin: 0 0 0.8mm 0; }
  .hint .cn { margin-left: 2mm; }

  .rows { display: flex; flex-direction: column; gap: 0.8mm; }
  .blockgap { height: 1.4mm; }
  .row { display: flex; align-items: stretch; gap: 3mm; border: 1.5px solid #ccc; border-radius: 2mm; padding: 0.6mm 3mm; }
  .row .num { flex: 0 0 8mm; display: flex; align-items: center; justify-content: center;
              font-size: 14pt; font-weight: 800; color: #444; }
  .row .num.iso { flex-direction: column; font-size: 8pt; line-height: 1; gap: 0.3mm; }
  .row .num.iso b { font-size: 14pt; }
  .row .text { flex: 1 1 0; min-width: 0; display: flex; flex-direction: column; justify-content: center; }
  .row .rt { font-size: 11pt; font-weight: 800; line-height: 1.1; }
  .row .rt .cn { font-size: 10pt; font-weight: 700; margin-left: 2mm; }
  .row .note { font-size: 7.6pt; background: #fff4cf; border-left: 1.2mm solid #d79b00; padding: 0.5mm 1.6mm; margin: 0.6mm 0 0.4mm; line-height: 1.12; }
  .row .note .en { display: block; font-weight: 700; }
  .row .note .cn { display: block; font-weight: 500; color: #222; }
  .row .keys { font-size: 7.4pt; color: #666; line-height: 1.12; margin: 0.4mm 0 0.7mm; }
  .row ul.checks { list-style: none; margin: 0; padding: 0; }
  .row ul.checks li { margin: 0 0 0.55mm 0; padding-left: 2.6mm; position: relative; }
  .row ul.checks li:before { content: ""; position: absolute; left: 0; top: 1.15mm; width: 1.3mm; height: 1.3mm; background: #111; }
  .row ul.checks .en { display: block; font-size: 8pt; font-weight: 700; line-height: 1.1; }
  .row ul.checks .cn { display: block; font-size: 7.3pt; font-weight: 500; color: #222; line-height: 1.1; }

  .imgpair { flex: 0 0 auto; display: flex; gap: 5mm; align-items: flex-start; }
  figure { margin: 0; display: flex; flex-direction: column; align-items: center; gap: 0.3mm; }
  .imgbox { border-radius: 1.2mm; overflow: hidden; line-height: 0; }
  .imgbox.good { border: 2px solid #1a8a3c; }
  .imgbox.bad { border: 2px solid #c0182a; }
  .imgbox.plain { border: 1.5px solid #111; }
  .imgbox img { display: block; }
  .imglabel { font-size: 7.5pt; font-weight: 700; line-height: 1; }
  .imglabel.good { color: #1a8a3c; } .imglabel.bad { color: #c0182a; }

  .checkbox-col { flex: 0 0 18mm; display: flex; align-items: center; justify-content: center; gap: 2mm; }
  .cb { display: flex; flex-direction: column; align-items: center; gap: 0.4mm; }
  .cb .box { width: 7mm; height: 7mm; border: 2px solid #111; border-radius: 1mm; }
  .cb .lbl { font-size: 8pt; font-weight: 700; }
  .cb.ok .lbl { color: #1a8a3c; } .cb.nok .lbl { color: #c0182a; }

  .footer { margin-top: auto; border-top: 3px solid #111; padding-top: 0.8mm; display: flex; align-items: center; gap: 3mm; }
  .footer .icon { font-size: 15pt; font-weight: 900; color: #c0182a; }
  .footer .text { font-size: 9.5pt; font-weight: 700; line-height: 1.2; }
  .footer .text .cn { font-weight: 600; }
  .footer .pg { margin-left: auto; font-size: 8.5pt; color: #444; font-weight: 600; }

  .note-line { font-size: 9pt; font-weight: 600; margin: 0 0 1.5mm 0; }
  .note-line .cn { margin-left: 2mm; font-weight: 500; }
  .planwrap { position: relative; width: 262mm; margin: 0 auto; border: 1.5px solid #111; line-height: 0; }
  .planwrap img { width: 100%; display: block; }
  .legend { position: absolute; right: 2mm; bottom: 2mm; line-height: 1.1; background: rgba(255,255,255,0.92);
            border: 1.5px solid #111; border-radius: 2mm; padding: 2mm 3mm; display: grid; gap: 1.6mm 6mm; }
  .legend.c2 { grid-template-columns: 1fr 1fr; }
  .legend.c1 { grid-template-columns: 1fr; }
  .legend .cl { grid-column: 1 / -1; border-top: 1px solid #111; padding-top: 1.5mm; display: grid; grid-template-columns: 1fr 1fr; gap: 0.5mm 5mm; font-size: 7.4pt; font-weight: 600; }
  .legend .cl .it { display: flex; align-items: center; gap: 1.6mm; }
  .legend .cl .dot { flex: 0 0 4.2mm; height: 4.2mm; border-radius: 50%; background: #111; color: #fff; font-size: 6.4pt; font-weight: 800; display: flex; align-items: center; justify-content: center; }
  .legend.rs { gap: 1mm 4mm; padding: 1.4mm 2.4mm; }
  .legend.rs .chip .sw { flex: 0 0 6.2mm; height: 6.2mm; }
  .legend.rs .chip .sw i { font-size: 7pt; }
  .legend.rs .chip .lt .en { font-size: 7.6pt; }
  .legend.rs .chip .lt .cn { font-size: 6.8pt; }
  .legend.rs .cl { font-size: 6.6pt; gap: 0.3mm 3mm; padding-top: 1mm; }
  .legend.rs .cl .dot { flex: 0 0 3.6mm; height: 3.6mm; font-size: 5.8pt; }
  .chip { display: flex; align-items: center; gap: 2.2mm; }
  .chip .sw { flex: 0 0 8mm; height: 8mm; border-radius: 1.5mm; display: flex; align-items: center; justify-content: center; border: 1px solid #111; }
  .chip .sw i { font-style: normal; font-size: 8.5pt; font-weight: 800; background: #fff; color: #111; border-radius: 1mm; padding: 0.3mm 1.1mm; line-height: 1.1; }
  .chip .lt .en { display: block; font-size: 9pt; font-weight: 800; }
  .chip .lt .cn { display: block; font-size: 8pt; font-weight: 600; color: #222; }
"""


def two(d, sep=' | '):
    return f'{E(d["en"])}{sep}{E(d["cn"])}'


def header_html(c, set_name):
    f = c['header']['fields']
    fields = ''
    for i, fld in enumerate(f):
        lab = f'{E(fld["en"])} <span class="lab-cn">{E(fld["cn"])}</span>:'
        fields += f'{lab} <span class="preset">{SET_NAME[set_name]}</span>' if i == 0 else f'{lab} <span class="blank"></span>'
    return (f'<div class="header"><div><span class="title-en">{E(c["header"]["title"]["en"])}</span>'
            f'<span class="title-cn">{E(c["header"]["title"]["cn"])}</span></div><div class="fields">{fields}</div></div>')


def footer_html(c, n, total):
    return (f'<div class="footer"><div class="icon">&#10007;</div><div class="text">{E(c["footer"]["en"])}<br>'
            f'<span class="cn">{E(c["footer"]["cn"])}</span></div><div class="pg">{n} / {total}</div></div>')


def title_bar(t, cont=False):
    extra = '<span class="cont">(cont. 续)</span>' if cont else ''
    return f'<div class="block-title"><span class="en">{E(t["en"])}</span><span class="cn">{E(t["cn"])}</span>{extra}</div>'


def hint_html(h):
    return f'<div class="hint">{E(h["en"])}<span class="cn">{E(h["cn"])}</span></div>'


def checkbox_html():
    return ('<div class="checkbox-col"><div class="cb ok"><div class="box"></div><div class="lbl">OK</div></div>'
            '<div class="cb nok"><div class="box"></div><div class="lbl">NOK</div></div></div>')


def img_size(path):
    with Image.open(os.path.join(HERE, path)) as im:
        return im.size


def img_tag(path, kind, block):
    """Anzeigegroesse: flache Motive nach Breite, hochkante/quadratische nach Hoehe (Bild immer unverzerrt)."""
    w, h = img_size(path)
    r = w / h
    if block == 'B':
        style = 'width:150mm;height:auto'
    elif r >= 1.8:
        style = 'width:%dmm;height:auto' % (135 if block == 'ISO' else 78)
    else:
        style = 'height:%dmm;width:auto' % (44 if block == 'ISO' else 72)
    return f'<img src="{path}" alt="" style="{style}">'


def fig(path, cls, label, block):
    lab = f'<span class="imglabel {cls}">{label}</span>' if cls in ('good', 'bad') else ''
    return f'<figure><div class="imgbox {cls}">{img_tag(path, cls, block)}</div>{lab}</figure>'


def text_html(r, with_keys=True):
    checks = ''.join(f'<li><span class="en">{E(x["en"])}</span><span class="cn">{E(x["cn"])}</span></li>' for x in r['checks'])
    note = ''
    if r.get('note'):
        note = f'<div class="note"><span class="en">{E(r["note"]["en"])}</span><span class="cn">{E(r["note"]["cn"])}</span></div>'
    keys = f'<div class="keys">{two(r["keys"])}</div>' if (with_keys and r.get('keys')) else ''
    return (f'<div class="text"><div class="rt">{E(r["title"]["en"])}<span class="cn">{E(r["title"]["cn"])}</span></div>'
            f'{note}{keys}<ul class="checks">{checks}</ul></div>')


def row_html(r, set_name, block):
    rid = str(r['id'])
    if block == 'A':
        cid = f'c{int(rid[:-1]):02d}a' if rid[-1].isalpha() else f'c{int(rid):02d}'
        figs = (fig(f'img/ref/{set_name}_v3_{cid}_good.png', 'good', '&#10003; good', block) +
                fig(f'img/ref/{set_name}_v3_{cid}_bad.png', 'bad', '&#10007; bad', block))
    elif block == 'ISO':
        figs = fig(f'img/ref/{set_name}_v3_iso_{rid.lower()}.png', 'good', '&#10003; good', block)
    else:
        figs = fig(f'img/ref/{set_name}_v3_rows.png', 'plain', '', block)
    num = f'<div class="num iso">ISO<b>{E(rid[1:])}</b></div>' if block == 'ISO' else f'<div class="num">{E(rid)}</div>'
    return (f'<div class="row">{num}{text_html(r, block != "B")}'
            f'<div class="imgpair">{figs}</div>{checkbox_html()}</div>')


def blocks_of(c, set_name):
    """[(block_key, title, hint, rows)] in Dokumentreihenfolge."""
    out = [('A', c['blockA']['title'], c['blockA']['hint'], c['blockA']['rows'])]
    if c.get('blockISO'):
        out.append(('ISO', c['blockISO']['title'], c['blockISO'].get('hint'), c['blockISO']['rows']))
    if c.get('blockB'):
        out.append(('B', c['blockB']['title'], c['blockB'].get('hint'), c['blockB']['rows']))
    return out


def render_pdf(html_path, pdf_path):
    subprocess.run([EDGE, '--headless', '--disable-gpu', '--no-sandbox', f'--print-to-pdf={pdf_path}', '--print-to-pdf-no-header',
                    'file:///' + html_path.replace('\\', '/')], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)


def measure(c, set_name):
    """Hoehe jeder Zeile in mm (jede Zeile einzeln auf eigener Seite gerendert) + Kopf-/Fussbedarf."""
    pages = []
    keys = []
    for blk, title, hint, rows in blocks_of(c, set_name):
        for r in rows:
            keys.append((blk, str(r['id'])))
            pages.append(f'<section class="page"><div class="rows">{row_html(r, set_name, blk)}</div></section>')
    probe = (f'<section class="page">{header_html(c, set_name)}{title_bar(c["blockA"]["title"])}{hint_html(c["blockA"]["hint"])}'
             f'<div class="rows" id="probe"></div>{footer_html(c, 1, 1)}</section>')
    doc = f'<!DOCTYPE html><html><head><meta charset="UTF-8"><style>{CSS}</style></head><body>' + ''.join(pages) + probe + '</body></html>'
    tmp = tempfile.mkdtemp()
    hp = os.path.join(HERE, f'_measure_{set_name}.html')      # liegt neben den Bildern (relative Pfade); wird danach geloescht
    pp = os.path.join(tmp, 'm.pdf')
    open(hp, 'w', encoding='utf-8').write(doc)
    try:
        render_pdf(hp, pp)
    finally:
        os.remove(hp)
    pdf = fitz.open(pp)
    assert len(pdf) == len(keys) + 1, f'Messseiten {len(pdf)} != {len(keys) + 1}'
    heights = {}
    for (blk, rid), page in zip(keys, pdf):
        rects = [d['rect'] for d in page.get_drawings() if d.get('color') and all(abs(v - .8) < .02 for v in d['color']) and d['rect'].width > 700]
        assert rects, f'Zeilenrahmen nicht gefunden: {blk} {rid}'
        heights[(blk, rid)] = max(r.height for r in rects) * PT_MM
    # Kopf/Fuss: freier Platz auf der Probeseite = Footer-Linie oben - Ende des Hinweistexts
    page = pdf[len(keys)]
    blocks = page.get_text('blocks')
    hint_bottom = max(b[3] for b in blocks if b[4].startswith('Compare every cap'))
    rules = [d['rect'] for d in page.get_drawings() if d.get('fill') and all(v < .2 for v in d['fill']) and d['rect'].height < 4 and d['rect'].width > 700]
    footer_top = max(r.y0 for r in rules)
    free = (footer_top - hint_bottom) * PT_MM
    return heights, free


def pack(c, set_name, heights, free_page):
    """Greedy-Seitenaufteilung. Rueckgabe: Liste von Seiten; Seite = [(block, 'bar'|'row', obj, cont)].
    free_page = Platz unter dem Hinweistext der ersten Blockleiste (Kopf, erste Leiste und Hinweis sind schon abgezogen)."""
    BAR, HINT, GAP, BLOCKGAP, SAFE = 7.4, 4.6, 0.8, 1.4, 2.0
    cap = free_page - SAFE
    pages, cur, used = [], [], 0.0
    for blk, title, hint, rows in blocks_of(c, set_name):
        bar_cost = BAR + (HINT if hint else 0) + BLOCKGAP        # weitere Blockleiste auf derselben Seite
        for idx, r in enumerate(rows):
            h = heights[(blk, str(r['id']))]
            if idx == 0:
                if not cur:
                    cur.append((blk, 'bar', (title, hint), False)); cur.append((blk, 'row', r, False)); used = h
                elif used + bar_cost + h > cap:
                    pages.append(cur)
                    cur = [(blk, 'bar', (title, hint), False), (blk, 'row', r, False)]; used = h
                else:
                    cur.append((blk, 'bar', (title, hint), False)); cur.append((blk, 'row', r, False)); used += bar_cost + h
            elif used + GAP + h > cap:
                pages.append(cur)
                cur = [(blk, 'bar', (title, hint), True), (blk, 'row', r, False)]; used = h
            else:
                cur.append((blk, 'row', r, False)); used += GAP + h
    if cur:
        pages.append(cur)
    return pages


def build(set_name, content, colors, rowcolors):
    c = content[set_name]
    heights, free = measure(c, set_name)
    pages = pack(c, set_name, heights, free)
    ls = c['layout_sheet']
    # Hello: Cluster-Uebersicht. Alpine: EIN Layout sheet nach Reihe (mit kleinen Cluster-Nummern 1-10 in den Kappenecken).
    sheets = ['rows'] if (c.get('blockB') and ls.get('row_legend')) else ['clusters']
    total = len(pages) + len(sheets)
    out = []
    n = 0
    for pg in pages:
        n += 1
        body = header_html(c, set_name)
        # Block-Gruppen innerhalb der Seite
        i = 0
        while i < len(pg):
            blk, kind, obj, cont = pg[i]
            assert kind == 'bar'
            title, hint = obj
            body += ('<div class="blockgap"></div>' if i > 0 else '') + title_bar(title, cont) + (hint_html(hint) if hint else '')
            rows = []
            i += 1
            while i < len(pg) and pg[i][1] == 'row':
                rows.append(row_html(pg[i][2], set_name, pg[i][0])); i += 1
            body += '<div class="rows">' + ''.join(rows) + '</div>'
        body += footer_html(c, n, total)
        out.append(f'<section class="page">{body}</section>')
    for sh in sheets:
        n += 1
        body = header_html(c, set_name) + title_bar(ls['title'])
        nt = ls['note']
        if sh == 'rows':
            # Reihen-Blatt: eigener Hinweis; kleine Zahl 1-10 = Zeile in Block A
            nt = {'en': 'The colours R1–R6 show the row of each cap. The small number 1–10 is the line in Block A. Check that every legend is printed on a cap of the right row.',
                  'cn': '颜色R1–R6表示每个键帽所在的排。小数字1–10对应A部分的各行。请检查每个字符都印在正确排位的键帽上。'}
        body +=f'<div class="note-line">{E(nt["en"])}<span class="cn">{E(nt["cn"])}</span></div>'
        if sh == 'clusters':
            items = [(x['id'], colors['clusters'][str(x['id'])]['hex'], x['en'], x['cn']) for x in ls['cluster_legend']]
            img = f'img/ref/{set_name}_v3_plan_clusters.png'
            cols = 2
        else:
            items = [(x['row'], rowcolors['rows'][x['row']]['hex'], x['en'], x['cn']) for x in ls['row_legend']]
            img = f'img/ref/{set_name}_v3_plan_rows.png'
            cols = 2
        chips = ''.join(
            f'<div class="chip"><span class="sw" style="background:{hx}"><i>{E(str(lab))}</i></span>'
            f'<span class="lt"><span class="en">{E(en)}</span><span class="cn">{E(cn)}</span></span></div>'
            for lab, hx, en, cn in items)
        cl = ''
        if sh == 'rows':
            cl = '<div class="cl">' + ''.join(f'<div class="it"><span class="dot">{x["id"]}</span><span>{E(x["en"])} {E(x["cn"])}</span></div>' for x in ls['cluster_legend']) + '</div>'
        body += f'<div class="planwrap"><img src="{img}" alt=""><div class="legend c{cols}{" rs" if sh == "rows" else ""}">{chips}{cl}</div></div>'
        body += footer_html(c, n, total)
        out.append(f'<section class="page">{body}</section>')
    title = f'{c["header"]["title"]["en"]} — {SET_NAME[set_name]}'
    doc = (f'<!DOCTYPE html>\n<html lang="en"><head><meta charset="UTF-8"><title>{E(title)}</title>'
           f'<style>{CSS}</style></head><body>\n' + '\n'.join(out) + '\n</body></html>\n')
    layout = [[(p[0], str(p[2]['id']) if p[1] == 'row' else 'bar') for p in pg] for pg in pages]
    return doc, total, layout, {f'{k[0]}:{k[1]}': round(v, 1) for k, v in heights.items()}, round(free, 1)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--sets', nargs='+', default=['hello', 'alpine'])
    a = ap.parse_args()
    content = json.load(open(os.path.join(HERE, 'qs_v3_content.json'), encoding='utf-8'))
    assert content.get('version') == 'v3-align-4', f'qs_v3_content.json: version = {content.get("version")!r}'
    colors = json.load(open(os.path.join(HERE, 'qs_v3_colors.json'), encoding='utf-8'))
    rowcolors = json.load(open(os.path.join(HERE, 'qs_v3_colors_alpine_rows.json'), encoding='utf-8'))
    for s in a.sets:
        doc, total, layout, heights, free = build(s, content, colors, rowcolors)
        p = os.path.join(HERE, f'qc_checklist_v3_{s}.html')
        open(p, 'w', encoding='utf-8').write(doc)
        print(f'[OK] {os.path.basename(p)}  {total} Seiten (Soll); frei je Seite {free} mm')
        print('   Zeilenhoehen mm:', heights)
        print('   Aufteilung:', [[f"{b}{'' if r == 'bar' else r}" if r != 'bar' else f"[{b}]" for b, r in pg] for pg in layout])
