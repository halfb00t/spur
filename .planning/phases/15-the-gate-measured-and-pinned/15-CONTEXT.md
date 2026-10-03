# Phase 15: The Gate, Measured and Pinned - Context

**Gathered:** 2026-10-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Four numbers into `bench/RESULTS.md` and two debt files retired. No `src/` geometry, no
`GearParams` field, no `DerivedDimensions` field; `tests/regression/pre_v0_2.json` (44
records, provenance header included) byte-unchanged throughout; `requirements.txt`'s 31
runtime pins unchanged — every new dev dependency is a `[dev]` extra (L12).

1. **The profile** (REQ-verify-profiled, SC1). `make verify`'s wall time per stage (ruff,
   mypy, import-linter, no-fake-done, pytest), pytest's per-file and top-N `--durations`,
   a `pytest-xdist` sweep over N with the BuildPool/OCCT tests' tolerance *measured*, the
   heaviest contributors named with what each proves, every proposed cut with its
   proof-value cost — measured D-10's way on the dev host, written to `bench/RESULTS.md`.
2. **The bar** (REQ-verify-at-the-bar, SC2). Set by the human at an in-phase checkpoint
   with the profile in front of them (D-01), read at or under afterwards by the same
   method on the same host; before/after rows in `bench/RESULTS.md`; the test count
   unchanged or the difference named; the pre-commit hook's "~11 s" comment corrected.
3. **The floor** (REQ-coverage-floor, SC3). `pytest-cov` added to `[dev]`; one baseline
   `--cov` run recorded; `fail_under` set just under it (D-10); `make verify`'s test
   target runs `--cov --cov-fail-under`; the worker-process ASSUMPTION settled by
   counting worker lines (D-09); a scratch red-on-the-floor run recorded, not committed.
4. **The pin** (REQ-ci-installs-the-pinned-kernel, SC4). CI's `test (3.12)` job resolves
   `cadquery==2.8.0` / `cadquery-ocp==7.9.3.1.1` because `requirements.txt` constrains
   every install in that job (D-13); a green run URL whose log prints the pair; the
   tripwire test stays; L34 logs the choice against L12.
5. **The ledger** (SC5). `2026-09-21-no-coverage-floor.md` and
   `2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md` retire in their fixing commits
   (INDEX rows 21 and 26 move); one L34 amends L12 and L13 (append-only); the planning
   record's "at discuss-phase" and "one of two mechanisms" sentences are corrected in the
   same PR (D-01, D-13).

Not this phase: a slow-test tier that the hook skips and CI runs (rejected — D-03);
constraining local `make venv` to the closure (filed as an idea — D-14); `model.py`'s
`type: ignore`s and the Phase 7/8 Nyquist pass (Phase 16); refreshing
`.planning/codebase/*.md`.

</domain>

<decisions>
## Implementation Decisions

### The bar — shape and timing
- **D-01:** **The bar's shape is fixed here; its number is set at one in-phase checkpoint,
  after the profile and the coverage baseline exist.** The executor halts at a
  `checkpoint:decision` carrying: the per-stage wall table, the per-file and top-N
  durations, the xdist sweep (D-06), the tolerance verdict (D-05), the coverage cost row
  (D-12), and every proposed cut with its proof-value cost (D-03). The human sets the
  bar (and picks N) from that table. The number is written back into this file as a
  dated addendum under this decision (ROADMAP SC2: "recorded in that phase's CONTEXT").
  ROADMAP Phase 15 SC2 / "Depends on" and REQUIREMENTS REQ-verify-profiled /
  REQ-verify-at-the-bar say "at this phase's discuss-phase" — false, since the profile is
  this phase's own first deliverable; both sentences are corrected to "at the profile
  checkpoint" in the `.planning/` commit of the profile plan (14 D-07 precedent; ROADMAP
  edited only through gsd's roadmap tooling as 08/09 did, never a whole-file write).
  Rejected: one `--durations` run now on a loaded host (load 4.37, a single non-alternating
  sample); a number picked today from Phase 12's 217.83 s (REQUIREMENTS "Out of Scope: a
  target chosen before the profile exists").
