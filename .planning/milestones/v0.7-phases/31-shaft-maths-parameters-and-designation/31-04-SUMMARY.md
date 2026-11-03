---
phase: 31-shaft-maths-parameters-and-designation
plan: 04
subsystem: shaft-maths
tags: [din5480, designation-codec, parser-refusals, seen-red-once, tech-debt]

requires:
  - phase: 31-shaft-maths-parameters-and-designation
    provides: FIT_PATTERN and the formulas (31-01), the oracle (31-02), ShaftDimensions through measure_over_pins (31-03)
provides:
  - din5480.DESIGNATION_MAX_LENGTH, Designation, DesignationError (token), format_designation, parse_designation
  - ShaftDimensions.designation, set by derive_shaft
  - parts.py docstring naming Phase 32 and the three gear-typed internals; the debt item re-targeted
  - five codec guards seen red once, recorded in bench/RESULTS.md
affects: [31-05, 31-06, phase-32, phase-33]

plan_head_before: a75d59f68fd1f7412c285fdb9981597dfe788e1e
plan_head_after: bc62e5996194959eae7864e6bcbff7957a8c87ac

actuals:
  tokens: 3500    # chars/4 over the added lines of src, tests, bench, pyproject and docs (14001 chars); the five red logs are evidence, not code
  tasks: 3
  commits: 4      # measured: git rev-list --count a75d59f..HEAD, before this SUMMARY's own commit

tech-stack:
  added: []
  patterns:
    - "a codec whose classes are all ASCII and whose every step is a fullmatch behind a length bound, so no float() or int() sees unchecked text"
    - "an error that carries the refused token as an attribute, so a caller names it without parsing a message"

key-files:
  created:
    - .planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-04-red-g-format.log
    - .planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-04-red-unicode-digit.log
    - .planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-04-red-no-length-bound.log
    - .planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-04-red-spaces.log
    - .planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-04-red-fractional-teeth.log
  modified:
    - src/spur/din5480.py
    - src/spur/shaft_calc.py
    - src/spur/parts.py
    - pyproject.toml
    - tests/test_din5480.py
    - tests/test_shaft_calc.py
    - bench/RESULTS.md
    - docs/tech_debt/active/2026-10-23-parts-one-line-widening-claim-is-false.md
    - docs/tech_debt/INDEX.md

key-decisions:
  - "Codec lives in din5480.py: the designation is the standard's notation; Designation's field names equal ShaftParams' four so Phase 33 builds ShaftParams(**d._asdict())"
  - "Length bound 64 code points, checked before any regex; the longest real designation is about 29 characters"
  - "D-14 debt route is option 2: re-target the item to Phase 32 and keep it active; splitting would need a resolved file carrying its own commit's sha"

requirements-completed: [REQ-designation-codec, REQ-shaft-params, REQ-shaft-basic-dims]

coverage:
  - id: D1
    description: "Every derived shaft carries its designation in the canonical form W 25x1.25x18x8f, and the default's designation parses back to ShaftParams()"
    requirement: "REQ-designation-codec"
    verification:
      - kind: unit
        ref: "tests/test_shaft_calc.py#test_the_default_shaft_is_designated_w_25x1_25x18x8f"
        status: pass
      - kind: unit
        ref: "tests/test_din5480.py#test_the_designation_prints_in_one_canonical_form"
        status: pass
    human_judgment: false
  - id: D2
    description: "The parser accepts exactly D-05's four variants, round-trips eight parameter sets, and refuses 25 unparseable strings naming the bad token; a designation over 64 characters is refused before any parsing without echoing the input"
    requirement: "REQ-designation-codec"
    verification:
      - kind: unit
        ref: "tests/test_din5480.py#test_the_designation_parser_accepts_the_listed_variants"
        status: pass
      - kind: unit
        ref: "tests/test_din5480.py#test_the_designation_round_trips"
        status: pass
      - kind: unit
        ref: "tests/test_din5480.py#test_an_unparseable_designation_is_refused_naming_its_token"
        status: pass
      - kind: unit
        ref: "tests/test_din5480.py#test_a_designation_longer_than_the_bound_is_refused_before_parsing"
        status: pass
    human_judgment: false
  - id: D3
    description: "The twelve ShaftDimensions keys are pinned in Phase 33's dims row order, and two derive_shaft calls return equal warnings"
    requirement: "REQ-shaft-basic-dims"
    verification:
      - kind: unit
        ref: "tests/test_shaft_calc.py#test_the_shaft_dimensions_keys_are_fixed"
        status: pass
    human_judgment: false
  - id: D4
    description: "Five codec guards seen red once (:g printer, \\d digits, no length bound, whitespace tolerated, fractional teeth truncated), reverted and recorded"
    requirement: "REQ-designation-codec"
    verification:
      - kind: other
        ref: "bench/RESULTS.md ### Seen red once (Phase 31), five 31-04 rows; investigation/31-04-red-*.log"
        status: pass
    human_judgment: false
  - id: D5
    description: "parts.py names Phase 32 and the three internals with Part unchanged; the debt item is re-targeted to Phase 32 and its INDEX row moved in the same commit"
    verification:
      - kind: other
        ref: "tests/test_seam.py, make lint-imports (Contracts: 10 kept, 0 broken.), make gear.unchanged, grep checks of the task 3 acceptance criteria"
        status: pass
    human_judgment: false

