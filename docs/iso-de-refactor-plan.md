# ISO-DE Refactor Plan — Cherry-135 Master Template

**Erstellt:** 2026-04-22  
**Grundlage:** Phase A Strukturanalyse (Handoff `cherry-135-iso-de-master-template`)  
**Quell-PDF:** `templates/135 Cherry 全五面.pdf`  
**Ziel-PDF:** `templates/cherry-135-iso-de.pdf`

---

## A. PDF-Struktur — Ist-Zustand

| Eigenschaft | Wert |
|---|---|
| Seiten | 1 |
| Seitengröße | 1570 × 1122.5 px |
| Drawings gesamt | 3818 |
| Basis-Block (y < 510) | 2785 drawings |
| Alternates-Block (y ≥ 510) | 1033 drawings |
| Text-Objekte | 0 (alle Labels sind Outline-Paths) |
| Farbmodell | RGB (fill als float-Tupel) |
| Typischer Key | Body-Fill + 5–12 Topographie-Layers + Legend-Paths |

### Drawings pro Key-Typ (Erkenntnis)

| Key-Typ | Drawings | Bedeutung |
|---|---|---|
| Einfache 1u Basis-Alpha | ~27–28 | wenig Topographie-Detail |
| Einfache 1u Basis-Mod | ~30–31 | |
| Alt-Mod 1u (aus Alternates) | ~30–35 | mehr Topographie-Layers |
| Alt-Shift 1.75u | 55 | deutlich mehr Detail als Basis-Shift |
| Alt-Enter-ISO (L-Form) | 53 | einzelner Pfad für die L-Form |
| Basis-LSHIFT (2.32u ANSI) | 34 | |
| Basis-RSHIFT (2.82u ANSI) | 37 | |

---

## B. Die 8 Key-Umzüge — Vollständige Mapping-Tabelle

### B.1 Shift-Keys (Moves #6 und #8)

| # | Key-ID Source | Source-Position | Source-Größe | Key-ID Target (Basis) | Target-Position | Ziel-Größe | Ziel-Label |
|---|---|---|---|---|---|---|---|
| 8 | `alt_mod_125` | (137, 766)–(202, 818) | 64.8px = **1.26u** | `lshift` | (137, 352)–(256, 404) | → 1.26u | SHIFT L |
| 6 | `alt_mod_175c` | (262, 766)–(355, 818) | 93px = **1.80u** | `rshift` | (798, 352)–(942, 404) | → 1.80u | SHIFT R |

**Korrektur (Anton, Phase B.0 Review):** Source ist `alt_mod_175c` (R1 1.75, y0=766) — NICHT `alt_shift_175a` (R2 1.75 "3000+", y0=638). Gleiche Cherry-Row R1 wie SHIFT-L.

### B.2 ISO-Enter (Move #5)

| # | Key-ID Source | Source-Position | Geometrie | Key-IDs Target | Ziel-Position |
|---|---|---|---|---|---|
| 5 | `alt_enter_iso` | (483, 583)–(562, 689) | L-Form, 1 Pfad | `enter_top` + `enter_bot` | `enter_top`: (864, 245)–(943, 296) + `enter_bot`: ??? |

**Geometrie-Analyse des `alt_enter_iso`:**
```
Source L-Form (x0=483, y0=583, x1=562, y1=689):
  TOP-Teil  (Tab-Row):    x = 483–562 (79px = 1.53u), y = 583–634
  BOT-Teil  (CapsLk-Row): x = 497–562 (65px = 1.26u), y = 634–689
  Innere Stufe (L-Kerbe): x = 483–497, y = 634 (14px tiefer links)
```

**Nach Transformation (right-aligned auf x=943):**
```
  Shift dx = 943 - 562 = +381
  ISO-Enter TOP:  x = 864–943 (79px) — passt exakt auf enter_top-Position ✓
  ISO-Enter BOT:  x = 878–943 (65px) — schmalere Unterseite
  Kerbe bei:      x = 864–878 (14px)
```

**Konsequenz:** `enter_bot` (119.4px, x0=824) schrumpft auf 65px (x0=878).  
Freigewordener Platz im CapsLk-Row: x=823.9 bis x=878 = **54px** → passt für `#`-Key (1u = 51.4px + ~2.5px Gap) ✓

### B.3 `#`-Key (Move #4) — FEHLEND im Basis-Block

| # | Key-ID Source | Source-Position | Fills | Ziel-Position (neu) |
|---|---|---|---|---|
| 4 | **`alt_alpha1`** (Kandidat A) | (138, 584)–(189, 635) | `#DACCB1` | (824, 299)–(876, 350) |
| 4 | **`alt_alpha2`** (Kandidat B) | (192, 584)–(243, 635) | `#9FA89F` | (824, 299)–(876, 350) |

