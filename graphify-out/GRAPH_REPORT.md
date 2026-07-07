# Graph Report - .  (2026-07-07)

## Corpus Check
- Corpus is ~38,827 words - fits in a single context window. You may not need a graph.

## Summary
- 826 nodes · 1810 edges · 43 communities (35 shown, 8 thin omitted)
- Extraction: 71% EXTRACTED · 29% INFERRED · 0% AMBIGUOUS · INFERRED: 528 edges (avg confidence: 0.72)
- Token cost: 62,978 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Account Usage Rendering|Account Usage Rendering]]
- [[_COMMUNITY_Transcript Parsing|Transcript Parsing]]
- [[_COMMUNITY_Session Summaries & Roster|Session Summaries & Roster]]
- [[_COMMUNITY_Markers & Hook Liveness|Markers & Hook Liveness]]
- [[_COMMUNITY_Roster Rendering|Roster Rendering]]
- [[_COMMUNITY_Model Cost Normalization|Model Cost Normalization]]
- [[_COMMUNITY_Module & Test Files|Module & Test Files]]
- [[_COMMUNITY_Display Frame Computation|Display Frame Computation]]
- [[_COMMUNITY_Transcript Reading|Transcript Reading]]
- [[_COMMUNITY_Context Estimation|Context Estimation]]
- [[_COMMUNITY_Display Run Loop|Display Run Loop]]
- [[_COMMUNITY_Liveness Classification|Liveness Classification]]
- [[_COMMUNITY_Cost Row Rendering Tests|Cost Row Rendering Tests]]
- [[_COMMUNITY_Turn Segmentation|Turn Segmentation]]
- [[_COMMUNITY_Mood Mascot Footer|Mood Mascot Footer]]
- [[_COMMUNITY_Recent Rows Rendering|Recent Rows Rendering]]
- [[_COMMUNITY_Mood Face Tests|Mood Face Tests]]
- [[_COMMUNITY_Dashboard UI Elements|Dashboard UI Elements]]
- [[_COMMUNITY_Recent Entries & Turn Cost|Recent Entries & Turn Cost]]
- [[_COMMUNITY_Usage Provider Lifecycle|Usage Provider Lifecycle]]
- [[_COMMUNITY_Credentials Reading|Credentials Reading]]
- [[_COMMUNITY_Panel Rendering|Panel Rendering]]
- [[_COMMUNITY_Live Panel Concepts|Live Panel Concepts]]
- [[_COMMUNITY_Per-turn Cost Tests|Per-turn Cost Tests]]
- [[_COMMUNITY_Context Gauge Row|Context Gauge Row]]
- [[_COMMUNITY_Session Summary Assembly|Session Summary Assembly]]
- [[_COMMUNITY_Usage Payload Parsing|Usage Payload Parsing]]
- [[_COMMUNITY_CLI Entry & Flags|CLI Entry & Flags]]
- [[_COMMUNITY_macOS Keychain Read|macOS Keychain Read]]
- [[_COMMUNITY_Recent Population Tests|Recent Population Tests]]
- [[_COMMUNITY_Account Usage Flag|Account Usage Flag]]
- [[_COMMUNITY_Fetch Usage Endpoint|Fetch Usage Endpoint]]
- [[_COMMUNITY_Usage Test Doubles|Usage Test Doubles]]
- [[_COMMUNITY_Aphorism Pool Vetting|Aphorism Pool Vetting]]
- [[_COMMUNITY_Render Width Cap|Render Width Cap]]
- [[_COMMUNITY_Footer Integration Tests|Footer Integration Tests]]
- [[_COMMUNITY_Mood Rotation Tests|Mood Rotation Tests]]
- [[_COMMUNITY_Model Threading Tests|Model Threading Tests]]
- [[_COMMUNITY_Usage Enabled Flag|Usage Enabled Flag]]
- [[_COMMUNITY_Speech Bubble Tests|Speech Bubble Tests]]
- [[_COMMUNITY_CI Workflow|CI Workflow]]
- [[_COMMUNITY_OAuth Token & Account Usage|OAuth Token & Account Usage]]
- [[_COMMUNITY_Tokey Entry Point|Tokey Entry Point]]

