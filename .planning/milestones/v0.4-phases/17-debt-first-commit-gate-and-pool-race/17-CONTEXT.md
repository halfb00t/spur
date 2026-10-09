# Phase 17: Debt First — Commit Gate and Pool Race - Context

**Gathered:** 2026-10-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Retire the two `must` debt items by a decision and a measurement, in a fixed order:

1. **The hook decision** — one new `Lxx` (expected L36) settles how the pre-commit
   `make verify` hook (63.555 s warm, L34) coexists with gsd's hard-coded 30 s SDK commit
   timeout (`COMMIT_TIMEOUT_MS` in gsd-core 1.16.0 `commands.cjs`; cite the symbol, the
   line drifts). Proved by one live `gsd_run query commit` on this repository returning
   `committed: true`. Every later commit of the milestone runs under it.
2. **The same-slot timeout race** — reproduced by the ten-identical-worst-row scenario in
   `bench/latency.py` (before the fix, the undocumented `500` visible), fixed in
   `src/spur/pool.py` by the two-fact guard plus a `_closed` flag, proved by a deterministic
   test seen red then green, re-run after the fix with zero `500`s.
3. **The margin decision** — its own `Lxx` (expected L37) for the composed worst row
   (29.42 s alone, `BuildTimeout` at 30 004 ms under ten concurrent builds), closing the
   race debt file together with the fix.

Not in this phase: any trochoid maths (Phase 18), any change to when the timeout clock
starts, to `SPUR_BUILD_TIMEOUT`'s meaning or to `MAX_QUEUED_BUILDS`, any patch to
`~/.claude/gsd-core`, any `--no-verify` policy (REQUIREMENTS.md "Out of Scope").

</domain>

<decisions>
## Implementation Decisions

### Hook arrangement (REQ-hook-and-commit-timeout-decided)
- **D-01:** **(b)+(c): a sub-30 s subset at `pre-commit`, the full `make verify` at
  `pre-push`.** CI, the `main` ruleset and `make pr.land` stay the wall (L22/L25). The
  `Lxx` amends L13 ("one definition of passing in three places" — the same `make verify`
  still runs in three places; the local hook *stage* moved and the commit stage runs a
  named prefix of it) and L34's closing sentence ("the commit-timeout debt stays active")
  by appending, never contradicting. Rejected: (a) alone — nothing shipped, cannot meet
  success criterion 1; (b) alone — no check at the commit boundary during the trochoid
  phases, where the L26 fixture replay matters most; (c) alone — the full gate unenforced
  locally until CI. — **Reversibility:** costly — undoing touches `.pre-commit-config.yaml`,
  the `Makefile`, six doc sites and needs a superseding `Lxx`.
