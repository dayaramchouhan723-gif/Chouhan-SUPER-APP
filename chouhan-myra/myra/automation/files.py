"""Safe local notes storage, kept inside the user's application data folder."""

from __future__ import annotations

import re
from pathlib import Path

NOTES_DIR = Path.home() / ".chouhan_myra" / "notes"


def _note_path(title: str) -> Path:
    normalized = re.sub(r"[^A-Za-z0-9._ -]", "", title).strip().strip(".")
    if not normalized or normalized in {".", ".."}:
        raise ValueError("Use a note title containing letters or numbers.")
    return NOTES_DIR / f"{normalized[:80]}.txt"


def save_note(title: str, body: str) -> str:
    path = _note_path(title)
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(body.strip() + "\n", encoding="utf-8")
    return f"Saved note: {path.stem}"


def list_notes() -> list[str]:
    if not NOTES_DIR.exists():
        return []
    return sorted(path.stem for path in NOTES_DIR.glob("*.txt") if path.is_file())


def read_note(title: str) -> str:
    path = _note_path(title)
    if not path.is_file():
        raise FileNotFoundError(f"No note named '{path.stem}' was found.")
    return path.read_text(encoding="utf-8").strip()


def delete_note(title: str) -> str:
    path = _note_path(title)
    if not path.is_file():
        raise FileNotFoundError(f"No note named '{path.stem}' was found.")
    path.unlink()
    return f"Deleted note: {path.stem}"