## God Nodes (most connected - your core abstractions)
1. `SessionSummary` - 42 edges
2. `TranscriptRecord` - 41 edges
3. `parse_line()` - 39 edges
4. `read_result()` - 37 edges
5. `make_summary()` - 37 edges
6. `SessionCache` - 34 edges
7. `render_text()` - 34 edges
8. `summarize_session()` - 26 edges
9. `prompt()` - 26 edges
10. `typed()` - 26 edges

## Surprising Connections (you probably didn't know these)
- `prompt()` --calls--> `TranscriptRecord`  [INFERRED]
  tests/conftest.py → src/cc_token_tracker/parser.py
- `tool_result()` --calls--> `TranscriptRecord`  [INFERRED]
  tests/conftest.py → src/cc_token_tracker/parser.py
- `typed()` --calls--> `TranscriptRecord`  [INFERRED]
  tests/conftest.py → src/cc_token_tracker/parser.py
- `FindActiveTranscript` --uses--> `TranscriptRecord`  [INFERRED]
  tests/test_reader.py → src/cc_token_tracker/parser.py
- `ReadTranscript` --uses--> `TranscriptRecord`  [INFERRED]
  tests/test_reader.py → src/cc_token_tracker/parser.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **CI Pipeline (lint + matrix test)** — _github_workflows_ci_ci, _github_workflows_ci_lint, _github_workflows_ci_test [EXTRACTED 1.00]
- **Account Usage Fetch Flow** — readme_account_usage, readme_oauth_token_read, changelog_macos_keychain [INFERRED 0.85]

## Communities (43 total, 8 thin omitted)

### Community 0 - "Account Usage Rendering"
Cohesion: 0.07
Nodes (34): _project_title(), One render pass's presentation scope over the session summaries.      ``sessions, The session's display title: the real cwd as a ``~``-relative path.      Falls b, RosterView, AccountUsage, Credits, _num_or_none(), _parse_iso() (+26 more)

### Community 1 - "Transcript Parsing"
Cohesion: 0.05
Nodes (38): account_usage(), _as_int(), MessageCost, Deduped cost for one assistant message.      The four components are plain ints, Coalesce an absent (None) count to 0 for summing. Sum-only zeroing., Compute deduped per-message costs and a running session total.      Includes onl, _int_or_none(), _is_tool_result() (+30 more)

### Community 2 - "Session Summaries & Roster"
Cohesion: 0.08
Nodes (28): build_roster_view(), Stamp liveness onto ``summaries`` and derive the panel's roster scope.      Each, discover_sessions(), Enumerate ``<projects_dir>/*/*.jsonl``, newest first, within the window.      ``, Full-parse one transcript into a :class:`SessionSummary`, or ``None``.      The, Summaries across calls, re-parsing changed transcripts only.      Each :meth:`su, One discovered transcript: where it is, whose project, how fresh.      ``project, SessionCache (+20 more)

### Community 3 - "Markers & Hook Liveness"
Cohesion: 0.08
Nodes (21): main(), Claude Code SessionStart/SessionEnd hook: write a session liveness marker.  Clau, Process one hook payload: write the matching marker. Return whether one     was, Console-script / ``python -m`` entry point: one hook tick from stdin.      Reads, run_hook(), MarkerInfo, _parse_marker(), Per-session open/close markers written by the Claude Code hooks.  The roster's a (+13 more)

### Community 4 - "Roster Rendering"
Cohesion: 0.10
Nodes (33): AccountUsage, RenderableType, _account_block(), _credits_row(), _footer(), _header(), _k(), _last_line() (+25 more)

### Community 5 - "Model Cost Normalization"
Cohesion: 0.10
Nodes (11): normalize_model(), Strip a trailing ``-YYYYMMDD`` date suffix, if present., Dollar cost of one turn, or None when the model is unknown.      ``cost_usd`` is, turn_cost_usd(), CostUsdPassthrough, KnownModels, Normalization, A trailing -YYYYMMDD date suffix is stripped before the second lookup;     $?/No (+3 more)