**Ziel-Position `#`-Key:**
- x0 = ae.x1 + 2.5gap = 821.5 + 2.5 = **824**
- x1 = 824 + 51.4 = **875.4** ≈ 876
- y0/y1 = CapsLk-Row: 299–350

**Open Question (kritisch):** Welcher Alt-Key ist das `#`-Key-Design?  
- `alt_alpha1` hat Fill `#DACCB1` = gleiche Fill wie `ae` (Ä) → vermutlich VARIANT von Ä oder ein anderer key
- `alt_alpha2` hat Fill `#9FA89F` = gleiche Fill wie `plus` (+*~)  
→ **Muss durch visuellen Render des Alternates-Blocks geklärt werden (Phase B.1)**

### B.4 `+*~`-Key (Move #7) — BEREITS im Basis-Block

| # | Key-ID Basis | Position | Draws | Status |
|---|---|---|---|---|
| 7 | `plus` | (810, 245)–(861, 296) | 28 draws | VORHANDEN, aber weniger Detail |

Der `plus`-Key (Basis) hat nur **28 Drawings** vs `alt_alpha2` (Alt) mit **34 Drawings**.  
Die 6 Extra-Drawings im Alt sind vermutlich präzisere Legend-Overlays.

**Entscheidung für Phase B:** `plus` durch `alt_alpha2` ERSETZEN, da besseres Detail. Falls `alt_alpha2` das `#`-Key-Design ist → `plus` durch das korrekte Alt-Key ersetzen.

### B.5 Rechte Mods (Moves #1, #2, #3) — Größen-Mismatch

| # | Key-ID Source (Alt) | Source-Position | Size | Key-ID Target (Basis) | Target-Size | Ziel-Label |
|---|---|---|---|---|---|---|
| 2 | `alt_mod1` | (138, 530)–(189, 582) | **1.00u** (51.6px) | `ralt` | 1.24u (63.9px) | ALT GR |
| 1 | `alt_mod2` | (191, 530)–(243, 582) | **1.00u** (51.6px) | `rwin` | 1.24u (63.9px) | FN |
| 3 | `alt_mod3` | (245, 530)–(297, 582) | **1.00u** (51.6px) | `rctrl` | 1.24u (63.9px) | STRG |

**Ziel-Positionen (Right-mods neu, 1u each):**
```
Spacebar endet bei x=673.8.
AltGr  (pos 1): x0=676.3,  x1=727.7  (51.4px)
FN     (pos 2): x0=730.2,  x1=781.6  (51.4px)
STRG-R (pos 3): x0=784.1,  x1=835.5  (51.4px)
```

**Open Question — MENU-Key:**  
Basis-Block hat **4** rechte Mods: `ralt`, `rwin`, `menu`, `rctrl`.  
Handoff spezifiziert nur 3 neue (AltGr=Pos1, FN=Pos2, STRG=Pos4).  
`menu` (aktuelle Pos 3 nach Spacebar): Status unklar. Optionen:
- A: Entfernen (Paths löschen, Coord-Map-Eintrag entfernen)
- B: Belassen + Coord-Map als `group=unused` oder `group=compat`
- C: Umbenennen zu context-menu (bleibt als 4. rechter Mod)

→ **Anton entscheiden vor Phase B.5**

---

## C. Technische Risiken und Mitigations

### Risiko 1: `#`-Key-Quelle unbekannt (KRITISCH)
**Problem:** Nicht klar welcher alt_alpha (1 oder 2 oder ein anderer) das `#`-Key-Design trägt.  
**Mitigation:** In Phase B.1 zuerst visuellen Render der Alternates-Reihe y=584–635 erstellen. Dann manuell identifizieren.

### Risiko 2: ISO-Enter BOT braucht #-Key-Gap
**Problem:** Der `enter_bot` (119.4px) muss für die ISO-Enter-Transformation von 119.4px auf 65px schrumpfen — damit der `#`-Key-Slot (54px) frei wird.  
**Mitigation:** Die Geometrie-Rechnung oben zeigt: 54px verfügbar ≥ 51.4px (1u) + 2.5px Gap ✓  
**Aber:** Wenn ISO-Enter-BOT kleiner als 65px wird durch Rounding-Fehler → neu rechnen.

