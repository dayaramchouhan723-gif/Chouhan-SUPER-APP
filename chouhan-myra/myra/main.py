"""Command-line entry point and explicit local command router."""

from __future__ import annotations

import argparse
import sys

from myra.ai.gemini import get_gemini_response
from myra.ai.memory import forget, get_profile, remember
from myra.automation.apps import open_app
from myra.automation.system import system_status
from myra.config import get_api_key
from myra.tools.notes import run_notes
from myra.tools.qr import make_qr
from myra.tools.spotify import search_spotify
from myra.automation.whatsapp import open_whatsapp

HELP_TEXT = """Commands:
  /help                         Show this list
  /note add TITLE: TEXT          Save a local note
  /note list                     List notes
  /note read TITLE               Read a note
  /note delete TITLE             Delete one note
  /status                        Show read-only system information
  /open-app NAME                 Open calculator, files, or browser
  /spotify QUERY                 Open Spotify search in your browser
  /qr TEXT                       Create a QR image (optional [qr] extra)
  /screen                        Capture one screenshot and extract its text
  /camera                        Capture one frame and ask Gemini about it
  /whatsapp [DRAFT]              Open WhatsApp Web; you send messages yourself
  /remember name|language VALUE  Save one local preference
  /memory                        Show saved name/language preferences
  /forget                        Clear saved profile preferences
  /voice                         Listen to one voice request
  /exit                          Quit

Regular messages are sent to Gemini. Tools run only when you enter their
explicit slash command; Gemini replies cannot trigger local actions."""


def handle_message(text: str) -> tuple[str, bool]:
    """Run an explicit local command or ask Gemini; bool says whether to speak."""
    message = text.strip()
    if not message:
        return "Please enter a message.", False

    command, _, argument = message.partition(" ")
    command = command.lower()
    argument = argument.strip()

    if command == "/help":
        return HELP_TEXT, False
    if command == "/status":
        return system_status(), False
    if command == "/note":
        try:
            return run_notes(argument), False
        except (OSError, ValueError) as exc:
            return str(exc), False
    if command == "/open-app":
        return open_app(argument), False
    if command == "/spotify":
        return search_spotify(argument), False
    if command == "/whatsapp":
        return open_whatsapp(argument), False
    if command == "/qr":
        try:
            return f"QR image saved to {make_qr(argument)}", False
        except (OSError, ValueError, RuntimeError) as exc:
            return str(exc), False
    if command == "/remember":
        field, separator, value = argument.partition(" ")
        if not separator:
            return "Use /remember name VALUE or /remember language VALUE.", False
        return remember(field, value), False
    if command == "/memory":
        profile = get_profile()
        if not profile:
            return "No saved profile preferences.", False
        return "Saved preferences:\n" + "\n".join(
            f"- {key}: {value}" for key, value in sorted(profile.items())
        ), False
    if command == "/forget":
        return forget(), False
    if command == "/screen":
        return _read_screen(), False
    if command == "/camera":
        return _ask_about_camera(), False
    if command == "/voice":
        return _handle_voice()
    if command.startswith("/"):
        return f"Unknown command: {command}. Type /help.", False

    try:
        return get_gemini_response(message), True
    except (RuntimeError, ValueError, OSError) as exc:
        return f"Assistant error: {exc}", False


def _read_screen() -> str:
    from myra.vision.ocr import extract_text
    from myra.vision.screen import capture_screen

    image_path = None
    try:
        image_path = capture_screen()
        return extract_text(image_path)
    except (RuntimeError, OSError) as exc:
        return str(exc)
    finally:
        if image_path is not None:
            image_path.unlink(missing_ok=True)


def _ask_about_camera() -> str:
    from myra.vision.camera import capture_camera_frame

    image_path = None
    try:
        image_path = capture_camera_frame()
        return get_gemini_response("Describe the image briefly and objectively.", image_path=image_path)
    except (RuntimeError, ValueError, OSError) as exc:
        return f"Camera request failed: {exc}"
    finally:
        if image_path is not None:
            image_path.unlink(missing_ok=True)


def _handle_voice() -> tuple[str, bool]:
    from myra.voice.stt import listen_once

    try:
        heard = listen_once()
    except RuntimeError as exc:
        return str(exc), False
    print(f"You said: {heard}")
    response, should_speak = handle_message(heard)
    return response, should_speak


def run_cli() -> None:
    print("CHOUHAN MYRA — independent Python assistant")
    print("Type /help for commands. Type /exit to quit.")
    while True:
        try:
            text = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            return
        if text.lower() in {"/exit", "/quit"}:
            print("Goodbye.")
            return
        response, should_speak = handle_message(text)
        print(f"\nChouhan Myra: {response}")
        if text.lower() == "/voice" and should_speak:
            try:
                from myra.voice.tts import speak

                speak(response)
            except RuntimeError:
                # Typed chat remains usable when optional speech output is absent.
                pass


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="chouhan-myra",
        description="An independent, local-first Python assistant.",
    )
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--orb", action="store_true", help="Open the optional Tkinter chat window.")
    modes.add_argument("--wake", action="store_true", help="Explicitly enable wake-phrase listening.")
    args = parser.parse_args()

    if args.orb:
        try:
            get_api_key(prompt=True)
            from myra.voice.orb import run_orb

            run_orb()
        except (RuntimeError, ImportError) as exc:
            print(f"Could not start the orb: {exc}", file=sys.stderr)
            raise SystemExit(1) from exc
        return

    if args.wake:
        from myra.voice.wake_word import listen_wake_word

        def on_command(text: str) -> None:
            print(f"\nYou: {text}")
            response, _ = handle_message(text)
            print(f"Chouhan Myra: {response}")
            try:
                from myra.voice.tts import speak

                speak(response)
            except RuntimeError as exc:
                print(f"Speech output is unavailable: {exc}")

        try:
            listen_wake_word(on_command)
        except KeyboardInterrupt:
            print("\nWake mode stopped.")
        return

    run_cli()


if __name__ == "__main__":
    main()
