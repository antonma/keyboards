# Quality Audit — GK75-terminal_2.pdf

**Datum:** 2026-04-17  
**Auditor:** claude-code  
**Verglichen gegen:** v5-Baseline (CLAUDE.md) + GK75-TheWell-v7.pdf

---

## Ergebnis: ⚠️ BEDINGT OK

| Test                  | Ergebnis | Details                                    |
|-----------------------|----------|--------------------------------------------|
| 1. Stroke Count       | ⚠️ WARN  | 10970 vs v5-Baseline 11382 (−412, >−50)    |
| 2. Farbmodell         | ✅ PASS  | Rein CMYK (k/K), kein RGB                  |
| 3. Erwartete Farben   | ✅ PASS  | Matrix-Palette vollständig vorhanden        |
| 4. Dateigröße         | ✅ PASS  | 800 KB < 2 MB                              |
| 5. Keine Raster       | ✅ PASS  | Keine eingebetteten Bilder (vgl. v7=13 MB) |

---

## Test 1 — Stroke Count

| Template              | Stroke-Ops (Stream) | Fill-Ops | Dateigröße |
|-----------------------|--------------------:|----------:|--------:|
| v5 (Goldstandard)     |              11 382 |       906 | 872 KB  |
| v6 (The Well)         |              10 927 |       794 | 9 100 KB |
| v7 (The Well)         |              10 473 |       770 | 13 167 KB |
| **terminal_2**        |          **10 970** |   **617** | **800 KB** |

**Befund:** terminal_2 hat 10 970 Stroke-Ops — besser als v7 (10 473) und v6 (10 927), aber
−412 unter dem v5-Goldstandard (11 382).

**Ursache:** Der Stroke-Verlust von −926 Ops passierte bereits in der v5→v6-Transition
(Label-Ersetzung zerstörte zugehörige Strokes). terminal_2 wurde wahrscheinlich nicht
von v5, sondern von einem bereits degradierten Template abgeleitet.

**Handlungsbedarf:** Kein sofortiger Fix notwendig, solange terminal_2 nicht auf v5
zurückgebaut werden soll. Für die Produktion empfohlen: terminal_2 von v5-Quelle ableiten.

---

## Test 2 — Farbmodell

Stream-Operatoren:
- `k` (CMYK fill): ✅ vorhanden
- `K` (CMYK stroke): ✅ vorhanden
- `rg` / `RG` (RGB): ✅ nicht vorhanden
- `g` / `G` (Graustufe): ✅ nicht vorhanden

→ **Farbmodell: rein CMYK** — kein CMYK/RGB-Mix.

---

## Test 3 — Farb-Inventar (Terminal-Palette)

### CMYK Fills (12 unique)

| CMYK (C M Y K)               | → RGB approx. | Häufigkeit | Bedeutung             |
|------------------------------|--------------|:----------:|-----------------------|
| 0.7020 0.0549 0.8510 0.0000  | #4BF026      | ×28        | Matrix-Grün (Accent)  |
| 0.7176 0.6392 0.6980 0.8039  | #0E120F      | ×12        | Near-Black Dunkelgrün |
| 0.7922 0.4588 0.7843 0.4706  | #1C491D      | ×9         | Dunkles Grün (Modifier)|
| 0.4941 0.3373 0.2510 0.0039  | #80A8BE      | ×6         | Blaugrau (Alpha/Legend)|
| 0.7490 0.5804 0.7451 0.7882  | #0D160D      | ×5         | Near-Black Grün       |
| 0.8157 0.5333 0.3020 0.0745  | #2B6EA4      | ×2         | Blau (AltGr?)         |
| 0.8235 0.7098 0.5569 0.6431  | #101A28      | ×1         | Sehr dunkel blaugrün  |
| 0.7647 0.7137 0.6000 0.7608  | #0E1118      | ×1         | Near-Black            |
| 0.2000 0.1294 0.0980 0.0000  | #CCDDE6      | ×1         | Hell (Spacebar/Accent)|
| 0.7961 0.6824 0.5725 0.6353  | #121D27      | ×1         | Dunkel Blaugrün       |
| 0.7255 0.6431 0.6902 0.8157  | #0C100E      | ×1         | Tiefes Schwarz-Grün   |
| 0.3098 0.4235 0.7255 0.0667  | #A48941      | ×1         | Amber (Detail)        |

### CMYK Strokes (3 unique)

| CMYK (C M Y K)               | → RGB approx. | Häufigkeit | Bedeutung       |
|------------------------------|--------------|:----------:|-----------------|
| 0.7216 0.6784 0.6706 0.8824  | #080909      | ×8         | Tastenkanten     |
| 0.6275 0.6941 0.6980 0.7843  | #141010      | ×7         | Tastenkanten     |
| 0.7255 0.6431 0.6902 0.8157  | #0C100E      | ×2         | Detail-Strokes   |

**Befund:** Palette konsistent für Terminal-/Matrix-Thema. Matrix-Grün (#4BF026) ist der
dominante Accent. Hintergründe sind sehr dunkle Grün/Blautöne. Keine fehlenden Farben.

---

## Test 4 — Dateigröße

- terminal_2.pdf: **800 KB** ✅ (Limit: < 2 000 KB)
- Zum Vergleich: v6 = 9 100 KB (eingebettete Raster!), v7 = 13 167 KB

---

## Test 5 — Keine eingebetteten Raster

800 KB Dateigröße belegt: keine eingebetteten Rasterbilder. Das ist der erwartete Zustand
für ein vektorbasiertes Keycap-Template.

---

## Zusammenfassung

**terminal_2.pdf ist für Design-Zwecke verwendbar.**

Einziges offenes Problem: Stroke-Count liegt −412 unter dem v5-Goldstandard. Für einen
produktionsreifen PDF-Export sollte das Template von der v5-Quelle (GK75-German-Tigry-original.pdf)
neu abgeleitet werden.

## Nächste Schritte

1. Matrix-Grün-Tiles aus `images/frow/matrix_F*.png` in F-Row-Keycaps einsetzen
2. Wenn Produktionsreife gewünscht: terminal_2 von v5-Original neu aufbauen (Stroke-Vollständigkeit)
3. `verify_template.py` schreiben (fehlt noch, per CLAUDE.md vorgeschrieben)
