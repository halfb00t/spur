---
phase: 29-ubuntu-26-final-reading
verified: 2026-10-22T13:42:45Z
status: passed
score: 11/11 must-haves verified (close branch)
covered_files:
  - ".planning/phases/29-ubuntu-26-final-reading/29-01-PLAN.md"
  - ".planning/phases/29-ubuntu-26-final-reading/29-01-SUMMARY.md"
  - ".planning/phases/29-ubuntu-26-final-reading/investigation/29-01-window-20261022T1313Z.tsv"
  - "bench/RESULTS.md"
  - "docs/tech_debt/INDEX.md"
  - "docs/tech_debt/active/2026-10-10-ubuntu-latest-migrates-to-ubuntu-26-on-19-october.md"
covered_digest: "v3:sha256:c0b8027f24c0c1791e3981b1037669d7a70c2956d0dede8663c096f304ef4a2b"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 29: Ubuntu 26 Final Reading Verification Report

**Phase Goal:** The first `ubuntu-latest` run that runs on Ubuntu 26.04 is read from its whole log, all three jobs, before any fix; resolved on a green reading, handed to the human on a red one.
**Verified:** 2026-10-22T14:10:00Z
**Status:** passed
**Re-verification:** No, initial verification

## Scope of this verification

The phase did not end on the green or red branch. The trigger (an `ubuntu-latest` run on Ubuntu 26.04) has not fired. The human answered `close` at Task 2, so the plan's `close` branch applies, and the ROADMAP's discretionary close condition (`Closed — trigger not fired`) was invoked. I verified against the plan's `close` must-haves. The green and red truths (SC1 to SC3) are "not applicable when closed on the condition above" per ROADMAP, and no 26.04 run exists to which they could apply.

**Requirement accounting (stated explicitly):** `REQ-ubuntu26-classified-on-migration` is **deferred by an approved close, not satisfied and not a gap**. It is accounted for in `.planning/REQUIREMENTS.md` under `### CI — Ubuntu 26 (trigger not fired by the v0.6 close)` in Future Requirements. It is not reported complete anywhere. The phase goal itself ("read the first 26.04 run") was **not achieved in fact**, because no such run exists. What was achieved is the plan's honest not-fired outcome: no fabricated reading, the item still active, the trigger restated. The ROADMAP explicitly permits this and says the requirement is "neither orphaned silently nor reported complete".

## Goal Achievement

