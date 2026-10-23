# Phase 26: Gate Fails With a Cause - Context

**Gathered:** 2026-10-15
**Status:** Ready for planning

<domain>
## Phase Boundary

`make verify` and `main` CI stop failing for reasons that are not the product, and the
failures and stalls that remain leave their cause in the log. Six items, in the roadmap's
fixed order: (1) the hook pin ignores the caller's `PYTEST_ARGS`; (2) Ubuntu 26 is
pre-classified on a throwaway PR; (3) the "twin selectors" race is fixed and its mechanism
proved; (4) the `resource_tracker` flake is fixed from a reproduction (or re-deferred with the
measurement); (5) a stalled test leaves its id and a stack dump; (6) `make test-image` runs
what it claims.

Requirements: REQ-hook-pin-ignores-caller-args, REQ-ubuntu26-preclassified,
REQ-twin-selectors-race-fixed, REQ-tracker-flake-fixed-from-repro, REQ-hang-leaves-evidence,
REQ-test-image-runs-what-it-claims. Success criteria and boundaries: `.planning/ROADMAP.md`
§ "Phase 26: Gate Fails With a Cause" — not repeated here.

Locked before this discussion (roadmap / kickoff, not re-asked):
- Hang evidence is dump-only; `faulthandler_exit_on_timeout` waits for a first captured hang.
- Ubuntu 26 is pre-classified now on a throwaway PR; only the human may pin `ubuntu-24.04`.
- The hook-pin fix's shape (strip `PYTEST_ARGS` in `_make_env()` vs `PYTEST_ARGS=` on the
  dry-run command line) is the planner's call; both caller forms tested red first.
- No `src/spur/pool.py` change, no `filterwarnings` entry, no rerun plugin, no
  `shutdown(wait=True)`, no new dependency (`pytest-timeout` out).

</domain>

<decisions>
## Implementation Decisions

### Flake fix and proof runs
- **D-01:** The flake fix is **arms B and C together**, in `tests/test_pool.py` only: a
  module-level autouse fixture whose teardown calls `gc.collect()` (B — the guard that covers
  any future test with the same `manager` / `pytest.raises` pattern) **and** `del manager`
  after last use in the three producer tests STACK identified (C — removes the cycle at its
  source). One fix commit; the debt item
  `docs/tech_debt/active/2026-10-06-resource-tracker-flake-fails-the-gate.md` is retired in
  that commit, quoting the forced-GC table. The success line reads "located and fixed from a
  reproduction", never "gone".
- **D-02:** The forced-GC-in-lock reproduction (patch `ResourceTracker._check_alive` to call
  `gc.collect()` first, so cyclic garbage holding a semaphore is finalised re-entrantly) is
  **committed as a gate test**, not left in a scratchpad. It must be seen red against the
  unfixed file (STACK: arm A fails 3 of 3) and green after B + C; the red is recorded in the
  commit or plan summary. Its gate cost is measured and recorded. Shape (subprocess pytest
  run vs in-process patch) is the planner's call, provided the patch cannot leak into other
  tests on the same xdist worker.
- **D-03:** STACK's reproduction is **re-run on this host first** (READ-from-STACK until then).
  If it does not reproduce here, the fix does not land: the item is re-deferred with the
  measurement that failed to reproduce it (SC3, L08).
- **D-04:** The natural-rate acceptance run is **10 before + 10 after, interleaved**
  (A1 B1 … A10 B10), `tests/test_pool.py` + `tests/test_api.py` at `-n 8 --cov`. Cap, arms and
  stop rule committed before the run starts. Effective `-n`, tool versions, host load and
  signature-classified reds recorded in `bench/RESULTS.md` (appended, never rewritten). Read
  as "consistent, not conclusive" — 0 of 10 by luck is 15–30 %; the forced-GC test is the
  proof.
- **D-05:** Twin-selectors repeat proof: **20 local runs** of `tests/test_browser.py` at
  `-n 8`, count recorded, **plus the post-merge `main` CI run read green** (main is where it
  failed, 2 of the last 8 runs). This is in addition to the delayed-STL-route red (old step) →
  green (new step) proof SC2 already requires.

### Hang evidence
- **D-06:** `-v --durations=<N>` goes on the **`test` recipe, so every `make verify`** (local
  and CI) prints test ids on start and finish. The one recorded hang was local, under the
  harness; evidence helps only if it is on when the hang happens. Not on `test.fast`.
  `tests/test_hooks.py`'s shared-recipe pin compares the pytest lines only through `-n <N>`
  (research C2), so a flag after the worker count stays inside it — verify, don't assume.
