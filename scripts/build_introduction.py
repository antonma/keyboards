#!/usr/bin/env python3
"""Project Introduction (EN + 中文) aus einer Textquelle als PDF erzeugen.

Inhaltsquellen: docs/introductions/common.yaml (Schriften, Labels) und
docs/introductions/<design>.yaml (Texte, Zonen, Zahlen). Keine Texte in diesem Script.

Aufruf:
    py -3 scripts/build_introduction.py --design alpine [--out PFAD] [--cjk-font PFAD[:INDEX]]
    py -3 scripts/build_introduction.py --design hello --check

--check prueft ohne PDF-Ausgabe (laeuft auch ohne reportlab):
    * jedes Zeichen der Inhaltsdatei ist im jeweiligen Font vorhanden
    * jede EN-Passage hat ein 中文-Gegenstueck (und umgekehrt), Zahlen in beiden gleich
    * Zahlen der Farbtabelle == Kappensumme == Hauptboard + Zusatzkappen == Aufschluesselung
    * listet alle "TODO Anton"-Marker der Inhaltsdateien

Abhaengigkeiten: PyYAML, PyMuPDF (fitz, nur --check), reportlab (nur PDF-Ausgabe):
    py -3 -m pip install reportlab
"""
import argparse
import io
import os
import re
import sys
from pathlib import Path

import yaml

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent
INTRO_DIR = REPO / "docs" / "introductions"
DEFAULT_OUT_DIR = REPO / "work" / "introductions"

# ---------------------------------------------------------------- Layout (pt, Ursprung oben links)
PAGE_W, PAGE_H = 595.2756, 841.8898
FRAME_X0, FRAME_X1 = 45.4, 549.9          # Kopfzeile, Farbfelder, Tabelle, Fusszeile
COL_EN_X, COL_EN_W = 56.7, 228.0           # Textspalten
COL_CN_X, COL_CN_W = 297.6, 241.0
RULE_X0, RULE_X1 = 56.7, 538.6
TOP = 36.0                                  # Inhaltsbeginn auf Folgeseiten
BOTTOM = 798.0                              # unterste Inhaltskante
FOOTER_RULE_Y, FOOTER_BASE_Y = 810.7, 820.6
BODY_SIZE, EN_LEAD, CN_LEAD, BODY_OFF = 8.2, 11.5, 12.6, 8.2
HEAD_SIZE, HEAD_LEAD = 10.0, 12.8
PARA_GAP = 5.0
SECTION_PAD = 10.0                          # unter dem Abschnitt, vor der naechsten Trennlinie
HERO = dict(top=143.7, x=89.4, w=416.5)   # Hoehe aus dem Seitenverhaeltnis des Bildes (16:10 -> 260 pt)
FIG_GAP, FIG_CAP_LEAD = 14.0, 9.6
SWATCH_Y0, SWATCH_H = 104.7, 31.0
TABLE_COLS = [50.4, 181.5, 292.5]            # Zone, Hex, Caps (Pantone entfaellt, Anton 2026-10-07)
TABLE_ROW_H, TABLE_HEAD_H, TABLE_SWATCH_W = 17.5, 21.0, 131.1

RED = (200 / 255, 16 / 255, 46 / 255)
GREY_RULE = (221 / 255,) * 3
C333, C666, BLACK, WHITE = (0.2,) * 3, (0.4,) * 3, (0, 0, 0), (1, 1, 1)

# Kinsoku (einfache Fassung): nicht am Zeilenanfang / nicht am Zeilenende
NO_START = set("，。、；：！？）」』】〉》”’·…—%)]},.;:!?")
NO_END = set("（「『【〈《“‘([{")
CJK_PUNCT_SINGLE = set("—…“”‘’")


class BuildError(Exception):
    pass


# ---------------------------------------------------------------- Inhalt laden
def deep_merge(base, over):
    out = dict(base)
    for k, v in over.items():
        out[k] = deep_merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def load_content(design):
    common_p, design_p = INTRO_DIR / "common.yaml", INTRO_DIR / f"{design}.yaml"
    for p in (common_p, design_p):
        if not p.exists():
            raise BuildError(f"Inhaltsdatei fehlt: {p}")
    common = yaml.safe_load(common_p.read_text(encoding="utf-8")) or {}
    own = yaml.safe_load(design_p.read_text(encoding="utf-8")) or {}
    c = deep_merge(common, own)
    c["_files"] = [common_p, design_p]
    return c


