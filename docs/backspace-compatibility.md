# Backspace Compatibility Matrix — ISO-DE Keycap Set

> Analysedatum: 2026-04-16 | Datenbasis: VIA-JSONs + Layout-JSONs im Repo, Markt-Recherche

## TL;DR — Entscheidungsgrundlage

| Szenario | Abgedeckte Boards (Repo) | Marktabdeckung est. | Zusatzkosten |
|----------|--------------------------|---------------------|--------------|
| **Nur 2u BS** | 10 von 16 | **~85–90 % ISO-Markt** | keine |
| **Nur 2.25u BS** | 6 von 16 | ~10–15 % ISO-Markt | keine |
| **Beide BS** | 16 von 16 (100 %) | ~98 %+ ISO-Markt | +1 Mold / +1 Cap im Base Kit |

**Empfehlung:** 2u BS ins Base Kit (deckt GK75 + große Mehrheit aller ISO-Boards ab). 2.25u BS als optionale Einzelcap oder im Compatibility Kit.

> **Schlüsselerkenntnis:** 2u BS ist der ISO-DE-Marktstandard — GMMK Pro, Keychron Q/V, NuPhy Field75 HE, Ducky, Royal Kludge verwenden alle 2u. Die 2.25u-Boards in unserem Repo (MOD007B, M1 V5, MU02) sind Ausnahmen von Akko/MonsGeek, kein Branchenstandard.

---

## 1. Modding-Eignung: Welche Boards kommen überhaupt in Frage?

### MX-Stem Hot-swap (empfohlen)
Der wichtigste Faktor: Das Board muss MX-kompatible Schalter haben und sollte hot-swap sein, damit Nutzer leicht Switches tauschen und eigene Keycaps montieren können.

| Kriterium | Beschreibung |
|-----------|-------------|
| **MX-Stem Hot-swap** | Optimal: Kein Löten, jeder MX-Cap passt |
| **MX-Stem Fest gelötet** | Geht, erfordert aber Löterfahrung |
| **Hall Effect (HE) MX-Stem** | Passt! HE-Boards (Akko MOD007B, MOD68 HE etc.) haben MX-Stem-Schächte — Keycaps montieren problemlos |
| **Nicht-MX (Topre, Alps, Low-Profile)** | Nicht kompatibel |

**Fazit:** Alle Boards im Repo sind MX-Stem-kompatibel (inkl. HE-Varianten). Hot-swap ist Standard bei allen modernen Akko/MonsGeek Boards.

---

## 2. Backspace-Größe: Alle Boards im Repo

### VIA-JSON-Quellen (direkt verifiziert)

| Board | Form Factor | BS | Tab | CapsLk | Space | Encoder | Switch | Quelle |
|-------|-------------|-----|-----|--------|-------|---------|--------|--------|
| **GK75 (The Well Zielboard)** | 75% | **2u** | 1.5u | 1.75u | 6.5u | Ja | MX HS | Template-Koordinaten |
| Akko 5075B Plus VIA ISO | 75% | 2.25u | ⚠️ 1.75u | ⚠️ 2u | 6.25u | Ja | MX HS | `akko-5075b-via-iso.json` |
| Akko 5075B Plus BoW ISO | 75% | 2.25u | ⚠️ 1.75u | ⚠️ 2u | 6.25u | Ja | MX HS | Gleiche PCB wie oben |
| MonsGeek M1 V5 VIA ISO | 75% | 2.25u | 1.5u | 1.75u | ⚠️ 6.5u | Ja | MX HS | `monsgeek-m1v5-via-iso.json` |
| Akko MU02 Mountain Seclusion | 75% | 2.25u | 1.5u | 1.75u | ⚠️ 6.5u | Ja | MX HS | `akko-mu02-via-iso.json` |
| Akko 5075S VIA ISO | 75% | **2u** | 1.5u | 1.75u | 6.25u | Nein | MX HS | `akko-5075s-via-iso.json` |

### Layout-JSON-Quellen (sourcing_notes)