- **D-07:** `faulthandler_timeout = 120` in `pyproject.toml` `[tool.pytest.ini_options]`,
  **set now from a recorded local `--durations` reading, then confirmed on the phase's first
  CI run**: read CI's `--durations`, record it, and change the value only if CI's slowest test
  × 2 exceeds 120 s. The plan names the confirm step as a task, not a hope.
- **D-08:** The deliberately stalled test is a **throwaway**: a temporary test file run once at
  `-n 8 --cov` with a short timeout override, its whole log kept under the phase's
  `investigation/` directory and quoted in `bench/RESULTS.md`. Nothing that sleeps is
  committed.
- **D-09:** Gate cost of the added flags: **3 + 3 `make test` runs interleaved** (A B A B A B),
  1-minute load logged per run, no idle wait. Recorded against L43's 300 s bar. If the
  before/after delta exceeds 5 %, stop and ask before escalating to Phase 25's quiet-host
  protocol.
- **D-10:** The hang item stays `active` with a runbook stating what the evidence cannot see
  (a stall after the last test, outside `faulthandler_timeout`'s per-item window) and the
  operator step for that window. No cause is claimed.

### `make test-image`
- **D-11:** **Rule pre-committed, checkpoint on surprise.** Run `make test-image` once first and
  record its whole red set (the research's two `tests/test_bench.py` exit-128 tests are a
  guess, not the reading). The fix: mount `bench/` and `scripts/` read-only, set
  `PYTHONPATH=/app/src:/app`, and `--ignore` only files that need `make`, git, the Dockerfile
  or `.github`. The executor proceeds if every recorded red fits that rule; if any red has
  another cause, it stops and asks. Excluding `tests/test_calc.py` / `tests/test_trochoid.py`
  by name is rejected (guts the image suite's maths coverage).
- **D-12:** A host-only file's reason is carried by **`--ignore` in the recipe plus a recipe
  comment** naming why, matching the existing `--ignore=tests/test_browser.py` pattern. No
  `skipif` added to test files.
- **D-13:** Guard after the fix: **extend `tests/test_hooks.py`'s existing `test-image` pin**
  (`test_the_image_suite_ignores_the_browser_test`) to the new mounts, `PYTHONPATH` and
  `--ignore` list. Tightened, never deleted. Running `test-image` in CI is out of scope
  (deferred).

### Ubuntu 26 throwaway PR
- **D-14:** Branch **from `main` at the `v0.5` tag** (`26ddd74`), e.g. `spike/26-ubuntu-26`,
  one commit changing only the three `runs-on` lines in `.github/workflows/ci.yml` to
  `ubuntu-26.04`. It reads the shipped tree on the new image — what the rollout will run. A
  twin-selectors red there is classified as the known main-only red, not an Ubuntu 26 cause.
- **D-15:** **Executor prepares, the human pushes.** The executor creates the branch and commit
  locally and stops at a checkpoint with the exact `git push` and `gh pr create --draft` lines.
  The human runs them; the executor resumes, pulls each job's whole log with
  `gh run view --log`, and classifies `test (3.12)`, `vendor-bundle` and `image` in
  `bench/RESULTS.md` (`Image:` line from `Set up job`, per-job result) before any `ci.yml` edit
  lands. PR closed unmerged; the branch is the human's to delete (`spike/21-linux-runner`
  precedent). A red job is not fixed: options go to the human.
- **D-16:** **If the clock is missed** (jobs not finished, or the 26.04 queue stalls, before the
  rollout reaches the repo): classify whatever ran with its timestamp against the first
  migrated `main` run, mark SC5 "not met as written" with the reason, and continue the phase.
  Phase 29 still reads the migrated run. No pin without the human.

### Claude's Discretion
- The hook-pin fix's shape (roadmap: planner's call; both caller forms tested red first).
- Exactly how the twin-selectors step waits for the link's own STL request and the 350 ms
  debounce before taking its baseline; folding 24 CX-05 and 21 IN-04a (`_follow_link` on
  `BUILD_WAIT_MS`) into the same change.
- `--durations` count (STACK suggests 25).
- Whether the forced-GC gate test lives in `tests/test_pool.py` or beside it, provided D-02
  holds.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and rules
- `.planning/ROADMAP.md` § "Phase 26: Gate Fails With a Cause" — goal, fixed item order, SC1–SC5, boundaries, phase-close checks
- `.planning/REQUIREMENTS.md` — the six Phase 26 REQs and "Rules every requirement lives by"
- `.planning/PROJECT.md` § "Current Milestone: v0.6 Clean Ledger"
- `docs/architecture/decision_log.md` — L08, L13, L23, L34, L36, L43 (gate definition, bar, Python pin)
- `CLAUDE.md` — debt filing/retiring rules, `make verify` as the gate

