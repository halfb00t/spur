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

## Milestone: v0.2 — Fit to Shaft

**Shipped:** 2026-10-01
**Phases:** 6 (7–12) | **Plans:** 34 | **Sessions:** not tracked

### What Was Built
- Selectors that raise on an empty selection and a 44-record pre-v0.2 fixture replayed by
  every later phase, byte-unchanged at the close (L26).
- A hex bore that replaces the round profile and a keyway slot with an explicit as-cut-wall
  datum, both with measured root-circle refusals; the round bore's chamfer reach closed at
  the kernel's measured contact (L27, L28).
- A tooth-tip chamfer capped at a kernel boundary bisected to ~2 µm (L29).
- One cutout pattern per part — spokes, holes, honeycomb — with a measured cell cap and
  every wall rule pinned one step either side on the kernel (L30).
- The composed sweep, `spoke_count` `le` 32, the 249-row composition matrix, three-interface
  parity proven model-driven, the CLI's real exit contract in its doc (L31).

### What Worked
- Gates fired and were decided, not argued away: D-06 (fixture cost 16.27 s over a 15 s
  line), D-18 (200-count rows at 42–69 s → `le` 60/40), D-03 (four composed rows over 30 s →
  a probe → `le` 32), D-10 (+28.28 s gate cost accepted). Each is one verbatim human answer
  in a SUMMARY and a numbered section in RESULTS.md.
- The fixture as the standing L05 proof: six phases of geometry changes, zero fixture edits,
  and the one time a selector silently vanished a chamfer the tripwire caught it.
- Spike before field: HEX_CELL_CAP, the tip-chamfer kernel boundary and ROOT_CONTACT were all
  measured by a throwaway probe before any schema field existed, then written as constants
  with the measurement cited.
- Cross-CLI review earned its keep on the last phase: the Codex lane found a regression test
  that could not fail (WR-06) and three over-claims in the records that the internal pass had
  read past.

### What Was Inefficient
- The composed sweep took four runs to get a decisive reading because `bench/build_time.py`
  read load at the end of a 6–7 min sweep while labelling it "at start" — a tool bug found
  only by comparing a quiet-host launch with the runner's own figure. Fixed in 12-03; the
  rationale sentence then needed a second correction (WR-07).
- `gsd_run query commit`'s 30 s timeout versus a 3.5 min `make verify` hook: every close-out
  commit had to be a plain `git commit`, and the disposition ledger's own auto-commit killed a
  hook mid-run with the review report stashed. Recovered by waiting for the orphan; the debt
  item is `nice` and now names this path.
- Phase 12 was re-verified twice over: once after UAT (canonicalized by the UAT predicate),
  once after the review fixes changed eight covered files — and the second report was pushed
  seven minutes after the user had already landed the PR by hand, so it reached `main` via a
  cherry-pick on the close branch. Land-then-verify and verify-then-land need one owner.
- Stale-by-fingerprint again, from the other side: v0.1's reports went stale because they
  fingerprinted STATE.md; v0.2's went stale because a later phase legitimately changed shared
  files. Both closes were overrides with the cause proven; neither reflects unverified code.

### Patterns Established
- Append-only decision log with in-place rewording allowed only for text added in the same
  PR (0 deleted lines against the branch base) — how both WR-02 (L30) and WR-05/07/08 (L31)
  were corrected.
- Measurements are records: prose claims in RESULTS.md may be corrected, numbers and run
  headings never; a decision's evidence sentence can be wrong while the decision stands.
- A gate's offer is a number from a probe (`spoke_count` 32: 29.41 s inside, 33: 30.11 s
  over), never a round figure.
- Human-judgment items are listed in VALIDATION.md's manual-only table so UAT presents them
  once instead of treating them as untested.
- `--files` plus the phase-start base when the incremental review scope is empty but a
  second reviewer lane is wanted.

### Key Lessons
1. Label a reading by when it was taken; a load figure read at the wrong end of a run is
   worse than none (12-02/12-03, WR-07).
2. A regression test is only a test if the bug it names makes it fail — check the fixture
   arithmetic against the regressed branch, not just the correct one (WR-06).
3. Hooks that take minutes need commits that wait minutes; a tool with a 30 s commit timeout
   must not be allowed to commit in this repo at all.
4. When the PR is landed by hand, say so in the session before anything else is pushed —
   a verification report that misses the squash costs a cherry-pick and a second PR.
5. Shared files make earlier phases' digests stale by construction; record the cause once
   per close rather than re-running five verifiers to re-stamp identical trees (same lesson
   as v0.1 #5, second occurrence).

### Cost Observations
- Model mix: not recorded — this repo keeps no per-session model accounting.
- Sessions: not tracked.
- Notable: ~11 h 45 min of executor time where measured (Phases 7–10); Phase 12's close-out
  (UAT, three audits, two review passes, re-verification, the milestone close) ran through
  nine `make verify` hook runs of ~3.5 min each.

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v0.1 | n/a | 5 | Phase branches + PR + `make pr.land` replaced direct pushes to `main`; ruleset on `main` |
| v0.2 | n/a | 6 | Build-time gates as human checkpoints with probe-derived offers; cross-CLI (Codex) review lane on the last phase; Nyquist + security audits at verify:post |

### Cumulative Quality

| Milestone | Tests | Coverage | Zero-Dep Additions |
|-----------|-------|----------|-------------------|
| v0.1 | 191 | not measured (no coverage floor — `nice` debt) | 0 — `pyproject.toml` deps unchanged, `requirements.txt` 31 → 31 pins |
| v0.2 | 907 | not measured | 0 — 31 → 31 pins; `bench/export_cost.py` stdlib only |

### Top Lessons (Verified Across Milestones)

1. Verifier digests go stale for reasons that are not unverified code (v0.1: STATE.md fingerprinted; v0.2: shared files changed by a later phase) — prove the cause from the artefact and record the override, do not re-stamp.
2. Measurement before knobs held across both milestones: every runtime bound (`mem_limit`, timeout, gzip level, `le`s, `HEX_CELL_CAP`) cites the run that set it, and the two bounds that moved in v0.2 moved on a probe's number.
