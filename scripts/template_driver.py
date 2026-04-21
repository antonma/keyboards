"""template_driver.py — Abstract driver interface for keycap PDF templates

Drivers:
  PdfDriver     — base for all PDF templates (RGB + CMYK, PyMuPDF overdraw)
  PdfCmykDriver — GK75 Tigry (CMYK; hue_shift falls back to solid, no 3D shading)
  PdfRgbDriver  — Cherry 135 全五面 (RGB; hue_shift preserves 3D shading)
  PsdDriver     — stub for future PSD 5-View support

Usage:
    from scripts.template_driver import TemplateDriver

    with TemplateDriver.for_template(pdf_path, coord_map_path) as drv:
        drv.recolor("alpha", "#161820", mode="solid")
        drv.export(output_path)
"""

import colorsys
import io
import json
import sys
from abc import ABC, abstractmethod
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

COLOR_TOLERANCE = 30 / 255.0


# ── Colour helpers ────────────────────────────────────────────────────────────

def hex_to_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0, int(h[4:6], 16) / 255.0


def rgb_to_hex(r: float, g: float, b: float) -> str:
    return "#{:02X}{:02X}{:02X}".format(round(r * 255), round(g * 255), round(b * 255))


def color_near(c1: tuple, c2: tuple, tol: float = COLOR_TOLERANCE) -> bool:
    return all(abs(a - b) <= tol for a, b in zip(c1[:3], c2[:3]))


def hue_shift_color(src: tuple, ref: tuple, tgt: tuple) -> tuple:
    """Shift src by the H+S delta between ref and tgt; luminance unchanged."""
    def to_hls(r, g, b):
        return colorsys.rgb_to_hls(r, g, b)  # (h, l, s)

    rh, rl, rs = to_hls(*ref[:3])
    th, tl, ts = to_hls(*tgt[:3])
    sh, sl, ss = to_hls(*src[:3])

    new_h = (sh + (th - rh)) % 1.0
    new_s = max(0.0, min(1.0, ss + (ts - rs)))
    new_l = sl  # preserve luminance → 3D depth intact

    return colorsys.hls_to_rgb(new_h, new_l, new_s)


# ── Abstract base ─────────────────────────────────────────────────────────────

class TemplateDriver(ABC):
    def __init__(self, template_path: Path, coord_map_path: Path):
        self.template_path = Path(template_path)
        self.coord_map_path = Path(coord_map_path)
        self._coord_map = None

    @classmethod
    def for_template(cls, template_path: Path, coord_map_path: Path) -> "TemplateDriver":
        """Return the right driver by inspecting the template and coord map."""
        template_path = Path(template_path)
        coord_map_path = Path(coord_map_path)

        if template_path.suffix.lower() == ".psd":
            return PsdDriver(template_path, coord_map_path)

        # Detect color model from coord map
        color_model = "CMYK"
        if coord_map_path.exists():
            with open(coord_map_path, encoding="utf-8") as f:
                meta = json.load(f)
            color_model = meta.get("color_model", "CMYK").upper()

        if color_model == "RGB":
            return PdfRgbDriver(template_path, coord_map_path)
        return PdfCmykDriver(template_path, coord_map_path)

    def get_coordinate_map(self) -> dict:
        if self._coord_map is None:
            with open(self.coord_map_path, encoding="utf-8") as f:
                self._coord_map = json.load(f)
        return self._coord_map

    def keys_for_group(self, group: str) -> list:
        return [k for k in self.get_coordinate_map()["keys"] if k["group"] == group]

    def key_bboxes(self, group: str) -> list:
        return [(k["x0"], k["y0"], k["x1"], k["y1"]) for k in self.keys_for_group(group)]

    @abstractmethod
    def recolor(self, group: str, color_hex: str, mode: str = "solid") -> int:
        """Recolor all fills in group. Returns count of paths overdrawn."""
        ...

    @abstractmethod
    def export(self, output_path: Path):
        """Save result to output_path."""
        ...

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


# ── PDF base driver ───────────────────────────────────────────────────────────

