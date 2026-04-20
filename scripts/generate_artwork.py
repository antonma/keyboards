"""
generate_artwork.py — Ideogram API v3 wrapper

Usage:
    py -3 scripts/generate_artwork.py \\
        --prompt "moon surface, detailed craters" \\
        --aspect ASPECT_1_1 \\
        --model turbo \\
        --output images/oni-v4/mond.png

    py -3 scripts/generate_artwork.py --help

Env:
    IDEOGRAM_API_KEY  required — set as Codespace secret

Output:
    <output>.png            — generated image
    <output>.meta.json      — prompt, model, seed, cost estimate
"""

import argparse
import io
import json
import os
import sys
import time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

IDEOGRAM_URL = "https://api.ideogram.ai/v1/ideogram-v3/generate"
COST_PER_IMAGE = {
    "turbo":   0.08,
    "default": 0.12,
    "quality": 0.16,
}
# V3 API format (lowercase with x)
VALID_ASPECTS_V3 = [
    "1x1", "4x3", "3x4", "16x9", "9x16",
    "16x10", "10x16", "2x3", "3x2", "3x1", "1x3",
    "2x1", "1x2", "4x5", "5x4",
]
# Legacy format → V3 format (for backward compat with build-configs)
ASPECT_MAP = {
    "ASPECT_1_1":   "1x1",
    "ASPECT_4_3":   "4x3",
    "ASPECT_3_4":   "3x4",
    "ASPECT_16_9":  "16x9",
    "ASPECT_9_16":  "9x16",
    "ASPECT_16_3":  "3x1",   # closest: 3:1 wide (F-row)
    "ASPECT_3_1":   "3x1",
    "ASPECT_10_16": "10x16",
}
VALID_ASPECTS = list(ASPECT_MAP.keys()) + VALID_ASPECTS_V3
MAX_RETRIES = 3
RETRY_BASE_DELAY = 5.0


def parse_args():
    p = argparse.ArgumentParser(description="Generate artwork via Ideogram API v3")
    p.add_argument("--prompt",  required=True, help="Image generation prompt")
    p.add_argument("--output",  required=True, help="Output PNG path (e.g. images/oni-v4/mond.png)")
    p.add_argument("--aspect",  default="ASPECT_1_1", choices=VALID_ASPECTS, help="Aspect ratio")
    p.add_argument("--model",   default="turbo", choices=["turbo", "default", "quality"])
    p.add_argument("--negative", default="", help="Negative prompt")
    p.add_argument("--seed",    type=int, default=None, help="Seed for reproducibility")
    p.add_argument("--dry-run", action="store_true", help="Print request without calling API")
    return p.parse_args()


def get_api_key() -> str:
    key = os.environ.get("IDEOGRAM_API_KEY", "")
    if not key:
        print("ERROR: IDEOGRAM_API_KEY env var not set.", file=sys.stderr)
        print("  Set it as a Codespace secret or: export IDEOGRAM_API_KEY=<key>", file=sys.stderr)
        sys.exit(1)
    return key


def call_ideogram(api_key: str, payload: dict, retries: int = MAX_RETRIES) -> dict:
    """POST to Ideogram API with exponential backoff on rate-limit / server errors."""
    try:
        import urllib.request
        import urllib.error
    except ImportError:
        pass  # stdlib

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        IDEOGRAM_URL,
        data=data,
        headers={
            "Api-Key": api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )

    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            if e.code in (429, 500, 502, 503) and attempt < retries:
                delay = RETRY_BASE_DELAY * (2 ** (attempt - 1))
                print(f"  HTTP {e.code} — retrying in {delay:.0f}s (attempt {attempt}/{retries})")
                time.sleep(delay)
            else:
                print(f"ERROR: Ideogram API returned HTTP {e.code}: {body}", file=sys.stderr)
                sys.exit(1)
        except Exception as e:
            print(f"ERROR: Request failed: {e}", file=sys.stderr)
            sys.exit(1)


def download_image(url: str, output_path: Path) -> None:
    import urllib.request
    output_path.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, output_path)


def write_metadata(output_path: Path, args, response: dict) -> None:
    images = response.get("data", [{}])
    first = images[0] if images else {}
    meta = {
        "prompt": args.prompt,
        "negative_prompt": args.negative,
        "aspect_ratio": args.aspect,
        "model": args.model,
        "seed": first.get("seed"),
        "url": first.get("url", ""),
        "cost_estimate_usd": COST_PER_IMAGE.get(args.model, 0.12),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    meta_path = output_path.with_suffix(".meta.json")
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Metadata: {meta_path}")


def main():
    args = parse_args()
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = Path(__file__).parent.parent / output_path

    aspect_v3 = ASPECT_MAP.get(args.aspect, args.aspect)  # normalize to V3 format

    payload = {
        "prompt": args.prompt,
        "aspect_ratio": aspect_v3,
        "rendering_speed": "DEFAULT" if args.model == "quality" else "TURBO",
        "style_type": "REALISTIC",
    }
    if args.negative:
        payload["negative_prompt"] = args.negative
    if args.seed is not None:
        payload["seed"] = args.seed

    print(f"Ideogram generate_artwork")
    print(f"  Prompt  : {args.prompt[:80]}{'...' if len(args.prompt) > 80 else ''}")
    print(f"  Aspect  : {args.aspect}")
    print(f"  Model   : {args.model}  (cost ~${COST_PER_IMAGE.get(args.model, 0.12):.2f})")
    print(f"  Output  : {output_path}")

    if args.dry_run:
        print("\n[DRY RUN] Would send:")
        print(json.dumps(payload, indent=2))
        print("\n[DRY RUN] No API call made.")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        # Write a placeholder PNG (1x1 black pixel)
        placeholder = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
            b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        output_path.write_bytes(placeholder)
        print(f"  Placeholder written: {output_path}")
        return

    api_key = get_api_key()
    print("\nCalling Ideogram API ...")
    response = call_ideogram(api_key, payload)

    images = response.get("data", [])
    if not images:
        print(f"ERROR: No images in response: {response}", file=sys.stderr)
        sys.exit(1)

    url = images[0].get("url", "")
    if not url:
        print(f"ERROR: No URL in response: {images[0]}", file=sys.stderr)
        sys.exit(1)

    print(f"  URL: {url[:80]}...")
    print(f"  Downloading ...")
    download_image(url, output_path)
    size_kb = output_path.stat().st_size // 1024
    print(f"  Saved: {output_path}  ({size_kb} KB)")

    write_metadata(output_path, args, response)
    print("\nDone.")


if __name__ == "__main__":
    main()
