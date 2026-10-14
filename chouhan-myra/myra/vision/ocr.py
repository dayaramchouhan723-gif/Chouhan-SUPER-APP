"""Extract visible text from one user-requested screenshot."""

from __future__ import annotations

from pathlib import Path


def extract_text(image_path: str | Path) -> str:
    try:
        import pytesseract
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError(
            'OCR is optional. Install it with: python -m pip install -e ".[vision]"'
        ) from exc

    try:
        text = pytesseract.image_to_string(Image.open(image_path)).strip()
    except Exception as exc:
        raise RuntimeError(
            f"Could not extract screen text: {exc}. Check that the Tesseract OCR "
            "program is installed and available on PATH."
        ) from exc
    return text or "No readable text was found in that screenshot."
