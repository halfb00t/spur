---
phase: 03-structured-logging-at-the-composition-boundary
verified: 2026-09-24T00:00:00Z
status: passed
score: 4/4 must-haves verified
covered_files:
  - ".planning/REQUIREMENTS.md"
  - ".planning/phases/03-structured-logging-at-the-composition-boundary/03-01-PLAN.md"
  - ".planning/phases/03-structured-logging-at-the-composition-boundary/03-01-SUMMARY.md"
  - ".planning/phases/03-structured-logging-at-the-composition-boundary/03-02-PLAN.md"
  - ".planning/phases/03-structured-logging-at-the-composition-boundary/03-02-SUMMARY.md"
  - ".planning/phases/03-structured-logging-at-the-composition-boundary/03-03-PLAN.md"
  - ".planning/phases/03-structured-logging-at-the-composition-boundary/03-03-SUMMARY.md"
  - ".planning/phases/03-structured-logging-at-the-composition-boundary/03-REVIEW-FIX.md"
  - ".planning/phases/03-structured-logging-at-the-composition-boundary/03-REVIEW.md"
  - ".planning/phases/03-structured-logging-at-the-composition-boundary/03-SECURITY.md"
  - ".planning/phases/03-structured-logging-at-the-composition-boundary/03-VALIDATION.md"
  - "README.md"
  - "docs/CODING_VALUES.md"
  - "docs/architecture/cli.md"
  - "docs/architecture/decision_log.md"
  - "docs/architecture/gear-maths/errors_and_logging.md"
  - "docs/architecture/http-api.md"
  - "docs/architecture/solid-model/errors_and_logging.md"
  - "docs/tech_debt/INDEX.md"
  - "docs/tech_debt/resolved/2026-09-21-no-structured-logging.md"
  - "pyproject.toml"
  - "src/spur/app.py"
  - "src/spur/cli.py"
  - "src/spur/pool.py"
  - "src/spur/records.py"
  - "tests/conftest.py"
  - "tests/test_api.py"
  - "tests/test_pool.py"
  - "tests/test_records.py"
covered_digest: "v1:sha256:00f19692a829743c5f8a8dbfd42d63a9536e04b76dae777e9f22f38c8139fb68"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 3: Structured Logging at the Composition Boundary Verification Report

**Phase Goal:** Production requests leave evidence — a structured logger configured once
at the composition boundary, covering the decision branches that already exist.
**Verified:** 2026-09-24
**Status:** passed
**Re-verification:** No — initial verification

## Context Note

This verification ran after an execute:post code review (`03-REVIEW.md`) found one
Critical (`CR-01`: the formatter silently dropped every exception traceback, including
uvicorn's own unhandled-error line) and two Warnings (`WR-01`: `model()`'s except clauses
missed unclassified exceptions; `WR-02`: the `calc.py` log-free test only caught a literal
`import logging`), and a fixer applied and committed all three
(`2a1900d`, `a2a2371`, `482c936`, recorded in `03-REVIEW-FIX.md`). This report verifies the
tree at `HEAD` (`47615e1`), i.e. plans + review fixes together, since that is the actual
state of the codebase the phase goal must hold against.

## Goal Achievement

### Observable Truths (Roadmap Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A test asserts each of the four decision branches (build started w/ slug, build failed w/ exception class, export served cache-vs-built, queue refused) emits a structured record with named fields | ✓ VERIFIED | `tests/test_api.py::test_a_fresh_build_emits_build_started_then_export_served_with_source_built`, `test_a_repeat_download_is_served_from_cache_with_zero_duration_and_no_build_started`, `test_a_failed_build_emits_build_failed_naming_the_class_and_the_level` (parametrized x3), `test_a_saturated_service_emits_queue_refused_naming_the_gear_and_the_ceiling` — all run individually by this verifier and passed (see Behavioral Spot-Checks) |
| 2 | `calc.py` stays log-free — pure, runs on every keystroke, `warnings` is its only diagnostic | ✓ VERIFIED | `grep -n "^import\|^from" src/spur/calc.py` shows no `logging`/`records` import; `tests/test_records.py::test_calc_module_stays_log_free` (regex belt) plus the new import-linter contract `"The gear maths stays free of the logger"` (`pyproject.toml:152`, KEPT per `make lint-imports`) — belt and suspenders, both verified live |
| 3 | `docs/tech_debt/active/2026-09-21-no-structured-logging.md` is `Status: resolved`, sha recorded, `git mv`'d into `resolved/`, INDEX row moved — same commit as the fix | ✓ VERIFIED | `docs/tech_debt/resolved/2026-09-21-no-structured-logging.md` exists (active copy gone); `Status: resolved` / `Resolved in: 21b8fe4` present; `21b8fe4` resolves via `git cat-file -e`; `git log --follow` on the resolved file shows continuous history (a rename, not delete+add); `docs/tech_debt/INDEX.md:33` lists it under the Resolved table; all of this plus the four doc rewrites landed in one commit (`013997a`, confirmed via `git show --stat`) |
| 4 | `make verify` passes | ✓ VERIFIED | Ran independently at `HEAD` (`47615e1`): ruff clean, mypy `--strict` clean (23 files), import-linter 5/5 contracts KEPT, 99 tests passed in 32.00s |

