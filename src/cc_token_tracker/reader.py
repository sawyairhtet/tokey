"""Poll-based reader: turn one transcript into records.

One tick per call. This module does not own a sleep or poll loop; the caller
drives cadence. Each tick does a full re-read of the given transcript (no
byte-offset tracking) and parses every line with the existing parse_line.
Records that parse to None are dropped.

Full re-read is deliberate: account_usage dedupes by message_id in first-seen
order, so re-reading the whole file each tick is idempotent downstream.

WHICH transcript to read is decided upstream by
:func:`cc_token_tracker.sessions.discover_sessions`; this module only reads the
path it is handed, keeping resolution and reading separate.

The reader never raises. Any failure (no transcript resolved, transcript
missing or unreadable) resolves to a no-op tick: an empty ReadResult with
transcript_path None. A truncated final line that does not parse is dropped
while the prior records are kept.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from cc_token_tracker.parser import TranscriptRecord, parse_line

__all__ = ["ReadResult", "read_transcript"]


@dataclass(frozen=True)
class ReadResult:
    """Records parsed from the current transcript on one tick.

    records holds parsed TranscriptRecord values in transcript order (the same
    shape Turn uses for its records). transcript_path is the transcript resolved
    on this tick, or None for a no-op tick.
    """

    records: list[TranscriptRecord] = field(default_factory=list)
    transcript_path: str | None = None


def read_transcript(transcript_path: str | None) -> ReadResult:
    """Full re-read one already-resolved transcript path into a ReadResult.

    This owns the transcript read only -- it does not decide WHICH file. The path
    is resolved upstream (see the module docstring) and fed here, keeping
    resolution and reading separate.

    A None path -- nothing resolved this tick -- is the no-op tick: an empty
    ReadResult with transcript_path None, the same shape an unreadable transcript
    yields. Otherwise every line is parsed with parse_line and records that parse
    to None are dropped. Never raises.
    """
    if transcript_path is None:
        return ReadResult()

    try:
        with open(transcript_path, encoding="utf-8", errors="replace") as handle:
            records: list[TranscriptRecord] = []
            for line in handle:
                record = parse_line(line.rstrip("\n"))
                if record is not None:
                    records.append(record)
    except OSError:
        return ReadResult()

    return ReadResult(records=records, transcript_path=transcript_path)
