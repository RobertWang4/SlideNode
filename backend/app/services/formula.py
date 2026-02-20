"""Formula detection service using pix2tex (LaTeX-OCR)."""

import io
import logging

from PIL import Image

logger = logging.getLogger(__name__)

# Lazy singleton for the LatexOCR model
_latex_ocr = None


def _get_latex_ocr():
    global _latex_ocr
    if _latex_ocr is None:
        try:
            from pix2tex.cli import LatexOCR

            _latex_ocr = LatexOCR()
            logger.info("pix2tex LatexOCR model loaded")
        except Exception:  # noqa: BLE001
            logger.warning("pix2tex not available; formula detection disabled")
            return None
    return _latex_ocr


def _is_formula_candidate(img: Image.Image) -> bool:
    """Heuristic check: formula images tend to be wide & short with mostly white background."""
    w, h = img.size

    # Skip images that are too large (photos/diagrams) or too small (icons)
    if w > 2000 or h > 2000:
        return False
    if w < 20 or h < 20:
        return False

    # Formulas are typically wider than tall (aspect ratio > 1.5)
    # but also allow square-ish images for stacked equations
    aspect = w / max(h, 1)
    if aspect < 0.3:
        return False

    # Check if image is mostly white/light (formula on white background)
    try:
        grayscale = img.convert("L")
        pixels = list(grayscale.getdata())
        if not pixels:
            return False
        light_count = sum(1 for p in pixels if p > 200)
        light_ratio = light_count / len(pixels)
        # Formulas typically have >60% white/light pixels
        if light_ratio < 0.5:
            return False
    except Exception:  # noqa: BLE001
        pass

    return True


def detect_formula(image_bytes: bytes) -> str | None:
    """Attempt to detect and OCR a LaTeX formula from image bytes.

    Returns LaTeX string if formula detected, None otherwise.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
    except Exception:  # noqa: BLE001
        return None

    if not _is_formula_candidate(img):
        return None

    ocr = _get_latex_ocr()
    if ocr is None:
        return None

    try:
        # pix2tex expects RGB images
        if img.mode != "RGB":
            img = img.convert("RGB")

        latex = ocr(img)

        if not latex or len(latex.strip()) < 2:
            return None

        # Basic sanity check: LaTeX formulas typically contain math-like characters
        math_indicators = set(r"\^_{}+=()-*/")
        has_math = any(c in latex for c in math_indicators)
        if not has_math and len(latex) < 10:
            return None

        return latex.strip()
    except Exception:  # noqa: BLE001
        logger.debug("pix2tex failed on image", exc_info=True)
        return None