### Observable Truths (close branch)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | The newest read (13:13Z) lists every `ci` run created from 2026-10-19T00:00:00Z, in order, with each job's `Image:`/`Version:` copied from its own log, and a tsv of the raw lines | VERIFIED | Live `gh run list --workflow ci.yml --limit 200` gives 156 runs (the read says 156) and exactly 10 in the window, same ids and `createdAt` as the table. A script compared all 10 table rows to the 30 tsv rows on run, created, event, branch, head7, attempt, conclusion and per-job image/version: identical. The ids and `createdAt` are in ascending order. Task 1's first verify script, re-run: `script1 ok 2026-10-22T13:13 ['not fired'] 10`. |
| 2 | Exactly one `Outcome:` line, derived from the table and not from the date or label | VERIFIED | One `Outcome: not fired` at RESULTS.md line 6809. All 30 tsv image cells are `ubuntu-24.04`, none `ubuntu-26.04`, so no red, green or pending rule holds. |
| 3 | Close: ROADMAP Progress row reads `Closed — trigger not fired` | VERIFIED | ROADMAP.md line 529: `\| 29. Ubuntu 26 Final Reading \| v0.6 \| 1/1 \| Closed — trigger not fired \| 2026-10-22 \|`. The phase-list line stays `- [ ]` (Phase 20 precedent in the plan). |
| 4 | Close: dated `Not applicable: closed ... on the close condition` line in the Phase 29 criteria | VERIFIED | ROADMAP.md, under the Success Criteria header: `Not applicable: closed 2026-10-22 on the close condition: no ubuntu-latest run named Ubuntu 26.04 by the milestone close (last read 2026-10-22T13:13Z, bench/RESULTS.md).` The original SC 1 to 3 text is preserved. |
| 5 | Close: STATE.md Roadmap Evolution has the dated `- Phase 29 closed (trigger not fired), ...` line | VERIFIED | STATE.md line 808. Note: STATE.md Blockers/Concerns still carries the two Ubuntu lines (see Advisory). |
| 6 | Close: debt item stays `active` with trigger restated and run 38724011970 attached; INDEX trigger restated | VERIFIED | The item is in `docs/tech_debt/active/` with `Status: active`. It is absent from `resolved/`. Its dated paragraph names the 13:13Z read heading, 10 runs, 30 of 30 jobs on 24.04, the restated trigger (`Image: ubuntu-26.04`, matched on the message, not the step column), and run 38724011970, image `20261012.163.1`, install 14.44 s. INDEX line 19 has the trigger restated (`... Phase 29 closed 2026-10-22, trigger not fired`). |
| 7 | Close: REQ leaves the v0.6 list and Traceability for Future Requirements, in the words the human approved | VERIFIED | The commit c16daa8 diff matches plan edits (a) to (e): bullet removed from `## v0.6 Requirements`, new `### CI — Ubuntu 26 (trigger not fired by the v0.6 close)` under Future Requirements with the requirement text unchanged plus the `Deferred:` sentence, Traceability row removed, Coverage 16 total / 16 mapped, last-updated line. The REQ id appears only in Future Requirements and in the coverage note. |
| 8 | Close: SUMMARY `requirements-completed` is empty | VERIFIED | 29-01-SUMMARY.md line 46: `requirements-completed: []`. The requirement is not marked complete in REQUIREMENTS.md either. |
| 9 | `tests/regression/` and `.github/workflows/ci.yml` unchanged vs `v0.5` at every commit of the plan; `bench/RESULTS.md` and `decision_log.md` 0 deleted lines vs `v0.5` | VERIFIED | `git diff --quiet v0.5 <c> -- .github/workflows/ci.yml tests/regression/` is clean for 1aeeec9, c16daa8, 128cc60 and c5f14f6 and for HEAD. `git diff --numstat v0.5 HEAD`: RESULTS.md 878 added / 0 deleted, decision_log.md 116 / 0. Also no `L46` and no `ubuntu-24.04` pin anywhere. |
| 10 | Edge (precision, L08): every figure in the 13:13Z record is copied from the tsv or a log | VERIFIED | Table vs tsv is identical. I re-fetched four whole job logs from GitHub (jobs 119787040571, 119789154418, 118579321958, 119100406167) through the plan's awk filter. Each printed `Image: ubuntu-24.04` and the exact `Version:` in its tsv row. The counts "156 runs", "10 in window", "30 rows" and "30 of 30" were each recomputed. The earlier reads' figures (8 runs/24 jobs, 10/30; versions `20261012.334.1` and `20261018.339.1`) match their tsvs. 26-02 figures are only restated in the item and match the 26-02 section. |
| 11 | Edge (empty/ordering/adjacency/encoding) on a window with no 26.04 job | VERIFIED | No run is pinned-label (no 26.04 job), so no head-`ci.yml` check is needed and none was claimed. All runs are attempt 1. The image is matched on the message part, not the step column. The window is not empty, so the table form (not the one-sentence form) is correct. |

**Score:** 11/11 truths verified (0 present, behavior-unverified)

### Prohibitions (ADR-550)

