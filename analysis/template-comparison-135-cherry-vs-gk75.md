# Template-Analyse: 135 Cherry 全五面 vs GK75 Tigry

**Datum:** 2026-04-21  
**Template:** `templates/135 Cherry 全五面.pdf`  
**Vergleich:** `templates/GK75-German-Tigry-original.pdf`  
**Ziel:** Machbarkeitsanalyse — kann das Build-Framework auf Cherry 135 ausgeweitet werden?

---

## Phase 1: PDF-Basics

| Eigenschaft | GK75 Tigry (Referenz) | Cherry 135 全五面 |
|-------------|----------------------|-----------------|
| Format | PDF 1.6 | PDF 1.6 |
| Creator | Adobe Illustrator | Adobe Illustrator 26.0 (Windows) |
| Producer | Adobe PDF library | Adobe PDF library 16.03 |
| Erstelldatum | — | 2024-05-23 |
| Dateigröße | 872 KB (v5-Baseline) | **537 KB** |
| Seiten | 1 | 1 |
| Seitengröße | 1098 × 1830 pt (Portrait) | **1570 × 1123 pt (Landscape)** |
| Seitengröße (mm) | ~387 × 645 mm | **~554 × 396 mm** |
| Farbmodell | **CMYK** | **Reines RGB** |

**Kritischer Unterschied:** Die Cherry 135 ist im Querformat und nutzt ausschließlich RGB — die GK75 war CMYK im Hochformat.

---

## Phase 2: Layer-Struktur

| Layer | GK75 Tigry | Cherry 135 |
|-------|-----------|------------|
| MC0 | 底色层 (Basisfarben) | 设计 (Design) |
| MC1 | Ebene 1 (Details/Legends) | 键帽 (Keycaps) |
| MC2 | 图层 3 (Zweites Design) | 文字说明 (Text/Beschriftungen) |

**Fazit Layer:** Identische MC0/MC1/MC2-Konvention — Layer-Zugriff per `BDC`-Marker funktioniert gleich. Layer-Namen unterscheiden sich (chinesische Bezeichnungen), aber technisch kompatibel.

---

## Phase 3: Path- und Fill-Analyse

| Eigenschaft | GK75 Tigry | Cherry 135 |
|-------------|-----------|------------|
| Drawings gesamt | ~13.289 | **3.818** |
| Fills (f) | 906 | 460 |
| Strokes (s) | 11.382 | 3.358 |
| Fill+Stroke (B) | 1 | 0 |
| Unique fill colors | 6 (CMYK) | **63 (RGB)** |
| Unique stroke colors | 3 (CMYK) | unbekannt |

### Keycap-Zählung Cherry 135

Das Template zeigt **135 Keycap-Fills** (h ≥ 45pt, w ≥ 45pt) auf einer Seite:

| Bereich | Row y | Keys | Beschreibung |
|---------|-------|------|--------------|
| Main Layout | y ≈ 135 | 16 | F-Reihe (ESC + F1–F12 + Nav) |
| Main Layout | y ≈ 243 | 21 | Zahlenreihe + Backspace (106pt) + 3× Nav |
| Main Layout | y ≈ 297 | 21 | QWERTY-Reihe + Tab (79pt) + ISO-Enter |
| Main Layout | y ≈ 351 | 16 | ASDF-Reihe + CapsLock (93pt) + Enter (119pt) |
| Main Layout | y ≈ 405 | 17 | ZXCV-Reihe + LShift (119pt) + RShift (145pt) |
| Main Layout | y ≈ 459 | 13 | Bottom-Reihe + Space (335pt, ≈6.5u) |
| Extra/Side | y ≈ 567 | 7 | Sonderkeys (inkl. Spacebar 375pt) |
| Extra/Side | y ≈ 621 | 3 | Modifier-Extras |
| Extra/Side | y ≈ 675 | 5 | Modifier-Extras |
| Extra/Side | y ≈ 783 | 4 | Alternates |
| Extra/Side | y ≈ 837 | 8 | Numpad-Block? |
| Extra/Side | y ≈ 891 | 4 | Numpad-Block |
| **Gesamt** | | **135** | |

**Main Layout (y < 500):** 104 Keys = vollständiges 75%-80%-Layout  
**Extra Area (y ≥ 500):** 31 Keys = Alternate-Caps / Sondertasten

### 全五面 Bedeutung

Der Titel `139+4 新原厂 全五面` bedeutet:
- **139+4**: 139 Basis-Keycaps + 4 Alternate-Keys
- **新原厂**: Neues Original-Fabrik-Design
- **全五面**: Alle 5 Flächen (für Dye-Sub-Druck aller Keycap-Seiten: Top/Front/Left/Right/Back)

Die 31 Extra-Keys (y ≥ 500) repräsentieren wahrscheinlich Front- und Seitenansichten für 5-seitigen Druck oder spezielle Alternate-Keys (ISO-Enter, Numpad, etc.).

---

## Phase 4: Legende / Text

| Eigenschaft | GK75 Tigry | Cherry 135 |
|-------------|-----------|------------|
| Echte Textzeichen | Row-Labels (ArialMT Subset) | **Keine** |
| Legend-Darstellung | Outlined Vectors (Vektorpfade) | Outlined Vectors |
| Fonts eingebettet | 0 (außer ArialMT Subset) | **0** |

**Fazit:** Alle Labels/Legenden sind vektorisierte Pfade — keine echten Textzeichen. Der PyMuPDF Redact+TextWriter-Ansatz (aus dem GK75-Build-Framework) wäre technisch anwendbar.

---

