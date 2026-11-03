---
phase: 33-interfaces-and-parity
plan: 01
subsystem: testing
tags: [make-verify, gate-baseline, chromium, playwright, number-input, wr02, pydantic, bench]

requires:
  - phase: 32-shaft-model-and-solid
    provides: "the merged code (6800769) whose gate cost this plan reads as the phase's baseline"
provides:
  - "bench/RESULTS.md: the Phase 33 opener, the gate baseline (33-01) and the 91-token Chromium table over 37 number inputs"
  - "33-01-token-table.json: {token, blank} per probed token, the input plan 33-03 transcribes into tests/number_box_tokens.py"
  - "33-01-token-probe.py: the re-runnable Chromium/pydantic/API probe"
  - "## Decision result: the human's picks A1, B1, C1, read by 33-03, 33-06, 33-08, 33-09"
affects: [33-03, 33-06, 33-08, 33-09]

actuals:
  tokens: 155651   # chars/4 over the added lines of 78f8ec6; 37293 of the 622606 chars are not the 5394-line verify log
  tasks: 2
  commits: 1
plan_head_before: ead2a4ca45d902c7123e26f660c2de5edb4842f3
plan_head_after: 78f8ec63519f9e8743e31dbc2be65b751d36c873

tech-stack:
  added: []
  patterns:
    - "the number box is probed in the gate's own Chromium and its table, not the HTML spec, is the authority for a server rule (D-02)"
    - "inputs keyed `gear.<field>` / `shaft.<field>` in one probe page because `module` and `teeth` exist on both models"

key-files:
  created:
    - .planning/phases/33-interfaces-and-parity/investigation/33-01-verify.log
    - .planning/phases/33-interfaces-and-parity/investigation/33-01-verify-meta.log
    - .planning/phases/33-interfaces-and-parity/investigation/33-01-token-probe.py
    - .planning/phases/33-interfaces-and-parity/investigation/33-01-token-probe.log
    - .planning/phases/33-interfaces-and-parity/investigation/33-01-token-table.json
    - .planning/phases/33-interfaces-and-parity/33-01-SUMMARY.md
  modified:
    - bench/RESULTS.md

key-decisions:
  - "A1: server rule = four conditions (token != token.strip(), '_' anywhere, a leading '+', a trailing '.'), pinned as an invariant over the committed table; the 10 non-finite/overflow tokens keep their bound's or pydantic's own sentence"
  - "B1: browser proof = one #<field>=%2B<default> link per number field and mate_teeth (30 gear links in 33-03, 7 shaft links in 33-08); the full 91-token table walked in the light test"
  - "C1: the WR-02 fixing commit is 33-03's, in app.py, before the switch (33-06); refuse()/gearQuery() stay byte-identical through the phase, diffed against 6800769 in 33-09; L49 records this SC4 reading"

patterns-established:
  - "A probe table with a `held but the rule refuses` and a `blank, accepted somewhere, the rule lets it through` line is the stop-and-ask trigger; both read `none` here, so A3 never applied"

requirements-completed: [REQ-wr02-fixed, REQ-gate-cost-recorded]

coverage:
  - id: D1
    description: "A recorded `make verify` baseline on Phase 32's unmodified code (2644 passed in 229.17s), logs committed and copied into bench/RESULTS.md"
    requirement: "REQ-gate-cost-recorded"
    verification:
      - kind: other
        ref: "grep -E '^=+ [0-9]+ passed' .planning/phases/33-interfaces-and-parity/investigation/33-01-verify.log"
        status: pass
      - kind: other
        ref: "grep -cE 'exit status:? 0$' .planning/phases/33-interfaces-and-parity/investigation/33-01-verify-meta.log"
        status: pass
    human_judgment: false
  - id: D2
    description: "The number box probed in Chromium 153.0.8010.12 over 37 inputs and 91 tokens, with pydantic, /api/info and ShaftParams columns, the rule verdict and the table in JSON"
    requirement: "REQ-wr02-fixed"
    verification:
      - kind: other
        ref: ".venv/bin/python .planning/phases/33-interfaces-and-parity/investigation/33-01-token-probe.py (three summary lines printed; json has 91 tokens, 66 blank)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The human's choice of the server rule (A), the browser proof's breadth (B) and the fixing commit's place (C)"
    requirement: "REQ-wr02-fixed"
    verification: []
    human_judgment: true
    rationale: "A pick between options is a human decision (checkpoint gate blocking-human); recorded as given, nothing to auto-verify"

duration: 11min
completed: 2026-10-27
status: complete
---

# Phase 33 Plan 01: Gate baseline and the number box measured on every field Summary

