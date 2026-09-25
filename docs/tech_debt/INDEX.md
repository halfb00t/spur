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
| must | [The concurrent latency bar was waived, not demonstrated](active/2026-09-23-concurrent-latency-bar-waived.md) | 02-05 writes L17/L18, the harness or the machine changes, or any run reads above 2.45x |
| nice | [CadQuery's `Shape` typing forces four `type: ignore`s](active/2026-09-21-cadquery-shape-typing.md) | CadQuery narrows its own return types, or the pipeline is touched anyway |
| nice | [No server-side cancellation on client abort](active/2026-09-21-no-server-side-cancellation.md) | slider-dragging actually saturates the queue |
| nice | [No coverage floor in the gate](active/2026-09-21-no-coverage-floor.md) | after one measured baseline run |
| nice | [The service has no authentication](active/2026-09-21-no-authentication.md) | the moment it is bound to anything but localhost |
| nice | [Enji Guard not connected](active/2026-09-21-enji-guard-not-connected.md) | owner decides they want continuous AI audit |

## Resolved

| Item | Resolved in |
|---|---|
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
