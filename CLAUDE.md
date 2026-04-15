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
docs/                           # HTML-Visualisierungen, Previews
  keycap-layouts-iso-de.html    # Interaktiver Layout-Viewer (alle 16 Layouts)
scripts/
  recolor_template.py           # PDF-Farbersetzung (pikepdf)
  layout-mapper.py              # VIA JSON → Layout-Daten
templates/
  GK75-German-Tigry-original.pdf  # Hersteller-Original (NICHT ÄNDERN)
  GK75-TheWell-v*.pdf           # Aktuelle Design-Version
designs/the-well/
  the-well-design-document-EN.docx
  the-well-design-document-CN.docx
layouts/                        # Keyboard-Layout JSON-Daten
via-raw/                        # VIA JSON-Rohdaten
inventory/                      # Keycap-Inventar
```

## PDF-Keycap-Templates bearbeiten

### Wie die Templates aufgebaut sind
- Hersteller schickt Adobe Illustrator PDF mit Keycap-Positionen
- Jede Taste ist ein Vektorpfad (Curve) mit einer Füllfarbe
- Legends (Tastenbeschriftungen) sind **outlined text** = Vektorpfade, KEINE echten Textzeichen
- Template hat Layer: MC0 (底色层/Basisfarben), MC1 (Ebene 1/Details+Legends), MC2 (图层 3/zweites Design)

### recolor_template.py
Ersetzt Füllfarben im PDF-Content-Stream mit pikepdf.

```bash
# Farben analysieren
python3 scripts/recolor_template.py templates/GK75-German-Tigry-original.pdf dummy.pdf --analyze

# The Well Farben anwenden
python3 scripts/recolor_template.py templates/GK75-German-Tigry-original.pdf templates/GK75-TheWell.pdf --scheme the-well
```

### Kritische Regeln für PDF-Farbersetzung
1. **pikepdf verwenden** — nie manuell PDF-Streams manipulieren (kaputte Datei)
2. **Float-Precision: 6 Dezimalstellen** — `0.086275` nicht `0.086` (sonst Rundungsfehler)
3. **Hex → PDF Float**: `int(hex, 16) / 255.0` mit 6 Dezimalstellen formatieren
4. **Immer verifizieren**: Nach Ersetzung Farben auslesen und Hex-Roundtrip prüfen

### Labels ändern (das Schwierige)
Die Legends sind Vektorpfade. Man kann NICHT einfach Text ersetzen.

**Ansatz 1 — Affinity Studio (empfohlen für Label-Änderungen):**
1. PDF in Affinity öffnen (Import as Pages, PDF/X-4)
2. Doppelklick bis zum einzelnen Vektorpfad des Labels
3. Alten Pfad löschen, neuen Text setzen, in Outlines konvertieren
4. Export als PDF/X-4

**Ansatz 2 — Programmatisch (nur für Farben, nicht Labels):**
- Farben ersetzen: pikepdf Stream-Manipulation (funktioniert gut)
- Labels ersetzen: NICHT programmatisch machbar ohne die exakten Vektorpfade zu kennen

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

### Modifier-Labels (Symbole statt Text)
| Taste     | Label  | Unicode  |
|----------|--------|----------|
| CapsLock | ⇪      | U+21EA   |
| Tab      | ↹      | U+21B9   |
| Shift    | ⇧      | U+21E7   |
| Backspace| ⟵      | U+27F5   |
| Enter    | ↵      | U+21B5   |
| Delete   | Entf   | (Text)   |

### Navigation (Deutsch)
| Taste    | Label           |
|----------|----------------|
| Page Up  | Bild ↑ (2-zeilig)|
| Page Down| Bild ↓ (2-zeilig)|
| Home     | Pos 1           |
| End      | Ende            |

### Was NICHT geändert wird
- Strg, Win, Alt, Fn, Esc → bleiben wie sie sind
- Key-Positionen → kommen vom Hersteller-Template
- AltGr-Zeichen: ², ³, {, [, ], }, \, @, €, µ, ~, |
- Hex-Farbcodes, Maße (1u, 1.25u, 6.5u etc.)

## ADRs (Decisions)
- **Ein Design pro PDF** — keine gemischten Templates
- **Layout-Konventionen** — Cherry ISO-DE Standard (siehe oben)
- **Kit-Struktur** — Base Kit (~140 Keys) + Extension Kits
- **Shine-Through Hidden Horror** — Phase 2, wartet auf Hersteller-Feedback

## GitHub
- Repo: antonma/keyboards (Branch: master)
- Token: in Brain DB / Claude Memory gespeichert
- Push nach jeder Dateiänderung