### Risiko 3: alt_shift_175a vs alt_shift_175b — Welche ist SHIFT-R?
**Problem:** Beide sind identisch (92.1px, 55 Draws, #A7A88F Fill).  
**Mitigation:** Visueller Render. Vermutlich: 175a = SHIFT-L (linker Shift, Topographie konvex links), 175b = SHIFT-R (rechts konvex). Alternativ: beide sind identisch und nur 1 wird für SHIFT-R genutzt.

### Risiko 4: Path-Transformation Affin — alle Layers
**Problem:** Jeder Key besteht aus 30–55 Drawings. ALLE müssen um denselben dx/dy verschoben werden.  
**Mitigation:** PyMuPDF `get_drawings()` liefert alle Pfade mit Rect. Filtern per Source-BBox + Toleranz, dann `dx/dy`-Transform auf alle Path-Items anwenden.

### Risiko 5: Stroke-Count nach Refactor
**Goldstandard v5 (GK75):** 11.382 Strokes. Cherry-135-Basis hat eigene Baseline.  
**Erwartung:** Cherry-135-ISO-DE wird ANDERE Baseline haben als Universal (we replace paths).  
**Mitigation:** Neue Baseline nach Phase B dokumentieren, `verify_cherry.py` anpassen.

---

## D. Alle Alternates-Keys — Vollständige Tabelle

| Key-ID | Position | Width_u | Draws | Fill (Body) | Vermutliche Funktion |
|---|---|---|---|---|---|
| `alt_mod1` | (138,530)–(189,582) | 1.00u | 30 | #C8C1AA | Rechtes Mod 1u (AltGr) |
| `alt_mod2` | (191,530)–(243,582) | 1.00u | 31 | #D5C7AD | Rechtes Mod 1u (FN) |
| `alt_mod3` | (245,530)–(297,582) | 1.00u | 30 | #D7C7AE | Rechtes Mod 1u (STRG-R) |
| `alt_mod4` | (299,530)–(350,582) | 1.00u | 28 | #D5C6AD | Rechtes Mod 1u (?) |
| `alt_mod5` | (352,530)–(404,582) | 1.00u | 30 | #CEC4B3 | Rechtes Mod 1u (?) |
| `alt_mod6` | (406,530)–(458,582) | 1.00u | 29 | #C7B69C | Rechtes Mod 1u (?) |
| `alt_space_7u` | (832,540)–(1207,591) | 7.30u | 29 | #C8C0A7 | 7u Spacebar Alternativ |
| `alt_alpha1` | (138,584)–(189,635) | 1.00u | 34 | #DACCB1 | **#-Key Kandidat A** |
| `alt_alpha2` | (192,584)–(243,635) | 1.00u | 34 | #9FA89F | **#-Key Kandidat B / +*~-Upgrade** |
| `alt_enter_iso` | (483,583)–(562,689) | 1.53u | 53 | #B5B5A6 | **ISO L-Enter** ✓ |
| `alt_alpha3` | (138,638)–(189,689) | 1.00u | 32 | #C8C0A7 | Alpha Variante |
| `alt_alpha4` | (192,638)–(243,689) | 1.00u | 32 | #D9C9B3 | Alpha Variante |
| `alt_shift_175a` | (246,638)–(338,689) | 1.79u | 55 | #A7A88F | **SHIFT 1.75u Kandidat A** |
| `alt_shift_175b` | (343,638)–(435,689) | 1.79u | 55 | #A7A88F | **SHIFT 1.75u Kandidat B** |
| `alt_alpha5` | (438,638)–(490,689) | 1.00u | 31 | #C9BEA8 | Alpha Variante |
| `alt_mod_125` | (137,766)–(202,818) | 1.26u | 35 | #C8C1AA | **SHIFT-L 1.25u** ✓ |
| `alt_alpha6` | (206,766)–(258,818) | 1.00u | 33 | #CDBB9F | Alpha Variante |
| `alt_mod_175c` | (262,766)–(355,818) | 1.80u | 38 | #C8C1AA | Mod 1.75u (weitere Variante) |
| `alt_mod_2u` | (363,766)–(469,818) | 2.06u | 38 | #DACCB1 | Mod 2u (Backspace-Variante?) |
| `alt_a1–alt_a8` | y≈831–882 | 1.01u ea | 29 ea | varies | 1u Alpha-Set Variante |
| `alt_mod_15a–d` | y≈887–939 | 1.52u ea | 30–32 ea | varies | 1.5u Mod-Set (Win/Alt/Ctrl-Varianten) |

---

## E. Phase B — Ausführungsplan

### B.0 Visueller Render der Alternates-Sektion (10 Min)
```python
# Render y=520–700 des PDFs bei 3x Auflösung → PNG
# Identifiziert: #-Key, +*~-Key, welche shift_175 für L/R
```
**Output:** `d:/tmp/cherry_alts_render.png`  
**Fragen die beantwortet werden:** alt_alpha1 vs alt_alpha2 = welcher ist `#`?

### B.1 Source-Keys extrahieren
Für jeden der 8 Umzüge: alle Drawings per Bounding-Box-Lookup extrahieren und in Python-Dict speichern mit `{key_id: [drawings_list]}`.

```python
# Toleranz 3px um BBox
def extract_key_paths(page, x0, y0, x1, y1, tol=3):
    return [d for d in page.get_drawings()
            if d['rect'].x0 >= x0-tol and d['rect'].y0 >= y0-tol
            and d['rect'].x1 <= x1+tol and d['rect'].y1 <= y1+tol]
```

### B.2 ANSI-Target-Keys aus Basis-Block entfernen
Mit pikepdf: Content-Stream-Bytes der Target-Keys excisieren.  
Betroffen: `lshift` (2.32u), `rshift` (2.82u), `enter_bot` (2.32u), `enter_top` (falls ISO-Enter komplett neu), `ralt`/`rwin`/`rctrl` (1.24u each), und ggf. `plus` (1u, 28 draws).

**Achtung:** `enter_top` und neue ISO-Enter-TOP haben GLEICHE x-Position und fast gleiche Größe (78.2 vs 79px). Prüfen ob enter_top BEIBEHALTEN werden kann mit minimaler Transformation.

### B.3 Source-Keys an neue Positionen einfügen
Mit PyMuPDF `page.draw_*`-Methoden oder direktem PDF-Content-Stream-Append.  
Für jeden Path im source-dict: alle Koordinaten um `(dx, dy)` verschieben, neuen Path in neue PDF-Seite schreiben.

```python
# dx = target_cx - source_cx
# dy = target_cy - source_cy
# Transform jedes (x,y) in d['items']: x_new = x + dx, y_new = y + dy
```

### B.4 Label-Overrides
Für `ralt` → "ALT GR", `rwin` → "FN", `rctrl` → "STRG":
Falls Labels als Outline-Paths vorhanden: Die alten Paths aus dem Source-Key sind bereits falsch (WIN statt FN etc.) — müssen durch redact + TextWriter mit korrektem Label ersetzt werden.

**Alternativ:** Falls die alt_mod1..3 bereits KEIN Label enthalten (reine Key-Shapes ohne Text), dann Labels per TextWriter hinzufügen.

### B.5 ISO-DE PDF speichern
```python
doc.save('templates/cherry-135-iso-de.pdf')
```
Danach sofort verify-Check: Stroke-Count + neue Baseline dokumentieren.

---

## F. Neue Coord-Map — Erwartete Key-Positionen (cherry-135-iso-de)

Änderungen gegenüber der aktuellen `cherry-135-coordinate-map.json`:

| Key-ID | Alt Key-ID | x0 | y0 | x1 | y1 | width_u | Gruppe | Label |
|---|---|---|---|---|---|---|---|---|
| `lshift_125` | (war `lshift`) | 137 | 352 | 201 | 404 | **1.26u** | mod | SHIFT L |
| `less` | (unverändert) | 204 | 352 | 255 | 404 | 1.00u | alpha | < > |
| `rshift_175` | (war `rshift`) | 798 | 352 | 888 | 404 | **1.75u** | mod | SHIFT R |
| `iso_enter` | (war `enter_top`+`enter_bot`) | 864 | 245 | 943 | 350 | L-Form | accent | ↵ |
| `hash` | (NEU) | 824 | 299 | 876 | 350 | **1.00u** | alpha | # |
| `altgr` | (war `ralt`) | 676 | 406 | 728 | 458 | **1.00u** | mod | ALT GR |
| `fn` | (war `rwin`) | 730 | 406 | 782 | 458 | **1.00u** | mod | FN |
| `rctrl_1u` | (war `rctrl`) | 784 | 406 | 836 | 458 | **1.00u** | mod | STRG |

**Entfernt aus Basis-Block:**
- `lshift` (2.32u ANSI) → ins Archiv / Alternates
- `rshift` (2.82u ANSI) → ins Archiv / Alternates
- `enter_top` + `enter_bot` → ersetzt durch `iso_enter`
- `ralt` (1.24u), `rwin` (1.24u), `rctrl` (1.24u) → ersetzt durch 1u-Varianten
- `menu` → Status offen (Anton-Entscheidung)

---

## G. Offene Fragen vor Phase B (Anton entscheiden)

1. **`#`-Key-Quelle:** `alt_alpha1` oder `alt_alpha2`? → Render in B.0 zeigt es.
2. **MENU-Key:** Entfernen, behalten, oder umbenennen? (hat keine ISO-DE Funktion)
3. **`plus`-Key:** Ersetzen durch besseres Alt-Key oder beibehalten (28 draws reicht)?
4. **alt_shift_175a vs alt_shift_175b:** Beide identisch oder L/R-Hände unterschiedlich?

---

## H. Zeitschätzung Phase B

| Schritt | Zeit |
|---|---|
| B.0 Render + Identify | 10 Min |
| B.1 Source-Keys extrahieren (Script) | 20 Min |
| B.2 ANSI-Keys excisieren (pikepdf) | 45 Min |
| B.3 Source-Keys transformieren + einfügen | 60–90 Min |
| B.4 Label-Overrides | 30 Min |
| B.5 Save + Verify | 15 Min |
| **Gesamt** | **~3h** |
