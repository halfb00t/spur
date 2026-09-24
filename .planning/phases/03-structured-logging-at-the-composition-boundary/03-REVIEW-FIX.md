---
phase: 03-structured-logging-at-the-composition-boundary
fixed_at: 2026-09-24T11:21:07Z
review_path: .planning/phases/03-structured-logging-at-the-composition-boundary/03-REVIEW.md
iteration: 1
findings_in_scope: 3
fixed: 3
skipped: 0
status: all_fixed
---

# Phase 03: Code Review Fix Report

**Fixed at:** 2026-09-24T11:21:07Z
**Source review:** .planning/phases/03-structured-logging-at-the-composition-boundary/03-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 3 (CR-01, WR-01, WR-02 -- `fix_scope: critical_warning`; IN-01 excluded by scope)
- Fixed: 3
- Skipped: 0

**Verification environment:** `workflow.use_worktrees` is `false` in `.planning/config.json`, so all edits, syntax/type checks, and `make verify` ran directly in the main checkout (no isolated worktree was created; no worktree teardown was needed).

## Fixed Issues

### CR-01: `_JsonFormatter` silently drops every exception traceback, including uvicorn's own unhandled-error log line

**Files modified:** `src/spur/records.py`, `tests/test_records.py`, `docs/architecture/http-api.md`
**Commit:** `2a1900d`
**Applied fix:** `_JsonFormatter.format()` now renders `record.exc_info` via `self.formatException()` (falling back to a cached `record.exc_text`) and `record.stack_info` via `self.formatStack()`, into a dedicated `traceback` field (and `stack_info` field respectively). `spur`'s own `build_failed()` helper never sets `exc_info`, so its own records are unchanged (verified by a new regression test); the fix only affects records `spur` doesn't control, such as uvicorn's own `"Exception in ASGI application"` line. Added two tests: one drives a real multi-frame traceback through the formatter and asserts the `traceback` field contains the exception's type/message while the JSON stays one physical line; the other confirms `build_failed()`'s own emitted record never carries a `traceback` field (the design boundary from L20/D-06/T-03-05). Corrected `docs/architecture/http-api.md`'s Logging section to describe the new `traceback` field and the boundary it respects. Did not touch `decision_log.md`'s L20 entry (append-only; this is a bug fix inside L20's stated design, not a new decision).

## WR-01: `model()`'s exception handling only covers three known classes -- anything else vanishes from spur's own log vocabulary

**Files modified:** `src/spur/app.py`, `tests/test_api.py`, `docs/architecture/http-api.md`
**Commit:** `a2a2371`
**Applied fix:** Added a catch-all `except Exception as exc: build_failed(...); raise` in `model()`, after the three existing named-class `except` clauses. During review-context verification I found the naive placement from REVIEW.md's suggested fix would also catch `_build_slot()`'s own admission-control `HTTPException` (raised from inside the same `try` block for the 503 "busy" case, which already calls `queue_refused()` itself) -- that would have produced a spurious duplicate `build.failed` record alongside the correct `queue.refused` one. Adapted the fix by adding `except HTTPException: raise` immediately before the catch-all, so admission-control refusals still pass through untouched. Added a new test that drives an unexpected exception class (`MemoryError`) through `model()` via the injected build backend, asserts exactly one `build.failed` record naming that class at ERROR level, and confirms (via `pytest.raises`) the exception still propagates unhandled rather than being swallowed. Also added a regression assertion to the existing queue-saturation test confirming the busy-refusal path still emits no spurious `build.failed`. Updated `docs/architecture/http-api.md`'s Logging table to describe the catch-all.

## WR-02: `test_calc_module_stays_log_free` only catches a literal `import logging`, not `from .records import ...`

**Files modified:** `pyproject.toml`, `tests/test_records.py`
**Commit:** `482c936`
**Applied fix:** Added the import-linter contract `"The gear maths stays free of the logger"` (`source_modules = ["spur.calc"]`, `forbidden_modules = ["spur.records", "logging"]`), matching the shape of the existing CAD-kernel contract. Verified `make lint-imports` reports all 5 contracts KEPT, including the new one. Also broadened the existing regex test to additionally flag `from .records`, `from spur.records`, and `import spur.records` -- belt and suspenders, matching the CAD-kernel boundary's existing pattern of both a doc-adjacent test and an enforced contract.

## Skipped Issues

None -- all in-scope findings were fixed.

---

_Fixed: 2026-09-24T11:21:07Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
