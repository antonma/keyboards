# CLAUDE.md — Keyboards Repo

## Projekt
Keycap-Shop: Custom ISO-DE Keycap Sets. Hauptdesign: "The Well — 呪" (Dark Horror).

## Brain DB
Alle Handoffs, Session-Logs, Decisions und Todos liegen in der **Brain DB** (Supabase).
- Project-Slug: `keycap-shop`
- Lies immer zuerst die offenen Handoffs: `SELECT * FROM active_handoffs WHERE project = 'keycap-shop';`
- Schreibe am Ende jeder Session einen Session-Log und ggf. Handoff.
- **Keine Task-Dateien ins Repo** — Handoffs gehören in die Brain DB.

## Repo-Struktur
```
docs/
  keycap-layouts-iso-de.html       # ← KANONISCHE LABEL-REFERENZ (alle 16 Layouts)
scripts/
  recolor_template.py              # Füllfarben ersetzen (pikepdf, CMYK)
  cleanup_dolch_remnants.py        # Orphaned Paths entfernen (pikepdf stream excision)
  replace_modifier_labels.py       # Modifier-Symbole: ↹ ⇪ ⇧ ⟵ ENTF (PyMuPDF)
  replace_nav_labels.py            # Nav-Labels: POS 1, Bild↑, Bild↓ (PyMuPDF)
  apply_legend_colors.py           # Legende-Farben per Gruppe (PyMuPDF overdraw)
  make_v7.py                       # v6→v7: Uppercase Modifier Labels (PyMuPDF)
  layout-mapper.py                 # VIA JSON → Layout-Daten
templates/
  GK75-German-Tigry-original.pdf   # Hersteller-Original (NICHT ÄNDERN)
  GK75-TheWell-v6.pdf              # v5 + Dolch-Cleanup + Labels + Legende-Farben
  GK75-TheWell-v7.pdf              # v6 + Uppercase Modifier Labels (aktuell)
designs/the-well/
  the-well-design-document-EN.docx
  the-well-design-document-CN.docx
layouts/                           # Keyboard-Layout JSON-Daten
via-raw/                           # VIA JSON-Rohdaten
inventory/                         # Keycap-Inventar
```

## PDF-Keycap-Templates bearbeiten

### Wie die Templates aufgebaut sind
- Hersteller schickt Adobe Illustrator PDF mit Keycap-Positionen
- Jede Taste ist ein Vektorpfad (Curve) mit einer Füllfarbe
- Legends (Tastenbeschriftungen) sind **outlined text** = Vektorpfade, KEINE echten Textzeichen
  - Ausnahme: Row-Labels ("R1"–"R4") sind echte BT/ET-Texte mit ArialMT Subset-Font
- Template hat Layer: MC0 (底色层/Basisfarben), MC1 (Ebene 1/Details+Legends), MC2 (图层 3/zweites Design)
- Internes Farbmodell: **CMYK mit ICC-Profil** — PyMuPDF rendert zu RGB via ICC-Konversion
  - Folge: Farben shiften leicht, z.B. #8899AA → rendert als #8999A9, #1E2830 → #202830
  - Für Farb-Klassifikation immer **Toleranz ~20-30/255** verwenden, nicht exakten Match

### Tool-Wahl: pikepdf vs PyMuPDF

| Aufgabe | Tool | Grund |
|---------|------|-------|
| Keycap-Füllfarben ersetzen | **pikepdf** | Direkte Byte-Manipulation im CMYK-Stream |
| Labels ersetzen (Redact + neu) | **PyMuPDF (fitz)** | add_redact_annot + TextWriter |
| Pfad-Farben überschreiben | **PyMuPDF (fitz)** | get_drawings() + Shape overdraw |
| Stream-Bytes excisieren | **pikepdf** | Byte-Range-Cuts (z.B. Dolch-Cleanup) |

```bash
# Windows: immer py -3 statt python3
py -3 scripts/recolor_template.py templates/GK75-German-Tigry-original.pdf dummy.pdf --analyze
py -3 scripts/make_v7.py
```

