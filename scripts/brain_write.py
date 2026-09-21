"""
brain_write.py -- Ein-Schritt-Schreiber fuer Antons Brain DB (Supabase `notes`).

Ersetzt die ~19-Schritt-Handarbeit (curl, Datei schreiben, Antwort lesen, Dedup
per Hand pruefen, Supersede-SQL von Hand tippen) durch einen einzigen Aufruf.

Nur Standardbibliothek (urllib, json, argparse) -- kein `requests` noetig.
Erwartet die Env-Vars SUPABASE_URL und SUPABASE_KEY (service_role-Key).
Der Key wird NIE ausgegeben, auch nicht in Fehlermeldungen (siehe `_mask`).

Usage:
    py -3 scripts/brain_write.py --type knowledge --topic alpine-farbkorrektur \
        --title "Alpine-132 Kontrast: AA ab Ratio 4.5" \
        --summary "Kontrastmessung zeigt AA-Konformitaet erst ab 4.5:1." \
        --content-file d:\\tmp\\note.md

    py -3 scripts/brain_write.py --type handoff --project keycap-shop \
        --topic alpine-farbkorrektur --title "Handoff 2026-09-22: naechster Schritt" \
        --summary "Anton hat Onyx-Ton festgelegt, Recolor-Paket steht aus." \
        --content-file d:\\tmp\\handoff.md \
        --tldr-next "Recolor-Paket an affinity-builder geben" \
        --supersede 0d08dc4b-352c-4a6d-84b0-854203a62388

    py -3 scripts/brain_write.py --type knowledge --topic foo --title "Bar" \
        --summary "..." --content-file d:\\tmp\\note.md --update <note-id>

    py -3 scripts/brain_write.py --append-note <note-id> --append-text-file d:\\tmp\\zusatz.md

    py -3 scripts/brain_write.py --batch d:\\tmp\\batch.json

    py -3 scripts/brain_write.py --type knowledge --topic foo --title "Bar" \
        --summary "..." --content-file d:\\tmp\\note.md --dry-run

Exit-Codes:
    0  Erfolg (alle Aktionen durchgefuehrt)
    1  HTTP-/Laufzeitfehler
    2  Dedup-Treffer -- kein Insert, Kandidaten ausgegeben (--force zum Ueberschreiben)
    3  Offener Handoff-Vorgaenger im selben (project, topic) ohne --supersede-Bestaetigung
    4  Secret-Muster im Titel/Summary/Content gefunden -- Abbruch
    5  Ungueltiger Aufruf (fehlende Pflichtfelder, kaputte Batch-Datei, ...)

Schema/Regeln: siehe C:\\Users\\Yogi\\.claude\\skills\\brain-db\\SKILL.md
"""

import argparse
import io
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

DEFAULT_PROJECT = "keycap-shop"
DEFAULT_SOURCE_AGENT = "claude-code"

# Typen, die episodisch sind und normalerweise status='open' bekommen,
# bzw. 'resolved' (session-log ist per Definition abgeschlossen).
DEFAULT_STATUS_BY_TYPE = {
    "session-log": "resolved",
    "handoff": "open",
    "decision": "open",
    "state": "open",
    "knowledge": "open",
    "preference": "open",
    "how-to-use": "open",
}

VALID_TYPES = set(DEFAULT_STATUS_BY_TYPE) | {
    "project-index", "topic-index", "quick-map", "active-threads",
}

SECRET_PATTERNS = [
    re.compile(r"sb_secret_[A-Za-z0-9_-]+"),
    re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),  # JWT
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
]


def _mask(text: str) -> str:
    """Maskiert SUPABASE_KEY (falls im Text enthalten) und generische Secret-Muster."""
    key = os.environ.get("SUPABASE_KEY", "")
    if key and key in text:
        text = text.replace(key, "***MASKED***")
    for pat in SECRET_PATTERNS:
        text = pat.sub("***MASKED***", text)
    return text


def find_secrets(*texts):
    """Gibt das erste gefundene Secret-Muster zurueck (maskiert), sonst None."""
    for text in texts:
        if not text:
            continue
        for pat in SECRET_PATTERNS:
            m = pat.search(text)
            if m:
                return pat.pattern
    return None


