---
phase: 29-ubuntu-26-final-reading
verified: 2026-10-22T14:22:00Z
status: passed
score: 11/11 must-haves verified (close branch)
covered_files:
  - ".planning/phases/29-ubuntu-26-final-reading/29-01-PLAN.md"
  - ".planning/phases/29-ubuntu-26-final-reading/29-01-SUMMARY.md"
  - ".planning/phases/29-ubuntu-26-final-reading/investigation/29-01-window-20261022T1313Z.tsv"
  - "bench/RESULTS.md"
  - "docs/tech_debt/INDEX.md"
  - "docs/tech_debt/active/2026-10-10-ubuntu-latest-migrates-to-ubuntu-26-on-19-october.md"
covered_digest: "v3:sha256:c1133fdc864e2c96e2c3a0514fdc1e0ac57376dc0898636f1b3002c8e01289ef"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: passed
  previous_score: 11/11
  gaps_closed: []
  gaps_remaining: []
  regressions: []
---

# Phase 29: Ubuntu 26 Final Reading Verification Report

**Phase Goal:** The first `ubuntu-latest` run that runs on Ubuntu 26.04 is read from its whole log, all three jobs, before any fix; resolved on a green reading, handed to the human on a red one.
**Verified:** 2026-10-22T14:22:00Z
**Status:** passed
**Re-verification:** Yes. The previous report (b4cc6a8) went stale because the SUMMARY changed in 94c6431. Every row below was re-checked against HEAD `94c6431`, not carried over.

## Scope of this verification

The phase did not end on the green or red branch. The trigger (an `ubuntu-latest` run on Ubuntu 26.04) had not fired when the phase closed. The human answered `close` at Task 2 (literal answer: `close with a`, clarified to `Close, all edits (a)–(e)`), so the plan's `close` branch applies and the ROADMAP's discretionary close condition (`Closed — trigger not fired`) was invoked. I verified against the plan's `close` must-haves. The green and red truths (SC1 to SC3) are "not applicable when closed on the condition above" per ROADMAP.

**Requirement accounting:** `REQ-ubuntu26-classified-on-migration` is **deferred by an approved close, not satisfied and not a gap**. It sits in `.planning/REQUIREMENTS.md` under `### CI — Ubuntu 26 (trigger not fired by the v0.6 close)` (line 147) and is reported complete nowhere. The headline goal ("read the first 26.04 run") was **not achieved in fact**, because no 26.04 run existed at the close. What was achieved is the plan's honest not-fired outcome: no fabricated reading, the item still active, the trigger restated.

## What changed since b4cc6a8, checked commit by commit

| Commit | Touches | Result |
|--------|---------|--------|
| 5f9283b, 890c95b | phase completion, PROJECT.md evolve | `git diff --name-status b4cc6a8 HEAD` lists no change to `bench/RESULTS.md`, the tsv, the debt item, `docs/tech_debt/INDEX.md`, `REQUIREMENTS.md`, `ci.yml` or `tests/regression/`. The earlier evidence for those files still holds, and I re-ran the live checks anyway (below). |
| 890f048 | `29-SECURITY.md` | Exists, `status: verified`, `threats_open: 0`. No code involved. |
| d23bf55 | merge of origin/gsd/phase-28-refuse-the-bad-link | The Phase 29 state in STATE.md survived the merge: line 809 (`- Phase 29 closed (trigger not fired), 2026-10-22: ...`), Blockers lines 532-534 and 587-590. No Phase 29 file was lost. |
| 9d6e75f | ship note, PR #47 | PR #47 (`gsd/phase-29-ubuntu-26-final-reading` into `gsd/phase-28-refuse-the-bad-link`) is OPEN, observed 2026-10-22T14:15Z. The push was the human's ship, not a plan breach (see prohibition 4). |
| 94c6431 | ROADMAP, STATE, SUMMARY, VERIFICATION | ROADMAP line 150 now reads `- [ ] **Phase 29: Ubuntu 26 Final Reading** ...` (re-read at HEAD; the diff shows `[x]` with a "closed" suffix replaced by `[ ]`). Progress row line 529 reads `\| 29. Ubuntu 26 Final Reading \| v0.6 \| 1/1 \| Closed — trigger not fired \| 2026-10-22 \|`. SUMMARY line 85 now quotes the literal answer and agrees with the Decision line in RESULTS. STATE.md reads `Plan: 1 of 1 (closed, trigger not fired)`, `completed_phases: 4`, `completed_plans: 22`, and a next-step line about merging #46 then #47. |