### Füllfarben ersetzen (recolor_template.py)
Ersetzt CMYK-Füllfarben im PDF-Content-Stream mit pikepdf.
1. **Float-Precision: 6 Dezimalstellen** — `0.086275` nicht `0.086` (sonst Rundungsfehler)
2. **Hex → PDF Float**: `int(hex, 16) / 255.0` mit 6 Dezimalstellen formatieren
3. **Immer verifizieren**: Nach Ersetzung Farben auslesen und Hex-Roundtrip prüfen

### Labels ersetzen — Programmatischer Ansatz (Redact + TextWriter)

Labels sind Vektorpfade → direkte Text-Ersetzung geht NICHT. Aber: **Redact + TextWriter funktioniert.**

```python
import fitz
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')  # PFLICHT für Unicode-Output

FONT_PATH = r'C:\Windows\Fonts\seguisym.ttf'  # Segoe UI Symbol — hat alle nötigen Glyphen

font = fitz.Font(fontfile=FONT_PATH)

# Schritt 1: Alten Vektorpfad wegredaktieren
label_area = fitz.Rect(r.x0 + 5, r.y0 + 5, r.x1 - 5, r.y1 - 5)  # 5px Innenabstand
annot = page.add_redact_annot(label_area)
annot.set_colors(fill=key_bg_color)   # mit Hintergrundfarbe füllen
annot.update()
page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

# Schritt 2: Neuen Text einfügen
writer = fitz.TextWriter(page.rect)
text_w = font.text_length(label, fontsize=fontsize)
x = key_cx - text_w / 2              # horizontal zentrieren
y = key_cy + fontsize * 0.35         # Baseline: ~35% der Fontgröße unter Mitte
writer.append(fitz.Point(x, y), label, font=font, fontsize=fontsize)
writer.write_text(page, color=legend_rgb)
```

**KRITISCH:** `page.insert_text(..., fontfile=...)` funktioniert NICHT für Unicode-Symbole
(rendert Dots statt Glyphen). Immer **fitz.TextWriter** verwenden.

**Mehrere Farben:** Eine Writer-Instanz pro Legendenfarbe (write_text hat eine Farbe für alle).

### Legende-Farben anpassen (Overdraw-Strategie)

Die originalen CMYK-Legendenpfade können nicht direkt umgefärbt werden. Stattdessen:
neue RGB-Pfade on top zeichnen mit `fitz.Shape`:

```python
shape = page.new_shape()
for item in path['items']:
    if item[0] == 'l':   shape.draw_line(item[1], item[2])
    elif item[0] == 'c': shape.draw_bezier(item[1], item[2], item[3], item[4])
    elif item[0] == 're': shape.draw_rect(item[1])
shape.finish(fill=target_rgb, color=None, even_odd=path.get('even_odd', True))
shape.commit()
```

