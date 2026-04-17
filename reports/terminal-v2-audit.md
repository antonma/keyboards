# GK75-terminal_2.pdf — Quality & Consistency Audit

**Datum:** 2026-04-17  
**Datei:** `templates/GK75-terminal_2.pdf`  
**Tool:** PyMuPDF (fitz) + pikepdf  
**Baseline:** GK75-TheWell-v5 (Goldstandard)

---

## Zusammenfassung

| Gate | Ergebnis | Status |
|------|----------|--------|
| Dateigröße < 2 MB | 800.5 KB | ✅ |
| Stroke Count ≥ 11.332 | 10.974 | ⚠️ WARN |
| Farbmodell (kein Mix) | Pure RGB | ✅ (kein Mix) |
| Keine grünen Bodies | Erfüllt | ✅ |
| Alpha BG = #0F1410 | #121F13 gefunden | ⚠️ Abweichung |
| Mod BG = #181D18 | #161813 gefunden | ⚠️ Abweichung |
| Alpha Legends = #3FFF3F (Phosphor) | #8999A9 dominiert (×506) | ❌ FEHLER |
| Mod Legends = #A8C8A8 | nicht gefunden | ❌ FEHLER |
| Sub-Legends = #1F6B1F | nicht eindeutig | ⚠️ unklar |

