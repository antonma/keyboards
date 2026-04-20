"""
build_design.py — End-to-End design build orchestrator

Reads a build-config YAML and executes the full pipeline:
  1. generate_artwork   (Ideogram API)
  2. [REVIEW GATE 1]   pause + push artwork-review branch
  3. slice_artwork      (per-group tile slicing)
  4. place_artwork      (PDF placement)
  5. recolor            (body/legend color ops)
  6. verify_template    (quality gate)
  7. [REVIEW GATE 2]   pause + push final PDF for review
  8. merge + commit     (on 'commit' signal)

Usage:
    py -3 scripts/build_design.py --design terminal-v2
    py -3 scripts/build_design.py --design oni-v4 --resume gate2
    py -3 scripts/build_design.py --design the-well --dry-run
    py -3 scripts/build_design.py --list

Review gates pause and print a GitHub URL for mobile review.
Resume with --resume gate1 or --resume gate2.
"""

import argparse
import io
import json
import os
import subprocess
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

try:
    import yaml
except ImportError:
    yaml = None

REPO = Path(__file__).resolve().parent.parent
BUILD_CONFIGS_DIR = REPO / "build-configs"
STATE_DIR = REPO / ".build-state"
GITHUB_REPO = "antonma/keyboards"


# ── YAML loader fallback (minimal) ───────────────────────────────────────────

def load_yaml(path: Path) -> dict:
    if yaml:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    # Minimal fallback: only handles simple key: value and lists
    # For complex configs, install PyYAML: py -3 -m pip install pyyaml
    print("WARN: PyYAML not installed — using minimal parser. Install with: py -3 -m pip install pyyaml")
    result = {}
    current_list_key = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            stripped = line.rstrip()
            if not stripped or stripped.lstrip().startswith("#"):
                continue
            if stripped.startswith("  - "):
                if current_list_key:
                    result.setdefault(current_list_key, []).append(stripped[4:].strip())
            elif ":" in stripped:
                k, _, v = stripped.partition(":")
                k = k.strip()
                v = v.strip()
                if v:
                    result[k] = v
                    current_list_key = None
                else:
                    current_list_key = k
                    result[k] = []
    return result


# ── State management ─────────────────────────────────────────────────────────

def load_state(design: str) -> dict:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    state_file = STATE_DIR / f"{design}.json"
    if state_file.exists():
        return json.loads(state_file.read_text(encoding="utf-8"))
    return {"design": design, "stage": "start", "artworks": {}}


def save_state(design: str, state: dict):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    state_file = STATE_DIR / f"{design}.json"
    state_file.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def clear_state(design: str):
    state_file = STATE_DIR / f"{design}.json"
    if state_file.exists():
        state_file.unlink()


# ── Git helpers ───────────────────────────────────────────────────────────────

def git(*args, check=True) -> subprocess.CompletedProcess:
    return subprocess.run(["git"] + list(args), cwd=REPO, check=check,
                          capture_output=True, text=True)


def current_branch() -> str:
    return git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()


def push_review_branch(design: str, stage: str):
    branch = f"artwork-review/{design}"
    try:
        git("checkout", "-B", branch)
        git("add", "images", "templates", "build-configs")
        git("commit", "-m", f"[review] {design} — {stage}", "--allow-empty")
        git("push", "origin", branch, "--force")
        git("checkout", "master")
        print(f"\n  Branch pushed: {branch}")
        print(f"  Review at: https://github.com/{GITHUB_REPO}/tree/{branch}")
    except subprocess.CalledProcessError as e:
        print(f"  WARN: git push failed: {e.stderr}")
        git("checkout", "master", check=False)


# ── Script runners ────────────────────────────────────────────────────────────

def run_script(script: str, *args) -> int:
    cmd = ["py", "-3", str(REPO / "scripts" / script)] + list(args)
    print(f"  $ {' '.join(cmd[2:])}")
    result = subprocess.run(cmd, cwd=REPO)
    return result.returncode


# ── Review gate ───────────────────────────────────────────────────────────────

