---
phase: 13-latency-bar
plan: 07
subsystem: testing
tags: [latency, decision-log, tech-debt, docker, docs]

requires:
  - phase: 13-latency-bar plan 04
    provides: "the decisive bar-3 session (outcome a, Run 13 1.31x / Run 14 1.42x) on the unmodified harness"
  - phase: 13-latency-bar plan 06
    provides: "SC3's composed-worst-row session under ten concurrent builds, and the same-slot timeout-cleanup race debt it filed"
provides:
  - "L32 (amends L18): the phase's full record -- both observations' verdicts, the fleet-user environment change, the bar demonstrated (outcome a), and SC3's finding -- appended, append-only, every number cited"
  - "Dockerfile HEALTHCHECK comment's measured-p95 sentence brought current (eight -> fifteen runs), no ratio bar cited"
  - "docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md retired to resolved/ with its sha, closing the phase's must debt"
  - "fleet-user confirmed back at its pre-phase state; make verify green at phase end (910 passed)"
  - "REQ-latency-observations-explained and REQ-latency-bar-demonstrated-or-superseded marked complete -- every declaring plan (13-01/02/03/04/06/07) now summarized"
affects: [14-honest-record, PROJECT.md]

actuals:
  tokens: 4500
  tasks: 2
  commits: 3
  plan_head_before: 2601f59f6f0705d970072686603355e5edcc0956
  plan_head_after: PENDING_FINAL_COMMIT

tech-stack:
  added: []
  patterns:
    - "A file cannot carry its own commit's sha: the retiring commit writes Resolved in: as its own subject; a follow-up commit replaces the subject with the sha, in both the debt file and the INDEX cell (12-03 precedent, repeated here)"

key-files:
  created: []
  modified:
    - docs/architecture/decision_log.md
    - Dockerfile
    - docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md
    - docs/tech_debt/resolved/2026-09-23-concurrent-latency-bar-waived.md
    - docs/tech_debt/INDEX.md
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md
    - .planning/STATE.md

key-decisions:
  - "L32 appended after L31 (amends L18); the decision log's diff against 9f26052 deletes zero lines -- L18 and every earlier entry untouched"
  - "Outcome (a): the bar is demonstrated, not superseded -- bar-3's both concurrent runs read under 2.00x (1.31x, 1.42x) on the unmodified harness, so 13-05's outcome-(b) path and D-09/D-11 were never reached"
  - "The debt retired in the commit that logged L32 (6709953), with the sha recorded in a required follow-up commit (05668ef) since a file cannot name its own commit's sha"
  - "fleet-user's pre-phase state was already Exited -- the phase's own host-prep step (13-02) never started it, so 'restoring' it means confirming it is still Exited, not running docker start"

patterns-established:
  - "Decision-log amendment shape held again (L25/L31 precedent): bold-lead paragraphs, each citing a RESULTS/SUMMARY/INVESTIGATION section, a Reversibility paragraph, then Reason/Machine -- no number re-estimated"

requirements-completed: [REQ-latency-observations-explained, REQ-latency-bar-demonstrated-or-superseded]

coverage:
  - id: D1
    description: "L32 appended to decision_log.md (amends L18), append-only, every ratio it states present in bench/RESULTS.md or 13-LATENCY-INVESTIGATION.md"
    requirement: "REQ-latency-bar-demonstrated-or-superseded"
    verification:
      - kind: other
        ref: "git diff --numstat 9f26052 -- docs/architecture/decision_log.md | cut -f2 -- printed 0 (zero deleted lines)"
        status: pass
      - kind: other
        ref: "python heading-order/ratio-citation assertion script (plan Task 1 <verify>) -- printed 'L32 ok'"
        status: pass
    human_judgment: false
  - id: D2
    description: "Dockerfile HEALTHCHECK comment's measured-p95 sentence updated to the new run count (eight -> fifteen) and worst reading, no ratio bar cited, every other line unchanged"
    requirement: "REQ-latency-bar-demonstrated-or-superseded"
    verification:
      - kind: other
        ref: "git diff 9f26052 -- Dockerfile -- only '#' comment lines differ"
        status: pass
      - kind: other
        ref: "grep -c '2.00x' Dockerfile == 0; grep -c 'the eight bench/RESULTS.md' Dockerfile == 0; grep -c 'bench/RESULTS.md latency runs' Dockerfile == 1"
        status: pass
    human_judgment: false
  - id: D3
    description: "docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md retired: Status resolved, Resolution section, git mv to resolved/, INDEX row moved, sha recorded in both the file and INDEX"
    requirement: "REQ-latency-bar-demonstrated-or-superseded"
    verification:
      - kind: other
        ref: "ls docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md (absent) and docs/tech_debt/resolved/2026-09-23-concurrent-latency-bar-waived.md (present); grep -c filename docs/tech_debt/INDEX.md == 1"
        status: pass
      - kind: other
        ref: "grep '^Resolved in:' docs/tech_debt/resolved/2026-09-23-concurrent-latency-bar-waived.md matches the INDEX cell's sha (6709953) and the L32 commit"
        status: pass
    human_judgment: false
  - id: D4
    description: "fleet-user returned to its pre-phase state (13-02: Exited); spur-spur-1 still Up; src/ and the regression fixture unchanged since 9f26052; make verify green at phase end"
    requirement: "REQ-latency-bar-demonstrated-or-superseded"
    verification:
      - kind: other
        ref: "docker ps -a --filter name=^fleet-user$ (Exited); docker ps --filter name=^spur-spur-1$ (Up); lsof -nP -iTCP:8001 -sTCP:LISTEN -t (empty); git diff --quiet 9f26052 -- src tests/regression/pre_v0_2.json (exit 0)"
        status: pass
      - kind: other
        ref: "make verify -- 910 passed in 212.76s"
        status: pass
    human_judgment: true
    rationale: "Task 2 is a checkpoint:human-verify (gate=blocking) by plan design -- the human confirms the end state and the resume text is recorded verbatim, not auto-approved"