- **D-02:** **Absolute wall seconds of `make verify` on the dev host.** `/usr/bin/time -p`
  around the whole gate (Phase 12 B2's shape), measured D-10's way (D-04). It is what the
  pre-commit hook costs per commit and what REQ-verify-at-the-bar's "same way, same host"
  measures. CI's `test (3.12)` job duration is recorded as context on a different
  (4-vCPU) host — never the bar. Rejected: a ratio to the baseline (hides the absolute
  cost; every later phase re-measures the baseline to read it); pytest seconds only (the
  hook's wall time is what the human waits for; the profile times the other stages anyway).
- **D-03:** **Parallelism and non-proof dedup are free; every skip, removal, mark or
  sampling is accepted by name or stays.** `pytest-xdist` and changes that leave the set
  of assertions intact (sharing one built solid across assertions on identical params,
  deleting a duplicated build) need no approval. Any test removed, skipped, marked or
  sampled is a row at the D-01 checkpoint with what it proves and what its loss costs;
  the human accepts each by name, else it stays. L13's "one definition of passing, three
  places" is untouched. Rejected: no cuts at all (the checkpoint then presents cuts for
  the record only — a legitimate outcome of D-01, not a rule); a `slow` tier skipped by
  the hook and run by CI (hook and CI would no longer run the same gate — a supersession
  of L13 nobody asked for).
- **D-04:** **D-10's load rule, unchanged: alternate, record load, no quiet gate.**
  Before/after are alternating A/B full `make verify` runs in one session, load read
  before each, delta = mean(B) − mean(A). The single-sided profile is two runs with load
  recorded; per-file durations are read as shares. Host-state header as every
  `RESULTS.md` section has (machine facts, HEAD, load samples, `SPUR_*` values), plus the
  peak-RSS reading D-05 adds. Phase 13 reached the D-05 quiet bar in 2 of 5 sessions and
  read ~2.0 with a Claude session open; waiting for it here would mean closing this
  session, possibly more than once. Rejected: the D-05 quiet gate; a CI job wall time as
  a second reading of the profile (context only, D-02).

### pytest-xdist policy
- **D-05:** **xdist is adoptable only on three consecutive green full runs at the chosen
  N, each with the full test count, zero flakes, zero reruns, peak RSS recorded.** The
  risk is memory, not CPU: every xdist worker that runs a kernel test pages in OCCT, and
  `tests/test_pool.py` spawns two more `BuildPool` processes per test that builds. One
  failure anywhere = not adopted this phase; the reading is recorded in `RESULTS.md`,
  `pytest-xdist` stays a `[dev]` extra, and the bar is set on serial + dedup. No
  `pytest-rerunfailures` or kin — a flaky gate is worse than a slow one. Rejected: one
  green run (a 1-in-5 flake in the process-pool tests would not show); measure only, do
  not adopt (leaves most of the time on the table for no proof gained).
- **D-06:** **N is swept, not assumed: {2, 4, 8, 12}, one full run each, load and peak
  RSS recorded; the human picks N at the D-01 checkpoint from the knee.** The planner
  runs D-05's three tolerance runs at the sweep's *apparent* knee before the checkpoint so
  the verdict is on the table; if the human picks a different N, three runs at that N
  precede the before/after rows. The chosen N is written as a literal in the Makefile
  with a comment citing the `RESULTS.md` sweep table — not `-n auto` (12 here, 4 on CI's
  runner: the memory reading would decide after the fact). Rejected: `-n auto` with RSS
  recorded; a fixed conservative 4 to mirror CI (leaves 8 cores idle on the host the bar
  is measured on).
- **D-07:** **The `-n` flag lives in the Makefile `test` target only.** `make test` /
  `make verify` (and therefore CI's `make verify PYTHON=python`) go parallel; a bare
  `.venv/bin/pytest tests/test_calc.py -k x` stays serial, so `-x`, `--pdb` and
  single-file debugging keep working. Concrete reason against `addopts`: `make test-image`
  pip-installs only `pytest httpx` inside the image (`Makefile:83–89`) — `-n` in
  `addopts` would break it. `make test-image` stays serial and unchanged this phase
  (noted in `<deferred>`). Rejected: `addopts` in `pyproject.toml`; giving `test-image`
  xdist too (one more place to keep in step for a check that is CI's `image` job's cousin,
  not the gate).
- **D-08:** **`--dist load` (xdist's default); isolation only when a tolerance run
  measures a reason.** Individual tests spread for balance; module-scoped fixtures
  (`tests/test_api.py:28`'s autouse override, `tests/test_records.py:40`) are set up per
  worker process, which is what xdist does anyway. If one of D-05's three runs fails on a
  pool or app-global test, those tests get an `xdist_group` mark under `--dist loadgroup`,
  the failure and the reason are recorded, and the three runs restart. Rejected:
  `--dist loadfile` (safe by construction, but `tests/test_model.py` — the heaviest file,
  48 kernel tests — serialises on one worker and caps the gain); grouping the pool tests
  pre-emptively (removes a risk before measuring whether it exists).

### Coverage floor
- **D-09:** **Worker-process lines count.** `[tool.coverage.run]` gains `concurrency =
  ["multiprocessing"]`, `parallel = true` and `sigterm = true` — `BuildPool` uses
  `mp.get_context("spawn")` (`src/spur/pool.py:35`) and `recreate_for` /
  `_run_with_timeout` call `proc.terminate()` (`pool.py:205`), so without `sigterm` a
  terminated worker's data is lost. pytest-cov's subprocess hook and combine do the rest
  and already combine across xdist workers. **ASSUMPTION (planner verifies against
  pytest-cov's and coverage.py's docs, executor proves on the baseline):** spawned
  children started by `ProcessPoolExecutor` pick up pytest-cov's subprocess measurement;
  the proof is that `pool.build_export` and `pool._warm` read covered in the baseline
  report. The baseline section states in words that worker lines are counted and how.
  Rejected: declaring them uncovered and setting the floor on that reading (understates
  what the suite exercises); `# pragma: no cover` on the entry points (hides code the
  pool tests do run — the opposite of a floor's purpose).
  **Addendum 2026-10-03 (plan-phase, from 15-RESEARCH.md Pitfalls 1–2; human accepted):**
  the mechanism above is stale — pytest-cov 7.0 dropped its subprocess hook, and
  `concurrency = ["multiprocessing"]` alone replaces coverage.py's default `"thread"`, so
  the `TestClient` portal thread that builds and shuts down the `BuildPool` stops being
  traced (`pool.py` read 85 %, lines 74–91, 222, 225–226 missing). The decision's intent
  stands; the config is `concurrency = ["multiprocessing", "thread"]`, `parallel = true`,
  `sigterm = true` (verified: `pool.py` 100 %, identical totals serial and at `-n 4`).
  L34 records the correction.
- **D-10:** **`fail_under` = the baseline total rounded down to a whole percent; one more
  point down if that leaves under 0.25 pt of slack; the spread across D-05's three runs
  must fit inside the slack.** The three tolerance runs are run with `--cov` on, so their
  totals are the determinism check for free; if their spread exceeds the slack, the floor
  widens to cover it and the spread is recorded. On ~3,100 statements one point is ~31
  untested lines — a whole new untested function trips it; a timing-dependent `pool.py`
  branch does not. Rejected: baseline − 1.0 at two decimals (always one point, reads as a
  strange literal); baseline − 0.1 (a single timing-dependent branch could flip a run
  red with no code change — the flaky-gate failure, not the drift the floor is for).
  **Addendum 2026-10-03 (plan-phase, from 15-RESEARCH.md Pitfalls 3 and 7; human
  accepted):** the arithmetic above is off — `src/spur` is 1,069 statements and 294
  branches, so with `branch = true` one point is ~13.6 units, not ~31 lines on ~3,100
  statements; the qualitative argument (a new untested function trips a one-point slack,
  one timing-dependent branch does not) survives. And `fail_under` compares
  `round(total, precision) < fail_under` with `precision = 0` by default: a total of
  45.93 against `fail_under = 46` printed FAIL and exited 0. `[tool.coverage.report]`
  therefore sets `precision = 2`, and the slack is computed with that rounding. The rule
  stands; L34 cites 1,069 / 294.
- **D-11:** **Scope is `src/spur` only**, as `[tool.coverage.run] source` already says.
  `scripts/` (78 tests of its own) and `bench/` are tooling, not the gate's subject;
  `bench/` in particular is hand-run measurement code with no test by design. Rejected:
  `src/spur` + `scripts/`; everything mypy checks.
- **D-12:** **Coverage runs on every `make verify`; its cost is one row at the D-01
  checkpoint, not a separate decision.** The coverage plan lands after the profile; its
  wall-time delta is measured D-10's way (A = the gate without `--cov`, B = with, same N)
  against the profiled baseline and presented at the checkpoint — the bar the human sets
  already includes it. No pre-chosen ceiling, no separate halt. The Makefile `test`
  target carries `--cov --cov-fail-under` (REQ's text; whether the threshold is read from
  `[tool.coverage.report] fail_under` or passed as `--cov-fail-under=NN` is the planner's
  after checking pytest-cov's precedence rule). The scratch red-on-the-floor run (one
  test file removed, `make verify` goes red) is recorded in `RESULTS.md` with the file
  named and the number read, never committed. Rejected: a pre-agreed ceiling that forces
  a second checkpoint (a number chosen before the profile exists); CI-only coverage
  (breaks L13 and REQ's own acceptance text).

### CI kernel pin mechanism
- **D-13:** **`requirements.txt` constrains every pip install in CI's `test` job**
  (`pip install -c requirements.txt …`, or `PIP_CONSTRAINT=requirements.txt` on the step —
  the planner's call; the effect is fixed). L12's closure does one more job: its 31 `==`
  lines (no hashes, comment lines only at the top — valid as a constraints file) pin both
  halves of the kernel pair and every other runtime package to exactly what the image
  ships; the dev extras and the packages `docker/refresh-requirements.sh` prunes stay
  free; `pyproject.toml`'s ranges are untouched. The closure was resolved on linux/amd64 —
  CI's runner. **This is not one of REQ-ci-installs-the-pinned-kernel's two named
  options**; the REQ sentence ("by one of two mechanisms…") and ROADMAP SC4 are amended
  to name it in the same PR (08 D-01 / 14 D-07 precedent; roadmap via gsd tooling). L34
  records the choice against L12's "why floors and ranges" rationale. Rejected: REQ
  option A, `pip install --no-deps -r requirements.txt` then the dev extras (works — pip
  keeps satisfied pins — but the second install pulls the pruned ~550 MB of cadquery's
  transitive deps back in, and it is CI-only by construction); REQ option B, an upper
  bound on `cadquery` in `pyproject.toml` (pins every environment, but `cadquery-ocp` is
  pinned only through cadquery 2.8.0's own `<8.0,>=7.9.3.1` cap — a 7.9.x ocp patch would
  still move under the fixture; pinning it directly adds a product dependency for a
  test-fixture reason and narrows L12's "loose ranges for dev" sentence). —
  **Reversibility:** reversible — one env line or flag in `ci.yml`.
- **D-14:** **CI only this phase; `make venv` unchanged; the local path filed as an
  idea.** `docs/ideas/2026-10-03-constrain-make-venv-to-the-closure.md` (filed in this
  discuss commit, INDEX row added) with the trigger: a fresh `make venv VENV=.venv-proof`
  on macOS arm64 under `-c requirements.txt` installs and passes `make verify` — the
  closure's arm64 wheel availability is unproven. `test_the_fixture_was_captured_on_the_
  kernel_this_run_uses` stays the local remedy ("recreate the venv to match"). Rejected:
  CI and `make venv` now (one more ~1.4 GB install in the phase, a wider L34, and a
  prerequisite change to `$(STAMP)`); CI only with nothing filed.
- **D-15:** **"Where the pin lives" is written in the tripwire test's docstring and in a
  `ci.yml` comment; `tests/regression/pre_v0_2.json` is not edited.** The docstring
  (`tests/regression/test_pre_v0_2.py:80–90`) names `requirements.txt` as the pin,
  `docker/refresh-requirements.sh` as what moves it, and `make fixture.regen` as the
  fixture's own move; the assertion message may say the same (code, not fixture). The
  JSON `regenerate` note is prose inside the fixture file — editing it changes the
  file's bytes, which the milestone's byte-unchanged rule forbids for a prose reason.
  Rejected: the docstring + `docs/HOW_TO_DEVELOP.md` (misses whoever edits `ci.yml`);
  amending the fixture note as its own commit.
- **D-16:** **The proof is an explicit version-print step in CI plus the tripwire green,
  on one run whose URL goes into L34 and the retired debt file.** One `python -c` line
  prints the installed `cadquery` and `cadquery-ocp` versions by name (placement — before
  or after `make verify`, which creates `.venv` — is the planner's) so the log states the
  pair without reading pip's install output, which is ~60 names long and absent on a cache
  hit. The debt file's `Resolved in` therefore cites the pin commit's sha *and* the run
  URL; since the run exists only after a push, the retirement is a follow-up commit (13's
  `6709953` → `05668ef` precedent for a file that cannot carry its own sha). Rejected: a
  scratch branch run constrained to `cadquery-ocp==8.0.1.0.0` to show the tripwire fire on
  CI (manufactures a trigger that has not fired in nature; the test's own unit coverage is
  the proof it fires); pip's "Successfully installed …" line alone.
  **Addendum 2026-10-03 (plan-phase; the human's answer to 15-05 Task 2's checkpoint):**
  `.github/workflows/ci.yml` triggers only on `pull_request` and on pushes to `main`
  (planner's reading; every past phase-branch run was a `pull_request` event), so pushing
  the branch alone starts no run. Mechanism: **`draft-pr`** — 15-05 opens the phase PR as
  a draft at its push (`gh pr create --draft`) and reads the run URL from that PR's checks;
  at ship, `/gsd-ship`'s `gh pr create` would refuse a second PR, so the draft is updated
  with `gh pr edit` and marked ready with `gh pr ready` instead. Also corrected here: the
  "absent on a cache hit" justification above is false for this workflow (RESEARCH Pitfall
  14 — run 37116412012 hit the pip cache and still printed the pair); the print step stands
  as the cheaper-to-read proof, and L34 says so. 15-05 Task 2's checkpoint is pre-answered
  by this addendum.

### The record
- **D-17:** **One L34, append-only, amending L12 and L13.** L26–L33 are one entry per
  phase; L34 keeps the pattern: the measured gate (baseline, the bar set and read, N and
  the sweep, the tolerance verdict, cuts accepted by name if any), the floor (baseline
  total, `fail_under`, the spread, worker lines counted), and the pin (the constraints
  mechanism against L12's rationale, the run URL). L12's and L13's text untouched (L25 →
  L22, L32 → L18, L33 → L09/L10/L30 precedent); PROJECT.md's L12/L13 rows get their
  Outcome column updated at the transition. Every number cited to a `RESULTS.md` section
  or a SUMMARY sha, none re-estimated.
- **D-18:** **Retirements in the fixing commits.** `2026-09-21-no-coverage-floor.md`
  (nice) retires in the coverage commit, its false "pytest-cov is installed" sentence
  corrected on the way out (REQ); `2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md`
  (must) retires per D-16. `docs/tech_debt/INDEX.md` rows 21 and 26 move to the resolved
  table in those commits.
- **D-19:** **Every "~11 s warm" claim in the tree is found by grep and dealt with per its
  file's rule in this PR:** `.pre-commit-config.yaml`'s comment gets the measured number
  (REQ); `docs/architecture/decision_log.md` L13 is append-only, so L34 carries the
  correction; `.planning/PROJECT.md` Constraints "Gate" gets the number at the
  transition; `.planning/codebase/TESTING.md` is a map, refreshed by `/gsd-map-codebase`,
  not hand-edited (see `<deferred>`).
- **D-20:** **No `src/` change is expected.** Coverage config, the Makefile, `ci.yml`,
  `pyproject.toml`'s `[dev]` extras and `[tool.coverage.*]`, one test docstring, prose. If
  the xdist tolerance or the worker-coverage proof turns out to need a `src/` change (a
  worker-side hook, for instance), the executor stops and asks — it is not a geometry
  change, but it is outside what this phase promised. The fixture is byte-unchanged by
  construction; `git diff --exit-code 20cd484 -- tests/regression/pre_v0_2.json` is the
  final pass (12 D-20's shape).
- **D-21:** **Process (13 D-18, 14 D-15, ROADMAP "Process Notes").** Branch
  `gsd/phase-15-the-gate-measured-and-pinned` cut from `origin/main` `20cd484` (PR #17
  landed); plain `git commit` with explicitly staged files (the hook runs ~4 min at 927
  tests today — and gets faster mid-phase once D-07 lands; `gsd_run query commit`'s 30 s
  timeout cannot survive it either way); lands via `make pr.land PR=N` (L22/L25);
  `.planning/` rides the same PR; who wrote the diff does not review it (CLAUDE.md).

### Claude's Discretion
- **Plan order.** Suggested: (1) the profile — serial baseline with `--durations`, the
  N sweep, the three tolerance runs at the apparent knee, `RESULTS.md` section, the
  REQ/SC2 sentence correction; (2) coverage — `pytest-cov` extra, `[tool.coverage.run]`
  config, baseline run, `fail_under`, the cost delta, the scratch red run, debt file 1
  retired; (3) the D-01 checkpoint, then applying N, the bar, `--cov` on the `test`
  target, the hook comment, the before/after rows; (4) the pin — `ci.yml`, docstring, push,
  run URL, debt file 2 retired in a follow-up; (5) L34, PROJECT/REQ/SC amendments. (4) is
  independent and may run earlier.
- `--durations` count (25 is a reasonable default) and whether `--durations=N` stays in
  `make test` after the profile (default: profile only).
- How peak RSS of the whole process tree is measured — `/usr/bin/time -l` reports the
  waited-for child's `ru_maxrss`, not the tree's sum; a 1 s sampler over the tree (the
  `make bench.memory` approach) is the honest reading. The planner names the method and
  what it measures in the host-state header.
- The Makefile spelling (`PYTEST_WORKERS ?= N` vs a literal in the recipe) and the comment
  that cites the sweep table.
- `[tool.coverage.report]` flags (`skip_covered`, `show_missing`, `precision`) and the
  terminal report format on a red run; which test file is removed for D-12's scratch run.
- `PIP_CONSTRAINT` env vs an explicit `-c` step in `ci.yml`; where the version-print step
  sits; whether the `actions/setup-python` pip cache key needs `cache-dependency-path`
  adjusting (default already hashes `**/requirements.txt`).
- The checkpoint table's layout and the L34 title and Reason wording.
- Whether `xdist_group` marks (D-08, only if triggered) are declared in `pyproject.toml`
  `markers` — `--strict-markers` is on, so an undeclared mark fails collection.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements, roadmap, project
- `.planning/REQUIREMENTS.md` — "### Kernel pin" (REQ-ci-installs-the-pinned-kernel: the
  sentence D-13 amends) and "### The gate" (REQ-verify-profiled, REQ-verify-at-the-bar —
  the "at discuss-phase" sentences D-01 corrects; REQ-coverage-floor with the worker
  ASSUMPTION D-09 settles and the false "pytest-cov is installed" claim D-18 corrects);
  "Rules every requirement lives by"; "Out of Scope" (a target chosen before the profile).
- `.planning/ROADMAP.md` "### Phase 15: The Gate, Measured and Pinned" — goal, "Depends
  on" (the "at this phase's discuss-phase" clause), SC1–SC5 (SC2 and SC4 are the
  sentences D-01/D-13 amend); "## Process Notes (carried forward)".
- `.planning/PROJECT.md` — "Current Milestone: v0.3 Clean Ledger" (the `make verify`
  profiled / coverage floor / CI kernel pin target text and the three rules); "Success
  Metric (Milestone v0.3)" 1–2; "Constraints → Gate" (the "~11s warm" claim, D-19); Key
  Decisions rows L12, L13 (Outcome columns at transition).
- `CLAUDE.md` — "How to verify (the gate)", "Finishing work properly", "Capturing ideas
  and debt" (retirement mechanics), "Code style".
- `docs/CODING_VALUES.md` — the coding standard for the Makefile/config comments.

### The debt and its history
- `docs/tech_debt/active/2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md` — the
  must item D-13/D-16 retire: why the fixture's exact values depend on one kernel pair,
  the two options it named, "needs the human".
- `docs/tech_debt/active/2026-09-21-no-coverage-floor.md` — the nice item D-18 retires:
  "a floor picked before measuring is a number, not a guarantee"; its false "pytest-cov
  is installed" sentence.
- `docs/tech_debt/INDEX.md` rows 21 and 26 — move to the resolved table in the retiring
  commits; `docs/tech_debt/TEMPLATE.md` for `Status`/`Resolved in`.
- `docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md` — why
  commits are plain `git commit`; its trigger text names the hook's runtime, which this
  phase changes (update the number there too, do not retire — upstream gsd behaviour).
- `docs/ideas/2026-10-03-constrain-make-venv-to-the-closure.md` — D-14's filed idea and
  its trigger.

### Decisions
- `docs/architecture/decision_log.md` — **L12** (the closure, "why floors and ranges";
  the entry L34 amends), **L13** (`make verify` is the gate, "~11 s warm"; the second
  entry L34 amends), L08 (no plausible numbers), L16 (no formatter — do not reformat the
  Makefile or `pyproject.toml`), L21 (`disallow_any_explicit` — any new test helper obeys
  it), L22/L25 (merge gate; `required-jobs.txt` must still match `ci.yml`, enforced by
  `tests/test_pr_land.py`), L23 (3.12 only — CI matrix stays `["3.12"]`), L26 (fixture
  byte-unchanged), L32/L33 (the "amends Lxx" append-only shape).
- `.planning/phases/13-latency-bar/13-CONTEXT.md` — D-05 (the quiet bar D-04 declines),
  D-09 (checkpoint-with-the-numbers shape D-01 copies), D-12 (amending-entry shape), D-18
  (process).
- `.planning/phases/14-honest-record/14-CONTEXT.md` — D-07 (correcting the planning
  record's own sentence in the PR — D-01/D-13's precedent), D-14/D-15 (retirement and
  process).
- `.planning/milestones/v0.2-phases/12-composition-pass/12-CONTEXT.md` — D-10 (the
  alternating A/B measurement D-04 reuses), D-17 (every number behind a committed script
  or make target), D-18 (append-only precedent).

### The measurement record
- `bench/RESULTS.md` "## Composition pass test cost (Phase 12, D-10)" (lines 2130–2198)
  — the host-state header shape, the alternating A/B table (A1 193.30 s / B1 217.90 s /
  A2 185.88 s / B2 217.83 s), "### make verify wall time" (907 passed in 216.73 s at load
  9.07), "### Regression fixture share" (86 passed in 19.24 s); "### make verify wall
  time" under "## Body cutout build and export time (Phase 11)" (line 1532: 621 passed /
  178.55 s wall). The new sections sit after the Phase 14 material in the same shape.
- `bench/README.md` — the host/port/comparability rules every `RESULTS.md` section obeys.
- `bench/__init__.py::machine_facts()` — every printed number carries the machine.

### The gate's own files
- `Makefile` — `verify` (50), `lint`/`typecheck`/`lint-imports`/`no-fake-done` (52–68),
  `test` (70–71: `$(PY) -m pytest $(PYTEST_ARGS)` — D-07/D-12's one edit site),
  `test-image` (83–89: installs only `pytest httpx` — why `addopts` is wrong), `$(STAMP)`
  (33–42: `pip install -e '.[dev]'` — untouched by D-14), `PYTEST_ARGS ?=` (6).
- `pyproject.toml` — `[project.optional-dependencies] dev` (the two new extras),
  `[tool.pytest.ini_options]` (`addopts = "--strict-markers --strict-config"`, untouched
  by D-07; `markers` if D-08 triggers), `[tool.coverage.run]` (`branch = true`, `source =
  ["src/spur"]`, the comment pointing at the debt file — D-09/D-11 edit here),
  `[tool.coverage.report]` (new — D-10/D-12), the `[tool.ruff]` comment on L16.
- `.github/workflows/ci.yml` — the `test` job (12–27: `make verify PYTHON=python` on
  `ubuntu-latest`, `setup-python` with `cache: pip`) — D-13's constraint, D-15's comment,
  D-16's print step; `.github/workflows/required-jobs.txt` unchanged (job names do not
  change).
- `.pre-commit-config.yaml` — lines 6–8, "A warm run is ~11 s" (D-19).
- `tests/regression/test_pre_v0_2.py` — `test_the_fixture_was_captured_on_the_kernel_
  this_run_uses` (80–90: D-15's docstring); `tests/regression/pre_v0_2.json` provenance
  header (lines 1–9: read, never written).
- `src/spur/pool.py` — `_SPAWN = mp.get_context("spawn")` (35), `_warm` (41),
  `build_export` (53: the worker-side function whose coverage proves D-09),
  `recreate_for` (99), `_run_with_timeout` (157–220: `proc.terminate()` at 205 — why
  `sigterm = true`).
- `tests/test_pool.py` (14 tests, real `BuildPool` processes), `tests/test_api.py:28–41`
  (module-scoped autouse `dependency_overrides`), `tests/test_records.py:40–44`,
  `tests/conftest.py` (autouse root-logger reset) — the shared-state sites D-08 watches.
- `tests/test_model.py` (48 kernel tests; the 15 Phase 12 tier-2 rows measured at
  30.66–30.73 s), `tests/regression/test_pre_v0_2.py` (86 cases, 19.24 s),
  `tests/test_pr_land.py` (58 tests, 13 subprocess calls), `tests/test_skip_tokens.py`
  (20 tests) — the likely top contributors the profile names.
- `docker/refresh-requirements.sh` — what moves `requirements.txt` (D-15's text); the
  PRUNE list (why the closure is 31 packages, not ~56); `requirements.txt` header comment
  (its "pyproject.toml keeps loose ranges for installing into your own environment"
  sentence stays true under D-14).

### Process
- `docs/HOW_TO_DEVELOP.md` §4/§6/§7/§8 — branch per phase, PR, cross-CLI review, land.
- `.planning/codebase/TESTING.md` — the map (dated 2026-10-02; "Warm run ~11 seconds",
  "Coverage measurement in place" are stale — refreshed by tooling, not edited here).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `bench/RESULTS.md` "Composition pass test cost" section — the exact A/B protocol,
  table and host-state header D-04 reuses; `/usr/bin/time -p make verify` is the wall
  reading.
- `bench/__init__.py::machine_facts()` — the host facts line for every new section.
- `Makefile` `PYTEST_ARGS ?=` — already threads extra pytest flags through `make test`
  (`make test PYTEST_ARGS="tests/regression -q"` is how the fixture share was read); the
  profile's `--durations` run needs no new target.
- `tests/regression/test_pre_v0_2.py::test_the_fixture_was_captured_on_the_kernel_this_
  run_uses` — the tripwire that stays; its message already says "recreate the venv to
  match", D-14's local remedy.
- 13's `6709953` → `05668ef` two-commit retirement — the shape D-16 needs for a debt file
  that must cite a CI run that does not exist until after the push.
- `docs/ideas/TEMPLATE.md` + `INDEX.md` — D-14's idea file follows them.

### Established Patterns
- A number is measured via a committed command, recorded with host state and load, cited
  in the `Lxx`, never re-estimated (12 D-17, L27–L33).
- A decision that needs a number halts at a checkpoint with the number and a pre-agreed
  shape (07 D-06, 12 D-03, 13 D-09, 14 D-06) — D-01 is the fifth instance.
- Rows over a bar are recorded as measured, never re-run to green (11-06, 13 D-05's
  "non-decisive" marking) — D-05's "one failure = not adopted" follows it.
- Comments carry the measurement and the date; a literal in config cites the table it
  came from (`HEX_CELL_CAP = 120` from the spike's Cap line) — D-06's N and D-10's
  `fail_under` follow it.
- The planning record's own false sentence is corrected in the PR that discovers it
  (14 D-07) — D-01 and D-13.
- The decision log is append-only; an amendment is a new entry naming the old one.
- Debt is resolved in the fixing commit: status, sha, `git mv`, INDEX row.
- No formatter: Makefile and `pyproject.toml` edits are hand-aligned to the existing
  comment style (L16).

### Integration Points
- `Makefile` `test` recipe — `-n N`, `--cov --cov-fail-under` (D-07, D-12).
- `pyproject.toml` — `dev` extras (`pytest-xdist`, `pytest-cov`), `[tool.coverage.run]`,
  `[tool.coverage.report]`, possibly `markers`.
- `.github/workflows/ci.yml` `test` job — the constraint, the comment, the print step.
- `.pre-commit-config.yaml` — the comment number.
- `bench/RESULTS.md` — one Phase 15 section with the profile, sweep, tolerance, coverage
  baseline, cost rows, scratch red run, before/after.
- `docs/architecture/decision_log.md` (L34); `docs/tech_debt/` → `resolved/` ×2 +
  INDEX; `docs/ideas/` + INDEX (D-14); `.planning/REQUIREMENTS.md` / `ROADMAP.md` /
  `PROJECT.md` sentences (D-01, D-13, D-19); this file's D-01 addendum.

</code_context>

<specifics>
## Specific Ideas

**Numbers on record (`bench/RESULTS.md`), the profile's starting point:** Phase 12 B2:
`907 passed in 216.73s`, 217.83 s wall, load 9.07 at start, HEAD `480da30`; A runs at 621
tests 193.30 s / 185.88 s; Phase 11: 621 passed / 178.55 s wall at load 3.07–4.65;
regression share 86 passed in 19.24 s (16.27 s at 07-01); the 15 Phase 12 tier-2 kernel
rows 30.66–30.73 s alone. Today: 927 tests on `20cd484`; no `--durations` on record; no
per-stage split on record. The hook is "~3.5–4 min" in every Phase 12–14 note.

**Test inventory (`grep -c 'def test_'`, 2026-10-03):** `test_calc.py` 69, `test_pr_land.py`
58, `test_model.py` 48, `test_api.py` 44, `test_bench.py` 24, `test_cli.py` 22,
`test_skip_tokens.py` 20, `test_pool.py` 14, `test_records.py` 13, `regression/` 5 (one
parametrised over 44 records, one over the solid subset). Parametrisation multiplies
these to 927 items.

**Host (discuss time):** 12 CPUs, Apple M2 Max, arm64, 32.0 GiB, 1-minute load 4.37;
`.venv` Python 3.12.13; `pytest 9.1.1` installed; `pytest-xdist` and `pytest-cov` **not**
installed (`pip list`).

**Memory shape D-05 watches:** one serial pytest process pages in ~1.4 GB of OpenCascade
(cold) — resident set per kernel-test process is what the sampler reads; `test_pool.py`
tests each start a `BuildPool(workers=…)` of spawned processes that import the kernel.
At N = 12 the tree can hold 12 xdist workers plus their pools. CI's `ubuntu-latest` has
4 vCPUs / 16 GB — N = 12 there would oversubscribe; the chosen literal N is a dev-host
knee and the planner states what CI runs (the same N, or `min(N, cpu)` — the planner's,
with the reasoning in the Makefile comment).

**Tolerance-run bookkeeping (D-05/D-06/D-10 together):** sweep = 4 full runs (N = 2, 4,
8, 12), each recorded `<N> | passed/failed | pytest s | wall s | load | peak RSS`;
tolerance = 3 further full runs at the apparent knee with `--cov` on, each recorded the
same way plus the coverage total; the spread of those three totals is D-10's determinism
reading. Coverage cost (D-12) = alternating A (no `--cov`) / B (`--cov`) at the same N.

**Constraints-file facts (D-13):** `requirements.txt` has 31 `==` lines, 0 hashes, five
leading `#` comment lines; pip constraints files accept comments and `name==version`
lines but not extras or editables — the dev extras are installed from `pyproject.toml`
as today. pip reads `PIP_CONSTRAINT` as the env form of `-c` (ASSUMPTION — planner
confirms against pip's docs before choosing env vs flag).

**The checkpoint's offer (D-01):** the table above, then "the bar at <mean(B) of the
chosen configuration> s" as the first offer, every proposed cut as a named row with its
proof and cost, the human's answer written verbatim into this file's D-01 addendum, the
`RESULTS.md` "Gate decision" subsection and L34 (12 "### Gate decision" shape).

**Prose sites for the measured number (D-19):** `.pre-commit-config.yaml:6–8`;
`decision_log.md` L13 ("~11 s warm", via L34); `PROJECT.md` "Constraints → Gate" ("~11s
warm"); `README.md` is not known to carry the claim — the executor greps `~11` across the
tree and lists what it found.

</specifics>

<deferred>
## Deferred Ideas

- **Constrain local `make venv` to the closure** — D-14; filed as
  `docs/ideas/2026-10-03-constrain-make-venv-to-the-closure.md` with its arm64 trigger.
- **`make test-image` running pytest in parallel** — not taken (D-07); the in-image run
  installs only `pytest httpx` and is the `image` job's cousin, not the gate. Revisit if
  the image check's runtime becomes a complaint.
- **A `slow` marker tier** — rejected, not deferred (D-03): it would make the hook and CI
  run different gates (L13). Recorded so it is not re-proposed as new.
- **A scratch CI run proving the tripwire fires on a different `cadquery-ocp`** — not
  taken (D-16); the trigger has not fired in nature and the test's own unit proof stands.
- **`--durations` permanently in `make test`** — Claude's discretion defaulting to no;
  revisit if the gate's cost drifts and nobody notices.
- **`/gsd-map-codebase --paths bench`** and a refresh of `.planning/codebase/TESTING.md`
  ("Warm run ~11 seconds", "Coverage measurement in place", "pytest 8+") — owed since
  Phase 13 (STATE.md); process, not product.
- **The gsd commit-timeout debt** (`2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md`)
  — its trigger text cites the hook's runtime; this phase updates the number, does not
  retire it (upstream gsd setting is the trigger).

</deferred>

---

*Phase: 15-the-gate-measured-and-pinned*
*Context gathered: 2026-10-03*
