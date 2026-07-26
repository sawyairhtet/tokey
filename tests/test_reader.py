"""Tests for cc_token_tracker.reader.

Uses real temp files (tempfile), not mocks of open. read_transcript full
re-reads an already-resolved transcript path each tick; WHICH path is resolved
upstream by sessions.discover_sessions (see tests/test_sessions.py).
"""

import os
import tempfile
import unittest

from cc_token_tracker.parser import TranscriptRecord
from cc_token_tracker.reader import read_transcript

# A genuine typed prompt (no message id) and an assistant line carrying a
# message id, so tests can name which records came back.
PROMPT = '{"type":"user","message":{"role":"user","content":"hi"}}'


def assistant_line(message_id, text):
    return (
        '{"type":"assistant","message":{"id":"' + message_id + '",'
        '"role":"assistant","content":[{"type":"text","text":"' + text + '"}],'
        '"stop_reason":"end_turn","usage":{"input_tokens":1,"output_tokens":1,'
        '"cache_creation_input_tokens":0,"cache_read_input_tokens":0}}}'
    )


class ReadTranscript(unittest.TestCase):
    """read_transcript parses an already-resolved transcript path. The path is
    resolved upstream by discovery; these tests pin the read/parse and no-op
    behavior by handing a path in directly.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = self.tmp.name
        self.transcript = os.path.join(self.base, "transcript.jsonl")

    def write(self, path, text):
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)

    def assert_noop(self, result):
        self.assertEqual(result.records, [])
        self.assertIsNone(result.transcript_path)

    def test_none_path_is_noop(self):
        # nothing resolved this tick (discovery found no transcript)
        self.assert_noop(read_transcript(None))

    def test_missing_transcript_is_noop(self):
        # a resolved path that does not exist on disk
        self.assert_noop(read_transcript(self.transcript))  # never created

    def test_happy_path_multiple_turns(self):
        lines = [
            PROMPT,
            assistant_line("m1", "first"),
            PROMPT,
            assistant_line("m2", "second"),
        ]
        self.write(self.transcript, "\n".join(lines) + "\n")

        result = read_transcript(self.transcript)

        self.assertEqual(result.transcript_path, self.transcript)
        self.assertEqual(len(result.records), 4)
        self.assertTrue(all(isinstance(r, TranscriptRecord) for r in result.records))
        self.assertEqual([r.message_id for r in result.records],
                         [None, "m1", None, "m2"])

    def test_final_line_without_trailing_newline_is_kept(self):
        # well-formed final line with NO trailing newline must still be returned
        content = PROMPT + "\n" + assistant_line("m1", "done")
        self.write(self.transcript, content)

        result = read_transcript(self.transcript)

        self.assertEqual(len(result.records), 2)
        self.assertEqual(result.records[-1].message_id, "m1")

    def test_truncated_final_line_dropped_rest_kept(self):
        # load-bearing: final line truncated mid-JSON is dropped, prior records
        # kept, and the read does not raise
        good = PROMPT + "\n" + assistant_line("m1", "ok") + "\n"
        truncated = '{"type":"assi'
        self.write(self.transcript, good + truncated)

        result = read_transcript(self.transcript)

        self.assertEqual(len(result.records), 2)
        self.assertEqual([r.message_id for r in result.records], [None, "m1"])
        self.assertEqual(result.transcript_path, self.transcript)

    def test_line_with_raw_u2028_is_one_record(self):
        # pin: a single valid JSONL line whose content carries a raw U+2028
        # (legal unescaped in a JSON string per RFC 8259, emitted raw by V8's
        # JSON.stringify) must stay one line. split("\n") keeps it intact;
        # splitlines() would break it into two fragments that both fail to parse
        # and the real assistant message would vanish with no error.
        line = assistant_line("u2028msg", "before\u2028after")
        self.write(self.transcript, line + "\n")

        result = read_transcript(self.transcript)

        self.assertEqual(len(result.records), 1)
        self.assertEqual(result.records[0].message_id, "u2028msg")

    def test_distinct_reads_do_not_mix(self):
        # each read_transcript call is a fresh full re-read with no cross-file
        # state: reading A then B returns only the file actually read. This is
        # what makes a session switch rebase to the new transcript alone.
        file_a = os.path.join(self.base, "a.jsonl")
        file_b = os.path.join(self.base, "b.jsonl")
        self.write(file_a, PROMPT + "\n" + assistant_line("msgA", "A") + "\n")
        self.write(file_b, PROMPT + "\n" + assistant_line("msgB", "B") + "\n")

        first = read_transcript(file_a)
        self.assertEqual(first.transcript_path, file_a)
        ids_first = [r.message_id for r in first.records]
        self.assertIn("msgA", ids_first)
        self.assertNotIn("msgB", ids_first)

        second = read_transcript(file_b)
        self.assertEqual(second.transcript_path, file_b)
        ids_second = [r.message_id for r in second.records]
        self.assertIn("msgB", ids_second)
        self.assertNotIn("msgA", ids_second)


if __name__ == "__main__":
    unittest.main()
