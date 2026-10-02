---
phase: 13-latency-bar
plan: 02
subsystem: testing
tags: [latency, investigation, pre-registration, checkpoint, docker]

requires:
  - phase: 13-latency-bar plan 01
    provides: "the split poller, the per-run harness, the quiet-gated session driver and the tabulator (session.py, run_experiment.py, poller.py, tabulate.py), proven by one tracer run and one tracer session"
provides:
  - "D-08's run order settled by the human: harness order (concurrent, then single); --order value concurrent,single"
  - "13-LATENCY-INVESTIGATION.md through ## Predictions, committed under a pre-register subject before any campaign run (D-04)"
  - "the host in D-06's environment for the campaign: fleet-user confirmed not Up/Restarting, spur-spur-1 confirmed Up, before/after load samples on record"
affects: [13-03, 13-07]

actuals:
  tokens: 2200
  tasks: 3
  commits: 2
  plan_head_before: cd54647db09e82dd525426a141444c73d9be9ca5
  plan_head_after: 3bb28d3352be43bdbfeb1350d11840c0c6b241ad

tech-stack:
  added: []
  patterns:
    - "pre-registration commit: predictions committed under a subject containing 'pre-register' before any campaign run exists, so 13-03 can diff its running state against a fixed point (D-04)"

key-files:
  created:
    - .planning/phases/13-latency-bar/13-LATENCY-INVESTIGATION.md
  modified:
    - .planning/phases/13-latency-bar/13-02-SUMMARY.md

key-decisions:
  - "D-08's evidence conflict resolved by the human: harness order (concurrent, then single), not D-08's literal single-then-concurrent text -- matches Runs 1-8 and the decisive D-07 session; --order concurrent,single, the scripts' existing default"
  - "Host prepared per D-06: fleet-user already read Exited before the checkpoint (no docker stop needed); the human confirmed the host quiet for the campaign window ('approved')"

patterns-established:
  - "Pre-registration gate: a prediction section is written and committed before any run that could inform it exists; a later correction after data is a dated note under ## Verdict, never a rewrite of ## Predictions"

requirements-completed: [REQ-latency-observations-explained]

coverage:
  - id: D1
    description: "D-08's run order is a recorded human decision (not a planner guess), with the implied --order value"
    requirement: "REQ-latency-observations-explained"
    verification:
      - kind: other
        ref: "checkpoint:decision resume text '1' (harness-order), recorded verbatim in this SUMMARY"
        status: pass
      - kind: integration
        ref: "git diff --quiet 9f26052 -- src bench"
        status: pass
    human_judgment: false
  - id: D2
    description: "13-LATENCY-INVESTIGATION.md pre-registered through ## Predictions in 02-LATENCY-INVESTIGATION.md's shape, committed under a pre-register subject before any campaign run"
    requirement: "REQ-latency-observations-explained"
    verification:
      - kind: other
        ref: "python heading-order/prediction-row/--order/restart-looping assertion script -- printed 'pre-registration ok'"
        status: pass
      - kind: other
        ref: "git log -1 --format=%s -- 13-LATENCY-INVESTIGATION.md | grep -c pre-register -- printed 1"
        status: pass
    human_judgment: false
  - id: D3
    description: "Host prepared per D-06: fleet-user not Up/Restarting, spur-spur-1 Up, before/after load states on record, human confirmed the host quiet for the campaign window"
    requirement: "REQ-latency-observations-explained"
    verification:
      - kind: other
        ref: "test \"$(docker ps -a --filter 'name=^fleet-user$' --format '{{.Status}}' | grep -cE '^(Up|Restarting)')\" = 0 && docker ps --filter 'name=^spur-spur-1$' --format '{{.Status}}' | grep -q '^Up' -- VERIFY_PASS"
        status: pass
    human_judgment: true
    rationale: "the human's confirmation that the campaign window will stay quiet (no make verify/commit, no other CPU-heavy work) is a judgment about future behavior the harness cannot itself verify"

duration: ~5min (this continuation session, Task 3 only -- re-reads and verify checks; Tasks 1-2 ran in the prior executor session, ending at commit 67eeefb, 2026-10-02T08:05:34+06:00)
completed: 2026-10-02
status: complete
---

# Phase 13 Plan 02: Pre-Registration and Host Prep Summary

**D-08's run order settled by the human (harness order, concurrent-then-single); the investigation's
Question/Environment/Method/Predictions pre-registered and committed before any campaign run; the
host confirmed in D-06's environment (fleet-user down, spur-spur-1 up) with before/after state on
record.**

## Performance

- **Duration:** ~5 min this continuation session (Task 3 only: two re-reads of host state plus the
  automated verify); Tasks 1 and 2 ran in the prior executor session and are unaffected by this
  continuation.
- **Prior session ended:** 2026-10-02T08:05:34+06:00 (commit `67eeefb`)
- **This session:** 2026-10-02 (UTC date; exact continuation-session timestamps not separately
  logged -- see git commit times for the record)
- **Tasks:** 3/3 complete
- **Files touched this plan:** 2 (`13-LATENCY-INVESTIGATION.md` created, `13-02-SUMMARY.md`
  finalized)

## Task 1: D-08's run order (checkpoint:decision) -- RESOLVED

