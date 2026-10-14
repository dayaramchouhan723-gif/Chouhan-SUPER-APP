"""Provider selection and Groq-to-Gemini fallback for the mobile chat."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from myra.ai.gemini import get_gemini_response
from myra.ai.groq import get_groq_response


def get_assistant_response(
    text: str,
    *,
    provider: str,
    groq_api_key: str,
    gemini_api_key: str,
    history: Sequence[Mapping[str, str]] = (),
) -> tuple[str, str, bool]:
    """Return (answer, provider used, fell back to Gemini)."""
    selected = provider.strip().lower()
    if selected not in {"groq", "gemini"}:
        raise ValueError("Choose Groq or Gemini.")
    if not text.strip():
        raise ValueError("The prompt cannot be empty.")

    if selected == "gemini":
        if not gemini_api_key.strip():
            raise RuntimeError("The Gemini API key is missing.")
        try:
            return (
                get_gemini_response(
                    text,
                    api_key=gemini_api_key,
                    history=history,
                ),
                "Gemini",
                False,
            )
        except Exception:
            raise RuntimeError(
                "Gemini request failed. Check its saved key and your internet connection."
            ) from None

    try:
        return (
            get_groq_response(
                text,
                api_key=groq_api_key,
                history=history,
            ),
            "Groq",
            False,
        )
    except Exception:
        if not gemini_api_key.strip():
            raise RuntimeError(
                "Groq failed and the Gemini fallback key is missing."
            ) from None
        try:
            answer = get_gemini_response(
                text,
                api_key=gemini_api_key,
                history=history,
            )
            return answer, "Gemini fallback", True
        except Exception:
            raise RuntimeError(
                "Groq failed and the Gemini fallback also failed. "
                "Check both saved keys and your internet connection."
            ) from None