class BrainDBError(RuntimeError):
    pass


class BrainClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def _headers(self, extra=None):
        h = {
            "apikey": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if extra:
            h.update(extra)
        return h

    def _request(self, method: str, path: str, body=None, extra_headers=None):
        url = f"{self.base_url}{path}"
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(url, data=data, method=method,
                                      headers=self._headers(extra_headers))
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read()
                return resp.status, (json.loads(raw) if raw else None)
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="replace")
            raise BrainDBError(f"HTTP {e.code} {method} {path}: {_mask(raw)}") from None
        except urllib.error.URLError as e:
            raise BrainDBError(f"Verbindungsfehler {method} {path}: {_mask(str(e.reason))}") from None

    def select(self, table: str, params: dict):
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        status, body = self._request("GET", f"/rest/v1/{table}?{qs}")
        return body or []

    def insert(self, table: str, row: dict):
        status, body = self._request(
            "POST", f"/rest/v1/{table}", body=row,
            extra_headers={"Prefer": "return=representation"},
        )
        if not body:
            raise BrainDBError(f"Insert in {table} lieferte keine Repraesentation zurueck")
        return body[0]

    def patch(self, table: str, row_id: str, fields: dict):
        status, body = self._request(
            "PATCH", f"/rest/v1/{table}?id=eq.{row_id}", body=fields,
            extra_headers={"Prefer": "return=representation"},
        )
        if not body:
            raise BrainDBError(f"Patch auf {table}?id=eq.{row_id} lieferte keine Zeile zurueck")
        return body[0]

    def search_hybrid(self, query: str, project=None, note_type=None, count=8):
        body = {"query": query, "mode": "hybrid", "count": count}
        if project:
            body["project"] = project
        if note_type:
            body["type"] = note_type
        status, resp = self._request(
            "POST", "/functions/v1/search-notes", body=body,
        )
        return (resp or {}).get("results", [])


def get_client() -> BrainClient:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise BrainDBError("SUPABASE_URL / SUPABASE_KEY nicht gesetzt (Env-Variablen fehlen)")
    return BrainClient(url, key)


