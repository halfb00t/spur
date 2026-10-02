---
phase: 13-latency-bar
verified: 2026-10-02T00:00:00Z
status: passed
score: 4/4 must-haves verified
covered_files:
  - ".planning/phases/13-latency-bar/13-01-PLAN.md"
  - ".planning/phases/13-latency-bar/13-01-SUMMARY.md"
  - ".planning/phases/13-latency-bar/13-02-PLAN.md"
  - ".planning/phases/13-latency-bar/13-02-SUMMARY.md"
  - ".planning/phases/13-latency-bar/13-03-PLAN.md"
  - ".planning/phases/13-latency-bar/13-03-SUMMARY.md"
  - ".planning/phases/13-latency-bar/13-04-PLAN.md"
  - ".planning/phases/13-latency-bar/13-04-SUMMARY.md"
  - ".planning/phases/13-latency-bar/13-05-PLAN.md"
  - ".planning/phases/13-latency-bar/13-05-SUMMARY.md"
  - ".planning/phases/13-latency-bar/13-06-PLAN.md"
  - ".planning/phases/13-latency-bar/13-06-SUMMARY.md"
  - ".planning/phases/13-latency-bar/13-07-PLAN.md"
  - ".planning/phases/13-latency-bar/13-07-SUMMARY.md"
  - "Dockerfile"
  - "bench/RESULTS.md"
  - "bench/latency.py"
  - "docs/architecture/decision_log.md"
  - "docs/tech_debt/INDEX.md"
  - "docs/tech_debt/active/2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md"
  - "docs/tech_debt/resolved/2026-09-23-concurrent-latency-bar-waived.md"
  - "tests/test_bench.py"
covered_digest: "v2:sha256:52106be4bccb022dd8e877db0e2f0470a20b5c7d389885f47029b9f902bef842"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 13: Latency Bar Verification Report

**Phase Goal:** The ten-concurrent latency bar is either demonstrated on both runs of one
session or superseded by a logged decision with the measurement — the two previously
unexplained observations each get a cause ruled in or out, and the `must` debt file
retires.
**Verified:** 2026-10-02
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC1 — The write-up names, for each of the two observations, the candidate ruled in/out, with no `src`/`bench` change | ✓ VERIFIED | `13-LATENCY-INVESTIGATION.md` `## Verdict`: Obs. 1 "not reproduced in this environment" (Pair A split, pre-registered escape clause fires, D-06); Obs. 2 ruled to candidate (ii) "the floor is real" (4/24 verdict cells flip inside one percentile). `git diff --quiet 9f26052 34d9ef4 -- src bench` exits 0 — no `src`/`bench` touched through the write-up commit. |
| 2 | SC2 — `scenario_concurrent` ≤ 2.00× idle p95 on both runs of one decisive session on the unmodified harness, OR superseded by a logged `Lxx` | ✓ VERIFIED | `bench/RESULTS.md` "### Bar session bar-3 (Runs 13-14)": decisive (D-05, three samples <1.5), Run 13 = 1.31×, Run 14 = 1.42×, both ≤1.99×. "**Outcome (a): demonstrated.**" Commit `fe17199`→`e15437e`. Two prior attempts (bar-1, bar-2) correctly recorded non-decisive, not counted, per D-05. |
| 3 | SC3 — Composed worst row (29.42 s) measured once under ten concurrent builds, recorded whatever it reads | ✓ VERIFIED | `bench/RESULTS.md` "### Composed worst row under ten concurrent builds (Phase 13)": run aborted after all ten requests sent (0/10 served, 6/10 refused, 4/10 timed out, 2 of those crashed with an undocumented `500`); recorded from server records (`sc3.server1.records.jsonl`) since the client-side summary never materialized; no plausible ratio invented for the missing p95 (L08 honored). Human checkpoint `1.` ("record it") authorized this per D-16 ("whatever it reads"). Defect filed as `must`-severity debt with a named trigger. |
| 4 | SC4 — Debt file retires (status/sha/mv/INDEX), L18 untouched + new `Lxx` appended, Dockerfile `HEALTHCHECK` comment says what was measured | ✓ VERIFIED | `docs/tech_debt/resolved/2026-09-23-concurrent-latency-bar-waived.md`: `Status: resolved`, `Resolved in: 6709953`, `## Resolution (2026-10-02)` section, file lives only under `resolved/` (confirmed absent from `active/`). `docs/tech_debt/INDEX.md` line 48 lists it under the Resolved table. `docs/architecture/decision_log.md`: `git diff 9f26052 HEAD` on this file deletes 0 lines (append-only); `## L32 — The concurrent latency bar, demonstrated on the harness as it stands (amends L18)` appended after L31, cites 13-LATENCY-INVESTIGATION.md and bench/RESULTS.md sections throughout, no re-estimated numbers. `Dockerfile` lines 39-50: comment updated to "fifteen bench/RESULTS.md latency runs" (was "eight"), cites no ratio bar — see Anti-Patterns for a minor precision nit on this count. |

