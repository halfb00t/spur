# Phase 15: The Gate, Measured and Pinned - Research

**Researched:** 2026-10-03
**Domain:** Dev-tooling and CI for a pytest + CadQuery/OpenCascade project: gate wall-time profiling, `pytest-xdist` against spawned-process pools and a C++ kernel, `pytest-cov`/`coverage.py` across `multiprocessing` workers, pip constraints in a CI job that installs inside `make`.
**Confidence:** HIGH on the library behaviours (each was run on this host, with the evidence quoted below); MEDIUM on anything that only CI can show (the Linux run) and on timings (this host carried load 3-15 from other sessions during research, so every timing here is indicative and is **not** a D-04 number).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

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
- **D-10:** **`fail_under` = the baseline total rounded down to a whole percent; one more
  point down if that leaves under 0.25 pt of slack; the spread across D-05's three runs
  must fit inside the slack.** The three tolerance runs are run with `--cov` on, so their
  totals are the determinism check for free; if their spread exceeds the slack, the floor
  widens to cover it and the spread is recorded. On ~3,100 statements one point is ~31
  untested lines — a whole new untested function trips it; a timing-dependent `pool.py`
  branch does not. Rejected: baseline − 1.0 at two decimals (always one point, reads as a
  strange literal); baseline − 0.1 (a single timing-dependent branch could flip a run
  red with no code change — the flaky-gate failure, not the drift the floor is for).
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

### Deferred Ideas (OUT OF SCOPE)
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
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-verify-profiled | Per-stage wall time of `make verify`, pytest per-file and top-N `--durations`, xdist tolerance *measured*, every cut priced, written to `bench/RESULTS.md` | Non-pytest stages are ~0.7 s warm in total, so pytest is the whole gate (Pitfall 12). `--durations=N` output shape and the awk per-file aggregation are verified (Code Examples 1-2). A scratch run shows xdist tolerates the OCCT/`BuildPool` tests at N=4 on 3 full runs, with the memory shape and the cache-order risk named (Common Pitfalls 9-10). Tree-RSS sampler method verified (Code Example 3). |
| REQ-verify-at-the-bar | `make verify` at or under the human's bar, same method and host; no unaccepted cut; dev dependency in `[dev]` only; hook comment corrected | The Makefile `test` edit site, `PYTEST_WORKERS` spelling, and the `PYTEST_ARGS` escape hatches (`-n0`, `--no-cov`) are verified (Code Example 4, Pitfall 5). Every "~11 s" site is a grep away (D-19). `requirements.txt` untouched: both new packages are `[dev]` (Standard Stack). |
| REQ-coverage-floor | `pytest-cov` in `[dev]`, one baseline `--cov` run recorded, `fail_under` just under it, `make verify` gates on it, worker-process ASSUMPTION settled | **D-09's mechanism is stale and must change** (Pitfalls 1-2): pytest-cov 7 dropped subprocess measurement and `concurrency = ["multiprocessing"]` alone silently drops thread lines. A verified-working config is in Code Example 5. `fail_under` precedence, rounding (`precision`), the partial-run trap and the `.gitignore` gap are verified (Pitfalls 3-5, 6). D-10's "~31 lines per point" is wrong by 2.3x (Pitfall 7). |
| REQ-ci-installs-the-pinned-kernel | CI resolves `cadquery==2.8.0` / `cadquery-ocp==7.9.3.1.1`; green run URL shows the pair; tripwire stays; logged as `Lxx` | CI installs *inside* `make verify` (via `$(STAMP)`), so the mechanism is `PIP_CONSTRAINT` on the step, not a separate pip step (Pitfall 8). Verified by `pip install --dry-run` on macOS arm64 and on a simulated linux/x86_64 cp312 target that the constraint binds and still resolves the pair, with the dev extras and both new packages (Code Example 6). `tests/test_pr_land.py`'s ci.yml parser is safe for the edit (Pitfall 11). |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

Extracted from `/Users/halfb00t/git/halfb00t/spur/CLAUDE.md` (a symlink to `AGENTS.md`). Treat with the authority of locked decisions.

- **The gate is `make verify`** (ruff, mypy `--strict`, import-linter, unfinished-work scan, pytest). Nothing is "done" until it passes; state the command and the result line in the reply. `make check` adds Docker checks.
- **Stop and ask** when: an architectural claim is not in the decision log; a locked decision (Lxx) looks wrong (propose superseding, do not ignore); a library behaviour is unverified after a real check; evidence conflicts (doc vs code vs prior decision vs the human); a destructive operation; a stability-for-speed trade. Ask format: trigger, 2-3 options, recommendation, wait.
- **New non-trivial choice** = 2-3 options + tradeoffs + recommendation, human picks, logged as a new `Lxx`. Do not re-litigate logged decisions. Flag guesses as `ASSUMPTION:`.
- **Standing rules:** a number the tool prints is a number someone will cut metal to (L08); a parameter the user did not set must never silently change the part (L05, L03). This phase touches neither (no `src/`, no fixture), but the fixture byte-unchanged rule is the standing proof.
- **Keep it simple:** simplest solution that works; surgical edits; no speculative abstraction; one concern per commit.
- **Finishing work:** new behaviour ships with tests in the same change; performance/memory claims are measured and the numbers recorded (the `docs/review-2026-09-21.md` / `plan-2026-09-21.md` standard); no `TODO`/`pass`/unreachable branch (`make verify` scans for the markers).
- **Debt and ideas live in files:** `docs/<dir>/TEMPLATE.md`, INDEX row in the same commit; retire debt in the fixing commit (`Status: resolved`, sha, `git mv` to `resolved/`, INDEX row moved). State before the final reply whether any item was filed and its path.
- **Tools:** reuse `make` targets; gsd skills for planning/execution; Conventional Commits in normal prose; no formatter (L16) - hand-align Makefile and `pyproject.toml` edits to the existing comment style.
- **Code style (`docs/CODING_VALUES.md`):** comments explain *why* and carry the measurement; `calc.py` never imports `cadquery`; vendor types stop at their boundary; English throughout.
- **Cross-CLI review:** whoever wrote the diff does not review it.
- **Project skills:** `.ai_skills/` and `.claude/skills/` hold only a `README.md` (no SKILL.md files exist), so there are no project skill patterns to apply.

## Summary