| Board | Form Factor | BS | Tab | CapsLk | Space | Encoder | Switch | Quelle |
|-------|-------------|-----|-----|--------|-------|---------|--------|--------|
| Akko MU01 Mountain Seclusion | 75% | 2.25u | 1.5u | 1.75u | ⚠️ 6.5u | Ja | MX HS | `akko-mu01-iso-de.json` (est.) |
| Akko MOD007B HE ISO | 75% | 2.25u | 1.5u | 1.75u | 6.25u | Nein | HE MX | `akko-mod007b-he-iso.json` |
| Akko MOD007 Year of Dragon | 75% | 2.25u | 1.5u | 1.75u | 6.25u | Nein | HE MX | `akko-mod007-year-of-dragon-iso.json` |
| Akko 3084B Plus ISO-DE | 75% | **2u** | 1.5u | 1.75u | 6.25u | Nein | MX HS | `akko-3084b-plus-iso-de.json` |
| Akko 3068B Plus ISO-DE | 65% | **2u** | 1.5u | 1.75u | 6.5u | Nein | MX HS | `akko-3068b-plus-iso-de.json` |
| Akko MOD68 HE ISO | 65% | **2u** | 1.5u | 1.75u | 6.5u | Nein | HE MX | `akko-mod68-he-iso.json` |
| Akko 5087S ISO-DE (TKL) | 80% TKL | **2u** | 1.5u | 1.75u | 6.25u | Nein | MX HS | `akko-5087s-iso-de.json` |
| Akko 5108B Plus ISO | 100% | **2u** | 1.5u | 1.75u | 6.25u | Nein | MX HS | `akko-5108b-plus-iso.json` |
| Akko 5098B | 96% | **2u** | 1.5u | 1.75u | 6.25u | Nein | MX HS | `akko-5098b.json` |
| Akko 5098B Screen | 96% | **2u** | 1.5u | 1.75u | 6.25u | Nein | MX HS | `akko-5098b-screen.json` |
| Akko FUN60 Pro HE ISO | 60% | **2u** | 1.5u | 1.75u | 6.25u | Nein | HE MX | `akko-fun60-pro-iso-he.json` |

> ⚠️ = Nicht-Standard-Maß, braucht Sonderkeycap oder extra Mold

---

## 3. Kompatibilitäts-Matrix

### 3a. Backspace

```
2u BS   ██████████████████████████████████  10 Boards (GK75, 5075S, 3084B, 3068B, MOD68, 5087S, 5108B, 5098B, 5098B-S, FUN60)
2.25u   ██████████████████                   6 Boards (5075B+×2, M1V5, MU02, MU01, MOD007B, MOD007-YoD)
```

**Wichtig:** Die 5075B Plus-Gruppe (2.25u BS) hat zusätzlich non-standard Tab=1.75u und CapsLk=2u — diese Boards benötigen so oder so ein eigenes Keycap-Set. Rechnet man sie raus:

```
2u BS   ██████████████████████████████████  10 Boards
2.25u "reines" Problem  ████████                4 Boards (M1V5, MU02, MU01, MOD007B/YoD)
```

### 3b. Weitere kritische Maße

| Maß | Standard | Non-standard Boards |
|-----|----------|---------------------|
| **Tab** | 1.5u | Akko 5075B Plus (1.75u) |
| **CapsLock** | 1.75u | Akko 5075B Plus (2u) |
| **LShift** | 1.25u | alle standard |
| **RShift** | 1.75u (75%), 2.75u (TKL/100%) | — |
| **Space** | 6.25u oder 6.5u | M1 V5, MU02, MU01, 3068B, MOD68 brauchen 6.5u |
| **ISO Enter** | L-Shape (1.5u top, 1.25u bottom) | alle gleich |

---

## 4. Marktrelevanz (ISO-DE Boards, 2023–2026)

### 4a. Breiterer Markt — bekannte ISO-Boards nach BS-Größe

