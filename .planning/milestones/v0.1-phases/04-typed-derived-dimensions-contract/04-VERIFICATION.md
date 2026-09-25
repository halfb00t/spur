---
phase: 04-typed-derived-dimensions-contract
verified: 2026-09-24T15:06:19Z
status: passed
score: 4/4 must-haves verified
covered_files: [".planning/REQUIREMENTS.md", ".planning/phases/04-typed-derived-dimensions-contract/04-01-PLAN.md", ".planning/phases/04-typed-derived-dimensions-contract/04-01-SUMMARY.md", ".planning/phases/04-typed-derived-dimensions-contract/04-02-PLAN.md", ".planning/phases/04-typed-derived-dimensions-contract/04-02-SUMMARY.md", ".planning/phases/04-typed-derived-dimensions-contract/04-03-PLAN.md", ".planning/phases/04-typed-derived-dimensions-contract/04-03-SUMMARY.md", "docker/smoke.py", "docs/CODING_VALUES.md", "docs/architecture/decision_log.md", "docs/architecture/gear-maths/errors_and_logging.md", "docs/architecture/gear-maths/implementation.md", "docs/architecture/gear-maths/strategy.md", "docs/architecture/gear-maths/tactics.md", "docs/architecture/http-api.md", "docs/tech_debt/INDEX.md", "docs/tech_debt/resolved/2026-09-21-untyped-info-contract.md", "pyproject.toml", "src/spur/app.py", "src/spur/calc.py", "src/spur/cli.py", "src/spur/params.py", "src/spur/pool.py", "tests/test_api.py", "tests/test_calc.py", "tests/test_cli.py", "tests/test_model.py"]
covered_digest: "v1:sha256:7c3331d7728d07bd492d0df28c22b0d1dcad4950710002b5fe309c789e7a9a81"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 4: Typed Derived-Dimensions Contract Verification Report

**Phase Goal:** The response every interface reads has a real shape — a typed model,
checked by mypy, instead of an honest but unchecked `dict[str, Any]`.
**Verified:** 2026-09-24T15:06:19Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `derive()` returns a `DerivedDimensions` Pydantic model with explicit optional fields in place of `dict[str, Any]` | ✓ VERIFIED | `src/spur/calc.py:165` `class DerivedDimensions(BaseModel)`, `model_config = ConfigDict(frozen=True)`, 19 explicitly typed fields, none with a `default=`. `derive()` (line 224) is the sole construction site, returning `DerivedDimensions(...)` by keyword, not a dict. `git grep -n with_mate -- src tests docs/architecture` → no output. |
| 2 | `make verify` passes with mypy's `disallow_any_explicit` turned on across `src/` — L14's ratchet retired, not re-deferred | ✓ VERIFIED | Ran `make verify` independently from a clean shell: ruff clean, `mypy src tests docker bench` → `Success: no issues found in 23 source files`, import-linter 5/5 contracts kept, `no-fake-done` silent pass, pytest `104 passed in 30.04s`. `pyproject.toml:90` has `disallow_any_explicit = true` in `[tool.mypy]` with no per-module override that disables it (only override present is the unrelated `cadquery.*`/`OCP.*` `ignore_missing_imports`). `git grep -nE 'type: *ignore\[explicit-any' -- src tests docker bench` → no output. `docs/architecture/decision_log.md` ends with `## L21 … (supersedes L14)`, and a diff against the pre-L21 commit (`059a7e4~1`) confirms the log through L14 is an exact, byte-identical prefix. |
| 3 | The generated OpenAPI document reflects the new typed shape, and the web UI's existing reads of `detail[].ctx.fields` and `warnings` still work, verified by the test suite | ✓ VERIFIED | Fetched `/openapi.json` live via `TestClient`: `/api/info`'s 200 response `$ref`s `#/components/schemas/DerivedDimensions`; that component's `properties` and `required` both have exactly 19 entries; `pitch_d`/`centre_distance` carry `unit: mm`, `span_teeth` carries none. `/api/health` similarly `$ref`s `HealthReport` (`required` = `status`,`version`,`pool`) with nested `PoolState` (`required` = its 3 fields). `src/spur/static/app.js` reads `d.span_teeth`, `info.centre_distance`, `info.warnings`, and the 15 `DIMS` rows — all match `DerivedDimensions` field names, held by `tests/test_api.py::test_every_key_the_ui_reads_is_a_derived_dimensions_field`, run directly and passing. `detail[].ctx.fields` is read at `app.js:116` and asserted in `tests/test_api.py:137` and `tests/test_calc.py:96`, unaffected by this phase's changes and still passing. |
| 4 | `docs/tech_debt/active/2026-09-21-untyped-info-contract.md` is `Status: resolved` with its commit sha recorded, `git mv`'d into `docs/tech_debt/resolved/`, and its row moved in `docs/tech_debt/INDEX.md` — in the same commit as the fix | ✓ VERIFIED | `docs/tech_debt/active/2026-09-21-untyped-info-contract.md` does not exist; `docs/tech_debt/resolved/2026-09-21-untyped-info-contract.md` does, with `Status: resolved` and `Resolved in: 013900d`. `git cat-file -e 013900d^{commit}` resolves (`feat(04-01): derive() returns a frozen DerivedDimensions model`). `docs/tech_debt/INDEX.md` lists the item only under "## Resolved", not "## Active". Commit `cfe5f8d` (`feat(04-03): turn disallow_any_explicit on and retire L14's ratchet`) shows the `pyproject.toml` rule flip, the `git mv` (rename, not delete+recreate), and the `INDEX.md` edit together in one commit. |

**Score:** 4/4 truths verified (0 present, behavior-unverified)

### Plan-Level Must-Haves (Supplementary Detail)

All 04-01/04-02/04-03 PLAN frontmatter `must_haves.truths` were additionally spot-checked
against the codebase (not merely SUMMARY claims):

| Must-have | Status | Evidence |
|---|---|---|
| `DerivedDimensions` frozen, validated on construction, `calc.py` keeps `TYPE_CHECKING` guard, no `logging`/CAD kernel import | ✓ VERIFIED | `src/spur/calc.py` unchanged import boundary; import-linter contract "The gear maths stays free of the CAD kernel" / "...free of the logger" both KEPT |
| `spur info --mate-teeth` refuses exactly what `/api/info` refuses (incl. `0`) | ✓ VERIFIED | `tests/test_cli.py::test_info_rejects_a_mate_the_api_would_reject` run directly, passes; live-checked `/api/info?mate_teeth=0` and `mate_teeth=-5` both return 422; `.venv/bin/spur info --mate-teeth=-5` exits 2 |
| Omitting `--mate-teeth` still means "no mate" | ✓ VERIFIED | `tests/test_cli.py::test_cli_and_api_print_the_same_document`, no-mate case, asserts `cli_out["mate_teeth"] is None` |
| `[tool.pydantic-mypy]` with `init_typed`/`init_forbid_extra` removes the 6 plugin class-line errors | ✓ VERIFIED | `pyproject.toml:97-99`; independent `mypy --disallow-any-explicit src tests docker bench` → `Success: no issues found in 23 source files` |
| No `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` markers in phase-modified files | ✓ VERIFIED | Grepped each of `calc.py`, `app.py`, `cli.py`, `params.py`, `pool.py`, `docker/smoke.py`, `test_calc.py`, `test_cli.py`, `test_api.py`, `test_model.py` individually — no matches |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/spur/calc.py` | `DerivedDimensions` model + `derive()` single construction site | ✓ VERIFIED | 19 fields, `ConfigDict(frozen=True)`, no defaults; `derive()` line 224 |
| `src/spur/app.py` | `info() -> DerivedDimensions`, `health() -> HealthReport`, `schema() -> JsonSchemaValue` | ✓ VERIFIED | All three annotations present and match FastAPI-inferred OpenAPI components |
| `src/spur/cli.py` | `cmd_info` prints via `model_dump_json`; `_mate_teeth` range-checks the flag | ✓ VERIFIED | `cli.py:96` and `:30` |
| `tests/test_cli.py` | D-13 equivalence test + mate-range parity test | ✓ VERIFIED | Both present, run directly, pass |
| `tests/test_api.py` | OpenAPI contract test (D-11) + UI-key belt (D-12) | ✓ VERIFIED | Both present, run directly, pass |
| `pyproject.toml` | `disallow_any_explicit = true`, `[tool.pydantic-mypy]` settings | ✓ VERIFIED | No per-module override weakens it |
| `docs/architecture/decision_log.md` | `L21` appended, supersedes L14, log otherwise unchanged | ✓ VERIFIED | Exact-prefix diff confirmed |
| `docs/tech_debt/resolved/2026-09-21-untyped-info-contract.md` | Resolved, moved, resolvable sha | ✓ VERIFIED | See truth 4 |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `src/spur/app.py:info()` | `src/spur/calc.py:derive()` | `derive(_gear(q), mate_teeth=q.mate_teeth)` | ✓ WIRED | Live call confirmed via TestClient |
| `src/spur/cli.py:cmd_info` | `src/spur/calc.py:derive()` | `derive(...).model_dump_json(indent=2)` | ✓ WIRED | Confirmed by source read + passing D-13 test |
| `tests/test_api.py` | `src/spur/static/app.js` | belt reads `STATIC` path, regexes `DIMS` keys | ✓ WIRED | Test passes; app.js keys manually cross-checked against model fields |
| `/openapi.json` | `src/spur/calc.py:DerivedDimensions` | FastAPI infers schema from the return annotation | ✓ WIRED | Live `/openapi.json` fetch confirms `$ref` and full field/required parity |
| `tests/test_cli.py` | `src/spur/app.py:InfoQuery` | reads `InfoQuery.model_json_schema()` bounds, pins CLI's copy | ✓ WIRED | Confirmed bounds (`ge=6, le=1000`) match `cli.py`'s `_MATE_TEETH_MIN/MAX` |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `make verify` gate | `make verify` (full, from repo root) | ruff clean; mypy `Success: no issues found in 23 source files`; 5/5 import-linter contracts kept; `104 passed in 30.04s` | ✓ PASS |
| Independent mypy strict-Any check | `.venv/bin/mypy --disallow-any-explicit src tests docker bench` | `Success: no issues found in 23 source files` | ✓ PASS |
| OpenAPI reflects `DerivedDimensions` | live `TestClient(app).get('/openapi.json')` | `$ref` correct, `required`/`properties` = 19 fields, units correct | ✓ PASS |
| API refuses `mate_teeth=0`/`-5` | live `TestClient(app).get('/api/info', params={'mate_teeth': 0/-5})` | both `422` | ✓ PASS |
| CLI refuses the same mate values | `.venv/bin/spur info --mate-teeth=-5` | exit 2, `--mate-teeth` on stderr, nothing on stdout | ✓ PASS |
| CLI accepts a valid mate | `.venv/bin/spur info --mate-teeth 40` | numeric `centre_distance` present | ✓ PASS |
| Named unit/integration tests | `pytest tests/test_calc.py::test_a_derived_dimensions_result_cannot_be_changed tests/test_cli.py::test_cli_and_api_print_the_same_document tests/test_api.py::test_openapi_documents_the_typed_contracts tests/test_api.py::test_every_key_the_ui_reads_is_a_derived_dimensions_field tests/test_cli.py::test_info_rejects_a_mate_the_api_would_reject -v` | `5 passed` | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| REQ-typed-derived-dimensions | 04-01, 04-02, 04-03 | `DerivedDimensions` model; `disallow_any_explicit` on; `make verify` green | ✓ SATISFIED | All 4 roadmap SCs verified above; `.planning/REQUIREMENTS.md:226` marks it `Complete` for Phase 4, and the codebase evidence confirms that claim (not merely trusted) |
| REQ-cli-parity | 04-03 (additional) | CLI offers the same numbers/errors as the API | ✓ SATISFIED | The one gap this phase found (`--mate-teeth` range) is closed and tested; `.planning/REQUIREMENTS.md:51` and `:217` (Phase 1, "Complete (shipped v0)") — this phase's Task 1 closed a regression-prevention gap in an already-shipped requirement, not a new orphaned scope |

