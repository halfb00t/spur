---
phase: 07-foundation-generalized-edge-selection-regression-fixture
reviewed: 2026-09-26T07:10:05Z
depth: standard
files_reviewed: 14
files_reviewed_list:
  - bench/RESULTS.md
  - docs/architecture/decision_log.md
  - docs/architecture/solid-model/tactics.md
  - docs/tech_debt/active/2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md
  - docs/tech_debt/INDEX.md
  - Makefile
  - src/spur/calc.py
  - src/spur/model.py
  - tests/regression/capture.py
  - tests/regression/corpus.py
  - tests/regression/pre_v0_2.json
  - tests/regression/test_pre_v0_2.py
  - tests/test_calc.py
  - tests/test_model.py
findings:
  critical: 0
  warning: 1
  info: 0
  total: 1
status: issues_found
---

# Phase 07: Code Review Report

**Reviewed:** 2026-09-26T07:10:05Z
**Depth:** standard
**Files Reviewed:** 14
**Status:** issues_found

## Summary

Reviewed the diff between `c640ed8` and `HEAD` for the two plans of this phase: the
pre-v0.2 regression fixture (07-01: `tests/regression/capture.py`, `corpus.py`,
`pre_v0_2.json`, `test_pre_v0_2.py`, plus doc/debt records) and the generalized edge
selection work (07-02: `calc.bore_rim_limit`, `model.BORE_RIM_SLACK`, the two
`BuildError` guards in `_bore_rim_edges`/`_groove_floor_edges`).

Verified, not just read:
- `make verify` passes clean (289 tests, ruff, mypy --strict, import-linter) on the
  current tree.
- `calc.py` still imports no `cadquery`/`OCP` (checked import list directly; the
  import-linter contract also confirms this).
- Ran the tripwire from `bench/RESULTS.md` verbatim (`m._bore_rim_edges = lambda *a,
  **k: []` against `tests/regression`): reproduced exactly the claimed **32 failed, 53
  passed in 13.46-13.48s**, and `git status --porcelain -- src tests` was empty
  afterward, confirming the claim that the monkeypatch is in-process only.
- Cross-checked `pre_v0_2.json`'s provenance header and record count (44 records: 39
  `built`, 5 `mate-only`) against `capture.py`'s and `corpus.py`'s logic and against the
  claims in `bench/RESULTS.md`/`L26` — all match.
- Traced `bore_rim_limit(p)` / `BORE_RIM_SLACK` through `_bore_rim_edges` and
  `_groove_floor_edges` into `_build_checked`'s `except BuildError: raise` and app.py's
  (unchanged, out-of-scope) `except BuildError -> HTTPException(422, ...)` to confirm the
  new guards actually reach the API as documented, not swallowed by the generic
  `except Exception` catch-all's "try smaller fillets or chamfers" relabeling.
- Confirmed the arithmetic in `bench/RESULTS.md`'s new "Regression fixture cost" section
  (mean/delta figures) and the 44/39/5 and 85-test-count claims.

One process note, not a finding: running `tests/regression/capture.py` directly during
this review (to check it runs cleanly) rewrote `pre_v0_2.json`'s `git_head` field as a
side effect of the script doing exactly what it's designed to do. That edit was reverted
(`git checkout -- tests/regression/pre_v0_2.json`) before this report was written; the
working tree is clean.

No Critical issues found. One Warning: a latent, currently-non-triggering key-collision
gap in `tests/regression/corpus.py`'s deduplication logic that runs against the module's
own stated invariant ("a record that disappears is a guarantee that disappears").

## Warnings

### WR-01: A mate-case key can silently collide with another case's key, dropping a corpus record with no error

**File:** `tests/regression/corpus.py:210-227`

**Issue:** `cases()` guards against a literal duplicate `entry.tag` (`seen_tags`, raises
`ValueError`), but the *synthesized* mate-case key, `f"{entry.tag}+mate={entry.mate}"`
(line 225), is never checked against `seen_tags` or against other synthesized keys. If
any future entry's `tag` happens to end in a substring that collides with another
entry's synthesized mate key — e.g. a base entry literally tagged
`"foo+mate=40"` and a *different* entry tagged `"foo"` with `mate=40` — both write to
`result["foo+mate=40"]` (line 216-218 for the base case, line 227 for the mate case).
The second write silently overwrites the first in the `result` dict; no exception, no
test failure at the point of collision. `test_the_fixture_records_every_corpus_set`
(`tests/regression/test_pre_v0_2.py`) only compares the fixture against whatever
`cases()` currently returns, so it cannot detect a case that `cases()` itself already
merged away before the fixture was ever regenerated against it — the corpus would
silently carry one fewer guarantee than `ENTRIES` implies, without a `make fixture.regen`
diff or a red test ever naming it.

This does not currently trigger — none of the 78 entries in `ENTRIES` has a tag
containing `"+mate="` — but it is exactly the failure mode this module's own docstring
warns against ("Do not narrow, shorten or re-pick it -- a record that disappears is a
guarantee that disappears... a record that disappears is a guarantee that disappears").
A collision here is invisible by construction, which is a sharper version of the same
risk the module otherwise defends against by convention (D-05 in L26) rather than by a
check.

**Fix:** Track synthesized mate keys in `seen_tags` (or a second set) before writing, and
raise the same `ValueError` on collision as the literal-tag case does:

```python
mate_key = mate_keys.get((p, entry.mate))
if mate_key is None:
    case_key = f"{entry.tag}+mate={entry.mate}"
    if case_key in result:
        raise ValueError(f"synthesized case key collides with an existing entry: {case_key}")
    mate_keys[(p, entry.mate)] = case_key
    result[case_key] = Case(params=entry.params, mate=entry.mate, sources=[entry.tag])
else:
    result[mate_key].sources.append(entry.tag)
```

---

_Reviewed: 2026-09-26T07:10:05Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
