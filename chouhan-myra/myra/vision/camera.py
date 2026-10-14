"""Capture a single camera frame only after an explicit command."""

from __future__ import annotations

from pathlib import Path
from tempfile import gettempdir


def capture_camera_frame(camera_index: int = 0) -> Path:
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError(
            'Camera support is optional. Install it with: python -m pip install -e ".[vision]"'
        ) from exc

    camera = cv2.VideoCapture(camera_index)
    try:
        if not camera.isOpened():
            raise RuntimeError("Could not open camera. Check device permissions and camera index.")
        ok, frame = camera.read()
        if not ok:
            raise RuntimeError("The camera did not return an image.")
        path = Path(gettempdir()) / "chouhan-myra-camera.jpg"
        if not cv2.imwrite(str(path), frame):
            raise RuntimeError("Could not save the camera image.")
    finally:
        camera.release()
    return path
