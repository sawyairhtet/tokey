"""Tests for cc_token_tracker.roster (the v0.6 all-expanded roster view).

Snapshot-style layout tests render to plain text through a non-terminal rich
Console and assert on substrings, so they pin figures and markers without
chasing exact box-drawing geometry. Auto-follow is tested through the real
SessionCache over a temp projects tree.
"""

import io
import os
import tempfile
import time
import unittest

from rich.console import Console

from cc_token_tracker.roster import (
    ROSTER_LIMIT,
    _k,
    build_roster_view,
    percent_figure,
    render_roster,
)
from cc_token_tracker.sessions import SessionCache, SessionSummary

NOW = 1_780_000_000.0

PROMPT = '{"type":"user","message":{"role":"user","content":"hi"}}'


def make_summary(**overrides):
    fields = dict(
        project="proj-a",
        file_name="s1.jsonl",
        total_tokens=123_456,
        total_cost_usd=1.2345,
        unpriced=False,
        context_used=98_304,
        context_limit=200_000,
        context_percent=49.152,
        last_write=NOW - 240,
        is_active=False,
        last_cost_usd=0.142,
        last_input_tokens=12_400,
        last_output_tokens=3_200,
        last_cache_read_tokens=8_100,
    )
    fields.update(overrides)
    return SessionSummary(**fields)


def render_text(summaries, **kwargs):
    kwargs.setdefault("now", NOW)
    panel = render_roster(summaries, width=100, **kwargs)
    console = Console(width=100, file=io.StringIO(), force_terminal=False)
    console.print(panel)
    return console.file.getvalue()


def line_with(text, needle):
    return [line for line in text.splitlines() if needle in line]


class FigureHelpers(unittest.TestCase):
    def test_percent_figure(self):
        self.assertEqual(percent_figure(None), "?")
        self.assertEqual(percent_figure(64.2), "64%")
        self.assertEqual(percent_figure(100.0), "100%")
        # Over 100: the number stays, the trailing ? marks the overflow.
        self.assertEqual(percent_figure(104.0), "104%?")
        self.assertEqual(percent_figure(100.4), "100%?")

    def test_k_compact_thousands(self):
        self.assertEqual(_k(12_400), "12.4k")
        self.assertEqual(_k(800), "0.8k")
        self.assertEqual(_k(67_200), "67.2k")
        self.assertEqual(_k(0), "0.0k")


class Header(unittest.TestCase):
    def test_title_active_count_and_interval(self):
        active = make_summary(project="proj-live", is_active=True)
        idle = make_summary(project="proj-idle", file_name="s2.jsonl")
        text = render_text([active, idle], interval=1.0)
        self.assertIn("tokey", text)
        self.assertIn("2 active sessions", text)
        self.assertIn("[1.0s]", text)

    def test_singular_active_session(self):
        active = make_summary(project="proj-only", is_active=True)
        text = render_text([active])
        self.assertIn("1 active session", text)
        self.assertNotIn("1 active sessions", text)


