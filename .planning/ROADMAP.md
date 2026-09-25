# Roadmap: spur

## Overview

`spur` already ships. Phase 1 records the completed v0 baseline — the working parametric
involute spur gear generator currently in the tree, with all 11 ingested requirements
satisfied and `make verify` passing. Milestone v0.1 ("Hardening") builds forward from
there: Phases 2–5 pay down the three `must` tech-debt items and close the standing
CI-unverified blocker, so the generator is operable under real load and its response
contract is type-checked — before any new gear geometry (helical/internal/rack gears,
tooth chamfers, new bore profiles, body cutouts) makes every build heavier. No new gear
features ship in this milestone; see "Forward Scope" below for where those candidates are
tracked.

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [x] **Phase 1: v0 Baseline (Shipped)** - The generator, its three interfaces, and its
  error/measurement/export contract, as already built and verified.
- [x] **Phase 2: CAD Off the Event Loop** - CAD kernel work moves to worker processes, and (completed 2026-09-24)
  the multi-process memory ceiling is measured, not carried over from the single-process
  design.
- [x] **Phase 3: Structured Logging at the Composition Boundary** - Production requests (completed 2026-09-24)
  leave evidence: a structured logger at startup covers the decision branches that already
  exist.
- [x] **Phase 4: Typed Derived-Dimensions Contract** - `derive()`'s response gets a real (completed 2026-09-24)
  shape, checked by mypy with `disallow_any_explicit` on.
- [x] **Phase 5: CI Observed Green** - CI is the trusted merge gate: every `main` commit (completed 2026-09-25)
  has a run, red or run-less merges are refused, Python 3.12 only.
- [x] **Phase 6: Address tech debt: merge gate + solid cache** - The merge-gate and (completed 2026-09-25)
  solid-cache `must` items the v0.1 audit left open (to be planned).

## Phase Details

### Phase 1: v0 Baseline (Shipped)

**Goal**: Users can generate a correct, print/CNC-ready involute spur gear — with numbers
they can trust — from a web UI, an HTTP API, or a CLI, all driven by one parameter model.
**Depends on**: Nothing (first phase)
**Requirements**: REQ-involute-geometry, REQ-bore-and-fillets, REQ-face-recesses,
REQ-measurement-aids, REQ-three-interfaces, REQ-cli-parity, REQ-shareable-links,
REQ-stl-step-export, REQ-error-contract, REQ-no-auth-default, REQ-docker-multiarch
**Success Criteria** (what is observably TRUE today):

  1. The same gear and the same derived numbers are reachable from the web UI, the HTTP
     API, and the CLI, all built from one `GearParams` model; the CLI's numbers, warnings,
     and exit codes match the API's. *(REQ-three-interfaces, REQ-cli-parity)*
  2. Every gear configuration lives in the URL, so it can be shared and reopened as a
     link. *(REQ-shareable-links)*
  3. The generated solid reflects involute tooth geometry (module, teeth, pressure angle,
     profile shift), backlash, root fillets, a D-flat or round bore with clearance and
     chamfer, and optional filleted-floor face recesses on one or both sides.
     *(REQ-involute-geometry, REQ-bore-and-fillets, REQ-face-recesses)*
  4. Users can download the generated gear as STL (for slicing) or STEP (for CAD) from
     any of the three interfaces. *(REQ-stl-step-export)*
  5. Users get caliper, span (Wildhaber), and centre-distance measurements for matching an
     existing physical gear, with a warning — never a fabricated number — when no working
     centre distance exists. *(REQ-measurement-aids)*
  6. A direct conflict between two explicit parameters is refused (422 / exit 2) naming the
     offending fields; a trimmable dimension is capped and the trim is reported in
     `warnings`; the service deploys via Docker/compose on `linux/amd64` and `linux/arm64`,
     bound to `127.0.0.1` with no built-in authentication by default.
     *(REQ-error-contract, REQ-no-auth-default, REQ-docker-multiarch)*
**Plans**: N/A — this baseline predates GSD planning and was built and verified directly
against `make verify`; there is no PLAN.md history to point to.

### Phase 2: CAD Off the Event Loop

