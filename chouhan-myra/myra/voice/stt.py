"""Optional, one-shot speech-to-text input."""

from __future__ import annotations


def listen_once(language: str = "en-US", timeout: int = 6, phrase_time_limit: int = 15) -> str:
    try:
        import speech_recognition as sr
    except ImportError as exc:
        raise RuntimeError(
            'Voice input is optional. Install it with: python -m pip install -e ".[voice]"'
        ) from exc

    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening once. Speak after the tone...")
            recognizer.adjust_for_ambient_noise(source, duration=0.4)
            audio = recognizer.listen(
                source, timeout=timeout, phrase_time_limit=phrase_time_limit
            )
        return recognizer.recognize_google(audio, language=language)
    except sr.WaitTimeoutError as exc:
        raise RuntimeError("No speech was detected before the listening timeout.") from exc
    except sr.UnknownValueError as exc:
        raise RuntimeError("I could not understand that recording.") from exc
    except sr.RequestError as exc:
        raise RuntimeError(f"Speech recognition service failed: {exc}") from exc
    except OSError as exc:
        raise RuntimeError(f"Could not open the microphone: {exc}") from exc
