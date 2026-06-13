"""Multi-session roster view: the v0.6 all-expanded tokey screen.

One panel, one compact block per live session, newest first (7-day window).
Every block stacks the same four-part shape, so a newly-started session just
adds another block:

    ▶ my-api-server                                            active
      73% ·· ████████░░░ · ~27k left
      Last: $0.142 · IN 12.4k · OUT 3.2k · CACHE 8.1k

The ``▶`` marks the auto-followed session (the newest transcript, exactly like
the v0.3+ auto-follow); the right-hand label is the session's liveness state.
The block is summary-driven: every figure comes from the per-session
:class:`cc_token_tracker.sessions.SessionSummary`, including the ``Last:`` line
(the session's most recent completed turn). There is no live ``Frame`` in this
view and no keyboard input.

Liveness scope (v0.6.0): each block carries an active/closing/dropped label from
its transcript mtime (:mod:`cc_token_tracker.liveness`). Dropped sessions leave
the roster; the header counts the live ("active") ones only; closing sessions
stay visible but uncounted. The footer total is ACTIVE-ONLY, the same scope as
the header count.

Honesty markers carried into every block:
- LAST cost: ``$?`` when the last turn's model is unpriceable; ``no completed
  turn yet`` when the transcript has not finished a turn.
- CONTEXT: ``?`` when the limit is unknown (model absent from the limits table)
  with no bar invented; a trailing ``?`` (``104%?``) when the estimate exceeds
  the documented window. The percent is an ESTIMATE from the last prompt's
  input-side token counts; see :mod:`cc_token_tracker.context`.
"""

from __future__ import annotations

import logging
import sys
import time
from dataclasses import dataclass, replace

from rich import box
from rich.console import Console, Group
from rich.live import Live
from rich.padding import Padding
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from cc_token_tracker.display import _ACCENT, MAX_PANEL_WIDTH
from cc_token_tracker.liveness import ACTIVE, DROPPED, classify_liveness
from cc_token_tracker.sessions import SessionCache, SessionSummary

__all__ = [
    "ROSTER_LIMIT",
    "RosterView",
    "build_roster_view",
    "percent_figure",
    "render_roster",
    "run",
    "main",
]

_LOG = logging.getLogger(__name__)

# At most this many session blocks render; overflow becomes a "+N more" line
# above the footer. The footer total still covers every active session.
ROSTER_LIMIT = 10

# Width of a block's context bar, in cells.
_BAR_WIDTH = 24

# Left indent (cells) for a block's body, so the context/Last lines line up
# under the project name rather than under the ▶ marker column.
_MARKER_WIDTH = 2

# Context gauge colour (distinct from the cyan ▶/title accent).
_CONTEXT_COLOR = "yellow"


@dataclass(frozen=True)
class RosterView:
    """One render pass's presentation scope over the session summaries.

    ``sessions`` is the on-screen roster: every summary whose liveness is not
    "dropped" (so active + closing), newest first, each carrying its freshly
    computed ``state``. ``active_count`` counts the "active" ones ONLY --
    closing sessions stay on screen as blocks but are never counted. Dropped
    sessions are absent from ``sessions`` entirely. This is presentation, not
    accounting: the cost and token figures inside each summary are reused
    verbatim, never recomputed here.
    """

    sessions: list[SessionSummary]
    active_count: int


def build_roster_view(
    summaries: list[SessionSummary], *, now: float
) -> RosterView:
    """Stamp liveness onto ``summaries`` and derive the panel's roster scope.

    Each summary is re-stamped with ``state = classify_liveness(now,
    last_write)`` (the field is presentation-only; see
    :class:`cc_token_tracker.sessions.SessionSummary`). The roster keeps the
    non-dropped ones in the given order; the active count is the number of
    "active" survivors. Pure given ``now``: no IO, no re-parsing, no touching
    of the frozen cost outputs.
    """
    staged = [
        replace(summary, state=classify_liveness(now, summary.last_write))
        for summary in summaries
    ]
    sessions = [summary for summary in staged if summary.state != DROPPED]
    active_count = sum(1 for summary in sessions if summary.state == ACTIVE)
    return RosterView(sessions=sessions, active_count=active_count)