def review_gate(design: str, stage: str, files_to_review: list, config: dict):
    print("\n" + "═" * 60)
    print(f"  🎨 REVIEW GATE — {stage.upper()}: {design}")
    print("═" * 60)
    for f in files_to_review:
        print(f"  {f}")

    push_review_branch(design, stage)

    print(f"""
  Instructions:
    ok / weiter    → continue pipeline
    verwerfen      → abort (nothing committed to master)
    re-prompt <name>: <new prompt>  → re-generate one artwork

  Waiting for your input:""")

    while True:
        try:
            response = input("  > ").strip().lower()
        except EOFError:
            response = "ok"

        if response in ("ok", "weiter", "continue", ""):
            print("  Continuing ...")
            return "continue"
        elif response in ("verwerfen", "abort"):
            print("  Aborting build.")
            return "abort"
        elif response.startswith("re-prompt"):
            print("  Re-prompt not yet implemented in CLI — re-run with updated config.")
            return "abort"
        else:
            print("  (ok / verwerfen)")


# ── Main pipeline ─────────────────────────────────────────────────────────────

def list_designs():
    configs = sorted(BUILD_CONFIGS_DIR.glob("*.yaml")) + sorted(BUILD_CONFIGS_DIR.glob("*.yml"))
    if not configs:
        print("No build configs found in build-configs/")
        return
    print("Available designs:")
    for c in configs:
        print(f"  {c.stem}")


