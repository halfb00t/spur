# Tech debt index

Known-bad code, missing tests, brittle paths, risky shortcuts, deliberate skips. One file
per item in `active/`; move to `resolved/` (never delete) when fixed, in the same commit
as the fix.

Severity (grep-able `Severity:` field):

- **blocker** — data corruption, silent partial success, source-of-truth violation,
  paid-API drain risk. Fix before shipping.
- **must** — correctness or maintainability hygiene, or deferred work with a named
  trigger.
- **nice** — cosmetic, speculative, honour-system.

## Active

| Severity | Item | Trigger to revisit |
|---|---|---|
| must | [A link with an invalid enum value loads a blank select and builds the default part](active/2026-10-10-root-shape-bogus-loads-a-blank-select.md) | Phase 23 or 24 touches buildForm's enum rendering, or a user reports a link that loaded a blank select (pinned as today's behaviour by the browser test's step `root_shape=bogus as today`) |
| must | [A whole-suite `make verify` hung near the end with no failure, no crash report and no survivor](active/2026-10-10-make-verify-hung-at-98-percent-with-no-failure.md) | the next `make verify` that neither passes nor fails (keep its whole log, then rerun with `-v --durations=20`), or `BuildPool.shutdown` is next touched |
| nice | [The shared-recipe hook pin reads the caller's `PYTEST_ARGS`, so `make verify PYTEST_ARGS="--ignore=..."` fails it](active/2026-10-10-hook-pin-reads-the-callers-pytest-args.md) | `tests/test_hooks.py` is next touched, or a narrowed `make verify` is next wanted |
| nice | [`make test-image` collects test files that read files the image does not hold](active/2026-10-10-test-image-collects-tests-that-read-host-files.md) | `make test-image` is next run for real (Docker up), or a test that reads a host-only file is next added |
| nice | [No server-side cancellation on client abort](active/2026-09-21-no-server-side-cancellation.md) | slider-dragging actually saturates the queue |
| nice | [A full run sometimes loses BuildPool's worker coverage, moving the total by 0.22 points](active/2026-10-04-worker-coverage-flush-is-sometimes-lost.md) | a `make verify` reads under the floor with no code change, or `BuildPool.shutdown`/`_run_with_timeout` is next touched after Phase 17 (Phase 17 touched it; not observed in 43/43 runs) |
| nice | [The service has no authentication](active/2026-09-21-no-authentication.md) | the moment it is bound to anything but localhost |
| nice | [Enji Guard not connected](active/2026-09-21-enji-guard-not-connected.md) | owner decides they want continuous AI audit |
| nice | [Eleven composed-solid cutout volumes are 6 dp literals asserted at rel=1e-6](active/2026-10-03-composed-cutout-volume-literals-pinned-at-six-places.md) | the CadQuery/OCP kernel pair is bumped, or a composed-solid cutout row is next re-pinned |
| nice | [Phase 7's Nyquist audit lists 3 tasks with no named automated command](active/2026-10-05-phase-07-nyquist-gaps.md) | the covered file is next touched (`tests/regression/capture.py`, `tests/regression/test_pre_v0_2.py`, `src/spur/model.py` bore-rim selection, or `bench/RESULTS.md`'s fixture-cost section) |
| nice | [`Resolved in:` shas in the debt ledger point at squash-merged branch commits, not at `main`](active/2026-10-05-resolved-in-shas-point-at-squashed-branch-commits.md) | a `Resolved in:` sha fails to resolve in a clone, a remote `gsd/phase-*` branch is deleted, or the retirement rule in CLAUDE.md is next edited |
| must | [A reentrant `resource_tracker` cleanup warning sometimes fails `make verify`](active/2026-10-06-resource-tracker-flake-fails-the-gate.md) | the next `make verify` failure, with its whole log kept (as 19-01 did) so the test and worker localise the fix; or, if none by Phase 20 planning or the next milestone's start, whole-suite loops of `make test` at `-n 8 --cov` and `-n 8 --no-cov` (re-deferred 2026-10-09 by the human at Phase 19's 19-03: 0 of 60 two-file isolation loops reproduced it, so xdist and coverage were not separated; every occurrence, four so far, came from a whole-suite run; escalated to `must` by the human 2026-10-06) |
| nice | [A wedged worker holds process exit until it finishes or is killed](active/2026-10-06-wedged-worker-holds-process-exit.md) | `BuildPool.shutdown` is next touched, or a graceful shutdown is observed to hang |
| nice | [The English-throughout rule has no check in the gate](active/2026-10-05-english-throughout-has-no-check-in-the-gate.md) | a non-English line next lands in a tracked file, or `no-fake-done` is next edited |
| nice | [A pytest-xdist worker segfaults in OCCT at interpreter exit](active/2026-10-09-xdist-worker-segfaults-in-occt-at-exit.md) | the human names the command that crashed every run on 2026-10-09 07:19–08:36 (command, cwd, venv, environment), or a `BuildPool` worker exit ever logs SIGSEGV |
| nice | [Phase 19 code review: four info findings deferred](active/2026-10-09-phase-19-review-info-findings-deferred.md) | `model.py`, `bench/trochoid_part.py` or the `DIMS` table is next touched (IN-01, IN-02, IN-04); the L34 bar is re-set under a new `Lxx` (IN-03) |

## Resolved

| Item | Resolved in |
|---|---|
| [A same-slot timeout cleanup race produces an undocumented 500 instead of a 503](resolved/2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md) | `0628182` and `7af75af` — see the file's own `Resolved in:` field |
| [gsd's 30 s commit timeout kills the pre-commit `make verify` hook, warm or cold](resolved/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md) | `c06749d` — see the file's own `Resolved in:` field |
| [`.planning/intel/` still repeats two figures the live docs have since corrected](resolved/2026-10-05-intel-context-repeats-superseded-figures.md) | docs(intel): correct the Python floor and gate duration; index L17–L35 — see the file's own `Resolved in:` field |
| [`make no-fake-done` matches nothing on macOS: `git grep -E` has no `\b`](resolved/2026-10-05-no-fake-done-scan-is-blind-on-macos.md) | fix(gate): match unfinished-work markers with -w so the scan runs on macOS — see the file's own `Resolved in:` field |
| [CAD builds block the event loop](resolved/2026-09-21-cad-builds-block-the-event-loop.md) | `daeb284` — see the file's own `Resolved in:` field |
| [No structured logging anywhere](resolved/2026-09-21-no-structured-logging.md) | `21b8fe4` — see the file's own `Resolved in:` field |
| [The info contract is `dict[str, Any]`](resolved/2026-09-21-untyped-info-contract.md) | `013900d` — see the file's own `Resolved in:` field |
| [The ship-note's CI skip token leaks into the squash-merge commit and skips CI on `main`](resolved/2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md) | `fac76f5` — see the file's own `Resolved in:` field |
| [`test_a_wedged_build_is_terminated_and_its_worker_replaced` flakes on the GitHub runner](resolved/2026-09-25-test-pool-wedged-worker-flakes-on-the-github-runner.md) | `ae052f8` — see the file's own `Resolved in:` field |
| [A cached solid's `.BoundingBox()` reads wrong after it has been STL-exported](resolved/2026-09-24-shared-solid-cache-corrupts-later-boundingbox.md) | `655ec52` — see the file's own `Resolved in:` field |
| [The commit-msg hook trusts a cut line typed by hand in an editor session](resolved/2026-09-25-commit-msg-hook-trusts-a-hand-typed-cut-line.md) | `e46ed34` — see the file's own `Resolved in:` field |
| [`make pr.land` judges a run by the listed jobs only, never by the run's own conclusion](resolved/2026-09-25-pr-land-admits-a-run-with-a-failing-unlisted-job.md) | `9ca8320` — see the file's own `Resolved in:` field |
| [The required-jobs drift test reads job ids, so a `name:` override slips past it](resolved/2026-09-25-required-jobs-drift-test-ignores-job-name-overrides.md) | `0573319` — see the file's own `Resolved in:` field |
| [`make pr.land` reports "a skip token reached main" for any run it failed to observe](resolved/2026-09-25-pr-land-blames-a-skip-token-for-any-missed-post-merge-run.md) | `e4345a4` — see the file's own `Resolved in:` field |
| [A round bore's chamfer reach is not checked against the root circle](resolved/2026-09-26-round-bore-chamfer-reach-is-not-checked.md) | `4b6a5b9` — see the file's own `Resolved in:` field |
| [A 200-tooth tip chamfer narrows SPUR_BUILD_TIMEOUT's margin](resolved/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md) | `89304e2` — see the file's own `Resolved in:` field |
| [The heaviest spoke row's arithmetic total with Phase 10's tip-chamfer row crosses 30 s under load](resolved/2026-09-29-spoke-le-arithmetic-total-crosses-30s-under-load.md) | `89304e2` — see the file's own `Resolved in:` field |
| [`cli.md` claims exit 2 where `cmd_export` exits 1](resolved/2026-09-28-cli-md-claims-exit-2-where-cmd-export-exits-1.md) | `0deb25a` — see the file's own `Resolved in:` field |
| [The concurrent latency bar was waived, not demonstrated](resolved/2026-09-23-concurrent-latency-bar-waived.md) | `6709953` — see the file's own `Resolved in:` field |
| [The root fillet's straight lead-in can reach above the pitch circle](resolved/2026-09-28-root-lead-in-can-reach-above-the-pitch-circle.md) | `825095f` — see the file's own `Resolved in:` field |
| [The filleted-spoke removed-volume proof has no closed-form cross-check](resolved/2026-09-29-filleted-spoke-volume-proof-pinned-not-derived.md) | `61e1bea` — see the file's own `Resolved in:` field |
| [No coverage floor in the gate](resolved/2026-09-21-no-coverage-floor.md) | `2aadcea` — see the file's own `Resolved in:` field |
| [CI resolves the kernel from an unpinned range; the fixture pins one kernel exactly](resolved/2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md) | `839dfea` — see the file's own `Resolved in:` field |
| [CadQuery's `Shape` typing forces five `type: ignore`s](resolved/2026-09-21-cadquery-shape-typing.md) | `4f7e8fe` — see the file's own `Resolved in:` field |