**Score:** 4/4 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `.planning/phases/13-latency-bar/13-LATENCY-INVESTIGATION.md` | Investigation write-up, `02-*`-shaped, status complete | ✓ VERIFIED | All required headings present (`## Question` … `## Cleanup`); 634 lines; `## Verdict` names a ruling for both observations with cited run labels/files. |
| `.planning/phases/13-latency-bar/investigation/` | Six pair sessions (12 runs), 3 bar sessions, 1 SC3 session — status/summary/JSONL files | ✓ VERIFIED | 123 files present; spot-checked `A1-run1.*`, `A2-run2.*`, `B1-run1.*` sets — each pair/run has `.inproc.jsonl`, `.poller.jsonl`, `.summary.json`, `.stdout/.stderr.txt`, `.session.log`, `.status.json`. |
| `bench/RESULTS.md` | Investigation summary, 3 bar-session subsections, SC3 subsection | ✓ VERIFIED | "### Phase 13 investigation sessions", "### Bar session bar-1/2/3", "### Composed worst row under ten concurrent builds (Phase 13)" all present with host-state headers, per-run tables, and findings. |
| `bench/latency.py` | `scenario_composed`, `run_composed`, `RequestOutcome`, `COMPOSED_ROWS`, `DEFAULT_SCENARIOS` unchanged order | ✓ VERIFIED | Present; `scenario_single`/`scenario_concurrent` byte-identical to `9f26052` per 13-06's own pinned test (`test_the_no_argument_latency_run_is_still_concurrent_then_single` — passed, see Behavioral Spot-Checks). |
| `tests/test_bench.py` | D-15's three new rows pinning composed-row selection, no-argument order, 503 parsing | ✓ VERIFIED | `test_the_composed_latency_scenario_fires_the_worst_composed_row_first_then_the_next_nine_heaviest`, `test_the_no_argument_latency_run_is_still_concurrent_then_single`, `test_a_503_is_recorded_by_the_reason_the_server_gave` all present and pass. |
| `docs/architecture/decision_log.md` | `## L32` appended after L31, amends L18 | ✓ VERIFIED | Present at the file's end; L18's own text has 0 deleted lines in the phase's diff. |
| `docs/tech_debt/resolved/2026-09-23-concurrent-latency-bar-waived.md` | Retired debt, `Status: resolved`, sha, moved | ✓ VERIFIED | Confirmed via `git log --follow`; moved from `active/` in commit `6709953`, sha recorded in follow-up `05668ef`. |
| `docs/tech_debt/active/2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md` | New debt filed for the SC3 finding, `Severity: must`, named trigger | ✓ VERIFIED | Present, `Severity: must`, `Status: active`, named trigger ("the ten-identical-worst-row scenario is run, a 500 is observed in production, `_run_with_timeout`/`recreate_for` is next touched, or `SPUR_BUILD_TIMEOUT`'s default is reconsidered"). INDEX row present (line 28). |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `13-LATENCY-INVESTIGATION.md` (`## Method`) | `investigation/session.py` | `--order` value, pair definitions | ✓ WIRED | Method section names `--order concurrent,single` and the A/B/C pair definitions used by `session.py --mode pair`; Results tables pasted from `tabulate.py` output over the committed files. |
| `bench/RESULTS.md` (bar sessions) | `investigation/bar-<n>-run<k>.txt` | captures copied verbatim | ✓ WIRED | Ratios (1.31×, 1.42× etc.) match the captured run output pattern used throughout; E10 (no re-rounding) honored. |
| `docs/architecture/decision_log.md` (`## L32`) | `13-LATENCY-INVESTIGATION.md`, `bench/RESULTS.md` | citations throughout L32's text | ✓ WIRED | L32 cites `13-LATENCY-INVESTIGATION.md § Verdict/§ Observation 1/2/§ Recommendation` and `bench/RESULTS.md` section names directly, no re-derived numbers. |
| Retired debt file | `docs/tech_debt/INDEX.md` | row moved to Resolved table in same commit set | ✓ WIRED | INDEX line 48 (Resolved) cites the file at its new `resolved/` path; no longer present in the Active table. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| D-15's three pinned tests (composed-row selection, no-argument order, 503 parsing) pass | `.venv/bin/python -m pytest tests/test_bench.py -k "composed_latency or no_argument_latency or reason_the_server_gave" -q` | `3 passed, 20 deselected in 2.29s` | ✓ PASS |
| `test_bench.py` collects the expected 23 tests, including the three new rows | `pytest tests/test_bench.py --collect-only -q` | 23 tests collected, including all three new rows by name | ✓ PASS |
| `src`/`bench` untouched through end of investigation write-up (SC1's "no `src`/`bench` change" constraint) | `git diff --quiet 9f26052 34d9ef4 -- src bench` | exit 0 | ✓ PASS |
| `src`/regression fixture unchanged across the whole phase (D-17) | `git diff --quiet 9f26052 HEAD -- src tests/regression/pre_v0_2.json` | exit 0 | ✓ PASS |
| Decision log is append-only across the phase | `git diff 9f26052 HEAD -- docs/architecture/decision_log.md \| grep '^-' \| grep -v '^---' \| wc -l` | `0` | ✓ PASS |
| No debt markers (`TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER`) in phase-touched files | `grep -n -E "TBD\|FIXME\|XXX\|TODO\|HACK\|PLACEHOLDER"` over `bench/latency.py`, `tests/test_bench.py`, `Dockerfile`, `decision_log.md`, both debt files, `investigation/*.py` | no matches | ✓ PASS |

`make verify` itself was not re-run in full by this verification (the 907→910-test, ~213 s run is already recorded in `13-07-SUMMARY.md` as the pre-commit-hook-gated result of the phase's own final commit — re-running the full suite here would add no new evidence per the single-full-run constraint, and the three named D-15 tests above are the behavior this phase actually added).

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|-------------|-----------------|--------------|--------|----------|
| REQ-latency-observations-explained | 13-01, 13-02, 13-03, 13-07 | Both observations get a cause ruled in or out by the bounded investigation | ✓ SATISFIED | Truth #1 above; `13-LATENCY-INVESTIGATION.md` `## Verdict`. |
| REQ-latency-bar-demonstrated-or-superseded | 13-04, 13-05, 13-06, 13-07 | Outcome (a) or (b), never a third; SC3's composed row measured and recorded; debt retires | ✓ SATISFIED | Truths #2, #3, #4 above. |

No orphaned requirements: `.planning/REQUIREMENTS.md` lines 205-206 map exactly these two IDs to Phase 13, both "Complete", and both appear in the `requirements:` frontmatter of at least one of this phase's seven plans.

### Plan 13-05 — Not Applicable (not a gap)

13-05-PLAN.md exists only for outcome (b). 13-04 recorded outcome (a) (bar-3 demonstrated, both
runs ≤1.99×), so 13-05's own Task 1 clause fired immediately: "write `13-05-SUMMARY.md` as
'not executed -- outcome (a)' and make no change." Confirmed in `13-05-SUMMARY.md`: no file
under `bench/`, `tests/` or `investigation/` was touched by this plan. Its must_haves (the
outcome-(b) floor/restart-protocol machinery) are therefore **not applicable**, not failed —
consistent with 12-CONTEXT.md D-04's framing and this phase's own pre-registered "never a
third outcome" rule.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `Dockerfile` | 40-42 | Comment says "across the fifteen bench/RESULTS.md latency runs" | ℹ️ Info | The 15-count includes the SC3 session, which aborted before computing any idle/under-load `/api/health` p95 (`13-06` finding: "idle/under-load p95: do not exist for this run"). The cited 0.7-2.3 ms range is still numerically accurate — it comes entirely from the 14 runs that did produce a reading — but the sentence implies all fifteen contributed to that range, and one of the fifteen contributed zero data points toward it. Not a printed/plausible number (L08 is not violated — no number was fabricated), and the comment does not cite the 2.00× bar (so SC4's "if it cites the bar" clause does not technically require this sentence's update at all). Recommend a follow-up wording tweak (e.g. "fourteen of the fifteen ... runs") next time this comment is touched; does not block this phase's goal. |

No debt markers (`TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER`), no stub returns, and no
hardcoded-empty-render patterns found in any file this phase touched.

### Human Verification Required

None. This phase's four Manual-Only items (`13-VALIDATION.md`) were directly checked against
the underlying artifacts during this verification (the investigation write-up against its raw
JSONL/summaries; the bar-session tables and L32 against `bench/RESULTS.md`; the SC3 section's
per-request table and row count; the debt-file git history and INDEX row) rather than deferred.
All four human checkpoints the phase itself raised during execution (D-08 run order, two D-06/D-05
host-quiet confirmations, the D-05 bar-3 retry authorization, the SC3 "record it" decision, and
the fleet-user restoration) were answered by the human and recorded verbatim in their respective
SUMMARYs, matching the orchestrator-supplied facts for this verification exactly.

### Gaps Summary

None. All four roadmap Success Criteria are met: both observations received a ruled cause
(one "not reproduced," one ruled in to the floor being real — both are rulings, not a dodge,
per the pre-registered escape-clause rule); the bar was demonstrated outright on bar-3
(outcome (a), no harness/bar change needed); SC3's composed worst row was measured once and
recorded exactly as it read (an aborted run exposing a real server defect, filed as new `must`
debt rather than silently retried or smoothed over); and the `must` debt file retired with its
sha, `git mv`, and INDEX row moved, the decision log append-only, and the Dockerfile comment
updated (with one minor wording-precision nit noted above, not blocking).

---

_Verified: 2026-10-02_
_Verifier: Claude (gsd-verifier)_
