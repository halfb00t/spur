# Phase 17: Debt First — Commit Gate and Pool Race - Research

**Researched:** 2026-10-06
**Domain:** developer-workflow tooling (git hooks, GNU make, pre-commit) and one asyncio / `concurrent.futures` race in `src/spur/pool.py`; no geometry, no new dependency
**Confidence:** HIGH (every load-bearing claim below was either read in the live tree this session or reproduced in a scratch copy; the few `[ASSUMED]` items are listed in the Assumptions Log)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Hook arrangement (REQ-hook-and-commit-timeout-decided)**
- **D-01:** **(b)+(c): a sub-30 s subset at `pre-commit`, the full `make verify` at `pre-push`.** CI, the `main` ruleset and `make pr.land` stay the wall (L22/L25). The `Lxx` amends L13 ("one definition of passing in three places" — the same `make verify` still runs in three places; the local hook *stage* moved and the commit stage runs a named prefix of it) and L34's closing sentence ("the commit-timeout debt stays active") by appending, never contradicting. Rejected: (a) alone — nothing shipped, cannot meet success criterion 1; (b) alone — no check at the commit boundary during the trochoid phases, where the L26 fixture replay matters most; (c) alone — the full gate unenforced locally until CI. — **Reversibility:** costly — undoing touches `.pre-commit-config.yaml`, the `Makefile`, six doc sites and needs a superseding `Lxx`.
- **D-02:** **The subset is the four static steps plus a pytest slice**: `lint typecheck lint-imports no-fake-done`, then pytest over every test file **except** `tests/test_model.py`, `tests/test_pool.py`, `tests/test_api.py`, `tests/test_cli.py`, at `-n 8 --no-cov`. Research priced it at 11.0–11.1 s for 617 tests (twice), ≈12 s warm all-in, ≈21 s with a cold mypy cache (9.1 s), host load 5–9 — ≥9 s of headroom under 30 s. It keeps `tests/test_calc.py` (where Phase 18's maths lands) and `tests/regression` (the L26 fixture replay) at the commit boundary. `--no-cov` is mandatory: `fail_under = 96` reads a partial run as a failure. **Re-price at decision time** and record the number with its load figure, labelled by when it was taken, in the `Lxx` (PITFALLS 14; the 12-02/12-03 lesson). Rejected: static-only (0.59 s warm — no test at commit; a red fixture replay surfaces only at push); static + calc-only files (3.9 s, loses the fixture replay).
- **D-03:** **Makefile shape — a shared static target, and the slice as the same test recipe with narrower arguments, so nothing runs twice and the full gate's cost is unchanged.** Placeholder names (Claude's): `verify.static: lint typecheck lint-imports no-fake-done`; `verify: verify.static test`; `verify.fast: verify.static test.fast`; `test.fast` invokes the identical `$(PY) -m pytest -n $(PYTEST_WORKERS)` line with the `--ignore=` list and `--no-cov`. `make -n verify` shows the static prefix (success criterion 1); the pytest slice is the gate's own recipe narrowed, not a second list. Rejected: `verify: verify.fast test` literally (runs the 11 s slice twice; ~64 s → ~75 s, over L34's 66 s bar); a static-only prefix with the slice as a hook entry outside `verify`'s graph (two pytest lists — PITFALLS 14's drift).
- **D-04:** **`test.fast` selects by exclusion (`--ignore=tests/test_model.py` …), never by inclusion or marker.** Fail-safe direction: a new test file runs at commit until someone names it heavy. No pyproject edit, no decorated tests (`--strict-markers` is on and no marker is registered).
- **D-05:** **Hook config.** `default_install_hook_types: [pre-commit, commit-msg, pre-push]`; the existing `verify` hook keeps `entry: make verify` and moves to `stages: [pre-push]`; a new hook (id Claude's, e.g. `verify-fast`) runs `make verify.fast` at `stages: [pre-commit]`; `no-skip-token` is unchanged at `commit-msg`. Every hook stays pinned to one stage (the config already records the unpinned double-run). Pre-push semantics (once per push, from the first non-delete stdin line, nothing to push → no hook, unstaged changes stashed so the gate sees index + untracked files, `--no-verify` and `SKIP=` bypasses) are verified in a scratch repo **as a plan task** and the result recorded in the `Lxx` — SUMMARY disagreement 11 (STACK/PITFALLS say stashed, ARCHITECTURE says working tree) is settled by that check, not by citation.

**Install ownership and the killed-commit rule**
- **D-06:** **The gate installs the hooks.** The `.venv` stamp recipe (`$(STAMP)` in the `Makefile`, which `make venv` and every gate target depend on) runs `$(VENV)/bin/pre-commit install` after `pip install -e '.[dev]'`, so a fresh clone gets all three hook types on its first `make venv` / `make verify`. The config header and `docs/HOW_TO_DEVELOP.md` §0 say "run `make venv` once". Caveat for the planner: `$(STAMP)` depends on `pyproject.toml` only, so an **existing** clone whose stamp is newer than `pyproject.toml` never re-runs it — the mechanism that makes a config change re-install on the next gate run (e.g. a hook stamp `$(VENV)/.hooks-installed: .pre-commit-config.yaml $(STAMP)` that `verify.static` depends on) is Claude's discretion, but the outcome is required: this clone (`.git/hooks` holds `pre-commit` and `commit-msg` only today) must end the phase with `pre-push` installed without a hand-typed command. In CI the install runs against the checkout and fires nothing; harmless (ASSUMPTION: `pre-commit install` succeeds in a GitHub Actions checkout — a plan task confirms it on the phase's first CI run). Rejected: documentation only (a forgotten clone pushes unverified until CI, silently); a gate step that refuses when `.git/hooks/pre-push` is missing (couples `make verify` to `.git` state).
- **D-07:** **On `{committed: false, reason: 'commit_timeout'}`: wait for the orphan, then exactly one plain `git commit`.** Measured (PITFALLS 15, git 2.54.0): the killed SDK commit leaves nothing committed, no `index.lock`, and the hook process running to completion as an orphan (parent PID 1). The rule: confirm no `pre-commit` / `pytest` / `mypy` process from the hook is alive (`pgrep`), wait for it, then commit by hand once with the hook allowed to finish, and record the hand commit in the plan's SUMMARY. Never retry the SDK commit blind — a retry overlaps the orphan (two gates sharing the stash) and is itself killed. This supersedes, for this repo, the executor's "remove the lock and retry once" recovery (`~/.claude/gsd-core/agents/gsd-executor.md`, the `commit_timeout` bullet), which assumed a warm retry passes. Lives in `docs/HOW_TO_DEVELOP.md` and the `Lxx`.
- **D-08:** **File the upstream request for a configurable `COMMIT_TIMEOUT_MS` on open-gsd/gsd-core, cite it, never depend on it.** One issue naming the symbol (not the line), the absence of a config key, and #3886 as prior art; the `Lxx` records the issue URL and date. The phase does not wait on it; `~/.claude/gsd-core` is not patched (outside the repo, overwritten by `gsd-update`).
- **D-09:** **Run `make verify` before every push, then push.** The explicit run warms the page cache and shows the result; the pre-push hook then runs warm (~64 s) inside the shell tool's 120 s default. `docs/HOW_TO_DEVELOP.md` §6 and the `gsd-ship` note carry the rule. Rejected: an explicit long tool timeout on every push (a five-minute silent hook on one tool call); no rule (occasional killed pushes and double gate runs).

**Margin (REQ-worst-row-margin-decided)**
- **D-10:** **Record the limit as documented behaviour; no default moves.** The `Lxx` states: the heaviest allowed composed row (`bench/sweeps/composed.json` row 4 — `teeth=200 module=10 bore_d=9 keyway_width=3 keyway_depth=1.4 spoke_count=32 spoke_width=0.4 hub_d=52 rim_wall=0.4 spoke_fillet=5 tip_chamfer=3 recess_sides=both`) has 0.58 s of single-build margin on the reference host and does not finish inside `SPUR_BUILD_TIMEOUT` under concurrent load; `503 timeout` is the contract for it, and a bigger host raises the env var. `SPUR_BUILD_TIMEOUT` stays 30 s, `spoke_count`'s `le` stays 32. L05 (an unset parameter never changes the part) and L08 (no number tuned toward a pass) both hold; every shared link that builds today still builds. Rejected: raising the default (every deployment waits longer on a wedged worker; the 4× slower-hardware rationale would need restating; no proven margin on slower hosts either); lowering `spoke_count` a third time (a new concurrent sweep to pick the number, and links at 32 spokes start returning `422`).
- **D-11:** **The numbers that set it are SC3's recorded pair plus the identical-row run that comes free with the reproduction.** SC3 (`.planning/milestones/v0.3-phases/13-latency-bar/investigation/sc3.server1.records.jsonl`): 29.42 s alone, `BuildTimeout` at `duration_ms` 30004 with both workers busy. The identical-row run adds the same row's wall time with one busy worker and three queued behind it, at the recorded load. No dedicated worst-row-under-N sweep.
- **D-12:** **The limit reaches users.** One sentence where `503` / `SPUR_BUILD_TIMEOUT` is documented (`README.md` lines 71 and 92–95 today): builds near the caps can exceed `SPUR_BUILD_TIMEOUT` under concurrent load and return `503 timeout`; raise the variable on a bigger host. Plus the required dated notes in `bench/RESULTS.md` and on the "~1.02x" headline at `docs/tech_debt/resolved/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md:63`.
- **D-13:** **The `Lxx` names its revisit trigger:** Phase 19's composed re-measure (REQ-trochoid-composes-and-is-priced measures the heaviest row against `SPUR_BUILD_TIMEOUT` anyway), or any change to `SPUR_BUILD_TIMEOUT`'s default or to an `le` cap.

