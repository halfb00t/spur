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

## Milestone: v0.3 — Clean Ledger

**Shipped:** 2026-10-05
**Phases:** 4 (13–16) | **Plans:** 20 | **Sessions:** not tracked

### What Was Built
- The ten-concurrent latency bar demonstrated on the unmodified harness (`bar-3`:
  1.31×/1.42×) after a pre-registered twelve-run campaign ruled both L18 observations; SC3
  measured the composed worst row under ten concurrent builds as it read (0/10 served) and
  filed the race it exposed (L32).
- `derive()` warns when the root lead-in ends above the pitch circle and README states the
  condition; the filleted-spoke removed volume checked against a polar closed form at
  `abs=1e-9`, with tripwires proving the bar load-bearing; two UAT gaps closed by a
  gap-closure plan (L33).
- `make verify` profiled (224.28 s serial), then run on eight workers at 63.555 s against a
  66 s bar the human set from the profile, under `fail_under = 96`; CI installs the fixture's
  kernel pair through `PIP_CONSTRAINT` (L34).
- `model.py` clean under mypy `--strict` with zero suppressions through two `isinstance`
  boundaries; Phases 7 and 8 Nyquist-validated retroactively in their archived directories
  (L35).
- Ledger: six debt items retired in their fixing commits, five filed (one `must`); the v0.2
  audit amended in place by a dated section.

### What Worked
- Pre-registration. 13-02 committed the method and predictions (`67eeefb`) before any run,
  with the escape clause for a split pair written before Pair A split. Nothing was tuned
  toward a pass (L08) — and the bar passed anyway on the harness as it stood.
- The bar set from the profile, not before it. 15-01 measured, 15-03 priced fifteen cuts,
  the human refused all of them by name and set 66 s, 15-04 read 63.555 s. No test was lost
  to a round number.
- Gap closure as a plan. 14's UAT found two real gaps (a tripwire that could not
  discriminate; a "cannot exist" that was false for four rows); 14-04 closed them with a
  control call and a re-measurement, then the phase was re-verified on the final code.
- Retroactive capability runs on archived phases. `/gsd-validate-phase 7` and `8` resolved
  the archived directories in place (16-CONTEXT D-08); the v0.2 record was completed without
  copying anything.
- Debt retired in the fixing commit, six times out of six — `Status: resolved`, sha,
  `git mv`, INDEX row, same commit.

### What Was Inefficient
- The quiet-host gate (D-05: 1-min load under 1.5 for three consecutive samples) was reached
  in 2 of 5 Phase 13 sessions; `bar-1`, `bar-2` and SC3 capped out at 900 s. A developer
  machine with a Claude Code session active idles at ~2.0 and costs measurement sessions.
- SC3 exposed a server defect (two same-slot timeouts racing cleanup → an undocumented 500)
  that D-17 put out of scope; the milestone's "zero `must`" metric then failed on a row the
  milestone itself wrote. The metric should have named the rows that existed at kickoff.
- `gsd_run query commit`'s 30 s timeout vs the hook, third milestone running: every close-out
  commit was a plain `git commit`; one UAT commit was killed mid-hook. L34 cut the hook from
  ~3.5 min to ~64 s, still over 30 s.
- 15-01 recorded 10 h 41 m wall across an overnight human checkpoint with active time not
  measured; the per-plan table cannot be summed without a footnote.
- Three review passes left 17 findings `open` (14: 4, 15: 8, 16: 5), all warning or info,
  none triaged before the close; v0.2 had closed every finding in-phase.
- Stale-by-fingerprint, third occurrence: Phases 13–15 read `stale` because L33/L34/L35 and
  the retirements touched the shared files their reports cover. Recorded once more as an
  override with the cause proven per phase.

### Patterns Established
- Pre-registered measurement: method, predictions and escape clause committed before the
  first run; verdicts quoted from the committed run files, never re-rounded (E10).
- A quiet-host gate with a cap, and a "non-decisive" outcome recorded rather than retried.
- A measurement checkpoint where the human sets the number from the profile (15-03:
  `knee-headroom N=8 bar=66 cuts=none before=244.59`), recorded verbatim as a dated CONTEXT
  addendum.
- A draft PR opened mid-phase to read CI (15-05), promoted with `gh pr edit` + `gh pr ready`
  at ship — never a second PR for the branch.
- Pure-math oracles beside the kernel proof (`_filleted_spoke_volume`, `_holes_volume`,
  `_hex_cells_volume`), each sharing no code with the production path it checks, plus a
  control call on the unpatched build before any monkeypatch.
- A closed record is amended by a dated section, never rewritten (the v0.2 audit's `nyquist`
  block, 16-03).