**Score:** 4/4 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/spur/records.py` | Kernel-free module: `configure()`, formatter, level parser, five per-event helpers | ✓ VERIFIED | Contains `configure`, `_JsonFormatter`, `_JsonHandler`, `_parse_level`, `_gear_fields`, `_ms`, `_emit`, `build_started`, `export_served`, `build_failed`, `queue_refused`, `worker_replaced`. Imports only `datetime, json, logging, os, sys`, `spur.__version__`, `.build_errors.BuildError`, `.params.GearParams` — reaches neither `cadquery`/`OCP` nor `fastapi`/`starlette`/`spur.app` |
| `src/spur/cli.py` | `cmd_serve` calls `configure()` before `uvicorn.run(..., log_config=None)`; `cmd_info`/`cmd_export` untouched | ✓ VERIFIED | `configure()` at line 54, `log_config=None` at line 63; `cmd_info`/`cmd_export` contain no logging call (D-07) |
| `src/spur/app.py` | Idempotent second `configure()` in `lifespan()`; `build_started`/`export_served`/`build_failed`/`queue_refused` at the existing branches | ✓ VERIFIED | `configure()` called at `lifespan()` line 132; `build_started`/`export_served` wired into `model()`'s cache/compressed/built paths; three named `except` clauses plus a WR-01 catch-all (`except HTTPException: raise` guard before it, avoiding a spurious duplicate on the admission-refusal path) all call `build_failed`; `_build_slot` calls `queue_refused` before its `raise HTTPException(503, ...)` |
| `src/spur/pool.py` | `worker_replaced()` inside `recreate_for`'s identity guard, after the counter | ✓ VERIFIED | `worker_replaced(slot=i, cause=cause)` at line 151, immediately after `self.replaced += 1` (line 150) and inside the `if self._executors[i] is not executor: return` guard — the only call site, confirmed by `grep -n worker_replaced src/spur/pool.py` showing no hits inside `_run_with_timeout` |
| `tests/conftest.py` | Autouse root-logger reset | ✓ VERIFIED | Present, used by every test in `test_records.py`/`test_api.py`/`test_pool.py` |
| `tests/test_records.py` | Formatter round-trip, level knob, idempotency, `calc.py` log-free, traceback rendering (review fix) | ✓ VERIFIED | 13 tests, all pass in isolation (`.65s`) |
| `tests/test_api.py` / `tests/test_pool.py` | `caplog` branch tests for all five events | ✓ VERIFIED | Named tests found and independently re-run; all pass |
| `docs/architecture/decision_log.md` | `L20`, appended, dated, records D-01–D-04/D-06/D-14 and the two-call-site correction | ✓ VERIFIED | `## L20 — Structured JSON logging, configured at two idempotent call sites` present; `git diff --stat main...HEAD -- docs/architecture/decision_log.md` shows `68 insertions(+)`, `0 deletions` (verified the sole `-` line in the raw diff is the file-header line, not content) |
| `docs/tech_debt/resolved/2026-09-21-no-structured-logging.md` | Retired debt item | ✓ VERIFIED | Present, `Status: resolved`, `Resolved in: 21b8fe4` |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `src/spur/cli.py` | `src/spur/records.py` | `cmd_serve` calls `configure()` before `uvicorn.run(..., log_config=None)` | ✓ WIRED | Confirmed by line inspection |
| `src/spur/app.py` | `src/spur/records.py` | `lifespan()` calls `configure()`; `model()` calls the per-event helpers | ✓ WIRED | Confirmed; import line 33 imports all five relevant helpers |
| `src/spur/pool.py` | `src/spur/records.py` | `recreate_for` calls `worker_replaced()` inside the identity guard | ✓ WIRED | Confirmed at exact line, correct ordering |
| `tests/test_api.py` / `tests/test_pool.py` | `src/spur/records.py` | `caplog` asserts literal event/field names | ✓ WIRED | Literal strings `build.started`, `export.served`, `build.failed`, `queue.refused`, `worker.replaced` all found and asserted |
| `docs/tech_debt/INDEX.md` | `docs/tech_debt/resolved/2026-09-21-no-structured-logging.md` | Resolved-table link | ✓ WIRED | `docs/tech_debt/INDEX.md:33` links the moved file |