No orphaned requirements: `.planning/REQUIREMENTS.md`'s Phase 4 row lists only
`REQ-typed-derived-dimensions`; `REQ-cli-parity` is declared explicitly in 04-03's
frontmatter and its Phase 1 acceptance is unaffected.

### Anti-Patterns Found

None in the files this phase modified. `git grep` for debt markers
(`TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER`) across every phase-touched `src`/`tests`/`docker`
file returned nothing. No stub returns, no empty handlers, no hardcoded-empty props found
in `calc.py`, `app.py`, or `cli.py` — every `DerivedDimensions`/`HealthReport`/`PoolState`
field is built from a real computed value or a real branch condition (`... if rr else
None`, `... if p.bore_d > 0 else None`, etc.), not a blanket default.

### Notable, Non-Blocking Items (checked, not gaps)

1. **`docs/architecture/gear-maths/tests.md:28` still cites "L14 note" for the missing
   coverage floor.** Confirmed still present. This predates Phase 4 entirely — `L14`
   never mentioned coverage in the first place (04-03-PLAN.md flagged assumption 8), so
   the pointer was already stale before this phase touched anything, and `tests.md` is
   not one of the five documents D-15/Task 3 targeted for correction. The 04-03 executor
   explicitly noted it as a tangent rather than making an out-of-scope edit, per
   CLAUDE.md's surgical-edit rule. Informational only — does not affect any of the four
   roadmap success criteria.
