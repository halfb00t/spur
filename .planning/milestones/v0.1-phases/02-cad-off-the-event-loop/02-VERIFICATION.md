---
phase: 02-cad-off-the-event-loop
verified: 2026-09-24T05:03:22Z
status: passed
score: 5/5 must-haves verified
covered_files: [".planning/REQUIREMENTS.md", ".planning/phases/02-cad-off-the-event-loop/02-01-PLAN.md", ".planning/phases/02-cad-off-the-event-loop/02-01-SUMMARY.md", ".planning/phases/02-cad-off-the-event-loop/02-02-PLAN.md", ".planning/phases/02-cad-off-the-event-loop/02-02-SUMMARY.md", ".planning/phases/02-cad-off-the-event-loop/02-03-PLAN.md", ".planning/phases/02-cad-off-the-event-loop/02-03-SUMMARY.md", ".planning/phases/02-cad-off-the-event-loop/02-04-PLAN.md", ".planning/phases/02-cad-off-the-event-loop/02-04-SUMMARY.md", ".planning/phases/02-cad-off-the-event-loop/02-05-PLAN.md", ".planning/phases/02-cad-off-the-event-loop/02-05-SUMMARY.md", ".planning/phases/02-cad-off-the-event-loop/02-REVIEW.md", ".planning/phases/02-cad-off-the-event-loop/02-SECURITY.md", ".planning/phases/02-cad-off-the-event-loop/02-UAT.md", ".planning/phases/02-cad-off-the-event-loop/02-VALIDATION.md", ".planning/quick/260924-bv5-fix-02-review-md-findings-cr-01-cr-02-an/260924-bv5-PLAN.md", ".planning/quick/260924-bv5-fix-02-review-md-findings-cr-01-cr-02-an/260924-bv5-SUMMARY.md", "Dockerfile", "Makefile", "README.md", "bench/README.md", "bench/RESULTS.md", "bench/__init__.py", "bench/corpus.py", "bench/latency.py", "bench/memory.py", "compose.yaml", "docker/smoke.py", "docs/architecture/decision_log.md", "docs/architecture/http-api.md", "docs/architecture/overview.md", "docs/architecture/packaging.md", "docs/tech_debt/INDEX.md", "docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md", "docs/tech_debt/resolved/2026-09-21-cad-builds-block-the-event-loop.md", "pyproject.toml", "src/spur/app.py", "src/spur/build_errors.py", "src/spur/cli.py", "src/spur/model.py", "src/spur/pool.py", "tests/test_api.py", "tests/test_bench.py", "tests/test_pool.py"]
covered_digest: "v1:sha256:a749783aadf10cbbc3a669f1b3a9a22cba6edf671ea64ff6d5345727c2eb80d9"
behavior_unverified: 0
overrides_applied: 1
overrides:
  - must_have: "the debt file's two load scenarios show /api/health p95 within 2x of idle p95, concurrent scenario"
    reason: "Eight runs across four sessions (bench/RESULTS.md) never demonstrated the concurrent scenario's <=2.00x ratio on both runs of one session (pre-fix 2.02x/2.45x, 2.32x/2.35x; post-fix 1.31x/2.10x, 1.86x/2.02x, the last pair on a host a watcher held under the file's own 1.5 idle-load bar). The human explicitly waived broken-windows ledger item 1 on this evidence rather than requiring a further re-run or fix, and filed the caveat plus two unexplained observations as must-severity tech debt (docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md). L18 (decision_log.md) records this as 'accepted with caveat, not demonstrated' verbatim. The single-build scenario (the debt file's own headline numbers) clears the bar on every run recorded."
    accepted_by: "human (via .planning/WINDOWS.md item 1, waived)"
    accepted_at: "2026-09-23T14:17:18.148Z"
