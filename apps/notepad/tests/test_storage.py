import json
import os
import stat
import tempfile
import unittest
from pathlib import Path

from goreecloud_notepad.storage import Note, Preferences


class NoteTests(unittest.TestCase):
    def test_write_read_unicode_and_line_endings(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "a note.txt"
            note = Note(text="Hello 🌿\r\nHello GoreeCloud\n")
            self.assertTrue(note.dirty)
            note.save(path)
            self.assertFalse(note.dirty)
            self.assertEqual(path.read_bytes(), b"Hello \xf0\x9f\x8c\xbf\r\nHello GoreeCloud\n")
            opened = Note.open(path)
            self.assertEqual(opened.text, note.text)
            opened.text += "New line\n"
            self.assertTrue(opened.dirty)
            opened.text = note.text
            self.assertFalse(opened.dirty)

    def test_refuse_missing_destination(self):
        with self.assertRaises(ValueError):
            Note(text="hello").save()

    def test_existing_mode_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "note.txt"
            path.write_text("original")
            path.chmod(0o640)
            Note(text="updated").save(path)
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o640)

    def test_invalid_utf8_not_silently_replaced(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "broken.txt"
            path.write_bytes(b"\xff")
            with self.assertRaises(UnicodeError):
                Note.open(path)


class PreferencesTests(unittest.TestCase):
    def test_defaults_and_persistence(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "config" / "settings.json"
            prefs = Preferences(path)
            self.assertEqual(prefs.get("appearance"), "light")
            self.assertTrue(prefs.get("word_wrap"))
            prefs.set("appearance", "dark")
            prefs.set("word_wrap", False)
            prefs.set("font_size", 19)
            reloaded = Preferences(path)
            self.assertEqual(reloaded.get("appearance"), "dark")
            self.assertFalse(reloaded.get("word_wrap"))
            self.assertEqual(reloaded.get("font_size"), 19)
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

    def test_corrupt_values_fall_back_safely(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "settings.json"
            path.write_text(json.dumps({
                "appearance": "rainbow",
                "word_wrap": "no",
                "font_size": 900,
                "monospace": 1
            }))
            prefs = Preferences(path)
            self.assertEqual(prefs.get("appearance"), "light")
            self.assertTrue(prefs.get("word_wrap"))
            self.assertEqual(prefs.get("font_size"), 15)
            self.assertFalse(prefs.get("monospace"))


if __name__ == "__main__":
    unittest.main()
