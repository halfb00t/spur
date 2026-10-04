# No coverage floor in the gate

Severity: nice
Status: resolved
Date: 2026-09-21
Resolved in: test(15-02): gate make verify on a coverage floor set from the measured baseline
Source: setting up the gate (L13)
Related files:
- pyproject.toml (`[tool.coverage.run]`)
- Makefile (`verify`)

## Context

`[tool.coverage.run]` is configured with `branch = true` and `source = ["src/spur"]`, but
nothing measures coverage in `make verify` and there is no `fail_under`. `pytest-cov` was
not installed -- `pip show pytest-cov` was empty on 2026-10-01 (REQUIREMENTS.md
REQ-coverage-floor); 15-01 added it to `[dev]`.

The reason is deliberate: a floor picked before measuring is a number, not a guarantee,
and a floor set too low is worse than none because it reads as approval.

## Why it matters

Low, today: 50 tests cover the geometry, the API, the CLI and the STL topology, and the
existing suite was written against a review that measured what it was testing. The risk
is drift — new code landing with no test and nothing noticing until someone looks.

## Next step

Run `pytest --cov` once, read the real number, set `fail_under` just under it, and add
`--cov --cov-fail-under` to the `test` target so it gates. Then this file moves to
`resolved/`.

Revisit when: immediately after one measured baseline run — this is a ten-minute item
being held only until the number exists.

## Resolution (2026-10-04)

Phase 15 measured the baseline and set the floor (all numbers in `bench/RESULTS.md`, "The
gate, measured and pinned (Phase 15)"):

- Baseline: one serial `--cov` run, C0, read 96.99 % (1,069 statements, 294 branches, 26
  missed) with 927 passed -- "Coverage baseline". Worker lines are counted: BuildPool's
  workers are spawned processes and `pytest-cov` 7 has no subprocess hook, so
  `[tool.coverage.run]` carries `concurrency = ["multiprocessing", "thread"]`,
  `parallel = true` and `sigterm = true`; `tests/test_pool.py` alone reads `pool.py` at
  100.00 % serially and at `-n 2`.
- Tolerance: three `-n 8 --cov` runs, B1-B3, read 97.21 % each (23 missed), spread 0.00
  points, all six alternating runs green -- "Tolerance and coverage cost". Coverage costs
  3.51 s at `-n 8` (mean 60.61 s without, 64.12 s with).
- Floor: `fail_under = 96`, D-10's rule: floor(L - max(0.25, S)) with L = 96.99 (the lowest
  total, C0) and S = 0.00 -- "Coverage floor". `precision = 2`, so a total of exactly 96.00
  passes and 95.99 fails. C0 had lost three worker statements to the unexplained flush
  loss of 15-RESEARCH Pitfall 13 (0.22 points); the floor's slack covers it.
- Gate: `make test` runs `--cov` and reads the floor from `[tool.coverage.report]
  fail_under` alone; no `--cov-fail-under` anywhere. Partial runs pass `--no-cov`.
- Red on the floor: a full run without `tests/test_cli.py` read 90.24 % against 96 and
  exited non-zero -- "Red on the floor".

`docs/architecture/decision_log.md` L34 (written by 15-06) logs it.
