---
phase: 13-latency-bar
plan: 03
subsystem: testing
tags: [latency, investigation, bounded-campaign, verdict, floor-analysis]

requires:
  - phase: 13-latency-bar plan 01
    provides: "the split poller, the per-run harness, the quiet-gated session driver and the tabulator (session.py, run_experiment.py, poller.py, tabulate.py)"
  - phase: 13-latency-bar plan 02
    provides: "13-LATENCY-INVESTIGATION.md pre-registered through ## Predictions under commit 67eeefb, the --order value (concurrent,single), and the host in D-06's environment"
provides:
  - "Six pair sessions (A1, B1, C1, A2, B2, C2), twelve runs, raw samples and summaries committed (D-01, D-02, D-03)"
  - "13-LATENCY-INVESTIGATION.md complete: Results, Verdict, Recommendation, Cleanup filled by the pre-registered rule, Predictions byte-identical to the pre-registration commit"
  - "Observation 1 verdict: not reproduced in this environment (Pair A split: A1 worse, A2 not worse) -- no candidate ruled in or out"
  - "Observation 2 verdict: candidate (ii) ruled in -- the floor is real -- with the floor-analysis numbers (clock resolution, min gap, one-percentile spreads) that D-09/D-10 need to set M"
affects: [13-04, 13-05, 13-07]

actuals:
  tokens: 7200
  tasks: 2
  commits: 2
  plan_head_before: aff8f688aba95319cf073341f2a290590380106e
  plan_head_after: 48415926d10281a6d1a4400e19061be133b8ac42

tech-stack:
  added: []
  patterns:
    - "Launch each session via run_in_background, read status.json before launching the next -- never a foreground call spanning the whole quiet-wait-plus-runs window, never a busy-wait loop"
    - "Pasted tabulate.py output (--sessions, --tables) composes the write-up verbatim; derived tables (Observation 1 direction, H1 re-check, Observation 2 flip summary) are built from the pasted per-run numbers, never a second, differently-computed figure"

key-files:
  created:
    - .planning/phases/13-latency-bar/investigation/A1.status.json (+ A1-run1/A1-run2 raw files)
    - .planning/phases/13-latency-bar/investigation/B1.status.json (+ B1-run1/B1-run2 raw files)
    - .planning/phases/13-latency-bar/investigation/C1.status.json (+ C1-run1/C1-run2 raw files, two server records)
    - .planning/phases/13-latency-bar/investigation/A2.status.json (+ A2-run1/A2-run2 raw files)
    - .planning/phases/13-latency-bar/investigation/B2.status.json (+ B2-run1/B2-run2 raw files)
    - .planning/phases/13-latency-bar/investigation/C2.status.json (+ C2-run1/C2-run2 raw files, two server records)
  modified:
    - .planning/phases/13-latency-bar/13-LATENCY-INVESTIGATION.md

key-decisions:
  - "Pair A split (A1 worse, A2 not worse) triggers the pre-registered escape clause verbatim: observation 1 is 'not reproduced in this environment' rather than forcing a ruling onto Pairs B/C's own directions (B points worse, C is split) -- the rule anticipated exactly this case and was applied as written, not reinterpreted after seeing the data."
  - "Observation 2 ruled to candidate (ii) (the floor is real): three in-process runs and one poller run flip their verdict inside one percentile; candidate (iii)'s exact claim (flipping runs are exactly the below-median-n runs) was checked and found false (three below-median runs do not flip), so (iii) was not credited even though its weaker, non-exact intuition pointed the same direction."
  - "The measured smallest gap between distinct samples (2.328e-10 s) is reported as a float64-precision artifact below the declared 41.7 ns clock resolution, not as evidence for D-10's M -- the Recommendation flags that D-10's own '10x clock resolution' heuristic (417 ns) is two to three orders of magnitude smaller than the one-percentile spreads this campaign actually measured (0.090-0.296 ms), a mismatch worth the human's attention before M is fixed in L32."
  - "No debt file filed: observation 1 was not reproduced (no cause ruled in) and observation 2's cause is a harness/measurement-floor property, not a server defect -- D-17 reserves debt filing for a server-side cause ruled in, and none was."

