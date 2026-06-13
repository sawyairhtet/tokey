"""Session liveness classification: active / closing / dropped (v0.6.0, T1).

A pure, presentation-scope helper. A session's liveness is derived ONLY from
how long ago its transcript was last written -- the file mtime captured during
discovery (``SessionSummary.last_write``, an ``os.stat`` field). No transcript
is opened or re-read to derive activity; the mtime is free from the stat the
discovery pass already does.

The boundaries are exact and authoritative (``age = now - last_write``, in
seconds, half-open on the low side):

    age < 600            -> "active"
    600 <= age < 720     -> "closing"
    age >= 720           -> "dropped"

This module decides the LABEL only. Roster scope -- which states stay on screen
and which count toward the header's active figure -- lives with the panel
assembly that consumes these labels; see :func:`cc_token_tracker.roster.build_roster_view`.
"""

from __future__ import annotations

__all__ = [
    "ACTIVE",
    "CLOSING",
    "DROPPED",
    "CLOSING_AFTER_SECONDS",
    "DROPPED_AFTER_SECONDS",
    "classify_liveness",
]

# The three labels, named so callers compare against a constant rather than a
# bare string literal.
ACTIVE = "active"
CLOSING = "closing"
DROPPED = "dropped"

# A session reads "active" while younger than this, "closing" from here until
# DROPPED_AFTER_SECONDS, and "dropped" at or beyond it. The bounds are exact:
# an age of exactly 600 is closing, exactly 720 is dropped.
CLOSING_AFTER_SECONDS = 600.0
DROPPED_AFTER_SECONDS = 720.0


def classify_liveness(now: float, last_write: float) -> str:
    """Label one session from its transcript mtime: active/closing/dropped.

    ``now`` and ``last_write`` are POSIX timestamps; ``last_write`` is the
    transcript file mtime (``os.stat(...).st_mtime``). The age is
    ``now - last_write``; see the module docstring for the exact, authoritative
    boundaries. A negative age (clock skew making a file look future-dated) is
    younger than every boundary and so reads "active".
    """
    age = now - last_write
    if age < CLOSING_AFTER_SECONDS:
        return ACTIVE
    if age < DROPPED_AFTER_SECONDS:
        return CLOSING
    return DROPPED