## Phase 5: Koordinaten-Vergleich mit GK75

| Maß | GK75 Tigry | Cherry 135 |
|-----|-----------|------------|
| 1u Breite | ~52.2 pt | ~51.4 pt |
| 1u Höhe | ~52.0 pt | ~51.4 pt |
| Keycap-Count | 84 | ~135 (104 Main + 31 Extra) |
| Layout-Typ | 75% TKL, GK75-spezifisch | 75–80% Cherry-Standard |
| Koordinaten-Ursprung | y=0 oben (PyMuPDF) | y=0 oben (PyMuPDF) |

**Vorhandene Coordinate Map:** `layouts/keycap-coordinate-map.json` ist GK75-spezifisch mit 84 Keys. Für Cherry 135 muss eine neue Map erstellt werden.

---

## Phase 6: Kritische Unterschiede & Framework-Impact

### 🔴 Breaking Differences

| Differenz | Impact |
|-----------|--------|
| **CMYK → RGB** | `recolor_template.py` (pikepdf CMYK-Bytes) funktioniert NICHT. Neue RGB-Recolor-Strategie nötig. |
| **63 Shading-Farben statt 6** | Keycap-Körper bestehen aus Farbverläufen (3D-Shading). Keine einfache Farb-Klassifikation möglich. |
| **Anderes Layout** (135 vs 84 Keys) | `layouts/keycap-coordinate-map.json` muss neu erstellt werden. |
| **Landscape statt Portrait** | Alle hardkodierten Y-Koordinaten ungültig. |
| **Andere 1u-Größe** (51.4 vs 52.2 pt) | Artwork-Tiling-Größen müssen angepasst werden. |

### 🟡 Kompatible Bereiche

| Bereich | Status |
|---------|--------|
| Layer-Konvention (MC0/MC1/MC2) | ✅ Identisch |
| Text-Format (outlined vectors, keine echten Fonts) | ✅ Identisch |
| PDF-Format (1.6, Illustrator) | ✅ Identisch |
| Build-Orchestrator (`build_design.py`) | ✅ Config-getrieben, wiederverwendbar |
| Artwork-Generierung (`generate_artwork.py`) | ✅ API-seitig layoutunabhängig |
| Artwork-Slicing (`slice_artwork.py`) | ✅ Wiederverwendbar |
| Artwork-Placement (`place_artwork.py`) | ✅ Coordinate-Map-getrieben, wiederverwendbar |

---

## Empfehlung

### → **Option B: Framework für Cherry 135 erweitern**

Option A (Tools 1:1 wiederverwenden) ist nicht möglich — das Farbmodell ist inkompatibel.  
Option C (vollständige Neuentwicklung) ist Overkill — der Framework-Kern ist bereits generisch.

**Option B** ist der richtige Weg: 4 gezielte Erweiterungen, Rest kann wiederverwendet werden.

### Konkrete Schritte (priorisiert)

#### Schritt 1 — Neue Coordinate Map (Aufwand: ~3h)
```
layouts/cherry-135-coordinate-map.json
```
- Script `scripts/extract_cherry_coords.py` schreiben
- Extraktion aus fills mit h≈51pt, w≥45pt aus dem PDF
- Key-IDs und Gruppen manuell zuweisen (ISO-DE Layout)

#### Schritt 2 — RGB Recolor (Aufwand: ~2h)
Datei: `scripts/recolor.py`

- Farbmodell-Erkennung: CMYK (pikepdf) vs RGB (PyMuPDF overdraw)
- Für Cherry: Overdraw-Strategie (wie `apply_legend_colors.py` beim GK75)
- Problem: 63 Shading-Farben müssen entweder alle ersetzt werden oder das gesamte Keycap wird solid übermalt → einfacher wäre **volle Überlagerung** (opaque fill over entire key rect)

#### Schritt 3 — Verify Baseline (Aufwand: ~1h)
```python
# verify_template.py Cherry-Baseline
stroke_count: 3358
fill_count: 460
color_model: RGB
```

#### Schritt 4 — Build-Config Cherry Test-Design (Aufwand: ~1h)
```yaml
# build-configs/cherry-test.yaml
base_template_pdf: templates/135 Cherry 全五面.pdf
coordinate_map: layouts/cherry-135-coordinate-map.json
```

### Gesamtaufwand Estimate

| Task | Stunden |
|------|---------|
| Coordinate Map extrahieren + validieren | 3h |
| RGB Recolor-Strategie | 2h |
| Verify Baseline Cherry | 1h |
| Build-Config + Smoke-Test | 1h |
| **Gesamt** | **~7h** |

---

## Offene Fragen

1. **Shading-Problem**: Die 63 RGB-Shading-Farben pro Keycap machen einen gezielten Farb-Swap schwierig. Soll der Keycap-Körper komplett solid übermalt werden (verliert 3D-Tiefe) oder soll ein Shift des gesamten Farbtons erfolgen?

2. **Extra-Keys (y ≥ 500)**: Sind das Alternates für ISO-DE (ISO-Enter, etc.) oder Seitenansichten für 全五面-Druck? Müssen diese ebenfalls recoloriert werden?

3. **Key-Gruppen**: Cherry 135 hat keine vordefinierte Gruppenstruktur. Müssen alpha/mod/fkey/accent/nav manuell gemappt werden?

4. **ISO-DE-Vollständigkeit**: Hat das Template bereits alle ISO-DE-Keys (ä/ö/ü, <> key, etc.)? Prüfung nötig.

---

*Analysiert am 2026-04-21 mit PyMuPDF / fitz. Keine Daten wurden verändert.*
