"""Tests for cc_token_tracker.shim (Ticket 6).

Real temp files (tempfile), not mocks of open. The shim parses the statusline
stdin JSON and atomically writes the top-level transcript_path to a pointer file
the reader polls.
"""

import json
import os
import tempfile
import unittest
from unittest import mock

from cc_token_tracker.shim import (
    extract_transcript_path,
    run_shim,
    write_pointer_atomic,
)


def stdin_blob(**fields):
    # Build a statusline stdin object the way Claude Code would: one small JSON
    # object with transcript_path as a top-level field.
    return json.dumps(fields)


class ExtractTranscriptPath(unittest.TestCase):
    def test_valid_blob_returns_path(self):
        text = stdin_blob(transcript_path="/x/y/t.jsonl", session_id="s")
        self.assertEqual(extract_transcript_path(text), "/x/y/t.jsonl")

    def test_empty_string_is_none(self):
        self.assertIsNone(extract_transcript_path(""))

    def test_invalid_json_is_none(self):
        self.assertIsNone(extract_transcript_path("{not json"))

    def test_missing_key_is_none(self):
        self.assertIsNone(extract_transcript_path(stdin_blob(session_id="s")))

    def test_null_value_is_none(self):
        self.assertIsNone(extract_transcript_path('{"transcript_path": null}'))

    def test_non_string_value_is_none(self):
        self.assertIsNone(extract_transcript_path('{"transcript_path": 123}'))


class WritePointerAtomic(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = self.tmp.name
        self.pointer = os.path.join(self.base, "pointer")

    def test_pointer_has_exact_path_and_no_leftover_temp(self):
        target = "/some/transcript/path.jsonl"
        ok = write_pointer_atomic(target, self.pointer)
        self.assertTrue(ok)
        with open(self.pointer, encoding="utf-8") as handle:
            self.assertEqual(handle.read(), target)
        # the pointer's directory holds only the pointer, no leftover temp file
        self.assertEqual(os.listdir(self.base), ["pointer"])

    def test_mkstemp_uses_pointer_directory(self):
        # load-bearing: the temp MUST be created in the pointer's own directory
        # so os.replace stays on one filesystem and cannot raise cross-device. A
        # temp placed in /tmp would make os.replace fail across mounts.
        real_mkstemp = tempfile.mkstemp
        seen = {}

        def spy(*args, **kwargs):
            seen["dir"] = kwargs.get("dir")
            return real_mkstemp(*args, **kwargs)

        with mock.patch("cc_token_tracker.shim.tempfile.mkstemp", side_effect=spy):
            ok = write_pointer_atomic("/p/q.jsonl", self.pointer)

        self.assertTrue(ok)
        self.assertEqual(seen["dir"], os.path.dirname(self.pointer))

    def test_unwritable_directory_returns_false(self):
        # pointer inside a directory that does not exist: write fails cleanly
        bad_pointer = os.path.join(self.base, "nope", "pointer")
        ok = write_pointer_atomic("/p/q.jsonl", bad_pointer)
        self.assertFalse(ok)
        self.assertFalse(os.path.exists(bad_pointer))
        # and nothing leaked into the existing base directory
        self.assertEqual(os.listdir(self.base), [])


class RunShim(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = self.tmp.name
        self.pointer = os.path.join(self.base, "pointer")

    def test_valid_stdin_writes_pointer_and_returns_status(self):
        text = stdin_blob(
            transcript_path="/t/path.jsonl",
            model={"display_name": "Opus"},
            cwd="/home/u/project",
        )
        status = run_shim(text, self.pointer)
        self.assertIsInstance(status, str)
        self.assertTrue(status)  # non-empty
        with open(self.pointer, encoding="utf-8") as handle:
            self.assertEqual(handle.read(), "/t/path.jsonl")

    def test_garbage_stdin_does_not_create_pointer(self):
        # empty and invalid-JSON stdin (plus null / missing key) must leave the
        # pointer untouched while still returning a non-empty status.
        for text in ("", "{not json", "null", stdin_blob(session_id="s")):
            with self.subTest(text=text):
                if os.path.exists(self.pointer):
                    os.unlink(self.pointer)
                status = run_shim(text, self.pointer)
                self.assertIsInstance(status, str)
                self.assertTrue(status)
                self.assertFalse(os.path.exists(self.pointer))


if __name__ == "__main__":
    unittest.main()
