---
phase: 07-foundation-generalized-edge-selection-regression-fixture
reviewed: 2026-09-26T08:11:41Z
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
  warning: 5
  info: 0
  total: 5
status: issues_found
---

# Phase 07: Code Review Report

**Reviewed:** 2026-09-26T08:11:41Z
**Depth:** standard
**Files Reviewed:** 14
**Status:** issues_found

## Summary

Scope: `calc.bore_rim_limit`, the two `model.py` edge selectors' new `BuildError`
guards, `BORE_RIM_SLACK`, and the new `tests/regression/` fixture pair (`corpus.py`,
`capture.py`, `pre_v0_2.json`, `test_pre_v0_2.py`), plus the docs/decision-log/Makefile
entries this phase added. Diffed against `c640ed8..HEAD` per file.

The core behaviour change is sound and matches its own decision-log entry (L26): both
selectors now raise a named `BuildError` on an empty match while their feature is on,
the raise is not caught by `_build_checked`'s catch-all (`except BuildError: raise`
precedes the relabeling branch), `bore_rim_limit(p)` reduces to `bore_radius(p)` exactly
as `calc.py`'s new unit test proves, and the fixture is unchanged by this plan's second
half (`git diff --exit-code tests/regression/pre_v0_2.json`, confirmed by re-reading
`bench/RESULTS.md`'s own record of that check). No critical or security-relevant defect
was found.

Five warnings remain, all quality/test-integrity issues rather than production-code
bugs: one re-verified from the prior review (a corpus key-collision gap with no live
trigger today) and four independently confirmed from the Codex evidence lane (a fixture
coverage gap that would hide a missing solid snapshot, two test-assertion gaps that let
the selector tests pass on a differently-wrong selection, a documentation instruction
that contradicts the fixture's own regeneration rule, and a numerically wrong order-of-
magnitude claim repeated in both `model.py` and the decision log). Every Codex claim was
independently re-read against the cited source before being accepted; none were rejected
outright, though two are combined below because they cite the same test region.

## Warnings

### WR-01: `corpus.cases()`'s synthesized mate-case key is never checked for collision

**File:** `tests/regression/corpus.py:210-230`
**Issue:** `seen_tags` (line 210-212) rejects a duplicate literal `entry.tag`, but the
mate branch (lines 222-230) synthesizes a second dict key, `case_key =
f"{entry.tag}+mate={entry.mate}"` (line 225), and writes `result[case_key] = ...`
(line 227) unconditionally — with no check against `result`'s existing keys or against
`base_keys`. Nothing stops that synthesized string from colliding with another entry's
literal `tag` (a base case) or with a different `(params, mate)` pair's own synthesized
key, should one ever be added. A collision silently overwrites the earlier `Case`,
dropping a `Case` (and, downstream, a fixture record and its regression coverage) with
no error — the exact failure mode `docs/tech_debt/active/...` and L26 exist to prevent,
just from the corpus builder itself rather than the kernel. No current `ENTRIES` tag
happens to collide, so this has no live trigger today, but the risk is unguarded going
into Phases 8-12 where more entries will be added.
**Fix:** After computing `case_key`, assert it is not already a key of `result` (or of
`seen_tags`), e.g. `if case_key in result: raise ValueError(f"corpus key collision: {case_key}")`
before the assignment on line 227.

### WR-02: The fixture's coverage test cannot catch a missing `solid` snapshot (external: codex)

**File:** `tests/regression/test_pre_v0_2.py:31-33, 55-61`
**Issue:** Read the cited lines directly: `_SOLID_RECORDS` (lines 31-33) is built by
filtering `_RECORDS.items()` on `"solid" in record`, so a non-mated record with no
`"solid"` key silently drops out of `test_a_pre_v0_2_parameter_set_builds_the_same_solid`'s
parametrization — no failure, no skip marker, nothing. `test_the_fixture_records_every_
corpus_set` (lines 55-61) is the only test that walks every corpus case and compares it
against the fixture, but its `fixture_index`/`corpus_index` tuples are `(params,
mate_teeth, sources)` only — `"solid" in record` is never part of the comparison. A
record whose `solid` key is missing or was dropped (a `capture.py` bug, or a hand-edited
JSON, the exact scenario the test's own docstring — "A corpus edit with no regeneration,
or a hand-edited JSON, must go red here" — says it exists to catch) still matches on
params/mate/sources and passes this test, while silently losing its geometry coverage.
This directly undercuts L26's stated guarantee that "a change to the pre-v0.2 part can
no longer ship unnoticed" for exactly the un-mated (built) records that guarantee is
about.
**Fix:** Extend `test_the_fixture_records_every_corpus_set`'s comparison to include
whether a `solid` key is present for every non-mated case, e.g. fold
`"solid" in record` into `fixture_index`'s tuple keyed against `case.mate is None` from
`corpus_index`, or add a standalone assertion that every record with `mate_teeth is
None` also has `"solid" in record`.

### WR-03: Selector-matrix test proves counts, not edge identity, for the recess-floor selector — and permits duplicate rim edges from one end face (external: codex)

**File:** `tests/test_model.py:44-134` (selector-matrix test and its follow-up loop,
approximately lines 99-134 in the current file)
**Issue:** Read the cited test. `floor_count = len(_groove_floor_edges(bare, rr,
heights))` (around line 90) only ever compares a count against the expected `floor` int
— there is no equivalent to the bore-rim follow-up loop (`for e in
_bore_rim_edges(...): assert ... radius() == pytest.approx(bore_radius(bare_p), ...)`)
that would check a selected floor edge's radius or z against the groove geometry
independently of `_groove_floor_edges`'s own filter. A regression that made the selector
match the same number of wrong-but-coincidentally-equal-count edges (e.g. groove-mouth
circles instead of groove-floor circles, which share radii with the floor circles by
construction) would pass silently, contradicting the test's own docstring claim that
"the bore-rim chamfer and the recess-floor fillet each pick their own edges, never each
other's." Separately, the bore-rim follow-up loop (`for e in _bore_rim_edges(bare,
bare_p): ... assert min(abs(a.z), abs(a.z - bare_p.face_width)) < TOL`) checks each
selected edge sits on *an* end face but never asserts the selection spans *both* end
faces (e.g. via `{round(min(abs(a.z), abs(a.z - face_width))) for e in edges}` or an
explicit per-face count) — a selector bug that returned both rim circles from z=0 and
missed z=face_width entirely would still satisfy `rim_counter == Counter({"CIRCLE": 2})`
and the per-edge z check.
**Fix:** Add an independent identity check for floor edges (e.g. assert each selected
edge's `radius()` is in `rr` and its `startPoint().z` is in `heights`, mirroring the
bore-rim loop), and add an explicit per-end-face count or a set-of-z-values assertion to
the bore-rim loop so a selection concentrated on one face is distinguishable from one
that spans both.

### WR-04: The fixture's own module docstring tells contributors to regenerate after fixing an ordinary regression, contradicting D-03 (external: codex)

**File:** `tests/regression/test_pre_v0_2.py:14-16`
**Issue:** Read verbatim: "A red test here in Phases 8-12 is that phase's bug, never
this fixture's (D-03). Fix the regression, then run `make fixture.regen` in its own
commit stating what moved and why -- never as part of a feature commit." Read against
L26 (`docs/architecture/decision_log.md:766-775`), D-03 restricts regeneration to
exactly two triggers — "a cadquery/cadquery-ocp pin bump (L12), or a deliberate contract
change carrying its own Lxx" — and states explicitly "A red fixture in Phases 8–12 is,
by definition, a bug in that phase, not a reason to regenerate." The test module's own
instruction reads as an unconditional two-step recipe ("fix the regression, then
regen") for any red test in that range, with no carve-out limiting `fixture.regen` to
the two sanctioned triggers. A contributor following the docstring literally after an
ordinary code fix — rather than reading D-03's stricter rule first — could regenerate
the fixture around a still-incomplete fix, laundering a real regression into the new
frozen baseline; that is exactly the failure mode L26 exists to prevent.
`tests/regression/capture.py:1, 5-8`'s own docstring gets this right ("During v0.2 the
file changes only in its own commit... a cadquery/cadquery-ocp pin bump under L12, or a
deliberate contract change carrying a new Lxx"), which makes `test_pre_v0_2.py`'s looser
phrasing an internal inconsistency between the two files, not just a loose reading of
L26.
**Fix:** Reword `test_pre_v0_2.py`'s docstring to match `capture.py`'s: fixing a
regression means making the code match the frozen fixture again, full stop; regenerate
only for the two D-03 triggers, each in its own commit. E.g. replace the last sentence
with "Fix the code until this test is green again; `make fixture.regen` is for a
cadquery/cadquery-ocp pin bump (L12) or a deliberate, `Lxx`-carrying contract change
only — never to launder a fix."

### WR-05: `BORE_RIM_SLACK`'s margin over the measured kernel tolerance is off by two orders of magnitude, in both the code comment and the decision log (external: codex)

**File:** `src/spur/model.py:50-55`; also `docs/architecture/decision_log.md:781-784`
**Issue:** `model.py:50-55` reads: "`BORE_RIM_SLACK = 0.01` ... 10 microns, not TOL: it
must clear the kernel's post-boolean vertex/edge tolerance -- measured 1e-7 mm ... by
three orders of magnitude". `decision_log.md:781-784`'s L26 entry makes the same claim:
"`model.BORE_RIM_SLACK` (0.01 mm) is the selection slack, measured at 1e-7 mm ... and
kept three orders of magnitude below that" (loosely worded, but referring to the same
0.01-vs-1e-7 comparison). Computed directly: `0.01 / 1e-7 = 1e5`, i.e. `10**5` — five
orders of magnitude, not three. The adjacent claim in the same sentences — "forty times
under `MIN_WALL` (0.4 mm)" — is correct (`0.4 / 0.01 = 40`); only the kernel-tolerance
comparison is wrong, and it is wrong identically in both places, meaning one was very
likely copied from the other without the arithmetic being re-checked. Per this
project's own standing rule, a comment carrying the measurement that forced a design
choice is expected to carry the *right* measurement (CLAUDE.md: "Comments explain *why*,
and carry the measurement or the constraint that forced the choice"); this one doesn't,
even though the chosen value (0.01 mm) itself remains a defensible margin regardless of
whether it's counted as three or five orders of magnitude above 1e-7 mm.
**Fix:** Change "by three orders of magnitude" to "by five orders of magnitude" in
`src/spur/model.py:53` and the equivalent phrase in `decision_log.md:781-784`. The log
is append-only (L26 itself: "the log is append-only by policy, and nothing above it
changes" is stated for L01-L25's entries generally) — if L26 is treated as still open
for a same-day correction before this phase ships, fix it in place; otherwise add a
one-line superseding correction rather than leaving the wrong number as the log's
permanent record of this margin.

---

_Reviewed: 2026-09-26T08:11:41Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
