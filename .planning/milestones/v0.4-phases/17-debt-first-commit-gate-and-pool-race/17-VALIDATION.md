---
phase: "17"
slug: "debt-first-commit-gate-and-pool-race"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-10-06"
validated: "2026-10-06"
---

# Phase 17 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded from `17-RESEARCH.md` § Validation Architecture; the per-task map was filled from the five plans and their SUMMARY `coverage:` blocks after execution (validate-phase, 2026-10-06).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 + pytest-xdist (`-n 8`, clamped to the host) + pytest-cov; `filterwarnings = ["error", ...]`, `--strict-markers --strict-config` |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]`; coverage floor `fail_under = 96` |
| **Quick run command** | `make test PYTEST_ARGS="<paths or -k> -q --no-cov"` (PYTEST_ARGS comes last, so `--no-cov` wins) |
| **Full suite command** | `make verify` (62–73 s warm on the dev host across this phase's five post-wave runs; the pre-push gate since L36) |
| **Commit-time subset** | `make verify.fast` — 11.3 s warm, 19.9 s with an empty mypy cache (17-01, four timed readings); the pre-commit hook since L36 |

---

## Sampling Rate

- **After every task commit:** the pre-commit hook runs `make verify.fast` (everything but `test_pool.py`, `test_model.py`, `test_api.py`, `test_cli.py`); heavy files run explicitly by the task's row
- **After every plan wave:** `make verify` (orchestrator post-merge gate: 937 → 939 → 943 passed, coverage ≥ 97.03 % on every run)
- **Before `/gsd-verify-work`:** full suite green (`943 passed in 71.56s`, 97.25 %, after wave 5)
- **Max feedback latency:** ~73 s (full gate), ~12 s (commit subset)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 17-01 T1 (tracer) | 17-01 | 1 | REQ-hook-and-commit-timeout-decided | T-17-01 | hooks never bypassed (no `--no-verify`, no `SKIP=`) | unit + structural | `make test PYTEST_ARGS="tests/test_hooks.py -q --no-cov"` (3 passed; 3 failed against the unedited tree); `make -n verify` lists the static recipes before exactly one pytest line | ✅ | ✅ green |
| 17-01 T2 | 17-01 | 1 | REQ-hook-and-commit-timeout-decided | — | N/A | scratch-repo measurement + grep | nine pre-push scenarios in a scratch bare repo (table in 17-01-SUMMARY; row 5 needs a named remote, caveat in L36); `grep -n "^## L36" docs/architecture/decision_log.md` | ✅ | ✅ green |
| 17-01 T3 | 17-01 | 1 | REQ-hook-and-commit-timeout-decided | T-17-04 | the gate decides what passes | full gate + plain commit through the new stage | `make verify` (937 passed, 65.69 s); hook commit `c06749d` passed `verify-fast` in 12.33 s | ✅ | ✅ green |
| 17-02 T1 | 17-02 | 2 | REQ-hook-and-commit-timeout-decided | — | N/A | live pre-push + shallow clone | `git push <scratch bare> HEAD:refs/heads/probe` → `make verify (…)….Passed`, real 63.97; `--depth 1` clone: `pre-commit install` wrote all three hooks (macOS; Linux CI read at ship) | ✅ | ✅ green |
| 17-02 T2 (checkpoint:human-verify, blocking-human) | 17-02 | 2 | REQ-hook-and-commit-timeout-decided | — | nothing posted in the human's name unread | human gate | issue text approved verbatim → open-gsd/gsd-core#5231 (`gh issue view 5231` OPEN) | ✅ | ✅ green |
| 17-02 T3 | 17-02 | 2 | REQ-hook-and-commit-timeout-decided | — | N/A | live SDK commit (SC1) | `node ~/.claude/gsd-core/bin/gsd-tools.cjs query commit …` → `committed: true`, hash `5a3332f` = HEAD, real 13.57 s (`17-02-sdk-commit.json`) | ✅ | ✅ green |
| 17-03 T1 | 17-03 | 3 | REQ-same-slot-timeout-race-reproduced | — | N/A | unit | `make test PYTEST_ARGS="tests/test_bench.py -q --no-cov"` (26 passed; 5 new tests, RED on `ImportError` first) | ✅ | ✅ green |
| 17-03 T2 | 17-03 | 3 | REQ-same-slot-timeout-race-reproduced; REQ-worst-row-margin-decided (D-11 reading) | — | N/A | live bench, recorded | `.venv/bin/python -m bench.latency --base-url http://127.0.0.1:8001 identical` on a fresh server → `Reproduced in attempt 1.` (three `500` rows, three `build.failed` `AttributeError`); automated check `attempts ['1'] hits [True]` | ✅ | ✅ green |
| 17-04 T1 | 17-04 | 4 | REQ-same-slot-timeout-race-fixed | — | documented `503 timeout`, never an unhandled `AttributeError` | unit (RED first) | `make test PYTEST_ARGS="tests/test_pool.py -k 'stale_executor or same_tick or closed_pool or never_awaits' -n0 --no-cov"` → `3 failed, 1 passed` against the unfixed pool (ast tripwire passes by design) | ✅ | ✅ red-as-designed, then green |
| 17-04 T2 (checkpoint:decision, blocking-human) | 17-04 | 4 | REQ-same-slot-timeout-race-fixed | — | N/A | D-17 gate | verdict-line check: `Reproduced in attempt 1.` → checkpoint not presented, `pool.py` unchanged before it | ✅ | ✅ green |
| 17-04 T3 | 17-04 | 4 | REQ-same-slot-timeout-race-fixed | — | documented `503 timeout` | unit + repeat loops + full gate | same `-k` command → `4 passed`; `tests/test_pool.py tests/test_api.py` 20× `-n 8 --cov` 20/20, 20× `-n 4 --cov` 20/20; `make verify` 2/3 (run 2: resource-tracker flake, accepted `proceed-as-known-flake`, debt trigger fired `b8ef84a`) — `investigation/17-04-stability.md` | ✅ | ⚠️ flaky gate (tests ✅ green) |
| 17-05 T1 | 17-05 | 5 | REQ-same-slot-timeout-race-fixed | — | N/A | live bench after the fix, recorded | same scenario on `0628182` → four `503 timeout`, zero `500`, no `AttributeError`, `workers_replaced` 0→1; automated check `after the fix: 1 run(s), zero 500s, no AttributeError` | ✅ | ✅ green |
| 17-05 T2 | 17-05 | 5 | REQ-worst-row-margin-decided | — | no default or cap moves (L05) | grep / diff + docs tests | `grep -n "^## L37" docs/architecture/decision_log.md`; `git diff e64d764 -- src/spur/params.py` empty, `app.py` comment-only; `make test PYTEST_ARGS="tests/test_cli.py -q --no-cov"` 44 passed; `tests/test_api.py::…` asserts `spoke_count` maximum 32 | ✅ | ✅ green |
| 17-05 T3 | 17-05 | 5 | REQ-same-slot-timeout-race-fixed; REQ-worst-row-margin-decided | — | N/A | grep | race debt in `resolved/` names `0628182` and `7af75af`; `docs/tech_debt/INDEX.md` Active holds no `must` row; automated check `phase end state holds` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

Requirement coverage after execution: REQ-hook-and-commit-timeout-decided — COVERED (`tests/test_hooks.py`, 3 tests; live SDK commit recorded); REQ-same-slot-timeout-race-reproduced — COVERED (`tests/test_bench.py`, 5 tests); REQ-same-slot-timeout-race-fixed — COVERED (`tests/test_pool.py`, 4 tests + 40/40 loops); REQ-worst-row-margin-decided — COVERED for the behaviour (caps and defaults pinned by `tests/test_api.py`, README read by `tests/test_cli.py`); whether L37's numbers support "documented behaviour" is a judgement and stays manual-only. The three new files ran green together on 2026-10-06: `49 passed in 12.09s`.

---

## Wave 0 Requirements

- [x] `tests/test_pool.py` — four new tests (stale-executor, same-tick sibling, `_closed`, ast tripwire), run red against the unfixed `pool.py` first (17-04)
- [x] `tests/test_bench.py` — registry assertion updated; `record_500`, identical-rows and baseline-suppression tests (17-03)
- [x] `bench/latency.py` — `record_500`, `run_composed(rows, label, record_500)`, `identical` in `_SCENARIOS` only (17-03)
- [x] `Makefile` — `verify.static`, `verify.fast`, `test.fast`, hooks stamp (17-01)
- [x] `tests/test_hooks.py` — hook/target drift pin and main-checkout-only stamp test (17-01)
- [x] a bare scratch remote for the real pre-push proof (17-01 Task 2 scratch table; 17-02 Task 1 push to an empty bare repo)
- No framework install: pytest, xdist, cov already present.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Pre-push semantics (once per push, first ref, stash of unstaged changes, per-clone install) | REQ-hook-and-commit-timeout-decided | Needs a scratch repo + bare remote and a human-readable log | Done 17-01 Task 2: nine-row table in 17-01-SUMMARY, quoted in L36 (row 5 holds with a named remote) |
| Hook install on GitHub's Linux runner (A1/A3) | REQ-hook-and-commit-timeout-decided | The shallow-clone proof ran on macOS only | Read the first CI run at `/gsd-ship`: three `pre-commit installed at .git/hooks/…` lines and a green job (carried in 17-05-SUMMARY "For ship") |
| The undocumented `500` reproduces on a fresh server before the fix | REQ-same-slot-timeout-race-reproduced | Live bench on a running server; a miss is a legitimate measured outcome (L08) | Done 17-03: `Reproduced in attempt 1.` in `bench/RESULTS.md`; readout in `investigation/attempt-1.*` |
| Zero `500`s after the fix | REQ-same-slot-timeout-race-fixed | Same live bench; the deterministic test is the proof, the table is the record | Done 17-05: four `503 timeout`, zero `500` in `bench/RESULTS.md`; `investigation/after-1.*` |
| L37's numbers support "documented behaviour" rather than a different decision | REQ-worst-row-margin-decided | The automated checks prove presence and append-only, not that the reading is honest | Read L37 against `bench/RESULTS.md` (29.42 s alone, 0.58 s margin, `BuildTimeout` at `duration_ms` 30004) |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies (14/14 tasks carry at least one `<automated>` block)
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (all six W0 items shipped in waves 1–4)
- [x] No watch-mode flags
- [x] Feedback latency < 75 s (full gate), < 13 s (commit subset)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** validated 2026-10-06 by validate-phase (State A audit: 0 gaps found, 0 resolved, 0 escalated; no tests generated — every requirement already carried green automated coverage from execution)

## Validation Audit 2026-10-06

| Metric | Count |
|---|---|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |
