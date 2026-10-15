# `slug()` totality is not guarded in the gate, and it runs inside failure-record paths

Severity: must
Status: active
Date: 2026-10-15
Source: phase 22 code review, finding WR-01 (`.planning/milestones/v0.5-phases/22-download-name-carries-the-root/22-REVIEW.md`); untriaged until the v0.5 milestone audit, filed at the human's call at the v0.5 close
Related files:
- src/spur/params.py:267 (`slug()` calls `calc.root_mode`)
- src/spur/records.py:180 (`build.failed` / `queue.refused` records call `slug()`)
- src/spur/app.py:496 (the download header)
- tests/test_trochoid.py:225 (`test_the_download_name_follows_the_root_root_mode_builds`)

## Context
Since Phase 22 (L40), `slug()` is no longer a trivial f-string: it runs `profile`, `cutter`,
`_junction` and `_root_curve` through `root_mode` to decide whether the part ends
`_trochoid`. It is called while building the record of a failed or refused build. L40 (D-02)
accepts that `slug()` stays total on the evidence of a one-off sweep, which is a command, not a
test, so nothing in `make verify` re-proves it. The new tests prove 6 pure rows and 2
`build.failed` rows; the refusal reasons `bracket degenerate`, `curve invalid` and
`tooth severed` are never driven through `slug()`. The reviewer's 60k-case fuzz found no
failure, so this is a regression guard, not a live bug.

## Why it matters
If a future `calc` change makes `root_mode` raise for some validated parameter set, the
exception replaces the original `BuildError` on the failure path: the response becomes a 500
and the real cause is lost from the record.

## Next step
Revisit when `calc.root_mode`, `cutter`, `_junction` or `_root_curve` is next changed, or when
any response or record shows an exception raised from `slug()`. The fix: a seeded test beside
`test_the_download_name_follows_the_root_root_mode_builds` that validates a few hundred random
`root_shape="trochoid"` requests (or a slice of `bench.trochoid.sweep_cases()` covering every
refusal reason) and asserts `slug().endswith("_trochoid") == (root_mode(...).mode == "trochoid")`
with no exception; milliseconds, so it belongs in the commit slice.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
