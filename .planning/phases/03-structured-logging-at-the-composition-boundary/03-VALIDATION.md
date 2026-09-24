---
phase: "3"
slug: "structured-logging-at-the-composition-boundary"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-09-24"
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8+ (`pyproject.toml` `dev` extra `pytest>=8`) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` — `testpaths = ["tests"]`, `filterwarnings = ["error", ...]` |
| **Quick run command** | `.venv/bin/python -m pytest tests/test_api.py tests/test_pool.py -q` |
| **Full suite command** | `make verify` |
| **Estimated runtime** | ~30 seconds for pytest alone (76 tests, 29.02s measured in research); `make verify` adds ruff, mypy `--strict`, import-linter and the unfinished-work scan |

---

## Sampling Rate

- **After every task commit:** Run `.venv/bin/python -m pytest tests/test_api.py tests/test_pool.py -q`
- **After every plan wave:** Run `make verify`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** ~60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| T1 — One request, one JSON line (tracer) | 03-01 | 1 | REQ-structured-logging | T-03-01, T-03-02, T-03-04 | Only already-public `GearParams` values, counters, a local id and a duration leave the process; `json.dumps(..., default=str)` cannot raise inside a log call | integration (end-to-end: configure → request → formatted line → `json.loads`) | `make test PYTEST_ARGS="tests/test_records.py -q"` | ❌ new file (created by this task) | ✅ green |
| T1 — import boundary of the new module | 03-01 | 1 | REQ-structured-logging | — | `records.py` reaches neither the CAD kernel nor the web framework, so `spur.cli` and `spur.app` can both import it without violating the four existing contracts | static (import-linter) | `make lint-imports` | ✅ `pyproject.toml` contracts exist | ✅ green |
| T2 — per-request vocabulary | 03-01 | 1 | REQ-structured-logging | T-03-01 | The identity that rides on every record is built in one place (`_gear_fields`), so a future field cannot be added at one call site only | unit/contract (`caplog`, `set_level(INFO)` + non-empty assertion) | `make test PYTEST_ARGS="tests/test_api.py -q"` | ✅ `tests/test_api.py` | ✅ green |
| T3 — line format and level knob | 03-01 | 1 | REQ-structured-logging | T-03-02, T-03-04 | A newline-bearing value cannot forge a second log line; a double `configure()` cannot double-print | unit (formatter round-trip, `_parse_level`, idempotency, `calc.py` negative check) | `make test PYTEST_ARGS="tests/test_records.py -q"` | ❌ new file (created in T1) | ✅ green |
| T3 — `calc.py` stays log-free | 03-01 | 1 | REQ-structured-logging | — | The pure-maths module that runs on every keystroke gains no logging import (L01) | static (inverted grep) | `! grep -nE '^[[:space:]]*(import\|from)[[:space:]]+logging' src/spur/calc.py` | ✅ `src/spur/calc.py` | ✅ green |
| T1 — `build.failed` | 03-02 | 2 | REQ-structured-logging | T-03-05, T-03-08 | The exception **class name** is published, never traceback text; attacker-influenced values are JSON-serialized, never interpolated | unit/contract (`caplog`, parametrized over three exception classes) | `make test PYTEST_ARGS="tests/test_api.py -q"` | ✅ `tests/test_api.py` | ✅ green |
| T1 — response contract unchanged | 03-02 | 2 | REQ-structured-logging | — | Status codes, `detail[].type` values and `Retry-After` headers move only when someone means to move them | regression (pre-existing test) | `make test PYTEST_ARGS="tests/test_pool.py -q"` | ✅ `tests/test_pool.py` | ✅ green |
| T2 — `queue.refused` | 03-02 | 2 | REQ-structured-logging | T-03-07 | One WARNING record per refused request, bounded by the admission control that already bounds builds (L04) | unit/contract (`caplog`, every slot held) | `make test PYTEST_ARGS="tests/test_api.py tests/test_pool.py -q"` | ✅ both files | ✅ green |
| T3 — `worker.replaced` | 03-02 | 2 | REQ-structured-logging | T-03-06 | Emitted inside `recreate_for`'s identity guard, so one incident produces exactly one record — the log agrees with the counter | integration (real pool, real subprocess) + regression (one-record-per-incident) | `make test PYTEST_ARGS="tests/test_pool.py -q"` | ✅ `tests/test_pool.py` | ✅ green |
| T3 — emission site is the guard, not the callers | 03-02 | 2 | REQ-structured-logging | T-03-06 | A CR-01/WR-01 double-count regression in the log is caught structurally, not by review | static (grep for the call's location) | `grep -n 'worker_replaced' src/spur/pool.py` | ✅ `src/spur/pool.py` | ✅ green |
| T1 — `L20` decision checkpoint | 03-03 | 3 | REQ-structured-logging | T-03-09 | A one-way, append-only record is confirmed by a human before it becomes permanent | checkpoint (blocking, no automated verify by design) | — (blocking human decision) | n/a | ✅ green (resolved by human: option A, 2026-09-24) |
| T2 — `L20` appended | 03-03 | 3 | REQ-structured-logging | T-03-09 | History is never rewritten to look cleaner: the diffstat must add lines only | static (grep + diffstat) | `git diff --stat HEAD -- docs/architecture/decision_log.md` | ✅ `docs/architecture/decision_log.md` | ✅ green |
| T3 — docs true + debt retired in one commit | 03-03 | 3 | REQ-structured-logging | T-03-10, T-03-11, T-03-12 | The debt file is `git mv`'d (history follows it) with a resolvable fix sha, and only after the gate passes | static (file-move and sha gates) + the phase gate | `make verify` | ✅ all targets exist | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

All three gaps are closed inside Plan 03-01, wave 1 — the wave that also creates the module
they cover, so nothing in wave 2 or 3 waits on a missing scaffold.

- [x] `tests/test_records.py` — JSON formatter round-trip test (`json.loads` on an emitted record proves `extra` fields survive) and `SPUR_LOG_LEVEL` parsing tests — new file; no logging module exists yet. **Created by 03-01 Task 1, extended by 03-01 Task 3.**
- [x] `tests/conftest.py` — autouse root-logger reset, so every `configure()` test starts unconfigured and no test leaks a handler bound to a captured stream into the rest of the session. New file; the suite has no conftest today. **Created by 03-01 Task 1.**
- [x] Every D-16 branch test (`build.started`, `build.failed`, `export.served`, `queue.refused`, `worker.replaced`) needs `caplog.set_level(logging.INFO)` **and** a non-empty `caplog.records` assertion — `caplog` defaults to WARNING (reproduced live in research), so an unguarded INFO test passes while exercising nothing. The suite has zero `caplog` precedent today. **Required by acceptance criteria on 03-01 T2 and all three 03-02 tasks.**
- [x] `calc.py` stays log-free — a one-line negative assertion in `tests/test_records.py` plus an inverted-grep gate, cheap insurance against drift. **03-01 Task 3.**
- No framework install needed — pytest's `caplog` fixture is built in, and this phase installs no package at all (stdlib only, D-01).

---

## Manual-Only Verifications

All phase behaviors have automated verification. One task — 03-03 Task 1 — is a blocking
human decision checkpoint rather than a behavior: `docs/architecture/decision_log.md` is
append-only by policy, so `L20` is confirmed before it becomes permanent. It has no
automated verify by design; the entry it gates does (03-03 Task 2).

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 60s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** validated 2026-09-24 — execute-phase `verify:post` nyquist hook (no gaps; no auditor spawn needed)

---

## Validation Audit 2026-09-24

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |

Every automated row in the Per-Task Verification Map has a green counterpart at `945219a`
(`make verify`: ruff, mypy `--strict`, 4/4 import contracts kept, 96 tests). Static gates
re-run at audit time: `worker_replaced(` appears once in `src/spur/pool.py` (inside
`recreate_for`'s guard); `c8b7fc8` (L20) is insertions-only; `calc.py` has no `logging`
import and `tests/test_records.py::test_calc_module_stays_log_free` pins it; the debt file
moved as `R057` in `013997a`, the same commit as the docs fixes. The single non-automated
row (03-03 T1) is a `checkpoint:decision`, not a behavior — resolved by the human as
option A — so `nyquist_compliant: true` holds for every phase behavior.
