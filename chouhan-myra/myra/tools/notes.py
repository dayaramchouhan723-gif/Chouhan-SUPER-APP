"""Command-line wrappers for the local notes store."""

from __future__ import annotations

from myra.automation.files import delete_note, list_notes, read_note, save_note


def run_notes(command: str) -> str:
    parts = command.strip().split(maxsplit=2)
    if not parts:
        return "Use /note add TITLE: TEXT, /note list, /note read TITLE, or /note delete TITLE."

    action = parts[0].lower()
    if action == "list":
        notes = list_notes()
        return "No saved notes." if not notes else "Saved notes:\n" + "\n".join(
            f"- {note}" for note in notes
        )
    if action == "add":
        note_text = " ".join(parts[1:])
        if ":" not in note_text:
            return "Use /note add TITLE: TEXT."
        title, body = note_text.split(":", maxsplit=1)
        if not title.strip():
            return "Use a non-empty note title."
        return save_note(title, body)
    if action in {"read", "delete"}:
        if len(parts) < 2:
            return f"Use /note {action} TITLE."
        title = " ".join(parts[1:])
        return read_note(title) if action == "read" else delete_note(title)
    return "Use /note add TITLE: TEXT, /note list, /note read TITLE, or /note delete TITLE."
