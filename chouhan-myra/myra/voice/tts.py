"""Optional text-to-speech output."""

from __future__ import annotations


def speak(text: str) -> None:
    try:
        import pyttsx3
    except ImportError as exc:
        raise RuntimeError(
            'Speech output is optional. Install it with: python -m pip install -e ".[voice]"'
        ) from exc

    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception as exc:
        raise RuntimeError(f"Speech output failed: {exc}") from exc