This phase is mostly measurement and configuration, and the research found the library facts the plan depends on. Four of them contradict wording in CONTEXT.md and need correcting in the plan (none changes a decision's *intent*): (1) pytest-cov 7.x removed its subprocess/`.pth` measurement, so D-09's "pytest-cov's subprocess hook ... do the rest" is stale; (2) D-09's `concurrency = ["multiprocessing"]` on its own silently stops tracing threads, which drops real `pool.py` and `app.py` lines; (3) D-10's "~3,100 statements, one point is ~31 lines" is really 1,069 statements + 294 branches, so one point is ~13.6 units; and `fail_under` rounds to `precision` (default 0), which moves the real trip point half a point below the number written; (4) CI has no separate install step - pip runs inside `make verify` via `$(STAMP)` - so D-13's constraint must be `PIP_CONSTRAINT` on the `make verify` step.

The scratch measurements (all indicative: the host carried load 3-15 from ten logged-in users) say the profile will be dominated by `tests/test_model.py` (201 items, ~158 s of the ~190 s serial gate) and that the non-pytest stages total under a second warm. A full 927-test run at `-n 4` with coverage finished in 83-93 s, three times, 927 passed each, with a 169-test subset also producing byte-identical coverage totals serial vs `-n 4`. Coverage cost on the heavy kernel file was +2 %; it only multiplies the pure-Python tests (which cost under a second in total). These are research-grade samples, not D-04 rows; the executor still owes the alternating A/B runs.

The one non-deterministic item found is worker-process coverage: in one of three full `-n 4` runs, `pool.py` lines 63-67 and 222 (the only real `BuildPool` build path) were missing, moving the total by 3 statements (~0.22 pt). The cause is unproven (`[ASSUMED]`: worker data written after the combine, or a lost xdist-worker flush). It is exactly what D-10's "spread must fit inside the slack" clause is for, so the three tolerance runs are the right place to size the floor.

**Primary recommendation:** add `pytest-xdist>=3.8` and `pytest-cov>=7.1` to `[dev]`; config coverage with `concurrency = ["multiprocessing", "thread"]`, `parallel = true`, `sigterm = true` and `[tool.coverage.report] fail_under`, `precision = 2`; `make test` runs `-n $(PYTEST_WORKERS) --cov` and reads the floor from config; add `.coverage*` to `.gitignore`; pin the kernel with `env: PIP_CONSTRAINT: requirements.txt` on CI's `make verify` step plus a post-step version print; measure everything the house way into one `bench/RESULTS.md` section.

## Architectural Responsibility Map

This phase has no web tiers. The "tiers" are the places a gate behaviour can live.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Parallel test execution (`-n N`) | Makefile `test` recipe | - | D-07: not `addopts`, because `make test-image` installs only `pytest httpx` (`Makefile:83-89`) and a bare `.venv/bin/pytest` must stay serial for `-x`/`--pdb`. |
| Coverage measurement config (`concurrency`, `parallel`, `sigterm`, `source`, `branch`) | `pyproject.toml` `[tool.coverage.run]` | - | Read by coverage.py in every process it starts, including spawned `BuildPool` workers; must not live on a CLI flag. |
| Coverage floor value (`fail_under`, `precision`) | `pyproject.toml` `[tool.coverage.report]` | Makefile `--cov` | pytest-cov falls back to the config value when `--cov-fail-under` is absent (verified, plugin.py:270-271), so one literal, one place. |
| Coverage *enablement* in the gate | Makefile `test` recipe (`--cov`) | - | Same reason as `-n`: a bare `pytest` and `make test-image` stay coverage-free. |
| Kernel-pair pin in CI | `ci.yml` `test` job (`PIP_CONSTRAINT`) | `requirements.txt` (the constraint data) | The install runs inside `make verify` -> `$(STAMP)`; the env var is the only seam that does not touch the Makefile (D-14 keeps local `make venv` unchanged). |
| Proof the pin held | `ci.yml` post-step version print | `test_the_fixture_was_captured_on_the_kernel_this_run_uses` | The print states the pair; the tripwire fails loudly if the pair ever differs from the fixture's provenance. |
| Measurement record | `bench/RESULTS.md` (one new section) | `decision_log.md` L34, debt files | House rule 12 D-17: every number behind a committed command and recorded with host state. |
| Hook wall-time claim | `.pre-commit-config.yaml` comment | L34 (for L13's text) | D-19: L13 is append-only. |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pytest-xdist | `>=3.8` (3.8.0, uploaded 2025-07-01) | `-n N` parallel runs | The pytest-dev org's own plugin; ~36.7M downloads/week `[VERIFIED: pypistats.org API]`. Installed and exercised against pytest 9.1.1 on this host. Workers are execnet `popen` subprocesses (fresh interpreters, not forks of a kernel-loaded parent) `[CITED: xdist/workermanage.py in the installed 3.8.0, makegateway/popen at lines 68-186]`. |
| pytest-cov | `>=7.1` (7.1.0, uploaded 2026-03-21) | `--cov`, `--cov-fail-under`, combine across xdist workers | pytest-dev org plugin, ~51M downloads/week `[VERIFIED: pypistats.org API]`. Floor 7.1 because 7.1.0 "fixed total coverage computation to always be consistent, regardless of reporting settings ... can make --cov-fail-under behave different depending on reporting options" `[CITED: pytest-cov.readthedocs.io/en/latest/changelog.html]` - a floor that gates must not depend on report flags. |

### Supporting (installed transitively, not listed in `[dev]`)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| coverage | 7.16.2 (pulled by pytest-cov; pytest-cov 7.0 requires >=7.10.6 `[CITED: changelog]`) | The measurement engine; owns `[tool.coverage.*]` | Configured, never imported by project code. |
| execnet | 2.1.2 (pulled by xdist) | xdist's worker transport | None. |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `concurrency = ["multiprocessing","thread"]` + `parallel` + `sigterm` | `patch = ["subprocess"]` (coverage >=7.10) | Also measured `pool.py` at 100 %, but it starts coverage in *every* Python process through the `a1_coverage.pth` hook and left empty (0 measured lines) `.coverage.<host>.pid*` files uncombined in the data dir after several runs (seen with the `patch`-only config serial, the `patch` + `concurrency` config serial and at `-n 4`). Config E left none in any of its runs. Prefer explicit multiprocessing config; revisit only if a future test needs a non-multiprocessing subprocess measured. |
| Floor in `[tool.coverage.report]` only | `--cov-fail-under=NN` also in the Makefile | Two literals that can drift. REQ-coverage-floor's text says "`--cov --cov-fail-under`"; satisfy it by amending the REQ sentence (already being amended in this PR) rather than duplicating the number. |
| awk over `--durations=0` for per-file shares | A committed `bench/` script, or `--junit-xml` + parser | A new script needs tests under mypy `--strict` and `disallow_any_explicit` (`make typecheck` covers `bench`). The awk is two lines and its inputs are visible in the output. See Open Question 3 on 12 D-17. |

**Installation (edit `pyproject.toml` `[project.optional-dependencies] dev`, lines 20-27):**
```toml
    "pytest-xdist>=3.8",
    "pytest-cov>=7.1",
```
`$(STAMP)` depends on `pyproject.toml` (`Makefile:33`), so the next `make` target re-runs `pip install -e '.[dev]'` and installs both into `.venv` `[VERIFIED: Makefile:33-42]`. The same rule fires on *any* later `pyproject.toml` edit (including `[tool.coverage.*]`), costing a few seconds of pip.

**Version verification:** `pip index versions pytest-cov` -> 7.1.0 latest; `pip index versions pytest-xdist` -> 3.8.0 latest; `pip index versions coverage` -> 7.16.2; `pip index versions execnet` -> 2.1.2 (all run 2026-10-03 with pip 26.1.2).

## Package Legitimacy Audit

Ran `gsd-tools query package-legitimacy check --ecosystem pypi pytest-cov pytest-xdist coverage execnet`. The seam returned **SUS** for all four; the reasons are `unknown-downloads` (PyPI's JSON API publishes no download counts), `no-repository` for pytest-cov (its PyPI `project_urls` key is `Sources`, not `Source`), and `too-new` for coverage (7.16.2 was published 2026-09-27). Independent evidence is in the table. The two packages are named by the human in locked decisions D-05 and D-12.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| `pytest-xdist` [WARNING: flagged as suspicious by the seam (unknown-downloads) - verify before using.] | PyPI | first upload 2010-01-18 (16 yrs) | ~36.7M/week (pypistats) | github.com/pytest-dev/pytest-xdist | SUS (seam artefact) | Flagged - planner adds a one-line `checkpoint:human-verify`; D-05 and the D-01 checkpoint already name it, so the human's naming is the verification to record. |
| `pytest-cov` [WARNING: flagged as suspicious by the seam (unknown-downloads, no-repository) - verify before using.] | PyPI | first upload 2010-04-25 (16 yrs) | ~51.0M/week (pypistats) | github.com/pytest-dev/pytest-cov | SUS (seam artefact) | Flagged - as above; D-12 names it. |
| `coverage` (transitive) | PyPI | ancient (coveragepy) | n/a | github.com/coveragepy/coveragepy | SUS (`too-new`: latest release 2026-09-27) | Not a direct dependency; pytest-cov selects it. Leave unpinned; pytest-cov's own floor (>=7.10.6) applies. |
| `execnet` (transitive) | PyPI | n/a | n/a | execnet.readthedocs.io | SUS (unknown-downloads) | Transitive of xdist; no action. |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** `pytest-xdist`, `pytest-cov` (seam artefacts, see above) - planner inserts a `checkpoint:human-verify` before the install; `requirements.txt` gains nothing (all four stay out of the 31-pin runtime closure).

No `postinstall`-style hooks exist on PyPI wheels; the only install-time file coverage adds is `a1_coverage.pth` in `site-packages`, shipped inside the `coverage` wheel and inert unless a coverage env var is set `[VERIFIED: ls sv/lib/python3.12/site-packages showed a1_coverage.pth after pip install pytest-cov]`.

## Architecture Patterns

### System Architecture Diagram

```
 git commit
     |
     v
 .pre-commit-config.yaml (always_run) --> make verify            CI: ci.yml `test (3.12)` job
     |                                        ^                      |  env PIP_CONSTRAINT=requirements.txt
     |                                        |                      v
     |                           (same gate) -+---------------- make verify PYTHON=python
     v
 +---------------- make verify ----------------------------------------------------------+
 |  $(STAMP) (if pyproject.toml newer): venv + pip install -e '.[dev]'  <-- constrained   |
 |  lint (ruff) -> typecheck (mypy) -> lint-imports -> no-fake-done      (<1 s warm total)|
 |  test:  python -m pytest -n N --cov $(PYTEST_ARGS)                                     |
 +---------------------------------------------------------------------------------------+
                    |
                    v
          pytest controller process  (starts coverage; owns the combine + report)
                    |  execnet popen
        +-----------+-----------+------------ ... N xdist workers (fresh interpreters)
        |                       |
   kernel tests in-process   TestClient(app) lifespan ---> BuildPool(2)  [tests/test_pool.py]
   (test_model, regression,                                  |  mp.get_context("spawn")
    test_cli, test_api)                                      v
        |                                      2 spawn workers: _warm -> import spur.model
        |                                      build_export  (coverage via `multiprocessing`
        |                                      patch; SIGTERM handler via `sigterm = true`)
        v                                                    |
   .coverage.<host>.<pid>.<rand>  (parallel = true)  <-------+
        |
        v
   pytest-cov combines -> total -> round(total, precision) < fail_under ? session.testsfailed += 1
                    |
                    v
        exit code 1 (red on the floor)  /  0
```

The measurement path (executor) is separate and sequential: serial profile -> N sweep -> 3 tolerance runs at the knee with `--cov` -> coverage baseline -> coverage cost A/B -> D-01 checkpoint -> apply N/bar -> before/after A/B -> L34.

### Recommended Project Structure
No new directories. Files touched (per D-20), plus one the CONTEXT list misses:
```
Makefile                          # test recipe: -n $(PYTEST_WORKERS) --cov; PYTEST_WORKERS ?= N
pyproject.toml                    # [dev] +2; [tool.coverage.run] +3 keys; [tool.coverage.report] new
.gitignore                        # ADD .coverage* (and htmlcov/) -- not in D-20's list; see Pitfall 6
.github/workflows/ci.yml          # PIP_CONSTRAINT env; post-step version print; "where the pin lives" comment
.pre-commit-config.yaml           # lines 6-8 "A warm run is ~11 s" -> measured number
tests/regression/test_pre_v0_2.py # docstring of the tripwire (lines 80-90); NOT pre_v0_2.json
bench/RESULTS.md                  # one Phase 15 section after "Composition pass test cost (Phase 12, D-10)"
docs/architecture/decision_log.md # L34 (append-only)
docs/tech_debt/{active->resolved}/ # two files + INDEX rows
```

### Pattern 1: Coverage config that counts spawned-worker lines
**What:** let coverage's own multiprocessing support instrument `BuildPool`'s spawned children; keep thread tracing; write per-process data files; save on SIGTERM.
**When to use:** this repo's `[tool.coverage.run]` (currently `branch = true`, `source = ["src/spur"]` at `pyproject.toml:125-129`).
**Example:** see Code Example 5. Verified results: `tests/test_pool.py` alone, `pool.py` 100 % (0 missing of 54 statements, 0 of 6 branches) under this config, versus `54 3 6 0 95% 50, 63-67` under the current config (workers uncounted).

### Pattern 2: House measurement method (D-10 / D-04)
**What:** alternating A/B full `make verify` under `/usr/bin/time -p`, load read from `sysctl -n vm.loadavg` before each, host-state header (machine facts, HEAD, loads, `SPUR_*`), delta = mean(B) - mean(A). The precedent section is `bench/RESULTS.md` "Composition pass test cost (Phase 12, D-10)" (lines 2130-2198): Host state, Same-session alternating runs (Run | Code | Load | pytest | Wall), make verify wall time, Regression fixture share, Gate decision with the human's verbatim answer.
**Example (what a row looks like there):** `| A1 | c9a169d | 2.87 | 621 passed in 183.67s | 193.30 |`.

### Anti-Patterns to Avoid
- **`concurrency = ["multiprocessing"]` without `"thread"`.** Replaces the default `thread`; the portal/lifespan thread's lines disappear (Pitfall 2).
- **`-n` or `--cov` in `addopts`.** Breaks `make test-image` and makes every debug run parallel and coverage-gated (D-07; Pitfall 5).
- **A separate `pip install -c requirements.txt` step in `ci.yml`.** Nothing is installed there; the venv is created later by `make` (Pitfall 8).
- **`-n auto`.** Rejected by D-06; the memory reading would decide after the fact.
- **Re-running a red tolerance run until green.** House rule (11-06, 13 D-05): record as measured.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Parallel test distribution | A custom multiprocessing runner or per-file shell fan-out | `pytest-xdist` (`-n N`, default `--dist load`) | Collection, scheduling, result merging, per-worker tmp dirs (`tmp_path` is per-worker, and the suite uses only `tmp_path` for writes - verified by grep). |
| Cross-process coverage merge | Reading `.coverage.*` and summing | `pytest-cov` (combines across xdist workers and `parallel` files) | Branch arcs and context merging are not additive. |
| The floor check | A test asserting the percentage, or a `grep` in the Makefile | `[tool.coverage.report] fail_under` read by pytest-cov | Exit code 1 plus a "Coverage failure" line is already produced and was shown to gate (Pitfall 4). |
| Per-file duration shares | A pytest plugin or conftest hook | `--durations=0 --durations-min=0` piped to a 2-line awk (Code Example 2) | pytest has no per-file aggregation; the awk reads the documented line shape. |
| Process-tree RSS | `psutil` (a new dependency) | A `ps -axo pid=,ppid=,rss=` sampler loop (Code Example 3) | No dependency; `/usr/bin/time -l` reports only the waited-for child. |
| Pinning the kernel pair | A new `==` line for `cadquery-ocp` in `pyproject.toml`, or a second pin list | The existing `requirements.txt` as a constraints file | One source of truth for the pair (L12); D-13. |

**Key insight:** every piece of machinery this phase needs already exists; the work is configuration and honest measurement. The risk is in the interactions (rounding, thread tracing, where pip runs), all of which were reproduced below.

## Common Pitfalls

### Pitfall 1: pytest-cov 7 no longer measures subprocesses (D-09's premise is stale)
**What goes wrong:** D-09 says "pytest-cov's subprocess hook and combine do the rest". Under pytest-cov >= 7.0 there is no subprocess hook.
**Why:** "Dropped support for subprocesses measurement. It was a feature added long time ago when coverage lacked a nice way to measure subprocesses created in tests. It relied on a `.pth` file, there was no way to opt-out and it created bad interactions with coverage's new patch system added in 7.10." `[CITED: pytest-cov.readthedocs.io/en/latest/changelog.html, 7.0.0 (2025-09-09)]` The docs now say to use `patch = ["subprocess"]` `[CITED: pytest-cov.readthedocs.io/en/latest/subprocess-support.html]`.
**How to avoid:** configure coverage.py itself (`concurrency = [..."multiprocessing"...]`, Code Example 5). Verified on this host, pytest-cov 7.1.0 + coverage 7.16.2: with the current config `pool.py` reads `54 3 6 0 95% 50, 63-67` (the `_warm` and `build_export` bodies uncounted); with the config below it reads 100 %.
**Warning signs:** `pool.py` stuck at 95 % with 50, 63-67 missing in the baseline report.

### Pitfall 2: `concurrency = ["multiprocessing"]` alone drops thread lines
**What goes wrong:** the key replaces coverage's default (`"thread"`, `[CITED: coverage.readthedocs.io/en/latest/config.html]` "concurrency (multi-string, default "thread")"). Code that runs in a thread (the `TestClient` lifespan/portal thread that builds the `BuildPool` and shuts it down) stops being traced.
**Evidence (run on this host, `tests/test_pool.py` only):** D-09's literal config (`concurrency = multiprocessing`, `parallel`, `sigterm`) -> `pool.py 54 7 6 0 85% 74-91, 222, 225-226`, TOTAL 46 %. Adding `thread` -> `pool.py 54 0 6 0 100%`, TOTAL 53 % (also identical with `patch = ["subprocess"]`). The loss is silent: tests pass, the number is just too low, so a floor set on it would be too low too.
**How to avoid:** `concurrency = ["multiprocessing", "thread"]`.

### Pitfall 3: `fail_under` rounds to `precision` (default 0) before comparing
**What goes wrong:** `coverage.results.should_fail_under` is `round(total, precision) < fail_under` `[VERIFIED: sv/lib/python3.12/site-packages/coverage/results.py:484-503, read this session]`. At the default `precision = 0`, a floor of 97 trips only below 96.5, and pytest-cov prints a *contradictory* line.
**Reproduced:** total 45.93 %, `fail_under = 46`, default precision -> `FAIL Required test coverage of 46.0% not reached. Total coverage: 45.93%` and **exit code 0**. With `precision = 2` -> `ERROR: Coverage failure: total of 45.93 is less than fail-under=46.00`, **exit code 1**.
**How to avoid:** set `[tool.coverage.report] precision = 2`, and compute D-10's slack with the same rounding. Also note `fail_under = 100` is special-cased (must be exactly 100).

### Pitfall 4: the floor really does gate from config alone
`pytest-cov` copies the config value when the CLI flag is absent: `if self.options.cov_fail_under is None and hasattr(cov_config, 'fail_under'): self.options.cov_fail_under = cov_config.fail_under` `[VERIFIED: sv/lib/python3.12/site-packages/pytest_cov/plugin.py:270-271]`. On failure it does `session.testsfailed += 1` (plugin.py:~380), i.e. pytest exit code 1. Reproduced: `[report] fail_under = 80` with a `test_calc.py`-only run -> exit code 1. The CLI flag wins when both are present, which is the drift hazard of writing the number twice.

### Pitfall 5: partial runs now fail the floor
**What goes wrong:** the documented way of reading the fixture share is `make test PYTEST_ARGS="tests/regression -q"` (CONTEXT code_context; 12's RESULTS section). With `--cov` in the recipe and a floor in config, that run reports ~46 % and exits 1.
**How to avoid:** the escape hatch is `--no-cov` in `PYTEST_ARGS` (reproduced: `--cov ... --no-cov` exits 0 with no `CovDisabledWarning` turned into an error by `filterwarnings = error`), and `-n0` to run serially. Say so in the Makefile comment beside `test` and in the RESULTS section's method note. Also: every profile/`--durations` run should pass `--no-cov` (or the planner should profile before `--cov` lands - plan order (1) already does).

### Pitfall 6: `.coverage*` is not gitignored
`.gitignore` (read this session) has no `.coverage`, `.coverage.*` or `htmlcov` entry. `pytest --cov` writes `.coverage` into the cwd on every `make verify`, i.e. on every commit through the hook. Add `.coverage*` (and `htmlcov/` if an HTML report is ever produced). This file is not in D-20's list.

### Pitfall 7: D-10's unit arithmetic is wrong by ~2.3x
**Measured:** `src/spur` is **1,069 statements and 294 branches** (`coverage report`, TOTAL row, every run). With `branch = true` the percentage is `(covered statements + covered branches) / (statements + branches)` over 1,363 units, so **one point = ~13.6 units**, not "~31 untested lines" on "~3,100 statements". The qualitative argument of D-10 survives (a whole new untested function of ~14+ lines trips a one-point slack; one timing-dependent branch does not) but numbers quoted in L34 must use 1,069 / 294.
**Scratch totals (full suite, `-n 4`, config E):** 26 missed statements -> 96.99 %; 23 and 23 missed -> ~97.2 % (each statement = 0.073 pt). By D-10: whole percent below = 97, slack ~0.2 < 0.25, so `fail_under = 96`; with `precision = 2` the effective trip point is 95.995, ~1.2 pt (~16 units) under the baseline.

### Pitfall 8: CI has no install step; the constraint must ride on `make verify`
**What goes wrong:** D-13 reads "`pip install -c requirements.txt …`, or `PIP_CONSTRAINT=requirements.txt` on the step". `ci.yml` (lines 19-27, read this session) has only `checkout`, `setup-python` (with `cache: pip`) and `- run: make verify PYTHON=python`. The venv and `pip install -e '.[dev]'` happen inside `make verify` (`Makefile:39-41`); the CI log confirms it: `python -m venv .venv`, `.venv/bin/python -m pip install --quiet --upgrade pip`, `.venv/bin/python -m pip install -e '.[dev]'` appear under "Run make verify PYTHON=python" `[VERIFIED: gh run view 37116412012 --log]`. A `-c` flag in a separate step installs nothing into `.venv`.
**How to avoid:** `env: PIP_CONSTRAINT: requirements.txt` on the `make verify` step (or job). Verified that it binds: `PIP_CONSTRAINT=requirements.txt pip install --dry-run --ignore-installed --report ... -e '.[dev]'` resolves fastapi 0.141.1 / starlette 1.6.0 / uvicorn 0.53.0 / fonttools 4.65.0 (the closure) where the unconstrained resolve gives 0.142.2 / 1.7.0 / 0.54.0 / 4.66.1; it is identical to the `-c requirements.txt` flag form. A conflicting constraint (`cadquery-ocp==8.0.1.0.0`) fails with `ResolutionImpossible`, so it fails closed. Relative path works because make runs in the repo root; use `${{ github.workspace }}/requirements.txt` if you prefer not to depend on that.
**Side facts (verified):** a constraint on `hatchling==1.24.0` (below the build requirement `hatchling>=1.25`) was *ignored* by build isolation in both the env and flag forms (pip 26.2.1), so the closure cannot break the editable build; and the dev tools are not in the closure, so CI's ruff/mypy float (CI ran ruff 0.16.10 / mypy 2.4.0 on 2026-10-03; this `.venv` has 0.16.8 / 2.3.1).

### Pitfall 9: xdist gain is sublinear; the serial run is already multi-core
`tests/regression` serial under `/usr/bin/time -l`: **19.15 s real, 24.35 s user, 23.76 s sys, 588,627,968 B max RSS** (~2.5 cores busy on average) `[VERIFIED: run this session]`; STATE.md records "pytest at ~9 cores" on a cold run (Phase 11 note). `[ASSUMED]` mechanism: OpenCASCADE/VTK threading inside a single kernel call. So the sweep's knee is below 12 and N=12 may oversubscribe. Measured scratch: 169-test subset 61-64 s serial -> 21-22 s at `-n 4`; full suite 83-93 s at `-n 4` against CI's serial **927 passed in 193.21 s** `[VERIFIED: CI run 37116412012 log line 491]`.

### Pitfall 10: process-global caches make test cost order- and worker-dependent
`build()` is behind an `lru_cache` and `_EXPORTS` is a parent byte cache (tests bypass them where it matters: `tests/test_model.py` lines ~162, 238, 325, 456, 583, 598, 884, 919 comments; `tests/test_pool.py` 258, 289). Under xdist, which tests share a process changes cache hits, so total CPU can rise while wall falls. No test failed on this in the scratch runs, but if a tolerance run fails on a cache-order assumption record it per D-08 and use `xdist_group`. Note: `xdist_group` is registered by xdist itself `[VERIFIED: pytest --markers listed "@pytest.mark.xdist_group ... Provided by pytest-xdist." with xdist installed]`, so the CONTEXT discretion item about declaring it in `markers` is moot - declare nothing.

### Pitfall 11: the ci.yml drift test is a regex parser
`tests/test_pr_land.py::_effective_job_names` (lines 223-266, read this session) takes job ids as two-space keys matching `^  ([a-zA-Z][\w-]*):\s*$` and a job `name:` only as `^    name:` (exactly four spaces). A step-level `env:` (8 spaces) or job-level `env:` (4 spaces, no `name:`) is invisible to it. Do not add a four-space `name:` under `test:`; `required-jobs.txt` stays `test (3.12)`, `vendor-bundle`, `image`. Run `tests/test_pr_land.py` after the edit.

### Pitfall 12: nothing outside pytest matters to wall time
Single samples at load 6.83 on warm caches (`.mypy_cache`, `.import_linter_cache`): `make lint` 0.08 s, `make typecheck` 0.44 s ("no issues found in 37 source files"), `make lint-imports` 0.12 s ("5 kept, 0 broken"), `make no-fake-done` 0.02 s. The profile's per-stage table will say pytest is ~99.9 % of the gate on this host; CI's cold stages are the only place the others show. Not D-04 rows.

### Pitfall 13: a lost worker flush moves the total by ~0.22 pt (unproven cause)
Observed: three full `-n 4` runs with config E -> missed statements 26, 23, 23. The 26 run lacked `pool.py` lines 63-67 (`build_export`, the worker body) and 222 (`return await self._run_with_timeout(...)`, `export()`), i.e. the only real worker-build path (`test_a_real_worker_builds_and_downloads`) went unrecorded that once. Not reproduced in 5 further `-n 4` runs of `test_pool.py` + `test_api.py` (all 100 %), 4 serial `test_pool.py` runs, and 2 more full runs. `[ASSUMED]` cause: worker data written after the controller's combine (workers are shut down with `shutdown(wait=False)`), or a lost xdist-worker flush under load (that run had a 1 s `ps` sampler and load 6-15). It is one test's worth of lines: size the floor's slack to cover it (D-10 already says so) and let the three tolerance runs measure the real spread.

### Pitfall 14: D-16's "absent on a cache hit" premise is false for this workflow
The `actions/setup-python` pip cache restores pip's *download* cache; the venv is created fresh each run, so pip's install output is present even on a cache hit. Run 37116412012's log shows both `Cache hit for: setup-python-Linux-x64-24.04-...` and, at 10:26:51, `Successfully installed ... cadquery-2.8.0 cadquery-ocp-7.9.3.1.1 cadquery-ocp-proxy-7.9.3.1.1 ... mypy-2.4.0 ... pytest-9.1.1 ... ruff-0.16.10` `[VERIFIED: gh run view 37116412012 --log]`. The explicit print step is still a good, cheaper-to-read proof (D-16 stands), but its stated justification should be corrected in L34.

### Pitfall 15: injected-timeout tests under load
`tests/test_pool.py` sets `pool.timeout = 0.2` (lines 164, 378) and `1.0` (line 446), and joins the manager thread with `timeout=5` (line 189). A resolved debt records these flaking on the GitHub runner for a different reason (`ae052f8`). D-05's three-consecutive-green rule is the right gate; if one fails, the failing test goes to the debt/D-08 path, not a retry.

## Code Examples

### 1. `--durations` output shape (verified, pytest 9.1.1)
```
$ python -m pytest tests/test_calc.py -q --durations=3
============================== slowest durations ===============================
0.03s call     tests/test_calc.py::test_the_count_floor_never_exceeds_the_exact_count
...
```
`--durations=N` lists the N slowest setup/call/teardown phases; `--durations-min=N` default is 0.005 s, or 0.0 with `-vv` `[VERIFIED: pytest --help]`. Each line is `<seconds>s <phase> <nodeid>`. With N small, a trailing "(K durations < 0.005s hidden. Use -vv to show these durations.)" line appears.

### 2. Per-file aggregation (pytest does not provide it)
```bash
.venv/bin/python -m pytest --no-cov -n0 -q --durations=0 --durations-min=0 > /tmp/d.txt   # profile run: serial, no coverage
grep -E '^[0-9.]+s (call|setup|teardown) ' /tmp/d.txt \
  | awk '{split($3,a,"::"); t[a[1]]+=$1; n[a[1]]++} END{for(f in t) printf "%8.2fs %5d %s\n", t[f], n[f], f}' \
  | sort -rn
```
Verified on a 431-item run: `0.12s 81 tests/test_skip_tokens.py`, `0.07s 1212 tests/test_calc.py` (1212 = 404 items x 3 phases). Parametrised ids containing `test_x.py::...` text (the regression ids do) are safe because the split is on the first `::` only. Before `--cov` lands in the Makefile, drop `--no-cov`/`-n0`.

### 3. Tree-RSS sampler (what `/usr/bin/time -l` cannot give)
```bash
# sum RSS (KB) of $PID and all its descendants once a second; keep the max
ps -axo pid=,ppid=,rss= | awk -v root=$PID '{p[$1]=$2; r[$1]=$3; ids[NR]=$1}
  END{keep[root]=1; c=1; while(c){c=0; for(i in ids){id=ids[i]; if(!(id in keep)&&(p[id] in keep)){keep[id]=1;c=1}}}
      t=0;n=0; for(id in keep){t+=r[id];n++} print t, n}'
```
Scratch result: full suite, `-n 4`, **peak tree RSS sum 3,648 MiB over a max of 8 processes** (1 s sampling). `[ASSUMED]` that a per-process RSS sum overstates real memory because file-backed pages of the OCCT/VTK libraries are shared between processes; say "sum of per-process RSS" in the host-state header. Single serial `pytest tests/regression`: 588,627,968 B max RSS (`/usr/bin/time -l`).

### 4. Makefile `test` recipe (edit site `Makefile:70-71`)
```make
# N is the knee of bench/RESULTS.md's xdist sweep (12-CPU M2 Max); -n0 runs serially, and
# --no-cov skips the coverage floor for a partial run:
#   make test PYTEST_ARGS="tests/regression -q --no-cov -n0"
PYTEST_WORKERS ?= <N from the sweep>

test: $(STAMP)  ## run the test suite (a cold first run is page cache, not the tests)
	$(PY) -m pytest -n $(PYTEST_WORKERS) --cov $(PYTEST_ARGS)
```
`PYTEST_ARGS` lands last, so `-n0` and `--no-cov` override cleanly (verified: `--cov ... --no-cov` exits 0). The floor is read from `[tool.coverage.report]`.

### 5. `pyproject.toml` coverage blocks (replace `pyproject.toml:125-129`; verified in TOML form, `-n 2`, `pool.py` 100 %, TOTAL 52.97 % on `test_pool.py`)
```toml
[tool.coverage.run]
branch = true
source = ["src/spur"]
# BuildPool's spawned workers (pool.py:35) are separate processes: "multiprocessing" makes
# coverage instrument them, "thread" must be listed too or setting this key drops the
# default and the lifespan thread's lines vanish, "parallel" writes one data file per
# process for pytest-cov to combine, "sigterm" saves a worker that pool.py:205 terminates.
concurrency = ["multiprocessing", "thread"]
parallel = true
sigterm = true

[tool.coverage.report]
# <baseline>% read on <date> (bench/RESULTS.md "<section>"), minus the D-10 slack. precision 2 so
# the number printed and the number compared are the same one (the default rounds to 0 dp).
fail_under = <D-10 number>
precision = 2
```
`sigterm = true` was measured to change nothing in this suite today (identical per-line output with it on and off across `test_pool.py`, 2 runs each) because the only terminated workers run test helpers outside `src/spur`; keep it as the guard the terminate path needs (`pool.py:204-205`: `for proc in executor._processes.values(): proc.terminate()`), and say in the comment that it is a guard, not a measured effect. The wedged-worker test's `proc.exitcode == -signal.SIGTERM` assertion (`tests/test_pool.py`, just after the `manager.join(timeout=5)` at line 189) still passed with it on (16 passed).

### 6. CI pin and proof (`ci.yml` lines 24-27)
```yaml
      # The kernel pair the regression fixture was captured on (cadquery 2.8.0 /
      # cadquery-ocp 7.9.3.1.1) is pinned here: requirements.txt, the L12 closure, is a pip
      # constraints file for the install `make verify` runs inside $(STAMP). A kernel bump
      # moves it with docker/refresh-requirements.sh, and the fixture with `make fixture.regen`;
      # test_the_fixture_was_captured_on_the_kernel_this_run_uses is the tripwire (L34).
      - run: make verify PYTHON=python
        env:
          PIP_CONSTRAINT: requirements.txt
      - name: kernel pair this run resolved
        if: always()
        run: .venv/bin/python -c "from importlib.metadata import version as v; print('cadquery', v('cadquery'), 'cadquery-ocp', v('cadquery-ocp'))"
```
Local preflight that needs no CI and no install (verified, pip 26.2.1, macOS arm64):
```bash
PIP_CONSTRAINT=requirements.txt .venv/bin/python -m pip install --dry-run --ignore-installed \
  --quiet --report /tmp/r.json -e '.[dev]'   # then read cadquery / cadquery-ocp out of "install"
```
Result: 83 packages, `cadquery 2.8.0`, `cadquery-ocp 7.9.3.1.1`, `cadquery-ocp-proxy 7.9.3.1.1`, `vtk 9.6.2`, identical for env and flag forms. A linux/x86_64 cp312 simulation (`--platform manylinux_2_31_x86_64 ... --only-binary=:all:` with the dev extras plus `pytest-cov` and `pytest-xdist`) also resolved the same pair with the constraint (86 packages) - `cadquery_ocp-7.9.3.1.1-cp312-cp312-manylinux_2_31_x86_64.whl` exists on PyPI `[VERIFIED: pypi.org/pypi/cadquery-ocp/7.9.3.1.1/json]`. This is a simulation; only the CI run is the proof.

### 7. The scratch red-on-the-floor run (no file deletion needed)
```bash
make verify PYTEST_ARGS="--ignore=tests/test_cli.py"
```
`--ignore` removes the file from the run without touching the tree (a literal deletion would dirty the tree under the pre-commit stash dance). `test_cli.py` is only a candidate (`cli.py` is 88 of 1,069 statements) and **was not run end to end**: the executor must pick a file whose loss exceeds the D-10 slack and record the total actually read. A single-file partial run reproduced the shape: `ERROR: Coverage failure: total of 46 is less than fail-under=80` and `FAIL Required test coverage of 80.0% not reached. Total coverage: 45.93%`, exit 1. Record the file named, the total read and the floor, never commit anything.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| pytest-cov `.pth` subprocess measurement | coverage.py's own `patch = [...]` / `concurrency` config | pytest-cov 7.0.0, 2025-09-09 `[CITED: changelog]` | D-09's "subprocess hook" does not exist; configure coverage directly. |
| pytest-cov total could vary with report flags | consistent total regardless of reporting settings | pytest-cov 7.1.0, 2026-03-21 `[CITED: changelog]` | Why the `[dev]` floor is `>=7.1`. |
| coverage `patch = subprocess` | available | coverage 7.10 `[CITED: coverage.readthedocs.io config]` | Alternative to explicit multiprocessing config; not chosen (strays). |

**Deprecated/outdated:** `pytest-cov`'s `COV_CORE_*`-style subprocess behaviour (removed in 7.0).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The ~2.5-core average of a serial `tests/regression` run is OpenCASCADE/VTK internal threading | Pitfall 9 | Knee of the sweep may differ from the guess; the sweep measures it regardless. |
| A2 | Summed per-process RSS overstates true memory because shared library pages are counted per process | Code Example 3 | The recorded "peak RSS" is an upper bound; the host-state header must say so. |
| A3 | The first full run's missing `pool.py` 63-67/222 came from worker data written after the combine or a lost xdist flush under load | Pitfall 13 | If it is a real nondeterminism in a different place, the floor's slack must be sized from more than three runs. The three tolerance runs measure it. |
| A4 | `sigterm = true` matters when a worker is terminated *mid-`build_export`* (not exercised by any current test) | Code Example 5 | If wrong it is a harmless extra signal handler in each worker. |
| A5 | xdist at `-n 4` behaves the same on CI's 4-vCPU/16 GB runner as on the M2 Max (memory 3.6 GiB summed RSS here) | Pitfall 9 | CI could OOM or flake; first proof is the CI run itself, so keep the `-n` literal reversible (Makefile var). |
| A6 | `ubuntu-latest` for this public repo is the 4 vCPU / 16 GB runner | Open Q 4 | D-02's "4-vCPU" context row would be wrong; `[CITED: docs.github.com runners table]` says public repos get 4 vCPU / 16 GB and the repo is `PUBLIC` (`gh repo view`), so the risk is low. |
| A7 | The SUS verdicts for `pytest-cov`/`pytest-xdist` are seam artefacts | Package Legitimacy Audit | If a human disagrees, the install is gated by the checkpoint anyway. |

## Open Questions

1. **D-09 and D-10 each contain a premise the research disproves (stop-and-ask trigger: evidence conflicts with a locked decision's text).**
   - What we know: D-09's intent (worker lines count) is achievable and verified; its mechanism ("pytest-cov's subprocess hook", `concurrency = ["multiprocessing"]` alone) is not. D-10's rule is sound but its unit arithmetic (~31 lines/pt) is 2.3x off and `fail_under` rounds at `precision`.
   - Recommendation: the planner implements Code Example 5 and records the corrections in the plan and in L34; D-09/D-10's *decisions* stand. Surface the two corrections to the human at the D-01 checkpoint rather than a separate halt.
2. **Literal REQ text "`--cov --cov-fail-under`".**
   - What we know: config-only satisfies the intent (verified gating) with one literal; the flag form would duplicate the number.
   - Recommendation: config-only, and amend REQ-coverage-floor's sentence alongside the other REQ amendments in the same PR (D-01/D-13 precedent).
3. **12 D-17 ("every number behind a committed script or make target") vs the awk per-file aggregation.**
   - What we know: the per-file table needs a two-line awk; the gate itself is `make test`. A committed `bench/` script would need tests under mypy strict.
   - Recommendation: record the exact command in the RESULTS section's method note (committed prose, reproducible), no new script. If the human wants a script, it is one small `bench/` file plus its test; decide at plan time.
4. **What `-n` does CI run?** D-06 leaves "the same N or `min(N, cpu)`" to the planner. CI is 4 vCPU/16 GB (A6). If the sweep's knee is <= 6, one literal serves both hosts; otherwise pass `PYTEST_WORKERS=4` in `ci.yml` (a change to the literal `make verify PYTHON=python` text that REQ-ci cites) or give the Makefile a `$(shell ...)` clamp. The scratch `-n 4` run on a 12-CPU host used ~3.6 GiB summed RSS.
5. **Seam verdict SUS on the two new `[dev]` packages.** Planner adds the `checkpoint:human-verify` line the protocol requires; the human has already named both packages.
6. **Observation outside scope (CLAUDE.md "evidence conflicts"):** AGENTS.md and L23 say `cadquery-ocp` "publishes wheels for nothing newer" than 3.12, yet PyPI lists `cp313` and `cp314` wheels for `cadquery-ocp 7.9.3.1.1` (macOS arm64/x86_64, manylinux_2_31 x86_64/aarch64, win) `[VERIFIED: pypi.org/pypi/cadquery-ocp/7.9.3.1.1/json file list]`. Not this phase's decision; mention to the human, do not act.
7. **Does the macOS arm64 result change D-14?** The arm64 dry-run under `-c requirements.txt` resolved all 83 packages, which is evidence toward the idea file's trigger but not the proof it names (install + `make verify`). Leave the idea filed; add one sentence to it only if the human wants the evidence recorded.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12 (`.venv`) | the gate | yes | 3.12.13 | - |
| GNU make | `make verify` | yes | 4.4.1 (`/opt/homebrew/opt/make/libexec/gnubin/make`) | - |
| git | no-fake-done, commits | yes | - | - |
| gh (authenticated) | run URL, `gh run view --log` | yes (listed CI runs) | - | - |
| pre-commit + installed hook | D-21 commits | yes | 4.6.2, `.git/hooks/pre-commit` present | - |
| `/usr/bin/time` (BSD) | `-p` wall, `-l` max RSS | yes | macOS | - |
| `pytest-xdist` in `.venv` | sweep, tolerance | **no** | - | installed by `$(STAMP)` after the `pyproject.toml` edit (needs network) |
| `pytest-cov` in `.venv` | baseline, floor | **no** | - | same |
| Network to PyPI | install; pip dry-run proof | yes | - | - |
| Docker | `make check` only; not needed for the gate | yes (`~/bin/docker`) | - | not required |
| Linux 4-vCPU runner | the CI proof, the CI `-n` question | only through a push | - | none: the run URL is the proof |
| Quiet host | the D-05 quiet bar | **no** - 10 users logged in, load 3-15 during research | - | D-04: alternate A/B, record load (this is why D-04 exists) |

**Missing dependencies with no fallback:** none blocking.
**Missing dependencies with fallback:** the two `[dev]` packages (installed by the first `make` after the edit).

**Research method disclosure:** all library experiments ran in a scratch venv outside the repo (`.../scratchpad/sv`, with a `.pth` onto the repo `.venv`'s site-packages, `PYTHONPATH=src`, `COVERAGE_FILE` in the scratchpad). `git status --short` stayed empty; `.venv` was not modified.

## Validation Architecture

Nyquist validation is enabled (`workflow.nyquist_validation = true`). This phase ships configuration and a measurement record rather than product behaviour, so most proofs are commands whose output is checked, not new pytest tests. CLAUDE.md's "new behaviour ships with its tests" is met by the existing suite plus the fixed proofs below; do not add a test that pins the `fail_under` literal (it would re-state the config and fail on every legitimate re-pin).

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 (installed); `pytest-xdist` 3.8.0 and `pytest-cov` 7.1.0 after the `[dev]` edit |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` (`addopts = "--strict-markers --strict-config"`, `filterwarnings = ["error", ...]`, untouched) and `[tool.coverage.*]` |
| Quick run command | `make test PYTEST_ARGS="tests/test_pr_land.py tests/test_bench.py -q --no-cov -n0"` |
| Full suite command | `make verify` (ends with `927 passed` unless a test count change is named) |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-verify-profiled | RESULTS section has the per-stage table, per-file table, top-N durations, sweep rows {2,4,8,12} with load and RSS, 3 tolerance rows, cost rows, host-state header | structural | `grep -nE '^(##|###) ' bench/RESULTS.md \| tail -20` plus `grep -c 'passed in' bench/RESULTS.md` against the expected row count; every full-run row says `927 passed` | RESULTS.md yes; section written by the phase |
| REQ-verify-profiled | xdist tolerance is *measured* | measurement | three consecutive `make verify` (or `make test`) runs at the chosen N, each `927 passed`, exit 0, zero reruns | n/a (recorded) |
| REQ-verify-at-the-bar | wall time reads at or under the bar, same method | measurement | `/usr/bin/time -p make verify` alternating A/B, `sysctl -n vm.loadavg` before each; assert `mean(B) <= bar` and test count unchanged | n/a (recorded) |
| REQ-verify-at-the-bar | no `[dev]`-external dependency; runtime closure untouched | unit/diff | `git diff --exit-code 20cd484 -- requirements.txt` | yes |
| REQ-verify-at-the-bar | hook comment corrected; no stray "~11 s" | grep | `git grep -n '~11' -- ':!bench/RESULTS.md' ':!docs/architecture/decision_log.md' ':!.planning/codebase'` returns only sites dealt with per D-19 | yes |
| REQ-coverage-floor | `pytest-cov` in `[dev]`; floor in config | grep | `grep -n 'pytest-cov\|fail_under\|precision' pyproject.toml` | yes |
| REQ-coverage-floor | worker lines counted | run | `make test PYTEST_ARGS="tests/test_pool.py --cov-report=term-missing:skip-covered -q"` shows `pool.py` absent from the skip-covered list or without 50, 63-67 | tests/test_pool.py yes |
| REQ-coverage-floor | the gate goes red below the floor | run | `make verify PYTEST_ARGS="--ignore=tests/test_cli.py"` exits non-zero with `Coverage failure` (recorded, nothing committed) | yes |
| REQ-coverage-floor | `.coverage*` ignored | grep | `git check-ignore .coverage .coverage.host.1.x` prints both | `.gitignore` edit needed |
| REQ-ci-installs-the-pinned-kernel | the pair is `cadquery==2.8.0` / `cadquery-ocp==7.9.3.1.1` on CI | CI log | `gh run view <id> --log \| grep -E 'cadquery 2.8.0 cadquery-ocp 7.9.3.1.1'` and `... \| grep -E 'passed'` | run exists only after the push |
| REQ-ci-installs-the-pinned-kernel | tripwire stays | unit | `.venv/bin/python -m pytest -n0 --no-cov tests/regression/test_pre_v0_2.py::test_the_fixture_was_captured_on_the_kernel_this_run_uses -q` | yes |
| REQ-ci-installs-the-pinned-kernel | ci.yml edit does not desync required jobs | unit | `.venv/bin/python -m pytest -n0 --no-cov tests/test_pr_land.py -q` (`test_required_jobs_file_matches_ci_yml_job_names`) | yes |
| REQ-ci-installs-the-pinned-kernel | local preflight resolves the pair | command | the `PIP_CONSTRAINT=... pip install --dry-run --report` command in Code Example 6 | n/a |
| SC5 / D-18 | both debt files retired | grep | `ls docs/tech_debt/resolved \| grep -E 'no-coverage-floor\|ci-resolves-the-kernel'`; `grep -c 'active/2026-09-21-no-coverage-floor\|active/2026-09-26-ci-resolves' docs/tech_debt/INDEX.md` equals 0 | yes |
| Whole phase | fixture and `src/` byte-unchanged (D-20) | diff | `git diff --exit-code 20cd484 -- tests/regression/pre_v0_2.json src` | yes |

### Sampling Rate
- **Per task commit:** the pre-commit hook runs `make verify` itself (plain `git commit`, D-21); run the quick command above while iterating.
- **Per wave merge:** `make verify`, state the command and the result line in the reply (CLAUDE.md).
- **Phase gate:** `make verify` green; the three D-05 runs; the CI run URL; the two `git diff --exit-code 20cd484` checks; `make pr.land PR=N`.

### Wave 0 Gaps
- [ ] `pyproject.toml` `[dev]` gains `pytest-xdist>=3.8`, `pytest-cov>=7.1`, then one `make` to install them (neither is in `.venv` today) - blocks the sweep, so it belongs in plan 1, with the profile.
- [ ] `.gitignore` gains `.coverage*` - before the first `--cov` run lands on a commit (otherwise the hook leaves untracked data files).
- [ ] No new test files or fixtures. Existing tests that already cover the touched seams: `tests/test_pr_land.py` (ci.yml parser), `tests/regression/test_pre_v0_2.py` (the tripwire), `tests/test_pool.py` (worker coverage proof).

### Measurement-validity checks (house method, D-04/D-10)
- every timing row carries the load read immediately before it and the machine line (`bench/__init__.py::machine_facts()`);
- A/B rows alternate in one session; the delta is `mean(B) - mean(A)`;
- profile `--durations` runs use `--no-cov -n0` so the ranking is not perturbed (measured here: `--cov` adds +2 % on `test_model.py` 158.7/157.6 s -> 161.6/160.9 s, +7 % on `tests/regression` 18.6 -> 20.0 s, +20 % on `test_cli.py` 11.8/12.0 -> 14.4 s, x2.5 on `test_calc.py` 0.26 -> 0.63 s, +45 % on `test_pool.py` 18.5 -> 26-27 s because worker kernel imports are now traced; a rank-neutral shift, but not zero);
- a red tolerance run is recorded as measured and never re-run to green.

## Security Domain

`workflow.security_enforcement` is absent from `.planning/config.json` (treated as enabled). This phase adds no endpoint, input or secret; the one security-relevant surface is the CI supply chain.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | - |
| V3 Session Management | no | - |
| V4 Access Control | no | - |
| V5 Input Validation | no | - |
| V6 Cryptography | no | - |
| V14 Configuration / dependencies (supply chain) | yes | exact-version constraints from the L12 closure for the runtime set in CI; package legitimacy gate for the two new `[dev]` packages; no new runtime dependency |

### Known Threat Patterns for a pip-in-CI stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Dependency substitution / typosquat on a new dev package | Tampering | The Package Legitimacy Audit above; both are pytest-dev org packages named by the human; install gated by a human-verify line. |
| Unpinned transitive upgrade changes the kernel under the fixture | Tampering | `PIP_CONSTRAINT=requirements.txt` (31 `==` pins); the tripwire test fails loudly if the pair ever differs. |
| Constraints file without hashes (a compromised wheel with the same version passes) | Tampering | Residual, accepted: the closure has "no hashes" (CONTEXT D-13), same as the image build today (L12). Not widened by this phase. |
| Coverage `.pth` auto-start executing in every interpreter | Elevation | Inert unless coverage env vars are set; `a1_coverage.pth` ships in the official `coverage` wheel. Config E does not rely on it. |

## Sources

### Primary (HIGH confidence)
- Local experiments, this host, 2026-10-03 (scratch venv `sv`): pytest 9.1.1, pytest-cov 7.1.0, pytest-xdist 3.8.0, coverage 7.16.2, pip 26.2.1, Python 3.12.13: coverage configs A-G on `tests/test_pool.py`; serial vs `-n 4` on a 169-test subset and on the full 927-test suite (x3); `--cov` A/B on four files; `--durations` output shape and awk; floor/precision/partial-run/`--no-cov` behaviour; `pip install --dry-run --report` with and without `PIP_CONSTRAINT`/`-c`, on macOS arm64 and a simulated linux/x86_64 cp312 target.
- Installed source read this session: `pytest_cov/plugin.py` (lines 262-275, 352-425), `coverage/results.py` (`should_fail_under` 484-503, `display_covered` 401-419), `xdist/workermanage.py` (execnet `popen` gateways).
- GitHub Actions run 37116412012 log (`gh run view --log`): install inside `make verify`, cache hit with install output present, `927 passed in 193.21s`, ruff 0.16.10 / mypy 2.4.0.
- Repo files read with `Read` this session: `pyproject.toml` (14-30, 96-135), `Makefile` (28-73), `.github/workflows/ci.yml` (8-29), `src/spur/pool.py` (33-68, 203-226), `tests/test_pr_land.py` (223-266 via sed), `.gitignore`, `bench/RESULTS.md` (2125-2198).
- [pytest-cov changelog](https://pytest-cov.readthedocs.io/en/latest/changelog.html) - 7.0.0 and 7.1.0 entries.
- [pytest-cov subprocess support](https://pytest-cov.readthedocs.io/en/latest/subprocess-support.html) - removal and `patch = ["subprocess"]` migration.
- [coverage.py configuration](https://coverage.readthedocs.io/en/latest/config.html) - `concurrency` (default "thread"), `patch`, `parallel`, `sigterm`, `fail_under`, `precision`.
- [coverage.py subprocess measurement](https://coverage.readthedocs.io/en/latest/subprocess.html) - `patch`, `sigterm`, multiprocessing with spawn ("all subprocesses terminate cleanly or they won't record their coverage").
- [GitHub-hosted runners](https://docs.github.com/en/actions/reference/runners/github-hosted-runners) - public repo ubuntu-latest: 4 vCPU / 16 GB.
- PyPI JSON: `https://pypi.org/pypi/cadquery-ocp/7.9.3.1.1/json`, `.../pytest-cov/json`, `.../pytest-xdist/json`; `https://pypistats.org/api/packages/pytest-cov/recent` and `.../pytest-xdist/recent`.

### Secondary (MEDIUM confidence)
- WebSearch for xdist + OpenCascade interactions returned only generic xdist segfault/fork threads and an unrelated OCP-in-server issue; nothing authoritative about OCCT specifically. Treated as no evidence; the claim "xdist tolerates the OCCT/`BuildPool` tests" rests on the scratch runs (three full 927-test runs at N=4), which D-05 requires the executor to repeat formally.

### Tertiary (LOW confidence)
- None used as a basis for a recommendation.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH on versions and roles (registry, installed, run); the seam's SUS verdicts are explained and gated.
- Architecture (coverage config, pin mechanism): HIGH - each claim reproduced locally; the Linux CI result is a simulation until the run URL exists.
- Pitfalls: HIGH for 1-8, 11, 14; MEDIUM for 9-10 and 13 (the mechanism is assumed; the observation is real).
- Timings: LOW as numbers (loaded host, single samples); useful only as shape (pytest ~all of the gate; `-n 4` roughly halves it).

**Research date:** 2026-10-03
**Valid until:** 2026-11-02 (pytest-cov, coverage and pip are all fast-moving; re-check pytest-cov's changelog if `[dev]` resolves a version past 7.1).