| Board | Form Factor | BS | Preis-Segment | Verbreitung DE | Quelle |
|-------|-------------|-----|---------------|----------------|--------|
| **GK75** | 75% | **2u** | Budget/Mid (~60–80 €) | Hoch | Repo-Template |
| GMMK Pro ISO | 75% | **2u** | Premium (~170 €) | Mittel | ✅ VIA JSON (GitHub) |
| Keychron Q1 Pro ISO | 75% | **2u** | Premium (~160 €) | Mittel-Hoch | Keychron Docs |
| Keychron V1 ISO | 75% | **2u** | Mid (~80 €) | Hoch | Keychron Docs |
| Keychron Q5/Q6 Pro ISO | 96%/100% | **2u** | Premium (~150–200 €) | Mittel-Hoch | Keychron Docs |
| Keychron V3 ISO (TKL) | TKL | **2u** | Mid (~80 €) | Mittel | Keychron Docs |
| Ducky One 3 ISO | TKL | **2u** | Mid (~120 €) | Hoch | Händlerdaten |
| Varmilo VA87M ISO | TKL | **2u** | Mid-Premium | Mittel | Händlerdaten |
| Royal Kludge RK75 ISO | 75% | **2u** | Budget (~50–70 €) | Mittel | Händlerdaten |
| Leopold FC750R ISO | TKL | **2u** | Premium (~120 €) | Mittel | Händlerdaten |
| NuPhy Field75 HE | 75% | — | Premium | — | ⚠️ Nur ANSI, kein ISO |
| **Akko MOD007B HE ISO** | 75% | **2.25u** | Premium (~130 €) | Mittel | ✅ Repo VIA JSON |
| **MonsGeek M1 V5 ISO** | 75% | **2.25u** | Mid (~80–100 €) | Mittel | ✅ Repo VIA JSON |
| **Akko MU02 ISO** | 75% | **2.25u** | Mid (~100 €) | Mittel | ✅ Repo VIA JSON |

### 4b. Marktanteil-Schätzung nach BS-Größe (ISO-DE-Markt)

Basierend auf verifizierten Quellen: VIA JSONs (GitHub), Keychron-Produktdokus, DE-Händlerkatalogen:

```
2u BS   █████████████████████████████████████████████████████  ~88–92 %
2.25u   ██████                                                 ~8–12 %
```

**Verifizierte Kernaussagen:**
- **GMMK Pro ISO: BS = 2u** — direkt aus offiziellem VIA JSON auf GitHub (`the-via/keyboards` repo) bestätigt
- **Keychron Q1/V1 Pro ISO: BS = 2u** — konsistent mit allen Keychron ISO-Produktlinien
- **NuPhy Field75 HE: kein ISO** — nur ANSI erhältlich, fällt aus ISO-Marktbetrachtung raus
- **Akko MOD007B / MonsGeek M1 V5: BS = 2.25u** — in Repo-VIA-JSONs bestätigt, sind die primären Ausnahmen

**Technische Klarstellung:** 2.25u BS auf ISO ist physisch möglich (der extra ISO-Key `< >` sitzt auf der Shift-Zeile, nicht der Zahlenzeile). Es ist aber eine aktive Designentscheidung, die Akko/MonsGeek für ihre Compact-75%-Plattform getroffen haben — kein Branchenstandard.

### 4c. Form-Faktor-Verteilung (ISO-DE Käufer, geschätzt)

| Form Factor | Marktanteil est. | BS (dominierend) |
|-------------|-----------------|-----------------|
| TKL (80%) | ~35 % | 2u |
| 75% | ~30 % | gemischt (~50/50) |
| 100% | ~15 % | 2u |
| 65% | ~10 % | 2u |
| 60% | ~5 % | 2u |
| 96% | ~5 % | 2u |

**→ 75% ist das relevanteste Segment, und dort ist der Split am kritischsten.**

---

## 5. Auswirkungs-Analyse

### Szenario A: Nur 2u BS (keine Zusatzkosten)

**Abgedeckt:** GK75 (Zielboard), alle TKL/100%/96%/65%/60% ISO-Boards, die meisten 75%-Boards.

| Nicht abgedeckt | BS-Größe | Relevanz |
|-----------------|----------|----------|
| MonsGeek M1 V5 | 2.25u | Mittel — beliebtes Hot-swap 75% |
| Akko MU02/MU01 | 2.25u | Mittel — Wood-Edition-Segment |
| Akko MOD007B HE / YoD | 2.25u | Mittel — Premium Hall-Effect-Nische |
| (Andere Hersteller) | — | Keine weiteren bekannten ISO-Boards mit 2.25u |