**Goal**: CAD kernel work runs in worker processes outside the request-serving event loop,
and the resulting multi-process memory ceiling is a measured number — not an assumption
carried forward from the single-process design L07 measured.
**Depends on**: Phase 1
**Requirements**: REQ-cad-off-event-loop, REQ-measured-memory-ceiling
**Success Criteria** (what must be TRUE, each backed by a measurement, not a prediction):

  1. Repeating the debt file's own two load scenarios — one 200-tooth fine build in
     flight, and ten concurrent builds — against the new topology shows `/api/health` p95
     within 2× of idle p95, with the measured numbers recorded next to the baseline on
     record (0.22 s → 0.76 s → 2.00 s for the single build; repeatedly over 5 s for ten
     concurrent, 12-core machine). *(REQ-cad-off-event-loop)*
  2. A memory sweep of the actual N-worker topology — not L07's per-process numbers
     multiplied out — produces a measured ceiling, and `compose.yaml`'s `mem_limit` is set
     from that number. *(REQ-measured-memory-ceiling)*
  3. `docs/architecture/decision_log.md` gains two new entries that supersede, and say they
     supersede, L07 (per-process cache/memory formula) and L06 ("concurrency buys latency,
     not throughput") — each dated, each citing the new measurement, neither edited in
     place. *(REQ-measured-memory-ceiling)*
  4. `docs/tech_debt/active/2026-09-21-cad-builds-block-the-event-loop.md` is
     `Status: resolved` with its commit sha recorded, `git mv`'d into
     `docs/tech_debt/resolved/`, and its row moved in `docs/tech_debt/INDEX.md` — in the
     same commit as the fix. *(REQ-cad-off-event-loop)*
  5. `make verify` passes with the new topology in place; admission control still lives in
     the web layer and the CLI still never queues (L04) — unchanged by the process pool.
**Plans**: 5/5 plans executed, in 4 waves (01 and 02 run in parallel)

- [x] 02-01-PLAN.md — One build, in another process: the kernel-free `BuildError`, the
  affinity-routed `BuildPool`, the async endpoint, the parent-side byte cache, and the
  import-linter contract that makes the boundary enforced rather than reviewed *(wave 1)*
- [x] 02-02-PLAN.md — The measuring instrument: `bench/` (L07's own 40-gear corpus, both
  load scenarios, the N=1,2,4 container memory sweep) and `make bench`, deliberately
  outside the gate *(wave 1, parallel with 02-01)*
- [x] 02-03-PLAN.md — Failure modes and liveness: the per-build timeout that terminates a
  wedged worker, the three failure-mode status codes, and pool state on `/api/health`
  *(wave 2)*
- [x] 02-04-PLAN.md — The measured numbers: run both harnesses, record `bench/RESULTS.md`,
  and set `SPUR_BUILD_TIMEOUT`, `mem_limit`, `SPUR_BUILD_WORKERS` and
  `max_tasks_per_child` from what was measured *(wave 3)*
- [x] 02-05-PLAN.md — Close the loop: L17 (supersedes L07) and L18 (supersedes L06), the
  healthcheck timeout brought down from the measurement, and the debt file resolved and
  moved in the same commit *(wave 4)*

### Phase 3: Structured Logging at the Composition Boundary

**Goal**: Production requests leave evidence — a structured logger configured once at the
composition boundary, covering the decision branches that already exist.
**Depends on**: Phase 1 (no dependency on Phase 2 found in the debt files — the logging
gap and the event-loop gap are independent; nothing in
`docs/tech_debt/active/2026-09-21-no-structured-logging.md` ties its fields to the process
pool's build-queue mechanics)
**Requirements**: REQ-structured-logging
**Success Criteria** (what must be TRUE, proven by a test, not console-reading):

  1. A test asserts that each of the four existing decision branches — build started (with
     parameter slug), build failed (with exception class), export served from cache vs.
     built, queue refused — emits a structured log record with named fields.
  2. `calc.py` stays log-free: it remains pure, runs on every keystroke, and its
     `warnings` output is its only diagnostic (L01/AGENTS.md boundary, unchanged).
  3. `docs/tech_debt/active/2026-09-21-no-structured-logging.md` is `Status: resolved`
     with its commit sha recorded, `git mv`'d into `docs/tech_debt/resolved/`, and its row
     moved in `docs/tech_debt/INDEX.md` — in the same commit as the fix.
  4. `make verify` passes.

**Plans**: 3/3 plans executed, in 3 waves (each wave depends on the one before — `records.py` and
`app.py` are touched by both code plans, so there is no honest parallelism here)

- [x] 03-01-PLAN.md — The tracer and the module: kernel-free `records.py` (`configure()`,
  the JSON formatter, the level knob), wired at both composition points (`cli.cmd_serve`
  with `log_config=None`, and the `lifespan()` call research proved mandatory), plus
  `export.served`/`build.started` and the record format's edges *(wave 1)*
- [x] 03-02-PLAN.md — The failure branches: `build.failed` with the exception class and
  duration, `queue.refused` with the in-flight count, and `worker.replaced` emitted inside
  `recreate_for`'s identity guard so one incident is one record *(wave 2)*
- [x] 03-03-PLAN.md — Close the loop: `L20`, the four §Logging sections and the README row
  that are now false, and the debt file resolved and moved in the same commit *(wave 3)*

### Phase 4: Typed Derived-Dimensions Contract

**Goal**: The response every interface reads has a real shape — a typed model, checked by
mypy, instead of an honest but unchecked `dict[str, Any]`.
**Depends on**: Phase 1 (independent of Phases 2 and 3 — the contract change touches
`calc.py`'s return type and the API/CLI/UI's read of it, not the process topology or the
logger)
**Requirements**: REQ-typed-derived-dimensions
**Success Criteria** (what must be TRUE, checked by the gate, not asserted):

  1. `derive()` returns a `DerivedDimensions` Pydantic model with explicit optional fields
     in place of `dict[str, Any]`.
  2. `make verify` passes with mypy's `disallow_any_explicit` turned on across `src/` —
     L14's named ratchet is retired, not re-deferred.
  3. The generated OpenAPI document reflects the new typed shape, and the web UI's
     existing reads of `detail[].ctx.fields` and `warnings` still work, verified by the
     test suite.
  4. `docs/tech_debt/active/2026-09-21-untyped-info-contract.md` is `Status: resolved`
     with its commit sha recorded, `git mv`'d into `docs/tech_debt/resolved/`, and its row
     moved in `docs/tech_debt/INDEX.md` — in the same commit as the fix.
**Plans**: 3/3 plans executed, in 3 waves (each depends on the one before — `app.py`, `cli.py`,
`tests/test_api.py` and `tests/test_calc.py` are touched by more than one plan, and the
pre-commit hook runs `make verify` in the one working tree, so there is no honest
parallelism here)

- [x] 04-01-PLAN.md — The typed info contract, end to end: `DerivedDimensions` built once
  in `derive(p, mate_teeth=…)`, read by `/api/info` and `spur info`, proven by the
  CLI-equals-API, OpenAPI and `app.js` tests; the gear-maths docs made true *(wave 1)*
- [x] 04-02-PLAN.md — `/api/health` as `HealthReport` (`pool: null`, not absent),
  `/api/schema` as `JsonSchemaValue`, and every remaining explicit `Any` removed, rule
  still off, down to the six model class lines *(wave 2)*
- [x] 04-03-PLAN.md — `spur info --mate-teeth` given `InfoQuery`'s range (REQ-cli-parity,
  L08), then `L21` (supersedes L14) and the house rule, then `disallow_any_explicit` on
  via the pydantic plugin's typed-initialiser settings (human decision, 2026-09-24),
  with the debt file retired in the same commit *(wave 3)*

### Phase 5: CI Observed Green

**Goal**: CI is the trusted merge gate for `main` — every commit that lands there has a
GitHub Actions run attached, structurally rather than by discipline; a red, missing or
stale run cannot be merged through the sanctioned path; the supported Python is the one
that actually runs (3.12); and the 2026-09-21 "CI workflow unverified" blocker is retired
with run URLs as evidence. *(Reframed 2026-09-25 in `05-CONTEXT.md`: the original premise —
"the workflow has never executed" — was false; 13 runs existed and `main` push run
35963114939 was green on all four jobs. What the runs revealed is the work: the two squash
commits on `main` since Phase 2 have no run because a `[ci skip]` token rode into their
bodies, and PR #2 was merged with `test (3.10)` red.)*
**Depends on**: Phase 1 (independent of Phases 2–4; small and deliberately not bundled
into any of them per the milestone's own scoping)
**Requirements**: REQ-ci-verified
**Success Criteria** (what must be TRUE, each evidenced by a test, a run URL or a setting read back — not a prediction):

  1. No commit in this repository can carry a GitHub Actions skip token: a repo-owned
     `commit-msg` hook rejects all six (`[skip ci]`, `[ci skip]`, `[no ci]`,
     `[skip actions]`, `[actions skip]`, `skip-checks: true`), proven by a test; and the
     repository's squash-merge message is the PR title + body, never the branch's commit
     subjects.
  2. `make pr.land PR=N` is the documented merge path (`docs/HOW_TO_DEVELOP.md` §8): it
     refuses a PR whose head sha lacks a green run for every named job (`test (3.12)`,
     `vendor-bundle`, `image`), refuses a branch behind `main`, squash-merges, and exits
     non-zero unless a run appears for the squash commit — printing its URL.
  3. spur supports Python 3.12 only: `requires-python`, ruff's `target-version`, the CI
     matrix, the Makefile's interpreter choice, the README and a decision-log entry
     superseding L01's floor all agree, and `make verify` is green.
  4. The "CI workflow unverified" blocker in `STATE.md` is retired citing runs 35963114939
     (`main` push `59f02c3`, all four jobs green) and 36088409707 (PR #3 head `2c4b544`,
     tree-identical to `main` HEAD `bfc9110`);
     `docs/tech_debt/active/2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md` is
     `Status: resolved` in the same commit as the hook + setting, moved to `resolved/` with
     its INDEX row; L22 (the merge gate) and L23 (Python 3.12 only) are appended to
     `docs/architecture/decision_log.md`. *(REQ-ci-verified)*
  5. A ruleset on `main` requires `test (3.12)`, `vendor-bundle` and `image` to be green on
     an up-to-date head and requires a pull request, read back via
     `gh api repos/halfb00t/spur/rules/branches/main`; `docs/HOW_TO_DEVELOP.md` §8 records
     the command that applied it. *(D-12, supersedes D-06 — added in plan-phase 2026-09-25
     after verifying the repository is public)*
**Plans**: 6/6 plans executed, in 6 waves (each depends on the one before — `Makefile`,
`docs/HOW_TO_DEVELOP.md`, `docs/architecture/decision_log.md` and
`.github/workflows/required-jobs.txt` are touched by more than one plan, L22 must be
appended before L23, and the pre-commit hook runs `make verify` in the one working tree)

- [x] 05-01-PLAN.md — The skip-token gate: a `commit-msg` hook (`scripts/skip_tokens.py`)
  refusing the six tokens anywhere above git's scissors line, proven by a refused real
  commit (tracer); the squash message set to PR title + body; the manual ship-note step;
  the debt file retired *(wave 1)*
- [x] 05-02-PLAN.md — `make pr.land PR=N`: lands a green PR with the checked head, subject
  and body, prints the squash commit's run URL or exits non-zero (tracer); then every
  stale, red, missing or token-carrying PR refused, and `required-jobs.txt` held equal to
  `ci.yml` *(wave 2)*
- [x] 05-03-PLAN.md — The wall: the repository's `default` ruleset retargeted to `main`
  (`test (3.12)`, `vendor-bundle`, `image` green on an up-to-date head; a pull request
  required), read back via `rules/branches/main` and recorded in §8; §8 rewritten around
  `make pr.land`, the sanctioned path through it, and §2 no longer pushing to `main`;
  L22 appended *(wave 3)*
- [x] 05-04-PLAN.md — Python 3.12 only: L23 (supersedes L01's floor); `requires-python`,
  ruff py312 and the three findings it forces; `make venv`, the CI matrix and the
  required list narrowed in one commit *(wave 4)*
- [x] 05-05-PLAN.md — The record made true: every current document says 3.12 and cites the
  observed runs; REQ-ci-verified reworded; the STATE.md blocker retired with run URLs
  35963114939 and 36088409707 *(wave 5)*
- [x] 05-06-PLAN.md — Gap closure (05-VERIFICATION.md 4/5, CR-01): `find_skip_tokens`
  searches the whole text it is given and git's cut line is applied only by the hook's own
  entry to an editor buffer, so `make pr.land` refuses a PR body hiding a token below a
  cut line (tracer: the verifier's reproduction as two tests, the fix, the one-line re-run);
  the hook cuts only when git ran an editor (`GIT_EDITOR=:` otherwise), the hand-typed
  cut-line residue filed as `must` debt *(wave 6, gap closure)*

## Forward Scope

Milestone v0.1 is hardening only — no new gear geometry ships in Phases 2–5. Candidates
for the *next* milestone are gathered, not scoped, in `REQUIREMENTS.md` under "Future
Requirements": helical/internal/rack/bevel gears, tooth chamfers, new bore/centre-hole
profiles, parametric body cutouts (spokes, lightening holes, hex patterns), the trochoidal
root-fillet idea (would supersede L10), and a browser-driven viewer test. None of these
are phases yet — the next `/gsd-new-milestone` run picks from that list deliberately, the
way this one did.

The five `nice`-severity tech-debt items in `docs/tech_debt/active/` (coverage floor,
CadQuery `Shape` typing, server-side cancellation, no authentication, Enji Guard/CVE
alerting) stay in their own lifecycle, each with its own trigger — not carried into this
roadmap.

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. v0 Baseline (Shipped) | N/A | Complete | Shipped (pre-dates this roadmap) |
| 2. CAD Off the Event Loop | 5/5 | Complete    | 2026-09-24 |
| 3. Structured Logging at the Composition Boundary | 3/3 | Complete    | 2026-09-24 |
| 4. Typed Derived-Dimensions Contract | 3/3 | Complete    | 2026-09-24 |
| 5. CI Observed Green | 6/6 | Complete    | 2026-09-25 |
| 6. Address tech debt: merge gate + solid cache | 4/4 | Complete    | 2026-09-25 |

### Phase 6: Address tech debt: merge gate + solid cache

**Goal:** Close the five open tech-debt items in the merge gate and the solid cache, each resolved in the commit that fixes it: the `commit-msg` hook checks the whole buffer git hands it (no hand-typed cut line can hide a skip token); `make pr.land` refuses a run whose own conclusion is not `success`, resolves `jobs.<id>.name` overrides in the drift test, and reports only what it observed after the merge; `_build_cached` never hands out a solid carrying a mesh (export works on a copy, `.BoundingBox()` stays exact, the autouse cache reset fixture is deleted). Every behaviour change ships with its test, the copy-vs-strip numbers are measured and written down, `make verify` stays green.
**Requirements**: TBD
**Depends on:** Phase 5
**Plans:** 4/4 plans complete
takes a row move in every plan, `scripts/pr_land.py`, `tests/test_pr_land.py` and
`docs/HOW_TO_DEVELOP.md` are shared by 06-02..06-04, L24 must precede L25, and the
pre-commit hook runs `make verify` in the one working tree)

Plans:

- [x] 06-01-PLAN.md — The solid cache: STL export meshes `shape.copy()`, so a cached solid

**Cross-cutting constraints:**

- `make verify` passes (L13)
  never carries a mesh -- `.BoundingBox()` stays exact and a preview after a fine export is
  a preview (tracer); the autouse cache reset deleted; L24 with the measured costs; the
  debt retired *(wave 1)*
- [x] 06-02-PLAN.md — The commit-msg hook reads the whole buffer, no cut: a real
  editor-session commit hiding a token below a hand-typed cut line is refused (tracer); the
  refusal names the line and the `-v` way out, §6 says the same; the debt retired *(wave 2)*
- [x] 06-03-PLAN.md — `make pr.land`'s verdict: a run whose own `conclusion` is not
  `success` is refused, proven on run 36116930241 (tracer); the drift test reads
  `jobs.<id>.name`; §8's up-to-date-`main` rule; two debts retired *(wave 3)*
- [x] 06-04-PLAN.md — After the merge, `make pr.land` reports only what it observed
  (tracer); the docstring and §8 say which half the ruleset carries; L25 amends L22; the
  last debt retired; STATE.md cites run 36122394253 *(wave 4)*