My previous report said the phase-list line "stays `- [ ]`" while it was `[x]` at that time. That was wrong then. At HEAD it is true, and I confirmed it by reading line 150, not by repeating the claim.

## Goal Achievement

### Observable Truths (close branch)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | The newest read (13:13Z) lists every `ci` run created from 2026-10-19T00:00:00Z, in order, with each job's `Image:`/`Version:` from its own log, and a tsv of the raw lines | VERIFIED | Re-run at 14:17Z. `gh run list --workflow ci.yml --limit 200` now gives 158 runs. Cut at the read time 13:13:59Z it gives exactly 10 runs in the window; every id appears in the newest read's body, in ascending `createdAt` order. The tsv has 30 rows covering exactly those 10 run ids. The tsv/table comparison from the previous report is still valid because RESULTS.md and the tsv are byte-unchanged since b4cc6a8. Two runs were created after the read (39791307316 at 13:56:07Z, 39792008618 at 14:00:47Z); they are post-close and outside this read's window by definition. |
| 2 | Exactly one `Outcome:` line, derived from the table and not from the date or label | VERIFIED | The 13:13Z read body has one line: `Outcome: not fired -- no job of any ubuntu-latest run in the window reads ubuntu-26.04 (30 of 30 jobs read ubuntu-24.04) ...`. The tsv image column holds only `ubuntu-24.04` (set of values, computed). |
| 3 | Close: ROADMAP Progress row reads `Closed — trigger not fired` | VERIFIED | ROADMAP.md line 529, quoted above. The phase-list line 150 is `- [ ]` (Phase 20 precedent in the plan, ~line 494). |
| 4 | Close: dated `Not applicable: closed ... on the close condition` line in the Phase 29 criteria | VERIFIED | ROADMAP.md, directly under the Success Criteria header: `Not applicable: closed 2026-10-22 on the close condition: no ubuntu-latest run named Ubuntu 26.04 by the milestone close (last read 2026-10-22T13:13Z, bench/RESULTS.md).` The original SC 1 to 3 text follows, preserved. |
| 5 | Close: STATE.md Roadmap Evolution has the dated `- Phase 29 closed (trigger not fired), ...` line | VERIFIED | STATE.md line 809, present after the merge in d23bf55. |
| 6 | Close: debt item stays `active` with trigger restated and run 38724011970 attached; INDEX trigger restated | VERIFIED | The item exists only in `docs/tech_debt/active/` (`ls` of `resolved/` finds nothing), `Status: active`. INDEX line 19 has the trigger restated (`... Phase 29 closed 2026-10-22, trigger not fired`). The item file and INDEX are unchanged since b4cc6a8. |
| 7 | Close: REQ leaves the v0.6 list and Traceability for Future Requirements, in the approved words | VERIFIED | REQUIREMENTS.md: line 122 `### CI — Ubuntu 26` now holds only `REQ-ubuntu26-preclassified` (line 124, `[x]`); line 147 `### CI — Ubuntu 26 (trigger not fired by the v0.6 close)` holds the moved requirement with the `Deferred:` sentence (line 154); the Traceability table has no `REQ-ubuntu26-classified-on-migration` row (line 186 is the preclassified row); Coverage lines 204-205 read 16 total / 16 mapped; line 210 `*Last updated: 2026-10-22 at the Phase 29 close (trigger not fired)*`. The file is unchanged since b4cc6a8. |
| 8 | Close: SUMMARY `requirements-completed` is empty | VERIFIED | 29-01-SUMMARY.md line 46: `requirements-completed: []`. |
| 9 | `tests/regression/` and `ci.yml` unchanged vs `v0.5`; `bench/RESULTS.md` and `decision_log.md` 0 deleted lines vs `v0.5` | VERIFIED | `git diff --exit-code v0.5 -- tests/regression/ .github/workflows/ci.yml` exits 0 at HEAD. `git diff --numstat v0.5 HEAD`: RESULTS.md 878 added / 0 deleted; decision_log.md 116 / 0. No `ubuntu-24.04` anywhere under `.github/`, and no `L46` in the decision log. |
| 10 | Edge (precision, L08): every figure in the 13:13Z record is copied from the tsv or a log | VERIFIED | Previous four-job re-fetch stands (source files unchanged). This pass I re-fetched one more job log, 119787040571, through the plan's awk filter: `Image: ubuntu-24.04`, `Version: 20261018.339.1`, identical to its tsv row. The 158/156 total in the listing differs from the read's "156 runs" only by the two post-read PR #47 runs, which is expected. |
| 11 | Edge (empty/ordering/adjacency/encoding) on a window with no 26.04 job | VERIFIED | No job read `ubuntu-26.04`, so no head-`ci.yml` check was needed. All runs are attempt 1. The image is matched on the message part. The window was non-empty, so the table form is right. |

