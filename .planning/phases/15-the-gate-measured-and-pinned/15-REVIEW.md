---
phase: 15-the-gate-measured-and-pinned
reviewed: 2026-10-04T00:00:00Z
depth: standard
files_reviewed: 18
files_reviewed_list:
  - .github/workflows/ci.yml
  - .gitignore
  - .pre-commit-config.yaml
  - bench/RESULTS.md
  - docs/architecture/decision_log.md
  - docs/architecture/packaging.md
  - docs/HOW_TO_DEVELOP.md
  - docs/ideas/2026-10-03-constrain-make-venv-to-the-closure.md
  - docs/ideas/INDEX.md
  - docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md
  - docs/tech_debt/active/2026-10-04-worker-coverage-flush-is-sometimes-lost.md
  - docs/tech_debt/INDEX.md
  - docs/tech_debt/resolved/2026-09-21-no-coverage-floor.md
  - docs/tech_debt/resolved/2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md
  - Makefile
  - pyproject.toml
  - README.md
  - tests/regression/test_pre_v0_2.py
findings:
  critical: 0
  warning: 4
  info: 4
  total: 8
status: issues_found
---

# Phase 15: Code Review Report

**Reviewed:** 2026-10-04
**Depth:** standard
**Files Reviewed:** 18
**Status:** issues_found

## Summary

No `src/` code changed, so this review is about the gate's construction and the numbers
the phase wrote down. No BLOCKER found: the Makefile `$(shell ...)` expression is correct
under make's quoting (`$$(( n < w ? n : w ))` expands to the intended POSIX arithmetic),
`.gitignore` covers both `.coverage` and `.coverage.*` (confirmed with `git check-ignore`),
`addopts` and `requirements.txt` are untouched, and `PIP_CONSTRAINT` is a real, working
constraint (CI run 37181871926 re-read with `gh`: head `839dfea`, conclusion `success`,
`created: 4/4 workers`, `927 passed in 203.16s`, `TOTAL ... 97.29%`, the pair line, and the
`Cache hit` line all match the record).

I recomputed the arithmetic in `bench/RESULTS.md` § "The gate, measured and pinned
(Phase 15)": per-file sums and shares, the sweep speed-ups, mean(A)/mean(B) of both
tolerance and before/after sets, the bar margin, the floor derivation, the 71-item cut
arithmetic (74 listed minus the three `dedup-g4-g5` rows that sit on the other side of
each pair, 71 deselected, 927 - 71 = 856) and the 47.46 s sum. All reproduce. The
`git diff --quiet` byte-identity claims for `20cd484`/`862a807`/`4b798ac`/`5797199` also
hold. The defects are an omitted comparison that changes how the CI datapoint reads, stale
references left behind by the two debt retirements, and a debt file that now contradicts
its own evidence.

## Warnings

### WR-01: The one CI datapoint is recorded without the baseline that shows `-n 4` bought nothing on the runner

**File:** `bench/RESULTS.md:2800-2815`, `Makefile:79-85`, `docs/architecture/decision_log.md:1663-1680`
**Issue:** `### CI run` states `927 passed in 203.16s` at `-n 4` with coverage and calls it
"context ... never the bar". It does not say what CI read before the phase. The same file
set already holds that number: 15-RESEARCH line 483 cites `927 passed in 193.21 s` serial,
CI run 37116412012 (I re-read that run's log: `927 passed in 193.21s`; the `test (3.12)`
job ran 10:26:16 to 10:30:16, 240 s, its `make verify` step 231 s). The pinned run's job
took 267 s and its `make verify` step 259 s. So on CI the phase's change (`-n 4`, `--cov`,
two more dev packages) made pytest about 10 s slower and the job about 27 s slower, while
every other site reports a 3.6x gain that exists only on the 12-core dev host. The Makefile
comment justifies the clamp as protecting the 4-vCPU runner and L34's title says the gate
"runs on eight workers"; neither is measured on that runner, and the sweep's own finding
(the serial suite already uses 4.2-4.5 cores, so extra workers on 4 vCPUs have nothing to
add) predicts exactly this. L08: the record leaves the reader to assume CI got at least
no worse. Coverage overhead (5.8 % at `-n 8` on the dev host) explains part, not all, of
the 10 s, and one run each is thin, which is the reason to state both rather than drop one.
**Fix:** In `### CI run`, add the prior run's figures beside the new ones: serial, no
coverage, `193.21s` pytest / 240 s job (run 37116412012) against `-n 4 --cov`, `203.16s` /
267 s (run 37181871926), stated as two single runs on different commits, no verdict.
Then either (a) give CI its own measured worker count (`PYTEST_WORKERS` env on the
`make verify` step, with an A/B on the runner), or (b) leave `-n 4` and amend L34 to say the
gain is dev-host-only and CI did not speed up. Change the L34 title from "runs on eight
workers" to "runs on up to eight workers".