2. **04-02 Task 1 carried `tdd="true"` but its SUMMARY has no `## TDD Gate Compliance`
   section, and no separate RED `test(04-02)` commit precedes the `feat(04-02)`
   commits.** Confirmed: `04-02-SUMMARY.md` has no such section, and `git log` shows
   `64b53ab` (feat), `8d662f1` (feat), `6064c4f` (test) with no preceding RED-only
   commit for Task 1. Checked `.planning/config.json`: no `workflow.tdd_mode` key is
   set (default off), which matches the orchestrator's note. Under this project's
   config, TDD-gate compliance is advisory, not a phase-gate requirement — informational
   only, does not block phase-goal achievement. (Task 1 in 04-03, by contrast, *does*
   carry a full `## TDD Gate Compliance` section with the RED transcript, so the
   project's convention was followed where it mattered for range-check correctness.)
3. **`spur info --mate-teeth 0` now exits 2 instead of meaning "no mate."** Confirmed
   deliberate (R-2, human decision 2026-09-24) and fully covered:
   `test_info_rejects_a_mate_the_api_would_reject` includes `0` in its rejected-values
   set, and the API itself was independently confirmed to return `422` for
   `mate_teeth=0` and `mate_teeth=-5`. Omitting the flag entirely (the actual "no mate"
   path) is separately tested and still returns `null`/`null` for
   `mate_teeth`/`centre_distance`.
4. **04-01-SUMMARY.md's `duration: ~45min` is reconstructed, not measured.** Confirmed
   — the SUMMARY itself discloses this ("approximate — session start wasn't captured at
   dispatch time; reconstructed from the scope of work, not measured to the minute").
   Duration is not a success criterion for this phase and does not affect goal
   achievement; flagged here only because the orchestrator asked it be checked.

### Human Verification Required

None. Every roadmap success criterion and every supplementary must-have was verifiable
by direct command execution (`make verify`, independent `mypy`, live `TestClient`
requests against `/openapi.json`/`/api/info`/`/api/health`, named pytest runs, and direct
file/git inspection) rather than by trusting SUMMARY.md's narrative.

### Gaps Summary

No gaps. All four ROADMAP success criteria are independently verified true in the
codebase, not merely asserted. `make verify` passes (confirmed by a fresh run, not
reused from the orchestrator's report): ruff clean, mypy `--strict` plus
`disallow_any_explicit` clean across 23 source files, all 5 import-linter contracts kept,
no unfinished-work markers, 104/104 tests passing. The typed contract is wired end to
end — `derive()` → `DerivedDimensions` → `/api/info` response → `/openapi.json` schema →
`spur info` stdout → `app.js`'s reads — and held in place by five tests that were each
run directly during this verification, not just cited from the SUMMARY.

---

*Verified: 2026-09-24T15:06:19Z*
*Verifier: Claude (gsd-verifier)*
