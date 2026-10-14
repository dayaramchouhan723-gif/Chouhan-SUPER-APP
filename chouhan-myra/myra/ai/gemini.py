"""Minimal Gemini REST client using Python's standard library."""

from __future__ import annotations

import base64
import json
import mimetypes
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from myra.ai.languages import requested_language
from myra.ai.memory import profile_prompt
from myra.config import get_api_key

DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
MAX_IMAGE_BYTES = 12 * 1024 * 1024


def get_gemini_response(
    text: str,
    api_key: str | None = None,
    *,
    image_path: str | Path | None = None,
    model: str = DEFAULT_MODEL,
    timeout: float = 45,
) -> str:
    """Send one user request to Gemini and return its text response."""
    if not text.strip():
        raise ValueError("The prompt cannot be empty.")

    key = api_key or get_api_key(prompt=True)
    language = requested_language(text)
    system_parts = [
        "You are Chouhan Myra, an independent personal assistant. Be helpful, "
        "clear, and honest about uncertainty. Never claim to have performed an "
        "action unless the local app confirmed it."
    ]
    if language:
        system_parts.append(f"Reply in {language}.")
    user_profile = profile_prompt()
    if user_profile:
        system_parts.append(user_profile)

    parts: list[dict[str, object]] = [{"text": text}]
    if image_path is not None:
        path = Path(image_path)
        image_bytes = path.read_bytes()
        if len(image_bytes) > MAX_IMAGE_BYTES:
            raise ValueError("The image is too large. Use an image under 12 MB.")
        mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        parts.append(
            {
                "inlineData": {
                    "mimeType": mime_type,
                    "data": base64.b64encode(image_bytes).decode("ascii"),
                }
            }
        )

    payload = {
        "systemInstruction": {"parts": [{"text": " ".join(system_parts)}]},
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {"temperature": 0.6, "maxOutputTokens": 2048},
    }
    url = f"{API_BASE}/{model}:generateContent?{urlencode({'key': key})}"
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        # Do not echo the request URL because it contains the API key.
        detail = exc.read().decode("utf-8", errors="replace")
        try:
            message = json.loads(detail).get("error", {}).get("message", "Request failed")
        except json.JSONDecodeError:
            message = "Request failed"
        raise RuntimeError(f"Gemini returned HTTP {exc.code}: {message}") from exc
    except URLError as exc:
        raise RuntimeError(f"Could not reach Gemini: {exc.reason}") from exc
    except (TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Gemini response could not be read: {exc}") from exc

    candidates = result.get("candidates", [])
    if not candidates:
        feedback = result.get("promptFeedback", {}).get("blockReason")
        suffix = f" (blocked: {feedback})" if feedback else ""
        raise RuntimeError(f"Gemini returned no answer{suffix}.")
    response_parts = candidates[0].get("content", {}).get("parts", [])
    answer = "\n".join(
        str(part["text"]) for part in response_parts if isinstance(part, dict) and "text" in part
    ).strip()
    if not answer:
        raise RuntimeError("Gemini returned an empty text response.")
    return answer