Klassifikation welche Farbe ein Legendenpfad bekommt:
1. Hintergrund-Fill-Farbe des Keycaps bestimmen (get_drawings(), größter enthaltener Pfad)
2. Accent-Fill (~#C8D0D8) → Accent-Legend #2A3540
3. Modifier-Fill (~#202830 nach ICC) → Modifier-Legend #5A7A90
4. Y-Position 252–312 (F-Key-Zeile) → FKey-Legend #4A6070
5. Sonst → Alpha-Legend #8899AA (keine Änderung nötig)

### GK75-spezifische Key-Koordinaten (PyMuPDF, y=0 oben)

```
Zeile          Y-Bereich    Beispiele
F-Key-Zeile    252–312      ESC(123,254,175,306), F1-F12
Zahlenzeile    325–378      Backspace(838,325,945,378), ENTF(963,325,1015,378)
Tab-Zeile      380–432      Tab(123,380,203,432), PgUp(963,380,1015,432)
CapsLk-Zeile   435–487      CapsLk(123,435,217,487), PgDn(963,435,1015,487)
Shift-Zeile    491–543      LShift(123,491,189,543), RShift(797,491,890,543)
Bottom-Zeile   545–597      STRG-L(123,545,189,597), WIN(192,545,258,597)
                             ALT-L(261,545,327,597), ALT-R(674,545,726,597)
                             FN(729,545,781,597)

Nav-Spalte (rechts, x≈963–1015):
  POS 1:  (963, 170, 1015, 223)   — über Rotary-Encoder
  ENTF:   (963, 325, 1015, 378)
  Bild↑:  (963, 380, 1015, 432)
  Bild↓:  (963, 435, 1015, 487)
```

### Bekannte Fallstricke

- **AltGr-Farb-Artefakt**: AltGr-Pfade (#3A6A8A Ziel) erscheinen als #3C6A8A — Rundungsfehler,
  visuell kaum sichtbar, akzeptabel
- **Dolch-Remnants**: Orphaned Paths bei Y<400 im original Tigry-Template — cleanup_dolch_remnants.py
- **Redact über TextWriter-Text**: Funktioniert — zweiter Redact entfernt auch vorherige TextWriter-Inhalte
- **Kein `even_odd` vergessen**: Buchstaben mit Lücken (O, B, 8...) brauchen even_odd=True für korrekte Füllung
- **Windows stdout**: Immer `sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')` am Anfang
- **Seitenkoordinaten**: PyMuPDF y=0 oben links; nativer PDF y=0 unten — get_drawings() liefert PyMuPDF-Koordinaten
- **Space-Key hat leeren `name`**: In keycap-coordinate-map.json ist `space.name = ""` — Tile-Dateinamen im
  `--keys`-Mode müssen `key['id']` verwenden, nicht `key['name']`
- **`artworks: null`** (YAML mit nur Kommentaren): PyYAML parst `artworks:` gefolgt von nur Kommentaren als `None`,
  nicht als `[]` — immer `config.get("artworks") or []` statt `.get("artworks", [])`
- **Ideogram Aspect-Ratios**: Kein `ASPECT_7_1` o.ä. — breitestes Format ist `ASPECT_3_1` (3:1).
  Für Spacebar (6.5:1) ist `ASPECT_3_1` das Maximum; PyMuPDF streckt das Bild auf die Key-Fläche.

## The Well — 呪 Farbschema

### Keycap Base Colors
| Gruppe     | Hex       | PDF RGB                          |
|-----------|-----------|----------------------------------|
| Alphas    | #161820   | 0.086275 0.094118 0.125490      |
| Modifiers | #1E2830   | 0.117647 0.156863 0.188235      |
| F-Keys    | #1C2228   | 0.109804 0.133333 0.156863      |
| Navigation| #1A2530   | 0.101961 0.145098 0.188235      |
| Accents   | #C8D0D8   | 0.784314 0.815686 0.847059      |
| Spacebar  | #BCC6D0   | 0.737255 0.776471 0.815686      |

### Legend Colors (pro Gruppe verschieden!)
| Gruppe           | Hex       | Tasten                              |
|-----------------|-----------|-------------------------------------|
| Alpha Legends   | #8899AA   | A-Z, 0-9, Symbole, Umlauts         |
| Modifier Legends| #5A7A90   | Strg, Win, Alt, Fn, ⇪, ⇧, ↹, ⟵   |
| F-Key Legends   | #4A6070   | F1-F12, Entf                       |
| Accent Legends  | #2A3540   | Esc, ↵, ↑↓←→ (dunkel auf hell!)    |
| Nav Legends     | #5A7A90   | Bild↑, Bild↓, Pos 1, Ende         |
| AltGr Legends   | #3A6A8A   | ², ³, {, [, ], }, \, @, €, µ, ~, | |

### Hersteller-Template Originalfarben (GK75 Tigry)
```
#F5F4EB = 0.961 0.957 0.922   Alpha (weiß/creme)
#E4B57B = 0.898 0.71 0.486    Accent (orange)
#EBB885 = 0.925 0.725 0.525   Accent (heller orange)
#A4CEC3 = 0.647 0.808 0.765   Accent (mint/Enter)
#8B8B8A = 0.549 0.549 0.545   Modifier (mittelgrau)
#828486 = 0.51 0.518 0.529    Modifier (grau)
#6B6C6C = 0.42 0.424 0.427    F-Keys (dunkelgrau)
#53555A = 0.329 0.337 0.353   Navigation (dunkler)
#4B4B4B = 0.298 0.298 0.298   Navigation (dunkelst)
#A4A4A4 = 0.647 0.647 0.647   Arrows (hellgrau)
#AA1616 = 0.667 0.09 0.09     Dolch rot (zweites Design)
```

## Cherry ISO-DE Layout Konventionen

### Modifier-Labels — Symbole und Text

**Kanonische Referenz: `docs/keycap-layouts-iso-de.html`** — dort sind alle Labels definiert.
Bei Zweifel immer HTML prüfen.

| Taste     | Label  | Unicode  | Farbe    |
|----------|--------|----------|----------|
| CapsLock | ⇪      | U+21EA   | #5A7A90  |
| Tab      | ↹      | U+21B9   | #5A7A90  |
| Shift    | ⇧      | U+21E7   | #5A7A90  |
| Backspace| ⟵      | U+27F5   | #5A7A90  |
| Enter    | ↵      | U+21B5   | #2A3540  |
| ESC      | ESC    | (Text)   | #2A3540  |
| STRG     | STRG   | (Text)   | #5A7A90  |
| WIN      | WIN    | (Text)   | #5A7A90  |
| ALT      | ALT    | (Text)   | #5A7A90  |
| FN       | FN     | (Text)   | #5A7A90  |

Font für alle Labels: **Segoe UI Symbol** (`C:\Windows\Fonts\seguisym.ttf`)

### Navigation (Deutsch) — alle GROSSBUCHSTABEN außer "Bild"

| Taste      | Label           | Farbe   | Hinweis              |
|------------|----------------|---------|----------------------|
| Page Up    | Bild↑ (2-zeilig)| #5A7A90 | "Bild" = dt. Substantiv|
| Page Down  | Bild↓ (2-zeilig)| #5A7A90 |                      |
| Home       | POS 1          | #5A7A90 | GROSSBUCHSTABEN      |
| Delete     | ENTF           | #4A6070 | GROSSBUCHSTABEN      |

### Was NICHT geändert wird
- Key-Positionen → kommen vom Hersteller-Template
- AltGr-Zeichen: ², ³, {, [, ], }, \, @, €, µ, ~, | (bleiben als Vektorpfade)
- Hex-Farbcodes, Maße (1u, 1.25u, 6.5u etc.)
- Das grafische Icon rechts neben Fn (x=784–836) — Hersteller-Design, kein Text

## ADRs (Decisions)
- **Ein Design pro PDF** — keine gemischten Templates
- **Layout-Konventionen** — Cherry ISO-DE Standard (siehe oben)
- **Kit-Struktur** — Base Kit (~140 Keys) + Extension Kits
- **Shine-Through Hidden Horror** — Phase 2, wartet auf Hersteller-Feedback

## GitHub
- Repo: antonma/keyboards (Branch: master)
- Token: in Brain DB / Claude Memory gespeichert
- Push nach jeder Dateiänderung

## Build-Framework (E2E Automation)

### Ground Truth: Coordinate Map
**`layouts/keycap-coordinate-map.json`** ist die einzige kanonische Quelle für Key-Positionen.
- 84 Keys, GK75 ISO-DE, mit x0/y0/x1/y1/cx/cy/group pro Key
- Nie hartkodierte Koordinaten in Scripts — immer aus der Map lesen
- Gruppen: `alpha`, `mod`, `fkey`, `accent`, `nav`, `spacebar`

### Build-Scripts

| Script | Funktion |
|--------|----------|
| `scripts/generate_artwork.py` | Ideogram API v3 → PNG generieren |
| `scripts/slice_artwork.py` | PNG → Key-Tiles pro Gruppe (moon/matrix/uniform) |
| `scripts/place_artwork.py` | Tiles → PDF (insert_image per Key via Coordinate Map) |
| `scripts/recolor.py` | Gruppe → neue Füllfarbe (Overdraw-Strategie) |
| `scripts/verify_template.py` | Quality Gate (Stroke Count, Farbmodell, Dateigröße) |
| `scripts/build_design.py` | Orchestrator: alles zusammen + 2 Review-Gates |

### Build-Configs
Jedes Design hat eine YAML-Datei in `build-configs/<design>.yaml`:
```yaml
design_name: terminal-v2
base_template_pdf: templates/GK75-German-Tigry-original.pdf
palette: { body_alpha: "#121F13", ... }
artworks:
  - name: matrix-frow
    target_group: fkey
    aspect_ratio: ASPECT_16_3
    model: turbo
    strategy: matrix
    prompt: "..."
color_operations:
  - group: alpha
    property: body
    color: "#121F13"
quality_baseline:
  stroke_count: 10974
  tolerance_pct: 1.0
```

### Design bauen
```bash
# Dry-Run (kein API-Call, kein Commit)
py -3 scripts/build_design.py --design terminal-v2 --dry-run

# Echter Build (pausiert an Gate 1 + Gate 2)
py -3 scripts/build_design.py --design terminal-v2

# Nach Gate-Pause fortsetzen
py -3 scripts/build_design.py --design terminal-v2 --resume gate2

# Alle Designs auflisten
py -3 scripts/build_design.py --list
```

### Review Gates
**Gate 1** — nach Artwork-Generierung: Artworks werden in `artwork-review/<design>` Branch gepusht.
Anton reviewt die PNGs auf GitHub (mobile), antwortet mit `ok` oder `verwerfen`.

**Gate 2** — vor finalem Commit: Fertiges PDF im gleichen Branch. Anton öffnet PDF, antwortet mit `commit` oder `verwerfen`.

### Rückfragen erlaubt bei
- Quelldatei nicht gefunden
- Gruppe aus Coordinate Map unbekannt
- verify_template schlägt nach 2 Retry-Versuchen fehl
- ADR-Konflikt

### Bei jedem Build: Brain DB Session-Log
```python
# Am Ende jeder Build-Session schreiben (project=keycap-shop, source_agent=claude-code)
```

### Ideogram API
- Env Var: `IDEOGRAM_API_KEY` (Codespace Secret)
- Kosten: ~$0.08–0.16 pro Bild
- Aktuelle Docs prüfen vor generate_artwork.py-Änderungen: ideogram.ai/api/docs
- Bei Dry-Run: `--dry-run` Flag → Placeholder PNG, kein API-Call

## PFLICHT: Template-Verifikation nach jeder PDF-Änderung

### Warum
In v6-v8 wurden 926 Stroke-Operationen (Tastenkanten) zerstört, weil:
1. CMYK/RGB Farbmodelle gemischt wurden
2. Label-Ersetzung die zugehörigen Strokes mitgelöscht hat
3. Keine Tests nach den Änderungen liefen

### Regel: KEIN git push ohne bestandene Tests

Nach jeder PDF-Manipulation MUSS `scripts/verify_template.py` laufen.
Wenn der Test fehlschlägt → FIX FIRST, dann push.

### 5 Pflicht-Tests

1. **Stroke-Count**: Baseline v5 = 11382 Strokes. Max -50 Toleranz.
2. **Farbmodell**: NUR CMYK oder NUR RGB — NIEMALS gemischt.
3. **Erwartete Farben**: Alle Design-Farben müssen im PDF vorhanden sein.
4. **Visueller Diff**: PDF rendern, Pixel-Diff gegen v5 Baseline. Tastenkanten-Region < 1% Abweichung.
5. **Dateigröße**: v5 = 872KB. Neue Version < 2MB (sonst eingebettete Raster = Fehler).

### Farbmodell: CMYK bevorzugen
Affinity exportiert CMYK. pikepdf muss auch CMYK ersetzen.
KEIN Mix aus CMYK-fills + RGB-fills im selben PDF.

### Label-Ersetzung: Strokes erhalten
Beim Löschen alter Label-Pfade: NUR Fill-Pfade entfernen, Stroke-Pfade BEIBEHALTEN.
Neue Labels müssen eigene Strokes mitbringen (gleiche Breite/Farbe wie Original).

### Baseline-Werte (v5 = Goldstandard)
- Strokes (S): 11382
- Fills (f): 906
- Fill+Stroke (B): 1
- CMYK fills: 6 unique
- CMYK strokes: 3 unique
- RGB fills: 0 (!)
- RGB strokes: 0 (!)
- Dateigröße: 872KB
- Graphics states: GS0-GS6
- Line widths: 0.016, 0.142, 0.216, 0.567