def norm(text):
    return " ".join(str(text).split())


def make_expander(c):
    zones = {z["name"]: z for z in c["zones"]}
    base = {"total": c["total_caps"], "main": c["main_caps"], "extra": c["extra_caps"],
            "n_zones": len(c["zones"]), "version": c["version"]}
    base.update({k: v for k, v in (c.get("values") or {}).items()})
    switches = c.get("switches") or {}

    def repl(m):
        key, arg = m.group(1), m.group(2)
        if arg is None:
            if key not in base:
                raise BuildError(f"Unbekannter Platzhalter {{{key}}}")
            return str(base[key])
        if key not in ("caps", "hex", "pantone"):
            raise BuildError(f"Unbekannter Platzhalter {{{key}:{arg}}}")
        if arg not in zones:
            raise BuildError(f"Platzhalter {{{key}:{arg}}}: Zone '{arg}' nicht in zones")
        return str(zones[arg][key])

    def cond(m):                                  # <<schalter:Text>> nur wenn switches.schalter true
        if m.group(1) not in switches:
            raise BuildError(f"Unbekannter Schalter <<{m.group(1)}:...>> (switches in der Inhaltsdatei fehlt)")
        return m.group(2) if switches[m.group(1)] else ""

    return lambda t: norm(re.sub(r"\{([a-z_]+)(?::([^}]+))?\}", repl,
                                 re.sub(r"<<(\w+):(.*?)>>", cond, str(t), flags=re.S)))


def collect_texts(c, ex):
    """Alle Texte als (ort, sprache, text) mit expandierten Platzhaltern. '**' bleibt erhalten."""
    out = [("tagline", "en", ex(c["tagline"])), ("footer", "en", ex(c["footer"])),
           ("title", "en", ex(c["title"])), ("doc_label", "en", ex(c["doc_label"])),
           ("cn_doc_label", "cn", ex(c["cn_doc_label"])), ("hero.caption", "en", ex(c["hero"]["caption"])),
           ("hero.caption_cn", "cn", ex(c["hero"]["caption_cn"])),
           ]
    for k, v in c["labels"].items():
        out.append((f"labels.{k}", "en", v))
    for z in c["zones"]:
        out.append((f"zone.{z['name']}", "en", z["name"]))
    for b in c["blocks"]:
        for n, f in enumerate(b.get("figures") or [], 1):
            out.append((f"figure[{n}]", "en", ex(f["caption"]["en"])))
            out.append((f"figure[{n}]", "cn", ex(f["caption"]["cn"])))
        if "section" not in b:
            continue
        sid = b["section"]
        t = b.get("title")
        if t:
            out.append((f"{sid}.title", "en", ex(t["en"])))
            out.append((f"{sid}.title", "cn", ex(t["cn"])))
        for i, pair in enumerate(b.get("body") or [], 1):
            out.append((f"{sid}.body[{i}]", "en", ex(pair["en"])))
            out.append((f"{sid}.body[{i}]", "cn", ex(pair["cn"])))
    return out


# ---------------------------------------------------------------- Fonts
def resolve_cjk(c, cli_value):
    spec = c["fonts"]["cjk"]
    path, index = spec["path"], int(spec.get("index", 0))
    env = os.environ.get("INTRO_CJK_FONT")
    src = cli_value or env
    if src:
        m = re.match(r"^(.*):(\d+)$", src)
        path, index = (m.group(1), int(m.group(2))) if m else (src, 0)
    p = Path(path)
    if not p.exists():
        raise BuildError(
            f"CJK-Schrift nicht gefunden: {p}\n"
            "  -> fonts.cjk.path in docs/introductions/common.yaml anpassen, oder\n"
            "     --cjk-font PFAD[:INDEX] bzw. Umgebungsvariable INTRO_CJK_FONT setzen.\n"
            "     Gebraucht wird ein vollstaendiger CJK-Font (z. B. Microsoft YaHei msyh.ttc, Noto Sans CJK SC).")
    return p, index