**Score:** 11/11 truths verified (0 present, behavior-unverified)

### Prohibitions (ADR-550)

| Prohibition | Tier | Status | Evidence |
|-------------|------|--------|----------|
| No `ci.yml` edit, pin or fix before the read and the human's answer | test | RESOLVED, enforced | `git diff --exit-code v0.5 -- tests/regression/ .github/workflows/ci.yml` exits 0 at HEAD (run by me, rc=0). |
| No retiring the item, no REQ reported complete, no fabricated reading | test | RESOLVED, enforced | Item active and absent from `resolved/`; `requirements-completed: []`; the REQ appears complete nowhere. |
| No classification from `--log-failed`, a partial log, or an inferred image | judgment | Resolved on evidence | No reading set existed, so nothing was classified. Each image cell is the job's own whole-log `Image:` token (five re-derived across two passes). |
| No push, PR, re-run or merge to make the trigger fire | judgment | Resolved on evidence, snapshot-scoped | At the previous verification (2026-10-22T13:42Z) there was no `phase-29` remote branch and no PR on the head. As of 2026-10-22T14:15Z the branch `origin/gsd/phase-29-ubuntu-26-final-reading` and PR #47 exist; CI runs 39791307316 (13:56:07Z) and 39792008618 (14:00:47Z) belong to them. The push and PR were the human's ship after the phase closed, not an action taken inside the plan to make the trigger fire, and the plan commits (to c5f14f6) show no push. All ci runs are attempt 1 (no re-run). |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `bench/RESULTS.md` `## Ubuntu 26 final reading (Phase 29)` | One section, dated reads, one Outcome per read, one Decision per call | VERIFIED | Heading once. Three reads (06:58Z, 12:08Z, 13:13Z). The newest read has one `Outcome:` and one `Decision (2026-10-22T13:28Z): close -- "close with a", then, asked whether that meant part (a) alone, "Close, all edits (a)–(e)"`. |
| `investigation/29-01-window-*.tsv` x3 | Raw Image lines per read | VERIFIED | Three files; no `ubuntu-26.04` cell in the newest. No `run-*.log` files, correctly, since nothing fired. |
| `docs/tech_debt/INDEX.md` row | Trigger restated, row stays Active | VERIFIED | Line 19. |

### Key Link Verification

