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

Per-key design API (Phase 2):
    with TemplateDriver.for_template(pdf_path, coord_map_path) as drv:
        drv.recolor_key("1", "#121E13", mode="luminance_aware_shift")
        drv.set_legend("1", main={"text": "1", "color": (0.32, 0.69, 0.36), "font_path": "...", "size": 18})
        drv.export(output_path)
"""

import colorsys
import io
import json
import sys
from abc import ABC, abstractmethod
from pathlib import Path

# Reconfigure in-place (no new wrapper) — avoids GC closing buffer when imported
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
elif hasattr(sys.stdout, "buffer"):
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

    def key_by_id(self, key_id: str) -> dict | None:
        for k in self.get_coordinate_map()["keys"]:
            if k["id"] == key_id:
                return k
        return None

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
        # Font cache: font_path → fitz.Font instance. Reusing the same object
        # ensures PyMuPDF embeds the font only once instead of once per key.
        self._font_cache: dict = {}

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

    def _gather_key_paths(self, key_id: str) -> list:
        """Return fill paths whose center falls inside the single key with given id."""
        key = self.key_by_id(key_id)
        if key is None:
            return []
        page = self._doc[0]
        kb = (key["x0"], key["y0"], key["x1"], key["y1"])
        return [
            p for p in page.get_drawings()
            if p.get("fill") and len(p["fill"]) >= 3 and p.get("rect") is not None
            and self._rect_center_in_bbox(p["rect"], kb)
        ]

    def _gather_key_stroke_paths(self, key_id: str) -> list:
        """Return stroke-only paths inside a single key bbox."""
        key = self.key_by_id(key_id)
        if key is None:
            return []
        page = self._doc[0]
        kb = (key["x0"], key["y0"], key["x1"], key["y1"])
        return [
            p for p in page.get_drawings()
            if p.get("color") and len(p["color"]) >= 3
            and not (p.get("fill") and len(p.get("fill", [])) >= 3)
            and p.get("rect") is not None
            and self._rect_center_in_bbox(p["rect"], kb)
        ]

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

    def recolor_key(self, key_id: str, color_hex: str, mode: str = "solid") -> int:
        """Recolor fills of a single key. Returns count of paths overdrawn."""
        key_paths = self._gather_key_paths(key_id)
        if not key_paths:
            return 0
        target_rgb = hex_to_rgb(color_hex)
        if mode == "hue_shift":
            color_map = self._build_hue_shift_map(key_paths, target_rgb)
        elif mode == "luminance_aware_shift":
            color_map = self._build_luminance_aware_map(key_paths, target_rgb)
        else:
            color_map = {id(p): target_rgb for p in key_paths}
        return self._overdraw_paths(key_paths, color_map)

    def set_legend(self, key_id: str, main: dict | None = None, sub: dict | None = None):
        """Overlay legend text on a key using fitz.TextWriter.

        main / sub dicts: {"text": str, "color": (r,g,b), "font_path": str, "size": float}
        Positions text at key center (cx, cy) from coord map.
        """
        if not main and not sub:
            return
        key = self.key_by_id(key_id)
        if key is None:
            return

        import fitz
        page = self._doc[0]
        cx, cy = key["cx"], key["cy"]

        def _draw_text(spec: dict, y_offset: float):
            text = spec.get("text", "")
            if not text:
                return
            font_path = spec.get("font_path", "")
            size = spec.get("size", 18)
            color = spec.get("color", (1.0, 1.0, 1.0))

            # Reuse cached Font instance so PyMuPDF embeds the font only once.
            cache_key = font_path or "__helv__"
            if cache_key not in self._font_cache:
                self._font_cache[cache_key] = (
                    fitz.Font(fontfile=font_path) if font_path else fitz.Font("helv")
                )
            font = self._font_cache[cache_key]
            text_w = font.text_length(text, fontsize=size)
            x = cx - text_w / 2
            y = cy + y_offset + size * 0.35
            writer = fitz.TextWriter(page.rect)
            writer.append(fitz.Point(x, y), text, font=font, fontsize=size)
            writer.write_text(page, color=color)

        if main and sub:
            _draw_text(main, y_offset=-sub["size"] * 0.5)
            _draw_text(sub,  y_offset=main["size"] * 0.5)
        elif main:
            _draw_text(main, y_offset=0.0)
        elif sub:
            _draw_text(sub,  y_offset=0.0)

    @staticmethod
    def _median_body_fill(paths: list, lum_min: float = 0.3, lum_max: float = 0.85) -> tuple:
        """Return median-luminance fill, excluding dark shadow/bevel (L<0.3) and
        specular highlights (L>0.85) that corrupt the reference hue.
        Falls back to unfiltered median if filtering leaves nothing.
        """
        fills = [tuple(p["fill"][:3]) for p in paths]
        filtered = [f for f in fills
                    if lum_min <= colorsys.rgb_to_hls(*f)[1] <= lum_max]
        candidates = filtered if filtered else fills
        return sorted(candidates, key=lambda c: colorsys.rgb_to_hls(*c)[1])[len(candidates) // 2]

    def _build_luminance_aware_map(self, paths: list, target_rgb: tuple) -> dict:
        """Shift hue, sat and lum together with proportional squeeze to avoid clipping.

        Reference = median-luminance body fill (L 0.3–0.85) so dark detail marks
        (L≈0.1) in alt_* keys do not corrupt the reference and cause the body fill
        to remain nearly unchanged.
        """
        fills = [tuple(p["fill"][:3]) for p in paths]
        if not fills:
            return {}
        lums = [colorsys.rgb_to_hls(*f)[1] for f in fills]
        ref_rgb = self._median_body_fill(paths)
        rh, rl, rs = colorsys.rgb_to_hls(*ref_rgb)
        th, tl, ts = colorsys.rgb_to_hls(*target_rgb)
        h_delta = ((th - rh) + 0.5) % 1.0 - 0.5
        s_delta = ts - rs
        l_delta = tl - rl

        shifted = [l + l_delta for l in lums]
        _MIN_L = 0.03

        if any(l < 0.0 or l > 1.0 for l in shifted):
            lum_min, lum_max = min(lums), max(lums)
            dev_low  = rl - lum_min
            dev_high = lum_max - rl
            head_low  = tl - _MIN_L
            head_high = 1.0 - tl
            scale_low  = (head_low  / dev_low)  if dev_low  > 1e-6 else 1.0
            scale_high = (head_high / dev_high) if dev_high > 1e-6 else 1.0
            scale = min(scale_low, scale_high, 1.0)

            def shifted_lum(orig_l: float) -> float:
                return max(_MIN_L, min(1.0, tl + (orig_l - rl) * scale))
        else:
            def shifted_lum(orig_l: float) -> float:
                return max(_MIN_L, min(1.0, orig_l + l_delta))

        def transform(src: tuple) -> tuple:
            sh, sl, ss = colorsys.rgb_to_hls(*src[:3])
            return colorsys.hls_to_rgb(
                (sh + h_delta) % 1.0,
                shifted_lum(sl),
                max(0.0, min(1.0, ss + s_delta)),
            )

        return {id(p): transform(tuple(p["fill"][:3])) for p in paths}

    def _build_hue_shift_map(self, paths: list, target_rgb: tuple) -> dict:
        """Shift hue+sat of each path's fill by the delta between reference and target.

        Reference = median-luminance body fill (L 0.3–0.85).
        Luminance per path is preserved → 3D shading depth intact.
        """
        ref_rgb = self._median_body_fill(paths)
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
        if stroke_paths:
            self._re_emit_strokes(stroke_paths)
        return count

    def recolor_key(self, key_id: str, color_hex: str, mode: str = "solid") -> int:
        stroke_paths = self._gather_key_stroke_paths(key_id)
        count = super().recolor_key(key_id, color_hex, mode)
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