**Kritischer Befund:** Die Alpha-Legends zeigen noch die The-Well-Graufarbe (#8999A9), nicht das Phosphor-Grün (#3FFF3F). Das ist der dominante Defekt des Templates.

---

## 1. Dateigröße

```
800.5 KB  →  OK (< 2 MB)
```

---

## 2. Stroke Count

| Metrik | Wert | Baseline | Delta |
|--------|------|----------|-------|
| Stroke-only | 10.941 | — | — |
| Fill+Stroke | 33 | — | — |
| **Total Strokes** | **10.974** | **11.382** | **–408** |

**Status: ⚠️ WARN** — 408 Strokes unter Baseline. Mögliche Ursachen:
- Modifier-Labels wurden redaktiert ohne Strokes neu einzufügen
- F-Key-Legends fehlen teilweise

---

## 3. Farbmodell

```
Fill  RGB: 699   CMYK: 0
Stroke RGB: 10.974  CMYK: 0
```

**Status: ✅ Konsistent (reines RGB)** — kein CMYK/RGB-Mix.  
**Hinweis:** Hersteller bevorzugt CMYK für Druckproduktion. Für Druck-Submit ggf. in CMYK konvertieren.

---

## 4. Body-Farben (area > 1.000 sqpt)

75 Fill-Pfade klassifiziert als Key-Bodies:

| Farbe (gefunden) | Anzahl | ADR-Soll | Delta (R/G/B) | Bewertung |
|-----------------|--------|----------|----------------|-----------|
| `#121F13` | 48 | Alpha BG `#0F1410` | +3 / +11 / +3 | ⚠️ G-Kanal +11 |
| `#161813` | 23 | Mod BG `#181D18` | –2 / –5 / –5 | ⚠️ leichte Abweichung |
| `#1C252F` | 1 | Keyboard-Baseplate | — | ℹ️ Hintergrundplatte |
| `#CAD0D7` | 1 | Encoder-Ring | — | ℹ️ Volumenknopf |
| `#18171E` | 1 | Spacebar (Duplikat) | — | ⚠️ Duplikat (s.u.) |
| `#202830` | 1 | **The-Well Modifier** | — | ❌ Orphan aus anderem Design |

**Befunde:**
- Keine hellen grünen Bodies — ✅
- #0F1410 → #121F13: G-Kanal-Abweichung (+11) könnte ICC-Shift sein, ist aber außerhalb der üblichen ~5-Punkte-Toleranz. Prüfen ob Quell-CMYK korrekt gesetzt war.
- **Orphan `#202830`**: The-Well-Modifier-Grau steckt noch im Template — ein verbleibender Überrest des v6/v7-Basis-Designs. Muss entfernt werden.
- **Spacebar-Duplikat**: Rect `(330, 546, 671, 598)` hat zwei überlagerte Fills (`#18171E` + `#161813`). Wahrscheinlich Layer-Überrest. Nur einer davon sollte bleiben.

---

## 5. Legend-Farben (area ≤ 1.000 sqpt)

624 Fill-Pfade klassifiziert als Legends/Symbole:

| Farbe (gefunden) | Anzahl | ADR-Soll | Bewertung |
|-----------------|--------|----------|-----------|
| `#8999A9` | 506 | ❌ The-Well Alpha-Legend-Grau | ❌ FEHLER — nicht konvertiert |
| `#50B05E` | 78 | Phosphor `#3FFF3F`? | ⚠️ Grün, aber falsche Helligkeit |
| `#AC8A59` | 27 | — | ❌ Unidentifiziert (warm gold) |
| `#284A35` | 10 | Sub-Legend `#1F6B1F`? | ⚠️ Dunkler als Soll |
| `#3C6A8A` | 2 | AltGr-Legende (The Well) | ❌ Orphan |
| `#131612` | 1 | — | ℹ️ Einzelpfad |

### Detailbefunde Legends

**#8999A9 × 506 — kritischer Defekt:**  
Dies ist exakt die Alpha-Legend-Farbe aus dem The-Well-Design (ICC-Shift von #8899AA). Die Mehrzahl der Alpha-Legends (A–Z, Zahlen, Symbole) wurden **nicht** auf Phosphor-Grün umgefärbt. Das Terminal-Design sieht damit aus wie ein umgefärbtes The-Well mit grünen Keycap-Hintergründen.

**#50B05E × 78 — partielles Grün:**  
Helligkeit R=80/G=176/B=94 — klar grüner Ton, aber weit entfernt von Phosphor-Helligkeit `#3FFF3F` (G=255). Könnte Zahlenreihe oder F-Key-Legends sein, die separat behandelt wurden. Keine Übereinstimmung mit ADR-Werten.

**#AC8A59 × 27 — warm gold:**  
Nicht im ADR definiert. Ursprung unklar — möglicher Überrest aus dem Tigry-Accent-Farbschema (Original: `#E4B57B` → ICC-Shift). Sollte entfernt oder bewusst eingesetzt sein.

**#3C6A8A × 2 — AltGr-Orphan:**  
The-Well-AltGr-Legend-Farbe. Zwei Pfade wurden nicht konvertiert. Zu entfernen.

---

## 6. Stroke-Farben

| Farbe | Anzahl | Bedeutung |
|-------|--------|-----------|
| `#080606` | 6.885 | Tastenkanten (near-black, leicht warm) |
| `#131612` | 4.067 | Keycap-Outlines (sehr dunkelgrün) |
| `#241814` | 22 | Sonderelemente (warm-dunkelbraun) |

Stroke-Farbmodell konsistent (alle RGB). Tastenkanten vorhanden, aber unter Baseline-Count.

---

## 7. Auffälligkeiten gesamt

| # | Befund | Schwere |
|---|--------|---------|
| 1 | Alpha-Legends noch in The-Well-Grau (#8999A9 ×506) | 🔴 KRITISCH |
| 2 | Stroke Count –408 unter Baseline (möglicherweise fehlende Label-Strokes) | 🟠 HOCH |
| 3 | Unidentifizierte Legend-Farbe #AC8A59 ×27 (warm gold, kein ADR-Eintrag) | 🟠 HOCH |
| 4 | Orphan The-Well-Body #202830 ×1 (sollte nicht im Terminal-Design sein) | 🟡 MITTEL |
| 5 | Spacebar Duplikat-Fill (#18171E + #161813 an gleicher Rect) | 🟡 MITTEL |
| 6 | Alpha BG: #121F13 vs ADR #0F1410 — G-Kanal +11 | 🟡 MITTEL |
| 7 | AltGr-Orphan #3C6A8A ×2 (The-Well-Rest) | 🟡 MITTEL |
| 8 | Phosphor-Grün #50B05E ×78 zu dunkel (G=176 statt G=255) | 🟡 MITTEL |
| 9 | Farbmodell RGB statt CMYK (OK für Screen, für Druck prüfen) | 🔵 INFO |

---

## 8. Empfohlene nächste Schritte

1. **Alpha-Legends phosphorisieren**: Script schreiben das #8999A9-Fills auf #3FFF3F (Phosphor) umfärbt — alle 506 Pfade. Achtung: Overdraw-Strategie (PyMuPDF Shape), nicht Redact.
2. **Stroke-Count-Verlust analysieren**: `get_drawings()` nach Strokes < erwarteter Breite durchsuchen; prüfen ob Labels ohne Strokes redaktiert wurden.
3. **#50B05E aufklären**: Welche Keys sind das? Position-Analyse (Y-Range) → dann entscheiden ob auf #3FFF3F oder ADR-konformen Wert anpassen.
4. **#AC8A59 aufklären**: Welche Keys/Legends tragen diese Farbe? Entweder in ADR aufnehmen oder auf korrekte Terminal-Farbe setzen.
5. **Orphans entfernen**: #202830 Body + #3C6A8A AltGr-Legends aus dem PDF excisieren.
6. **Spacebar-Duplikat bereinigen**: Einen der beiden überlagerten Fills entfernen.
7. **ADR aktualisieren**: Sofern die gefundenen ICC-Shifts (#121F13, #161813) bewusste Design-Entscheidungen sind, ADR entsprechend anpassen.

---

*Erstellt von Claude Code (claude-sonnet-4-6) · 2026-04-17*