patterns-established:
  - "Pre-registered escape clauses are applied literally even when they produce a less satisfying answer ('not reproduced') than forcing a ruling from the other pairs' data -- the whole point of pre-registration is that this decision was made before any run existed."

requirements-completed: [REQ-latency-observations-explained]

coverage:
  - id: D1
    description: "Six pair sessions (A1, B1, C1, A2, B2, C2) run one at a time, detached, each launched only after the previous session's status read done, in the pre-registered order and --order value"
    requirement: "REQ-latency-observations-explained"
    verification:
      - kind: other
        ref: "python assertion script over all six *.status.json -- printed 'six sessions done' with decisive=True for all six"
        status: pass
      - kind: other
        ref: "tabulate.py --check over all twelve run labels -- twelve 'check ok:' lines"
        status: pass
    human_judgment: false
  - id: D2
    description: "Every campaign run's started_utc is later than the pre-registration commit's time; the write-up's Predictions section is byte-identical to that commit's text"
    requirement: "REQ-latency-observations-explained"
    verification:
      - kind: other
        ref: "python datetime-comparison script -- printed 'pre-registration precedes all 12 runs'"
        status: pass
      - kind: other
        ref: "diff of the sed-extracted ## Predictions..## Results range against commit 67eeefb -- empty diff"
        status: pass
    human_judgment: false
  - id: D3
    description: "B1-run2 and B2-run2 ran teeth [180, 189]; every other campaign run ran teeth [190, 199]; C1 and C2 each have two server records files, A and B sessions have one"
    requirement: "REQ-latency-observations-explained"
    verification:
      - kind: other
        ref: "python script reading scenarios.concurrent.teeth from all twelve summary.json files, plus ls of *.server*.records.jsonl per session"
        status: pass
    human_judgment: false
  - id: D4
    description: "13-LATENCY-INVESTIGATION.md names, for observation 1 and observation 2 separately, the candidate ruled in/not-reproduced/not-separable and the measurement that ruled each other candidate out, citing run labels and file names"
    requirement: "REQ-latency-observations-explained"
    verification:
      - kind: other
        ref: "python assertion script over ## Verdict's ### Observation 1 / ### Observation 2 text -- required a ruling phrase and a run-label citation in each, printed 'write-up ok'"
        status: pass
    human_judgment: true
    rationale: "The automated check confirms a ruling phrase and a cited run label exist in each observation's verdict text; whether the stated reasoning (Pair A's split correctly triggers the pre-registered escape clause, candidate (ii) is correctly ruled in over (i)/(iii)) is sound reasoning over the pasted numbers is a judgment call a human should spot-check against the pasted tables."
  - id: D5
    description: "No src/ or bench/ change accompanies this plan's commits"
    requirement: "REQ-latency-observations-explained"
    verification:
      - kind: other
        ref: "git diff --quiet 9f26052 -- src bench"
        status: pass
    human_judgment: false

duration: ~50min
completed: 2026-10-02
status: complete
---

# Phase 13 Plan 03: Latency Investigation Campaign and Write-Up Summary

**Six pair sessions (twelve runs) run to completion and committed; the write-up rules observation
1 "not reproduced in this environment" (Pair A split between repetitions) and observation 2 to
candidate (ii) "the floor is real" (four of twenty-four verdict cells flip inside one percentile),
with no server-side cause ruled in and so no debt filed.**

## Performance

- **Duration:** ~50 min (session launches spanned 2026-10-02T02:36:53Z to 2026-10-02T03:11:43Z
  for the six campaigns themselves, roughly 35 min; the write-up, verification and SUMMARY took
  the remainder)
- **Started:** 2026-10-02T02:36:53Z (A1 launch)
- **Tasks:** 2/2 complete
- **Files touched:** 81 (80 raw investigation files across six sessions + the write-up)

## Accomplishments

### Task 1: The six pair sessions

Launched A1, B1, C1, A2, B2, C2 strictly in order, each via the Bash tool's `run_in_background`,
reading `<label>.status.json` before launching the next. No commit, `make verify`, or other
CPU-heavy command ran while any session was active.

| Session | Pair | Decisive | Quiet samples to release | Run1 exit | Run2 exit |
|---|---|---|---|---|---|
| A1 | A | yes | 3 | 0 | 0 |
| B1 | B | yes | 7 | 0 | 0 |
| C1 | C | yes | 14 | 0 | 0 |
| A2 | A | yes | 8 | 0 | 0 |
| B2 | B | yes | 26 | 0 | 0 |
| C2 | C | yes | 9 | 0 | 0 |

