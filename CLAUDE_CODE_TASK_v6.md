# CLAUDE CODE TASK: GK75-TheWell Template Cleanup + Label Anpassung

## Ziel
`templates/GK75-TheWell-v5.pdf` aufräumen und Labels anpassen → `templates/GK75-TheWell-v6.pdf`

## Kontext
- Das PDF ist ein Hersteller-Template (Adobe Illustrator PDF) für Keycap-Produktion
- Es wurde programmatisch umgefärbt (pikepdf) und in Affinity Studio nachbearbeitet
- Die Keycap-Flächen haben bereits die korrekten "The Well" Farben
- Die Legends (Tastenbeschriftungen) sind Vektorpfade (outlined text), KEINE echten Textzeichen
- Es gibt noch Reste vom gelöschten zweiten Keyboard (Dolch) auf der Seite

## Technischer Ansatz

### Option A: Affinity Studio (bevorzugt)
Affinity Studio V3 ist kostenlos und auf Antons Rechner installiert.
- Öffne `templates/GK75-TheWell-v5.pdf` in Affinity
- Alle Änderungen manuell/per Script
- Export als PDF/X-4

### Option B: Programmatisch (pikepdf + SVG)
- Labels sind Vektorpfade → kann man nicht einfach "Text ersetzen"
- Alternative: Neue Labels als SVG-Pfade generieren und in die PDF einsetzen
- Komplexer aber automatisierbarer

### Option C: Hybrid
- pikepdf für Cleanup (Reste entfernen)
- Neue Labels als separate SVG/PDF-Overlays generieren
- In Affinity zusammenfügen

## Aufgabe 1: Cleanup — Reste entfernen

In der unteren Seitenhälfte (unter den Mac-Ersatztasten und Q/L Detail-Keys) gibt es:
- Ein kleiner Strich in der Seitenmitte
- Ein helles Objekt unten links  
- Möglicherweise unsichtbare Elemente vom gelöschten Dolch-Keyboard

**Ansatz:** PDF-Content-Stream analysieren. Das Dolch-Keyboard war in Layer MC2 (图层 3).
MC2 wurde in v4 bereits entfernt, aber beim Affinity-Reexport könnten Artefakte entstanden sein.
Prüfe ob es leere Gruppen oder verwaiste Objekte gibt.

## Aufgabe 2: Modifier-Labels ändern

Die Modifier-Tasten haben aktuell Text-Labels. Unser Design verwendet Cherry-Symbole:

```
CapsLk  → ⇪  (U+21EA, Caps Lock symbol)
Tab     → ↹  (U+21B9, Tab symbol)  
Shift   → ⇧  (U+21E7, Shift symbol) — BEIDE Shift-Tasten (links 1.25u, rechts 1.75u)
← (BS)  → ⟵  (U+27F5, Backspace arrow)
Del     → Entf (deutscher Text)
```

NICHT ÄNDERN: Strg, Win, Alt, Fn, Esc — diese bleiben wie sie sind.
Enter ↵ ist bereits korrekt.

**Das Problem:** Die Labels sind Vektorpfade. Man kann nicht einfach den Text ändern.
**Lösung:** 
1. In Affinity: Alten Vektorpfad löschen, neues Textfeld mit dem Symbol erstellen, in Outlines konvertieren
2. Oder: SVG-Glyphen für ⇪, ↹, ⇧, ⟵ generieren und als Vektorpfade einfügen

**Positionierung:** Symbole ZENTRIERT auf der Taste, vertikal und horizontal.
**Größe:** Ca. 14pt für die Symbole (proportional zur Tastengröße).

## Aufgabe 3: Navigation-Labels auf Deutsch

```
PgUp → Bild ↑  (zweizeilig: "Bild" oben, "↑" unten)
PgDn → Bild ↓  (zweizeilig: "Bild" oben, "↓" unten)
Home → Pos 1   (einzeilig)
End  → Ende    (einzeilig)
```

**Schriftgröße:** Ca. 7-8pt (Nav-Tasten sind 1u, wenig Platz)
**Farbe:** #5A7A90

## Aufgabe 4: Legend-Farben pro Tastengruppe