duration: ~25min (continuation session, Task 2 and plan close-out only; Task 1 ran in a prior executor session ending at commit 05668ef)
completed: 2026-10-02
status: complete
---

# Phase 13 Plan 07: The Phase's Record — L32, Dockerfile, Debt Retirement, Host Restored Summary

**L32 appended to the decision log (amends L18) recording the bar demonstrated outright (bar-3: 1.31x/1.42x, outcome a) and SC3's composed-row finding; the Dockerfile's measured-p95 comment and the 2026-09-23 "waived, not demonstrated" debt both brought current and retired in the same commit; fleet-user confirmed back at its pre-phase Exited state and `make verify` green (910 passed) to close out Phase 13.**

## Performance

- **Duration:** ~25 min this continuation session (Task 2's checkpoint resolution and the plan's
  close-out: SUMMARY, requirements traceability, STATE/ROADMAP, final commit). Task 1 (L32,
  Dockerfile, debt retirement, sha follow-up) ran in a prior executor session, ending at commit
  `05668ef`.
- **Tasks:** 2/2 complete
- **Files modified this plan:** 8 (`docs/architecture/decision_log.md`, `Dockerfile`,
  `docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md` →
  `docs/tech_debt/resolved/2026-09-23-concurrent-latency-bar-waived.md`,
  `docs/tech_debt/INDEX.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`,
  `.planning/STATE.md`, this SUMMARY)

## Accomplishments
- `## L32 — The concurrent latency bar, demonstrated on the harness as it stands (amends L18)`
  appended after L31 — both observations' verdicts, the fleet-user environment change (D-06),
  the bar-3 demonstration (outcome a), SC3's composed-worst-row finding, Reversibility, Reason
  and Machine, every number cited to `bench/RESULTS.md` or `13-LATENCY-INVESTIGATION.md`.
- Dockerfile's `HEALTHCHECK` comment sentence updated: run count "eight" → "fifteen" (Runs 1-8,
  the three bar sessions bar-1/2/3, the SC3 run); worst reading unchanged (2.3 ms pre-L19,
  1.3 ms post-L19); no ratio bar cited; every other line, including the directive itself,
  unchanged.
- `docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md` retired: `Status: resolved`,
  a `## Resolution (2026-10-02)` section with the measured numbers, `git mv`'d to
  `docs/tech_debt/resolved/`, INDEX row moved to the Resolved table; the retiring commit's
  sha (`6709953`) recorded in a required follow-up commit (`05668ef`) since the file could not
  carry its own commit's sha at retirement time.
- Phase's last plan: `REQ-latency-observations-explained` and
  `REQ-latency-bar-demonstrated-or-superseded` marked complete in `REQUIREMENTS.md` (checkbox
  and traceability table) — `gsd_run query requirements.ready-ids` confirmed both ready before
  marking (every declaring plan — 13-01/02/03/04/06/07 — already summarized; 13-05 was not
  executed, correctly, since outcome (a) made it moot).
- Host confirmed at its pre-phase state and `make verify` run green to close the phase (below).

## Task Commits

Each task was committed atomically:

1. **Task 1: Append L32, update the Dockerfile sentence, retire the debt, record its sha** —
   `6709953` (docs: L32 + Dockerfile comment + debt retirement, one commit) and `05668ef`
   (docs: sha follow-up) — both landed in the prior executor session.
2. **Task 2: The human returns fleet-user to its pre-phase state; the phase's end state is
   confirmed** — `checkpoint:human-verify`, no code change; resolved this session (below).

**Plan metadata:** committed below (this SUMMARY, `.planning/STATE.md`, `.planning/ROADMAP.md`,
`.planning/REQUIREMENTS.md`).

## Task 2: Host restored, end state confirmed (`checkpoint:human-verify`, `gate=blocking`) — RESOLVED

**fleet-user, before the phase** (from `13-02-SUMMARY.md`): `fleet-user Exited (2) 13 hours ago`.
13-02's own host-prep step found fleet-user already `Exited` before the campaign started — no
`docker stop` was ever run on it this phase, so there is nothing for 13-07 to reverse; "restoring"
it means confirming it is still `Exited`, not invoking `docker start`.

