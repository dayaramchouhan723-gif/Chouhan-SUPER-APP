"""Small, explicit local profile memory; chat transcripts are not stored."""

from __future__ import annotations

from myra.config import _read_config, save_config

ALLOWED_FIELDS = {"name", "language"}


def get_profile() -> dict[str, str]:
    stored = _read_config().get("profile", {})
    if not isinstance(stored, dict):
        return {}
    return {
        str(key): str(value)
        for key, value in stored.items()
        if key in ALLOWED_FIELDS and isinstance(value, str)
    }


def remember(field: str, value: str) -> str:
    field = field.strip().lower()
    value = value.strip()
    if field not in ALLOWED_FIELDS:
        return "I can remember only your name or preferred language."
    if not value:
        return "Please provide a value to remember."
    data = _read_config()
    profile = data.get("profile", {})
    if not isinstance(profile, dict):
        profile = {}
    profile[field] = value[:100]
    data["profile"] = profile
    save_config(data)
    return f"Saved your preferred {field}: {profile[field]}."


def forget() -> str:
    data = _read_config()
    data.pop("profile", None)
    save_config(data)
    return "Cleared the saved name and language preference. Your API key was not changed."


def profile_prompt() -> str:
    profile = get_profile()
    if not profile:
        return ""
    details = ", ".join(f"{key}: {value}" for key, value in sorted(profile.items()))
    return f"User-provided preferences (use only when relevant): {details}."