### Community 6 - "Module & Test Files"
Cohesion: 0.10
Nodes (15): Usage accounting over parsed transcript records.  Pure logic: no file reading, n, Per-message breakdown plus cumulative session totals.      ``session_total`` equ, SessionAccounting, cc_token_tracker package., Parse a single Claude Code transcript line into a typed record.  This turns one, Per-turn dollar pricing keyed on transcript model strings.  Pure logic: no IO, n, Poll-based reader: turn the live transcript into records.  One tick per call. Th, Segment an ordered record stream into turns.  Pure logic: no IO, no file reading (+7 more)

### Community 7 - "Display Frame Computation"
Cohesion: 0.14
Nodes (9): prompt(), A genuine typed user prompt (opens a turn)., read_result(), ComputeFrame, DisplayStateUpdate, FrameRecentShape, compute_frame exposes recent_omitted: completed prompts that are neither     the, RecentOmitted (+1 more)

### Community 8 - "Transcript Reading"
Cohesion: 0.15
Nodes (10): find_active_transcript(), Full re-read one already-resolved transcript path into a ReadResult.      This o, Resolve WHICH transcript is active by recency, with no configuration.      Locat, read_transcript(), assistant_line(), FindActiveTranscript, Tests for cc_token_tracker.reader (Ticket 5).  Uses real temp files (tempfile),, find_active_transcript resolves the most recently modified *.jsonl under     ~/. (+2 more)

### Community 9 - "Context Estimation"
Cohesion: 0.15
Nodes (12): context_limit(), ContextEstimate, estimate_context(), Per-model context-window limits and used-context estimation.  Pure logic: no IO,, Documented context window for a transcript model string, or ``None``.      Same, Estimated context occupancy of one session.      ``used`` is the last prompt's i, Estimate context occupancy from parsed records, in transcript order.      Scans, assistant_record() (+4 more)

### Community 10 - "Display Run Loop"
Cohesion: 0.13
Nodes (18): compute_frame(), DisplayState, _FlashState, Frame, main(), Build a Frame from one ReadResult. Pure; never raises.      session_total comes, Holds the last good Frame across ticks., Fold one ReadResult into the display state and return the frame.          A no-o (+10 more)