**fleet-user, read now** (before presenting the checkpoint, this session):
```
fleet-user:   fleet-user Exited (2) 20 hours ago
spur-spur-1:  spur-spur-1 Up 42 hours (healthy)
```
Same kind as the pre-phase reading (`Exited`/`Up`) — only the elapsed-time text differs, as
expected of two reads of an unchanged container state taken hours apart. Per the plan's own
rule ("If 13-02 recorded fleet-user as Up or Restarting... run docker start... If it was
already Exited then, leave it"), no action was taken.

**Port 8001:** `lsof -nP -iTCP:8001 -sTCP:LISTEN -t` — no listener (exit 1, empty output).

**src/ and fixture diff since `9f26052`:** `git diff --stat 9f26052 -- src
tests/regression/pre_v0_2.json` — empty. No `src/` or fixture change exists anywhere in
Phase 13.

**`make verify`, run once this session** (no session running, Bash timeout 600000 ms):
```
Contracts: 5 kept, 0 broken.
============================= test session starts ==============================
...
======================= 910 passed in 212.76s (0:03:32) ========================
```
Green — no failures, same 910-test count the plan's prior self-check (221.90 s run) also saw.

**Automated `<verify>` (run exactly as the plan Task 2 specifies):**
```
git diff --quiet 9f26052 -- src tests/regression/pre_v0_2.json \
  && test -z "$(lsof -nP -iTCP:8001 -sTCP:LISTEN -t)" \
  && docker ps --filter 'name=^spur-spur-1$' --format '{{.Status}}' | grep -q '^Up'
```
Result: pass (exit 0) — no src/fixture change, no listener on 8001, spur-spur-1's status
line begins with `Up`.

**Human's resume text, verbatim:** `approved`.

**SC4: met.** The debt retired (`Status: resolved`, `Resolved in: 6709953`, matching the INDEX
cell and the L32 commit); the active path no longer exists; D-11's close path (debt stays
active with a new `Revisit when:`) does not apply — outcome (a) was demonstrated.

## Files Created/Modified
- `docs/architecture/decision_log.md` — `## L32` appended after `## L31` (90 insertions, 0
  deletions against `9f26052`); L18 and every earlier entry untouched.
- `Dockerfile` — the HEALTHCHECK comment's measured-p95 sentence updated (run count, same worst
  reading); the `HEALTHCHECK` directive and every non-comment line unchanged.
- `docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md` → `git mv`'d to
  `docs/tech_debt/resolved/2026-09-23-concurrent-latency-bar-waived.md` — `Status: resolved`,
  `Resolved in: 6709953`, `## Resolution (2026-10-02)` section added.
- `docs/tech_debt/INDEX.md` — the Active row deleted, a Resolved row added (`6709953` — see the
  file's own `Resolved in:` field).
- `.planning/REQUIREMENTS.md` — both Phase 13 requirement checkboxes and traceability rows
  flipped to complete (`requirements.mark-complete`, verified ready first via
  `requirements.ready-ids`).
- `.planning/ROADMAP.md` — Phase 13's progress row (6/7 → 7/7 once this plan's own checkbox and
  SUMMARY land) and its Wave 7 plan checkbox, via `roadmap.update-plan-progress`.
- `.planning/STATE.md` — position, decisions, session, and performance metrics updated below.

## Decisions Made
- L32 amends L18 by append (D-12): the decision log's diff against `9f26052` deletes zero
  lines; L18's own text is untouched.
- Outcome (a) taken, not (b): bar-3's both concurrent runs read under 2.00x on the unmodified
  harness, so 13-05 (outcome (b) only) correctly never executed and D-09/D-11 were never reached
  — confirmed again this session by re-reading `13-04-SUMMARY.md`/`13-06-SUMMARY.md`'s outcomes
  before marking requirements complete.
- The debt's retiring commit (`6709953`) could not carry its own sha, so a required follow-up
  commit (`05668ef`) replaced the subject placeholder with the sha in both the debt file and
  the INDEX cell — the project's standing subject-then-sha precedent (09-03/12-03), applied
  again here.
- fleet-user's "restoration" is a confirmation, not an action: 13-02 found it already `Exited`
  before the phase started anything, so the phase never changed its state and there is nothing
  to reverse.

## Deviations from Plan

None — plan executed exactly as written across both sessions. Task 1's work (L32, Dockerfile,
debt retirement, sha follow-up) is unchanged from the prior session; this session resolved
Task 2 and closed out the plan per the resume instructions.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

Phase 13 is complete: both of its requirements (`REQ-latency-observations-explained`,
`REQ-latency-bar-demonstrated-or-superseded`) are marked complete, every must-severity debt the
phase was responsible for either retired (`2026-09-23-concurrent-latency-bar-waived.md`) or
newly filed with its own trigger (`2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md`,
left open — not this plan's debt to close). `make verify` is green (910 passed) and the host is
back at its pre-phase state.

Noted for the phase transition (not this plan, per the plan's own `<output>` note):
`PROJECT.md`'s L18 row needs its Outcome column updated (D-12), and the phase lands through
`make pr.land PR=N` (L22/L25/D-18) — both outside this plan's file list.

---
*Phase: 13-latency-bar*
*Completed: 2026-10-02*
