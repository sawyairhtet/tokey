# Tokey

A tiny live panel that shows what each Claude Code prompt actually costs, in
tokens and in dollars. I built it because the built-in statusline tells you how
full your context is but never what the last turn spent, and that per-prompt
number is the thing I kept wanting to see.

## What it shows

Claude Code's built-in statusline shows how full your context window is. It does
not show what the prompt you just sent actually cost. This shows that, for every
live session at once.

The view is a roster: one compact block per Claude Code session from the last 7
days, newest first. Every block stacks the same shape, so a newly-started
session just adds another block within a refresh (no restart). Each block is:

- a **header line**: the project name and the session's liveness (`active`, or
  `closing` as it winds down), with `▶` marking the session tokey is
  auto-following (the most recently active one).
- **Context**: `NN% ·· bar · ~Nk left`, an estimate of how full the window is,
  derived from the last prompt's token figures (input plus cache read plus
  cache creation). Treat it as a gauge rather than an exact meter; an estimate
  that overflows the window renders like `104%?` instead of clamping to a clean
  100%, and a model the limit table does not know shows `context limit unknown`.
- **Last**: the session's most recent completed turn, broken into IN (input
  plus cache creation), OUT, CACHE (cache read, shown only when the turn read
  cache), and the turn's dollar cost. An unpriceable model shows `$?`; a session
  that has not finished a turn yet shows `no completed turn yet`.

With more than 10 live sessions the newest 10 render and a "+N more" line counts
the rest. A footer shows the active total, `active: $X · Nk tok`, summed over the
sessions currently active (the same scope as the header's active count); a
`(+ unpriced)` flag appears whenever any of them contains turns that could not
be priced.

Each turn is priced with its own model before summing, so sessions that mix
models add up correctly.

The per-prompt Last figure is the one I watch: it tells me which prompts are
expensive while I can still change how I am asking, instead of finding out at
the end.

## Requirements

- Python 3.11+
- Claude Code

## Install

Clone the repo, then from inside it:

    pip install -e .

This installs one command on your PATH: `tokey` (the panel). Tokey auto-detects
your active Claude Code session by reading the most recently modified transcript
under `~/.claude/projects`. No configuration needed.

If `tokey` is not found after install, your `~/.local/bin` is not on your
PATH. Add it (e.g. `export PATH="$HOME/.local/bin:$PATH"` in your shell rc) and
reopen the terminal.

## Windows

After `pip install -e .`, Windows often reports that `tokey` is "not
recognized". pip dropped it in your Python `Scripts` directory (something like
`...\PythonXX\Scripts`, or `...\Scripts` inside your venv) and that directory is
not on your PATH. Two ways to fix it:

**Option A: put Scripts on PATH (GUI editor).** Open the System Properties
environment-variable editor: press Win+R, run `sysdm.cpl`, go to the *Advanced*
tab, click *Environment Variables*, select `Path`, then *Edit* → *New* and add
your Python `Scripts` directory as its own entry. Reopen the terminal and
`tokey` will resolve.

Do NOT run `setx PATH "%PATH%;C:\...\Scripts"` to do this. `setx` re-expands
`%PATH%`, can fuse your user and system PATH together, and silently truncates
anything past its length limit; it corrupted a real PATH during testing here.
Always edit PATH through the GUI editor above.

**Option B: skip PATH entirely with `python -m`.** You do not have to touch
PATH at all; run the panel directly with:

    python -m cc_token_tracker.roster

If `python` isn't the launcher on your box, `py -m cc_token_tracker.roster`
does the same thing. Either way, the `-m` form must use the *same* interpreter
where you ran `pip install -e .`. If you installed into a venv, that venv's
`python` / `py` is the only one that can import `cc_token_tracker`.

## Run it

Open a second terminal pane next to Claude Code and run:

    tokey

The panel updates once a second. Keep Claude Code in one pane, the tracker in
the other. That two-pane setup is the intended way to use it.

Press Ctrl-C to quit the panel.

## Notes

- The tracker reads Claude Code's transcript files; it never scrapes your
  terminal and sends nothing anywhere. It runs entirely on your machine.
- It shows every live session at once and follows you across projects
  automatically. Start a new Claude Code session in any folder and it appears as
  a new block within a refresh, auto-followed (▶) as the newest.

A couple of things to know about the dollar figures: they are computed from a
built-in rate table (API list prices as of 2026-06-12), so treat them as close
estimates rather than a billing statement. Cache writes are priced at the
5-minute TTL rate; turns that carry 1-hour cache writes will undercount
slightly. A model the table does not know shows `$?` instead of a price, and
the session total then carries a "(+ unpriced)" marker so you know the figure
is partial rather than silently low.

The context column works the same way: limits come from a built-in per-model
table (documented context windows as of 2026-06-12), so it needs the same kind
of occasional refresh as the rate table when new models ship. A model the
table does not know shows `?` for context rather than a guessed limit, and an
estimate that exceeds the documented window keeps its number with a trailing
`?` (like `104%?`) instead of pretending to be full.

The panel reflects the transcript on disk: a brand-new session appears as a
block as soon as its transcript exists, showing `no completed turn yet` until
its first prompt completes.
