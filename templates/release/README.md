# templates/release/

## Zweck
Ein **Ordner je Release und Design** mit dem kompletten Hersteller-Paket (seit 2026-10-07).
Nur Meilenstein-Versionen, nicht der laufende Arbeitsstand. Die Arbeits-.af liegt weiterhin
unter `templates/hersteller/` (gitignored) und wird nie hierher verschoben, nur kopiert.

Alle .af und PDFs hier laufen über **Git LFS** (`.gitattributes`: `templates/release/**/*.af`
und `templates/release/**/*.pdf`).

## Struktur
```
templates/release/
  <design>/<version>_<YYYY-MM-DD>/
    DELTASET_<Design>_<version>.af
    DELTASET_<Design>_<version>.pdf                 # Druck-Export der .af
    DELTASET_<Design>_Project_Introduction_EN-CN.pdf
    DELTASET_<Design>_QC_Checklist_EN-CN.pdf
```
Aktuell: `alpine/139_2026-10-05/` (`DELTASET_Alpine_139.*`) und
`hello-moa/v1.36_2026-10-05/` (`DELTASET_Hello_MOA_v1.36.*`).

## Namensregeln
- Versionsnummer nur im **Ordnernamen** und in der **.af/.pdf des Designs**.
- Introduction und QC-Checkliste **ohne Version** im Dateinamen.
- Ein Release-Ordner = komplettes Paket für den Hersteller (genau diese 4 Dateien).

## REGEL: max. 1 Snapshot pro .af
Jede `.af` hier darf **höchstens einen** Affinity-Dokument-Snapshot enthalten. Snapshots/Verlauf
blähen die Datei stark auf — plausibler Zusammenhang (nicht gemessen): Hello_MOA v1.1 (142 MB)
→ v1.3 (206 MB) bei 135 Snapshots. Git kann die Anzahl nicht selbst prüfen (geschlossenes
Binärformat) — deshalb ist der QA-Schritt Pflicht.

## Release-Kette
1. `affinity-builder`: Kopie der Arbeits-.af in den neuen Release-Ordner (Speichern unter),
   Snapshots auf ≤ 1 reduzieren, per „Save As“ (Handschritt Anton), **PDF-Export** der .af (Druck-PDF).
   Arbeitsdatei bleibt unverändert.
2. `keycap-qa`: read-only, Snapshot-Anzahl ≤ 1 + Voll-Sweep GRÜN, Dateigröße notieren.
3. `pipeline-dev`: Project Introduction und QC-Checkliste aktuell bauen, unversioniert in den
   Ordner kopieren, LFS prüfen (`git check-attr filter`, nach `git add` `git lfs ls-files`),
   Commit + Push.
4. `brain-scribe`: Session-Log/Register.

Introductions ohne „-draft“ erst nach Antons Versandfreigabe.

## Altbestand
Die flachen Dateien `release_<design>_<version>_<YYYY-MM-DD>.af` direkt in diesem Ordner sind
**historisch (vor 2026-10-07)**. Sie bleiben unverändert liegen (kein Umzug, kein Löschen).

## Hinweise
- **LFS-Kontingent**: GitHub-Billing prüfen. Jede Version zählt voll (keine Deltas).
- **Backup der Arbeitsdateien**: offener Punkt, läuft außerhalb von Git (Ort legt Anton fest).
