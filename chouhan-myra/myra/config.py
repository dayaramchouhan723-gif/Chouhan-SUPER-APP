"""Local configuration and API-key storage."""

from __future__ import annotations

import getpass
import json
import os
import sys
from pathlib import Path
from typing import Any

CONFIG_PATH = Path.home() / ".chouhan_myra.json"


def _read_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {}
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Could not read local config at {CONFIG_PATH}: {exc}") from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"Local config at {CONFIG_PATH} must contain a JSON object.")
    return data


def save_config(data: dict[str, Any]) -> None:
    """Write private local settings without exposing their contents."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary = CONFIG_PATH.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    try:
        os.chmod(temporary, 0o600)
    except OSError:
        pass
    temporary.replace(CONFIG_PATH)
    try:
        os.chmod(CONFIG_PATH, 0o600)
    except OSError:
        pass


def get_api_key(*, prompt: bool = True) -> str:
    """Return the saved key or ask for one without echoing it."""
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if key:
        return key

    key = str(_read_config().get("api_key", "")).strip()
    if key:
        return key

    if not prompt:
        raise RuntimeError(
            "No Gemini API key is configured. Set GEMINI_API_KEY or run the assistant "
            "interactively to save one locally."
        )
    if not sys.stdin.isatty():
        raise RuntimeError(
            "No Gemini API key is configured and this session cannot prompt for one. "
            "Set GEMINI_API_KEY in your local environment."
        )

    key = getpass.getpass("Gemini API key (input hidden): ").strip()
    if not key:
        raise RuntimeError("An empty API key was not saved.")
    data = _read_config()
    data["api_key"] = key
    save_config(data)
    return key