def percent_figure(percent: float | None) -> str:
    """The context percent: ``NN%``, ``NNN%?`` past 100, ``?`` when unknown.

    An unknown limit yields ``?`` (the limits table never guesses). A percent
    above 100 keeps its number but gains a trailing ``?`` -- the estimate
    overflowed the documented window, and the marker says so instead of
    clamping to a clean-looking 100%.
    """
    if percent is None:
        return "?"
    figure = f"{round(percent)}%"
    return figure + "?" if percent > 100 else figure


def _k(tokens: int) -> str:
    """Token count in compact thousands: ``12.4k``, ``0.8k``, ``67.2k``."""
    return f"{tokens / 1000:.1f}k"


def _header(active_count: int, interval: float) -> Table:
    """Top line: ``tokey`` left, ``N active session(s) · [interval]`` right."""
    grid = Table.grid(expand=True)
    grid.add_column(justify="left", ratio=1)
    grid.add_column(justify="right")
    plural = "" if active_count == 1 else "s"
    right = Text.assemble(
        (f"{active_count} active session{plural}", "dim"),
        (" · ", "dim"),
        (f"[{interval:.1f}s]", "dim"),
    )
    grid.add_row(Text("tokey", style=f"bold {_ACCENT}"), right)
    return grid


def _context_line(summary: SessionSummary) -> Text:
    """A block's one-line context gauge: ``73% ·· ████░░ · ~27k left``.

    An unknown limit renders an honest ``context limit unknown for this model``
    with no bar invented. An over-100 estimate fills the bar and shows
    ``~0k left`` beside the ``NNN%?`` marker.
    """
    percent = summary.context_percent
    if percent is None:
        return Text("context limit unknown for this model", style="dim")
    filled = round(min(percent, 100.0) / 100.0 * _BAR_WIDTH)
    bar = (
        Text("█" * filled, style=_CONTEXT_COLOR)
        + Text("░" * (_BAR_WIDTH - filled), style="dim")
    )
    remaining_k = max(0, (summary.context_limit or 0) - (summary.context_used or 0)) // 1000
    return (
        Text.assemble((percent_figure(percent), f"bold {_CONTEXT_COLOR}"), (" ·· ", "dim"))
        + bar
        + Text.assemble((" · ", "dim"), (f"~{remaining_k}k left", "dim"))
    )


def _last_line(summary: SessionSummary) -> Text:
    """A block's ``Last:`` line: the most recent completed turn's figures.

    ``$?`` when that turn's model is unpriceable; ``no completed turn yet`` when
    the transcript has finished none. ``CACHE`` is shown only when the turn read
    cache (non-zero), matching the single-session hero's cache cell otherwise
    staying silent. IN folds cache-creation into input (done in the summary).
    """
    if summary.last_output_tokens is None:
        return Text.assemble(("Last: ", "dim"), ("no completed turn yet", "dim italic"))
    cost = "$?" if summary.last_cost_usd is None else f"${summary.last_cost_usd:.3f}"
    parts: list = [
        ("Last: ", "dim"),
        (cost, ""),
        (" · ", "dim"),
        (f"IN {_k(summary.last_input_tokens or 0)}", ""),
        (" · ", "dim"),
        (f"OUT {_k(summary.last_output_tokens)}", ""),
    ]
    if (summary.last_cache_read_tokens or 0) > 0:
        parts.append((" · ", "dim"))
        parts.append((f"CACHE {_k(summary.last_cache_read_tokens)}", ""))
    return Text.assemble(*parts)


def _session_block(summary: SessionSummary) -> Group:
    """One session's compact block: a header line (marker, project, liveness
    label) over the indented context and Last lines. The ``▶`` marks the
    auto-followed session; the right label is the liveness state."""
    is_live = summary.state == ACTIVE
    label = (
        Text("active", style="bold green")
        if is_live
        else Text("closing", style="dim")
    )
    head = Table.grid(expand=True, padding=0)
    head.add_column(width=_MARKER_WIDTH)
    head.add_column(justify="left", ratio=1, no_wrap=True, overflow="ellipsis")
    head.add_column(justify="right")
    head.add_row(
        Text("▶", style=_ACCENT) if summary.is_active else Text(""),
        Text(summary.project, style="bold" if is_live else "dim"),
        label,
    )
    body = Padding(
        Group(_context_line(summary), _last_line(summary)),
        (0, 0, 0, _MARKER_WIDTH),
    )
    return Group(head, body)


