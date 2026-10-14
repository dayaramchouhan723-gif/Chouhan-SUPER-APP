"""Helpers for responding in a user-requested language."""

from __future__ import annotations

import re


def requested_language(text: str) -> str | None:
    """Recognize plain requests such as 'speak in Spanish' or 'reply in Urdu'."""
    match = re.search(
        r"\b(?:speak|reply|respond|answer|talk)\s+(?:to me\s+)?in\s+"
        r"([A-Za-z][A-Za-z -]{1,35}?)(?:[.!?,]|$)",
        text,
        re.IGNORECASE,
    )
    if not match:
        return None
    return " ".join(match.group(1).strip().split())
