from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from myra.ai.groq import get_groq_response
from myra.ai.providers import get_assistant_response


class FakeResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


class GroqClientTests(unittest.TestCase):
    @patch("myra.ai.groq.urlopen", return_value=FakeResponse({
        "choices": [{"message": {"content": "Hello from Groq"}}]
    }))
    def test_chat_completion_uses_bearer_key_and_history(self, mocked_urlopen: object) -> None:
        answer = get_groq_response(
            "How are you?",
            "test-key",
            history=[{"role": "user", "content": "Hello"}],
        )
        self.assertEqual(answer, "Hello from Groq")
        request = mocked_urlopen.call_args.args[0]  # type: ignore[attr-defined]
        self.assertEqual(request.get_header("Authorization"), "Bearer test-key")
        payload = json.loads(request.data)
        self.assertEqual(payload["model"], "openai/gpt-oss-20b")
        self.assertEqual(payload["messages"][-2]["content"], "Hello")
        self.assertEqual(payload["messages"][-1]["content"], "How are you?")

    def test_empty_groq_key_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Groq API key"):
            get_groq_response("Hello", "")


class ProviderRoutingTests(unittest.TestCase):
    @patch("myra.ai.providers.get_gemini_response", return_value="Gemini answer")
    @patch("myra.ai.providers.get_groq_response", side_effect=RuntimeError("offline"))
    def test_groq_failure_falls_back_to_gemini(
        self,
        _groq: object,
        gemini: object,
    ) -> None:
        answer = get_assistant_response(
            "Hello",
            provider="Groq",
            groq_api_key="groq-key",
            gemini_api_key="gemini-key",
        )
        self.assertEqual(answer, ("Gemini answer", "Gemini fallback", True))
        gemini.assert_called_once()  # type: ignore[attr-defined]

    @patch("myra.ai.providers.get_gemini_response")
    @patch("myra.ai.providers.get_groq_response", return_value="Groq answer")
    def test_groq_success_does_not_call_fallback(
        self,
        _groq: object,
        gemini: object,
    ) -> None:
        answer = get_assistant_response(
            "Hello",
            provider="Groq",
            groq_api_key="groq-key",
            gemini_api_key="gemini-key",
        )
        self.assertEqual(answer, ("Groq answer", "Groq", False))
        gemini.assert_not_called()  # type: ignore[attr-defined]

    @patch("myra.ai.providers.get_gemini_response", return_value="Gemini answer")
    @patch("myra.ai.providers.get_groq_response")
    def test_explicit_gemini_selection_skips_groq(
        self,
        groq: object,
        _gemini: object,
    ) -> None:
        answer = get_assistant_response(
            "Hello",
            provider="Gemini",
            groq_api_key="groq-key",
            gemini_api_key="gemini-key",
        )
        self.assertEqual(answer, ("Gemini answer", "Gemini", False))
        groq.assert_not_called()  # type: ignore[attr-defined]

    @patch("myra.ai.providers.get_gemini_response", side_effect=RuntimeError("offline"))
    @patch("myra.ai.providers.get_groq_response", side_effect=RuntimeError("offline"))
    def test_double_failure_does_not_return_provider_details(
        self,
        _groq: object,
        _gemini: object,
    ) -> None:
        with self.assertRaisesRegex(RuntimeError, "fallback also failed") as raised:
            get_assistant_response(
                "Hello",
                provider="Groq",
                groq_api_key="private-groq",
                gemini_api_key="private-gemini",
            )
        self.assertNotIn("private-groq", str(raised.exception))
        self.assertNotIn("private-gemini", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