The human's answer, verbatim: `1` -- selecting option id `harness-order`, "Harness order:
concurrent, then single (recommended)".

Implied `--order` value: `concurrent,single` (the scripts' existing default -- no code change
was needed; both `run_experiment.py` and `session.py` already default to this order).

Verify run: `git diff --quiet 9f26052 -- src bench` exited 0 -- no `src/` or `bench/` change
exists before the investigation has run.

## Task 2: Pre-registration (`type="auto"`) -- COMPLETE

Created `.planning/phases/13-latency-bar/13-LATENCY-INVESTIGATION.md` in
`02-LATENCY-INVESTIGATION.md`'s shape, through `## Predictions` (the last four headings --
Results, Verdict, Recommendation, Cleanup -- are present with no body, for 13-03 to fill).

- **Commit:** `67eeefb` -- `docs(13-02): pre-register the latency investigation's method and
  predictions (D-04)`
- **Commit time:** `2026-10-02T08:05:34+06:00`
- Pre-registration verify script (heading order, the three prediction rows, `--order`,
  `restart-looping`) ran clean: `pre-registration ok`.
- Commit-subject verify (`git log -1 --format=%s -- 13-LATENCY-INVESTIGATION.md | grep -c
  pre-register`) printed `1`.

## Task 3: Host prep for the campaign (D-06) -- RESOLVED

**Pre-phase state** (captured before presenting the checkpoint, prior session):

```
fleet-user:   fleet-user Exited (2) 13 hours ago
spur-spur-1:  spur-spur-1 Up 35 hours (healthy)
vm.loadavg:   { 9.60 5.85 4.13 }  (1-min 9.60, 5-min 5.85, 15-min 4.13)
```

**Post-step state** (re-read this continuation session, after the human's resume):

```
fleet-user:   fleet-user Exited (2) 13 hours ago
spur-spur-1:  spur-spur-1 Up 35 hours (healthy)
vm.loadavg:   { 4.92 5.01 4.68 }  (1-min 4.92, 5-min 5.01, 15-min 4.68)
```

`fleet-user` read `Exited` both before and after -- no `docker stop` was needed; the human's
step was to confirm the host is quiet for the campaign window, not to change fleet-user's state.
`spur-spur-1` stayed `Up ... (healthy)` throughout, untouched (D-06, T-13-06).

**Human's resume text, verbatim:** `approved`

**Automated verify** (run as written in the plan):
```
test "$(docker ps -a --filter 'name=^fleet-user$' --format '{{.Status}}' | grep -cE '^(Up|Restarting)')" = 0 \
  && docker ps --filter 'name=^spur-spur-1$' --format '{{.Status}}' | grep -q '^Up'
```
Result: pass (fleet-user not Up/Restarting; spur-spur-1's status line begins with `Up`).

13-07 restores fleet-user's pre-phase state (`Exited (2)`) once the campaign window closes --
unchanged here, since fleet-user was already in that state throughout this plan.

## Deviations from Plan

None - plan executed exactly as written across both sessions.

## Authentication Gates

None.

## Known Stubs

None -- `## Results`, `## Verdict`, `## Recommendation` and `## Cleanup` in
`13-LATENCY-INVESTIGATION.md` are intentionally empty per the plan's `<action>`: 13-03 fills
them after the campaign runs. These are not stubs blocking this plan's own goal (pre-registration
before data) -- they are the next plan's deliverable.

## Threat Flags

None beyond the two already named in this plan's `<threat_model>` (T-13-05, T-13-06), both
mitigated as recorded above.

## Self-Check: PASSED

- `.planning/phases/13-latency-bar/13-LATENCY-INVESTIGATION.md` exists on disk: confirmed
  (`[ -f ... ]` exit 0, 8776 bytes).
- Commit `67eeefb` found in `git log --oneline --all`: confirmed.
- Task 1 `<verify>` (`git diff --quiet 9f26052 -- src bench`): exit 0 -- PASS.
- Task 2 `<verify>` (heading-order/prediction-row/`--order`/`restart-looping` assertion script):
  printed `pre-registration ok` -- PASS.
- Task 2 `<verify>` (commit-subject grep for `pre-register`): printed `1` -- PASS.
- Task 3 `<verify>` (fleet-user not Up/Restarting; spur-spur-1 Up): exit 0 -- PASS.
- Plan-level `<verification>`: D-08's order is the human's recorded answer (confirmed above);
  the pre-registration commit (`67eeefb`) exists and precedes the campaign (no `13-03`
  campaign-run artifacts exist yet); fleet-user is not Up or Restarting and spur-spur-1 is Up
  (confirmed above) -- all three PASS.
- All `<acceptance_criteria>` across Tasks 1-3 confirmed met (run order + `--order` recorded
  verbatim; eight headings in order with the last four empty; `## Predictions` contents present;
  `## Method` names the four scripts and the `--order` value; `## Environment` contains the D-06
  sentence verbatim; the pre-register commit's sha and time recorded; fleet-user/spur-spur-1
  status lines and load before/after recorded; the human's resume text recorded verbatim;
  spur-spur-1's post-step status line begins with `Up`).

Ready for 13-03 (the campaign: six sessions, A/B/C pairs, quiet-gated).
