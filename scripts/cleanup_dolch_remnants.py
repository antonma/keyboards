#!/usr/bin/env python3
"""
Remove Dolch-keyboard remnants from GK75-TheWell-v5.pdf → v6.pdf

The original Tigry template had two keyboards (Tigry top, Dolch bottom).
In v5, the Dolch keyboard was removed in Affinity Designer, but two orphaned
path groups remain in the content stream:
  - A thin horizontal line at Y≈249 (center-page stray stroke)
  - A curved shape at Y≈78-101 (bottom-left remnant)

These are isolated at Y < 400 while all legitimate content is at Y > 900.
The orphaned block is a single contiguous segment near the end of the stream,
immediately preceded by the last valid keycap path and followed by the
keyboard legend text blocks (BT...ET operations at Y > 1000).

Strategy: excise the exact byte range [cut_start, cut_end) from the content
stream, where:
  cut_start = byte after the last '\nf\n' before the first low-Y moveto
  cut_end   = byte of the 'q' that opens the first text block after the remnants
"""

import pikepdf
import re
import sys
from pathlib import Path

Y_THRESHOLD = 400  # anything below this Y in moveto is a remnant


def find_remnant_range(data: str) -> tuple[int, int]:
    """Return (cut_start, cut_end) byte offsets to excise from the stream."""
    # Find all moveto ops with Y < threshold
    pattern = re.compile(r'(-?[\d.]+)\s+(-?[\d.]+)\s+m\b')
    low_y_positions = [m.start() for m in pattern.finditer(data)
                       if float(m.group(2)) < Y_THRESHOLD]

    if not low_y_positions:
        return None, None

    first_low = low_y_positions[0]
    last_low = low_y_positions[-1]

    # cut_start: the color/width settings just before the first low-Y moveto
    # Walk back to the '\nf\n' that ends the last valid keycap path
    f_pos = data.rfind('\nf\n', 0, first_low)
    if f_pos == -1:
        raise ValueError("Could not find end of last valid path before remnants")
    cut_start = f_pos + 3  # keep '\nf\n', start cutting from char after

    # cut_end: the 'q' that opens the first text/graphics block after the remnants
    # After the last low-Y path there is 'S\nq\n' — we keep the 'q'
    match = re.search(r'S\n(?=q\n)', data[last_low:])
    if not match:
        raise ValueError("Could not find end of last remnant path (S\\nq\\n pattern)")
    cut_end = last_low + match.end()

    return cut_start, cut_end


def cleanup_pdf(input_path: str, output_path: str) -> dict:
    """Remove Dolch remnants from the PDF content stream."""
    pdf = pikepdf.open(input_path)
    page = pdf.pages[0]

    if '/Contents' not in page:
        raise ValueError("Page has no /Contents")

    contents = page['/Contents']
    streams = list(contents) if isinstance(contents, pikepdf.Array) else [contents]

    if len(streams) != 1:
        raise ValueError(f"Expected 1 content stream, got {len(streams)}")

    stream_obj = streams[0]
    raw = stream_obj.read_bytes()
    data = raw.decode('latin-1')

    cut_start, cut_end = find_remnant_range(data)
    if cut_start is None:
        print("No remnants found — nothing to remove.")
        pdf.close()
        return {"removed_bytes": 0}

    removed_bytes = cut_end - cut_start
    removed_section = data[cut_start:cut_end]

    # Verify the removed section contains only low-Y paths
    remaining_movetos = re.findall(r'(-?[\d.]+)\s+(-?[\d.]+)\s+m\b', removed_section)
    high_y_in_removed = [(x, y) for x, y in remaining_movetos if float(y) >= Y_THRESHOLD]
    if high_y_in_removed:
        raise ValueError(
            f"Safety check failed: found {len(high_y_in_removed)} high-Y movetos in "
            f"the section to be removed! First: {high_y_in_removed[0]}"
        )

    # Reconstruct stream
    clean_data = data[:cut_start] + data[cut_end:]
    stream_obj.write(clean_data.encode('latin-1'))

    pdf.save(output_path)
    pdf.close()

    return {
        "input": input_path,
        "output": output_path,
        "cut_start": cut_start,
        "cut_end": cut_end,
        "removed_bytes": removed_bytes,
        "removed_movetos": len(remaining_movetos),
        "safety_check": "passed",
    }


if __name__ == "__main__":
    repo_root = Path(__file__).parent.parent
    input_pdf = repo_root / "templates" / "GK75-TheWell-v5.pdf"
    output_pdf = repo_root / "templates" / "GK75-TheWell-v6.pdf"

    if len(sys.argv) == 3:
        input_pdf = Path(sys.argv[1])
        output_pdf = Path(sys.argv[2])

    if not input_pdf.exists():
        print(f"ERROR: Input file not found: {input_pdf}")
        sys.exit(1)

    print(f"Input:  {input_pdf}")
    print(f"Output: {output_pdf}")
    print()

    result = cleanup_pdf(str(input_pdf), str(output_pdf))

    print(f"Removed {result['removed_bytes']:,} bytes ({result['removed_movetos']} path moveto ops)")
    print(f"Safety check: {result['safety_check']}")
    print(f"Saved to: {result['output']}")