**Reproduction protocol (REQ-same-slot-timeout-race-reproduced)**
- **D-14:** **No quiet-host gate.** The `500` is a scheduling race; load widens the window. Host state and 1-min load are recorded as every `bench/RESULTS.md` section does, and the margin number from this run is labelled "at this load" beside SC3's. Rejected: Phase 13's D-05 gate (load < 1.5 × 3 samples, 900 s cap — reached in 2 of 5 sessions; a machine with a session active idles at ~2.0); a relaxed threshold picked for convenience.
- **D-15:** **Up to three attempts, each against a restarted server, every table recorded hit or miss.** Success criterion 3 says "run once"; one miss on a few-millisecond window is a weak negative, and three restarts bound the cost (~3 × ten 30 s builds). After three misses the record says "did not reproduce, measured" and D-17 applies.
- **D-16:** **The executor drives the run end to end**: the server started in the background with shipping defaults (2 workers, 4 queued builds, 30 s), the scenario run against it (`bench.latency` already refuses a non-fresh server via `held` / `_pool_state`), the server stopped, host state captured by the tool and the table committed into `bench/RESULTS.md`. Phase 13's SC3 ran this way. The human reads the committed table, not a paste.
- **D-17:** **If three runs show no `500` and the deterministic stale-executor test is red before the fix, the plan pauses at a checkpoint and the human chooses.** The checkpoint presents the three tables and the red test output; the options are "proceed on the test's evidence" (the `Lxx` and the debt resolution then say the bench was non-decisive and the in-process reproduction is the failure that was seen — L08 holds, PITFALLS 12) or "defer the fix". Nothing is written for the human; the phase does not proceed on its own, and does not hard-stop without asking.

