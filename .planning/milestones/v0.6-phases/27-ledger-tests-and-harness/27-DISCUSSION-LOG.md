# Phase 27: Ledger Tests and Harness - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md. This log preserves the alternatives considered.

**Date:** 2026-10-20
**Phase:** 27-ledger-tests-and-harness
**Areas discussed:** Group floor of 3, 19 IN-01/02 in model.py, Linux member listing

---

## Group floor of 3

| Option | Description | Selected |
|--------|-------------|----------|
| Count 3, comment only | `MIN_GROUP_MEMBERS` stays 3; the comment names uvicorn, the resource tracker and one worker; still a real non-vacuity check, 3 live before and 0 after | ✓ |
| Force a second concurrent build | Two overlapping builds so both pool workers spawn, then require 4; costs a build and adds a timing dependency | |
| Count 3 + check by command | Keep 3 and also assert a uvicorn, a resource_tracker and at least one worker by command line; `ps` parsing differs between macOS and Linux | |

**User's choice:** Count 3, comment only.
**Notes:** This closes the debt item's open "name the tracker, or force a second build" question with neither.

---

## 19 IN-01/02 in model.py

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, pass `rm` through | `_chamfer_tips` receives `rm`; the "one answer" comment becomes true; guarded by the 44-record fixture; the test_model.py:899 and :926 patches change shape | ✓ |
| No, skip with a reason | Row `skipped`: `root_mode` is pure, so the answers cannot diverge; zero `src/spur/` diff | |
| Comment only | Correct `_build`'s comment to what is true; no behaviour change | |

**User's choice:** Yes, pass `rm` through.
**Notes:** Before the question, Claude pointed out that two test patches change, not one as the roadmap says: `:899` (`_chamfer_tips`) and `:926` (`tip_chamfer_effective`).

---

## Linux member listing

First question:

| Option | Description | Selected |
|--------|-------------|----------|
| Print it in the harness | Print the group's members before the kill; claimed the phase PR's CI log would carry the Linux reading | ✓ (withdrawn) |
| One-off throwaway CI run | Temporary print on a throwaway PR, read once, reverted | |
| Print only on failure | Listing in the `pytest.fail` message only | |

**Correction:** Claude withdrew its own recommendation after the answer. pytest captures a passing test's output, `make verify` runs without `-s`, and under xdist the output stays in the worker. A green CI log would never show the print; Phase 26's `twin selectors:` lines were absent from both post-merge `main` logs.

Second question:

| Option | Description | Selected |
|--------|-------------|----------|
| One-off throwaway CI run | Temporary print plus a throwaway PR running only the browser test with `-s -n0` (26-02's shape); cite the run id; close unmerged | ✓ |
| Permanent: property + summary hook | `record_property` plus a `pytest_terminal_summary` hook; every green CI run records the group; about 15 lines plus a test | |
| Permanent: CI artifact | Write the listing to a file and upload it from ci.yml; changes ci.yml, and artifacts expire | |

**User's choice:** One-off throwaway CI run.

---

## Claude's Discretion

- The slug test's seed, draw count and stratification method, within the millisecond budget.
- The throwaway PR's exact workflow edit.
- The replacement patch form for the two `test_model.py` lambdas.
- No call-count test for D-03; the fixture and the existing chamfer tests are the proof.

## Deferred Ideas

None.