### Behavioral Spot-Checks

Independently re-run by this verifier (not taken from SUMMARY claims):

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Full gate | `make verify` | ruff clean; mypy --strict clean (23 files); import-linter 5/5 KEPT; 99 passed in 32.00s | ✓ PASS |
| `build.started`→`export.served` (built), cache (0ms, no start), compressed, `build.failed` x3 classes | `pytest tests/test_api.py -k "build_started_then_export_served or a_saturated_service_emits_queue_refused or a_failed_build_emits_build_failed"` | 5 passed in 0.99s | ✓ PASS |
| `worker.replaced` once per incident (wedge, dead worker, two-same-slot-deaths regression guard) | `pytest tests/test_pool.py -k "worker_replaced or wedged_build_is_terminated or dying_worker_surfaces or two_same_slot_deaths"` | 3 passed in 11.51s | ✓ PASS |
| `test_records.py` full file (formatter round-trip, traceback rendering, idempotency, level knob, `calc.py` log-free) | `pytest tests/test_records.py -v` | 13 passed in 0.65s | ✓ PASS |
| Decision log append-only | `git diff --stat main...HEAD -- docs/architecture/decision_log.md` | `1 file changed, 68 insertions(+)` | ✓ PASS |
| Debt file is a rename, not delete+add | `git log --follow --oneline -- docs/tech_debt/resolved/2026-09-21-no-structured-logging.md` | continuous history through `de5b3da` | ✓ PASS |
| No debt markers / stray `print()` in touched `src/` files | `grep -nE "TBD\|FIXME\|XXX\|TODO\|HACK\|PLACEHOLDER"` and `grep -rn "print("` on `records.py`/`app.py`/`pool.py`/`cli.py` | no matches | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|--------------|--------|----------|
| REQ-structured-logging | 03-01, 03-02, 03-03 | Structured logger at the composition boundary, emitting build started/failed, export served, queue refused | ✓ SATISFIED | All four roadmap success criteria verified above; `REQUIREMENTS.md`'s traceability table lists it as Phase 3, and `.planning/REQUIREMENTS.md` shows no other requirement mapped to "Phase 3" — no orphaned requirements |

### Anti-Patterns Found

None. No `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` markers, no stray `print()` calls,
no stub returns in any file this phase touched.

### Code Review Findings (context, not new findings)

`03-REVIEW.md` found 1 Critical + 2 Warnings; `03-REVIEW-FIX.md` records all three fixed in
commits `2a1900d`/`a2a2371`/`482c936`. This verifier independently confirmed the fixes are
present and behaviorally proven:
- CR-01 (dropped tracebacks): `_JsonFormatter.format()` now renders `exc_info`/`exc_text`
  into a `traceback` field and `stack_info` into a `stack_info` field; `spur`'s own
  `build_failed()` never sets `exc_info` (proven by
  `test_build_failed_helper_never_carries_a_traceback_field`), so this only affects
  uvicorn's own unhandled-error line — proven by
  `test_the_formatter_renders_a_real_traceback_into_a_dedicated_field`.
- WR-01 (unclassified exceptions vanish): `model()` gained
  `except HTTPException: raise` (guarding against a spurious duplicate on the
  admission-refusal path) followed by `except Exception as exc: build_failed(...); raise`
  — proven behaviorally by
  `test_an_unclassified_exception_still_emits_build_failed_and_is_not_swallowed`, which
  drives a `MemoryError` through the injected backend and asserts the exception still
  propagates (`pytest.raises`) while a `build.failed` record fires at ERROR.
- WR-02 (weak `calc.py` guard): both the regex test was broadened and a new import-linter
  contract `"The gear maths stays free of the logger"` was added — `make lint-imports`
  confirms 5/5 contracts KEPT.

One Info-level finding (`IN-01`, duplicate idempotency setup between two tests) was
explicitly out of the fixer's scope (`fix_scope: critical_warning`) and is cosmetic —
correctly not blocking.

### Human Verification Required

None. Every must-have truth was verified by a test this verifier ran directly (not by
console-reading or SUMMARY claims), matching the roadmap's explicit instruction ("proven by
a test, not console-reading").

### Gaps Summary

No gaps. All four roadmap success criteria hold in the codebase as of `HEAD` (`47615e1`),
independently re-verified: the four decision branches each emit a named-field structured
record proven by a passing test; `calc.py` is provably log-free by both a regex test and an
import-linter contract; the tech-debt lifecycle (status flip, sha, `git mv`, INDEX move) is
complete and landed in one commit; and `make verify` passes (ruff, mypy --strict,
import-linter, 99 tests) when run fresh in this session.

---

_Verified: 2026-09-24_
_Verifier: Claude (gsd-verifier)_