### WR-02: Two retirements left a false statement and two dangling links

**File:** `docs/architecture/gear-maths/tests.md:28-29`, `docs/architecture/decision_log.md:775`
**Issue:** `gear-maths/tests.md` still says "The module has no coverage floor in the gate
yet (L14 note, and `docs/tech_debt/active/2026-09-21-no-coverage-floor.md`)". That file was
`git mv`'d to `resolved/` in `2aadcea`, and the gate now has `fail_under = 96`. The
sentence is false and its link is dead. The same pass left `decision_log.md:775` (the L27/
regression-fixture entry) pointing at
`docs/tech_debt/active/2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md` and calling it
the live `must`-severity debt; it moved to `resolved/` in `454af54` and the sentence now
describes a problem CI no longer has. L34 lists "the five sites that repeated ~11 s"
as swept, but nobody grepped for the moved filenames. The only hits outside `.planning/`
and `resolved/` are these two (checked with `grep -rn`).
**Fix:** In `tests.md`, replace the bullet with the real state, for example: "The gate
holds a coverage floor over the whole package, `fail_under = 96` (L34); `calc.py` has no
floor of its own." In the decision log, the entry is append-only history, so leave its text
and add a trailing bracket `[resolved: see L34 and docs/tech_debt/resolved/2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md]`
or accept the stale path and say so in L34.

### WR-03: The commit-timeout debt now contradicts its own recovery argument and trigger

**File:** `docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md:20-31`, `docs/tech_debt/INDEX.md` (row for this file)
**Issue:** The edited Context says a warm hook "is itself over the 30 s limit now, not only
a cold one" (63-64 s measured). But "Why it matters" still argues the recovery "works
because the retry runs warm", and "Next step" still says to revisit "when an executor's
warm retry also times out". By the file's own new evidence that trigger has fired: a warm
run takes 2x the timeout, so every SDK commit in this repo times out, not the first of a
session. The title, the INDEX row ("on a cold cache") and `Severity: nice` all still
describe the pre-phase situation. The phase made this worse in practice (the hook went
from the claimed ~11 s to ~64 s) and filed the consequence as a paragraph inside a `nice`
item. By the standing rules a deferred item whose trigger has fired is `must`.
**Fix:** Retitle ("... kills the pre-commit `make verify` hook, warm or cold"), update the
INDEX row's title and trigger, rewrite "Why it matters" so it no longer relies on a warm
retry passing, and raise `Severity:` to `must` (INDEX row moves to the `must` group), or
state in the file why the trigger has not fired.

### WR-04: "None of the five `-n 8 --cov` runs" undercounts the record it cites

**File:** `bench/RESULTS.md:2764-2768`, `docs/tech_debt/active/2026-10-04-worker-coverage-flush-is-sometimes-lost.md:25-30`
**Issue:** The tally says all three serial full `--cov` runs lost `pool.py` 63-67/222 and
"none of the five `-n 8 --cov` runs that printed `pool.py` did", "eight runs, no cause".
The same RESULTS file prints a sixth `-n 8 --cov` run that shows `pool.py ... 100.00%`
(the 71-item deselect run in `### Proposed cuts`, line 2676, which kept
`test_a_real_worker_builds_and_downloads`), and the CI run later printed `pool.py 100.00%`
at `-n 4`. The debt file is the artifact someone uses to decide whether the loss is
serial-only, and it carries the stale count; it also was not updated after 15-05 even
though its Next step compares `-n` settings. The floor is unaffected (the loss is 0.22
points inside a 0.99-point margin), so this is a record defect, not a gate defect.
**Fix:** Say "six" `-n 8 --cov` runs (add the deselect run), nine runs counting 15-05's CI
`-n 4` run (`pool.py` 100.00 %, 22 missed), or reword to "of the `-n` runs that printed
`pool.py`, none lost the lines". Keep the serial 3 of 3 as the headline.

## Info

### IN-01: `requirements.txt` and `packaging.md` do not say the closure is now also CI's constraint file

**File:** `docs/architecture/packaging.md:11-16, 41`, `requirements.txt:1-5`
**Issue:** The file header and the packaging doc still describe `requirements.txt` as "the
exact package closure the Docker image installs" and say "`pyproject.toml` keeps loose
ranges for developer environments". The new second job (CI constraint, so `make lock` now
moves CI's kernel and the fixture tripwire) is written only in `ci.yml`, a test docstring
and L34. Someone regenerating the closure reads the one place that does not warn them. The
`~64 s warm` in packaging.md's gate block also drops the "12-core dev host, `-n 8` with
coverage" qualifier that README, HOW_TO_DEVELOP and `.pre-commit-config.yaml` carry.
**Fix:** One sentence in each: "also pip's constraint file for CI's `make verify` (L34); a
`make lock` that moves `cadquery`/`cadquery-ocp` needs `make fixture.regen`", and restore
the host qualifier on the `~64 s` figure. The generator's header text belongs to
`docker/refresh-requirements.sh`, not a hand edit.

### IN-02: `PYTEST_WORKERS` clamp trusts `getconf` blindly

**File:** `Makefile:85`
**Issue:** `n=$$(getconf _NPROCESSORS_ONLN)` has no fallback. If `getconf` is absent, or
prints a non-number on a platform that lacks the name, the arithmetic reads `n` as 0 and
the recipe silently runs `-n 0` (serial, with the measured 4x cost) with no message.
`_NPROCESSORS_ONLN` also ignores cgroup CPU quotas and affinity, so inside a CPU-limited
container the clamp the comment sells ("keeps it from oversubscribing a smaller host")
does not engage. Neither bites on macOS or the GitHub runner, which is why it was not seen.
**Fix:** `PYTEST_WORKERS ?= $(shell w=8; n=$$(nproc 2>/dev/null || getconf _NPROCESSORS_ONLN); [ "$$n" -ge 1 ] 2>/dev/null || n=1; echo $$(( n < w ? n : w )))`.
`nproc` is not on stock macOS, hence the `||` chain. Or state in the comment that the clamp
is host-CPU-count only.

### IN-03: L34 names two different "Before" numbers

**File:** `docs/architecture/decision_log.md:1663-1669`
**Issue:** L34 says "The Before row is the serial run with coverage, 244.59 s (C0)", then
reports the delta as -165.435 s / 3.60x, which is against the re-measured serial A mean
228.99 s, not 244.59 s (against C0 it would be -181.0 s, 3.85x). `bench/RESULTS.md`
`### Before and after` explains the swap; L34 does not, and the human's verbatim answer
(`before=244.59`) sits two sentences from a figure that does not use it.
**Fix:** Add a clause: "15-04 re-measured the same configuration as A (228.99 s mean) in
alternation with B, so the delta is against A; C0's 244.59 s was taken before `-n 8` went in
and is 15.6 s slower than the A mean, cause untested."

### IN-04: `make clean` leaves coverage data, and two concurrent gates in one tree share it

**File:** `Makefile:210-214`, `.gitignore:25-29`
**Issue:** `parallel = true` makes `.coverage.<host>.<pid>.<rand>` files in the repo root
on every `--cov` run (a `.coverage` file is there now). `.gitignore` hides them, but
`clean` removes `.pytest_cache` and `.ruff_cache` and not these, so stale data from a
killed run survives a "clean". Also, pytest-cov combines every `.coverage.*` in the
working directory, so a pre-commit hook and a hand-run `make verify` in the same checkout
(the R1 rule in `bench/RESULTS.md` forbids exactly that for load reasons) can combine or
erase each other's files and move the printed total. Not reproducible as a failure here.
**Fix:** Add `rm -f .coverage .coverage.*` to `clean`; optionally set
`[tool.coverage.run] data_file` under a per-run temp dir if concurrent gates in one tree
are meant to be supported.

---

_Reviewed: 2026-10-04_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