def _footer(active: list[SessionSummary]) -> Table:
    """The ACTIVE-ONLY total: ``active: $X.XXX · N.Nk tok`` left, with a right
    ``(+ unpriced)`` flag when ANY active session carries it (the dollar figure
    then covers the priceable turns only). Scope matches the header's active
    count exactly: closing and dropped sessions are excluded, while active
    blocks hidden by the ROSTER_LIMIT cap are still summed in. No session count
    -- the header already states how many are active."""
    total_cost = sum(s.total_cost_usd for s in active)
    total_tokens = sum(s.total_tokens for s in active)
    left = Text(f"active: ${total_cost:.3f} · {_k(total_tokens)} tok", style="bold")
    right = (
        Text("(+ unpriced)", style="yellow")
        if any(s.unpriced for s in active)
        else Text("")
    )
    grid = Table.grid(expand=True)
    grid.add_column(justify="left", ratio=1)
    grid.add_column(justify="right")
    grid.add_row(left, right)
    return grid


def render_roster(
    summaries: list[SessionSummary],
    *,
    width: int | None = None,
    now: float | None = None,
    interval: float = 1.0,
) -> Panel:
    """Render the all-expanded roster to a rich Panel. Pure given ``now``; no IO.

    ``summaries`` is the session-cache output, newest first, the auto-followed
    entry flagged ``is_active``. Liveness scope is applied here (see
    :func:`build_roster_view`): dropped sessions leave the roster, the header
    counts only the live ("active") ones, and closing sessions stay visible but
    uncounted. Every surviving session renders as a compact block; blocks beyond
    ROSTER_LIMIT collapse into a "+N more" line above the footer. The footer
    total is ACTIVE-ONLY (the same scope as the header count): closing and
    dropped sessions are excluded, while active blocks hidden by the cap are
    still summed. ``now`` drives the liveness scope (defaults to the current
    time; tests pin it); ``interval`` is shown in the header refresh tag.
    """
    if now is None:
        now = time.time()

    view = build_roster_view(summaries, now=now)
    roster = view.sessions

    items: list = [_header(view.active_count, interval), Rule()]
    if roster:
        shown = roster[:ROSTER_LIMIT]
        for summary in shown:
            items.append(_session_block(summary))
            items.append(Rule(style="dim"))
        omitted = len(roster) - len(shown)
        if omitted > 0:
            items.append(Text(f"+{omitted} more", style="dim"))
            items.append(Rule(style="dim"))
    else:
        items.append(Text("no sessions in the last 7 days", style="dim italic"))
        items.append(Rule(style="dim"))

    items.append(_footer([s for s in roster if s.state == ACTIVE]))

    return Panel(
        Group(*items),
        box=box.ROUNDED,
        padding=(1, 2),
        width=width,
    )


def run(interval: float = 1.0) -> int:
    """Poll loop: the all-expanded roster as the default and only view.

    Each tick re-runs discovery and re-parses the active transcript through the
    session cache (which re-parses a non-active transcript only when its
    (mtime, size) moves), then renders. A newly-started session therefore
    appears within one tick with no restart; auto-follow tracks the newest
    transcript. A tick that raises is logged and skipped; KeyboardInterrupt
    exits cleanly.
    """
    cache = SessionCache()
    console = Console()
    try:
        with Live(console=console, auto_refresh=False, screen=False) as live:
            while True:
                try:
                    summaries = cache.summaries()
                    target_width = min(console.width, MAX_PANEL_WIDTH)
                    live.update(
                        render_roster(
                            summaries, width=target_width, interval=interval
                        ),
                        refresh=True,
                    )
                except Exception:  # noqa: BLE001 - one bad tick must not kill us
                    _LOG.exception("roster tick failed; continuing")
                time.sleep(interval)
    except KeyboardInterrupt:
        pass
    return 0


def main() -> int:
    """Console-script entry point: the roster with its defaults."""
    return run()


if __name__ == "__main__":
    sys.exit(main())