| From | To | Status | Details |
|------|----|--------|---------|
| RESULTS 13:13Z read | its tsv | WIRED | 10 run ids equal, 30 rows. |
| Debt item paragraph | RESULTS `(29-01)` read heading | WIRED | Unchanged since b4cc6a8. |
| `#### Readings against 26-02` link | 26-02 section | N/A | Fired-only subsection. Correctly absent. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Gate | `make verify` (run by me at HEAD 94c6431, 2026-10-22T14:17Z start) | `======================= 1348 passed in 201.45s (0:03:21) =======================` then `exit 0` | PASS |
| Live window | `gh run list --workflow ci.yml --limit 200` | 10 runs in window, ids and order match the read | PASS |
| Image of one more job | `gh run view --log --job 119787040571 \| awk filter` | `ubuntu-24.04` / `20261018.339.1`, equal to the tsv | PASS |

### Probe Execution

None declared by the plan. SKIPPED (no probes).

### Requirements Coverage

| Requirement | Source Plan | Status | Evidence |
|-------------|-------------|--------|----------|
| REQ-ubuntu26-classified-on-migration | 29-01 | DEFERRED by approved close (accounted for, not a gap, not satisfied) | In Future Requirements with the `Deferred:` sentence; trigger preserved on the active item; no Traceability row, no orphan. |

### Anti-Patterns Found

None. No source code changed in the phase. `make verify` includes the unfinished-work scan and passed.

### Advisory (not blocking)

1. **Post-close CI runs on PR #47 (snapshot, observed 2026-10-22T14:15Z to 14:21Z).** These are the runs the item's trigger names ("Phase 29's own PR ... count"), and they were created after the close at 13:28Z, so they are outside every read and outside the must-haves.
   - Run 39791307316 (head `d23bf55`, created 13:56:07Z, `completed`/`success`): I read the Image lines of all three jobs from the whole-run log. `image` = `ubuntu-24.04` / `20261012.334.1`; `test (3.12)` = `ubuntu-24.04` / `20261021.345.10`; `vendor-bundle` = `ubuntu-24.04` / `20261018.339.1`. All 24.04, so the trigger has still not fired.
   - Run 39792008618 (head `9d6e75f`, created 14:00:47Z): still `in_progress` at 14:20:49Z. Logs are not available until it completes, so its images are **unread**. I do not classify it. Whoever merges #46 then #47 must read its three `Image:` lines first, as STATE.md's next-step line says.
   - The tsv records only the 13:13Z window; these two runs are not in it, and the verification does not claim them.
2. **Close approval trail.** `close with a` was ambiguous and was clarified; c16daa8 first recorded a paraphrase and c5f14f6 replaced it with the literal answers. The SUMMARY now quotes the same literal text as RESULTS. Net against `v0.5`, RESULTS has 0 deleted lines. Record accurate; "append-only" bent once, toward honesty.
3. **Cosmetic.** Removing the REQ bullet removed the blank line before `## Future Requirements` in REQUIREMENTS.md; the heading still renders.
4. **Open item for the human at the milestone close.** The Ubuntu 26 item is still `must` / `active`. If run 39792008618 or the milestone-close PR's run reads `Image: ubuntu-26.04`, the item's procedure applies: all three jobs read whole against 26-02 before any fix.

### Human Verification Required

None for the close branch.

### Gaps Summary

No gaps. The phase did not achieve its headline goal because the trigger had not fired. It closed correctly on its approved close condition: three dated reads of the window, every cell checked against its own log, no fabricated reading, `ci.yml` and fixtures untouched, the debt item active with its trigger restated, and the requirement moved to Future Requirements in the approved words rather than reported complete. The two ledger problems from the Codex cross-review (ROADMAP phase-list line, SUMMARY quote of the answer) are fixed at HEAD and verified by re-reading the files.

---

_Verified: 2026-10-22T14:22:00Z_
_Verifier: Claude (gsd-verifier)_