class PdfDriver(TemplateDriver):
    """Shared PDF driver logic: PyMuPDF overdraw for both CMYK and RGB templates."""

    def __init__(self, template_path: Path, coord_map_path: Path):
        super().__init__(template_path, coord_map_path)
        try:
            import fitz
        except ImportError:
            print("ERROR: PyMuPDF not installed. Run: py -3 -m pip install pymupdf", file=sys.stderr)
            raise
        self._doc = fitz.open(str(template_path))

    def close(self):
        if hasattr(self, "_doc") and self._doc:
            self._doc.close()
            self._doc = None

    def _rect_center_in_bbox(self, path_rect, key_bbox, margin: float = 2.0) -> bool:
        cx = (path_rect.x0 + path_rect.x1) / 2
        cy = (path_rect.y0 + path_rect.y1) / 2
        x0, y0, x1, y1 = key_bbox
        return (x0 - margin) <= cx <= (x1 + margin) and (y0 - margin) <= cy <= (y1 + margin)

    def _gather_group_paths(self, group: str) -> list:
        """Return all fill paths whose center falls inside any key in group."""
        page = self._doc[0]
        bboxes = self.key_bboxes(group)
        return [
            p for p in page.get_drawings()
            if p.get("fill") and len(p["fill"]) >= 3 and p.get("rect") is not None
            and any(self._rect_center_in_bbox(p["rect"], kb) for kb in bboxes)
        ]

    def _gather_group_stroke_paths(self, group: str) -> list:
        """Return all stroke-only paths within group key bboxes (no fill)."""
        page = self._doc[0]
        bboxes = self.key_bboxes(group)
        return [
            p for p in page.get_drawings()
            if p.get("color") and len(p["color"]) >= 3
            and not (p.get("fill") and len(p.get("fill", [])) >= 3)
            and p.get("rect") is not None
            and any(self._rect_center_in_bbox(p["rect"], kb) for kb in bboxes)
        ]

    def _overdraw_paths(self, paths: list, color_map: dict) -> int:
        import fitz
        page = self._doc[0]
        shape = page.new_shape()
        count = 0
        for path in paths:
            color = color_map.get(id(path))
            if color is None:
                continue
            for item in path.get("items", []):
                if item[0] == "l":    shape.draw_line(item[1], item[2])
                elif item[0] == "c":  shape.draw_bezier(item[1], item[2], item[3], item[4])
                elif item[0] == "re": shape.draw_rect(item[1])
                elif item[0] == "qu": shape.draw_quad(item[1])
            shape.finish(fill=color, color=None, even_odd=path.get("even_odd", True))
            count += 1
        shape.commit()
        return count

    def _re_emit_strokes(self, stroke_paths: list):
        """Re-draw stroke paths on top to restore Z-order after fill overdraw."""
        page = self._doc[0]
        shape = page.new_shape()
        for path in stroke_paths:
            sc = path.get("color")
            if not sc or len(sc) < 3:
                continue
            for item in path.get("items", []):
                if item[0] == "l":    shape.draw_line(item[1], item[2])
                elif item[0] == "c":  shape.draw_bezier(item[1], item[2], item[3], item[4])
                elif item[0] == "re": shape.draw_rect(item[1])
                elif item[0] == "qu": shape.draw_quad(item[1])
            shape.finish(
                fill=None,
                color=sc[:3],
                width=path.get("width", 0.5),
                even_odd=False,
            )
        shape.commit()

    def recolor(self, group: str, color_hex: str, mode: str = "solid") -> int:
        group_paths = self._gather_group_paths(group)
        if not group_paths:
            print(f"  WARN: No fill paths found for group '{group}'")
            return 0

        target_rgb = hex_to_rgb(color_hex)

        if mode == "hue_shift":
            color_map = self._build_hue_shift_map(group_paths, target_rgb)
        else:
            color_map = {id(p): target_rgb for p in group_paths}

        return self._overdraw_paths(group_paths, color_map)

    def _build_hue_shift_map(self, paths: list, target_rgb: tuple) -> dict:
        """Shift hue+sat of each path's fill by the delta between reference and target.

        Reference = median-luminance fill across the group → best proxy for base keycap colour.
        Luminance per path is preserved → 3D shading depth intact.
        """
        fills = [tuple(p["fill"][:3]) for p in paths]
        fills_by_lum = sorted(fills, key=lambda c: colorsys.rgb_to_hls(*c)[1])
        ref_rgb = fills_by_lum[len(fills_by_lum) // 2]

        return {
            id(p): hue_shift_color(tuple(p["fill"][:3]), ref_rgb, target_rgb)
            for p in paths
        }

    def export(self, output_path: Path):
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self._doc.save(str(output_path), garbage=4, deflate=True)


# ── Concrete drivers ──────────────────────────────────────────────────────────

class PdfRgbDriver(PdfDriver):
    """Driver for Cherry 135 全五面 — pure RGB, full hue_shift support."""

    def recolor(self, group: str, color_hex: str, mode: str = "solid") -> int:
        # Gather stroke paths BEFORE overdraw — get_drawings() re-parses the
        # content stream, and freshly committed shapes can trip MuPDF's parser.
        stroke_paths = self._gather_group_stroke_paths(group)

        count = super().recolor(group, color_hex, mode)

        # Re-emit strokes on top: Cherry profile 3D shading comes from stroke
        # lines drawn after fills in the original stream; overdraw buries them.
        if stroke_paths:
            self._re_emit_strokes(stroke_paths)
        return count


class PdfCmykDriver(PdfDriver):
    """Driver for GK75 Tigry — CMYK.

    hue_shift is technically possible but rarely useful: GK75 has only 6 fill
    colours (no 3D shading per key), so solid overdraw is always preferred.
    """
    pass


class PsdDriver(TemplateDriver):
    """Stub: PSD 5-View template support. See Handoff topic=psd-5view-integration."""

    def recolor(self, group: str, color_hex: str, mode: str = "solid") -> int:
        raise NotImplementedError(
            "PsdDriver not yet implemented — resolve Handoff topic=psd-5view-integration first"
        )

    def export(self, output_path: Path):
        raise NotImplementedError("PsdDriver not yet implemented")