def has_glyph_fn(font_path):
    import fitz
    f = fitz.Font(fontfile=str(font_path))
    return lambda ch: bool(f.has_glyph(ord(ch)))


def helv_ok(ch):
    try:
        ch.encode("cp1252")
        return True
    except UnicodeEncodeError:
        return False


# ---------------------------------------------------------------- --check
def todo_markers():
    found = []
    for p in sorted(INTRO_DIR.glob("*.yaml")):
        for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if "TODO" in line:
                found.append((p, n, line.strip()))
    return found


def run_check(c, design, cjk_path):
    ex = make_expander(c)
    ok = True
    print(f"== --check {design} ({', '.join(f.name for f in c['_files'])})")

    # 1. Zeichenabdeckung
    has_cjk = has_glyph_fn(cjk_path)
    missing = {}
    for where, lang, text in collect_texts(c, ex):
        for ch in text.replace("**", ""):
            if ch.isspace():
                continue
            if lang == "en" and helv_ok(ch):
                continue
            if not has_cjk(ch):
                missing.setdefault(ch, []).append(where)
    if missing:
        ok = False
        for ch, wh in missing.items():
            print(f"  FEHLT im Font: {ch!r} U+{ord(ch):04X}  in {sorted(set(wh))[:4]}")
    else:
        print(f"  [ok] alle Zeichen vorhanden (EN: Helvetica/cp1252, Rest + 中文: {cjk_path.name})")
    fallbacks = sorted({ch for _, lang, t in collect_texts(c, ex) if lang == "en"
                        for ch in t if not ch.isspace() and not helv_ok(ch)})
    if fallbacks:
        print(f"  [info] EN-Zeichen ausserhalb Helvetica, werden aus dem CJK-Font gesetzt: {''.join(fallbacks)}")

    # 2. EN <-> 中文 Paare
    pair_problems = []
    num_re = re.compile(r"\d+(?:\.\d+)?")
    n_pairs = 0
    for b in c["blocks"]:
        if "section" not in b:
            continue
        sid = b["section"]
        pairs = [("title", b["title"])] if b.get("title") else []
        pairs += [(f"body[{i}]", p) for i, p in enumerate(b.get("body") or [], 1)]
        if not b.get("title") and not b.get("body"):
            pair_problems.append(f"{sid}: Abschnitt ohne Inhalt")
        for label, p in pairs:
            n_pairs += 1
            en, cn = ex(p.get("en") or ""), ex(p.get("cn") or "")
            if not en or not cn:
                pair_problems.append(f"{sid}.{label}: {'EN' if not en else '中文'} fehlt")
                continue
            if not re.search(r"[一-鿿]", cn):
                pair_problems.append(f"{sid}.{label}: 中文-Text enthaelt keine chinesischen Zeichen")
            if re.search(r"[一-鿿]", en):
                pair_problems.append(f"{sid}.{label}: EN-Text enthaelt chinesische Zeichen")
            ne, nc = sorted(num_re.findall(en.replace("**", ""))), sorted(num_re.findall(cn))
            if ne != nc:
                diff = [n for n in set(ne) ^ set(nc)] + [n for n in ne if ne.count(n) != nc.count(n)]
                if all(re.fullmatch(r"[1-9]", n) for n in diff):      # "3 Enter keys" / "三个回车键" ist ok
                    print(f"  [info] {sid}.{label}: einstellige Zahl nur in einer Sprache als Ziffer: {sorted(set(diff))}")
                else:
                    pair_problems.append(f"{sid}.{label}: Zahlen in EN und 中文 weichen ab: EN {ne} / 中文 {nc}")
    if pair_problems:
        ok = False
        for p in pair_problems:
            print(f"  PAAR: {p}")
    else:
        print(f"  [ok] {n_pairs} EN/中文-Paare vollstaendig, Zahlen je Paar gleich")

    # 3. Zahlen
    zsum = sum(int(z["caps"]) for z in c["zones"])
    problems = []
    if zsum != c["total_caps"]:
        problems.append(f"Farbtabelle summiert {zsum}, Kappensumme (total_caps) ist {c['total_caps']}")
    if c["main_caps"] + c["extra_caps"] != c["total_caps"]:
        problems.append(f"main_caps {c['main_caps']} + extra_caps {c['extra_caps']} != total_caps {c['total_caps']}")
    bs = sum(int(v) for v in (c.get("extra_breakdown") or {}).values())
    if c.get("extra_breakdown") and bs != c["extra_caps"]:
        problems.append(f"extra_breakdown summiert {bs}, extra_caps ist {c['extra_caps']}")
    lc = c.get("legend_check")
    if lc:
        calc = sum(lc["inks"]) + lc["wordmark_objects"]
        if calc != int(c["values"]["legend_objects"]):
            problems.append(f"Legenden: Tinten {lc['inks']} + Wortmarke = {calc}, values.legend_objects ist {c['values']['legend_objects']}")
        else:
            print(f"  [ok] Legenden: {' + '.join(map(str, lc['inks']))} + {lc['wordmark_objects']} Wortmarke = {calc} Vektor-Objekte "
                  f"(+ {c['values']['placed_artworks']} platziert = {calc + int(c['values']['placed_artworks'])})")
    if problems:
        ok = False
        for p in problems:
            print(f"  ZAHL: {p}")
    else:
        parts = " + ".join(str(z["caps"]) for z in c["zones"])
        print(f"  [ok] Farbtabelle {parts} = {zsum} = total_caps; "
              f"{c['main_caps']} + {c['extra_caps']} = {c['total_caps']}; Aufschluesselung = {bs}")

    # 4. Bild, TODO-Marker
    imgs = [c["hero"]["image"]] + [f["image"] for b in c["blocks"] for f in (b.get("figures") or [])]
    for name in imgs:
        img = INTRO_DIR / name
        if not img.exists():
            ok = False
            print(f"  BILD fehlt: {img}")
        else:
            print(f"  [ok] Bild {img.relative_to(REPO)} ({img.stat().st_size / 1e6:.2f} MB)")
    todos = [t for t in todo_markers() if t[0].stem in (design, "common")]
    print(f"  [info] {len(todos)} TODO-Marker:")
    for p, n, line in todos:
        print(f"     {p.name}:{n}: {line}")
    print("== " + ("CHECK OK" if ok else "CHECK FEHLGESCHLAGEN"))
    return ok