def build(design: str, resume_from: str | None, dry_run: bool):
    config_path = BUILD_CONFIGS_DIR / f"{design}.yaml"
    if not config_path.exists():
        config_path = BUILD_CONFIGS_DIR / f"{design}.yml"
    if not config_path.exists():
        print(f"ERROR: No build config found for '{design}' in build-configs/")
        sys.exit(1)

    config = load_yaml(config_path)
    state  = load_state(design)

    print(f"build_design: {design}")
    print(f"  Config : {config_path.name}")
    print(f"  Resume : {resume_from or 'start'}")
    print(f"  Dry run: {dry_run}")
    print()

    base_pdf = REPO / config.get("base_template_pdf", "")
    if not base_pdf.exists():
        print(f"ERROR: base_template_pdf not found: {base_pdf}")
        sys.exit(1)

    working_pdf = REPO / "templates" / f"{design}-wip.pdf"
    import shutil
    shutil.copy(base_pdf, working_pdf)
    print(f"  Working PDF: {working_pdf.name}")

    artworks = config.get("artworks", [])
    color_ops = config.get("color_operations", [])

    # ── Stage: artwork generation ─────────────────────────────────────────────
    if not resume_from or resume_from == "start":
        print("\n── Stage 1: Artwork generation ──")
        generated = []
        for aw in artworks:
            prompt  = aw.get("prompt", "")
            group   = aw.get("target_group", "fkey")
            aspect  = aw.get("aspect_ratio", "ASPECT_1_1")
            model   = aw.get("model", "turbo")
            name    = aw.get("name", group)
            out_png = f"images/{design}/{name}.png"

            if dry_run:
                rc = run_script("generate_artwork.py",
                                "--prompt", prompt,
                                "--aspect", aspect,
                                "--model", model,
                                "--output", out_png,
                                "--dry-run")
            else:
                rc = run_script("generate_artwork.py",
                                "--prompt", prompt,
                                "--aspect", aspect,
                                "--model", model,
                                "--output", out_png)
            if rc != 0:
                print(f"\nERROR: Artwork generation failed for '{name}'")
                sys.exit(1)
            generated.append(out_png)

        state["stage"] = "gate1"
        save_state(design, state)

        # ── Gate 1 ────────────────────────────────────────────────────────────
        if not dry_run:
            result = review_gate(design, "gate1 — artworks generated", generated, config)
            if result == "abort":
                clear_state(design)
                sys.exit(0)

    # ── Stage: slice + place + recolor ────────────────────────────────────────
    if not resume_from or resume_from in ("start", "gate1", "gate2"):
        if resume_from != "gate2":
            print("\n── Stage 2: Slice / Place / Recolor ──")

            if dry_run:
                print("  [DRY RUN] Would execute:")
                for aw in artworks:
                    group = aw.get("target_group", "fkey")
                    name  = aw.get("name", group)
                    print(f"    slice_artwork  --source images/{design}/{name}.png --group {group}")
                    print(f"    place_artwork  --group {group} → {design}-wip.pdf")
                for op in color_ops:
                    print(f"    recolor        {op.get('group')}:{op.get('property')}:{op.get('color')}")
                print(f"    verify_template {design}-wip.pdf")
                print("\n[DRY RUN] Pipeline complete — no commits made.")
                return

            for aw in artworks:
                group   = aw.get("target_group", "fkey")
                name    = aw.get("name", group)
                strategy = aw.get("strategy", "matrix")
                palette  = aw.get("palette", "none")
                size     = str(aw.get("size", 434))
                src_png  = f"images/{design}/{name}.png"
                out_dir  = f"images/{design}/sliced/{group}"

                rc = run_script("slice_artwork.py",
                                "--source", src_png,
                                "--group", group,
                                "--output-dir", out_dir,
                                "--strategy", strategy,
                                "--palette", palette,
                                "--size", size)
                if rc != 0:
                    print(f"\nERROR: Slice failed for '{name}'")
                    sys.exit(1)

                next_pdf = REPO / "templates" / f"{design}-wip2.pdf"
                rc = run_script("place_artwork.py",
                                "--input", str(working_pdf),
                                "--tiles", out_dir,
                                "--group", group,
                                "--output", str(next_pdf))
                if rc != 0:
                    print(f"\nERROR: Place failed for '{name}'")
                    sys.exit(1)
                import shutil
                shutil.move(next_pdf, working_pdf)

            for op in color_ops:
                group = op.get("group", "")
                prop  = op.get("property", "body")
                color = op.get("color", "#000000")
                next_pdf = REPO / "templates" / f"{design}-wip2.pdf"
                rc = run_script("recolor.py",
                                "--input", str(working_pdf),
                                "--group", group,
                                "--property", prop,
                                "--color", color,
                                "--output", str(next_pdf))
                if rc != 0:
                    print(f"\nERROR: Recolor failed for {group}:{prop}:{color}")
                    sys.exit(1)
                import shutil
                shutil.move(next_pdf, working_pdf)

            # ── Verify ───────────────────────────────────────────────────────
            print("\n── Stage 3: Verify ──")
            rc = run_script("verify_template.py", str(working_pdf))
            if rc != 0:
                print("\nERROR: verify_template failed — fix before continuing")
                sys.exit(1)

            state["stage"] = "gate2"
            save_state(design, state)

        # ── Gate 2 ────────────────────────────────────────────────────────────
        if not dry_run:
            final_pdf = REPO / "templates" / f"{design}.pdf"
            import shutil
            shutil.copy(working_pdf, final_pdf)

            result = review_gate(
                design, "gate2 — build complete",
                [str(final_pdf)],
                config,
            )
            if result == "abort":
                print("  Build aborted. Working files kept for inspection.")
                sys.exit(0)

    # ── Final commit ──────────────────────────────────────────────────────────
    if not dry_run:
        print("\n── Stage 4: Commit to master ──")
        final_pdf = REPO / "templates" / f"{design}.pdf"
        import shutil
        shutil.copy(working_pdf, final_pdf)

        branch = f"artwork-review/{design}"
        try:
            git("checkout", "master")
            git("merge", "--no-ff", branch, "-m", f"build: {design} — E2E pipeline")
            git("push", "origin", "master")
            print(f"  Merged {branch} → master and pushed.")
        except subprocess.CalledProcessError:
            # Fallback: direct commit
            git("add", str(final_pdf))
            git("commit", "-m", f"build: {design} — E2E pipeline")
            git("push", "origin", "master")

        working_pdf.unlink(missing_ok=True)
        clear_state(design)
        print(f"\nBuild complete: templates/{design}.pdf")
    else:
        print("\n[DRY RUN] Pipeline complete — no commits made.")
        print(f"  Working PDF: {working_pdf}")

    print("\nDone.")


def main():
    p = argparse.ArgumentParser(description="E2E design build orchestrator")
    p.add_argument("--design",  help="Design name (matches build-configs/<name>.yaml)")
    p.add_argument("--resume",  choices=["gate1", "gate2"], help="Resume from a review gate")
    p.add_argument("--dry-run", action="store_true", help="Run without API calls or git commits")
    p.add_argument("--list",    action="store_true", help="List available designs")
    args = p.parse_args()

    if args.list:
        list_designs()
        return

    if not args.design:
        p.error("--design is required (or use --list)")

    build(args.design, args.resume, args.dry_run)


if __name__ == "__main__":
    main()
