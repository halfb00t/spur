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
| must | [An int field accepts `0-0`, a token the number box blanks](active/2026-10-28-int-fields-accept-a-blanked-zero-minus-zero-token.md) | L49's rule is next touched, an int field's default moves off 0, or an int field with a lower bound below 0 is added |
| must | [The shaft profile-shift cap refuses shifts DIN 5480-1 allows as exceptions at larger tooth counts](active/2026-10-26-shaft-shift-range-narrower-than-din-5480-exceptions.md) | Part 2, or the copy's exception table, gives the z-dependent limits |
| must | [The internal form-diameter construction sits above DIN 5480-2's d_Ff1 maximum on most rows](active/2026-10-26-form-diameter-construction-exceeds-din5480-2-maximum.md) | Phase 34 makes the pin-contact guard live |
| nice | [The pre-commit hook's name and L36's amendment still say "five heavy files"](active/2026-10-27-pre-commit-hook-name-and-l36-still-say-five-heavy-files.md) | `.pre-commit-config.yaml` is next edited |
| nice | [FIT_PATTERN accepts deviation letters and tolerance classes outside DIN 5480-1 Table 7/9](active/2026-10-26-fit-pattern-accepts-fits-outside-the-standards-set.md) | Phase 34 takes the fit tables |
| must | [`gear.unchanged` runs git and the schema probe with no timeout, inside the pre-commit hook](active/2026-10-23-gear-unchanged-has-no-timeout-on-git-or-probe.md) | the hook next stalls, or `scripts/gear_unchanged.py` is next touched |
| must | [`gear.unchanged` accepts any local `v0.6` tag, including a lightweight or moved one](active/2026-10-23-gear-unchanged-accepts-a-lightweight-or-moved-v0-6-tag.md) | `scripts/gear_unchanged.py` is next touched, or any CI path is found that can see a local tag |
| must | [CI's `ubuntu-latest` moves to Ubuntu 26 on 2026-10-19; the browser test's install has only run on 24.04](active/2026-10-10-ubuntu-latest-migrates-to-ubuntu-26-on-19-october.md) | the first `ubuntu-latest` run of `ci` whose job log holds `Image: ubuntu-26.04` (Phase 29's own PR and the v0.6 milestone-close PR count; read all three jobs whole against `bench/RESULTS.md` `### Ubuntu 26.04, pre-classified (26-02)` before any fix; Phase 29 closed 2026-10-22, trigger not fired) |
| must | [A whole-suite `make verify` hung near the end with no failure, no crash report and no survivor](active/2026-10-10-make-verify-hung-at-98-percent-with-no-failure.md) | the next `make verify` that neither passes nor fails: keep its whole log (`-v` and the faulthandler dump now name the test; the item's runbook covers a stall after the last test), or `BuildPool.shutdown` is next touched |
| nice | [No server-side cancellation on client abort](active/2026-09-21-no-server-side-cancellation.md) | slider-dragging actually saturates the queue |
| nice | [A full run sometimes loses BuildPool's worker coverage, moving the total by 0.22 points](active/2026-10-04-worker-coverage-flush-is-sometimes-lost.md) | a `make verify` reads under the floor with no code change, or `BuildPool.shutdown`/`_run_with_timeout` is next touched after Phase 17 (Phase 17 touched it; not observed in 43/43 runs) |
| nice | [The service has no authentication](active/2026-09-21-no-authentication.md) | the moment it is bound to anything but localhost |
| nice | [Enji Guard not connected](active/2026-09-21-enji-guard-not-connected.md) | owner decides they want continuous AI audit |
| nice | [Eleven composed-solid cutout volumes are 6 dp literals asserted at rel=1e-6](active/2026-10-03-composed-cutout-volume-literals-pinned-at-six-places.md) | the CadQuery/OCP kernel pair is bumped, or a composed-solid cutout row is next re-pinned |
| nice | [Phase 7's Nyquist audit lists 3 tasks with no named automated command](active/2026-10-05-phase-07-nyquist-gaps.md) | the covered file is next touched (`tests/regression/capture.py`, `tests/regression/test_pre_v0_2.py`, `src/spur/model.py` bore-rim selection, or `bench/RESULTS.md`'s fixture-cost section) |
| nice | [`Resolved in:` shas in the debt ledger point at squash-merged branch commits, not at `main`](active/2026-10-05-resolved-in-shas-point-at-squashed-branch-commits.md) | a `Resolved in:` sha fails to resolve in a clone, a remote `gsd/phase-*` branch is deleted, or the retirement rule in CLAUDE.md is next edited |
| nice | [A wedged worker holds process exit until it finishes or is killed](active/2026-10-06-wedged-worker-holds-process-exit.md) | `BuildPool.shutdown` is next touched, or a graceful shutdown is observed to hang |
| nice | [The English-throughout rule has no check in the gate](active/2026-10-05-english-throughout-has-no-check-in-the-gate.md) | a non-English line next lands in a tracked file, or `no-fake-done` is next edited |
| nice | [A pytest-xdist worker segfaults in OCCT at interpreter exit](active/2026-10-09-xdist-worker-segfaults-in-occt-at-exit.md) | the human names the command that crashed every run on 2026-10-09 07:19–08:36 (command, cwd, venv, environment), or a `BuildPool` worker exit ever logs SIGSEGV |
| nice | [`_wait_until_parked` spins `page.evaluate("0")` with no pause until a route parks](active/2026-10-15-wait-until-parked-spins-without-a-pause.md) | `_wait_until_parked` is next touched |
| nice | [Nothing pins that `_build` passes its own `rm` to `_chamfer_tips`](active/2026-10-20-nothing-pins-that-build-passes-its-own-rm-to-chamfer-tips.md) | `_build` or `_chamfer_tips` is next touched, or a public per-build cost counter exists |
| nice | [Phase 18's review leftovers and Phase 10's hard-coded chamfer bound](active/2026-10-21-phase-18-review-info-findings-deferred.md) | the next phase that changes the trochoid / hob-root maths in calc.py or its tests; for 10 IN-01, the next edit of bench/tip_chamfer_spike.py or the tip_chamfer bound |

## Resolved

| Item | Resolved in |
|---|---|
| [The shaft has no contention row: its heaviest build is measured alone, never under concurrent requests](resolved/2026-10-27-shaft-contention-row.md) | 3ee9a0a docs(bench): the heaviest shaft under ten concurrent requests (D-19) |
| [A link token the number box blanks but the API accepts builds a non-default part under a blank box](resolved/2026-10-21-an-accepted-link-token-builds-under-a-blank-box.md) | 69c1aa3 fix(api): refuse a link number the box would blank (WR-02, L49) |
| [Two guard lines in `shaft_model.build_shaft` are reached by no passing test](resolved/2026-10-27-shaft-model-two-guard-lines-no-passing-test-reaches.md) | 49021f5 test(shaft): pin the one-valid-solid guard and drop a dead re-raise |
| [The shaft's volume guard accepts a chamfer that was never cut](resolved/2026-10-27-shaft-volume-guard-accepts-an-uncut-chamfer.md) | 3e1eded fix(shaft): refuse a chamfer the kernel never cut (end-face read-back) |
| [Widening `Part` to the shaft must type `model._build_checked`, `model._write_export` and `records._gear_fields` in the same change](resolved/2026-10-23-parts-one-line-widening-claim-is-false.md) | 4018de8 feat(model): build and export a shaft through the one kernel doorway (Part widens) |
| [DIN 5480 anchor rows beyond Part 1 are missing: the Phase 31 checkpoint passed only partly](resolved/2026-10-26-din5480-anchor-rows-beyond-part-1-are-missing.md) | 45b6565 test(31): anchor four DIN 5480-2 rows and close the Part 1 anchor gap |
| [tip_chamfer_effective prints 0.0 for a chamfer that was not cut, because its null-gate reads the request](resolved/2026-10-21-tip-chamfer-effective-gate-reads-the-request.md) | `6497c28` — see the file's own `Resolved in:` field |
| [Phase 19 code review: the root_fillet label finding is still deferred](resolved/2026-10-09-phase-19-review-info-findings-deferred.md) | `61154d1` — see the file's own `Resolved in:` field |
| [A link with an invalid enum value loads a blank select and builds the default part](resolved/2026-10-10-root-shape-bogus-loads-a-blank-select.md) | `cb93d4e` — see the file's own `Resolved in:` field |
| [The environ pin raises `KeyError` on a module-level `from os import environ`](resolved/2026-10-20-environ-pin-raises-keyerror-on-module-level-import.md) | `27628ef` — see the file's own `Resolved in:` field |
| [The group floor of 3 is recorded as "two pool workers"; the live group is uvicorn, the resource tracker and one worker](resolved/2026-10-10-group-floor-of-3-is-not-two-pool-workers.md) | `99e2b7d` — see the file's own `Resolved in:` field |
| [The launch failure message names a stamp that skips the install](resolved/2026-10-10-launch-failure-message-names-a-stamp-that-skips-the-install.md) | `a393e50` — see the file's own `Resolved in:` field |
| [`stop_group` reads `ps` before it signals, so a failed `ps` leaves the server group alive](resolved/2026-10-10-stop-group-reads-ps-before-it-signals.md) | `a7c5f78` — see the file's own `Resolved in:` field |
| [A failed-build name test passes only while no other test downloads the same gear](resolved/2026-10-15-failed-build-name-test-depends-on-cache-order.md) | `c47bfc4` — see the file's own `Resolved in:` field |
| [`slug()` totality is not guarded in the gate, and it runs inside failure-record paths](resolved/2026-10-15-slug-totality-is-not-guarded-in-the-gate.md) | `345ee08` — see the file's own `Resolved in:` field |
| [The twin-selectors fix has not yet been read on a `main` run](resolved/2026-10-15-twin-selectors-fix-awaits-the-post-merge-main-read.md) | docs(26): record the post-merge main read and retire the twin-selectors read item — see the file's own `Resolved in:` field |
| [`make pr.land` merges the pushed PR head without checking the local branch is pushed](resolved/2026-10-20-pr-land-merges-a-stale-head.md) | fix(pr_land): refuse a local head branch the PR head does not carry — see the file's own `Resolved in:` field |
| [`make test-image` collects test files that read files the image does not hold](resolved/2026-10-10-test-image-collects-tests-that-read-host-files.md) | fix(26): make test-image mounts what its tests read and ignores only host-only files by name — see the file's own `Resolved in:` field |
| [A reentrant `resource_tracker` cleanup warning sometimes fails `make verify`](resolved/2026-10-06-resource-tracker-flake-fails-the-gate.md) | fix(26): collect the pool tests' cycles outside the resource tracker lock, located from a forced-GC reproduction — see the file's own `Resolved in:` field |
| [The browser step "twin selectors" reds `main` CI with one extra request](resolved/2026-10-15-twin-selectors-step-reds-main.md) | fix(26): take the twin-selectors baseline after the link's own STL request and settle past the debounce — see the file's own `Resolved in:` field |
| [The shared-recipe hook pin reads the caller's `PYTEST_ARGS`, so `make verify PYTEST_ARGS="--ignore=..."` fails it](resolved/2026-10-10-hook-pin-reads-the-callers-pytest-args.md) | test(26): the hook pins read the Makefile, not the caller's PYTEST_ARGS — see the file's own `Resolved in:` field |
| [A hex bore warns that the default bore_d and bore_flat are ignored, on every hex link](resolved/2026-10-11-hex-bore-warns-about-default-bore-fields.md) | fix(calc): name only the hex-ignored bore fields set away from their defaults — see the file's own `Resolved in:` field |
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
