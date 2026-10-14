from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from myra.mobile_config import load_mobile_settings, save_mobile_settings


class MobileSettingsTests(unittest.TestCase):
    def test_missing_file_has_no_keys(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            settings = load_mobile_settings(Path(directory) / "settings.json")
        self.assertEqual(settings["provider"], "Groq")
        self.assertEqual(settings["groq_api_key"], "")
        self.assertEqual(settings["gemini_api_key"], "")

    def test_settings_round_trip_and_restrictive_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "private" / "settings.json"
            expected = {
                "provider": "Gemini",
                "groq_api_key": "groq-test-value",
                "gemini_api_key": "gemini-test-value",
            }
            save_mobile_settings(path, expected)
            self.assertEqual(load_mobile_settings(path), expected)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(path.parent.stat().st_mode & 0o777, 0o700)
            self.assertEqual(json.loads(path.read_text())["provider"], "Gemini")

    def test_invalid_provider_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                save_mobile_settings(
                    Path(directory) / "settings.json",
                    {
                        "provider": "Other",
                        "groq_api_key": "g",
                        "gemini_api_key": "m",
                    },
                )


if __name__ == "__main__":
    unittest.main()
