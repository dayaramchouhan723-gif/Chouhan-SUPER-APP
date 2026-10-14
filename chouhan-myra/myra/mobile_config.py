"""Private, app-local settings for the Android Kivy client."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

DEFAULT_MOBILE_SETTINGS: dict[str, str] = {
    "provider": "Groq",
    "groq_api_key": "",
    "gemini_api_key": "",
}
VALID_PROVIDERS = {"Groq", "Gemini"}


def load_mobile_settings(path: str | Path) -> dict[str, str]:
    """Read settings from Android's private app data directory."""
    settings_path = Path(path)
    if not settings_path.exists():
        return dict(DEFAULT_MOBILE_SETTINGS)
    try:
        data: Any = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("Could not read the saved Android app settings.") from exc
    if not isinstance(data, dict):
        raise RuntimeError("The saved Android app settings are invalid.")

    provider = data.get("provider", "Groq")
    if not isinstance(provider, str) or provider not in VALID_PROVIDERS:
        provider = "Groq"
    return {
        "provider": provider,
        "groq_api_key": str(data.get("groq_api_key", "")),
        "gemini_api_key": str(data.get("gemini_api_key", "")),
    }


def save_mobile_settings(path: str | Path, settings: dict[str, str]) -> None:
    """Atomically save API keys with restrictive file permissions."""
    provider = settings.get("provider", "Groq")
    if provider not in VALID_PROVIDERS:
        raise ValueError("Choose Groq or Gemini.")
    data = {
        "provider": provider,
        "groq_api_key": settings.get("groq_api_key", "").strip(),
        "gemini_api_key": settings.get("gemini_api_key", "").strip(),
    }

    settings_path = Path(path)
    settings_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        os.chmod(settings_path.parent, 0o700)
    except OSError:
        pass
    temporary = settings_path.with_name(settings_path.name + ".tmp")
    try:
        temporary.write_text(
            json.dumps(data, indent=2) + "\n",
            encoding="utf-8",
        )
        try:
            os.chmod(temporary, 0o600)
        except OSError:
            pass
        temporary.replace(settings_path)
        try:
            os.chmod(settings_path, 0o600)
        except OSError:
            pass
    except OSError as exc:
        temporary.unlink(missing_ok=True)
        raise RuntimeError("Could not save settings in the app's private storage.") from exc
