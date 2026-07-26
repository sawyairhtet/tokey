# Tokey

Live terminal panel showing what each Claude Code prompt costs, in tokens and
dollars. Reads `~/.claude/projects/*/*.jsonl` transcripts. One runtime dep: `rich`.

- Console entry `tokey` → `cc_token_tracker.roster:main`
- `tokey-hook` → `cc_token_tracker.hook:main` (writes session liveness markers)

## Run / test
- Run: `tokey`  (`tokey cc` adds the opt-in account-usage block; `--no-mood` hides the footer mascot)
- Test: `pytest`
- Lint: `ruff check`

## Architecture: one frozen pipeline, consumed and never re-implemented

Data flows one direction. Every display layer CONSUMES the layer below and
reimplements none of it:

```
sessions.discover_sessions (which transcripts)
  → reader.read_transcript (full re-read, one path)
  → parser (jsonl lines → records)
  → segmentation (records → turns)
  → accounting + turn_cost + pricing (tokens → $)
  → context (window % estimate)
  → sessions.summarize_session → frozen SessionSummary
  → liveness → roster (render) → mood (footer)
```

`roster.py` is the ONLY render surface and `tokey`'s only entry point. There is
no second view: the single-session panel (`display.py`) was superseded by the
roster in v0.5.0 and deleted in the v0.8 audit. If you are adding UI, it goes in
`roster.py`.

`SessionSummary` (`sessions.py`) is the single data contract between the pipeline
and every render surface. Read it before touching anything visual.

## Invariants: break these and the numbers lie

- **Single source of truth for money/totals.** Session total is `account_usage(...)`
  over records; dollars come from `turn_cost.session_cost` (one turn:
  `turn_cost.turn_usd`). Never re-sum turn totals or re-price by hand somewhere
  new; call the existing helper.
- **Unpriceable turns.** A token-bearing turn whose model isn't in the pricing table
  is left OUT of the dollar sum and flips `unpriced` (renders `$1.23+`). A zero-token
  in-flight turn NEVER flips it.
- **Context estimate is honest-or-None.** Unknown model or no usage-bearing record
  yields `context_*` = `None`, never a fabricated limit or a fake 0. Overflow renders
  `104%?`, not a clamped 100%.
- **Per-model tables go stale.** `pricing.py` (rates) and `context.py` (window limits)
  are hand-maintained lookup tables keyed on model string. When a new Claude model
  ships, update BOTH or costs and context silently fall back to unknown.
- **Malformed transcript values die at the parse boundary.** `parser.py` coerces
  every scalar to its annotated type (`_str_or_none` / `_int_or_none`). Downstream
  layers document "never raises" and rely on it: `message_id` becomes a dict key
  in accounting, `model` hits a regex in pricing. Do not widen a field without a
  coercion.

## Conventions

- Version is single-sourced in `src/cc_token_tracker/__init__.py` (`__version__`). Bump there only.
- No em dashes anywhere, in code, docs, or comments. The `mood.py` aphorism pool is
  test-guarded for this (`test_mood.py`, VettingTests). Rewrite the grammar to fit
  (colon, comma, semicolon); do not blanket-swap in a hyphen.
- Lint config lives in `pyproject.toml` (`E,W,F,I,UP,B,SIM,RUF`, 88 cols). CI runs
  `ruff check src tests`, so a lint failure is a build failure.