**A recorded `make verify` baseline on Phase 32's code (2644 passed in 229.17s, real 230.70) and a Chromium table of 91 tokens over 37 number inputs showing the four-condition server rule matches the box on every token it can see, with the human's picks A1/B1/C1 recorded for the plans that implement them.**

## Performance

- **Duration:** 11 min (Started 2026-10-27T15:54:00Z, the baseline run's start, the first timed event of the plan; the wait for the human at the checkpoint is not counted)
- **Started:** 2026-10-27T15:54:00Z
- **Completed:** 2026-10-27
- **Tasks:** 2 (1 tracer, 1 checkpoint:decision)
- **Files modified:** 7 (1 existing, 6 created)

## Accomplishments

- Gate baseline: `make verify` on the tree byte-equal to Phase 32's merge (`6800769`) exited 0 on the 18-CPU Apple M5 Max: `2644 passed in 229.17s (0:03:49)`, `real 230.70` / `user 719.77` / `sys 723.33`, coverage TOTAL 98.22%, `Contracts: 10 kept, 0 broken.`, `gear.unchanged` green. Load 4.62 before, 7.15 after. Phase 32 read 233.83s at its close; that is history, 33-09 subtracts from this reading.
- Token probe: Chromium 153.0.8010.12 (Playwright 1.63.0 headless shell, the gate's own) over 37 inputs (29 gear + `mate_teeth` + 7 shaft) and 91 tokens; 66 tokens read back `''` on all 37 inputs, 25 are held. No token is blank on some inputs and held on others (`not uniform: none`).
- The disagreement lists the human was asked to read:
  - `held but the rule refuses: none`
  - `blank, accepted somewhere, the rule lets it through: none`
  - `blank, refused everywhere already, the rule lets it through:` `'%2022'`, `'Infinity'`, `'inf'`, `'-inf'`, `'infinity'`, `'NaN'`, `'nan'`, `'1e400'`, `'1e309'`, `'-1e309'`, `'9' * 400`, `'abc'`, `'0x10'`, `'1e'`, `'1e+'`, `'--5'`, `'1,5'`, `'- 5'`, `'-+5'`, `'0b1'`, `'5.e'`, `'.e1'`, `'1e0.5'`, `'1.5.2'`, `'1 0'`, `'1\xa00'`, `'%'`, `'\u0663'`, `'\uff12\uff12'`, `'\ufeff22\ufeff'`, `'22,5'`, `''`. Each is a 422 from pydantic or a bound already, so none builds under a blank box. Because the first two lists are empty, A3 (the stop-for-reading branch) did not apply.
- Phase 33's section opener and the empty `### Seen red once (Phase 33)` table are in bench/RESULTS.md for later plans to append to (139 lines added, 0 deleted).

## Task Commits

1. **Task 1: Tracer: the gate baseline on Phase 32's code and the number box measured over every field** - `78f8ec6` (docs)
2. **Task 2: The human picks A, B and C** - no commit of its own; the pick is this file's `## Decision result` (plan metadata commit below)

**Plan metadata:** see the `docs(33-01): complete ...` commit that adds this file (hash recorded in the orchestrator's return).

## Decision result

Picked by the human on 2026-10-27 (typed answer: "recommended", which the plan defines as A1, B1, C1). Nothing under `src/` or `tests/` was edited.

| Letter | Option id | Exact value | Date | Picked by |
|---|---|---|---|---|
| A | **A1** | The server rule is four conditions, a token is refused as written when any holds: `token != token.strip()`, `"_" in token`, `token.startswith("+")`, `token.endswith(".")`. Pinned as an invariant over the committed table (`33-01-token-table.json` transcribed into `tests/number_box_tokens.py`): no token the box blanks gets a 200 from any walked field and route, and no token the box holds is refused by the rule. The 10 non-finite and overflowing tokens (`Infinity`, `inf`, `-inf`, `infinity`, `NaN`, `nan`, `1e400`, `1e309`, `-1e309`, `'9' * 400`) are not added to the rule; they keep their bound's or pydantic's own sentence. | 2026-10-27 | the human |
| B | **B1** | One link per number field and `mate_teeth`, `#<field>=%2B<its default>` (`%2B30` for the mate), on a page whose builds never run: 30 gear links in 33-03, 7 shaft links in 33-08. The full 91-token table is walked per token over representative fields and every route in the light test, and re-probed in Chromium on every number input of the page. | 2026-10-27 | the human |
| C | **C1** | The WR-02 fixing commit is 33-03's, in `app.py`, before the part switch (33-06). `refuse()` and `gearQuery()` stay byte-identical through the phase; 33-09 diffs both against `6800769`. L49 records this reading of ROADMAP SC4. 33-09 writes the same reading beside ROADMAP criterion 4 and REQ-wr02-fixed (their own words are not rewritten). | 2026-10-27 | the human |

### Carry-forward notes for later plans

- **The empty string.** `''` is blank in the box (it is in the table's blank list) but pydantic already refuses it and the page never sends it (L44 D-06: a blank control means the default). The as-written rule must not apply to an empty value (an empty value keeps pydantic's own 422), and the table pin must treat `''` the same way: it is excluded from the "blank gets no 200" invariant's rule-side check, because the rule deliberately lets it through.
- **Box keying.** The probe keys every input as `gear.<field>` or `shaft.<field>` because `module` and `teeth` are fields of both models; a page that builds one part at a time (33-06) has no such clash, and 33-03/33-08 link names are the bare field names.
- **Rule column reading.** In the table, "Rule: refuses" means the four-condition rule refuses; "lets through" for a blanked token means pydantic or a bound is the only guard. 66 of 91 tokens are blank; the rule refuses 34 and lets 32 blanked tokens through (the 10 non-finite/overflow plus 22 malformed text tokens, all 422 already, `''` among them).

## Files Created/Modified

- `bench/RESULTS.md` - Phase 33 opener, `### The gate baseline (33-01)`, `### Tokens the number box blanks, every field (33-01)`, empty `### Seen red once (Phase 33)` table
- `.planning/phases/33-interfaces-and-parity/investigation/33-01-verify.log` - whole `/usr/bin/time -p make verify` output
- `.planning/phases/33-interfaces-and-parity/investigation/33-01-verify-meta.log` - start, end, load, HEAD, host, exit status
- `.planning/phases/33-interfaces-and-parity/investigation/33-01-token-probe.py` - the probe
- `.planning/phases/33-interfaces-and-parity/investigation/33-01-token-probe.log` - its output
- `.planning/phases/33-interfaces-and-parity/investigation/33-01-token-table.json` - 91 `{token, blank}` objects (66 blank)

## Decisions Made

A1, B1 and C1 as above; each follows the plan's recommendation, which cites 33-RESEARCH Pattern 3 for A1, `sweep()`'s measured per-link cost for B1 and Pitfall 2 (the switch needs no edit to `refuse()`/`gearQuery()`) for C1.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] The probe script sets `PLAYWRIGHT_BROWSERS_PATH` when unset**
- **Found during:** Task 1 (token probe)
- **Issue:** Playwright's default cache holds no browser on this host; the gate finds Chromium through the path the Makefile exports (line 28), so a bare run of the probe could not launch the gate's own browser.
- **Fix:** `main()` runs `os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(ROOT / ".venv" / "ms-playwright"))`, so the probe uses the same shell the gate does and an explicit environment value still wins.
- **Files modified:** `.planning/phases/33-interfaces-and-parity/investigation/33-01-token-probe.py`
- **Verification:** the probe launched Chromium 153.0.8010.12 and printed 37 inputs; ruff clean.
- **Committed in:** `78f8ec6`

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** None on the plan's scope; one line in an investigation script, nothing under `src/` or `tests/`.

## Issues Encountered

None. The baseline run was green first time (no hang), so the hang runbook was not used.

## Authentication Gates

None.

## Known Stubs

None. No file in this plan renders data; the only code is an investigation script.

## Threat Flags

None. No network endpoint, auth path or schema changed.

## Debt and ideas filed

None filed in this plan. The existing item `docs/tech_debt/active/2026-10-21-an-accepted-link-token-builds-under-a-blank-box.md` is retired by 33-03's fixing commit (D-06), not here; this plan's table also settles its "inferred, not observed in Chromium" note (the 28-01 tokens and the `+22`, `mate_teeth=%2022`, `20.`, `+2`, `2.` additions are all blank in Chromium on all 37 inputs).

## Next Phase Readiness

- 33-02 (the volume guard) is independent of these picks and can run next.
- 33-03 reads A1 (the four conditions, the table pin, `''` excluded from the rule side) and B1 (30 gear links) and lands the fix in `app.py` before the switch (C1); it transcribes `33-01-token-table.json`.
- 33-06 must leave `refuse()`/`gearQuery()` byte-identical (C1); 33-08 adds the 7 shaft links (B1); 33-09 diffs both functions against `6800769`, subtracts from the 229.17s baseline and writes the C1 reading beside SC4 and REQ-wr02-fixed.
- Shared requirement IDs (REQ-wr02-fixed and REQ-gate-cost-recorded are also declared by later plans) stay open until the last declaring plan finishes.

## Self-Check: PASSED

- Files found: all six investigation/bench files and this SUMMARY exist (`ls` and the commit's stat list).
- Commit `78f8ec6` is an ancestor of HEAD; `git rev-list --count ead2a4c..HEAD` is 1 (the measured `commits:`).
- `git status --porcelain -- src tests` prints nothing.

---
*Phase: 33-interfaces-and-parity*
*Completed: 2026-10-27*