**Carried forward from ROADMAP.md / REQUIREMENTS.md (locked, not re-discussed)**
- Order inside the phase: hook decision → race reproduced → race fixed → margin decision (the human's "hook decision before any geometry commit"). Until the hook decision lands, every commit is a plain `git commit` with the hook allowed to finish.
- The fix is exactly: `_run_with_timeout`'s `except TimeoutError` branch terminates and replaces only when **both** `self.executor_for(p) is executor` **and** `executor._processes is not None`; `BuildPool.shutdown()` sets `_closed`, which `recreate_for` honours (the second route PITFALLS 9 measured). No `await` inside the terminate-and-replace block (no lock; atomicity rests on the one event-loop thread). A second same-slot timeout raises `BuildTimeout` → the documented `503 timeout`.
- Scenario: in `_SCENARIOS`, **not** in `DEFAULT_SCENARIOS` (D-16 of Phase 13); reads the composed worst row ten times; a `record_500` keyword so the default `_fetch` and `tests/test_bench.py`'s `HTTPStatusError` pin stay as they are; the registry assertion at `tests/test_bench.py:604` updated deliberately.
- Tests: one deterministic stale-executor test in `tests/test_pool.py` seen red before the fix and green after; one same-tick sibling test accepting `BuildTimeout` or `BrokenProcessPool` for the sibling; `test_four_same_slot_requests_all_refuse_without_cancellation` (the 0.5 s gap) unchanged; both new tests run repeatedly under `-n 8 --cov` and `-n 4` with the counts recorded. After the fix the scenario re-run shows zero `500`s (table appended).
- Debt retirements: the commit-timeout file retires in the hook commit with its sha; the race file retires only in the commit that closes **both** findings (race + margin) — `Status: resolved`, sha, `git mv` into `resolved/`, INDEX row moved, same commit.
- Editing `pool.py` fires the revisit triggers of two `nice` debts (`2026-10-04-worker-coverage-flush-is-sometimes-lost.md`, `2026-10-06-resource-tracker-flake-fails-the-gate.md`): the plan schedules a **read** of each and records the outcome; a fix is not required.
- Doc sites the hook `Lxx` must bring true in the same commit: `.pre-commit-config.yaml` header, `docs/HOW_TO_DEVELOP.md` §0 (and the §6 ship note), `README.md:288`, `docs/architecture/packaging.md:49-51`, the `.github/workflows/ci.yml` comment, `scripts/pr_land.py:67` (the stale "~42 s pre-commit hook" comment), L13 and L34.

### Claude's Discretion
- Target and hook ids (`verify.static` / `verify.fast` / `test.fast` / `verify-fast` are placeholders); the exact `--ignore` spelling; the hook-stamp mechanism in D-06.
- The scenario's name (e.g. `identical`) and whether `record_500` is also a CLI flag (the requirement needs only the keyword; code-only is the default reading).
- A drift test pinning the hook entry to the Makefile target and `verify`'s dependency on the static target (PITFALLS 14 recommends one; no test reads `.pre-commit-config.yaml` today) — recommended, not required.
- The orphan-worker check PITFALLS 11 suggests (worker count returns to N after a same-slot double timeout, read from `_processes` and exit codes, no psutil).
- The after-fix re-run: one clean run with zero `500`s satisfies criterion 4; repeat only if the run is itself non-decisive.
- `Lxx` numbering: two entries, hook first then margin, after L35.

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope. Candidates not discussed (after-fix re-run count, `record_500` as a CLI flag, the orphan-worker PID test, a hook-drift test, what the two `nice` reads must produce) are listed under Claude's Discretion, not deferred.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-hook-and-commit-timeout-decided | One logged `Lxx` settles how the pre-commit gate coexists with gsd's 30 s `COMMIT_TIMEOUT_MS`; live `gsd_run query commit` returns `committed: true`; pre-push semantics verified in a scratch repo; six doc sites corrected; commit-timeout debt retired | Subset re-priced today (12.2 s slice + 0.37 s static warm, 8.68 s cold mypy); pre-push semantics measured in a scratch repo today (disagreement 11 settled: stashed); in-hook `pre-commit install` verified safe; `COMMIT_TIMEOUT_MS` re-read at `commands.cjs:3794`; no open upstream issue found; every doc site read |
| REQ-same-slot-timeout-race-reproduced | Ten-identical-worst-row scenario in `_SCENARIOS` (not default), `record_500` keyword, registry assertion updated; run once pre-fix with the `500` visible in `bench/RESULTS.md` | `bench/latency.py` `run_composed` / `_fetch` / registry read; plumbing plan; reproduction-probability analysis (gap ≤ ~20 ms) so a miss is expected as a possible outcome, with the D-15/D-17 path |
| REQ-same-slot-timeout-race-fixed | Two-fact guard + `_closed`; deterministic stale-executor test red→green; same-tick sibling test; 0.5 s-gap test unchanged; repeated runs under `-n 8 --cov` and `-n 4`; scenario re-run zero `500`s | Fix applied to a scratch copy and the three shapes run pre and post (stale: `AttributeError` → `BuildTimeout`; same-tick: `[BuildTimeout, AttributeError, AttributeError]` → three `BuildTimeout`; closed: slot replaced → unchanged); mypy accepts the guard with no suppression |
| REQ-worst-row-margin-decided | An `Lxx` for the composed worst row naming the number that set it; dated notes in `bench/RESULTS.md` and the tip-chamfer debt file; race debt retires with the race fix and this decision | D-10..D-13 locked; the two recorded numbers located (SC3 server records: 30004 ms, 29.42 s alone); README lines 71 and 92-95 read; retirement mechanics and the self-sha impossibility flagged |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

Directives extracted from `./CLAUDE.md` (a symlink target of `AGENTS.md`). The planner must verify compliance; research recommends nothing that contradicts them.

- **The gate is `make verify`.** Nothing is "done" until it passes; state the command run and the result line. `make check` adds Docker checks. The phase changes what `make verify` is a prefix of, so its own recipe list is the thing under edit (D-03).
- **Stop and ask first** on: an architectural claim not in the decision log; a locked decision (`Lxx`) that looks wrong (propose superseding it); a library/API behaviour unverified after a real check; conflicting evidence; destructive operations; a choice trading stability for speed. Two items in this research hit that rule (see Open Questions 1 and 2).
- **Decisions:** new non-trivial choice → 2–3 options + recommendation → human picks → new `Lxx`. Already done for this phase at discuss-phase (D-01..D-17); do not re-litigate.
- **Two standing rules:** (1) a printed number is a number someone cuts metal to — no plausible number (L08); every measurement in `bench/RESULTS.md` and in both `Lxx` carries its host load and date; a non-reproduction is recorded as measured. (2) An unset parameter never silently changes the part (L05) — the margin decision moves no default and no `le`.
- **Keep it simple:** surgical edits, one concern per commit, no speculative features. Race fix = the two-fact guard + `_closed`, nothing else in `pool.py`.
- **Finishing work properly:** new behaviour ships with its tests in the same change; performance/memory claims are measured and recorded; no `TODO`/`pass`/unreachable branches (`make verify` fails on markers; `no-fake-done` also refuses any `type: ignore` / `mypy: ignore-errors` under `src/spur/`).
- **Debt capture:** non-blocking work survives in files; retire debt in the fixing commit (`Status: resolved`, sha, `git mv` into `resolved/`, INDEX row moved). State in the final reply whether any item was filed.
- **Code style:** comments carry the measurement or the constraint; vendor types stop at their boundary; `calc.py` never imports `cadquery`; English throughout; Conventional Commits, normal prose (not caveman).
- **Skills:** `.ai_skills/` and `.claude/skills/` hold only a README (checked this session) — no project skill applies.
- **Commit rule until the hook decision lands:** plain `git commit` with the hook allowed to finish; never `gsd_run query commit` (it is killed at 30 s and orphans the hook).

## Summary

The phase is small in code and large in ceremony. The code is: a 4-line guard plus a `_closed` flag in `src/spur/pool.py`; a new scenario and a `record_500` keyword in `bench/latency.py`; three new tests; three Makefile targets; one new hook entry and two edits in `.pre-commit-config.yaml`. The rest is measurement, a log entry (two `Lxx`), six doc sites, and debt-file retirement. Everything the planner needs from the prior milestone research was re-checked against the live tree today and found accurate, with the corrections listed under "Flags" below.

Two things were decided by measurement during this research rather than by citation. First, the `pre-push` semantics (SUMMARY disagreement 11): in a scratch repo with pre-commit 4.6.2 and git 2.54.0 the hook ran once per push regardless of ref count, did not run when there was nothing to push, for a tag-only push or a delete-only push, and did not run under `--no-verify`; and a tracked file whose working-tree content was changed but unstaged was read at its *committed* content by the hook, while an untracked file stayed visible. So STACK and PITFALLS are right (unstaged changes are stashed) and ARCHITECTURE is wrong. Second, the race fix and all three test shapes were run against a scratch copy of `pool.py`, unfixed and fixed: the fix turns `AttributeError` into `BuildTimeout` in the deterministic stale-executor shape and in the same-tick shape, and `_closed` stops `recreate_for` from building an unowned executor after `shutdown()`.

The one real risk is the bench reproduction (REQ-same-slot-timeout-race-reproduced). The `500` needs the second same-slot request's own deadline to fire within roughly 20 ms of the first's; PITFALLS 9 measured 4/4 `AttributeError` at gaps up to 5 ms, 3/4 at 20 ms, and 4/4 clean `BrokenProcessPool` at 100 ms. `run_composed` submits the nine siblings only after its first `/api/health` poll sees the worst row holding a slot; SC3's gap was about 15 ms, but if the first poll lands before the server admits the request, the next poll is at +100 ms and the siblings land outside the window. In the ten-identical shape the other worker is idle, so the worst row (0.58 s margin alone) may also simply finish inside 30 s and produce no timeout at all. A miss is therefore a plausible outcome, not a harness bug; D-15 (three attempts) and D-17 (checkpoint) already cover it, and the deterministic test is what makes the fix provable either way.

**Primary recommendation:** Build in the fixed order — (1) hook commit: Makefile targets, hook config, scratch-repo and real pre-push proofs, `L36`, six doc sites, debt retired, then one live SDK commit; (2) scenario commit, then up to three recorded pre-fix runs; (3) fix + tests commit, then the post-fix run; (4) margin `L37`, README sentence, dated notes, race debt retired. Run the red/green and repeat-loop proofs for `tests/test_pool.py` explicitly — after step 1 the commit hook no longer runs that file.

### Flags — where the code or the instructions contradict the plan text

1. **"Retires with its sha in the fixing commit" cannot be satisfied literally.** A commit cannot contain its own sha. The two newest retirements record the commit *subject* (`Resolved in: fix(gate): match unfinished-work markers ...`, `docs/tech_debt/resolved/2026-10-05-no-fake-done-scan-is-blind-on-macos.md:6`) and L34 records a later commit's sha for a follow-up (`b8926e7`). For the race debt the fix commit precedes the retirement commit, so its sha is available. For the hook debt it is not. See Open Question 1.
2. **After the hook commit, `tests/test_pool.py`, `test_model.py`, `test_api.py` and `test_cli.py` are not run at commit.** The RED-then-GREEN evidence for the race tests, the README edit's effect on `tests/test_cli.py` (it reads `README.md`, `tests/test_cli.py:147`), and any `test_pool.py` change must each be exercised by an explicit command, not left to the hook.
3. **The ten-identical bench is not guaranteed to reproduce** (above). SC3's two `500`s came from a 10–15 ms gap, and the scenario has less cross-slot contention than SC3 had.
4. **`make verify` itself is not changed in cost** (`verify: verify.static test` runs each recipe once) but the hook stamp adds a `pre-commit install` to the first gate run after a config change — verified harmless inside a running hook (below).
5. **PATTERNS.md and CONTEXT.md agree with the live code** on every line reference checked (`pool.py` 123-125, 204-206, 224-226; `latency.py` 181-206, 219-262, 321-332; `tests/test_bench.py` 604, 634). No contradiction found there.

## Architectural Responsibility Map

This phase has no browser, SSR or database capability. The tiers that matter are the developer workflow and the backend process boundary.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Commit-time gate (static + slice) | Developer workstation: git hook → `make` | `.pre-commit-config.yaml` | The hook runs the Makefile target; the Makefile owns what "the gate" means (L13), the config only names the stage |
| Full gate at push | Developer workstation: `pre-push` → `make verify` | CI, `make pr.land` (the wall, L22/L25) | Same `make verify` as CI; pre-push is local feedback, not the wall |
| Hook installation | `make` (`$(STAMP)` / hook stamp) | `docs/HOW_TO_DEVELOP.md` §0 | D-06: the gate installs the hooks so a clone cannot forget |
| Killed-commit recovery | Process: executor/human rule (D-07) | `docs/HOW_TO_DEVELOP.md`, `L36` | gsd-core is outside the repo; the repo can only state the rule |
| Same-slot timeout cleanup | API / backend process: `BuildPool` on the event-loop thread | `app.py` exception mapping (unchanged) | Atomicity rests on the single loop thread; `app.py` already maps `BuildTimeout` → `503 timeout` |
| Race reproduction and margin measurement | Bench harness (`bench/latency.py`) against a live host server | `bench/RESULTS.md` | Not part of the gate (Phase 13 D-16) |
| Margin as documented behaviour | Documentation (`README.md`, `bench/RESULTS.md`, `L37`) | `params.py` / `app.py` untouched | D-10: no default or cap moves |

## Standard Stack

No new dependency, runtime or dev (REQUIREMENTS "Rules every requirement lives by"). Everything below is already pinned in `pyproject.toml` / the venv.

### Core
| Library / tool | Version | Purpose | Why Standard |
|----------------|---------|---------|--------------|
| pre-commit | 4.6.2 (`.venv/bin/pre-commit --version`, read this session) | Owns the three git hook stages | Already a dev extra: `pyproject.toml` line 26 reads `"pre-commit>=4",` |
| GNU Make | 4.4.1 (`make --version`, read this session) | The command surface; `verify` / `verify.static` / `verify.fast` / `test.fast` | Project rule: reuse `make`, never ad-hoc shell |
| pytest + pytest-xdist + pytest-cov | pytest 9.1.1 (RESULTS Host state), xdist `>=3.8`, cov `>=7.1` | The slice and the full gate | `pyproject.toml` lines 27-28; recipe already `-n $(PYTEST_WORKERS)` |
| stdlib `asyncio`, `concurrent.futures` | CPython 3.12.13 (`python3.12 --version`) | The pool and the tests | Project floor (L23); `executor._processes` private attribute guarded by `test_executor_processes_attribute_still_exists` |
| httpx | existing | Bench client | Already imported by `bench/latency.py` |

### Supporting
| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| gh | authenticated as `halfb00t` (`gh auth status`, this session) | File the D-08 upstream issue; read PR state | One issue, one task |
| `gsd_run query commit` | gsd-core 1.16.0 (`~/.claude/gsd-core/VERSION`) | The live SC1 proof | Only after the hook commit has landed |
| git | 2.54.0 | Hook semantics, orphaned-hook measurement | Pinned by the measurements being quoted |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `--ignore=` exclusion list (D-04) | pytest markers | Needs a registered marker (`--strict-markers` is on) and decorated tests; rejected in D-04 |
| One `$(HOOKS)` stamp | `pre-commit install` appended inside `$(STAMP)` only | `$(STAMP)` depends on `pyproject.toml` only; an existing clone would never re-run it (D-06 caveat) |
| A drift test that parses YAML | Plain-text assertions on `.pre-commit-config.yaml` | PyYAML is in the venv (6.0.3) only as a transitive of pre-commit, not a declared dev dependency, and mypy `--strict` over `tests` would need stubs; text assertions avoid both |

**Installation:** none. (`make venv` already installs `pre-commit`.)

**Version verification:** `pre-commit 4.6.2`, `GNU Make 4.4.1`, `git version 2.54.0`, `Python 3.12.13`, `node v22.23.1`, gsd-core `1.16.0` were all read from the tools in this session. No registry lookup was needed because nothing is installed.

## Package Legitimacy Audit

This phase installs no external package; the legitimacy gate (`gsd_run query package-legitimacy check`) was not run because there is nothing to check. `pre-commit`, `pytest-xdist`, `pytest-cov` are pre-existing dev extras already in `pyproject.toml` (lines 26-28, read this session).

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| (none new) | — | — | — | — | — | — |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram

```
 COMMIT PATH (after this phase)                              PUSH / MERGE PATH
 ------------------------------                              -----------------
 gsd_run query commit  ──► git commit ──► pre-commit shim        git push ──► pre-push shim
   (30 s hard cap,                         (per-clone .git/hooks)              │  (once per push,
    COMMIT_TIMEOUT_MS)                          │                              │   first non-delete ref,
                                                ▼                              │   nothing to push = no run)
                          .pre-commit-config.yaml (read live)                  ▼
                                    │                                 hook "verify"  stages:[pre-push]
        ┌───────────────────────────┤                                          │
        ▼                           ▼                                          ▼
  hook "verify-fast"        hook "no-skip-token"                         make verify  (~64 s warm)
  stages:[pre-commit]       stages:[commit-msg]                                 │
        │                                                                       ▼
        ▼                                                          CI + ruleset + make pr.land (the wall)
  make verify.fast  (≈12.6 s warm / ≈21 s cold mypy)
        │
        ├─► verify.static  =  lint → typecheck → lint-imports → no-fake-done      (0.37 s warm)
        └─► test.fast      =  pytest -n 8 --no-cov --ignore=<4 heavy files>        (≈12.2 s, 617 tests)

 verify = verify.static + test(-n 8 --cov)       <- same static prefix; slice is the same recipe, narrower

 make venv / make verify ──► $(HOOKS) stamp (.pre-commit-config.yaml newer than stamp?)
                                    └─► pre-commit install  (commit-msg, pre-commit, pre-push)

 RACE (pool.py), one incident, two same-slot requests A and B (hash affinity, no lock):
   A,B submit ─► same executor E ─► both wait_for(timeout)
   A's timer fires ─► [sync block: terminate E's procs ─► recreate_for(E) ─► shutdown(wait=False) sets E._processes=None, slot := E']
   B's timer fires (≤ ~20 ms later, before the manager thread flags the pool broken)
        BEFORE fix: reads E._processes.values()  ─► AttributeError ─► no handler ─► raw 500
        AFTER fix : executor_for(p) is E? no  (or _processes is None) ─► skip ─► raise BuildTimeout ─► 503 timeout
   shutdown(): sets _closed; recreate_for honours it, so no unowned executor is built afterwards
```

### Recommended Project Structure
No new directories. Files touched, by commit:

```
Makefile                         # verify.static, verify, verify.fast, test.fast, $(HOOKS) stamp, .PHONY, help comments
.pre-commit-config.yaml          # header, default_install_hook_types, verify→pre-push, verify-fast→pre-commit
docs/architecture/decision_log.md# L36 (hook), L37 (margin); append-amend L13 and L34
docs/HOW_TO_DEVELOP.md           # §0, §6 (push rule, killed-commit rule)
README.md  docs/architecture/packaging.md  .github/workflows/ci.yml  scripts/pr_land.py   # one-sentence truth fixes
bench/latency.py  tests/test_bench.py  bench/RESULTS.md                                 # scenario commit
src/spur/pool.py  tests/test_pool.py  bench/RESULTS.md                                  # fix commit
docs/tech_debt/{active→resolved}/…  docs/tech_debt/INDEX.md                             # two retirements
tests/test_hooks.py  (optional drift test)
```

### Pattern 1: A prefix by construction, not a second list
**What:** `verify` and `verify.fast` share one prerequisite `verify.static`; `test` and `test.fast` are the same recipe line with different arguments.
**When to use:** the whole hook decision (D-03).
**Example** (shape only — names are the CONTEXT placeholders; the in-repo lines being edited are quoted verbatim in "Code Examples"):
```make
verify.static: lint typecheck lint-imports no-fake-done
verify: verify.static test  ## the gate: lint, types, import boundaries, tests
verify.fast: verify.static test.fast  ## the commit-time subset: the static steps + a 617-test slice, <30 s
```
`make -n verify` then lists the four static recipes before the pytest line, which is what success criterion 1 asks to see.

### Pattern 2: The two-fact guard, then raise regardless
**What:** terminate-and-replace only when this request's `executor` is still the live slot's *and* still has its process table; `raise BuildTimeout` is unconditional.
**When to use:** the `except TimeoutError` branch only. The `except BrokenProcessPool` branch needs no change — `recreate_for`'s own identity guard plus `_closed` cover it.

### Pattern 3: Stale-executor test without timers for ordering
**What:** create the request task, `await asyncio.sleep(0)` once (the task runs to its first suspension: `executor` captured, work submitted, awaiting `wait_for`), then call `pool.recreate_for(...)` synchronously from the test as the "first caller's" cleanup, then await the task. No sleep orders anything; the worker sleeps past `pool.timeout`.
**Verified:** ran as `probe.py` against a scratch copy of `pool.py` (see "Code Examples").

### Anti-Patterns to Avoid
- **An `await` inside the terminate-and-replace block** (for example to await the process's death before replacing): reopens the race. No lock exists; atomicity is "one event-loop thread, no suspension point". State this in the comment, naming the failure.
- **Terminating the first process in the stale-executor test:** a terminated worker makes the future fail with `BrokenProcessPool` (via the manager thread) *before* the timeout, so the test would exercise the wrong branch. Let the worker keep sleeping and reap it afterwards.
- **A broad `except AttributeError`** in the timeout branch: hides a genuine third defect (PITFALLS 9).
- **`verify: verify.fast test`** (CONTEXT D-03 rejects it): runs the slice twice, ~64 s → ~75 s, over L34's 66 s bar.
- **Adding `--cov` to `test.fast`:** `fail_under = 96` reads a partial run as a failure.
- **A `type: ignore` to silence `executor._processes is not None`:** `make no-fake-done` refuses any under `src/spur/`. Not needed: mypy `--strict --warn-unreachable` accepts the guard as written (verified).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Hook stage dispatch, stash of unstaged files, once-per-push semantics | A hand-written `.git/hooks/pre-push` script | `pre-commit` with `stages: [pre-push]` | Measured behaviour below; hand-written hooks are per-clone, unversioned state |
| "One definition of passing" for two stages | A second hard-coded list of checks in the hook entry | The Makefile prerequisite `verify.static` shared by `verify` and `verify.fast` | PITFALLS 14: two lists drift |
| Per-clone hook install | A README instruction alone | A Make stamp that runs `pre-commit install` when `.pre-commit-config.yaml` is newer | D-06; a forgotten clone otherwise pushes unverified in silence |
| Timeout of an overrunning build | A lock, a new queue, an `await` for process death | The existing synchronous terminate/replace block + the two-fact guard | The fix is four lines; any new suspension point reintroduces the bug |
| Subprocess liveness for the orphan-worker check | `psutil` | `_processes` handles and `proc.exitcode` (as `test_a_wedged_build_is_terminated_and_its_worker_replaced` already does) | `psutil` is not a runtime dependency; "no new dependency" |
| Reading a YAML hook config in a drift test | `import yaml` | Plain-text assertions | Transitive-only dependency; stub friction under `mypy --strict` |

**Key insight:** every piece of this phase is "make an existing mechanism say what is true" (a Make prerequisite, a guard against a stale reference, a recorded measurement). Anything that adds a mechanism is the wrong direction.

## Runtime State Inventory

This is not a rename or migration phase. The one piece of runtime state it touches is recorded for the planner.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — verified: nothing stores hook or timeout state; `/api/health` `workers_replaced` is an in-process counter reset at server start | None |
| Live service config | None — `spur-spur-1` container on :8000 (`docker ps`, this session) is untouched; the bench uses :8001 | None |
| OS-registered state | `.git/hooks` of this clone: `commit-msg`, `pre-commit` (read this session; no `pre-push`); other clones and `.claude/worktrees/*` share the common hooks dir | Code edit: the hook stamp installs `pre-push`; then verify `ls .git/hooks` |
| Secrets/env vars | None — `PYTEST_ARGS`, `PYTEST_WORKERS`, `SPUR_*` are tuning variables, not secrets | None |
| Build artifacts | `.venv/.installed` stamp (exists); the new `$(VENV)/.hooks-installed` stamp is created on the first gate run; `.mypy_cache`, `.coverage.*` from repeat-loops | None; `make clean` removes the venv and its stamps |

## Common Pitfalls

### Pitfall 1: The bench scenario does not reproduce, and that is a result
**What goes wrong:** the fix is written, or the `Lxx` is claimed, against a `500` nobody saw (L08).
**Why it happens:** the `AttributeError` window is a few milliseconds (PITFALLS 9 table: gap 0–5 ms 4/4 `AttributeError`; 20 ms 3/4; 100 ms 0/4). The scenario's sibling submissions follow the first poll that sees the worst row holding a slot: ≈15 ms in SC3 (server records: `build.started` of the worst row `08:23:05.326890`, its same-slot sibling `08:23:05.341732`), ≈100 ms later if the first poll lands before admission. Separately, with ten identical rows only one worker is busy; the worst row (29.42 s alone) may finish inside 30 s and nothing times out.
**How to avoid:** follow D-15 (three attempts, a fresh server each, every table recorded hit or miss) and D-17 (checkpoint, no default). Do not state the expected row mix in advance (ARCHITECTURE 2.3). Read the server's own `build.failed` records (`exception` field) as SC3 did, not only the client table.
**Warning signs:** a table of `200` and `503 busy` only; `workers_replaced` 0 → 0; or `503 pool_broken` rows (the sibling outside the window — a documented 503, not the bug).

### Pitfall 2: A test that exercises the wrong branch
**What goes wrong:** the stale-executor test goes green before the fix because the request ended in `BrokenProcessPool`, not the `TimeoutError` branch.
**Why it happens:** terminating the worker (or letting the loop stall past the manager thread's detection) fails the future before the timer.
**How to avoid:** the worker sleeps past `pool.timeout`; do not terminate it before the assertion; capture `proc` and `manager` before `recreate_for` (it drops the manager reference), then reap with the existing `manager.join(timeout=5)` + `proc.exitcode == -signal.SIGTERM` pattern after terminating. See the red run recorded below: pre-fix result must read `AttributeError`.

### Pitfall 3: The commit hook no longer runs the heavy tests
**What goes wrong:** a red `test_pool.py` / `test_model.py` / `test_api.py` / `test_cli.py` change commits cleanly and fails only at push.
**How to avoid:** run the touched heavy file explicitly in the task that edits it, and record the command and result line. This is by design (D-01) and `L36` must say which commits can now be red.

### Pitfall 4: `make test` with a subset and `--cov`
**What goes wrong:** `fail_under = 96` fails a partial run. 
**How to avoid:** `--no-cov` for any slice (the Makefile comment already says so); for the `-n 8 --cov` repeat loops add `--cov-fail-under=0` or read only the test outcome, and record that the coverage total was not the question.

### Pitfall 5: Flaky new tests on a loaded runner, on a file with two known flakes
**What goes wrong:** CI's 4-vCPU runner (`-n 4`) widens or narrows timing windows; `tests/test_pool.py` already carries a documented CI-only failure class (`proc.join` vs `waitpid`) and the resource-tracker warning debt lists this file's shutdown path.
**How to avoid:** deterministic decisive test; sibling test accepts `BuildTimeout` or `BrokenProcessPool`; pre-warm the worker (`executor.submit(os.getpid).result()`); never `proc.join()`/`is_alive()` for death; no blanket `PytestUnraisableExceptionWarning` ignore. Run repeats and record counts. Capture the whole log if the `ResourceTracker called reentrantly` warning appears.

### Pitfall 6: Editing the config re-installs hooks from inside a running hook
**What goes wrong (feared):** the hook stamp runs `pre-commit install` while the hook that invoked `make` is executing, replacing `.git/hooks/pre-commit` mid-run.
**Verified harmless:** in a scratch repo a hook entry ran `sleep 1; pre-commit install; sleep 1`; the commit completed, the hook file was intact (`# File generated by pre-commit`), all three hook files present. Residual risk: low; flagged `A3`.

### Pitfall 7: The self-referential sha
See Flag 1 and Open Question 1.

### Pitfall 8: Killed SDK commit before the hook decision lands
Every `gsd_run query commit` before the hook commit is killed at 30 s and orphans a ~64 s gate. The planning commits for this phase (this `RESEARCH.md`, PATTERNS, PLAN files) and the first plans' commits are plain `git commit`. This research did not commit its file for that reason (see the return message).

## Code Examples

In-repo values below are quoted verbatim from files opened this session. Items marked "proposed" are not in the repo yet.

### The fix site (current text, `src/spur/pool.py`)
```python
            for proc in executor._processes.values():
                proc.terminate()
            self.recreate_for(p, executor, "timeout")
            raise BuildTimeout(
```
(lines 204-207), `recreate_for`'s guard:
```python
        i = hash(p) % self.workers
        if self._executors[i] is not executor:
            return  # someone else already replaced this slot for this incident
```
(lines 123-125), and:
```python
    def shutdown(self) -> None:
        for executor in self._executors:
            executor.shutdown(wait=False)
```
(lines 224-226).

### Proposed fix (applied to a scratch copy and run, repo untouched)
```python
        except TimeoutError:
            # ...existing comments kept; add: why both facts, and that nothing here awaits
            if self.executor_for(p) is executor and executor._processes is not None:
                for proc in executor._processes.values():
                    proc.terminate()
                self.recreate_for(p, executor, "timeout")
            raise BuildTimeout(
                f"Build exceeded the {self.timeout}s per-build timeout. Try a coarser "
                "quality or fewer teeth."
            ) from None
```
`__init__`: `self._closed = False` before `self._executors = [`. `recreate_for`: `if self._closed or self._executors[i] is not executor:`. `shutdown()`: `self._closed = True` first.
**mypy:** `.venv/bin/python -m mypy --strict --warn-unreachable` on a snippet with `if executor._processes is not None:` → `Success: no issues found in 1 source file` (no `type: ignore`). Do not add an `else:` with statements: `warn_unreachable` would then flag it, because typeshed types `_processes` as non-optional.

### Measured: the three race shapes, unfixed vs fixed (scratch copies, 2026-10-06, host load ≈3–4)
| Shape | Unfixed `pool.py` | With the guard + `_closed` |
|---|---|---|
| Deterministic stale executor (task started, `sleep(0)`, `recreate_for` by the test, await task; `timeout=0.5`, worker sleeps 2.0 s) | `AttributeError`, `replaced == 1` | `BuildTimeout`, `replaced == 1` |
| 3 same-slot requests in one tick, `timeout=1.0`, worker sleeps 10 s | `['BuildTimeout', 'AttributeError', 'AttributeError']`, `replaced == 1` | `['BuildTimeout', 'BuildTimeout', 'BuildTimeout']`, `replaced == 1` |
| `shutdown()` then `recreate_for(params, executor, "broken_pool")` | slot replaced (`executor_for(params) is executor` → `False`), `replaced == 1` | slot unchanged (`True`), `replaced == 0` |

The same-tick pre-fix row reproduces ARCHITECTURE 2.2's measurement. Coverage consequence: the false arm of the new `if` is covered only by the stale-executor test, and the `_closed` early return only by a `_closed` test — add one (`BuildPool(workers=1, timeout=1)` has no live process until first use, so it is cheap).

### Test skeleton for the deterministic stale-executor test (proposed; mirrors the shape that was run)
```python
def test_a_stale_executor_timeout_is_a_build_timeout_not_an_attribute_error() -> None:
    with TestClient(app):
        pool = app.state.pool
        params = GearParams(teeth=21)
        live = pool.executor_for(params)
        live.submit(os.getpid).result()                    # pre-warm: spawn + _warm not on the clock
        [proc] = list(live._processes.values())            # captured before recreate_for drops them
        manager = live._executor_manager_thread
        assert isinstance(manager, threading.Thread)
        replaced_before = pool.replaced
        original_timeout = pool.timeout
        pool.timeout = 0.5

        async def _drive() -> bytes:
            task = asyncio.create_task(pool._run_with_timeout(params, _sleep_past_timeout, 2.0))
            await asyncio.sleep(0)                          # task is now awaiting wait_for on `live`
            pool.recreate_for(params, live, "timeout")      # the "first caller" already cleaned up
            return await task

        try:
            with pytest.raises(BuildTimeout):               # pre-fix: AttributeError escapes instead
                asyncio.run(_drive())
        finally:
            pool.timeout = original_timeout
        assert pool.replaced == replaced_before + 1         # the stale branch replaced nothing
        proc.terminate()
        manager.join(timeout=5)
        assert not manager.is_alive()
        assert proc.exitcode == -signal.SIGTERM
```
Mypy `--strict` over `tests` applies; the existing tests cast `asyncio.gather(..., return_exceptions=True)` to `list[object]` — do the same in the same-tick test.

### Same-tick sibling test (proposed)
Three `create_task(pool._run_with_timeout(params, _sleep_past_timeout, 10.0))` in one tick, `pool.timeout = 1.0`, gather with `return_exceptions=True`; assert `isinstance(first, BuildTimeout)`; each sibling `isinstance(r, (BuildTimeout, BrokenProcessPool))` and never `AttributeError`; `pool.replaced == replaced_before + 1`; one `worker.replaced` record (`caplog.set_level(logging.INFO)`, `_event_records`). Note the honest limit: with siblings allowed to be `BrokenProcessPool`, this test would not catch an inserted `await`; only the deterministic test and (optionally) an `ast` check that the `except TimeoutError` handler contains no `Await` node do.

### Bench plumbing (current text, `bench/latency.py`, quoted for the planner)
```python
def run_composed(base_url: str) -> ComposedRun:
```
(line 219), `rows = _composed_rows()` (line 229), the 500-raising branch:
```python
    else:
        response.raise_for_status()
        status = "200"
```
and the registry:
```python
DEFAULT_SCENARIOS: tuple[str, ...] = ("concurrent", "single")
```
Proposed: `_fetch(..., record_500: bool = False)` → when true and `response.status_code == 500`, `status = "500"` instead of raising; `run_composed(base_url, rows=None, label="composed", record_500=False)` threading both through the worst-row fetch and the nine others; `scenario_identical` passes `[rows[0]] * 10, "identical", True`; `_composed_markdown` heading and `_report_markdown`'s baseline-suppression test (`name != "composed"`) take the label; `tests/test_bench.py:604` becomes `{"concurrent", "single", "composed", "identical"}`; add tests for `record_500=True` → `"500"`, default still `pytest.raises(httpx.HTTPStatusError)`, the identical rows all equal and equal to the worst row, and the baseline line omitted for `"identical"`.

### Running the scenario (D-16, proposed commands)
```bash
SPUR_PORT=8001 .venv/bin/spur serve > /path/to/attempt-N.server.log 2>&1 &   # :8000 is the spur-spur-1 container
.venv/bin/python -m bench.latency --base-url http://127.0.0.1:8001 identical
# stop the server; read build.failed / worker.replaced records from the log for the AttributeError line
```
Record per attempt: date/time, HEAD, `sysctl -n vm.loadavg` before and after, `bench.machine_facts()`, the per-request table, `workers_replaced` before/after, hit or miss. `bench/RESULTS.md` "### Host state" blocks (e.g. lines 1199, 1307, 2138, 2211) are the template.

### The hook arrangement (proposed config; stage pinning follows the file's own rule)
```yaml
default_install_hook_types: [pre-commit, commit-msg, pre-push]
# ...
      - id: verify-fast
        entry: make verify.fast
        language: system
        pass_filenames: false
        always_run: true
        stages: [pre-commit]
      - id: verify
        entry: make verify
        language: system
        pass_filenames: false
        always_run: true
        stages: [pre-push]
```
Current lines being edited, verbatim: `default_install_hook_types: [pre-commit, commit-msg]`, `entry: make verify`, `stages: [pre-commit]` (`.pre-commit-config.yaml` lines 18, 25, 32).

### Hook stamp (proposed; one stamp is enough)
```make
HOOKS := $(VENV)/.hooks-installed
$(HOOKS): .pre-commit-config.yaml $(STAMP)
	$(VENV)/bin/pre-commit install
	@touch $@
venv: $(HOOKS)
verify.static: $(HOOKS) lint typecheck lint-imports no-fake-done
```
(`$(STAMP)` already creates `pre-commit` in the venv through `.[dev]`.) New names go into `.PHONY` and the `##` help comments (the help grep is `'^[a-z][a-z.-]*:.*##'`, so dotted names list).

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| L13: `make verify` ~11 s warm, run in the pre-commit hook | L34: 63.555 s warm; this phase: pre-commit runs `verify.fast`, pre-push runs `verify` | 2026-10-04 (L34), this phase | The hook no longer outruns gsd's 30 s `COMMIT_TIMEOUT_MS` |
| Executor recovery for `commit_timeout`: remove the lock and retry once | Wait for the orphan (`pgrep`), then one plain `git commit` | this phase (D-07) | A blind retry overlaps the orphaned gate and is itself killed |
| Debt file: "compare identity against `self._executors[i]`" before touching `_processes` | Two facts: identity **and** `_processes is not None`, plus `_closed` | PITFALLS 9 / SUMMARY correction 8 | An identity-only guard leaves the `shutdown()` route open (measured: `_processes = None` with slot identity unchanged) |

**Deprecated/outdated:**
- The commit-timeout debt file's `commands.cjs:3655` and `gsd-executor.md:837` line references: stale. `const COMMIT_TIMEOUT_MS = 30_000;` is at `commands.cjs:3794` today and the three commit sites are at 2441, 2631 and 2787 (read this session). Cite the symbol, never the line.
- README/HOW_TO_DEVELOP/packaging/ci.yml wording "the pre-commit hook runs `make verify`" (all six sites read this session).
- ARCHITECTURE §3's "pre-push runs on the working tree": contradicted by the scratch-repo measurement below.

### Pre-push semantics, measured in a scratch repo (this session; pre-commit 4.6.2, git 2.54.0, 2026-10-06)
Two local hooks, `always_run: true`, `pass_filenames: false`: `fast` at `pre-commit`, `full` at `pre-push`; three hook types installed; a local bare remote.

| Scenario | `full` ran? |
|---|---|
| First push of 2 commits | once |
| Push again with nothing new (`Everything up-to-date`) | no |
| New commit, tracked file modified but unstaged (`UNSTAGED`) + untracked file present | once; the hook read `tracked=base` (the committed content — pre-commit printed `Stashing unstaged files`) and `untracked=untracked.txt` (visible) |
| One `git push` carrying two refs | once |
| Tag-only push of an already-pushed commit | no |
| Delete-only push | no |
| `git push --no-verify` | no |
| `SKIP=full git push` | printed `Skipped` |

Conclusion for `L36`: STACK and PITFALLS are right, ARCHITECTURE is wrong — unstaged changes are stashed; the gate sees index plus untracked files. Still true (PITFALLS 13): it verifies the checked-out tree, not an arbitrary `<sha>:refs/heads/x` pushed from another checkout; `.git/hooks/pre-push` exists per clone.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `pre-commit install` succeeds in a GitHub Actions checkout (CONTEXT D-06 ASSUMPTION, unchanged) | Hook stamp | CI's `make verify` step fails on the first run; confirm on the phase's first CI run; fallback is to run the install only when it can succeed (a plan task decides after reading the CI log), never to swallow its failure |
| A2 | CI's 4-vCPU runner (`-n 4`) does not make the two new tests flaky beyond what the repeat loops show locally | Pitfall 5 | A CI-only failure after the phase's PR; mitigated by the deterministic test and the loose sibling assertion; the loops cover only this host |
| A3 | Re-running `pre-commit install` from inside a running hook is safe on Linux (CI) as on macOS (verified only on macOS, git 2.54.0) | Pitfall 6 | A broken hook on Linux; in CI no hook fires, so the exposure is a developer on Linux |
| A4 | `uvicorn` graceful shutdown can reach the `shutdown()` route to the `AttributeError` (PITFALLS 9 flagged it ASSUMPTION; only the direct call is measured) | Fix scope | Affects only whether `_closed` is reachable in production; the guard is correct either way and the `_closed` test uses the direct call |
| A5 | The ten-identical scenario's worst row may finish inside 30 s on a lightly loaded host (reasoned from 29.42 s alone and one busy worker; not run) | Pitfall 1 | Only changes how likely a miss is; the protocol already covers a miss |
| A6 | A cold OS page cache would still keep the commit-time subset under 30 s (the 8.68 s cold-mypy and 12.2 s warm-slice figures are measured; an OS-cold OpenCascade page-in for the slice is not) | Hook pricing | A killed SDK commit on the first commit after a long idle or reboot; D-07 is the recovery. Re-price at decision time per D-02, and if the slice imports the kernel (not checked here) say so in the `Lxx` |
| A7 | The upstream issue text, once drafted, is acceptable to post publicly in the user's name | Open Question 2 | A public post the user did not review |

## Open Questions

1. **"Retires with its sha in the fixing commit" — which sha form?**
   - What we know: a commit cannot contain its own sha. Precedents: subject-line form (`docs/tech_debt/resolved/2026-10-05-no-fake-done-scan-is-blind-on-macos.md:6`, `...intel-context-repeats-superseded-figures.md:6`), a prior-commit sha (`2026-09-28-tip-chamfer...md:6` → `89304e2`), and L34's follow-up commit recording a sha. An active `nice` debt (`2026-10-05-resolved-in-shas-point-at-squashed-branch-commits.md`) already says squashed-branch shas are fragile.
   - What's unclear: whether SC2's "with its sha" means a follow-up commit or the subject form.
   - Recommendation: race debt — cite the **fix commit's sha** (it precedes the retiring margin commit, so it exists) plus the PR number is unknown until later; hook debt — use the subject form in the hook commit (matches the two newest retirements and keeps CLAUDE.md's "same commit"), and have the live SDK-commit task (which is a separate commit anyway) not edit it. If the human wants a sha, the alternative is a tiny follow-up commit; surface this to the human at plan review rather than choosing.

2. **Who posts the upstream issue (D-08), and when?**
   - What we know: `gh` is authenticated as `halfb00t`; searching `open-gsd/gsd-core` for "commit timeout" and for "COMMIT_TIMEOUT_MS" returned only #3886 (closed) today; the symbol, three call sites and the message text are read.
   - What's unclear: it is an outward-facing write in the user's name.
   - Recommendation: the executor drafts the issue body into the plan's SUMMARY and creates it only after a `checkpoint:human-verify` on the text (symbol not line, no config key, #3886 as prior art, no local paths or secrets); the `Lxx` then records URL and date.

3. **Which exact repeat counts for "repeatedly" (SC4)?** 
   - Recommendation: 20 loops of `tests/test_pool.py` together with `tests/test_api.py` at `-n 8 --cov --cov-fail-under=0` and 20 at `-n 4`, plus three full `make verify` runs; record `k/N green` for each. The repo precedent is "0/18 locally" in a test comment. The planner may choose different counts; the requirement is that they are recorded.

4. **Should an `ast` tripwire (no `Await` in the `except TimeoutError` handler) be added?** Optional; the sibling test cannot detect an inserted `await` (PITFALLS 9's request) because it accepts `BrokenProcessPool`. Recommend yes only if the planner wants the "no await" boundary enforced rather than commented — ~10 lines, no dependency.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12 + `.venv` | everything | ✓ | 3.12.13 | — (L23) |
| pre-commit | hooks, scratch-repo check | ✓ | 4.6.2 | — |
| GNU Make | targets | ✓ | 4.4.1 | — |
| git | hooks, orphan measurement | ✓ | 2.54.0 | — |
| Node | the SDK's `spawnSync` commit, `gsd_run` | ✓ | v22.23.1 | — |
| gsd-core | the live SC1 proof | ✓ | 1.16.0 | — |
| gh (authenticated) | D-08 issue | ✓ | logged in as `halfb00t` | file by hand |
| Docker | `make check` only; occupies :8000 (`spur-spur-1`, healthy) | ✓ | — | not needed for this phase's gate; the bench uses :8001 |
| Port 8001 free | the bench server | ✓ (no listener on 8001; `lsof`, this session) | — | any free port with `--base-url` |
| Quiet host | the bench | ✗ (load 3.0–4.1 this session; D-14 declines the gate) | — | record load beside each table |
| A bare remote for a real pre-push proof | success criterion "pre-push verified" | create one: `git clone --bare . <scratch>` | — | the scratch-repo toy hook already measured |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** a quiet host (not required).

Prices re-measured today for the `L36` (D-02: "re-price at decision time" is still a plan task; these are the research-time baselines, labelled by when they were taken):

| Piece | Wall | Conditions |
|---|---|---|
| `make lint typecheck lint-imports no-fake-done` (warm) | 0.37 s | 2026-10-06 ≈13:36, load 3.75 |
| pytest slice, `-n 8 --no-cov`, 4 files ignored | 617 passed in 11.98 s; 12.18 s wall | same session, load 3.75 → 4.07 |
| mypy over `src tests docker bench scripts` with an empty `--cache-dir` | 8.68 s | ≈13:38, load 3.0–3.8 |
| Subset warm / with cold mypy | ≈12.6 s / ≈21 s | sum of the above (prior research: ≈12 s / ≈21 s at load 5–9) |
| Full `make verify` | 63.555 s warm | L34 (2026-10-04) |

## Validation Architecture

> `workflow.nyquist_validation` is not set in `.planning/config.json` (the file holds only `workflow._auto_chain_active`, `workflow.use_worktrees`, `git.branching_strategy`), so the section is enabled.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 + pytest-xdist (`-n 8`, clamped to the host) + pytest-cov; `filterwarnings = ["error", ...]`, `--strict-markers --strict-config`, `testpaths = ["tests"]` (`pyproject.toml` lines 121-124) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]`; floor `fail_under = 96`, `precision = 2` (lines 152-155) |
| Quick run command | `make test PYTEST_ARGS="<paths or -k> -q --no-cov"` (PYTEST_ARGS comes last, so `--no-cov` wins) |
| Full suite command | `make verify` (~64 s warm; the phase gate) |
| Commit-time subset (after this phase) | `make verify.fast` (≈12.6 s warm) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-hook-and-commit-timeout-decided | `verify` depends on the static prefix and the subset is that prefix + the same pytest recipe | structural / dry-run | `make -n verify` — green: the four static recipes (`ruff check`, `mypy`, `lint-imports`, the `git grep` scan) print before the single `pytest` line, and no second pytest line appears; red: no static prefix, or two pytest lines. Optional pinned form: `tests/test_hooks.py` (text assertions: `entry: make verify.fast` is at `stages: [pre-commit]`, `entry: make verify` at `stages: [pre-push]`, and `make -n verify` / `make -n verify.fast` share the static recipes) | ❌ Wave 0 (optional drift test) |
| REQ-hook-and-commit-timeout-decided | Pre-push semantics (once per push, first ref, stash, per-clone install) | manual scratch-repo script, recorded in `L36` | the script run in this research (scratch repo + bare remote, log of hook runs); the plan repeats it and pastes the table | ✅ method verified this session |
| REQ-hook-and-commit-timeout-decided | The real gate passes under the *pre-push* environment (git sets different `GIT_*` vars than for pre-commit; `tests/test_no_fake_done.py` already scrubs `GIT_*`) | live | push a scratch branch to a local bare clone of this repo (`git clone --bare . <scratch>.git`, `git remote add scratch ...`, `git push scratch HEAD:refs/heads/probe` with a 300 s tool timeout); green: hook prints `verify ... Passed` and the push completes; red: a gate failure only seen under pre-push | ❌ Wave 0 (task, not a file) |
| REQ-hook-and-commit-timeout-decided | An SDK commit completes inside 30 s | live | `gsd_run query commit "docs(17): record the hook decision proof" --files <one .planning file>` timed with `time`; green: JSON `committed: true`, a `hash`, `git log -1 --format=%H` equals it, wall < 30 s; red: `reason: 'commit_timeout'` (then D-07: `pgrep -fl 'pre-commit|pytest|mypy'`, wait, one plain commit) | ✅ gsd-core 1.16.0 present |
| REQ-hook-and-commit-timeout-decided | Hooks installed without a hand-typed command | structural | `rm -f .venv/.hooks-installed; make verify.static; ls .git/hooks` — green: `commit-msg pre-commit pre-push` | ❌ Wave 0 (Makefile stamp) |
| REQ-hook-and-commit-timeout-decided | Doc sites say the new truth; stale "~42 s" gone | grep | `git grep -n "pre-commit hook" -- README.md docs .github scripts .pre-commit-config.yaml` and `git grep -n "~42 s" -- scripts` — green: no line says the pre-commit hook runs `make verify`; `~42 s` absent | ✅ |
| REQ-hook-and-commit-timeout-decided | Debt retired | structural | `test ! -e docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md`; `grep -n "Status: resolved" docs/tech_debt/resolved/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md`; INDEX row in the Resolved table | ✅ |
| REQ-same-slot-timeout-race-reproduced | Scenario registered, not default; `record_500` records a `500`; default `_fetch` still raises; ten identical rows | unit | `make test PYTEST_ARGS="tests/test_bench.py -q --no-cov"` — green: `DEFAULT_SCENARIOS == ("concurrent", "single")` still, `set(_SCENARIOS)` includes the new name, `_fetch(..., record_500=True)` returns status `"500"`, default raises `httpx.HTTPStatusError`, the ten rows are equal to the worst row, baseline line omitted for the new name; red before the edit: the registry assertion at `tests/test_bench.py:604` fails once the scenario is added | ✅ file exists (edit) |
| REQ-same-slot-timeout-race-reproduced | The `500` is visible in a pre-fix table with host state | bench (live, not gate) | `SPUR_PORT=8001 .venv/bin/spur serve` (background), `.venv/bin/python -m bench.latency --base-url http://127.0.0.1:8001 identical`; up to three attempts on restarted servers; green (hit): a row `500`, `workers_replaced` 0 → ≥1, server log `build.failed` with `exception: AttributeError`; miss: recorded as measured, D-17 checkpoint | ❌ Wave 0 (scenario code) |
| REQ-same-slot-timeout-race-fixed | A second same-slot timeout on a replaced executor is `BuildTimeout`, not `AttributeError` | unit (deterministic) | `make test PYTEST_ARGS="tests/test_pool.py -k stale_executor -q --no-cov"` — **red before the fix** (recorded: `AttributeError`), green after; reproduced in a scratch copy this session | ❌ Wave 0 (new test) |
| REQ-same-slot-timeout-race-fixed | Same-tick same-slot siblings never `AttributeError`; one replacement; one `worker.replaced` record | unit (timing) | `make test PYTEST_ARGS="tests/test_pool.py -k same_tick -q --no-cov"` — red before the fix (`[BuildTimeout, AttributeError, AttributeError]`), green after (siblings `BuildTimeout` or `BrokenProcessPool`) | ❌ Wave 0 (new test) |
| REQ-same-slot-timeout-race-fixed | `recreate_for` after `shutdown()` builds nothing (the `_closed` route) | unit | `make test PYTEST_ARGS="tests/test_pool.py -k closed -q --no-cov"` — red before (`executor_for(params) is executor` is `False`, `replaced == 1`), green after (`True`, `0`) | ❌ Wave 0 (new test) |
| REQ-same-slot-timeout-race-fixed | The 0.5 s-gap test is unchanged and still green | regression | `git diff -U0 tests/test_pool.py` shows additions only; `make test PYTEST_ARGS="tests/test_pool.py -k four_same_slot -q --no-cov"` green | ✅ |
| REQ-same-slot-timeout-race-fixed | New tests are stable under the gate's own invocation | repeat loop | `for i in $(seq 1 20); do .venv/bin/python -m pytest -n 8 --cov --cov-report= --cov-fail-under=0 -q tests/test_pool.py tests/test_api.py || echo FAIL $i; done`, then the same with `-n 4`; record `k/20 green` for each, plus three `make verify` runs | ✅ commands; counts recorded in SUMMARY |
| REQ-same-slot-timeout-race-fixed | Coverage floor holds with the new branches covered | gate | `make verify` — `fail_under = 96`; the false arm of the new `if` and the `_closed` early return are covered only by the new tests | ✅ |
| REQ-same-slot-timeout-race-fixed | Typing and the no-suppression pin hold | gate | `make typecheck no-fake-done` — green: `Success: no issues found`, no `type: ignore` under `src/spur/` | ✅ |
| REQ-same-slot-timeout-race-fixed | Zero `500`s after the fix | bench (live) | the same scenario command on a fresh server; green: only `200`, `503 timeout`, `503 busy`, `503 pool_broken`; table appended to `bench/RESULTS.md`. A zero-`500` run with a pre-fix miss proves nothing by itself — the deterministic test is the proof | ❌ Wave 0 |
| REQ-worst-row-margin-decided | `L37` exists and names the numbers | grep | `grep -n "^## L37" docs/architecture/decision_log.md`; the entry quotes `29.42`, `30004` (or `30.004 s`), `0.58`, the identical-row figure with its load and date, and the revisit trigger (D-13) | ❌ Wave 0 |
| REQ-worst-row-margin-decided | No default or cap moved | diff | `git diff <phase-base> -- src/spur/app.py src/spur/params.py` shows nothing for `int_env("SPUR_BUILD_TIMEOUT", 30)` or `spoke_count`'s `0, 32` | ✅ |
| REQ-worst-row-margin-decided | Limit reaches users; dated notes present | grep | `grep -n "503" README.md` shows the new sentence; `bench/RESULTS.md` and `docs/tech_debt/resolved/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md` carry a dated note beside "~1.02x"; run `make test PYTEST_ARGS="tests/test_cli.py -q --no-cov"` after the README edit (it reads `README.md`, and the commit hook no longer runs it) | ✅ |
| REQ-worst-row-margin-decided | Race debt retires only with both findings closed | structural | one commit: `Status: resolved`, `Resolved in:`, `git mv` to `resolved/`, INDEX row moved; `git show --stat HEAD` lists the rename and the INDEX edit together with the `L37` entry | ✅ |

### Sampling Rate
- **Per task commit:** the command named in the row for the task (heavy test files explicitly, since the commit hook no longer runs them), then the commit's own hook.
- **Per wave merge:** `make verify` (full, `-n 8 --cov`), result line stated.
- **Phase gate:** `make verify` green on the phase branch; the full gate also runs at push (pre-push) and in CI; `make check` only if the phase touches the container (it does not).

### Wave 0 Gaps
- [ ] `tests/test_pool.py` — three new tests (stale-executor, same-tick, `_closed`), run red against the unfixed `pool.py` first
- [ ] `tests/test_bench.py` — registry assertion (line 604) updated; `record_500`, identical-rows and baseline-suppression tests
- [ ] `bench/latency.py` — `record_500`, `run_composed(rows, label, record_500)`, the new scenario
- [ ] `Makefile` — `verify.static`, `verify.fast`, `test.fast`, `$(HOOKS)`, `.PHONY`
- [ ] `tests/test_hooks.py` — optional drift test (text assertions only)
- [ ] a bare scratch remote for the real pre-push proof (task, not a file)
- No framework install: pytest, xdist, cov already present.

## Security Domain

`security_enforcement` is absent from `.planning/config.json`, so this section applies. The phase touches no request-parsing, authentication or cryptographic surface; the relevant controls are about the tooling and one failure mode.

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — (the service has none; `docs/tech_debt/active/2026-09-21-no-authentication.md`) |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | no change | Pydantic `GearParams` at the boundary, untouched; bench rows are read from a committed JSON sweep, not user input |
| V6 Cryptography | no | — |
| V7 Error Handling and Logging | yes | The race returned a raw `500` with an unhandled `AttributeError`; the fix restores the documented `503 timeout` body. `worker.replaced` stays once per incident (inside the identity guard) |
| V14 Config / Build | yes | Hooks are repo-versioned config (`.pre-commit-config.yaml`); `--no-verify`/`SKIP=` remain possible bypasses, with CI + ruleset + `make pr.land` as the wall (L22/L25) |

### Known Threat Patterns for this stack
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Resource exhaustion: an orphaned wedged worker keeps a ~810–870 MiB OCC solid (L17) after a mishandled cleanup | Denial of Service | Guard so the first caller's terminate stands; `_closed` stops unowned replacements; optional test that the worker count returns to N (read `_processes`/exit codes, no `psutil`) |
| Information disclosure through an unhandled exception | Information Disclosure | Documented `503` body instead of an unhandled `AttributeError` (uvicorn logs the traceback server-side) |
| Gate bypass by habit (`--no-verify`) | Tampering | Not adopted (Out of Scope); CI + ruleset enforce |
| Supply chain via a new package | Tampering | None added; `package-legitimacy` not applicable |
| Publishing local paths/secrets in the upstream issue | Information Disclosure | Human checkpoint on the issue text (Open Question 2) |

## Sources

### Primary (HIGH confidence — read or measured in this session)
- `src/spur/pool.py`, `src/spur/app.py` (lines 85-160, 330-480), `src/spur/cli.py` (serve), `src/spur/__init__.py` (`int_env`), `src/spur/params.py` (spoke comment) — read in full or the relevant ranges.
- `bench/latency.py`, `bench/__init__.py` (`machine_facts`), `bench/RESULTS.md` (lines 465-610, 2205-2235), `tests/test_pool.py` (1-204, 400-527), `tests/test_bench.py` (540-660), `tests/test_no_fake_done.py` (1-45), `tests/test_cli.py` (138-175).
- `Makefile`, `.pre-commit-config.yaml`, `pyproject.toml` (pytest, coverage, deps), `.github/workflows/ci.yml` (15-60), `scripts/pr_land.py` (55-75), `docs/HOW_TO_DEVELOP.md` (10-32, 108-135), `README.md` (66-98, 280-292), `docs/architecture/packaging.md` (44-54), `docs/architecture/decision_log.md` (L13, L34, L35), `docs/tech_debt/` (both `must` files, both `nice` reads, INDEX, the tip-chamfer file lines 55-70).
- `~/.claude/gsd-core/bin/lib/commands.cjs` (`COMMIT_TIMEOUT_MS` lines 2441, 2631, 2787, 2793, 3794, 3813) and `agents/gsd-executor.md` (the `commit_timeout` bullet), `~/.claude/gsd-core/VERSION` = 1.16.0.
- `.planning/milestones/v0.3-phases/13-latency-bar/investigation/sc3.server1.records.jsonl` (the `build.started` / `build.failed` / `worker.replaced` timestamps and `AttributeError` records).
- Scratch-repo measurements (pre-push semantics; in-hook `pre-commit install`) and scratch-copy runs of the race fix, all under the session scratchpad; the repo tree was left unmodified (`git status` shows only the concurrently written `17-PATTERNS.md`).
- `gh search issues --repo open-gsd/gsd-core` ("commit timeout", "COMMIT_TIMEOUT_MS") and `gh issue view 3886` (state CLOSED).

### Secondary (MEDIUM confidence)
- `.planning/research/{SUMMARY,STACK,ARCHITECTURE,PITFALLS}.md` — prior-milestone research, cited for the window table (PITFALLS 9) and the orphaned-hook measurement (PITFALLS 15); the window table and the three race shapes were corroborated today, the orphan measurement was not re-run.

### Tertiary (LOW confidence)
- None used. External documentation lookups (Context7 / web) were not needed: every behaviour depended on was observed directly on the installed tools.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — nothing new; versions read from the tools.
- Architecture: HIGH — fix and test shapes run against a scratch copy; hook semantics measured in a scratch repo.
- Pitfalls: HIGH for the race and the hook; MEDIUM for CI-runner timing (A2) and Linux behaviour of in-hook reinstall (A3).
- Bench reproduction probability: MEDIUM — the mechanism is well supported (SC3 timestamps, PITFALLS 9 table) but the scenario itself has not been run.

**Research date:** 2026-10-06
**Valid until:** 2026-11-05 for the code facts (line numbers in `pool.py`, `latency.py`, Makefile drift with the first edit); the gsd-core line numbers are explicitly not to be cited (cite `COMMIT_TIMEOUT_MS`).