### Community 11 - "Liveness Classification"
Cohesion: 0.13
Nodes (10): classify_liveness(), classify_with_marker(), Session liveness classification: active / closing / dropped (v0.6.0, T1).  A pur, Label one session from its transcript mtime: active/closing/dropped.      ``now`, Liveness from a session marker, falling back to transcript mtime.      The marke, ClassifyLiveness, ClassifyWithMarker, make_summary() (+2 more)

### Community 12 - "Cost Row Rendering Tests"
Cohesion: 0.14
Nodes (8): A typed user prompt that opens a turn AND carries its raw text, exactly as     p, typed(), ModelTags, RECENT rows lead with the turn's own dollar cost ("$?" when unpriceable,     sam, The RECENT model tag: _model_tag abbreviates every known model to a     <=6 char, The hero line's COST cell: a dollar figure for a known model, "$?" for     an un, RecentAndSessionCost, RenderCost

### Community 13 - "Turn Segmentation"
Cohesion: 0.21
Nodes (12): _is_typed_prompt(), A genuine typed user prompt -- the thing that opens a turn., Group an ordered record stream into turns.      - A new turn OPENS at a typed us, segment_turns(), A user line carrying a tool_result (does NOT open a turn)., tool_result(), assistant(), ids() (+4 more)

### Community 14 - "Mood Mascot Footer"
Cohesion: 0.14
Nodes (19): accent(), _baymax(), current_index(), face_text(), is_working(), pick(), Group, Text (+11 more)

### Community 15 - "Recent Rows Rendering"
Cohesion: 0.16
Nodes (6): Render layer for the RECENT section. We assert STRUCTURE in the rendered     tex, Render layer for the '+N more' overflow line. The count is read straight     off, Render-only polish: hero field dividers, magenta RECENT cost figures, and     th, RenderOmitted, RenderPolish, RenderRecent

### Community 16 - "Mood Face Tests"
Cohesion: 0.13
Nodes (6): AccentTests, FaceSetTests, FaceTests, IsWorkingTests, make_summary(), Tests for cc_token_tracker.mood (multi-row mood faces + speech bubbles).  Everyt

### Community 17 - "Dashboard UI Elements"
Cohesion: 0.14
Nodes (18): Account-level Claude Usage Bars, Session Active Status Marker, Aphorism Speech Bubble, Per-session Context Usage Bar (% used, tokens left), Cost Display (USD per prompt/total), Header Bar (title, active sessions, refresh, plan), Last Prompt Line (cost, IN/OUT/CACHE tokens), Session Model Label (sonnet-4-6, opus-4-8) (+10 more)

### Community 18 - "Recent Entries & Turn Cost"
Cohesion: 0.16
Nodes (17): _cost_figure(), _model_tag(), _prompt_snippet(), Live token-usage display.  A long-running process that renders Claude Code token, The turn's typed-prompt text, whitespace-collapsed; '' when absent.      The ope, The history view's backing tuple AND the count the cap dropped.      The hero is, One turn's dollar cost via the existing pricing table, or None.      Pricing is, A turn's dollar figure, or "$?" when the model is unknown.      One rule for eve (+9 more)

### Community 19 - "Usage Provider Lifecycle"
Cohesion: 0.21
Nodes (7): Credentials, The bits of Claude Code's credential file this feature needs.      ``token`` is, Holds the last good :class:`AccountUsage` so render never blocks on IO.      :me, The last good reading, or None if none yet. Instant; never blocks., A dim status line for the panel, or None when nothing should show.          None, UsageProvider, Provider

### Community 20 - "Credentials Reading"
Cohesion: 0.23
Nodes (5): _credentials_from_blob(), Pull the OAuth token and plan out of a parsed credentials blob, or None.      Sh, Read the OAuth token and plan from Claude Code's credential store. Never     rai, read_credentials(), ReadCredentials

### Community 21 - "Panel Rendering"
Cohesion: 0.21
Nodes (15): _figure_grid(), _num(), Panel, Table, Text, Group thousands so the figures stay readable at a glance., A label-over-value grid: dim labels on top, figures beneath, spread     evenly a, The session total as one full-inner-width row: a dim ``TOTAL TOKENS``     label (+7 more)

### Community 22 - "Live Panel Concepts"
Cohesion: 0.18
Nodes (13): Per-model Context Limit Table, Per-model Pricing Rate Table, Direct Transcript Discovery, UTF-8 Stdout Guard, Single-sourced Version / tokey --version, Baymax Footer Companion, Context Fullness Gauge, Last Prompt Line (real-time) (+5 more)

### Community 23 - "Per-turn Cost Tests"
Cohesion: 0.32
Nodes (7): One turn: its records in transcript order, plus whether it closed.      ``comple, Turn, Model of the turn's LAST usage-bearing record, or None without one.      When a, Cost each turn independently, preserving turn order.      For every turn, runs :, turn_costs(), _turn_model(), TurnCosts

### Community 24 - "Context Gauge Row"
Cohesion: 0.20
Nodes (8): _context_line(), _context_model_label(), _context_row(), percent_figure(), The context percent: ``NN%``, ``NNN%?`` past 100, ``?`` when unknown.      An un, A block's one-line context gauge: ``73% ·· ████░░ · ~27k left``.      An unknown, Short model label for the context row: ``claude-opus-4-8`` -> ``opus-4-8``., The context gauge plus, right-aligned under the header's liveness label,     the

### Community 25 - "Session Summary Assembly"
Cohesion: 0.27
Nodes (7): Multi-session discovery and per-session accounting summaries.  Three layers, all, A placeholder summary for an OPEN session whose transcript does not exist., One pass: discover, read markers, summarize, stamp, order. Never raises., Attach fresh marker + is_active fields and order newest-first.          Recency, Full-parse summary of one transcript.      ``total_tokens`` is ``account_usage(., SessionSummary, _synthesize_summary()

### Community 26 - "Usage Payload Parsing"
Cohesion: 0.29
Nodes (4): parse_usage(), Shape the ``/api/oauth/usage`` body into an :class:`AccountUsage`. Pure.      To, Read creds, fetch, and swap in a fresh reading. Never raises.          A no-op w, ParseUsage

### Community 27 - "CLI Entry & Flags"
Cohesion: 0.22
Nodes (6): main(), mood_enabled(), Whether the footer mood face + speech bubble are shown. On by default;     ``--n, Whether the launch is just a version query (``--version``/``-V``).      Split ou, Console-script entry point: the roster, with ``cc`` enabling account usage., version_requested()

### Community 28 - "macOS Keychain Read"
Cohesion: 0.39
Nodes (3): Return the raw credentials JSON from the macOS login Keychain, or None.      A n, read_macos_keychain(), ReadMacosKeychain

### Community 30 - "Account Usage Flag"
Cohesion: 0.36
Nodes (4): account_usage_requested(), Whether to enable the account-usage block for this launch.      On when the ``cc, AccountUsageRequested, The launch-time switch for the opt-in account-usage block.

### Community 31 - "Fetch Usage Endpoint"
Cohesion: 0.39
Nodes (3): fetch_usage_blob(), GET the usage endpoint with the OAuth token. Returns the JSON, or None.      Sen, FetchUsageBlob

### Community 32 - "Usage Test Doubles"
Cohesion: 0.25
Nodes (3): _FakeResponse, Tests for cc_token_tracker.usage: the opt-in account-level usage feature.  These, Minimal stand-in for an urlopen response/context manager.

### Community 38 - "Usage Enabled Flag"
Cohesion: 0.50
Nodes (3): Whether the opt-in account-usage feature is switched on.      True only when :da, usage_enabled(), UsageEnabled

### Community 40 - "CI Workflow"
Cohesion: 0.67
Nodes (3): CI Workflow, Lint Job (ruff check), Test Job (pytest matrix)

### Community 41 - "OAuth Token & Account Usage"
Cohesion: 0.67
Nodes (3): macOS Keychain OAuth Fallback, Account-level Usage (tokey cc), OAuth Token Read (credentials/Keychain)

## Knowledge Gaps
- **16 isolated node(s):** `tokey`, `Lint Job (ruff check)`, `Test Job (pytest matrix)`, `Account-level Usage (tokey cc)`, `Live Session Tracking (tokey-hook)` (+11 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SessionSummary` connect `Session Summary Assembly` to `Account Usage Rendering`, `Aphorism Pool Vetting`, `Session Summaries & Roster`, `Markers & Hook Liveness`, `Roster Rendering`, `Footer Integration Tests`, `Mood Rotation Tests`, `Speech Bubble Tests`, `Liveness Classification`, `Mood Mascot Footer`, `Mood Face Tests`, `Context Gauge Row`, `Account Usage Flag`?**
  _High betweenness centrality (0.184) - this node is a cross-community bridge._