# ---------------------------------------------------------------- Text -> Zeilen
class Tok:
    __slots__ = ("segs", "w", "space", "first", "last")

    def __init__(self, segs, w, space, first, last):
        self.segs, self.w, self.space, self.first, self.last = segs, w, space, first, last


class Typesetter:
    def __init__(self, pdfmetrics, cjk_name):
        self.sw = pdfmetrics.stringWidth
        self.cjk = cjk_name

    def _font(self, ch, bold, lang):
        if lang == "cn" or not helv_ok(ch):
            return self.cjk
        return "Helvetica-Bold" if bold else "Helvetica"

    def _tok(self, chars, size, lang, space=False):
        segs = []
        for ch, bold in chars:
            f = self._font(ch, bold, lang)
            if segs and segs[-1][1] == f:
                segs[-1][0] += ch
            else:
                segs.append([ch, f])
        segs = [(t, f) for t, f in segs]
        w = sum(self.sw(t, f, size) for t, f in segs)
        return Tok(segs, w, space, chars[0][0], chars[-1][0])

    def tokenize(self, text, size, lang, force_bold=False):
        chars, bold = [], False
        for i, part in enumerate(text.split("**")):
            if i:
                bold = not bold
            chars += [(ch, bold or force_bold) for ch in part]
        toks, run = [], []

        def flush():
            if run:
                toks.append(self._tok(run[:], size, lang))
                run.clear()

        i = 0
        while i < len(chars):
            ch, b = chars[i]
            if ch.isspace():
                flush()
                toks.append(self._tok([(" ", b)], size, lang, space=True))
            elif lang == "cn" and (ord(ch) >= 0x2E80 or ch in CJK_PUNCT_SINGLE):
                flush()
                if ch == "—" and i + 1 < len(chars) and chars[i + 1][0] == "—":   # —— zusammenhalten
                    toks.append(self._tok([chars[i], chars[i + 1]], size, lang))
                    i += 1
                else:
                    toks.append(self._tok([(ch, b)], size, lang))
            else:
                run.append((ch, b))
            i += 1
        flush()
        return toks

    def wrap(self, text, size, width, lang, force_bold=False):
        toks = self.tokenize(text, size, lang, force_bold)
        kin = lang == "cn"
        lines, cur = [], []

        def cur_w():
            return sum(t.w for t in cur)

        def strip():
            while cur and cur[-1].space:
                cur.pop()

        for tok in toks:
            if tok.space:
                if cur:
                    cur.append(tok)
                continue
            if cur and cur_w() + tok.w > width + 0.01:
                sep = [t for t in cur[-1:] if t.space]       # Leerzeichen zwischen hochgezogenem Wort und tok
                strip()
                new = [tok]
                if kin:
                    for _ in range(6):
                        head = next(t for t in new if not t.space)
                        if not (len(cur) > 1 and (head.first in NO_START or cur[-1].last in NO_END)):
                            break
                        pulled = cur.pop()
                        gap = []
                        while cur and cur[-1].space:
                            gap.append(cur.pop())
                        new = [pulled] + sep + new
                        sep = gap[:1]
                    strip()
                lines.append(cur)
                cur = new
            else:
                cur.append(tok)
        strip()
        if cur:
            lines.append(cur)
        return lines


