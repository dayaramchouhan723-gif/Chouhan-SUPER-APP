from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from myra.automation import files
from myra.automation.system import system_status
from myra.ai.languages import requested_language
from myra.tools.notes import run_notes


class NotesTests(unittest.TestCase):
    def test_note_round_trip_and_rejects_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(files, "NOTES_DIR", Path(directory)):
                self.assertEqual(files.save_note("shopping", "tea and rice"), "Saved note: shopping")
                self.assertEqual(files.list_notes(), ["shopping"])
                self.assertEqual(files.read_note("shopping"), "tea and rice")
                with self.assertRaises(FileNotFoundError):
                    files.read_note("../../outside")
                self.assertEqual(files.delete_note("shopping"), "Deleted note: shopping")
                self.assertEqual(files.list_notes(), [])

    def test_note_command_keeps_text_after_title(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(files, "NOTES_DIR", Path(directory)):
                self.assertEqual(
                    run_notes("add shopping: tea, rice"),
                    "Saved note: shopping",
                )
                self.assertEqual(run_notes("read shopping"), "tea, rice")


class LanguageTests(unittest.TestCase):
    def test_explicit_language_request(self) -> None:
        self.assertEqual(requested_language("Please reply in Spanish."), "Spanish")
        self.assertIsNone(requested_language("Tell me about the moon."))


class SystemStatusTests(unittest.TestCase):
    def test_status_is_read_only_text(self) -> None:
        status = system_status()
        self.assertIn("Operating system:", status)
        self.assertIn("Python:", status)


if __name__ == "__main__":
    unittest.main()
