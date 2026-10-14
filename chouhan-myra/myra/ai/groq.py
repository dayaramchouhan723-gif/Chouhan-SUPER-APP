"""Small Groq chat-completions client built on Python's standard library."""

from __future__ import annotations

import json
import math
import os
import ssl
from collections.abc import Mapping, Sequence
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b")


def _ssl_context() -> ssl.SSLContext:
    try:
        import certifi
    except ImportError:
        return ssl.create_default_context()
    return ssl.create_default_context(cafile=certifi.where())


def get_groq_response(
    text: str,
    api_key: str,
    *,
    history: Sequence[Mapping[str, str]] = (),
    model: str = DEFAULT_GROQ_MODEL,
    timeout: float = 45,
) -> str:
    """Request one response from Groq without logging or echoing its API key."""
    if not text.strip():
        raise ValueError("The prompt cannot be empty.")
    key = api_key.strip()
    if not key:
        raise ValueError("A Groq API key is required.")

    messages: list[dict[str, str]] = [
        {
            "role": "system",
            "content": (
                "You are Chouhan Myra, an independent personal assistant. "
                "Be helpful, clear, and honest about uncertainty."
            ),
        }
    ]
    for item in history[-20:]:
        role = str(item.get("role", "")).strip().lower()
        content = str(item.get("content", "")).strip()
        if content and role in {"user", "assistant"}:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": text.strip()})

    payload = {"model": model, "messages": messages, "temperature": 0.6}
    request = Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=timeout, context=_ssl_context()) as response:
            result = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        # Keep the message independent of request headers and credentials.
        raise RuntimeError(f"Groq returned HTTP {exc.code}.") from None
    except URLError as exc:
        raise RuntimeError(f"Could not reach Groq: {exc.reason}") from None
    except (TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Groq response could not be read: {exc}") from None

    if not isinstance(result, dict):
        raise RuntimeError("Groq returned an invalid response.")
    choices = result.get("choices", [])
    if not isinstance(choices, list) or not choices:
        raise RuntimeError("Groq returned no answer.")
    choice = choices[0]
    if not isinstance(choice, dict):
        raise RuntimeError("Groq returned an invalid response.")
    message = choice.get("message", {})
    if not isinstance(message, dict):
        raise RuntimeError("Groq returned an invalid response.")
    answer = str(message.get("content", "")).strip()
    if not answer:
        raise RuntimeError("Groq returned an empty response.")
    return answer