def read_text_file(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def dedup_check(client: BrainClient, project: str, note_type: str, topic: str,
                 title: str, summary: str):
    """Titel-Suche + Hybrid-Suche. Gibt Liste kompakter Kandidaten-Dicts zurueck."""
    candidates = {}

    # (a) Titel-Suche (ilike) im selben project
    title_escaped = title.replace("*", "").replace(",", "")
    rows = client.select("notes", {
        "select": "id,type,topic,title,status,updated_at",
        "project": f"eq.{project}",
        "title": f"ilike.*{urllib_quote(title_escaped)}*",
    })
    for r in rows:
        candidates[r["id"]] = {**r, "match": "title"}

    # (b) Hybrid-Suche mit summary (oder title als Fallback)
    query_text = summary or title
    try:
        hits = client.search_hybrid(query_text, project=project, note_type=note_type, count=8)
    except BrainDBError:
        hits = []  # Suche darf nicht den ganzen Lauf blockieren
    for h in hits:
        cid = h.get("id")
        if not cid:
            continue
        entry = {
            "id": cid, "type": h.get("type"), "topic": h.get("topic"),
            "title": h.get("title"), "status": h.get("status"),
            "updated_at": h.get("updated_at"), "score": h.get("score"),
            "match": "hybrid",
        }
        if cid in candidates:
            candidates[cid]["match"] = "title+hybrid"
            candidates[cid]["score"] = h.get("score")
        else:
            candidates[cid] = entry

    return list(candidates.values())


def urllib_quote(s: str) -> str:
    from urllib.parse import quote
    return quote(s, safe="")


def is_exact_or_close_match(candidates, title, topic, note_type):
    """True wenn ein Kandidat exakter Titel-Treffer ist, oder sehr aehnlich im
    selben (topic, type)."""
    for c in candidates:
        if c.get("title") == title:
            return c
        if (c.get("topic") == topic and c.get("type") == note_type
                and c.get("match") in ("title", "title+hybrid")):
            return c
        score = c.get("score")
        if score is not None and score >= 0.9 and c.get("topic") == topic:
            return c
    return None


def find_open_handoff(client: BrainClient, project: str, topic: str):
    rows = client.select("notes", {
        "select": "id,title,tldr_next,tldr_blocked,status,updated_at",
        "project": f"eq.{project}",
        "topic": f"eq.{topic}",
        "type": "eq.handoff",
        "status": "eq.open",
        "order": "updated_at.desc",
        "limit": "1",
    })
    return rows[0] if rows else None


def build_row(args) -> dict:
    row = {
        "type": args.type,
        "project": args.project,
        "title": args.title,
        "status": args.status or DEFAULT_STATUS_BY_TYPE.get(args.type, "open"),
        "summary": args.summary,
        "content": args.content,
        "source_agent": args.source_agent,
    }
    if args.topic:
        row["topic"] = args.topic
    if args.tldr_next:
        row["tldr_next"] = args.tldr_next
    if args.tldr_done:
        row["tldr_done"] = args.tldr_done
    if args.blocked_reason:
        row["tldr_blocked"] = args.blocked_reason
    if args.tags:
        row["tags"] = args.tags
    return row


def print_action(**kwargs):
    print(json.dumps(kwargs, ensure_ascii=False))


def do_write(client: BrainClient, args) -> int:
    """Fuehrt einen einzelnen (nicht-batch) Schreibvorgang aus. Gibt Exit-Code zurueck."""

    # --- Append-Modus: separater, einfacher Pfad ---
    if args.append_note:
        if not args.append_text_file:
            print("Fehler: --append-note braucht --append-text-file", file=sys.stderr)
            return 5
        append_text = read_text_file(args.append_text_file)
        secret = find_secrets(append_text)
        if secret:
            print(json.dumps({"error": "secret_detected", "pattern": secret}))
            return 4
        existing = client.select("notes", {
            "select": "id,content", "id": f"eq.{args.append_note}",
        })
        if not existing:
            print(f"Fehler: Note {args.append_note} nicht gefunden", file=sys.stderr)
            return 5
        new_content = existing[0]["content"] + "\n\n---\n" + append_text
        if args.dry_run:
            print_action(action="dry-run-patch", table="notes", id=args.append_note,
                          body_preview=new_content[-200:])
            return 0
        updated = client.patch("notes", args.append_note, {"content": new_content})
        print_action(action="append", id=updated["id"])
        return 0

    # --- Pflichtfelder ---
    if not (args.title and args.summary and args.content is not None):
        print("Fehler: --title, --summary und --content-file sind Pflicht "
              "(ausser bei --append-note)", file=sys.stderr)
        return 5
    if args.type not in VALID_TYPES:
        print(f"Fehler: unbekannter --type '{args.type}'. Erlaubt: {sorted(VALID_TYPES)}",
              file=sys.stderr)
        return 5
    if args.type == "handoff" and not (args.topic and args.tldr_next):
        print("Fehler: --type handoff braucht --topic und --tldr-next", file=sys.stderr)
        return 5

    # --- Secret-Schutz ---
    secret = find_secrets(args.title, args.summary, args.content)
    if secret:
        print(json.dumps({"error": "secret_detected", "pattern": secret}))
        return 4

    # --- Update-Modus (PATCH statt INSERT) ---
    if args.update:
        row = build_row(args)
        if args.dry_run:
            print_action(action="dry-run-patch", table="notes", id=args.update,
                          body_preview={k: (v if k != "content" else v[:120]) for k, v in row.items()})
            return 0
        updated = client.patch("notes", args.update, row)
        print_action(action="update", type=args.type, id=updated["id"], title=updated["title"])
        for sup_id in args.supersede:
            _do_supersede(client, sup_id, updated["id"], args.dry_run)
        return 0

    # --- Dedup-Check (Standard an, --force ueberspringt den Abbruch) ---
    candidates = []
    if not args.no_dedup:
        candidates = dedup_check(client, args.project, args.type, args.topic or "", args.title, args.summary)
        if candidates:
            print("Dedup-Kandidaten gefunden:")
            for c in candidates:
                print(json.dumps({k: c.get(k) for k in
                                   ("id", "type", "topic", "title", "status", "updated_at", "score", "match")},
                                  ensure_ascii=False))
        match = is_exact_or_close_match(candidates, args.title, args.topic or "", args.type)
        if match and not args.force:
            print(json.dumps({
                "error": "dedup_match",
                "candidate_id": match["id"],
                "hint": f"Nutze --update {match['id']} oder --force zum Ueberschreiben",
            }, ensure_ascii=False))
            return 2

    # --- Handoff-Supersede-Regel ---
    if args.type == "handoff":
        prev = find_open_handoff(client, args.project, args.topic)
        if prev and prev["id"] not in args.supersede:
            print(json.dumps({
                "error": "open_predecessor_handoff",
                "predecessor_id": prev["id"],
                "predecessor_tldr_next": prev.get("tldr_next"),
                "predecessor_tldr_blocked": prev.get("tldr_blocked"),
                "hint": f"Uebernimm die offenen Punkte und bestaetige mit --supersede {prev['id']}",
            }, ensure_ascii=False))
            return 3

    row = build_row(args)

    if args.dry_run:
        print_action(action="dry-run-insert", table="notes",
                      body_preview={k: (v if k != "content" else v[:120]) for k, v in row.items()})
        for sup_id in args.supersede:
            print_action(action="dry-run-supersede", id=sup_id, superseded_by="<neue-id>")
        return 0

    inserted = client.insert("notes", row)
    print_action(action="insert", type=args.type, id=inserted["id"], title=inserted["title"])

    for sup_id in args.supersede:
        _do_supersede(client, sup_id, inserted["id"], dry_run=False)

    return 0


def _do_supersede(client: BrainClient, old_id: str, new_id: str, dry_run: bool):
    if dry_run:
        print_action(action="dry-run-supersede", id=old_id, superseded_by=new_id)
        return
    client.patch("notes", old_id, {"superseded_by": new_id, "status": "resolved"})
    print_action(action="supersede", id=old_id, superseded_by=new_id)


def run_batch(client: BrainClient, batch_path: str, dry_run_override: bool) -> int:
    batch_file = Path(batch_path)
    with open(batch_file, encoding="utf-8") as f:
        entries = json.load(f)
    if not isinstance(entries, list):
        print("Fehler: --batch Datei muss eine JSON-Liste sein", file=sys.stderr)
        return 5

    id_refs = {}  # "@1" -> real id (1-indexiert, in Reihenfolge der Liste)
    for i, entry in enumerate(entries, start=1):
        content_file = entry.get("content_file")
        content = None
        if content_file:
            cf = Path(content_file)
            if not cf.is_absolute():
                cf = batch_file.parent / cf
            content = read_text_file(str(cf))
        elif "content" in entry:
            content = entry["content"]

        supersede_refs = entry.get("supersede", [])
        resolved_supersede = []
        for ref in supersede_refs:
            if isinstance(ref, str) and ref.startswith("@"):
                idx = ref[1:]
                if idx not in id_refs:
                    print(f"Fehler: Batch-Eintrag {i} referenziert unbekanntes {ref}", file=sys.stderr)
                    return 5
                resolved_supersede.append(id_refs[idx])
            else:
                resolved_supersede.append(ref)

        ns = argparse.Namespace(
            type=entry.get("type"),
            project=entry.get("project", DEFAULT_PROJECT),
            topic=entry.get("topic"),
            title=entry.get("title"),
            summary=entry.get("summary"),
            content=content,
            source_agent=entry.get("source_agent", DEFAULT_SOURCE_AGENT),
            status=entry.get("status"),
            tldr_next=entry.get("tldr_next"),
            tldr_done=entry.get("tldr_done"),
            blocked_reason=entry.get("blocked_reason"),
            tags=entry.get("tags"),
            update=entry.get("update"),
            supersede=resolved_supersede,
            append_note=entry.get("append_note"),
            append_text_file=entry.get("append_text_file"),
            no_dedup=entry.get("no_dedup", False),
            force=entry.get("force", False),
            dry_run=dry_run_override,
        )
        rc = do_write(client, ns)
        if rc != 0:
            print(f"Abbruch bei Batch-Eintrag {i} (Exit {rc}). Vorherige Eintraege wurden "
                  f"bereits geschrieben (siehe Ausgabe oben).", file=sys.stderr)
            return rc

        # letzte insert/update-Aktion dieses Eintrags als @i merken (fuer Folge-Supersedes)
        # (do_write druckt die id, aber wir brauchen sie hier -- daher separat holen)
        # Einfachster Weg: erneut aus der DB lesen ueber Titel+project+type, juengste zuerst.
        rows = client.select("notes", {
            "select": "id", "project": f"eq.{ns.project}", "type": f"eq.{ns.type}",
            "title": f"eq.{urllib_quote(ns.title)}", "order": "updated_at.desc", "limit": "1",
        })
        if rows:
            id_refs[str(i)] = rows[0]["id"]

    return 0


def parse_args():
    p = argparse.ArgumentParser(
        description="Schreibt Notes/Handoffs in Antons Brain DB (Supabase) in einem Aufruf.",
    )
    p.add_argument("--type", help="notes.type, z.B. knowledge, handoff, decision, state, session-log")
    p.add_argument("--project", default=DEFAULT_PROJECT)
    p.add_argument("--topic", help="Slug, Pflicht bei --type handoff")
    p.add_argument("--title")
    p.add_argument("--summary", help="1-Satz-TL;DR")
    p.add_argument("--content-file", help="UTF-8 Markdown-Datei mit dem vollen Content")
    p.add_argument("--source-agent", default=DEFAULT_SOURCE_AGENT)
    p.add_argument("--status", help="Ueberschreibt den Typ-Default fuer notes.status")
    p.add_argument("--tldr-next", help="notes.tldr_next -- Pflicht bei --type handoff")
    p.add_argument("--tldr-done", help="notes.tldr_done")
    p.add_argument("--blocked", action="store_true",
                    help="Nur Marker; nutze --blocked-reason fuer den Text (tldr_blocked)")
    p.add_argument("--blocked-reason", help="notes.tldr_blocked")
    p.add_argument("--tags", nargs="*", help="notes.tags (Liste)")

    p.add_argument("--update", metavar="NOTE_ID", help="PATCH statt INSERT auf diese Note-ID")
    p.add_argument("--supersede", metavar="NOTE_ID", action="append", default=[],
                   help="Nach erfolgreichem Insert: superseded_by=neue-ID + status=resolved auf diese ID(s). Mehrfach erlaubt.")
    p.add_argument("--append-note", metavar="NOTE_ID",
                   help="Haengt --append-text-file ans Ende des Contents dieser Note an (statt Insert)")
    p.add_argument("--append-text-file")

    p.add_argument("--no-dedup", action="store_true", help="Dedup-Suche ueberspringen")
    p.add_argument("--force", action="store_true",
                   help="Dedup-Abbruch (Exit 2) ueberspringen; Suche laeuft und wird trotzdem gemeldet")

    p.add_argument("--dry-run", action="store_true",
                   help="Alles pruefen (Dedup, Vorgaenger, Secret-Check), nichts schreiben")

    p.add_argument("--batch", metavar="PATH", help="JSON-Datei mit Liste von Eintraegen")

    args = p.parse_args()

    if args.batch:
        return args

    if args.content_file:
        args.content = read_text_file(args.content_file)
    else:
        args.content = None

    return args


def main():
    args = parse_args()

    try:
        client = get_client()
    except BrainDBError as e:
        print(f"Fehler: {_mask(str(e))}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.batch:
            rc = run_batch(client, args.batch, args.dry_run)
        else:
            rc = do_write(client, args)
    except BrainDBError as e:
        print(f"Fehler: {_mask(str(e))}", file=sys.stderr)
        sys.exit(1)

    sys.exit(rc)


if __name__ == "__main__":
    main()