class SessionBlock(unittest.TestCase):
    def test_block_shows_project_state_context_and_last(self):
        active = make_summary(project="proj-live", is_active=True)
        text = render_text([active])

        (marker_line,) = line_with(text, "▶")
        self.assertIn("proj-live", marker_line)
        self.assertIn("active", marker_line)
        # Context gauge on one line: percent, a bar, and the remainder.
        self.assertIn("49%", text)
        self.assertIn("█", text)
        self.assertIn("~101k left", text)  # (200,000-98,304)//1000
        # Last line: the most recent completed turn, IN folding cache creation.
        self.assertIn("Last: $0.142 · IN 12.4k · OUT 3.2k · CACHE 8.1k", text)

    def test_marker_only_on_the_auto_followed_session(self):
        active = make_summary(project="proj-live", is_active=True,
                              last_write=NOW - 5)
        other = make_summary(project="proj-other", file_name="s2.jsonl",
                             is_active=False, last_write=NOW - 60)
        text = render_text([active, other])
        self.assertEqual(text.count("▶"), 1)
        (marker_line,) = line_with(text, "▶")
        self.assertIn("proj-live", marker_line)
        (other_line,) = line_with(text, "proj-other")
        self.assertNotIn("▶", other_line)
        # Both are live, so both carry the "active" label regardless of marker.
        self.assertIn("active", other_line)

    def test_closing_session_is_labeled_and_dim(self):
        active = make_summary(project="proj-live", is_active=True,
                              last_write=NOW - 5)
        # Age in [600, 720): liveness stamps this CLOSING.
        closing = make_summary(project="proj-closing", file_name="s2.jsonl",
                               last_write=NOW - 650)
        text = render_text([active, closing])
        (closing_line,) = line_with(text, "proj-closing")
        self.assertIn("closing", closing_line)

    def test_cache_omitted_when_last_turn_read_no_cache(self):
        active = make_summary(project="proj-live", is_active=True,
                              last_cache_read_tokens=0)
        text = render_text([active])
        self.assertIn("Last: $0.142 · IN 12.4k · OUT 3.2k", text)
        self.assertNotIn("CACHE", text)

    def test_unknown_context_limit_is_honest(self):
        active = make_summary(project="proj-live", is_active=True,
                              context_used=98_304, context_limit=None,
                              context_percent=None)
        text = render_text([active])
        self.assertIn("context limit unknown", text)
        self.assertNotIn("█", text)  # no bar invented without a limit

    def test_overflow_percent_marker_and_zero_left(self):
        active = make_summary(project="proj-live", is_active=True,
                              context_used=208_000, context_limit=200_000,
                              context_percent=104.0)
        text = render_text([active])
        self.assertIn("104%?", text)
        self.assertIn("~0k left", text)

    def test_unpriceable_last_turn_shows_question_mark(self):
        active = make_summary(project="proj-live", is_active=True,
                              last_cost_usd=None)
        text = render_text([active])
        self.assertIn("Last: $? · IN 12.4k", text)

    def test_no_completed_turn_is_honest(self):
        active = make_summary(project="proj-live", is_active=True,
                              last_cost_usd=None, last_input_tokens=None,
                              last_output_tokens=None,
                              last_cache_read_tokens=None)
        text = render_text([active])
        self.assertIn("no completed turn yet", text)
        self.assertNotIn("IN ", text)


