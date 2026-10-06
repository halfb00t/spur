# Phase 17: Debt First — Commit Gate and Pool Race - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-06
**Phase:** 17-debt-first-commit-gate-and-pool-race
**Areas discussed:** Hook choice + subset content, Install ownership + red-commit policy, Margin decision, Reproduction run protocol

---

## Hook choice + subset content

### Which hook arrangement does the Lxx lock?

| Option | Description | Selected |
|--------|-------------|----------|
| (b)+(c) subset at commit, full at pre-push | Commit hook runs a Makefile subset `verify` depends on; `make verify` moves to `stages: [pre-push]`. All three research files land here. | ✓ |
| (b) pre-push only | No commit-time checks. Any commit can be red locally; `git bisect` can land on one. | |
| (c) subset at commit only | Full gate enforced only by CI and `pr.land`. Research: "a weaker (b)". | |
| (a) upstream request only | Nothing shipped; cannot meet success criterion 1 as written. | |

**User's choice:** (b)+(c)

### What does the commit-time subset contain?

| Option | Description | Selected |
|--------|-------------|----------|
| Static + pytest slice | Static four + pytest excluding `test_model.py`, `test_pool.py`, `test_api.py`, `test_cli.py`, `-n 8 --no-cov`. 617 tests incl. `test_calc.py` and the L26 fixture replay. ~12 s warm, ~21 s cold mypy. | ✓ |
| Static only | 0.59 s warm, ~9.5 s cold. No test at commit. | |
| Static + calc-only tests | 3.9 s, 527 tests. Loses the fixture replay. | |

**User's choice:** Static + pytest slice

### How does the Makefile make the subset a prefix of `verify` without running the slice twice?

| Option | Description | Selected |
|--------|-------------|----------|
| Shared static target + same test recipe, different args | `verify.static`; `verify: verify.static test`; `verify.fast: verify.static test.fast` (the `test` recipe with `--ignore`/`--no-cov`). | ✓ |
| `verify: verify.fast test` literally | Full gate runs the slice twice: ~64 s → ~75 s, over the 66 s bar. | |
| Static-only prefix, slice outside the chain | Two pytest lists — PITFALLS 14 drift. | |

**User's choice:** Shared static target + same test recipe, different args

### How does `test.fast` pick its tests?

| Option | Description | Selected |
|--------|-------------|----------|
| Exclude heavy files by `--ignore` | No pyproject/test edits; a new test file runs at commit until named heavy. | ✓ |
| Include by path | 8.0–8.7 s; a new file is silently skipped at commit. | |
| Pytest marker | Needs a registered marker plus decorated tests. | |

**User's choice:** Exclude by `--ignore`

---

## Install ownership + red-commit policy

### Who makes sure every clone has the pre-push hook installed?

| Option | Description | Selected |
|--------|-------------|----------|
| `make venv` re-runs `pre-commit install` | The `.venv` stamp recipe installs all three hook types; config header + HOW_TO_DEVELOP §0 say "run `make venv` once". | ✓ |
| Documented command only | Same pattern D-02 used for commit-msg; nothing enforces it. | |
| A gate check that refuses when hooks are missing | Couples `make verify` to `.git` state. | |

**User's choice:** `make venv` re-runs `pre-commit install`
**Notes:** The stamp depends on `pyproject.toml` only; the re-install-on-config-change mechanism is Claude's discretion (CONTEXT D-06).

### What does an executor do when `gsd_run query commit` returns `commit_timeout`?

| Option | Description | Selected |
|--------|-------------|----------|
| Wait for the orphan, then one plain `git commit` | Confirm no hook process alive, hand-commit once with the hook allowed to finish, record it; never retry the SDK commit blind. | ✓ |
| Retry the SDK commit once, then hand commit | gsd's documented recovery; the retry overlaps the orphan. | |
| Stop and surface to the human | Every cold-cache commit stalls on the human. | |

**User's choice:** Wait for the orphan, then one plain `git commit`

### File the upstream `COMMIT_TIMEOUT_MS` knob request?

| Option | Description | Selected |
|--------|-------------|----------|
| File it, cite in the Lxx, never depend on it | Issue names the symbol, no config key, #3886 as prior art. | ✓ |
| Do not file | Saves an external action; loses the record. | |

**User's choice:** File it, cite in the Lxx, never depend on it

### Rule for the push itself under a pre-push hook and the shell tool timeout?

