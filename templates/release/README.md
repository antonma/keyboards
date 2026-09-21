# templates/release/

## Zweck
Dieser Ordner enthält ausschließlich **Meilenstein-Versionen** der Affinity-Templates —
die, die an den Hersteller rausgehen. Ein bis zwei Dateien pro Design, nicht der
laufende Arbeitsstand. Die Arbeits-.af liegt weiterhin unter `templates/hersteller/`
(gitignored, siehe `.gitignore`) und wird nie hierher verschoben, nur kopiert.

Dateien hier laufen über **Git LFS** (`.gitattributes`: `templates/release/**/*.af`).

## REGEL: max. 1 Snapshot pro Datei
Jede `.af` in diesem Ordner darf **höchstens einen** Affinity-Dokument-Snapshot enthalten.
Snapshots/Verlauf blähen die Datei stark auf — plausibler Zusammenhang (nicht gemessen):
Hello_MOA v1.1 (142 MB) → v1.3 (206 MB) bei 135 Snapshots.

Benennung: `release_<design>_<version>_<YYYY-MM-DD>.af`

## Release-Ablauf
1. Arbeitsdatei bleibt unter `templates/hersteller/` und wird dabei nie verändert.
2. `affinity-builder` erzeugt per "Speichern unter" eine **Kopie** nach `templates/release/`,
   löscht dort alle Snapshots bis auf einen und speichert ohne Verlauf.
3. `keycap-qa` prüft read-only per SDK: Snapshot-Anzahl ≤ 1, Voll-Sweep GRÜN,
   Dateigröße notieren.
4. Erst danach: commit + push.

Git kann die Snapshot-Anzahl nicht selbst prüfen (geschlossenes Binärformat) — deshalb
ist Schritt 3 Pflicht, kein optionaler Check.

## Hinweise
- **LFS-Kontingent**: GitHub-Billing prüfen. Jede Version zählt voll (keine Deltas),
  auch bei nur einem Snapshot pro Datei.
- **Backup der Arbeitsdateien**: offener Punkt. Läuft außerhalb von Git (z.B. Cloud-Sync
  wie Google Drive) — Ort legt Anton fest.
