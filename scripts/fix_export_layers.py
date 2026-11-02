"""Post-process an Affinity PDF export for a manufacturer (.ai delivery).

Affinity marks hidden layers only as "View OFF" (/AS auto-state), so a printer
printing straight from the PDF may still output them. This script:
- sets the hidden layers OFF in the default config (view, print and export),
- sets TrimBox and BleedBox equal to MediaBox (as in Tina's original .ai),
- writes <name>_final.pdf plus a byte-identical copy <name>_final.ai.
The input file stays untouched.

Default hidden layers are those of Tina's print files: 外框 (contours) and 图层 1 (3D unfold).

Usage:
    py -3 scripts/fix_export_layers.py <export.pdf> [--hidden 外框 "图层 1"]
"""
import argparse
import io
import pathlib
import shutil
import sys

import pikepdf

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", type=pathlib.Path)
    ap.add_argument("--hidden", nargs="+", default=["外框", "图层 1"])
    args = ap.parse_args()

    hidden_names = set(args.hidden)
    dst = args.pdf.with_name(args.pdf.stem + "_final.pdf")

    with pikepdf.open(args.pdf) as pdf:
        oc = pdf.Root.OCProperties
        names = [str(g.Name) for g in oc.OCGs]
        hidden = [g for g in oc.OCGs if str(g.Name) in hidden_names]
        if len(hidden) != len(hidden_names):
            sys.exit(f"hidden layers not found; layers in file: {names}")

        D = oc.D
        D.OFF = pikepdf.Array(hidden)
        D.ON = pikepdf.Array([g for g in oc.OCGs if str(g.Name) not in hidden_names])
        for g in hidden:
            g.Usage = pikepdf.Dictionary(
                View=pikepdf.Dictionary(ViewState=pikepdf.Name.OFF),
                Print=pikepdf.Dictionary(PrintState=pikepdf.Name.OFF),
                Export=pikepdf.Dictionary(ExportState=pikepdf.Name.OFF),
            )
        if "/AS" in D:
            del D["/AS"]

        for page in pdf.pages:
            mb = page.obj.MediaBox
            page.obj.TrimBox = pikepdf.Array(list(mb))
            page.obj.BleedBox = pikepdf.Array(list(mb))
        pdf.save(dst)

    shutil.copyfile(dst, dst.with_suffix(".ai"))
    print("layers:", names)
    print("hidden OFF:", sorted(hidden_names))
    print("written", dst, "and", dst.with_suffix(".ai"))


if __name__ == "__main__":
    main()