| Option | Description | Selected |
|--------|-------------|----------|
| Run `make verify` before every push, then push | Warms the cache; the hook runs warm (~64 s) inside the 120 s default. | ✓ |
| Push with an explicit long timeout | A five-minute silent hook on one tool call. | |
| No rule — CI is the wall | Occasional killed pushes and double gate runs. | |

**User's choice:** Run `make verify` before every push, then push

---

## Margin decision

### What does the margin Lxx decide?

| Option | Description | Selected |
|--------|-------------|----------|
| Record the limit as documented behaviour | No default moves; `503 timeout` is the contract for the heaviest composed row under load. | ✓ |
| Raise `SPUR_BUILD_TIMEOUT`'s default | Every deployment waits longer on a wedged worker; no proven margin on slower hosts. | |
| Lower `spoke_count`'s `le` again | Third lowering; links at 32 spokes start returning 422. | |

**User's choice:** Record the limit as documented behaviour

### Which measurement names the number in the Lxx?

| Option | Description | Selected |
|--------|-------------|----------|
| Existing SC3 + the identical-row run that comes free | 29.42 s alone and 30 004 ms under two-worker load, plus the same row with one busy worker and a queue. | ✓ |
| A dedicated worst-row-under-N sweep | Cleaner curve; one more bench session. | |
| SC3's existing numbers only | Nothing new measured. | |

**User's choice:** Existing SC3 + the identical-row run

### Does the recorded limit reach users, or stay in the record?

| Option | Description | Selected |
|--------|-------------|----------|
| README limits note + the 503 timeout doc | One sentence where `503 timeout` is documented, plus the dated notes in RESULTS and the tip-chamfer debt file. | ✓ |
| Record only | Lxx, RESULTS and the debt-file note only. | |

**User's choice:** README limits note + the 503 timeout doc

### What re-opens the recorded limit?

| Option | Description | Selected |
|--------|-------------|----------|
| Phase 19's composed re-measure, or any cap/timeout change | REQ-trochoid-composes-and-is-priced re-measures the heaviest row anyway. | ✓ |
| Only on a user report | Lazy; Phase 19 measures regardless. | |
| Fixed — no trigger | Nothing re-opens it short of a new Lxx. | |

**User's choice:** Phase 19's composed re-measure, or any cap/timeout change

---

## Reproduction run protocol

### Does the before-fix identical-row run wait for a quiet host?

| Option | Description | Selected |
|--------|-------------|----------|
| No gate; record load as every section does | Load widens the window; the margin number is read "at this load". | ✓ |
| Phase 13's gate with cap, non-decisive recorded | Load < 1.5 × 3 samples, 900 s cap; reached 2 of 5 sessions. | |
| Relaxed gate, load < 2.5 | A threshold picked for convenience. | |

**User's choice:** No gate; record load

### How many fresh-server runs before "the 500 did not reproduce" is recorded?

| Option | Description | Selected |
|--------|-------------|----------|
| Up to 3, each on a restarted server, all recorded | Bounds the cost; every table lands in RESULTS, hit or miss. | ✓ |
| Exactly one run | Criterion literal; one sample of a millisecond window. | |
| Until it reproduces | Open-ended. | |

**User's choice:** Up to 3, each on a restarted server, all recorded

### Who drives the bench run?

| Option | Description | Selected |
|--------|-------------|----------|
| Executor runs it end to end | Server in the background, scenario, server stopped, host state captured by the tool. | ✓ |
| Human runs it as a measurement checkpoint | The 15-03 pattern; quieter host, costs the human per attempt. | |
| Executor runs; human approves host state first | One pause per attempt. | |

**User's choice:** Executor runs it end to end

### If three runs show no 500 but the deterministic test is red before the fix?

| Option | Description | Selected |
|--------|-------------|----------|
| Checkpoint: the human chooses proceed-on-the-test or defer | Tables and red test output presented; nothing written for them. | ✓ |
| Proceed on the red test automatically | Reinterprets the roadmap's "phase stops". | |
| Hard stop — no fix without a bench 500 | Roadmap literal. | |

**User's choice:** Checkpoint: the human chooses proceed-on-the-test or defer

---

## Claude's Discretion

- Target and hook ids; the `--ignore` spelling; the hook re-install stamp mechanism.
- The scenario's name and whether `record_500` is also a CLI flag.
- A hook-drift test (recommended, not required); the orphan-worker count check (PITFALLS 11).
- The after-fix re-run count beyond one clean run.
- `Lxx` numbering (two entries after L35: hook, then margin).

## Deferred Ideas

None — discussion stayed within phase scope.