class FooterAndCaps(unittest.TestCase):
    def test_footer_active_only_total(self):
        active = make_summary(project="proj-live", is_active=True,
                              total_cost_usd=1.25, total_tokens=300_000)
        idle = make_summary(project="proj-idle", total_cost_usd=0.5,
                            total_tokens=50_000)
        text = render_text([active, idle])
        # Active-only total; both are active (240s old), so the active total is
        # the two-session sum: $1.75, 350k tok. No session count in the footer.
        self.assertIn("active: $1.750 · 350.0k tok", text)
        self.assertNotIn("2 sessions", text)
        self.assertNotIn("(+ unpriced)", text)

    def test_footer_unpriced_marker(self):
        active = make_summary(project="proj-live", is_active=True)
        odd = make_summary(project="proj-odd", unpriced=True)
        text = render_text([active, odd])
        self.assertIn("(+ unpriced)", text)

    def test_more_than_ten_sessions_cap_with_more_line(self):
        # Spacing kept under the 600s active window (index*30, max 360s) so this
        # stays a pure cap test, independent of the liveness boundaries.
        summaries = [
            make_summary(project=f"proj-{index:02d}",
                         file_name=f"s{index:02d}.jsonl",
                         is_active=(index == 0),
                         last_write=NOW - index * 30,
                         total_tokens=10_000, total_cost_usd=0.1)
            for index in range(13)
        ]
        text = render_text(summaries)

        self.assertEqual(ROSTER_LIMIT, 10)
        self.assertIn("proj-09", text)
        self.assertNotIn("proj-10", text)  # beyond the cap: hidden blocks
        self.assertIn("+3 more", text)
        # Footer total is ACTIVE-ONLY; all 13 are active, and the blocks hidden
        # beyond the cap are still summed in: 13*0.1 = $1.300, 13*10k = 130.0k.
        self.assertIn("active: $1.300 · 130.0k tok", text)

    def test_dropped_session_excluded_from_roster_and_footer(self):
        # 11 fresh/active sessions inside the 600s window plus one stale session
        # aged past the 720s dropped boundary: 12 discovered. The dropped one is
        # absent from the roster AND excluded from the active-only footer total.
        fresh = [
            make_summary(project=f"proj-{index:02d}",
                         file_name=f"s{index:02d}.jsonl",
                         is_active=(index == 0),
                         last_write=NOW - index * 30,
                         total_tokens=10_000, total_cost_usd=0.1)
            for index in range(11)
        ]
        dropped = make_summary(project="proj-dropped", file_name="dropped.jsonl",
                               last_write=NOW - 800,
                               total_tokens=50_000, total_cost_usd=0.5)
        summaries = fresh + [dropped]

        # Roster scope: the dropped session leaves; 11 remain, 10 shown.
        view = build_roster_view(summaries, now=NOW)
        self.assertEqual(len(view.sessions), 11)

        text = render_text(summaries)
        self.assertIn("+1 more", text)           # 11 roster blocks, 10 shown
        self.assertNotIn("proj-dropped", text)   # dropped block is gone
        # Footer is ACTIVE-ONLY: 11*0.1 = $1.100, 11*10k = 110.0k; the dropped
        # session's $0.50 / 50k are NOT summed in.
        self.assertIn("active: $1.100 · 110.0k tok", text)
        self.assertNotIn("$1.6", text)  # would be the all-discovered total

    def test_empty_roster(self):
        text = render_text([])
        self.assertIn("no sessions in the last 7 days", text)
        self.assertIn("active: $0.000 · 0.0k tok", text)  # active-only, no count

    def test_no_keybind_hints(self):
        active = make_summary(project="proj-live", is_active=True)
        text = render_text([active]).lower()
        for hint in ("press", "quit", "[q]", "keys:"):
            self.assertNotIn(hint, text)


class AutoFollow(unittest.TestCase):
    """The ▶ marker follows recency through the real cache, matching the live
    path's auto-follow."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.projects = self.tmp.name
        self.now = time.time()

    def write_transcript(self, project, name, age_seconds):
        project_dir = os.path.join(self.projects, project)
        os.makedirs(project_dir, exist_ok=True)
        path = os.path.join(project_dir, name)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(PROMPT + "\n")
        stamp = self.now - age_seconds
        os.utime(path, (stamp, stamp))
        return path

    def render(self, cache):
        summaries = cache.summaries(now=self.now)
        panel = render_roster(summaries, width=100, now=self.now)
        console = Console(width=100, file=io.StringIO(), force_terminal=False)
        console.print(panel)
        return console.file.getvalue()

    def test_marker_moves_when_another_session_becomes_newest(self):
        older = self.write_transcript("proj-a", "a.jsonl", age_seconds=200)
        self.write_transcript("proj-b", "b.jsonl", age_seconds=10)
        cache = SessionCache(self.projects)

        first = self.render(cache)
        (marker_line,) = line_with(first, "▶")
        self.assertIn("proj-b", marker_line)  # newest is the auto-followed one

        # proj-a becomes the most recently modified transcript.
        os.utime(older, (self.now - 1, self.now - 1))
        second = self.render(cache)
        (marker_line,) = line_with(second, "▶")
        self.assertIn("proj-a", marker_line)  # marker followed recency
        # proj-b is no longer the primary: its header line has lost the marker.
        (proj_b_line,) = line_with(second, "proj-b")
        self.assertNotIn("▶", proj_b_line)


if __name__ == "__main__":
    unittest.main()
