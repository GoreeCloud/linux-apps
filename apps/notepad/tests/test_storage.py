import json
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from goreecloud_notepad.storage import ExternalModificationError, Note, Preferences


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

    def test_reject_nul_with_original_file_intact(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "binary-like.txt"
            original = b"draft before\x00important text after\n"
            path.write_bytes(original)
            with self.assertRaisesRegex(OSError, "NUL"):
                Note.open(path)
            self.assertEqual(path.read_bytes(), original)


    def test_rename_failure_preserves_existing_note_and_dirty_state(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "note.txt"
            path.write_text("original", encoding="utf-8")
            note = Note.open(path)
            original_identity = note.file_identity
            note.text = "edited but not persisted"
            with mock.patch("goreecloud_notepad.storage.os.replace",
                            side_effect=OSError("simulated rename failure")):
                with self.assertRaisesRegex(OSError, "simulated rename failure"):
                    note.save()
            self.assertEqual(path.read_text(encoding="utf-8"), "original")
            self.assertEqual(note.saved_text, "original")
            self.assertEqual(note.file_identity, original_identity)
            self.assertTrue(note.dirty)
            self.assertEqual(list(Path(temp).glob(".note.txt.*.tmp")), [])
            note.save()
            self.assertEqual(path.read_text(encoding="utf-8"), note.text)
            self.assertFalse(note.dirty)

    def test_external_file_change_prevents_overwriting_user_data(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "shared-note.txt"
            path.write_text("first version", encoding="utf-8")
            note = Note.open(path)
            note.text = "local unsaved edit"
            path.write_text("external edit", encoding="utf-8")
            with self.assertRaises(ExternalModificationError):
                note.save()
            self.assertEqual(path.read_text(encoding="utf-8"), "external edit")
            self.assertEqual(note.saved_text, "first version")
            self.assertTrue(note.dirty)

            # A replacement with identical bytes still breaks tracked identity.
            path.write_text("first version", encoding="utf-8")
            replacement = Path(temp) / "replacement.txt"
            replacement.write_text("first version", encoding="utf-8")
            os.replace(replacement, path)
            with self.assertRaises(ExternalModificationError):
                note.save()
            self.assertEqual(path.read_text(encoding="utf-8"), "first version")
            self.assertTrue(note.dirty)


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

    def test_invalid_xdg_config_home_uses_home_config(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp) / "home"
            home.mkdir()
            with mock.patch.object(Path, "home", return_value=home):
                for invalid in ("", "relative/settings"):
                    with self.subTest(xdg_config_home=invalid):
                        with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": invalid}):
                            prefs = Preferences()
                            self.assertEqual(prefs.path, home / ".config/goreecloud/notepad/settings.json")
                            prefs.set("font_size", 17)
                            self.assertEqual(Preferences().get("font_size"), 17)


    def test_failed_settings_write_does_not_change_live_preferences(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "config" / "settings.json"
            prefs = Preferences(path)
            prefs.set("font_size", 18)
            original_bytes = path.read_bytes()
            with mock.patch("goreecloud_notepad.storage.os.replace",
                            side_effect=OSError("simulated full filesystem")):
                with self.assertRaisesRegex(OSError, "simulated full filesystem"):
                    prefs.set("font_size", 24)
            self.assertEqual(prefs.get("font_size"), 18)
            self.assertEqual(Preferences(path).get("font_size"), 18)
            self.assertEqual(path.read_bytes(), original_bytes)
            self.assertEqual(list(path.parent.glob(".settings.json.*.tmp")), [])
            prefs.set("font_size", 24)
            self.assertEqual(Preferences(path).get("font_size"), 24)


if __name__ == "__main__":
    unittest.main()
