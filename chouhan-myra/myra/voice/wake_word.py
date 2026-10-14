"""Explicitly enabled wake-phrase loop; not started in normal chat mode."""

from __future__ import annotations

from collections.abc import Callable

from myra.voice.stt import listen_once

WAKE_PHRASES = ("hey chouhan", "hey myra")


def listen_wake_word(on_command: Callable[[str], None], language: str = "en-US") -> None:
    """Listen until interrupted, and pass each command after the wake phrase."""
    print("Wake mode is active. Say 'Hey Chouhan' or 'Hey Myra', then your request.")
    print("Microphone listening continues until Ctrl+C.")
    while True:
        try:
            heard = listen_once(language=language, timeout=8, phrase_time_limit=6)
        except RuntimeError as exc:
            if "timeout" not in str(exc).lower():
                print(f"Voice input: {exc}")
            continue
        normalized = heard.lower().strip()
        for phrase in WAKE_PHRASES:
            if normalized.startswith(phrase):
                command = heard[len(phrase) :].strip(" ,.!?")
                if not command:
                    try:
                        command = listen_once(language=language)
                    except RuntimeError as exc:
                        print(f"Voice input: {exc}")
                        break
                if command:
                    on_command(command)
                break