All six sessions were decisive (the D-05 quiet gate released on three consecutive under-1.5
samples well inside the 900 s cap). No session aborted; no retry was needed. `fleet-user` read
`Exited` and `spur-spur-1` read `Up ... (healthy)` in every session's own `docker_ps` snapshot.

After the sixth session, all four Task 1 verifies passed:
- The six-sessions-done assertion (`decisive=True` for all six).
- `tabulate.py --check` over all twelve run labels: twelve `check ok:` lines.
- The pre-registration-precedes-all-runs check: `pre-registration precedes all 12 runs`.
- `git diff --quiet 9f26052 -- src bench`, an empty `lsof` on 8001, and no session lock.

Committed in **`a24cb93`** — `docs(13-03): record the latency investigation's six pair sessions,
raw samples and summaries (D-01, D-02, D-03)` (80 files, 255,960 insertions — entirely raw
measurement data: JSONL samples, per-run summaries, session status/log, server records).

### Task 2: The write-up

Generated every table from the committed raw files (`tabulate.py --sessions`, `tabulate.py
--tables`), pasted verbatim into `13-LATENCY-INVESTIGATION.md`'s `## Environment` and `## Results`
sections. Built three derived tables directly from the pasted per-run numbers (never a second,
differently-computed figure): the Observation 1 direction table, the H1 re-check agreement table,
and the Observation 2 flip summary.

**Observation 1 — run 2 against run 1:**

| Pair | Rep 1 direction | Rep 2 direction | Pair-level reading |
|---|---|---|---|
| A | worse (A1: 1.327x -> 1.940x) | not worse (A2: 1.896x -> 1.517x) | **split** |
| B | worse (B1: 1.476x -> 2.309x, miss) | worse (B2: 1.426x -> 1.528x) | **points worse** |
| C | not worse (C1: 1.792x -> 1.396x) | worse (C2: 1.369x -> 1.534x) | **split** |

Pair A does not point worse (it is split). Per the pre-registered rule, this means observation 1
is **not reproduced in this environment** — Pairs B and C's own directions (B worse, C split)
cannot rule any of the three candidates (cache-hit sends, worker state, window at the floor) in
or out. This is an explicit, pre-registered escape clause, applied as written.

**H1 re-check:** the split poller's run-2-vs-run-1 direction agreed with the in-process direction
in all six sessions — no disagreement anywhere. H1 stays refuted (not revived).

**Observation 2 — the floor:** candidate (ii), "the floor is real," is **ruled in**. Four of
twenty-four (run, source) verdict cells flip inside one percentile: `A1-run2` (inproc, 1.940x),
`C1-run1` (inproc, 1.792x), `A2-run1` (inproc, 1.896x), and `B1-run2` (poller, 1.865x). This
refutes candidate (i) outright. Candidate (iii)'s exact claim ("the flipping runs are exactly the
below-median-n runs") was checked directly and found false — three below-median-n runs
(`B1-run2`, `C2-run2`, `B2-run2`) do not flip — so (iii) was not credited.

The clock resolution read 41.7 ns on this host, uniform across all twelve runs. The measured
smallest gap between distinct samples (2.328e-10 s) is below that declared resolution and is
reported as a float64-precision artifact, not as a basis for D-10's floor constant M. The
one-percentile spreads that actually flipped a verdict ran 0.090-0.296 ms in absolute terms —
100-700x the clock resolution, not the ~10x D-10's own text anticipates. This mismatch is flagged
in the Recommendation for the human's attention before M is fixed in L32.

**Recommendation:** D-09's first offer is D-10's absolute floor (observation 2 ruled to (ii));
observation 1 names no first offer of its own (not reproduced, no cause ruled in). No server-side
cost is named, so no `docs/tech_debt/active/` item was filed under D-17 — no server-side cause
survived to be filed.

All three Task 2 verifies passed (Predictions byte-identical to commit `67eeefb`; the write-up's
structural assertions — `status: complete`, ruling phrases plus cited run labels in both
Observation subsections, non-empty Results/Recommendation/Cleanup; `git diff --quiet 9f26052 --
src bench`).

