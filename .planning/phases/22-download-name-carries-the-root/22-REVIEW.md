---
phase: 22-download-name-carries-the-root
reviewed: 2026-10-11T00:00:00Z
depth: standard
files_reviewed: 11
files_reviewed_list:
  - bench/RESULTS.md
  - docs/architecture/decision_log.md
  - docs/architecture/http-api.md
  - docs/ideas/INDEX.md
  - docs/ideas/retired/2026-10-08-download-name-carries-the-root-shape.md
  - src/spur/calc.py
  - src/spur/params.py
  - tests/browser_session.py
  - tests/test_api.py
  - tests/test_browser.py
  - tests/test_trochoid.py
findings:
  critical: 0
  warning: 2
  info: 3
  total: 5
status: issues_found
---

# Phase 22: Code Review Report

**Reviewed:** 2026-10-11
**Depth:** standard
**Files Reviewed:** 11
**Status:** issues_found

## Summary

The one production change is `GearParams.slug()` (`src/spur/params.py:190-210`): a `_trochoid` suffix exactly when `calc.root_mode` returns `mode == "trochoid"`. The rest is `calc.py` docstring text, tests, docs and bench readings.

I checked the following and found them sound:

- The local import is the same pattern `_feasible` already uses (`params.py:180`). The import-linter contracts allow it, because `calc` imports no `cadquery` or `OCP`.
- The `root_mode` call arguments match the other three call sites: `model.py:773`, `calc.py:354` and `calc.py:1086`. L40's line citations are correct.
- No cache is keyed by slug. The export cache key is `(params, fmt, quality, encoding)` (`app.py:401`), and the header is built per response (`app.py:496`).
- The slug only ever contains digits, `.`, `_` and fixed words, so the `Content-Disposition` header is not injectable.
- Totality. The claim is that `slug()` never raises on a validated `GearParams`. I fuzzed it with:
  - 60,000 seeded random requests over the full field ranges with `root_shape="trochoid"`, of which 49,223 validated and 5,470 were named `_trochoid`;
  - a 447-case corner grid over the extremes of teeth, module, pressure angle, shift, backlash and `root_fillet`, including the 32.14 and 33.07 degree tip-land limits.

  No call raised.
- The numbers in the Phase 22 bench section are consistent. The mean of 3.56, 3.20 and 1.13 is 2.63. The slowest step per run is named correctly. The L40 cross-references resolve.

No correctness or security defects in the shipped behaviour. The findings below are about how well the totality guarantee and the new tests are guarded.

## Warnings

### WR-01: `slug()` totality is unguarded in CI and the function now runs inside failure-record paths

**File:** `src/spur/params.py:206-210` (callers `src/spur/app.py:496`, `src/spur/records.py:180`)
**Issue:**

- `slug()` used to be a trivial f-string. It now runs `profile`, `cutter`, `_junction` and `_root_curve`. It is called while building `build.failed` and `queue.refused` records (`records.py:180`), that is, on the path that reports a failure.
- If `root_mode` ever raises for some validated parameter set, a future `calc` change is enough, the exception replaces the original `BuildError` and the response becomes a 500 with the real cause lost.
- L40 (D-02) accepts this on the evidence of a one-off sweep. The sweep is "a command, not a test", so nothing in `make verify` re-proves it.
- The new tests prove 6 pure rows and 2 `build.failed` rows. The refusal reasons `bracket degenerate`, `curve invalid` and `tooth severed` are never exercised through `slug()`.
- My own 60k-case fuzz found no failure today, so this is a regression guard, not a live bug.

**Fix:** Add a small seeded test beside `test_the_download_name_follows_the_root_root_mode_builds`. It would validate a few hundred random `root_shape="trochoid"` requests, call `slug()` on each, and assert `slug().endswith("_trochoid") == (root_mode(...).mode == "trochoid")`. Alternatively, reuse a slice of `bench.trochoid.sweep_cases()` that covers every reason. A seeded 300-case loop is milliseconds.

### WR-02: `test_a_failed_build_records_the_name_of_the_part_it_would_have_been` depends on no other test requesting the same gear

**File:** `tests/test_api.py:1117-1146`
**Issue:**

- The test only gets a 422 from the raising backend if the module-level byte cache (`spur.app._EXPORTS`) has no entry for the request.
- The guarantee is a comment: "25 teeth trochoid is downloaded by no other test ... 33.5 degree tip-land gear ...".
- Any later test that downloads 25-tooth trochoid or the 33.5 degree gear at `quality=preview` makes this one fail with a 200 instead of a 422, in an order-dependent way. Per-process caches mean it also changes under xdist scheduling.
- The same hand-maintained uniqueness is repeated in the `test_a_root_shape_link_is_served_with_the_root_it_cut` docstring.

**Fix:** Make isolation explicit instead of by convention. Clear the cache at the top of the test, or vary a field no other test uses, such as `face_width=7.7`, so the key is private:

```python
from spur.app import _EXPORTS
_EXPORTS.clear()   # before client.get(...)
```

If clearing is rejected because the cache is shared module state, add a unique `face_width` to both rows' `fields`.

## Info

### IN-01: The bore-off field block is duplicated in two test files

**File:** `tests/test_api.py:1120-1122`, `tests/test_trochoid.py:208`
**Issue:** `bore_d=0, bore_flat=0, bore_chamfer=0, recess_sides="none"` appears as an inline literal in `test_api.py` and as `_BORE_OFF` in `test_trochoid.py`. If the defaults move, the two copies drift independently.
**Fix:** Keep one in a shared test helper, or leave as is and accept the duplication. Low value either way.

### IN-02: Ragged docstring reflow in `serve_stl_from`

**File:** `tests/browser_session.py:287-295`
**Issue:** The edit left a short line, "because it needs ... builds one more part. The bytes must be served", followed by a very short "and not the", then a long line. The text is correct but reads as a hand-edited paragraph.
**Fix:** Re-wrap the paragraph to the file's usual width.

### IN-03: L40 quotes the best-case reading of the new step as its cost

**File:** `docs/architecture/decision_log.md` (L40, "The browser proof" paragraph); `bench/RESULTS.md` Phase 22 section
**Issue:**

- L40 states that `step download name` "read 1.13 s ... beside `step first build drawn` at 2.93 s".
- The three readings taken on the committed head are 3.56, 3.20 and 1.13 s. The bench section itself says the spread is unexplained.
- So 1.13 s is the low outlier of a bimodal sample. L40 defers to 22-02's numbers, which softens this, but the log entry is the locked record and carries the optimistic figure alone.

**Fix:** In L40, give the range ("1.13 to 3.56 s over the 22-02 readings") or point to the bench subsection without a figure of its own. The 45 s `BUILD_WAIT_MS` conclusion is unaffected.

---

_Reviewed: 2026-10-11_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