re_verification:
  previous_status: human_needed
  previous_score: 5/5
  gaps_closed:
    - "CR-01 (src/spur/pool.py): a same-slot sibling request queued behind a timed-out build raised uncaught asyncio.CancelledError (a BaseException every handler misses) instead of a mapped 503 -- fixed in 17048c9/08697f0/15fa5cd; now raises BrokenProcessPool, covered by tests/test_pool.py::test_four_same_slot_requests_all_refuse_without_cancellation."
    - "CR-02 (bench/memory.py): bench.memory sweep ran uncapped against compose.yaml's own mem_limit, silently re-capping any future N whose true peak exceeds it -- fixed in d334049 with an 8g sweep-only override; tests/test_bench.py pins the capped/uncapped predicate."
    - "WR-01 (src/spur/pool.py): two same-slot failures from one incident double-recreated the worker and double-counted workers_replaced -- fixed in 17048c9 with a stale-executor identity guard on recreate_for; covered by tests/test_pool.py::test_two_same_slot_deaths_from_one_incident_replace_the_worker_once."
    - "WR-02 (Dockerfile): HEALTHCHECK comment overstated the latency evidence (claimed 0.7-1.3ms across all eight runs; three of eight runs fall outside that range) -- corrected in 2b34ec4 to the true 0.7-2.3ms range, worst run named."
    - "02-05-PLAN.md Task 3 <human-check> (HEALTHCHECK timeout + comment + two shas) and Task 4 <human-check> (overview/http-api/packaging one consistent story), both listed as pending human_verification items in the prior report -- both recorded pass in 02-UAT.md (2026-09-24T03:37:15Z), after the last commit touching any covered file (15fa5cd, 2026-09-24T03:06:45Z)."
  gaps_remaining: []
  regressions: []
gaps: []
advisory: []
---

# Phase 2: CAD Off the Event Loop Verification Report

**Phase Goal:** CAD kernel work runs in worker processes outside the request-serving
event loop, and the resulting multi-process memory ceiling is a measured number — not an
assumption carried forward from the single-process design L07 measured.
**Verified:** 2026-09-24T05:03:22Z
**Status:** passed
**Re-verification:** Yes — after four code-review fixes (CR-01, CR-02, WR-01, WR-02) and
end-of-phase human UAT, against the prior `human_needed` report of 2026-09-23T15:18:49Z

## Why this report was regenerated