# ---------------------------------------------------------------- PDF
def lum(hexstr):
    h = hexstr.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255


def rgb(hexstr):
    h = hexstr.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


class Doc:
    def __init__(self, c, ex, out, cjk_path, cjk_index):
        try:
            from reportlab.pdfgen import canvas
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
        except ImportError:
            raise BuildError("reportlab ist nicht installiert. Installation (im Repo bewusst nicht automatisch):\n"
                             "    py -3 -m pip install reportlab")
        try:
            pdfmetrics.registerFont(TTFont("CJK", str(cjk_path), subfontIndex=cjk_index))
        except Exception as e:                                     # noqa: BLE001
            raise BuildError(f"CJK-Schrift {cjk_path} (Index {cjk_index}) nicht ladbar: {e}")
        self.c, self.ex = c, ex
        self.cv = canvas.Canvas(str(out), pagesize=(PAGE_W, PAGE_H), invariant=1, pageCompression=1)
        self.cv.setTitle(f"DELTASET {c['title']} {c['doc_label']} {c['version']}")
        self.cv.setAuthor(c["brand"])
        self.cv.setSubject(f"{c['doc_label']} (EN/中文)")
        self.ts = Typesetter(pdfmetrics, "CJK")
        self.page = 0
        self.y = 0.0
        self.warnings = []
        self.new_page(first=True)

    # --- Grundelemente (y von oben)
    def Y(self, y):
        return PAGE_H - y

    def text(self, x, y, s, font, size, color):
        self.cv.setFillColorRGB(*color)
        self.cv.setFont(font, size)
        self.cv.drawString(x, self.Y(y), s)

    def draw_lines(self, x, y0, lines, size, lead, color, off):
        for i, line in enumerate(lines):
            cx = x
            base = y0 + off + i * lead
            for tok in line:
                for t, f in tok.segs:
                    self.text(cx, base, t, f, size, color)
                    cx += self.ts.sw(t, f, size)
            if base > BOTTOM + 6:
                self.warnings.append(f"Seite {self.page}: Zeile unterhalb der Inhaltsgrenze")

    def rule(self, x0, x1, y):
        self.cv.setStrokeColorRGB(*GREY_RULE)
        self.cv.setLineWidth(0.4)
        self.cv.line(x0, self.Y(y), x1, self.Y(y))

    def rect(self, x0, y0, w, h, color):
        self.cv.setFillColorRGB(*color)
        self.cv.rect(x0, self.Y(y0 + h), w, h, stroke=0, fill=1)

    def new_page(self, first=False):
        if not first:
            self.footer()
            self.cv.showPage()
        self.page += 1
        self.y = TOP
        if first:
            self.header()

    def footer(self):
        c = self.c
        self.rule(FRAME_X0, FRAME_X1, FOOTER_RULE_Y)
        self.text(FRAME_X0, FOOTER_BASE_Y, self.ex(c["footer"]), "Helvetica", 6.8, C666)
        label = f"{c['labels']['page']} {self.page}"
        w = self.ts.sw(label, "Helvetica", 6.8)
        self.text(FRAME_X1 - w + 0.5, FOOTER_BASE_Y, label, "Helvetica", 6.8, C666)

    # --- Seite 1: Kopf
    def header(self):
        c, cv = self.c, self.cv
        self.text(FRAME_X0, 68.7, c["brand"], "Helvetica-Bold", 26, BLACK)
        n, pitch, sq = 26, 2.7, 1.6                     # rotes Punktband unter dem Wortbild
        for i in range(n):
            self.rect(FRAME_X0 + i * pitch, 73.8, sq, sq * 1.2, RED)
        # Untertitel mit fetter Versionsangabe
        x = FRAME_X0
        label = f"{self.ex(c['title'])}  ·  {self.ex(c['doc_label'])}  ·  "
        self.text(x, 90.2, label, "Helvetica", 9.5, C333)
        self.text(x + self.ts.sw(label, "Helvetica", 9.5), 90.2, c["version"], "Helvetica-Bold", 9.5, C333)
        # rechts: 中文-Dokumentname + Version, Kurzzeile
        cn = f"{self.ex(c['cn_doc_label'])} {c['version']}"
        self.text(FRAME_X1 - self.ts.sw(cn, "CJK", 8.0), 50.7, cn, "CJK", 8.0, C666)
        tag = self.ex(c["tagline"])
        self.text(FRAME_X1 - self.ts.sw(tag, "Helvetica", 8.0), 61.7, tag, "Helvetica", 8.0, C666)
        # Farbfelder (aus `zones`)
        zs = c["zones"]
        w = (FRAME_X1 - FRAME_X0) / len(zs)
        for i, z in enumerate(zs):
            x0 = FRAME_X0 + i * w
            self.rect(x0, SWATCH_Y0, w, SWATCH_H, rgb(z["hex"]))
            col = C333 if lum(z["hex"]) > 0.75 else WHITE
            cx = x0 + w / 2
            name, sub = z["name"], z["hex"]
            self.text(cx - self.ts.sw(name, "Helvetica-Bold", 7.4) / 2, 118.1, name, "Helvetica-Bold", 7.4, col)
            self.text(cx - self.ts.sw(sub, "Helvetica", 7.4) / 2, 127.6, sub, "Helvetica", 7.4, col)
        # Concept-Render
        img = INTRO_DIR / c["hero"]["image"]
        from PIL import Image                                     # reportlab bringt Pillow mit
        with Image.open(img) as im:
            iw, ih = im.size
        h = HERO["w"] * ih / iw
        cv.drawImage(str(img), HERO["x"], self.Y(HERO["top"] + h), HERO["w"], h)
        cap_y = HERO["top"] + h + 9.6
        self.text(FRAME_X0, cap_y, self.ex(c["hero"]["caption"]), "Helvetica", 7.0, C666)
        cap_cn = self.ts.wrap(self.ex(c["hero"]["caption_cn"]), 7.0, FRAME_X1 - FRAME_X0, "cn")
        self.draw_lines(FRAME_X0, cap_y + 2.0, cap_cn, 7.0, 9.6, C666, 7.0)
        self.y = cap_y + 2.0 + len(cap_cn) * 9.6 + 9.0

    # --- Abschnitte
    def pair_layout(self, en, cn, size, en_lead, cn_lead, en_bold=False):
        el = self.ts.wrap(en, size, COL_EN_W, "en", force_bold=en_bold)
        cl = self.ts.wrap(cn, size, COL_CN_W, "cn")
        self.check_kinsoku(cl)
        return el, cl, max(len(el) * en_lead, len(cl) * cn_lead)

    def check_kinsoku(self, lines):
        for n, ln in enumerate(lines):
            if n and ln[0].first in NO_START:       # erste Zeile eines Absatzes darf mit "·" (Listenpunkt) beginnen
                self.warnings.append(f"Seite {self.page}: 中文-Zeile beginnt mit {ln[0].first!r}")
            if ln and ln[-1].last in NO_END:
                self.warnings.append(f"Seite {self.page}: 中文-Zeile endet mit {ln[-1].last!r}")

    def section(self, b):
        ex = self.ex
        gap_default = float(b.get("gap", PARA_GAP))
        rows = []                                            # (kind, el, cl, height, gap_after)
        if b.get("title"):
            el, cl, h = self.pair_layout(ex(b["title"]["en"]), ex(b["title"]["cn"]), HEAD_SIZE, HEAD_LEAD, HEAD_LEAD,
                                         en_bold=True)
            rows.append(("title", el, cl, h, 5.0))
        # Absaetze mit gap_after: 0 laufen je Spalte unabhaengig weiter (wie im Original, z. B. nummerierte
        # Schritte); die Gruppe endet beim ersten Absatz mit Abstand > 0 und ist eine Seitenumbruch-Einheit.
        group_en, group_cn = [], []
        body = b.get("body") or []
        for n, p in enumerate(body):
            el, cl, _ = self.pair_layout(ex(p["en"]), ex(p["cn"]), BODY_SIZE, EN_LEAD, CN_LEAD)
            group_en += el
            group_cn += cl
            gap = float(p.get("gap_after", gap_default))
            if gap > 0 or n == len(body) - 1:
                rows.append(("body", group_en, group_cn,
                             max(len(group_en) * EN_LEAD, len(group_cn) * CN_LEAD), gap))
                group_en, group_cn = [], []

        group = 2 if b.get("title") and len(rows) > 1 else 1        # Ueberschrift bleibt mit erster Zeile zusammen
        i, started = 0, False
        while i < len(rows):
            at_top = self.y <= TOP + 0.01
            last = i + 1 if started else group
            need = sum(rows[k][3] for k in range(i, last)) + sum(rows[k][4] for k in range(i, last - 1))
            if not started and not at_top:
                need += 7.0
            if self.y + need > BOTTOM and not at_top:
                self.new_page()
                continue
            if not started:
                if not at_top:
                    self.rule(RULE_X0, RULE_X1, self.y)
                    self.y += 7.0
                started = True
            for k in range(i, last):
                kind, el, cl, h, gap = rows[k]
                if kind == "title":
                    self.draw_lines(COL_EN_X, self.y, el, HEAD_SIZE, HEAD_LEAD, RED, HEAD_SIZE)
                    self.draw_lines(COL_CN_X, self.y, cl, HEAD_SIZE, HEAD_LEAD, RED, HEAD_SIZE)
                else:
                    self.draw_lines(COL_EN_X, self.y, el, BODY_SIZE, EN_LEAD, BLACK, BODY_OFF)
                    self.draw_lines(COL_CN_X, self.y, cl, BODY_SIZE, CN_LEAD, BLACK, BODY_OFF)
                self.y += h + (gap if k < len(rows) - 1 else 0)
            i = last
        self.y += SECTION_PAD

    # --- Bildzeile (1 oder 2 Bilder, Bildunterschrift EN + 中文 darunter)
    def figures(self, b):
        from PIL import Image
        figs = b["figures"]
        n = len(figs)
        total = FRAME_X1 - FRAME_X0
        w = (total - FIG_GAP) / 2 if n > 1 else 300.0
        x0 = FRAME_X0 if n > 1 else FRAME_X0 + (total - w) / 2
        items, hmax = [], 0.0
        for f in figs:
            img = INTRO_DIR / f["image"]
            with Image.open(img) as im:
                iw, ih = im.size
            h = w * ih / iw
            en = self.ts.wrap(self.ex(f["caption"]["en"]), 7.0, w, "en")
            cn = self.ts.wrap(self.ex(f["caption"]["cn"]), 7.0, w, "cn")
            self.check_kinsoku(cn)
            items.append((img, h, en, cn))
            hmax = max(hmax, h + 9.6 + (len(en) + len(cn)) * FIG_CAP_LEAD)
        if self.y + hmax > BOTTOM and self.y > TOP + 0.01:
            self.new_page()
        top = self.y
        for i, (img, h, en, cn) in enumerate(items):
            x = x0 + i * (w + FIG_GAP)
            self.cv.drawImage(str(img), x, self.Y(top + h), w, h)
            ny = top + h + 2.0
            self.draw_lines(x, ny, [[self._italic(t) for t in ln] for ln in en], 7.0, FIG_CAP_LEAD, C666, 7.0)
            self.draw_lines(x, ny + len(en) * FIG_CAP_LEAD, cn, 7.0, FIG_CAP_LEAD, C666, 7.0)
        self.y = top + hmax + SECTION_PAD

    # --- Farbtabelle + Hinweis
    def zone_table(self):
        c, ex = self.c, self.ex
        lab = c["labels"]
        n = len(c["zones"])
        h = TABLE_HEAD_H + n * TABLE_ROW_H + 6
        if self.y + h > BOTTOM and self.y > TOP + 0.01:
            self.new_page()
        top = self.y
        heads = [lab["table_zone"], lab["table_hex"], lab["table_caps"]]
        for x, t in zip(TABLE_COLS, heads):
            self.text(x, top + 14.5, t, "Helvetica-Bold", 7.0, C666)
        self.rule(FRAME_X0, FRAME_X1, top + TABLE_HEAD_H)
        for r, z in enumerate(c["zones"]):
            ry = top + TABLE_HEAD_H + r * TABLE_ROW_H
            self.rect(FRAME_X0, ry, TABLE_SWATCH_W, TABLE_ROW_H, rgb(z["hex"]))
            col = C333 if lum(z["hex"]) > 0.75 else WHITE
            self.text(TABLE_COLS[0], ry + 11, f" {z['name']} ", "Helvetica", 7.0, col)
            for x, v in zip(TABLE_COLS[1:], (z["hex"], str(z["caps"]))):
                self.text(x, ry + 11, v, "Helvetica", 7.0, C666)
            self.rule(FRAME_X0 + TABLE_SWATCH_W, FRAME_X1, ry + TABLE_ROW_H)
        self.y = top + TABLE_HEAD_H + n * TABLE_ROW_H + 6 + SECTION_PAD - 2

    @staticmethod
    def _italic(tok):
        tok.segs = [(t, "Helvetica-Oblique" if f.startswith("Helvetica") else f) for t, f in tok.segs]
        return tok

    def finish(self):
        self.footer()
        self.cv.showPage()
        self.cv.save()