Aktuell sind fast alle Legends #8899AA (Ghostly grey). 
Laut Design-Spezifikation sollen sie pro Gruppe variieren:

```python
legend_colors = {
    "alpha":    "#8899AA",  # A-Z, 0-9, Symbole — BEREITS KORREKT
    "modifier": "#5A7A90",  # Strg, Win, Alt, Fn, ⇪, ⇧, ↹, ⟵
    "fkey":     "#4A6070",  # F1-F12, Entf
    "accent":   "#2A3540",  # Esc, ↵ Enter, ↑↓←→ (DUNKEL auf hellem #C8D0D8!)
    "nav":      "#5A7A90",  # Bild↑, Bild↓, Pos 1, Ende
    "altgr":    "#3A6A8A",  # ², ³, {, [, ], }, \, @, €, µ, ~, | — BEREITS IN V5 GEMACHT
}
```

WICHTIG: Die Accent-Tasten (Esc, Enter, Pfeiltasten) haben HELLEN Hintergrund (#C8D0D8).
Deren Legends müssen DUNKEL sein (#2A3540), sonst kein Kontrast!

## Aufgabe 5: Detail-Keys prüfen

Unterhalb des Keyboards gibt es Detail-Ansichten:
- **Q-Taste:** Base #161820, Q-Legend #8899AA, @-AltGr #3A6A8A ← prüfen
- **L-Taste:** Base #161820, L-Legend #8899AA, kein AltGr ← prüfen  
- **Mac-Tasten (Ctrl, Opt, Cmd, ⌘, Ctrl):** Base #1E2830, Legends #5A7A90 ← prüfen

## Farb-Referenz (alle Hex-Codes)

### Keycap Base Colors
| Gruppe     | Hex       | PDF RGB (6 Dezimalstellen)       |
|-----------|-----------|----------------------------------|
| Alphas    | #161820   | 0.086275 0.094118 0.125490      |
| Modifiers | #1E2830   | 0.117647 0.156863 0.188235      |
| F-Keys    | #1C2228   | 0.109804 0.133333 0.156863      |
| Navigation| #1A2530   | 0.101961 0.145098 0.188235      |
| Accents   | #C8D0D8   | 0.784314 0.815686 0.847059      |
| Spacebar  | #BCC6D0   | 0.737255 0.776471 0.815686      |

### Legend Colors
| Gruppe           | Hex       | PDF RGB (6 Dezimalstellen)       |
|-----------------|-----------|----------------------------------|
| Alpha Legends   | #8899AA   | 0.533333 0.600000 0.666667      |
| Modifier Legends| #5A7A90   | 0.352941 0.478431 0.564706      |
| F-Key Legends   | #4A6070   | 0.290196 0.376471 0.439216      |
| Accent Legends  | #2A3540   | 0.164706 0.207843 0.250980      |
| Nav Legends     | #5A7A90   | 0.352941 0.478431 0.564706      |
| AltGr Legends   | #3A6A8A   | 0.227451 0.415686 0.541176      |

## REGELN

1. **Tastenpositionen NICHT ändern** — die kommen vom Hersteller-Template
2. **Float-Precision: 6 Dezimalstellen** — sonst Rundungsfehler (siehe KEYCAP_DESIGN_INSTRUCTIONS.md)
3. **Ein Design pro PDF** — keine zweiten Keyboards
4. **Cherry ISO-DE Layout** — deutsche Labels (Strg, Entf, Bild↑ etc.)
5. **Modifier-Symbole statt Text** — ⇪ statt CapsLk, ↹ statt Tab, ⇧ statt Shift
6. **PDF/X-4 Export** — für Hersteller-Kompatibilität mit Adobe Illustrator
7. **Vektoren nicht rastern** — alles muss Vektorpfade bleiben

## Abhängigkeiten
- pip install pikepdf
- Affinity Studio V3 (kostenlos, auf Antons Rechner)
- Repo: https://github.com/antonma/keyboards

## Output
- `templates/GK75-TheWell-v6.pdf`
- Commit: `fix: TheWell v6 — Cherry ISO-DE labels, per-group legend colors, cleanup`
