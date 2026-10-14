from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from myra.ai.gemini import get_gemini_response


class FakeResponse:
    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(
            {"candidates": [{"content": {"parts": [{"text": "Hello from Gemini"}]}}]}
        ).encode("utf-8")


class GeminiClientTests(unittest.TestCase):
    @patch("myra.ai.gemini.urlopen", return_value=FakeResponse())
    def test_text_request_uses_rest_payload(self, mocked_urlopen: object) -> None:
        answer = get_gemini_response("Say hello", api_key="test-key")
        self.assertEqual(answer, "Hello from Gemini")

        request = mocked_urlopen.call_args.args[0]  # type: ignore[attr-defined]
        payload = json.loads(request.data)
        self.assertIn("systemInstruction", payload)
        self.assertEqual(
            payload["contents"][0]["parts"][0]["text"],
            "Say hello",
        )

    @patch("myra.ai.gemini.urlopen", return_value=FakeResponse())
    def test_chat_history_maps_assistant_role_to_gemini_model(
        self,
        mocked_urlopen: object,
    ) -> None:
        get_gemini_response(
            "Follow up",
            api_key="test-key",
            history=[
                {"role": "user", "content": "Remember this"},
                {"role": "assistant", "content": "I will"},
            ],
        )
        request = mocked_urlopen.call_args.args[0]  # type: ignore[attr-defined]
        payload = json.loads(request.data)
        self.assertEqual(
            [item["role"] for item in payload["contents"]],
            ["user", "model", "user"],
        )
        self.assertEqual(
            payload["contents"][1]["parts"][0]["text"],
            "I will",
        )


if __name__ == "__main__":
    unittest.main()