The prior VERIFICATION.md (2026-09-23T15:18:49Z, `human_needed`, 5/5, one override) went
stale: four commits landed after it, resolving all four findings from `02-REVIEW.md`
(critical CR-01/CR-02, warnings WR-01/WR-02) —
`17048c9` (CR-01/WR-01, `pool.py`/`app.py`/`http-api.md`/`test_pool.py`), `d334049`
(CR-02, `bench/memory.py`/`compose.yaml`/`bench/README.md`/`test_bench.py`), and
`08697f0`+`15fa5cd` (hardening/observing CR-01's cancelled-sibling path further). This
report re-verifies the *current* code, not the prior report's description of it. The two
`<human-check>` items the prior report left pending (both explicitly deferred to
end-of-phase by 02-05-PLAN.md's own tasks, per `workflow.human_verify_mode=end-of-phase`)
were subsequently performed by the human and recorded in `02-UAT.md`: both `result: pass`,
timestamped 2026-09-24T03:37:15Z UTC — after the last commit touching any covered file
(`15fa5cd`, 2026-09-24T03:06:45Z UTC; every later commit touched only `.planning/*.md`
artifacts, not covered files, confirmed via `git log --oneline 3dc047d..HEAD --stat`).
The concurrent-latency override from the prior report is carried forward verbatim
(frontmatter `overrides`) — no new override was invented.

## Goal Achievement

### Observable Truths

Five truths, one per ROADMAP.md success criterion. Truth 1 is asserted per-scenario
because the debt file's acceptance clause names two distinct scenarios with independent
outcomes; both halves are recorded rather than merged into a single averaged verdict.

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1a | `single` scenario: under-load p95 <= 2x idle p95, numbers recorded beside baseline | ✓ VERIFIED | `bench/RESULTS.md` § Latency: met on every run recorded — Runs 1-2 (1.12x, 1.18x), Runs 3-4 (1.68x, 1.17x), Run 5 (1.10x). Debt file's baseline (0.22s→0.76s→2.00s, 12-core machine) quoted verbatim beside the new figures, labelled as a different machine (D-17). Unchanged by the review-fix commits (none touched `bench/latency.py` or `bench/RESULTS.md`). |
| 1b | `concurrent` scenario: under-load p95 <= 2x idle p95, numbers recorded beside baseline | PASSED (override) | Not demonstrated on both runs of any of 4 sessions (8 runs: 2.02x/2.45x, 2.32x/2.35x, 1.31x/2.10x, 1.86x/2.02x). Human waived `.planning/WINDOWS.md` item 1 on this evidence 2026-09-23T14:17:18Z; caveat filed as must-severity debt (`docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md`), still `Status: active` with the correct trigger. L18 records "accepted with caveat, not demonstrated" verbatim. See `overrides` in frontmatter — carried forward unchanged. |
| 2 | Memory sweep of real N-worker topology produces a measured ceiling; `compose.yaml`'s `mem_limit` set from it | ✓ VERIFIED | `bench/RESULTS.md` § Memory: N=1/2/4 sweep (peaks 2052.1/2878.5/4731.9 MiB), `mem_limit: 4g` = 2878.5 MiB × 1.3 headroom, rounded up, confirmed 0/40 failures. `compose.yaml` ships `mem_limit: 4g` with the comment naming peak, factor, confirm result, and now also names CR-02's fix ("re-measure ... which runs under its own ceiling, not this one, CR-02 review"). L17 carries the same numbers, unchanged. |
| 3 | `decision_log.md` gains entries superseding, and saying they supersede, L07 and L06 — dated, citing measurement, neither edited in place | ✓ VERIFIED | L17 ("supersedes L07") and L18 ("supersedes L06") present, both dated 2026-09-23, both citing `bench/RESULTS.md` numbers inline; L19 (gzip level, unrelated decision) also present. Neither the review-fix commits nor the human-check resolution touched `decision_log.md`; L06/L07 remain byte-identical to the pre-phase text. |
| 4 | Debt file `Status: resolved`, sha recorded, `git mv`'d to `resolved/`, INDEX row moved — same commit as fix | ✓ VERIFIED | `docs/tech_debt/resolved/2026-09-21-cad-builds-block-the-event-loop.md` exists, reads `Status: resolved`, `Resolved in: daeb284`. `docs/tech_debt/active/2026-09-21-cad-builds-block-the-event-loop.md` does not exist. `docs/tech_debt/INDEX.md`'s Resolved table lists it; its Active table does not. Unaffected by the review-fix commits. |
| 5 | `make verify` passes with new topology; admission control stays in web layer; CLI never queues | ✓ VERIFIED | `make verify` run this session (see command/result below): ruff clean, mypy `--strict` "no issues found in 20 source files", 4 import-linter contracts kept/0 broken, **76 passed** in 28.35s (was 71 at the prior report; +5 from the review-fix commits' new tests: `tests/test_bench.py`'s 3 CR-02 predicate tests, `tests/test_pool.py`'s `test_four_same_slot_requests_all_refuse_without_cancellation` and `test_two_same_slot_deaths_from_one_incident_replace_the_worker_once`). `BUILD_QUEUE`/`_build_slot` still live in `src/spur/app.py` (web layer). `src/spur/cli.py::cmd_export` still imports `Format, export` from `.model` directly — no `.pool`, no `.app`, no queue import anywhere in `cli.py`. |

**Score:** 5/5 truths verified (1 via override, `overrides_applied: 1`); 0
present-but-behavior-unverified. The two cancellation/cleanup invariants introduced by
this round's fixes (CR-01: a same-slot sibling must surface `BrokenProcessPool`, never a
bare `asyncio.CancelledError`; WR-01: one incident replaces one worker, once) are each
exercised by a dedicated, currently-green test (`test_four_same_slot_requests_all_refuse_without_cancellation`,
`test_two_same_slot_deaths_from_one_incident_replace_the_worker_once`) that ran as part of
the 76-passed suite this session — behaviorally verified, not merely present and wired.

### `make verify` — command and result (run this session)

```
$ make verify
.venv/bin/python -m ruff check .
All checks passed!
.venv/bin/python -m mypy src tests docker bench
Success: no issues found in 20 source files
.venv/bin/lint-imports
Contracts: 4 kept, 0 broken.
.venv/bin/python -m pytest
collected 76 items
tests/test_api.py ...................                                    [ 25%]
tests/test_bench.py ...                                                  [ 28%]
tests/test_calc.py .....................                                 [ 56%]
tests/test_cli.py ....                                                   [ 61%]
tests/test_model.py .............                                        [ 78%]
tests/test_pool.py ................                                     [100%]
============================= 76 passed in 28.35s ==============================
```

### Advisory (New Scope, Unevidenced)

None. Step 7's anti-pattern scan on the review-fix commits' files
(`src/spur/pool.py`, `src/spur/app.py`, `bench/memory.py`, `compose.yaml`, `Dockerfile`,
`tests/test_pool.py`, `tests/test_bench.py`) found no `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/
`PLACEHOLDER` markers and no stub patterns. No new-scope 🛑 Blocker was raised this pass,
so there is nothing to route through the convergence evidence gate.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/spur/build_errors.py` | Kernel-free `BuildError`/`BuildTimeout` | ✓ VERIFIED | Present, contains both classes, no reference to `cadquery`/`OCP`/`spur.model`. Untouched by the review-fix commits. |
| `src/spur/pool.py` | `BuildPool`: N single-worker executors, affinity routing, timeout, termination/replacement, one-recreate-per-incident | ✓ VERIFIED | `recreate_for(p, executor)` now takes the caller's own captured executor and no-ops if the slot was already replaced (WR-01 fix, lines 94-140); `shutdown()` inside it no longer passes `cancel_futures=True` (CR-01 fix), with an extensive comment tracing the CPython `concurrent.futures.process` mechanics that made the cancelled-sibling path reachable. `_run_with_timeout` passes `executor` into both `recreate_for` calls (timeout and `BrokenProcessPool` branches). |
| `src/spur/app.py` | Async model endpoint, lifespan-managed pool, byte cache, admission control derived from `SPUR_BUILD_WORKERS`, `/api/health` pool fields | ✓ VERIFIED | `lifespan` builds `BuildPool` eagerly; `model()` is `async def`; `_BlobCache`/`_EXPORTS` live here; `_max_queued_builds()` derives from `SPUR_BUILD_WORKERS`; `health()` returns nested `pool` object from parent-local counters only, synchronous `def`, no await/lock/worker call (guarded by `test_health_handler_never_awaits_or_touches_pool_internals`). `BrokenProcessPool` handler's comment now also explains the CR-01 case (a same-slot sibling terminated by another request's timeout). |
| `pyproject.toml` | Import-linter contract forbidding `spur.app` → kernel, indirect included | ✓ VERIFIED | "The serving process never imports the CAD kernel" contract present, `allow_indirect_imports = false`, `source_modules = ["spur.app"]`. `lint-imports` (via `make verify`) reports 4 contracts kept, 0 broken. |
| `bench/latency.py`, `bench/memory.py`, `bench/corpus.py` | Rerunnable harness producing both scenarios and the N=1,2,4 sweep, sweep no longer self-capped | ✓ VERIFIED | `bench/memory.py`'s `_sweep_one` now writes an 8 GiB `mem_limit` override (`_SWEEP_MEM_LIMIT_BYTES`) via `_write_mem_limit_override` before running each N, mirroring `confirm()`'s existing mechanism (CR-02 fix); a row landing within 1% of that ceiling is refused (no peak reported) rather than silently capped. `bench/README.md` documents the change. |
| `bench/RESULTS.md` | Committed measurement record | ✓ VERIFIED | 362 lines, unchanged by the review-fix commits (they fix the harness/comments, not the already-committed measurement); every number in L17/L18/`compose.yaml`/`Dockerfile`/README still traces back to a line here. |
| `docs/architecture/decision_log.md` | L17, L18 (+ L19) | ✓ VERIFIED | Present, dated, cite `bench/RESULTS.md`, L06/L07 untouched. Unaffected by the review-fix commits. |
| `docs/tech_debt/resolved/2026-09-21-cad-builds-block-the-event-loop.md` | Resolved debt item | ✓ VERIFIED | Present, `Status: resolved`, `Resolved in: daeb284`. Unaffected by the review-fix commits. |
| `Dockerfile` | HEALTHCHECK timeout from measured p95, comment scoped to the evidence it cites | ✓ VERIFIED | `--timeout=2s`, comment now reads "0.7-2.3 ms across the eight bench/RESULTS.md latency runs (worst: 2.3 ms, concurrent Run 3, pre-L19; 1.3 ms post-L19)" — the WR-02 fix (`2b34ec4`), matching `bench/RESULTS.md`'s own per-run table exactly (no run outside the stated range). |
| `docs/architecture/overview.md`, `docs/architecture/http-api.md`, `docs/architecture/packaging.md` | System map redrawn for kernel-free server + N workers, one consistent story | ✓ VERIFIED (human-confirmed) | `http-api.md` gained a CR-01-related sentence in `17048c9`. Consistency across all three documents was confirmed by a human this session per `02-UAT.md` test 2 (`result: pass`, 2026-09-24T03:37:15Z) — see Human Verification below. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `src/spur/app.py` | `src/spur/pool.py` | `app.state.pool` created in lifespan; `model()` awaits injected `build_backend` → `pool.export` | ✓ WIRED | Confirmed by reading `app.py`; `build_backend()` hard-fails (no silent inline fallback) if `app.state.pool` is `None`. |
| `src/spur/pool.py` | `src/spur/model.py` | Dynamic `importlib.import_module("spur.model")` inside the worker entry point | ✓ WIRED | Confirmed in `_warm()` and `build_export()`; `lint-imports` confirms this stays invisible to the forbidden-import contract while still resolving at runtime (contract kept, 0 broken). |
| `src/spur/pool.py`'s `_run_with_timeout` | `src/spur/pool.py`'s `recreate_for` | Caller passes its own captured `executor`, not just the params, so a stale caller no-ops (WR-01) | ✓ WIRED | Both the `except asyncio.TimeoutError` and `except BrokenProcessPool` branches call `self.recreate_for(p, executor)` with the locally-captured `executor`; `recreate_for`'s identity check (`if self._executors[i] is not executor: return`) is exercised by `test_two_same_slot_deaths_from_one_incident_replace_the_worker_once`, which asserts `pool.replaced` rises by exactly 1 for two same-slot failures. |
| `bench/memory.py`'s `sweep()` | `_write_mem_limit_override` | Sweep-only 8g override, independent of `compose.yaml`'s shipped 4g | ✓ WIRED | `_sweep_one` calls `_write_mem_limit_override(f"{_SWEEP_MEM_LIMIT_BYTES}b")` before starting each N's container; `tests/test_bench.py` pins the capped-vs-uncapped predicate against `_SWEEP_MEM_LIMIT_BYTES`. |
| `docs/architecture/decision_log.md` (L17/L18) | `bench/RESULTS.md` | Numbers cited inline, traceable to the results file | ✓ WIRED | Cross-checked every figure in L17 (peaks, mem_limit, headroom, confirm result) and L18 (ratios) against `bench/RESULTS.md`'s own tables — all match, unchanged by this round. |
| `compose.yaml` `mem_limit` | `bench/RESULTS.md` | Comment cites the sweep row and headroom factor, plus the CR-02 fix | ✓ WIRED | `mem_limit: 4g` comment names 2878.5 MiB peak, ×1.3 headroom, 0/40 confirm failures, and now also "re-measure (bench.memory sweep -- which runs under its own ceiling, not this one, CR-02 review)". |
| `docs/tech_debt/INDEX.md` | `docs/tech_debt/resolved/...` | Resolved-section link | ✓ WIRED | Row present under `## Resolved`, links to the moved file, which exists at that path. |

### Data-Flow Trace (Level 4)

Not separately applicable — this phase has no UI-rendered dynamic values; the "data" that
matters is measurement numbers flowing from `bench/RESULTS.md` into `compose.yaml`,
`Dockerfile` and `decision_log.md`, all traced above under Key Link Verification and
cross-checked by direct read (not a static fallback anywhere in the chain).

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Full test suite passes, including the process-boundary and cancellation-invariant tests | `make verify` (ruff, mypy --strict, lint-imports, no-fake-done, pytest) | ruff clean; mypy "no issues found in 20 source files"; 4 import-linter contracts kept/0 broken; 76 passed in 28.35s | ✓ PASS |
| CR-01 invariant: a same-slot sibling queued behind a timed-out build never surfaces `asyncio.CancelledError` | Named test, run as part of the full suite above: `tests/test_pool.py::test_four_same_slot_requests_all_refuse_without_cancellation` | Included in the 76 passed | ✓ PASS |
| WR-01 invariant: two same-slot failures from one incident replace the worker exactly once | Named test, run as part of the full suite above: `tests/test_pool.py::test_two_same_slot_deaths_from_one_incident_replace_the_worker_once` | Included in the 76 passed | ✓ PASS |
| CR-02 invariant: `sweep()`'s override predicate correctly caps/refuses a row at its own ceiling | Named tests, run as part of the full suite above: `tests/test_bench.py::test_a_peak_equal_to_the_ceiling_is_capped`, `test_a_peak_well_below_the_ceiling_is_not_capped`, `test_the_tolerance_boundary_is_pinned_from_both_sides` | Included in the 76 passed | ✓ PASS |
| No debt-marker regressions in phase-modified files | `git grep -nE '\b(TBD\|FIXME\|XXX)\b' -- src/spur/pool.py src/spur/app.py bench/memory.py compose.yaml Dockerfile tests/test_pool.py tests/test_bench.py` | no output (0 matches) | ✓ PASS |
| CLI still calls `model.export` in-process, no pool | Direct read of `src/spur/cli.py` imports | `from .model import Format, export`; no import of `.pool` or `.app` anywhere in `cli.py` | ✓ PASS |

### Probe Execution

Not applicable — this phase declares no `scripts/*/tests/probe-*.sh` probes; its
measurement harness (`bench/`) is the analogous instrument and is covered above under
Behavioral Spot-Checks and the artifact/key-link tables. `bench/RESULTS.md` was
cross-checked directly against every downstream number rather than re-run this session,
since a fresh `make bench` run takes ~15+ minutes and the review-fix commits changed the
*harness's self-protection* (CR-02), not the already-committed measurement itself.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| REQ-cad-off-event-loop | 02-01, 02-02, 02-03, 02-04, 02-05 | CAD builds run outside the serving process; `/api/health` latency decoupled from build size | ✓ SATISFIED | Truths 1a/1b/4/5 above; `.planning/REQUIREMENTS.md` marks it `[x]` and `Complete` in the coverage table. |
| REQ-measured-memory-ceiling | 02-02, 02-04, 02-05 | Memory ceiling measured (not derived), `mem_limit` set from it, superseding decision-log entry | ✓ SATISFIED | Truths 2/3 above; `.planning/REQUIREMENTS.md` marks it `[x]` and `Complete`. |

No orphaned requirements: `.planning/REQUIREMENTS.md`'s Phase 2 section lists exactly
these two IDs, both claimed across the five plans' frontmatter `requirements:` fields.

### Anti-Patterns Found

None in phase-scoped files, including the four review-fix commits' files. `no-fake-done`
(part of `make verify`) returned clean this session. No stub returns, empty handlers, or
hardcoded-empty data patterns found in `src/spur/pool.py`, `src/spur/app.py`,
`bench/memory.py`, `compose.yaml`, or `Dockerfile` on direct read.

### Human Verification Required

None pending. Two items were deferred to end-of-phase by 02-05-PLAN.md's own Task 3 and
Task 4 `<human-check>` blocks (per `workflow.human_verify_mode=end-of-phase`) and both are
now recorded as performed and passed:

1. **Container reaches healthy under the new 2s HEALTHCHECK timeout; comment and shas
   distinguishable.** `02-UAT.md` test 1, `result: pass`, updated 2026-09-24T03:37:15Z —
   after the last commit touching any covered file (`15fa5cd`, 2026-09-24T03:06:45Z), and
   after the WR-02 Dockerfile-comment fix (`2b34ec4`, 2026-09-23T21:23:51Z) it was checked
   against.

2. **`overview.md`, `http-api.md` and `packaging.md` tell one consistent story.**
   `02-UAT.md` test 2, `result: pass`, updated 2026-09-24T03:37:15Z — after `17048c9`'s
   CR-01-related addition to `http-api.md` (2026-09-24T08:47:46+06:00 /
   2026-09-24T02:47:46Z), so the human read the current text, not a stale version.

All other Nyquist-checkpoint `<human-check>` blocks in this phase's plans (02-03 Task 3,
02-04 Tasks 1/2/3) were performed interactively during execution, not deferred — confirmed
via `02-03-SUMMARY.md` ("the qualitative property this plan's human-check proved by eye")
and `02-04-SUMMARY.md`'s coverage block (D2-D6, all `human_judgment: false`, `status:
pass`). D1's `human_judgment: true` entry in `02-04-SUMMARY.md` is the same
concurrent-latency decision already captured by the carried-forward override above, not a
separate pending item.

### Gaps Summary

None. All five roadmap success criteria are met or explicitly, evidentially overridden by
a documented human decision already on record (`.planning/WINDOWS.md`,
`docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md`, `decision_log.md`
L18) — not a gap introduced or accepted by this verification pass. All four `02-REVIEW.md`
findings (CR-01, CR-02, WR-01, WR-02) are resolved in the current code, each with a
dedicated regression test that ran green this session. `make verify` is green (76 tests,
4 contracts, clean lint/mypy/no-fake-done); the debt-resolution lifecycle, the
decision-log supersession, and the measured knobs (`SPUR_BUILD_TIMEOUT`, `mem_limit`,
`SPUR_BUILD_WORKERS`, the HEALTHCHECK timeout) are all traceable to `bench/RESULTS.md`.
Both previously-pending human-check items are now recorded pass in `02-UAT.md`, performed
against the current (post-fix) code. Status is `passed`.

---

_Verified: 2026-09-24T05:03:22Z_
_Verifier: Claude (gsd-verifier)_
