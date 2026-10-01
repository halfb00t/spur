---
phase: "13"
slug: "latency-bar"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-01"
---

# Phase 13 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded by plan-phase from `13-RESEARCH.md` "## Validation Architecture". Most of this
> phase is measurement recorded in prose (`13-LATENCY-INVESTIGATION.md`, `bench/RESULTS.md`,
> L32); the only test-suite-visible change is D-15's third `bench/latency.py` scenario and,
> if outcome (b) is taken, D-10's pass-bar formula. The Per-Task map is filled by the planner
> and audited by validate-phase.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 (Python 3.12, `.venv`; `pyproject.toml` pins `pytest>=8`) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` |
| **Quick run command** | `make test PYTEST_ARGS="-k <pattern>"` (any subset via `PYTEST_ARGS`) |
| **Full suite command** | `make verify` (ruff, mypy `--strict`, import contracts, unfinished-work scan, pytest) |
| **Estimated runtime** | ~218 s wall for `make verify` at Phase 12's end (907 tests; `bench/RESULTS.md` "Composition pass test cost (Phase 12, D-10)", run B2). Phase 15 re-measures per stage. |

---

## Sampling Rate

- **After every task commit:** Run `make test PYTEST_ARGS="-k <the task's test pattern>"` — for this phase that is the one new `tests/test_bench.py` row (D-15) and, only if outcome (b) is taken, the pass-bar unit test (D-10)
- **After every plan wave:** Run `make verify` (the pre-commit hook runs it on every `git commit` regardless — D-18)
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** ~218 s — `make verify` is the only automated tier the repo has (no `pytest-xdist`, no scoped hook); the quick command is the developer's loop between commits, not a replacement for the hook

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 13-01-T1 (tracer) | 01 | 1 | REQ-latency-observations-explained | T-13-01, T-13-02 | runs only against a server on 8001 it started; no output overwritten | e2e tracer | `ruff check .planning/phases/13-latency-bar/investigation/`; python check of `tracer-run1` JSONL + summary; `lsof` 8001 empty | created in task | ⬜ pending |
| 13-01-T2 | 01 | 1 | REQ-latency-observations-explained | T-13-01..04 | preflight (lock, 8001, fleet-user, clean src/bench), listener-PID check | script self-check + recompute | `tabulate.py --self-check`; `tabulate.py --check tracer-run1 tracer-C-run1 tracer-C-run2`; `tracer-C.status.json` check | created in task | ⬜ pending |
| 13-02-T1 | 02 | 2 | REQ-latency-observations-explained | — | — | checkpoint:decision (D-08 order) | `git diff --quiet 9f26052 -- src bench` | — | ⬜ pending |
| 13-02-T2 | 02 | 2 | REQ-latency-observations-explained | T-13-05 | predictions committed before data | structural | headings/prediction-rows python check; last commit subject contains `pre-register` | created in task | ⬜ pending |
| 13-02-T3 | 02 | 2 | REQ-latency-observations-explained | T-13-06 | the human stops fleet-user | checkpoint:human-verify | fleet-user not Up/Restarting and spur-spur-1 Up (`docker ps`) | — | ⬜ pending |
| 13-03-T1 | 03 | 3 | REQ-latency-observations-explained | T-13-08, T-13-09 | one session at a time; aborted/non-decisive marked | measurement + recompute | six `done` pair sessions; `tabulate.py --check` on twelve runs; every run after the pre-registration commit; src/bench clean, 8001 empty, no lock | — | ⬜ pending |
| 13-03-T2 | 03 | 3 | REQ-latency-observations-explained | T-13-10 | Predictions unchanged since pre-registration | structural (content Manual-Only) | Predictions diff against the `pre-register` commit; Verdict has both observations with a ruling and a run label | — | ⬜ pending |
| 13-04-T1 | 04 | 4 | REQ-latency-bar-demonstrated-or-superseded | T-13-11..13 | unmodified harness on 8001; fixed verdict and retry rules | measurement + structural | exactly one decisive `bar-*` status; every captured ratio in RESULTS; `bench/latency.py` and src unchanged; 8001 empty | — | ⬜ pending |
| 13-04-T2 | 04 | 4 | REQ-latency-bar-demonstrated-or-superseded | — | — | checkpoint:decision (D-09, D-10 gate; outcome b only) | `git diff --quiet HEAD -- src bench/latency.py bench/README.md` | — | ⬜ pending |
| 13-05-T1 | 05 | 5 | REQ-latency-bar-demonstrated-or-superseded | T-13-14, T-13-15 | the bar rule pinned at its boundary | unit (tdd; outcome b only) | `make test PYTEST_ARGS="tests/test_bench.py -q"`; `make lint typecheck`; src and fixture unchanged | Wave 0 test created in task (outcome b only) | ⬜ pending |
| 13-05-T2 | 05 | 5 | REQ-latency-bar-demonstrated-or-superseded | T-13-14 | — | measurement + structural | re-measure section present, decisive, captured ratios copied, one outcome phrase; 8001 empty | — | ⬜ pending |
| 13-05-T3 | 05 | 5 | REQ-latency-bar-demonstrated-or-superseded | T-13-16 | — | checkpoint:decision (D-11; on a miss only) | `git diff --quiet HEAD -- src bench/latency.py bench/README.md` | — | ⬜ pending |
| 13-06-T1 | 06 | 6 | REQ-latency-bar-demonstrated-or-superseded | T-13-17 | no-argument run stays concurrent, single | unit (tdd) | `make test PYTEST_ARGS="tests/test_bench.py -k 'composed_latency or no_argument_latency or reason_the_server_gave' -q"`; `make lint typecheck lint-imports`; bar scenario text byte-identical to 9f26052 | Wave 0 test created in task | ⬜ pending |
| 13-06-T2 | 06 | 6 | REQ-latency-bar-demonstrated-or-superseded | T-13-18, T-13-19 | own fresh server; worst row seen holding a slot | measurement + recompute | ruff + `tabulate.py --check sc3-run1`; `sc3` status/summary check; 8001 empty | — | ⬜ pending |
| 13-06-T3 | 06 | 6 | REQ-latency-bar-demonstrated-or-superseded | T-13-20 | — | structural | ten per-request rows copied into RESULTS; RESULTS append-only; src unchanged | — | ⬜ pending |
| 13-07-T1 | 07 | 7 | REQ-latency-bar-demonstrated-or-superseded | T-13-21..23 | L18 untouched; numbers from the record | structural | decision-log deleted lines 0; L32 last, unique, ratios in the record; Dockerfile comment-only change; debt file in exactly one place, one INDEX row | — | ⬜ pending |
| 13-07-T2 | 07 | 7 | REQ-latency-bar-demonstrated-or-superseded | T-13-24 | the human restores fleet-user | checkpoint:human-verify + phase gate | src/fixture clean, 8001 empty, spur-spur-1 Up; `make verify` | — | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_bench.py` — a new row pinning D-15's SC3 scenario's row selection against `bench/sweeps/composed.json` (1-based indices 4, 2, 3, 1, 9, 6, 10, 12, 11, 5), in the shape of `test_the_composed_sweep_stacks_each_cutout_on_its_heaviest_bore_beside_six_baselines` (`load_sweep` + exact `want` list) — written first (RED) inside 13-06 Task 1 as `test_the_composed_latency_scenario_fires_the_worst_composed_row_first_then_the_next_nine_heaviest`, beside `test_the_no_argument_latency_run_is_still_concurrent_then_single` and `test_a_503_is_recorded_by_the_reason_the_server_gave`
- [ ] The investigation scripts' own boundary cases (MIN_SAMPLES 19/20, p94/p96 at 99/100, ratio exactly 2.0, segment boundary, empty series) — `tabulate.py --self-check`, written in 13-01 Task 2; outside `make verify` by design (D-03)
- [ ] Only if outcome (b) adopts D-10's floor formula (`max(2.00 × idle_p95, idle_p95 + M)`): a unit test over `bench/latency.py`'s pass/fail decision (`_p95_or_warn` / `_report_markdown`) pinning at least one case where the ratio alone passes but the floor keeps it failing, or vice versa — this decision path has no unit test today
- [ ] No fixture or conftest gap for the investigation itself — it lives under `.planning/phases/13-latency-bar/investigation/` and is outside `make verify` by design (D-03)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The write-up names, per observation, the surviving candidate and the ruling measurement; predictions pre-registered before the first run | REQ-latency-observations-explained | SC1 forbids any `src/`/`bench/` change — nothing for `make verify` to assert | Read `13-LATENCY-INVESTIGATION.md` against the raw JSONL and per-run summaries under `investigation/`; both repetitions of each pair must point the same way (D-04) |
| `scenario_concurrent` ≤ 2.00× on both runs of one decisive session, OR L32 logged with the measured reason and re-measured on the changed harness | REQ-latency-bar-demonstrated-or-superseded | A live measurement on a quiet host (D-05); the number legitimately varies run to run | Read the new session tables in `bench/RESULTS.md` (host-state header, both runs, decisive/non-decisive marking) and L32 in `docs/architecture/decision_log.md` |
| The composed worst row under ten concurrent builds, recorded whatever it reads, with the per-request table and `workers_replaced` before/after | REQ-latency-bar-demonstrated-or-superseded (SC3) | One live run on a fresh server (D-16) | Read the SC3 section of `bench/RESULTS.md`; confirm the row count is ten and each row has an outcome |
| Debt file retired in the demonstrating/superseding commit; L18 untouched, L32 appended; Dockerfile `HEALTHCHECK` comment sentence updated to the new run count and worst reading | REQ-latency-bar-demonstrated-or-superseded (SC4) | File move + git log inspection | `git log --follow docs/tech_debt/resolved/2026-09-23-concurrent-latency-bar-waived.md`; `docs/tech_debt/INDEX.md` row moved; `Dockerfile` lines 41–50 |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 300s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