- **Why does `summarize_session()` connect `Session Summaries & Roster` to `Transcript Parsing`, `Transcript Reading`, `Context Estimation`, `Turn Segmentation`, `Recent Entries & Turn Cost`, `Per-turn Cost Tests`, `Session Summary Assembly`?**
  _High betweenness centrality (0.145) - this node is a cross-community bridge._
- **Why does `TranscriptRecord` connect `Transcript Parsing` to `Module & Test Files`, `Display Frame Computation`, `Transcript Reading`, `Context Estimation`, `Display Run Loop`, `Cost Row Rendering Tests`, `Turn Segmentation`, `Per-turn Cost Tests`?**
  _High betweenness centrality (0.128) - this node is a cross-community bridge._
- **Are the 24 inferred relationships involving `SessionSummary` (e.g. with `RosterView` and `MarkerInfo`) actually correct?**
  _`SessionSummary` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `TranscriptRecord` (e.g. with `MessageCost` and `SessionAccounting`) actually correct?**
  _`TranscriptRecord` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `parse_line()` (e.g. with `read_transcript()` and `assistant_record()`) actually correct?**
  _`parse_line()` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 36 inferred relationships involving `read_result()` (e.g. with `ReadResult` and `.test_happy_multi_turn()`) actually correct?**
  _`read_result()` has 36 INFERRED edges - model-reasoned connections that need verification._