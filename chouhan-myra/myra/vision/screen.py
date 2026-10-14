"""Capture one screen image after an explicit user request."""

from __future__ import annotations

from pathlib import Path
from tempfile import gettempdir


def capture_screen() -> Path:
    try:
        import mss
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError(
            'Screen capture is optional. Install it with: python -m pip install -e ".[vision]"'
        ) from exc

    output = Path(gettempdir()) / "chouhan-myra-screen.png"
    try:
        with mss.mss() as capture:
            monitor = capture.monitors[1]
            shot = capture.grab(monitor)
            Image.frombytes("RGB", shot.size, shot.rgb).save(output)
    except Exception as exc:
        raise RuntimeError(f"Could not capture the screen: {exc}") from exc
    return output