Committed in **`4841592`** — `docs(13-03): write up the latency investigation -- observation 1
not reproduced, observation 2 ruled to the floor being real (D-04, SC1)` (1 file, 488 insertions).

## Deviations from Plan

None - plan executed exactly as written. Both tasks' acceptance criteria and verifies passed on
the first attempt; no auto-fix, no architectural question, no checkpoint was triggered.

## Authentication Gates

None.

## Known Stubs

None. The write-up's `## Results`, `## Verdict`, `## Recommendation`, and `## Cleanup` sections
are all filled with real figures pasted from the committed raw files; no placeholder text, no
hardcoded empty value, no "coming soon."

## Threat Flags

None beyond the three already named in this plan's `<threat_model>` (T-13-08, T-13-09, T-13-10),
all mitigated as the plan prescribed: sessions launched strictly in sequence with a lock and port
preflight (T-13-08); `decisive`/`state` recorded in every committed `status.json`, all six read
`done`/`decisive: true` in the Environment table (T-13-09); the Predictions-diff verify gate ran
clean against the pre-registration commit before any ruling was written (T-13-10).

## Issues Encountered

None. One minor mechanical note (not a deviation): the first `tabulate.py --check` invocation was
run from inside the `investigation/` subdirectory, where `.venv/bin/python` does not resolve as a
relative path; the immediately following invocation from the repo root succeeded and produced all
twelve `check ok:` lines. No file or state was affected by the failed first attempt.

One observation worth surfacing without over-interpreting it (D-17 forbids chasing it further this
plan): Pair A's second repetition (A2) behaved like a cache-warmed run from its very first request
(slowest build 8.44 s, close to A1-run2's cache-influenced 8.51 s) despite `session.py` starting a
fresh server process for A2 with `_EXPORTS` reset in-process. Something beyond this app's in-memory
export cache may be at play (filesystem-level caching of CAD intermediates, OS page cache for a
repeatedly-read STL, or similar) — noted in the Results section, not investigated further, since
doing so would mean reading past the server boundary this plan is scoped to leave alone (D-17).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

13-04 can now run the decisive bar session (D-07/D-08) on the unmodified `make bench.latency`
(equivalently, `session.py --mode bar`), with observation 2's floor-analysis numbers in hand
(clock resolution 41.7 ns, measured one-percentile spreads 0.090-0.296 ms) should outcome (b) be
reached and D-10's absolute floor be adopted. 13-05 only runs if D-10's threshold is chosen at
that plan's checkpoint. `investigation/`'s six sessions' raw files are the permanent record this
investigation rests on; 13-07 restores `fleet-user`'s pre-phase state once the whole phase closes
(unchanged by this plan — `fleet-user` stayed `Exited` throughout).

No blockers.

---
*Phase: 13-latency-bar*
*Completed: 2026-10-02*

## Self-Check: PASSED

- All six sessions' `.status.json` files found on disk: confirmed.
- `13-LATENCY-INVESTIGATION.md` and this `13-03-SUMMARY.md` found on disk: confirmed.
- Both task commits (`a24cb93`, `4841592`) found in `git log --oneline --all`: confirmed.
- Task 1's four `<verify>` commands (six-sessions-done assertion, twelve `tabulate.py --check`
  lines, pre-registration-precedes-all-runs, `git diff --quiet 9f26052 -- src bench` plus
  `lsof`/lock checks): all PASS, re-confirmed above in Accomplishments.
- Task 2's three `<verify>` commands (Predictions-diff against commit `67eeefb`, the
  write-up's structural assertion script, `git diff --quiet 9f26052 -- src bench`): all PASS,
  re-confirmed above in Accomplishments.
- All `<acceptance_criteria>` across both tasks confirmed met: six `done`/`decisive:true`
  sessions with the correct teeth ranges and server-records-file counts; twelve `check ok:`
  lines; the last commit's subject starting `docs(13-03): record the latency investigation's
  six pair sessions`; `status: complete`; the three `## Results` pair subsections plus
  Observation 1/H1 re-check/Observation 2; both Verdict subsections with a ruling phrase and a
  cited run label; `## Predictions` byte-identical to the pre-registration commit; no debt file
  needed (none created, reason stated above).
