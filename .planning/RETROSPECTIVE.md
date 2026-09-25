# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v0.1 — Hardening

**Shipped:** 2026-09-25
**Phases:** 5 (2–6) | **Plans:** 21 | **Sessions:** not tracked

### What Was Built
- CAD builds run in `BuildPool` worker processes, off the serving event loop; the serving
  process is import-linter-forbidden from the kernel; per-build timeout (30 s), three
  failure-mode status codes, pool state on `/api/health`; memory ceiling swept on the real
  N-worker topology and `compose.yaml` `mem_limit: 4g` set from it (L17–L19).
- Structured JSON logging (`records.py`) configured at both composition points, five
  decision-branch records proven by `caplog`/`json.loads` tests; `calc.py` provably
  log-free (L20).
- `DerivedDimensions`, `HealthReport`/`PoolState` typed contracts; mypy
  `disallow_any_explicit` on globally with no suppressions (L21).
- CI as the merge gate: repo-owned `commit-msg` hook, `make pr.land PR=N`, a ruleset on
  `main`, Python 3.12 only (L22, L23).
- Five debt records retired in Phase 6: mesh-free cached solid (L24), whole-buffer hook,
  run-conclusion check, effective job names, honest post-merge report (L25).

### What Worked
- Measurement before knobs. Every runtime number — build timeout, `mem_limit`, gzip level,
  healthcheck timeout — came from `make bench` runs recorded in `bench/RESULTS.md`, and
  each superseding decision-log entry cites the run. No L07-style formula was carried
  forward.
- Review-then-verify caught real defects in-milestone: 02-REVIEW CR-01/CR-02 (pool
  cancellation, sweep ceiling), 05-REVIEW CR-01 (pr.land cut-line bypass), the cross-CLI
  review of PR #4 (run conclusion, drift-test names, post-merge blame). All closed before
  the milestone closed.
- Debt files with named triggers survived context resets; Phase 6 was scoped straight from
  the ledger and the first milestone audit, not from memory.
- Small phases: 3–6 plans each, 9–35 min of executor time per plan except the
  benchmark-bound 02-04.

### What Was Inefficient
- 02-04 (~2 h) was dominated by waiting on benchmark runs and eight latency re-runs chasing
  a ≤2.00x bar the harness could not resolve at its ~0.1 ms floor; it ended in a human
  waiver that is now `must` debt.
- Phase 5's premise ("the CI workflow never ran") was false — 13 runs already existed —
  and was discovered only at context time. A live read before the roadmap would have
  reframed it a phase earlier.
- Two squash commits reached `main` with no CI run because the ship-note's skip token rode
  into the squash body. Closing that hole took Phase 5 and part of Phase 6.
- GSD's verifier fingerprints `.planning/STATE.md`, which the very next GSD step rewrites,
  so every phase reads `stale` at ship and close time. Phase 6 shipped by hand with the
  cause proven from the digest; the milestone closed as an override for the same reason.
- Phase 6 lost small re-runs to a plan's own `-k` selector colliding with an existing test
  name and to a metadata-commit timeout (06-02, 06-03 issues).

### Patterns Established
- Pure decision core behind a thin shell (`bench/memory.py`, `scripts/pr_land.py`): refusals
  are plain functions over parsed JSON, provable offline; one live probe through the real
  `gh` as the tracer.
- Content equivalence (triangle count + decoded volume) instead of byte equality for OCCT
  outputs — export matched byte-for-byte in only 8 of 20 reruns.
- Decision log is append-only; a superseding entry names what it supersedes and cites the
  measurement (L17/L18 over L06/L07, L21 over L14, L23 over L01, L25 amends L22).
- Debt is retired inside the plan that fixes it, in a content-carrying commit;
  `Resolved in:` names the code-fix sha.
- TDD RED and GREEN land in one commit: the pre-commit hook runs the full `make verify`
  with no bypass, so a failing commit cannot exist.
- `.planning/` rides the phase branch and lands in the same PR as the code
  (`commit_docs: true`); the milestone close is itself a PR through `make pr.land`.

### Key Lessons
1. A bar at the instrument's noise floor is not a bar. Measure the harness first, or set the
   threshold above what it can resolve.
2. Verify a phase's premise with a live read before planning it.
3. Anything that becomes `main`'s commit message (the PR title and body, after D-03) must
   pass the same token check as a commit — one importable definition, two call sites.
4. Never fingerprint a file the workflow itself rewrites; bookkeeping files in
   `covered_files` make every verification stale by construction (upstream GSD behaviour).
5. When the tool's gate and the substance disagree, prove the cause from the artefact
   (recompute the digest at the candidate commits) and record it, rather than re-running
   the verifier to re-stamp an identical tree.

### Cost Observations
- Model mix: not recorded — this repo keeps no per-session model accounting.
- Sessions: not tracked.
- Notable: ~8 h 45 min of executor time across 21 plans (STATE.md per-plan table); Phase 2's
  five plans took 3 h 49 min of it, 02-04 alone ~2 h.

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v0.1 | n/a | 5 | Phase branches + PR + `make pr.land` replaced direct pushes to `main`; ruleset on `main` |

### Cumulative Quality

| Milestone | Tests | Coverage | Zero-Dep Additions |
|-----------|-------|----------|-------------------|
| v0.1 | 191 | not measured (no coverage floor — `nice` debt) | 0 — `pyproject.toml` deps unchanged, `requirements.txt` 31 → 31 pins |

### Top Lessons (Verified Across Milestones)

1. (one milestone so far — nothing cross-validated yet)