def build(c, out, cli_font):
    cjk_path, cjk_index = resolve_cjk(c, cli_font)
    ex = make_expander(c)
    out.parent.mkdir(parents=True, exist_ok=True)
    doc = Doc(c, ex, out, cjk_path, cjk_index)
    for b in c["blocks"]:
        if "section" in b:
            doc.section(b)
        elif b.get("figures"):
            doc.figures(b)
        elif b.get("zone_table"):
            doc.zone_table()
        else:
            raise BuildError(f"Unbekannter Block: {list(b)[:2]}")
    doc.finish()
    return doc


def main():
    ap = argparse.ArgumentParser(description="DELTASET Project Introduction (EN + 中文) aus docs/introductions/*.yaml")
    ap.add_argument("--design", required=True, help="Name der Inhaltsdatei docs/introductions/<design>.yaml (alpine|hello)")
    ap.add_argument("--out", help="Ausgabe-PDF (Default: work/introductions/<Design>_Project_Introduction_draft.pdf)")
    ap.add_argument("--check", action="store_true", help="nur pruefen, kein PDF schreiben")
    ap.add_argument("--cjk-font", help="CJK-Schrift PFAD[:INDEX] (ueberschreibt common.yaml / INTRO_CJK_FONT)")
    args = ap.parse_args()
    try:
        c = load_content(args.design)
        cjk_path, _ = resolve_cjk(c, args.cjk_font)
        if args.check:
            sys.exit(0 if run_check(c, args.design, cjk_path) else 1)
        out = Path(args.out) if args.out else DEFAULT_OUT_DIR / f"{args.design.capitalize()}_Project_Introduction_draft.pdf"
        doc = build(c, out, args.cjk_font)
    except BuildError as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        sys.exit(2)
    print(f"OK {out}  ({doc.page} Seiten, {out.stat().st_size / 1e6:.2f} MB, CJK-Font {cjk_path.name})")
    for w in doc.warnings:
        print(f"WARNUNG: {w}")


if __name__ == "__main__":
    main()