### Research (v0.6)
- `.planning/research/SUMMARY.md` — "Conflicts Between the Four Files" table (C1, C2, C9, C10 govern this phase) and "Open Human Decisions"
- `.planning/research/STACK.md` §1 (flake: forced-GC reproduction, arms A/B/C table), §2 (hang: `faulthandler_timeout`, `-v --durations`, why 120 s, the post-last-test blind spot), Ubuntu 26 section
- `.planning/research/ARCHITECTURE.md` — twin-selectors mechanism ASSUMPTION; hook-pin `-n <N>` comparison; test-image mount recommendation
- `.planning/research/PITFALLS.md` — acceptance-run discipline (committed cap and arms, signature-classified reds)

### Debt items this phase acts on
- `docs/tech_debt/active/2026-10-10-hook-pin-reads-the-callers-pytest-args.md` (nice) — retire on fix
- `docs/tech_debt/active/2026-10-15-twin-selectors-step-reds-main.md` (must) — retire on fix
- `docs/tech_debt/active/2026-10-06-resource-tracker-flake-fails-the-gate.md` (must) — retire on fix, or re-defer with measurement
- `docs/tech_debt/active/2026-10-10-make-verify-hung-at-98-percent-with-no-failure.md` (must) — stays active, gains runbook
- `docs/tech_debt/active/2026-10-10-test-image-collects-tests-that-read-host-files.md` (nice) — retire on fix
- `docs/tech_debt/active/2026-10-10-ubuntu-latest-migrates-to-ubuntu-26-on-19-october.md` (must) — stays active for Phase 29

### Records
- `bench/RESULTS.md` — append-only; the 21-08 "Linux path on the real runner" section and the `spike/21-linux-runner` record are the format precedent for D-15
- `.planning/milestones/v0.5-phases/24-bore-shape-selector/` — review finding CX-05
- `.planning/milestones/v0.5-phases/21-browser-test-of-the-viewer/` — review finding IN-04a; `investigation/` logs (hang, 21-07 hook-pin red)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tests/test_hooks.py::_make_env` (line 34) and `_dry_run` (line 58): the dry-run harness both hook-pin forms go through.
- `tests/test_hooks.py::test_the_image_suite_ignores_the_browser_test` (line 181): the existing `test-image` pin D-13 extends.
- `tests/test_browser.py`: `BUILD_WAIT_MS` (imported at line 39), `_follow_link` (line 204), existing `wait_for_request(... timeout=BUILD_WAIT_MS)` patterns (lines 272, 386, 410) for the twin-selectors wait.

### Established Patterns
- `Makefile` `test` (line 176–177): `pytest -n $(PYTEST_WORKERS) --cov --cov-report=term $(PYTEST_ARGS)`; `PYTEST_ARGS ?=` at line 6 and comes last.
- `Makefile` `test-image` (line 219): mounts `src/`, `tests/`, `pyproject.toml` only; `PYTHONPATH=/app/src`; `--ignore=tests/test_browser.py` with a comment giving the reason (D-12's pattern).
- `pyproject.toml` `[tool.pytest.ini_options]`: `--strict-config` (an unknown ini key fails), `filterwarnings = ["error", ...]` (why the flake fails the gate).
- `tests/test_pool.py`: 18 tests; manager-thread handling around lines 159–194.
- `.github/workflows/ci.yml`: three jobs on `ubuntu-latest` (lines 13, 61, 77); runs on every `pull_request`; required-job list in `.github/workflows/required-jobs.txt`.

### Integration Points
- `Makefile` `test` recipe (D-06), `pyproject.toml` ini (D-07), `Makefile` `test-image` recipe (D-11), `tests/test_pool.py` (D-01, D-02), `tests/test_browser.py` twin-selectors step (~line 1576/1611), `tests/test_hooks.py` (hook pin, test-image pin), `bench/RESULTS.md` (every measurement).

</code_context>

<specifics>
## Specific Ideas

- Branch name for the throwaway PR: `spike/26-ubuntu-26` (precedent `spike/21-linux-runner`).
- Every measurement above lands in `bench/RESULTS.md` with its command, host, load and tool versions; readings never rewritten.

</specifics>

<deferred>
## Deferred Ideas

- Run `make test-image` in CI (a new CI job) so the image suite cannot rot red again — a new capability; candidate for `docs/ideas/`.
- `faulthandler_exit_on_timeout` (REQ-hang-fails-named) — after the first captured hang (already in REQUIREMENTS "Future Requirements").

</deferred>

---

*Phase: 26-gate-fails-with-a-cause*
*Context gathered: 2026-10-15*