- **D-02:** **The subset is the four static steps plus a pytest slice**: `lint typecheck
  lint-imports no-fake-done`, then pytest over every test file **except**
  `tests/test_model.py`, `tests/test_pool.py`, `tests/test_api.py`, `tests/test_cli.py`,
  at `-n 8 --no-cov`. Research priced it at 11.0–11.1 s for 617 tests (twice), ≈12 s warm
  all-in, ≈21 s with a cold mypy cache (9.1 s), host load 5–9 — ≥9 s of headroom under
  30 s. It keeps `tests/test_calc.py` (where Phase 18's maths lands) and
  `tests/regression` (the L26 fixture replay) at the commit boundary. `--no-cov` is
  mandatory: `fail_under = 96` reads a partial run as a failure. **Re-price at decision
  time** and record the number with its load figure, labelled by when it was taken, in the
  `Lxx` (PITFALLS 14; the 12-02/12-03 lesson). Rejected: static-only (0.59 s warm — no test
  at commit; a red fixture replay surfaces only at push); static + calc-only files (3.9 s,
  loses the fixture replay).
- **D-03:** **Makefile shape — a shared static target, and the slice as the same test
  recipe with narrower arguments, so nothing runs twice and the full gate's cost is
  unchanged.** Placeholder names (Claude's): `verify.static: lint typecheck lint-imports
  no-fake-done`; `verify: verify.static test`; `verify.fast: verify.static test.fast`;
  `test.fast` invokes the identical `$(PY) -m pytest -n $(PYTEST_WORKERS)` line with the
  `--ignore=` list and `--no-cov`. `make -n verify` shows the static prefix (success
  criterion 1); the pytest slice is the gate's own recipe narrowed, not a second list.
  Rejected: `verify: verify.fast test` literally (runs the 11 s slice twice; ~64 s → ~75 s,
  over L34's 66 s bar); a static-only prefix with the slice as a hook entry outside
  `verify`'s graph (two pytest lists — PITFALLS 14's drift).
- **D-04:** **`test.fast` selects by exclusion (`--ignore=tests/test_model.py` …), never by
  inclusion or marker.** Fail-safe direction: a new test file runs at commit until someone
  names it heavy. No pyproject edit, no decorated tests (`--strict-markers` is on and no
  marker is registered).
- **D-05:** **Hook config.** `default_install_hook_types: [pre-commit, commit-msg,
  pre-push]`; the existing `verify` hook keeps `entry: make verify` and moves to
  `stages: [pre-push]`; a new hook (id Claude's, e.g. `verify-fast`) runs `make verify.fast`
  at `stages: [pre-commit]`; `no-skip-token` is unchanged at `commit-msg`. Every hook stays
  pinned to one stage (the config already records the unpinned double-run). Pre-push
  semantics (once per push, from the first non-delete stdin line, nothing to push → no
  hook, unstaged changes stashed so the gate sees index + untracked files, `--no-verify`
  and `SKIP=` bypasses) are verified in a scratch repo **as a plan task** and the result
  recorded in the `Lxx` — SUMMARY disagreement 11 (STACK/PITFALLS say stashed, ARCHITECTURE
  says working tree) is settled by that check, not by citation.

### Install ownership and the killed-commit rule
- **D-06:** **The gate installs the hooks.** The `.venv` stamp recipe (`$(STAMP)` in the
  `Makefile`, which `make venv` and every gate target depend on) runs
  `$(VENV)/bin/pre-commit install` after `pip install -e '.[dev]'`, so a fresh clone gets
  all three hook types on its first `make venv` / `make verify`. The config header and
  `docs/HOW_TO_DEVELOP.md` §0 say "run `make venv` once". Caveat for the planner:
  `$(STAMP)` depends on `pyproject.toml` only, so an **existing** clone whose stamp is newer
  than `pyproject.toml` never re-runs it — the mechanism that makes a config change
  re-install on the next gate run (e.g. a hook stamp `$(VENV)/.hooks-installed:
  .pre-commit-config.yaml $(STAMP)` that `verify.static` depends on) is Claude's
  discretion, but the outcome is required: this clone (`.git/hooks` holds `pre-commit` and
  `commit-msg` only today) must end the phase with `pre-push` installed without a
  hand-typed command. In CI the install runs against the checkout and fires nothing;
  harmless (ASSUMPTION: `pre-commit install` succeeds in a GitHub Actions checkout — a
  plan task confirms it on the phase's first CI run). Rejected: documentation only (a
  forgotten clone pushes unverified until CI, silently); a gate step that refuses when
  `.git/hooks/pre-push` is missing (couples `make verify` to `.git` state).
- **D-07:** **On `{committed: false, reason: 'commit_timeout'}`: wait for the orphan, then
  exactly one plain `git commit`.** Measured (PITFALLS 15, git 2.54.0): the killed SDK
  commit leaves nothing committed, no `index.lock`, and the hook process running to
  completion as an orphan (parent PID 1). The rule: confirm no `pre-commit` / `pytest` /
  `mypy` process from the hook is alive (`pgrep`), wait for it, then commit by hand once
  with the hook allowed to finish, and record the hand commit in the plan's SUMMARY. Never
  retry the SDK commit blind — a retry overlaps the orphan (two gates sharing the stash)
  and is itself killed. This supersedes, for this repo, the executor's "remove the lock
  and retry once" recovery (`~/.claude/gsd-core/agents/gsd-executor.md`, the
  `commit_timeout` bullet), which assumed a warm retry passes. Lives in
  `docs/HOW_TO_DEVELOP.md` and the `Lxx`.
- **D-08:** **File the upstream request for a configurable `COMMIT_TIMEOUT_MS` on
  open-gsd/gsd-core, cite it, never depend on it.** One issue naming the symbol (not the
  line), the absence of a config key, and #3886 as prior art; the `Lxx` records the issue
  URL and date. The phase does not wait on it; `~/.claude/gsd-core` is not patched
  (outside the repo, overwritten by `gsd-update`).
- **D-09:** **Run `make verify` before every push, then push.** The explicit run warms the
  page cache and shows the result; the pre-push hook then runs warm (~64 s) inside the
  shell tool's 120 s default. `docs/HOW_TO_DEVELOP.md` §6 and the `gsd-ship` note carry
  the rule. Rejected: an explicit long tool timeout on every push (a five-minute silent
  hook on one tool call); no rule (occasional killed pushes and double gate runs).

### Margin (REQ-worst-row-margin-decided)
- **D-10:** **Record the limit as documented behaviour; no default moves.** The `Lxx`
  states: the heaviest allowed composed row (`bench/sweeps/composed.json` row 4 —
  `teeth=200 module=10 bore_d=9 keyway_width=3 keyway_depth=1.4 spoke_count=32
  spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both`)
  has 0.58 s of single-build margin on the reference host and does not finish inside
  `SPUR_BUILD_TIMEOUT` under concurrent load; `503 timeout` is the contract for it, and a
  bigger host raises the env var. `SPUR_BUILD_TIMEOUT` stays 30 s, `spoke_count`'s `le`
  stays 32. L05 (an unset parameter never changes the part) and L08 (no number tuned
  toward a pass) both hold; every shared link that builds today still builds. Rejected:
  raising the default (every deployment waits longer on a wedged worker; the 4× slower-
  hardware rationale would need restating; no proven margin on slower hosts either);
  lowering `spoke_count` a third time (a new concurrent sweep to pick the number, and
  links at 32 spokes start returning `422`).
- **D-11:** **The numbers that set it are SC3's recorded pair plus the identical-row run
  that comes free with the reproduction.** SC3 (`.planning/milestones/v0.3-phases/13-latency-bar/investigation/sc3.server1.records.jsonl`):
  29.42 s alone, `BuildTimeout` at `duration_ms` 30004 with both workers busy. The
  identical-row run adds the same row's wall time with one busy worker and three queued
  behind it, at the recorded load. No dedicated worst-row-under-N sweep.
- **D-12:** **The limit reaches users.** One sentence where `503` / `SPUR_BUILD_TIMEOUT`
  is documented (`README.md` lines 71 and 92–95 today): builds near the caps can exceed
  `SPUR_BUILD_TIMEOUT` under concurrent load and return `503 timeout`; raise the variable
  on a bigger host. Plus the required dated notes in `bench/RESULTS.md` and on the
  "~1.02x" headline at
  `docs/tech_debt/resolved/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md:63`.
- **D-13:** **The `Lxx` names its revisit trigger:** Phase 19's composed re-measure
  (REQ-trochoid-composes-and-is-priced measures the heaviest row against
  `SPUR_BUILD_TIMEOUT` anyway), or any change to `SPUR_BUILD_TIMEOUT`'s default or to an
  `le` cap.

### Reproduction protocol (REQ-same-slot-timeout-race-reproduced)
- **D-14:** **No quiet-host gate.** The `500` is a scheduling race; load widens the window.
  Host state and 1-min load are recorded as every `bench/RESULTS.md` section does, and the
  margin number from this run is labelled "at this load" beside SC3's. Rejected: Phase 13's
  D-05 gate (load < 1.5 × 3 samples, 900 s cap — reached in 2 of 5 sessions; a machine with
  a session active idles at ~2.0); a relaxed threshold picked for convenience.
- **D-15:** **Up to three attempts, each against a restarted server, every table recorded
  hit or miss.** Success criterion 3 says "run once"; one miss on a few-millisecond window
  is a weak negative, and three restarts bound the cost (~3 × ten 30 s builds). After three
  misses the record says "did not reproduce, measured" and D-17 applies.
- **D-16:** **The executor drives the run end to end**: the server started in the
  background with shipping defaults (2 workers, 4 queued builds, 30 s), the scenario run
  against it (`bench.latency` already refuses a non-fresh server via `held` /
  `_pool_state`), the server stopped, host state captured by the tool and the table
  committed into `bench/RESULTS.md`. Phase 13's SC3 ran this way. The human reads the
  committed table, not a paste.
- **D-17:** **If three runs show no `500` and the deterministic stale-executor test is red
  before the fix, the plan pauses at a checkpoint and the human chooses.** The checkpoint
  presents the three tables and the red test output; the options are "proceed on the
  test's evidence" (the `Lxx` and the debt resolution then say the bench was non-decisive
  and the in-process reproduction is the failure that was seen — L08 holds, PITFALLS 12)
  or "defer the fix". Nothing is written for the human; the phase does not proceed on its
  own, and does not hard-stop without asking.

### Carried forward from ROADMAP.md / REQUIREMENTS.md (locked, not re-discussed)
- Order inside the phase: hook decision → race reproduced → race fixed → margin decision
  (the human's "hook decision before any geometry commit"). Until the hook decision lands,
  every commit is a plain `git commit` with the hook allowed to finish.
- The fix is exactly: `_run_with_timeout`'s `except TimeoutError` branch terminates and
  replaces only when **both** `self.executor_for(p) is executor` **and**
  `executor._processes is not None`; `BuildPool.shutdown()` sets `_closed`, which
  `recreate_for` honours (the second route PITFALLS 9 measured). No `await` inside the
  terminate-and-replace block (no lock; atomicity rests on the one event-loop thread). A
  second same-slot timeout raises `BuildTimeout` → the documented `503 timeout`.
- Scenario: in `_SCENARIOS`, **not** in `DEFAULT_SCENARIOS` (D-16 of Phase 13); reads the
  composed worst row ten times; a `record_500` keyword so the default `_fetch` and
  `tests/test_bench.py`'s `HTTPStatusError` pin stay as they are; the registry assertion at
  `tests/test_bench.py:604` updated deliberately.
- Tests: one deterministic stale-executor test in `tests/test_pool.py` seen red before the
  fix and green after; one same-tick sibling test accepting `BuildTimeout` or
  `BrokenProcessPool` for the sibling; `test_four_same_slot_requests_all_refuse_without_cancellation`
  (the 0.5 s gap) unchanged; both new tests run repeatedly under `-n 8 --cov` and `-n 4`
  with the counts recorded. After the fix the scenario re-run shows zero `500`s (table
  appended).
- Debt retirements: the commit-timeout file retires in the hook commit with its sha; the
  race file retires only in the commit that closes **both** findings (race + margin) —
  `Status: resolved`, sha, `git mv` into `resolved/`, INDEX row moved, same commit.
- Editing `pool.py` fires the revisit triggers of two `nice` debts
  (`2026-10-04-worker-coverage-flush-is-sometimes-lost.md`,
  `2026-10-06-resource-tracker-flake-fails-the-gate.md`): the plan schedules a **read** of
  each and records the outcome; a fix is not required.
- Doc sites the hook `Lxx` must bring true in the same commit: `.pre-commit-config.yaml`
  header, `docs/HOW_TO_DEVELOP.md` §0 (and the §6 ship note), `README.md:288`,
  `docs/architecture/packaging.md:49-51`, the `.github/workflows/ci.yml` comment,
  `scripts/pr_land.py:67` (the stale "~42 s pre-commit hook" comment), L13 and L34.

### Claude's Discretion
- Target and hook ids (`verify.static` / `verify.fast` / `test.fast` / `verify-fast` are
  placeholders); the exact `--ignore` spelling; the hook-stamp mechanism in D-06.
- The scenario's name (e.g. `identical`) and whether `record_500` is also a CLI flag (the
  requirement needs only the keyword; code-only is the default reading).
- A drift test pinning the hook entry to the Makefile target and `verify`'s dependency on
  the static target (PITFALLS 14 recommends one; no test reads `.pre-commit-config.yaml`
  today) — recommended, not required.
- The orphan-worker check PITFALLS 11 suggests (worker count returns to N after a same-slot
  double timeout, read from `_processes` and exit codes, no psutil).
- The after-fix re-run: one clean run with zero `500`s satisfies criterion 4; repeat only if
  the run is itself non-decisive.
- `Lxx` numbering: two entries, hook first then margin, after L35.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and acceptance
- `.planning/ROADMAP.md` § "Phase 17: Debt First — Commit Gate and Pool Race" — goal, the
  five success criteria, boundaries, the fixed order.
- `.planning/REQUIREMENTS.md` § "Debt — the two `must` items (first)" and § "Out of
  Scope" — REQ-hook-and-commit-timeout-decided, REQ-same-slot-timeout-race-reproduced,
  REQ-same-slot-timeout-race-fixed, REQ-worst-row-margin-decided, with acceptance text.
- `.planning/PROJECT.md` — core value (L08), current state, the v0.4 brief.

### Research (priced options, measured windows, pitfalls)
- `.planning/research/SUMMARY.md` — corrections 6, 8–12 and 19; "Decisions the human must
  make" items 5–6 (now decided here).
- `.planning/research/STACK.md` § "(c) The hook decision: facts and pricing" — the subset
  pricing table (measured 2026-10-06, load 5–9), pre-commit 4.6.2 `pre-push` semantics
  read from installed source and a scratch repo, the recommendation.
- `.planning/research/ARCHITECTURE.md` § 2 (the race: identity check shape, the injected-
  timeout test, the ten-identical scenario's plumbing in `bench/latency.py`) and § 3 (the
  hook: option table, the doc sites that must change).
- `.planning/research/PITFALLS.md` Pitfalls 9–15 — the two routes to the `AttributeError`
  and the measured window table; flaky-test shapes on a 4-vCPU runner; orphaned workers;
  the timeout clock; pre-push guarantees; subset drift; the orphaned-hook measurement.

### The debt being retired
- `docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md` — the
  hook debt (its `:3655` line reference is stale; cite `COMMIT_TIMEOUT_MS`).
- `docs/tech_debt/active/2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md`
  — the race diagnosis (crash site is the *second* caller's branch, not `recreate_for`) and
  the margin finding; both must be closed before it retires.
- `docs/tech_debt/active/2026-10-04-worker-coverage-flush-is-sometimes-lost.md`,
  `docs/tech_debt/active/2026-10-06-resource-tracker-flake-fails-the-gate.md` — the two
  `nice` reads editing `pool.py` triggers.
- `docs/tech_debt/resolved/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md` —
  carries the "~1.02x" headline that gets the dated note (D-12).
- `docs/tech_debt/INDEX.md`, `docs/tech_debt/TEMPLATE.md` — the retirement mechanics.

### Decisions being amended
- `docs/architecture/decision_log.md` L13 (`make verify` is the gate, three places), L34
  (the gate measured and pinned; closing sentence on the commit-timeout debt), L22/L25
  (the ruleset and `pr.land` wall), L05, L08, L26 (fixture rule the subset protects), L17
  (per-worker memory, for the orphan-worker argument).

### Measurements already on record
- `bench/RESULTS.md` § "Composed worst row under ten concurrent builds (Phase 13)" (the
  SC3 table, the margin finding), § "`SPUR_BUILD_TIMEOUT`" (why 30 s), § "The gate,
  measured and pinned (Phase 15)" (63.555 s warm, per-file share), the Phase 12
  "### Gate probe" (`spoke_count` 32 at 29.41 s, 33 at 30.11 s).
- `.planning/milestones/v0.3-phases/13-latency-bar/investigation/sc3.server1.records.jsonl`,
  `sc3-run1.stderr.txt` — requests `912cd2d4` / `0fc30d53` (the `500`s), `51e80f35` /
  `4b777b09` (the clean timeouts).
- `.planning/milestones/v0.3-phases/13-latency-bar/13-CONTEXT.md` — D-05 (the quiet-host
  gate this phase declines), D-13..D-17, `<deferred>` (the ten-identical scenario).
- `.planning/RETROSPECTIVE.md` v0.3 "What Was Inefficient" — the 2-of-5 quiet-host record,
  the orphan-hook recovery.

### Process docs the hook commit edits
- `docs/HOW_TO_DEVELOP.md` §0 ("one definition of passed in three places"), §2 (the phase
  branch is cut before discuss-phase), §6 (ship and push).
- `docs/architecture/packaging.md:49-51`, `README.md:288` and `:71,:92-95`,
  `.github/workflows/ci.yml` comment near line 24–38, `scripts/pr_land.py:67`.
- `~/.claude/gsd-core/agents/gsd-executor.md` — the `commit_timeout` recovery bullet D-07
  supersedes for this repo (outside the repo; read, never edit).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `Makefile`: `verify: lint typecheck lint-imports no-fake-done test`; `test` is
  `$(PY) -m pytest -n $(PYTEST_WORKERS) --cov --cov-report=term $(PYTEST_ARGS)` (its own
  comment says pass `--no-cov` for a subset); `$(STAMP) := $(VENV)/.installed` depends on
  `pyproject.toml` and runs `pip install -e '.[dev]'`; `venv: $(STAMP)`; `bench.latency`
  needs `make serve` first. `PYTEST_WORKERS` already caps at 8.
- `.pre-commit-config.yaml`: two local hooks, each pinned to one stage (`verify` →
  `pre-commit`, `no-skip-token` → `commit-msg`); `default_install_hook_types:
  [pre-commit, commit-msg]`; the header documents the per-clone re-install pattern (D-02
  of Phase 5). This clone's `.git/hooks`: `pre-commit`, `commit-msg`.
- `src/spur/pool.py`: `_run_with_timeout` (line 157; the `except TimeoutError` branch at
  183–210, `executor._processes.values()` at 204, `recreate_for(p, executor, "timeout")`
  at 206); `recreate_for` (99–155, its own identity guard works as designed);
  `shutdown()` at 224–226 (`shutdown(wait=False)` on every executor, no replacement — the
  second route); `executor_for(p)` is `hash(p) % workers`. No lock anywhere.
- `src/spur/app.py`: `BuildTimeout` → `503` `type: "timeout"` (435–445);
  `BrokenProcessPool` → `503` `type: "pool_broken"` (447–464); `SPUR_BUILD_TIMEOUT` read
  at 146; `MAX_QUEUED_BUILDS` at 98–102. No handler for `AttributeError` (hence the raw
  `500`).
- `bench/latency.py`: `_SCENARIOS` (321) and `DEFAULT_SCENARIOS = ("concurrent",
  "single")` (332; `main()` reads it, never `sorted(_SCENARIOS)`); `run_composed(base_url)`
  reads `_composed_rows()` itself (give it `rows` + a label); `_fetch` calls
  `raise_for_status()` (a `500` raises today); `_pool_state` / `held` enforce a fresh
  server; `_report_markdown` suppresses the baseline line only for `name == "composed"`.
- `tests/test_pool.py`: `test_four_same_slot_requests_all_refuse_without_cancellation`
  (400, the 0.5 s gap — unchanged),
  `test_two_same_slot_deaths_from_one_incident_replace_the_worker_once` (492),
  `test_a_wedged_build_is_terminated_and_its_worker_replaced` (139 — the
  terminate→recreate mechanics under test, with `_sleep_past_timeout`),
  `test_executor_processes_attribute_still_exists` (112 — the `_processes` tripwire),
  `test_each_build_failure_mode_maps_to_its_own_status_and_type` (237).
- `tests/test_bench.py`: the registry assertion at 604 (`set(_SCENARIOS) == {...}`); the
  `HTTPStatusError` pin at 634; `test_the_composed_latency_scenario_fires_the_worst_composed_row_first_then_the_next_nine_heaviest`
  (573) documents the row order SC3 used.
- `bench/sweeps/composed.json`: 18 rows; row 4 (1-based) is the worst composed row.

### Established Patterns
- Measurement before knobs: every runtime bound cites the run that set it
  (`params.py:105-118` for `spoke_count`'s two lowerings; `README.md:71` and
  `bench/RESULTS.md` § "`SPUR_BUILD_TIMEOUT`" for 30 s). The margin `Lxx` follows it.
- `bench/RESULTS.md` sections carry a "### Host state" block (machine, Python, kernel,
  HEAD, sweep file, date/time, load). The identical-row tables do too.
- Bench is not gate (Phase 13 D-16): a scenario that times out and replaces a worker never
  enters the no-argument run.
- Debt retirement in the fixing commit: `Status: resolved`, `Resolved in: <sha>`, `git mv`,
  INDEX row moved — one commit (CLAUDE.md; PITFALLS 24).
- Decision entries append-amend (L34 amends L12/L13; L33 amends L09/L10/L30): the new
  entries name what they amend and quote the measured number that set them.
- Comments carry the measurement or constraint that forced the choice (CLAUDE.md "Code
  style"); the `.pre-commit-config.yaml` header and `Makefile` comments are the model.

### Integration Points
- The hook commit: `.pre-commit-config.yaml`, `Makefile`, `docs/architecture/decision_log.md`
  (new `Lxx`), the six doc sites, `docs/tech_debt/active/2026-09-25-…` → `resolved/`,
  `docs/tech_debt/INDEX.md`; proof = one `gsd_run query commit` returning
  `committed: true` with the commit in `git log`.
- The scenario commit: `bench/latency.py`, `tests/test_bench.py`, `bench/RESULTS.md` (the
  before table(s)).
- The fix commit: `src/spur/pool.py`, `tests/test_pool.py`; `bench/RESULTS.md` (the after
  table).
- The margin commit: `docs/architecture/decision_log.md` (second `Lxx`), `README.md`,
  `bench/RESULTS.md` (dated note), the resolved tip-chamfer debt file (dated note),
  `docs/tech_debt/active/2026-10-02-…` → `resolved/`, `docs/tech_debt/INDEX.md`.
- Branch: `gsd/phase-17-debt-first-commit-gate-and-pool-race`, cut from `origin/main` at
  discuss time (HOW_TO_DEVELOP §2); lands through a PR via `make pr.land`.

</code_context>

<specifics>
## Specific Ideas

- The subset's headroom is the argument: "≥9 s under 30 s even on a loaded host" (STACK)
  is to be re-measured and quoted with its load in the `Lxx`, not copied.
- The hook `Lxx` states which commits can now be red (local and phase-branch commits that
  fail only the heavy tiers), that `git bisect` can land on one, and that `main` cannot
  receive one (L22).
- The orphaned-hook fact is the reason for D-07 and D-09 and belongs in the `Lxx` with its
  measurement (git 2.54.0, Node `spawnSync`, parent PID 1).
- The margin `Lxx` quotes the row's full parameter line and both numbers (29.42 s alone,
  30 004 ms under SC3), plus the identical-row figure with its load.
- The no-repro checkpoint is a real pause: tables and the red test output in front of the
  human, two named options, no default.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope. Candidates not discussed (after-fix re-run
count, `record_500` as a CLI flag, the orphan-worker PID test, a hook-drift test, what the
two `nice` reads must produce) are listed under Claude's Discretion, not deferred.

</deferred>

---

*Phase: 17-debt-first-commit-gate-and-pool-race*
*Context gathered: 2026-10-06*
