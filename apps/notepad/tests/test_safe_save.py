"""Regression tests for conflict-aware native Notepad saves."""
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from goreecloud_notepad.storage import ExternalModificationError, Note


class SafeSaveTests(unittest.TestCase):
    def test_external_edit_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "note.txt"
            path.write_bytes(b"first\r\n")
            note = Note.open(path)
            note.text = "my changes"
            path.write_bytes(b"external\r\n")
            with self.assertRaises(ExternalModificationError):
                note.save()
            self.assertEqual(path.read_bytes(), b"external\r\n")
            self.assertTrue(note.dirty)
            self.assertEqual(note.saved_text, "first\r\n")

    def test_identical_content_different_inode_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "note.txt"
            other = Path(directory) / "replacement.txt"
            path.write_text("same")
            note = Note.open(path)
            prior_identity = note.file_identity
            other.write_text("same")
            os.replace(other, path)
            note.text = "my edit"
            self.assertNotEqual(prior_identity, (path.stat().st_dev, path.stat().st_ino))
            with self.assertRaises(ExternalModificationError):
                note.save()
            self.assertEqual(path.read_text(), "same")
            self.assertEqual(note.file_identity, prior_identity)

    def test_deleted_note_not_recreated(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "note.txt"
            path.write_text("before")
            note = Note.open(path)
            note.text = "after"
            path.unlink()
            with self.assertRaises(ExternalModificationError):
                note.save()
            self.assertFalse(path.exists())
            self.assertTrue(note.dirty)

    def test_invalid_external_utf8_does_not_get_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "note.txt"
            path.write_text("hello")
            note = Note.open(path)
            note.text = "edited"
            path.write_bytes(b"\xff")
            with self.assertRaises(ExternalModificationError):
                note.save()
            self.assertEqual(path.read_bytes(), b"\xff")

    def test_unchanged_file_saves_twice_and_refreshes_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "note.txt"
            path.write_bytes("flower 🌿\r\n".encode())
            path.chmod(0o640)
            note = Note.open(path)
            previous = note.file_identity
            note.text = "one\r\ntwo\n"
            self.assertEqual(note.save(), path)
            self.assertNotEqual(note.file_identity, previous)
            self.assertEqual(note.file_identity, (path.stat().st_dev, path.stat().st_ino))
            note.text = "three\r\nfour\n"
            note.save()
            self.assertEqual(path.read_bytes(), b"three\r\nfour\n")
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o640)
            self.assertFalse(note.dirty)

    def test_save_as_preserves_changed_original(self):
        with tempfile.TemporaryDirectory() as directory:
            old = Path(directory) / "original.md"
            new = Path(directory) / "my-copy.md"
            old.write_text("original")
            note = Note.open(old)
            note.text = "my work"
            old.write_text("external update")
            note.save(new)
            self.assertEqual(old.read_text(), "external update")
            self.assertEqual(new.read_text(), "my work")
            self.assertEqual(note.file_identity, (new.stat().st_dev, new.stat().st_ino))
            note.text = "followup"
            note.save()
            self.assertEqual(new.read_text(), "followup")

    def test_symbolic_link_destination_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "real.txt"
            shortcut = Path(directory) / "alias.txt"
            target.write_text("original")
            shortcut.symlink_to(target)
            note = Note.open(shortcut)
            note.text = "my changes"
            with self.assertRaises(OSError):
                note.save()
            self.assertTrue(shortcut.is_symlink())
            self.assertEqual(target.read_text(), "original")

    def test_broken_symbolic_link_destination_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            shortcut = Path(directory) / "dangling.txt"
            shortcut.symlink_to(Path(directory) / "nonexistent.txt")
            with self.assertRaises(OSError):
                Note(text="important").save(shortcut)
            self.assertTrue(shortcut.is_symlink())

    @unittest.skipUnless(hasattr(os, "mkfifo"), "POSIX FIFO required")
    def test_fifo_cannot_be_opened_as_note(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fifo"
            os.mkfifo(path)
            with self.assertRaises(OSError):
                Note.open(path)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "POSIX FIFO required")
    def test_fifo_cannot_be_save_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fifo"
            os.mkfifo(path)
            with self.assertRaises(OSError):
                Note(text="important").save(path)

    def test_external_change_during_staging_aborts_and_cleans_up(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "note.txt"
            path.write_text("original")
            note = Note.open(path)
            note.text = "important draft"
            original_fsync = os.fsync

            def write_external(fd):
                path.write_text("other program")
                return original_fsync(fd)

            with mock.patch("goreecloud_notepad.storage.os.fsync", side_effect=write_external):
                with self.assertRaises(ExternalModificationError):
                    note.save()
            self.assertEqual(path.read_text(), "other program")
            self.assertEqual([p.name for p in Path(directory).iterdir()], ["note.txt"])
            self.assertTrue(note.dirty)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "POSIX FIFO required")
    def test_fifo_swap_during_staging_cannot_hang(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "note.txt"
            path.write_text("original")
            note = Note.open(path)
            note.text = "my changes"
            original_fsync = os.fsync

            def swap_to_fifo(fd):
                path.unlink()
                os.mkfifo(path)
                return original_fsync(fd)

            with mock.patch("goreecloud_notepad.storage.os.fsync", side_effect=swap_to_fifo):
                with self.assertRaises(ExternalModificationError):
                    note.save()
            self.assertTrue(stat.S_ISFIFO(path.lstat().st_mode))
            self.assertEqual([p.name for p in Path(directory).iterdir()], ["note.txt"])

    def test_symlink_swap_during_staging_cannot_overwrite_target(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "note.txt"
            other = Path(directory) / "other.txt"
            path.write_text("original")
            other.write_text("external")
            note = Note.open(path)
            note.text = "my changes"
            original_fsync = os.fsync

            def swap_to_link(fd):
                path.unlink()
                path.symlink_to(other)
                return original_fsync(fd)

            with mock.patch("goreecloud_notepad.storage.os.fsync", side_effect=swap_to_link):
                with self.assertRaises(ExternalModificationError):
                    note.save()
            self.assertTrue(path.is_symlink())
            self.assertEqual(other.read_text(), "external")
            self.assertTrue(note.dirty)

    def test_open_preserves_utf8_and_newlines(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "note.md"
            original = "🌿 line\r\nline two\n"
            path.write_bytes(original.encode("utf-8"))
            note = Note.open(path)
            self.assertEqual(note.text, original)
            self.assertEqual(note.saved_text, original)
            self.assertEqual(note.file_identity, (path.stat().st_dev, path.stat().st_ino))


if __name__ == "__main__":
    unittest.main()