### Key Lessons
1. Write the success metric about the state at kickoff, or the milestone's own discoveries
   fail it (metric 1).
2. A pre-registered protocol turns "the bar is unreachable" into a pass or a logged reason;
   the two observations behind v0.1's waiver were a restart loop and an instrument floor, not
   the server.
3. Set a performance bar from a profile the human has read, with every cut priced; "none" is
   a legitimate answer.
4. When a retroactive run's result is not saved, read it back from the committed artefact
   and say so (16-02); a disclosed deviation is cheaper than a re-run.
5. Triage review findings before the close or carry an explicit count forward — 17 open rows
   is a backlog, not a ledger.

### Cost Observations
- Model mix: not recorded — this repo keeps no per-session model accounting.
- Sessions: not tracked.
- Notable: ~7 h 35 min of executor time where measured (15-01's 10 h 41 m wall excluded);
  the pre-commit hook ran ~64 s per commit after 15-04 (L34) versus ~3.5 min before it.

---

## Milestone: v0.4 — True Root

**Shipped:** 2026-10-09
**Phases:** 3 executed (17–19) + 1 skipped by decision (20) | **Plans:** 22 | **Sessions:** not tracked

### What Was Built
- The commit gate split: `make verify.fast` at pre-commit (11.3 s warm) and the whole gate at pre-push, self-installed, proved by a live SDK commit (L36); the same-slot timeout race reproduced on attempt 1, fixed by a two-fact guard and `_closed`, zero 500s after; the heaviest composed row's limit recorded as documented behaviour (L37). Both `must` debts retired in their fixing commits.
- The hob's trochoid as pure `calc.py` maths: the cutter defined once, the envelope in contact-normal angle, one predicate with six named refusals, proven against a swept-cutter oracle (2.985e-12 mm over 10,326 curves), freecad.gears and KISSsoft; nothing a user can see changed (Phase 18).
- The root in the part, opt-in: `root_shape=trochoid` through one `makeSpline` per side with four structural guards and the kernel's arc dead band closed; the built root within 2e-3 × module of the oracle at 401 positions; `root_form_d`, `root_waist` (floor 0.4 mm), null thickness/gap, the undercut sentence from the cutter; parity on three interfaces; composes with every feature; the default unmoved, the fixture byte-identical, Phase 20 skipped with the flip's trigger named (L38).
- Review CR-01 caught a wrong printed number before verification (`root_waist` 2–5 % high on crossing joins); fixed and re-pinned by measurement.

### What Worked
- Spikes before schema (19-01/19-02): the chamfer law, the kernel bar, the guard bars and the waist floor were measured on a bench-built outline and put to the human with headroom before `GearParams` moved; 19-09 re-ran the same rows on the shipped code and they matched.
- One predicate, consumed everywhere: `root_mode` written and proven in Phase 18, wired in Phase 19; the integration checker found no second predicate and no orphaned export.
- The independent oracle on the built solid: 401 positions per root edge with a tripwire that goes red at 0.05 mm. The one real defect (the waist) was in a printed number the oracle does not read, and the code review caught it.
- Checkpoints answered in plain prose: after the first id-template prompt failed ("I have no idea what ids"), the orchestrator explained each decision and the human answered `take the recommendations`; every later checkpoint carried the options in words with the recommendation first.
- Fix-now at the review gate: CR-01 was a standing-rule breach (L08) in the phase's own new field; fixing it on the branch before the verifier ran avoided a stale report and a gap plan.

### What Was Inefficient
- The gate tripled: 52.89 s → 192.94 s mean on this host for 21 kernel-tier tests (305 s of call time at 401 oracle positions). Every post-wave `make test`, every pre-push hook and the fixer's run paid 3–4 min; the human accepted the cost over trimming a proof, and L34's 66 s bar is now a dead number awaiting its own decision.
- `requirements-completed` left empty on six of eleven Phase 19 SUMMARYs (spikes, the tracer, the matrices, L38), so the 3-source cross-reference leaned on bodies; the IDs were marked complete only at 19-11.
- The resource-tracker flake, fourth milestone running: 60 isolation loops saw nothing, one whole-suite baseline run did; re-deferred again with a trigger the skipped Phase 20 no longer serves.
- Twelve macOS crash reports of an xdist worker dying in OCCT at exit, none reproducible on demand; a pasted analysis over-claimed ("every worker", "probably spur") and cost a validation pass. Filed `nice` with the reproducing command as the trigger — still unknown.
- Commit trailers mixed again (executors `Sonnet 5.5`, orchestrator `Fable 5.1`); `init.manager` reads 17/18 as `stale` by fingerprint, the fourth milestone with the same cause.

### Patterns Established
- A kernel-tier bar set per module (`KERNEL_BAR_PER_MODULE` 2e-3) from the whole product's worst spline error, with a tripwire proving it load-bearing, and an oracle position count that is its own measured decision (41 positions read 28 % low).
- Structural guards that do not rest on `isValid()`: junction, spacing, annulus, area — each a `BuildError` naming the check and the remedy, reached by its own test.
- A conditional phase skipped the way its roadmap row prescribes: Progress row `Skipped (…)`, a dated Roadmap Evolution line naming the `Lxx`, criteria marked not applicable, the requirement mapped to the phase that can read it so nothing is orphaned.
- Gate cost as a checkpoint, not a silent trim: three runs with loads on the baseline's host, the delta against the same host, the options A/B/C with the trade stated, the human's answer recorded in the `Lxx`.
- Review info findings deferred as one debt file with their triggers, the ledger reconciled by the fix report.

### Key Lessons
- A number can be proved on the build and still be wrong in `derive()`: the oracle reads the solid, not the printed field. Any new printed quantity needs its own dense-sampled check (the CR-01 test now does this for the waist).
- A gate bar read on another host is not a bar on this one; record the delta against the same-host baseline and re-set the bar from an idle reading under its own decision — do not let it drift on paper.
- Human checkpoints must be answerable in prose; option ids are a convenience for the human, never a requirement.
- When a flake's trigger names a phase, the trigger dies with the phase if that phase is skipped — re-point it at an event, not a plan.

### Cost Observations
- Model mix: orchestrator Fable 5.1; executors, reviewer, fixer, verifier, auditors sonnet; ~0 % haiku
- Sessions: not tracked (one long orchestration session for Phase 19 through the close, compacted twice)
- Notable: Phase 19's wall clock was dominated by `make verify` at 165–240 s per run — roughly 25 full-gate runs across executors, post-wave gates, the fixer, the pre-push hooks and the regression gate.

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v0.1 | n/a | 5 | Phase branches + PR + `make pr.land` replaced direct pushes to `main`; ruleset on `main` |
| v0.2 | n/a | 6 | Build-time gates as human checkpoints with probe-derived offers; cross-CLI (Codex) review lane on the last phase; Nyquist + security audits at verify:post |
| v0.4 | n/a | 3 (+1 skipped) | Spikes before schema with human-set bars; an opt-in geometry field under L05 with the flip deferred under its own `Lxx`; a conditional phase skipped by decision; gate cost as a checkpoint; fix-now at the review gate |
| v0.3 | n/a | 4 | Debt-only milestone scoped from the ledger and the v0.2 audit; pre-registered measurement campaigns; UAT gap-closure plan (14-04); a draft PR mid-phase to read CI (15-05); retroactive Nyquist on archived phases |

### Cumulative Quality

| Milestone | Tests | Coverage | Zero-Dep Additions |
|-----------|-------|----------|-------------------|
| v0.1 | 191 | not measured (no coverage floor — `nice` debt) | 0 — `pyproject.toml` deps unchanged, `requirements.txt` 31 → 31 pins |
| v0.2 | 907 | not measured | 0 — 31 → 31 pins; `bench/export_cost.py` stdlib only |
| v0.4 | 1,220 | 97.92 % against `fail_under = 96`; `make verify` 192.94 s mean vs the 66 s bar (accepted) | 0 — 31 → 31 pins; stdlib maths only under `src/spur/` |
| v0.3 | 929 | 97.24 % against `fail_under = 96` (L34) | 0 — 31 → 31 pins; `pytest-xdist`, `pytest-cov` in `[dev]` only |

### Top Lessons (Verified Across Milestones)

1. Verifier digests go stale for reasons that are not unverified code (v0.1: STATE.md fingerprinted; v0.2 and v0.3: shared files changed by a later phase) — prove the cause from the artefact and record the override, do not re-stamp. Three closes, three overrides.
2. Measurement before knobs held across all three milestones: every runtime bound (`mem_limit`, timeout, gzip level, `le`s, `HEX_CELL_CAP`) cites the run that set it, the two bounds that moved in v0.2 moved on a probe's number, and v0.3's gate bar and coverage floor were set from a profile the human read first.
3. A bar the instrument cannot resolve is not a bar, and a bar it can resolve is demonstrable: v0.1 waived the ≤2.00× latency bar at a 0.1 ms floor; v0.3 ruled the floor real by a pre-registered campaign and then demonstrated the same bar on the same harness behind a quiet gate (L32). The fix was the measurement protocol, not the server.

4. The oracle proves the part, not the print-out (v0.4): the built root matched the swept-cutter oracle at 401 positions while `root_waist` printed 2–5 % high — a printed quantity needs its own dense-sampled check beside the kernel proof, and the code-review gate is where it was caught.