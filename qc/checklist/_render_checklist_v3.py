"""
Rendert qc_checklist_v3_{set}.html mit Edge headless zu PDF (A4 quer) und je Seite ein Vorschau-PNG.

    py -3 _render_checklist_v3.py [--sets hello alpine] [--dpi 150]
"""
import sys, io, os, subprocess, argparse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pikepdf, fitz

HERE = os.path.dirname(os.path.abspath(__file__))
EDGE = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--sets', nargs='+', default=['hello', 'alpine'])
    ap.add_argument('--dpi', type=int, default=150)
    a = ap.parse_args()
    for s in a.sets:
        html = os.path.join(HERE, f'qc_checklist_v3_{s}.html')
        pdf = os.path.join(HERE, f'qc_checklist_v3_{s}.pdf')
        subprocess.run([EDGE, '--headless', '--disable-gpu', '--no-sandbox', f'--print-to-pdf={pdf}',
                        '--print-to-pdf-no-header', 'file:///' + html.replace('\\', '/')],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        n = len(pikepdf.open(pdf).pages)
        doc = fitz.open(pdf)
        for i, page in enumerate(doc, 1):
            pix = page.get_pixmap(matrix=fitz.Matrix(a.dpi / 72, a.dpi / 72))
            pix.save(os.path.join(HERE, f'qc_checklist_v3_{s}_preview_p{i}.png'))
        print(f'[OK] {s}: {n} Seiten, {os.path.getsize(pdf)//1024} KB')