| Prohibition | Tier | Status | Evidence |
|-------------|------|--------|----------|
| No `ci.yml` edit, pin or fix before the read and the human's answer | test | RESOLVED, enforced | `git diff --exit-code v0.5 -- tests/regression/ .github/workflows/ci.yml` exits 0 at HEAD and at each plan commit. The wired check is the plan's own Task 2 and Task 3 verify (run by me). |
| No retiring the item, no REQ reported complete, no fabricated reading | test | RESOLVED, enforced | The item is active and not in `resolved/`. `requirements-completed: []`. The read commit 1aeeec9 touches only RESULTS and the tsv. I re-ran the close-branch checks (Progress row, N/A line, REQ move, Traceability row removed): `close checks ok`. |
| No classification from `--log-failed`, a partial log, or an inferred image | judgment | Resolved on evidence | No reading set exists, so there was no classification. Each image cell is the job's own whole-log `Image:` token (I re-derived four independently). `--log-failed` appears only in "not `--log-failed`" notes. All attempts are 1. The verdict is mine, not a test, but it rests on direct observation. |
| No push, PR, re-run or merge to make the trigger fire | judgment | Resolved on evidence | As of the verification snapshot (2026-10-22T13:42Z, before the ship pushed this branch and opened PR #47): no `phase-29` remote branch and no PR on the head. The newest `ci` run is still 39768296581 (Phase 28's, 2026-10-22T11:08:06Z), with no run created after it. All runs are attempt 1 (no re-run). |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `bench/RESULTS.md` `## Ubuntu 26 final reading (Phase 29)` | One section, dated reads, one Outcome per read, one Decision per call | VERIFIED | Heading at line 6697, once. Three reads (06:58Z, 12:08Z, 13:13Z), each with one `Outcome: not fired`. Decisions are `wait`, `wait` and `close`, one per read. |
| `investigation/29-01-window-*.tsv` x3 | Raw Image lines per read | VERIFIED | 24, 30 and 30 rows. No `ubuntu-26.04` in any. No `run-*.log` files, which is correct: nothing fired, so nothing to keep whole. |
| `docs/tech_debt/INDEX.md` row | Trigger restated, row stays Active | VERIFIED | Line 19, as above. |

### Key Link Verification

| From | To | Status | Details |
|------|----|--------|---------|
| RESULTS 13:13Z read | its tsv | WIRED | Every cell matches (script above). |
| Debt item paragraph | RESULTS `(29-01)` read heading | WIRED | The item names `### The ubuntu-latest window, read 2026-10-22T13:13Z (29-01)` and 26-02's heading. |
| `#### Readings against 26-02` link | 26-02 section | N/A | Fired-only subsection. Correctly absent. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Gate | `make verify` | `======================= 1348 passed in 225.78s (0:03:45) =======================` then `exit 0` (run by me at HEAD) | PASS |
| Live window | `gh run list --workflow ci.yml --limit 200 ...` | 10 runs in window, 156 total, no newer run: trigger still not fired | PASS |
| Image of four jobs | `gh run view ... --log --job ... \| awk filter` | all `ubuntu-24.04` with the recorded versions | PASS |

### Requirements Coverage

| Requirement | Source Plan | Status | Evidence |
|-------------|-------------|--------|----------|
| REQ-ubuntu26-classified-on-migration | 29-01 | DEFERRED by approved close (accounted for, not a gap, not satisfied) | Moved to Future Requirements in REQUIREMENTS.md with the `Deferred:` sentence. Trigger preserved on the active debt item. The id is in the PLAN frontmatter and in REQUIREMENTS.md. No orphans: REQUIREMENTS.md maps no other id to Phase 29, and the Traceability row was removed deliberately. |

### Anti-Patterns Found

None. No source code changed in the phase. A `TBD`/`FIXME`/`XXX` marker scan over the phase's changed files (RESULTS additions, item, INDEX, REQUIREMENTS, ROADMAP, STATE additions) found no unreferenced debt markers. `make verify` includes the unfinished-work scan and passed.

### Advisory (not blocking)

1. **Close approval trail.** The human's literal reply was `close with a`, which was ambiguous (it could mean part (a) alone). It was clarified by a follow-up question to "Close, all edits (a)–(e)". Commit c16daa8 first recorded a paraphrase in the Decision line, and c5f14f6 corrected it to the real words. That correction rewrote one line the same phase had added (1 insertion / 1 deletion in c5f14f6). Net against `v0.5`, RESULTS still has 0 deleted lines. The final record is accurate; the plan's "append-only" wording was bent once, in the direction of honesty.
2. **STATE.md Blockers/Concerns** still carries the two Ubuntu lines (`[v0.6]`, `[Phase 21]`). The SUMMARY flags this as a transition item for the orchestrator. STATE.md's header (`status: executing`, "Phase 29 execution started") is orchestrator state and is also pending the transition.
3. **Cosmetic.** Removing the REQ bullet also removed the blank line before `## Future Requirements` in REQUIREMENTS.md, so the heading now follows the preceding bullet directly. It still renders as a heading.
4. **SUMMARY gap.** The SUMMARY says Task 1's verify scripts were not re-run in the continuation. I ran the first one (passes). The commit-subject script is the plan's own; the subjects match the plan's `not fired` form.
5. **Open item for the human at the milestone close.** The Ubuntu 26 item is still `must` / `active`. The milestone-close PR and Phase 29's own PR are the likeliest first 26.04 runs; whoever lands them must read the `Image:` line of all three jobs before any fix, as the item states.

### Human Verification Required

None. The two judgment-tier prohibitions were resolved on direct observation and need no further human gate.

### Gaps Summary

No gaps. The phase did not achieve its headline goal because the trigger has not fired. It closed correctly on its approved close condition: three dated reads of the whole window, every cell checked against its own log, no fabricated reading, `ci.yml` and fixtures untouched, the debt item still active with the trigger restated, and the requirement moved to Future Requirements in the approved words rather than being reported complete.

---

_Verified: 2026-10-22T14:10:00Z_
_Verifier: Claude (gsd-verifier)_
