# Phase 26: Gate Fails With a Cause - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-15
**Phase:** 26-gate-fails-with-a-cause
**Areas discussed:** Flake fix + proof runs, Hang evidence shape, test-image rule, Ubuntu 26 PR logistics

---

## Flake fix + proof runs

**Q: Which fix lands in tests/test_pool.py?**

| Option | Description | Selected |
|--------|-------------|----------|
| B + C | Autouse teardown `gc.collect()` plus `del manager` in the 3 producers | ✓ |
| B only | STACK's primary pick; cycle stays, freed outside the lock | |
| C only | Zero cost; relies on remembering the pattern | |

**Q: Acceptance run size and shape?**

| Option | Description | Selected |
|--------|-------------|----------|
| 10+10 two-file, interleaved | `test_pool.py` + `test_api.py`, `-n 8 --cov`, ~10 min | ✓ |
| Whole-suite 5+5 `make test` | Same population as real occurrences; ~35 min | |
| Both, capped at 60 min | Most evidence, longest | |

**Q: Does the forced-GC harness stay in the repo?**

| Option | Description | Selected |
|--------|-------------|----------|
| Commit as a gate test | Seen red without B+C; permanent regression guard | ✓ |
| Commit opt-in, not in gate | Reproducible by hand, no guard | |
| Scratchpad only | STACK's original plan | |

**Q: Twin-selectors repeat count?**

| Option | Description | Selected |
|--------|-------------|----------|
| 20 local + 1 CI main run | ~15 min local plus the post-merge main run | ✓ |
| 50 local | ~40 min | |
| 10 local + delayed-route proof | Repeats as smoke only | |

---

## Hang evidence shape

**Q: Where does `-v` go?**

| Option | Description | Selected |
|--------|-------------|----------|
| Every make verify | Evidence on when the hang happens | ✓ |
| CI only | Local hangs stay anonymous | |
| Opt-in variable | Nobody turns it on in advance | |

**Q: Which reading sets `faulthandler_timeout`?**

| Option | Description | Selected |
|--------|-------------|----------|
| 120 s now, confirm on CI | Local reading recorded; CI `--durations` read and recorded; change only if CI slowest × 2 > 120 s | ✓ |
| Wait for CI reading first | Extra CI round-trip | |
| Local reading only | Risks dumps on healthy slow CI tests | |

**Q: Does the stalled test stay in the repo?**

| Option | Description | Selected |
|--------|-------------|----------|
| Throwaway, log kept | Temp file, run once, log in `investigation/` | ✓ |
| Committed guard in gate | Subprocess pytest on a sleeping test; ~5–10 s | |
| Pin only, in test_hooks.py | Static pin, no behaviour test | |

**Q: Gate cost measurement rigor?**

| Option | Description | Selected |
|--------|-------------|----------|
| 3+3 interleaved, load recorded | Escalate only if delta > 5 % | ✓ |
| Phase 25 protocol (L43) | Quiet host, 5+5 | |
| One after-reading | Confounded by load | |

---

## test-image rule

**Q: How is the fix chosen?**

| Option | Description | Selected |
|--------|-------------|----------|
| Pre-commit rule, checkpoint on surprise | Mount `bench/` + `scripts/` :ro, `PYTHONPATH=/app/src:/app`, `--ignore` make/git/Dockerfile/.github readers; stop if any red has another cause | ✓ |
| Always checkpoint after run | One extra stop | |
| Exclude by name | Drops `test_calc.py`, `test_trochoid.py` | |

**Q: How is the skip reason carried?**

| Option | Description | Selected |
|--------|-------------|----------|
| `--ignore` + recipe comment | Matches the existing browser-test pattern | ✓ |
| `skipif` in the test files | Reason in `-rs`; may hide a broken host checkout | |
| Both | | |

**Q: What keeps it honest after the fix?**

| Option | Description | Selected |
|--------|-------------|----------|
| Static pin only | Extend `test_hooks.py`'s test-image pin; CI run deferred | ✓ |
| Add test-image to CI now | New job, scope beyond the item | |
| Nothing beyond the fix | | |

---

## Ubuntu 26 PR logistics

**Q: What does the throwaway PR branch from?**

| Option | Description | Selected |
|--------|-------------|----------|
| main @ v0.5 tag | Reads the shipped tree on the new image | ✓ |
| Phase branch after hook pin | Mixes in an unshipped change | |
| Phase branch after twin-selectors fix | Breaks the fixed order, risks the clock | |

**Q: How does the hand-off work?**

| Option | Description | Selected |
|--------|-------------|----------|
| Executor prepares, you push | Checkpoint with exact push/PR lines | ✓ |
| Executor pushes on your OK | | |
| You do all of it | | |

**Q: If the clock is missed?**

| Option | Description | Selected |
|--------|-------------|----------|
| Record the miss, keep going | SC5 "not met as written" with reason | ✓ |
| Block the phase until classified | | |
| Drop SC5 if missed | Roadmap edit | |

---

## Claude's Discretion

- Hook-pin fix shape (roadmap: planner's call).
- Twin-selectors wait mechanism; folding 24 CX-05 and 21 IN-04a.
- `--durations` count.
- Location of the forced-GC gate test.

## Deferred Ideas

- Run `make test-image` in CI.
- `faulthandler_exit_on_timeout` after the first captured hang (already a Future Requirement).