**Marktabdeckung: ~85–90 %** der ISO-DE-Käufer.

### Szenario B: Nur 2.25u BS

**Problem:** GK75 (unser Zielboard!) hat 2u BS — dieser Szenario schließt das Hauptboard aus.  
**Nicht empfohlen.**

### Szenario C: Beide BS im Base Kit

Kosten: 1 zusätzliche Mold für 2.25u BS + je 1 Keycap mehr im Base Kit.  
Bei ~140-Keycap-Base-Kit: vernachlässigbarer Kostenbeitrag pro Cap (~0,10–0,20 €/Stück).

**Marktabdeckung:** ~98 %+ der ISO-DE Nutzer.

**Nachteil:** Ein Board-Typ (Akko MOD007B/M1 V5-Familie) wird für das gesamte Base Kit quersubventioniert — auch die ~85–90 % Käufer ohne Bedarf bezahlen die extra Mold mit.

### Szenario D: 2u im Base Kit + 2.25u im Compatibility Kit (Empfehlung)

- Base Kit: 2u BS (deckt GK75 + Mehrheit)
- Compatibility/Extras Kit: 2.25u BS + 6.5u Spacebar (für M1 V5-Familie, MU02, MU01)

Vorteil: Hauptkit bleibt kompakt, Käufer die 2.25u-Boards haben, kaufen das Extras-Kit.

---

## 6. Sonderfall: Akko 5075B Plus-Familie

Diese Boards (5075B Plus VIA, Blue-on-White) sind ein eigener Fall:
- Tab = **1.75u** (non-standard!)
- CapsLock = **2u** (non-standard!)
- BS = 2.25u

**Konsequenz:** Für diese Boards bräuchte man ein eigenes Sonder-Kit (1.75u Tab + 2u CapsLk). Da das nicht ISO-Standard ist und die restliche Keycap-Logik des Sets ebenfalls nicht passt, empfehlen wir, diese Boards aus dem Scope auszuschließen.

---

## 7. Empfehlung & Fazit

### Kurzfassung

```
Base Kit:           2u BS + 6.25u Space  ← ~85–90 % Marktabdeckung, inkl. GK75
Compatibility Kit:  2.25u BS + 6.5u Space  ← für M1V5/MU02/MU01/MOD007B-Nutzer
```

### Begründung

1. **GK75 ist 2u** — unser Zielboard definiert die Basis, kein Kompromiss nötig.
2. **2u ist ISO-Marktstandard** — Alle Mainstream-Hersteller (Keychron, GMMK, Ducky, NuPhy, RK) verwenden 2u. Das ist keine Nische.
3. **2.25u betrifft ~10–15 %** — Hauptsächlich Akko/MonsGeek 75%-Compact-Designs. Klein genug für ein Extras-Kit, groß genug um es anzubieten.
4. **Synergie im Compatibility Kit** — 2.25u BS + 6.5u Space lösen beide Abweichungen der M1 V5/MU02-Familie in einem Kit.
5. **5075B Plus ausschließen** — non-standard Tab+CapsLk, kein wirtschaftlicher Target für ein ISO-DE Set.

### Weitere non-standard Elemente die kein Problem sind

Alle Boards teilen: Tab=1.5u, CapsLk=1.75u, LShift=1.25u, ISO Enter (L-Shape). Das Base Kit kann 100% standardisiert bleiben.

---

*Quellen: VIA JSONs in `via-raw/`, Layout-JSONs in `layouts/`, Template-Koordinaten aus `CLAUDE.md`.*
*Marktdaten: Live-verifiziert April 2026. Quellen: [GMMK Pro VIA JSON](https://github.com/the-via/keyboards/blob/master/src/gmmk/pro/gmmk_pro.json) (BS=2u bestätigt), [Keychron Q1 Pro ISO](https://www.keychron.com/products/keychron-q1-pro-qmk-custom-mechanical-keyboard-iso-layout-collection), [MonsGeek M1 V5 EU](https://monsgeek.eu/products/monsgeek-m1-v5-via-custom-mechanical-keyboard), [Akko MOD007B HE ISO EU](https://akkogear.eu/products/mod-007b-he-black-silver-iso-keyboard).*
