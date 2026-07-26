"""Tests for cc_token_tracker.markers: the session open/close marker store.

The marker store is the roster's liveness source of truth. These tests pin the
atomic write, the keyed read, the open->closed tombstone overwrite, never-raise
tolerance of garbage, dir self-creation, and the TTL cleanup that keeps the
store bounded. A temp markers dir is injected so nothing touches the real store.
"""

import json
import os
import tempfile
import unittest

from cc_token_tracker.markers import (
    CLOSED,
    MARKER_STALE_AFTER_SECONDS,
    MARKER_TTL_SECONDS,
    OPEN,
    MarkerInfo,
    read_markers,
    write_marker,
)
from cc_token_tracker.sessions import DEFAULT_WINDOW_DAYS

NOW = 1_780_000_000.0


class WriteAndRead(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = os.path.join(self.tmp.name, "sessions")  # not pre-created

    def test_write_self_creates_dir_and_read_keys_by_transcript(self):
        ok = write_marker("sid-1", "/p/a.jsonl", "/p", OPEN,
                          markers_dir=self.dir, now=NOW)
        self.assertTrue(ok)
        self.assertTrue(os.path.isdir(self.dir))  # dir made on demand

        markers = read_markers(self.dir, now=NOW)
        self.assertEqual(set(markers), {"/p/a.jsonl"})
        marker = markers["/p/a.jsonl"]
        self.assertIsInstance(marker, MarkerInfo)
        self.assertEqual(marker.event, OPEN)
        self.assertEqual(marker.session_id, "sid-1")
        self.assertEqual(marker.ts, NOW)

    def test_session_end_overwrites_same_file_as_tombstone(self):
        write_marker("sid-1", "/p/a.jsonl", "/p", OPEN,
                     markers_dir=self.dir, now=NOW)
        write_marker("sid-1", "/p/a.jsonl", "/p", CLOSED,
                     markers_dir=self.dir, now=NOW + 5)

        # One file per session id: the close overwrote the open.
        files = [n for n in os.listdir(self.dir) if n.endswith(".json")]
        self.assertEqual(files, ["sid-1.json"])
        markers = read_markers(self.dir, now=NOW + 5)
        self.assertEqual(markers["/p/a.jsonl"].event, CLOSED)

    def test_missing_dir_reads_empty(self):
        self.assertEqual(read_markers(self.dir, now=NOW), {})

    def test_garbage_files_are_skipped(self):
        os.makedirs(self.dir, exist_ok=True)
        with open(os.path.join(self.dir, "bad.json"), "w") as fh:
            fh.write("{ not json")
        with open(os.path.join(self.dir, "wrong.json"), "w") as fh:
            json.dump({"event": "Nope", "transcript_path": "/x", "ts": NOW}, fh)
        with open(os.path.join(self.dir, "ignore.txt"), "w") as fh:
            fh.write("not a marker")
        write_marker("sid-good", "/p/g.jsonl", "/p", OPEN,
                     markers_dir=self.dir, now=NOW)

        markers = read_markers(self.dir, now=NOW)
        self.assertEqual(set(markers), {"/p/g.jsonl"})

    def test_newest_ts_wins_for_same_transcript(self):
        write_marker("sid-old", "/p/a.jsonl", "/p", CLOSED,
                     markers_dir=self.dir, now=NOW)
        write_marker("sid-new", "/p/a.jsonl", "/p", OPEN,
                     markers_dir=self.dir, now=NOW + 100)
        markers = read_markers(self.dir, now=NOW + 100)
        self.assertEqual(markers["/p/a.jsonl"].event, OPEN)
        self.assertEqual(markers["/p/a.jsonl"].session_id, "sid-new")

    def test_old_closed_tombstone_is_pruned(self):
        eight_days = 8 * 86400.0
        write_marker("sid-1", "/p/a.jsonl", "/p", CLOSED,
                     markers_dir=self.dir, now=NOW - eight_days)
        markers = read_markers(self.dir, now=NOW)
        self.assertEqual(markers, {})
        # The stale tombstone file was unlinked, not just hidden.
        self.assertEqual(
            [n for n in os.listdir(self.dir) if n.endswith(".json")], []
        )

    def test_recent_closed_tombstone_is_kept(self):
        write_marker("sid-1", "/p/a.jsonl", "/p", CLOSED,
                     markers_dir=self.dir, now=NOW - 60)
        markers = read_markers(self.dir, now=NOW)
        self.assertEqual(markers["/p/a.jsonl"].event, CLOSED)

    def test_old_open_marker_is_pruned_too(self):
        # A session killed hard leaves an OPEN marker with no tombstone behind
        # it. Liveness already treats it as dropped after two hours, but the
        # FILE also has to go or the store grows without bound for the life of
        # the install: once past the TTL it is unlinked like any other marker.
        write_marker("sid-crashed", "/p/a.jsonl", "/p", OPEN,
                     markers_dir=self.dir, now=NOW - 8 * 86400.0)
        self.assertEqual(read_markers(self.dir, now=NOW), {})
        self.assertEqual(
            [n for n in os.listdir(self.dir) if n.endswith(".json")], []
        )

    def test_open_marker_inside_the_ttl_is_kept(self):
        # The boundary the pruning must not cross: a long-lived but in-window
        # open session keeps its marker and stays matchable by the roster.
        write_marker("sid-1", "/p/a.jsonl", "/p", OPEN,
                     markers_dir=self.dir, now=NOW - 6 * 86400.0)
        self.assertEqual(read_markers(self.dir, now=NOW)["/p/a.jsonl"].event, OPEN)

    def test_session_id_with_separators_is_sanitized(self):
        ok = write_marker("../../evil", "/p/a.jsonl", "/p", OPEN,
                          markers_dir=self.dir, now=NOW)
        self.assertTrue(ok)
        # The file landed inside the markers dir, not via the traversal.
        names = os.listdir(self.dir)
        self.assertEqual(names, ["evil.json"])


class TtlMatchesDiscoveryWindow(unittest.TestCase):
    """The marker TTL and the roster's discovery window are the same 7 days,
    stated in two modules (markers cannot import sessions without a cycle).
    This pins the coupling so the two cannot silently drift apart."""

    def test_ttl_equals_the_discovery_window(self):
        self.assertEqual(MARKER_TTL_SECONDS, DEFAULT_WINDOW_DAYS * 86400.0)

    def test_ttl_is_far_longer_than_the_crash_bound(self):
        # The crash bound decides the LABEL (dropped) in hours; the TTL decides
        # when the file is deleted, days later. Inverting them would delete
        # markers the roster still classifies from.
        self.assertGreater(MARKER_TTL_SECONDS, MARKER_STALE_AFTER_SECONDS)


if __name__ == "__main__":
    unittest.main()