duration: 12min
completed: 2026-10-24
status: complete
---

# Phase 31 Plan 04: The Designation Codec Summary

**Every shaft prints `W 25x1.25x18x8f` in the shortest round-tripping numbers, and a strict ASCII-only parser reads it back (or refuses naming the token), with five codec guards seen red once and `parts.py` plus its debt item re-targeted to Phase 32**

## Performance

- **Duration:** 12 min
- **Started:** 2026-10-24T11:26Z
- **Completed:** 2026-10-24T11:38Z (before this SUMMARY's own commit)
- **Tasks:** 3
- **Files modified:** 14 (4 source and config, 2 test, `bench/RESULTS.md`, the debt item and INDEX, 5 logs)

## Accomplishments

- `derive_shaft(ShaftParams()).designation == "W 25x1.25x18x8f"`; `parse_designation("W25X1,25X18X8f")` returns `Designation(reference_d=25.0, module=1.25, teeth=18, fit='8f')`; `ShaftParams(**parse_designation(d)._asdict()) == ShaftParams()`.
- The grammar, in order: length bound 64; empty input; the type letter (`N` gets its own hub sentence, any other first word is named); one optional ASCII space; `re.split(r"[xX]", rest, maxsplit=3)` into four tokens; `[0-9]` number patterns for d_B and module, `[0-9]+` for teeth, `FIT_PATTERN` for the fit (the same constant `ShaftParams.fit` uses); only then `float()` and `int()`.
- 39 designation tests in `tests/test_din5480.py` (4 variants, 8 round trips, 25 refusals, the canonical form, the bound) plus the default-shaft test; `-k designation` over both files is 40 passed.
- The `ShaftDimensions` key order is pinned as Phase 33's dims rows.
- `parts.py` says Phase 32 widens `Part` in the change that makes model build a shaft, and names `_build_checked`, `_write_export` and `_gear_fields`. `Part = GearParams` is unchanged, and the pyproject C4 comment now says Phase 32.

## Measurements

- **Gate:** `make verify`: `2349 passed in 210.87s (0:03:30)`, exit 0, at the final tree before this SUMMARY (ruff clean, mypy `--strict` clean, `Contracts: 10 kept, 0 broken.`). 31-03's gate was `2308 passed`; the 41 added are this plan's tests (40 designation tests plus the key-order test, minus none removed). Wall time is not compared: load was not controlled. 31-06 prices the phase's gate delta.
- **Plan-level checks:** `make verify.fast` passed at each of the four commits; `make lint-imports` reads `Contracts: 10 kept, 0 broken.`; `make gear.unchanged` reads `gear.unchanged: tests/regression/, .github/workflows/ci.yml and /api/schema (8723 bytes) are byte-equal to v0.6`; `tests/test_seam.py` 6 passed.
- **Red runs:** each ran with `PYTHONDONTWRITEBYTECODE=1` and every `__pycache__` under `src` and `tests` purged before the run and after the revert (the 31-01 method). Counts: `:g` printer `1 failed, 38 passed`; `\d` digits `1 failed, 38 passed`; no length bound `1 failed, 38 passed`; whitespace stripped `5 failed, 34 passed` (spaced catalogue form, double space after W, no-break space after W, trailing newline, trailing space); fractional teeth `1 failed, 38 passed`. `git status --porcelain -- src tests` was empty after each revert and after the bench commit, which deletes 0 lines of `bench/RESULTS.md` (`5 0`).
- **Task 3 acceptance:** `git show --stat` of `bc62e59` lists exactly parts.py, pyproject.toml, the debt item and INDEX.md; pyproject and INDEX each `1 1` in numstat; model.py, records.py, pool.py and app.py are byte-identical across it.

## Task Commits

1. **Task 1 (tracer): print and parse the DIN 5480 designation** - `3d05f96` (feat)
2. **Task 2: the designation's variants, refusals and round trip** - `f4657c2` (test), then **the codec guards seen red once** - `04e7e5b` (docs)
3. **Task 3: Phase 32 widens Part, and the internals it must type** - `bc62e59` (docs)

The tracer gate: the tracer's `<verify>` is automated-only and `human_verify_mode` is `end-of-phase`; its checks (pytest `946 passed`, ruff, mypy, `make no-fake-done`, contracts) passed before the commit, and the same files ran green again with Task 2's tests. `Tracer verified end-to-end`, expansion went ahead.

## Decisions Made

- **Hub sentence rule:** a first word that is `N`, or `N` followed by a non-letter, gets the hub sentence with token `N`; any other word that does not start with `W` (for example `NOPE`, `DIN`, `w`) is named as itself.
- **Refusal token for a wrong split:** when the text does not split into four parts, the token is the whole text after `W` and its optional space (so `×` and a full-width x refuse naming the whole `25×1.25×18×8f`), as the plan's table lists.
- **Phase 33 handoff:** the 422 for an unparseable designation reads `DesignationError.token` (at most 64 characters, and the length refusal echoes nothing); a designation input builds `ShaftParams(**d._asdict())`, which gives the boundary's own refusals; a designation that contradicts an explicit field is Phase 33's 422 per L03. The renderer shows the token as text.
- **Phase 32 handoff:** the debt item `2026-10-23-parts-one-line-widening-claim-is-false.md` stays active, trigger "Phase 32 widens `Part`". In the change that makes model build a shaft, widen `Part` and type or dispatch `_build_checked`, `_write_export` and `_gear_fields`, then resolve the item in that commit.
- **Filed items:** no new debt or idea item. If the human later wants the spaced catalogue form (`W 25 x 1,25 x 18 x 8f`) accepted, that is an idea (D-21); it is refused today and pinned as a refusal row.

## Files Created/Modified

- `src/spur/din5480.py` - the codec: `DESIGNATION_MAX_LENGTH`, `Designation`, `DesignationError`, `_number`, `format_designation`, `parse_designation`
- `src/spur/shaft_calc.py` - `ShaftDimensions.designation` between `measure_over_pins` and `warnings`, set by `derive_shaft`
- `src/spur/parts.py`, `pyproject.toml` - docstring and C4 comment name Phase 32
- `tests/test_din5480.py` - `REFUSED_DESIGNATIONS`, `ROUND_TRIPS` and five designation tests
- `tests/test_shaft_calc.py` - the default's designation test and the key-order test
- `bench/RESULTS.md` - five `31-04` rows appended, none removed
- `docs/tech_debt/active/2026-10-23-parts-one-line-widening-claim-is-false.md`, `docs/tech_debt/INDEX.md` - re-targeted to Phase 32
- `.planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-04-red-*.log` - five whole red logs

## Deviations from Plan

### Auto-fixed Issues

None - plan executed exactly as written, with these wording choices the plan did not fix:

- The plan's table lists the no-break-space row as `("W 25x1.25x18x8f", " 25")`, which reads like a plain space; the row is a no-break space after W (`"W 25x1.25x18x8f"`, token `" 25"`), since a plain-space row would duplicate the double-space row. The non-ASCII rows are written as `\u` escapes because ruff's RUF001 refuses the literal characters.
- The refusal messages' wording is mine; each quotes the token with `!r` and says what it should have been.

**Total deviations:** 0 auto-fixed. **Impact on plan:** none.

## Issues Encountered

None.

## Known Stubs

None.

## Threat Flags

None. The designation text is the new untrusted input; T-31-09 to T-31-11 are mitigated and each guard was seen red once.

## Next Phase Readiness

Ready for 31-05, the copy checkpoint.
