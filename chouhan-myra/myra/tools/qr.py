"""Optional QR-code image creation."""

from __future__ import annotations

from pathlib import Path

from myra.config import CONFIG_PATH


def make_qr(data: str) -> Path:
    try:
        import qrcode
    except ImportError as exc:
        raise RuntimeError(
            'QR creation is optional. Install it with: python -m pip install -e ".[qr]"'
        ) from exc
    if not data.strip():
        raise ValueError("Add text or a URL after /qr.")
    output_dir = CONFIG_PATH.parent / ".chouhan_myra" / "qr"
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "latest.png"
    qrcode.make(data.strip()).save(output)
    return output
