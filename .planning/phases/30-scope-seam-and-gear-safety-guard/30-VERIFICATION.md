---
phase: 30-scope-seam-and-gear-safety-guard
verified: 2026-10-23T17:30:00Z
status: passed
score: 4/4 must-haves verified
covered_files:
  - ".planning/phases/30-scope-seam-and-gear-safety-guard/30-01-PLAN.md"
  - ".planning/phases/30-scope-seam-and-gear-safety-guard/30-01-SUMMARY.md"
  - ".planning/phases/30-scope-seam-and-gear-safety-guard/30-02-PLAN.md"
  - ".planning/phases/30-scope-seam-and-gear-safety-guard/30-02-SUMMARY.md"
  - ".planning/phases/30-scope-seam-and-gear-safety-guard/30-03-PLAN.md"
  - ".planning/phases/30-scope-seam-and-gear-safety-guard/30-03-SUMMARY.md"
  - ".planning/phases/30-scope-seam-and-gear-safety-guard/30-04-PLAN.md"
  - ".planning/phases/30-scope-seam-and-gear-safety-guard/30-04-SUMMARY.md"
  - ".planning/phases/30-scope-seam-and-gear-safety-guard/30-05-PLAN.md"
  - ".planning/phases/30-scope-seam-and-gear-safety-guard/30-05-SUMMARY.md"
  - "AGENTS.md"
  - "Makefile"
  - "bench/RESULTS.md"
  - "docs/architecture/decision_log.md"
  - "pyproject.toml"
  - "scripts/gear_unchanged.py"
  - "src/spur/app.py"
  - "src/spur/din5480.py"
  - "src/spur/din5480_tables.py"
  - "src/spur/model.py"
  - "src/spur/parts.py"
  - "src/spur/pool.py"
  - "src/spur/records.py"
  - "src/spur/shaft_calc.py"
  - "src/spur/shaft_model.py"
  - "src/spur/shaft_params.py"
  - "tests/test_api.py"
  - "tests/test_gear_unchanged.py"
  - "tests/test_hooks.py"
  - "tests/test_seam.py"
covered_digest: "v3:sha256:bd97d1b6adf366dc9e06631e4af4974f850c24fbbeac9e51800939cfb7934bdf"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 30: Scope, Seam and Gear-Safety Guard Verification Report

**Phase Goal:** The product is declared a gear and spline generator, in the decision log, before any shaft code exists; the shaft is walled off from the gear by import contracts and its own route prefix; and one check, run at every phase close, proves that no existing gear link builds a different part.
**Verified:** 2026-10-23
**Status:** passed
**Re-verification:** No, initial verification

## Goal Achievement

### Observable Truths (ROADMAP success criteria, the contract)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | L46 is logged, widens scope, amends L02/L05, says what it supersedes and leaves alone, and its commit precedes the first shaft module commit | VERIFIED | `docs/architecture/decision_log.md:3062` `## L46 — ... (amends L02 and L05; keeps L03, L04, L06, L08 and L44)` is the last `^## L` heading. Body has the decision, amendments, leaves-alone, freeze timing, the `part=` behaviour change, wall layout, proof. `git diff v0.6 -- decision_log.md` shows no removed lines, so no earlier entry (L02, L05) was edited. L46 commit `5d61f8e` is an ancestor of `bdf224d`, the only commit that adds the five shaft placeholder files (`git merge-base --is-ancestor`, run per file, all "yes"; the list is non-empty). `AGENTS.md` "What we're building" now says "gear and spline generator (L46)". |
| 2 | "Same gear, same links" is one command that fails on a changed `tests/regression/`, `ci.yml` or `/api/schema` bytes, reads green on the tree, was seen red per watched item, reds recorded in `bench/RESULTS.md`; gear-file edits this phase leave it green | VERIFIED | `make gear.unchanged` ran here: `gear.unchanged: tests/regression/, .github/workflows/ci.yml and /api/schema (8723 bytes) are byte-equal to v0.6`, 0.6 s. `scripts/gear_unchanged.py` read in full: the baseline is the `v0.6` tag via `git archive`, an untracked file in a watched dir counts, the schema is compared as raw bytes in one interpreter per tree, `spur.__file__` is asserted, empty bodies fail. `git diff v0.6 --stat` on `tests/regression`, `ci.yml`, `requirements.txt`, `README.md`, `calc.py`, `params.py` is empty. Wired into `verify.static` (Makefile line 113). `bench/RESULTS.md` "Seen red once (Phase 30)" has a row per watched item (edited regression file, untracked file, `ci.yml`, schema byte) plus missing-tag, shadow-import, shallow-depth, repo-state, dry-run pin and image reds. |
| 3 | The shaft cannot leak into the gear: contracts for no cadquery, no logger, no gear maths, solid reachable only through `model`; route-table pin; each seen red once | VERIFIED | `make lint-imports` here: `Contracts: 10 kept, 0 broken.`, including the five new shaft contracts. Five docstring-only modules exist (read in full: no statements). `tests/test_seam.py` read in full: regex belts per contract, an existence guard for contract-named modules, and a route pin (`/api/` set contains the v0.6 four, every other starts `/api/shaft/`, gear query keys equal `GearParams` fields plus `mate_teeth`/`quality`). Ran: 32 passed (seam, gear_unchanged, hooks, saturated). `grep ShaftParams src` finds only the docstring in `shaft_params.py` and `parts.py`; `grep api/shaft src` finds nothing, so no shaft route answers. `RESULTS.md` has a red row for C1, C2, C3, C4, C5, the existence guard, the route pin and the query-key pin. |
| 4 | The gate delta is recorded: `make verify` against v0.6's close on the same host, in `bench/RESULTS.md` | VERIFIED | `RESULTS.md` "The gate delta (30-05)": 1369 passed in 233.18 s (real 234.48 s) against 236.23 s baseline of record and the 239.51 s cross-check, load before and after, HEAD, host, coverage 98.00 %. Under L43's 300 s bar. The orchestrator's independent run agrees (1369 passed, 98.00 %). |

**Score:** 4/4 truths verified (0 present, behavior-unverified)

### Plan-level must-haves spot-checked

| Claim | Status | Evidence |
|-------|--------|----------|
| `_serve_model` extracted; `model()` delegates; 503 wording part-neutral and pinned | VERIFIED | `git diff v0.6 -- src/spur/app.py`: `q.quality` read as `quality` at each site, `params = _gear(q)` moved to the route, `request_id` minted after `_gear`, every other line identical. 503 text now "parts"; `test_a_saturated_service_names_its_queue_in_parts` passes and has a recorded red. |
| No `model._build` dispatch stub, no shaft import in `model.py` | VERIFIED | `model.py` diff since v0.6 is the `Part` import and two signatures. |
| `Part` seam on `pool`, `records`, `app`, `model` signatures | VERIFIED | Diff shows the ten signatures changed from `GearParams` to `Part`. |
| Placeholders cost nothing in coverage; `no-fake-done` green | VERIFIED | `make no-fake-done` exit 0; coverage table in `RESULTS.md` shows 0 statements, 100.00 %. |
| `make test-image` ignores the git-driven test | VERIFIED | Makefile line 277 and the `test_hooks.py` pin. |

### Requirements Coverage

| Requirement | Source | Status | Evidence |
|-------------|--------|--------|----------|
| REQ-scope-decision-logged | 30-02 | SATISFIED | L46 as above. Marked `[x]` and Complete in REQUIREMENTS.md. |
| REQ-gear-unchanged-proof | 30-01, 30-04, 30-05 | SATISFIED | `make gear.unchanged` green, seen red per item. REQUIREMENTS.md names "regression dir, ci.yml, gear /api/schema byte-equal"; all three are checked. |
| REQ-shaft-routes-separate | 30-03 | SATISFIED | Route pin and query-key pin pass; 10 contracts kept. No shaft route exists yet, the prefix is enforced for the ones Phase 33 adds. |

No orphaned requirement: the three IDs mapped to Phase 30 in REQUIREMENTS.md (lines 159-161) are all claimed by plans. REQ-gate-cost-recorded is correctly left open (cross-cutting, closes Phase 34).

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Same-gear check on the tree | `make gear.unchanged` | byte-equal to v0.6 (8723 bytes) | PASS |
| Import contracts | `make lint-imports` | 10 kept, 0 broken | PASS |
| Static gate | `make verify.static` | exit 0 | PASS |
| Seam, gear_unchanged, hooks, 503 pin | `pytest -k "seam or gear_unchanged or hooks or saturated or route or query_key or shaft or unchanged" --no-cov -n0` | 32 passed | PASS |
| CI-shaped run: shallow, tagless clone fetches the tag | `git clone --depth=1 --no-tags file://...`, then `python -m scripts.gear_unchanged` in it | tag fetched, byte-equal, exit 0, clone stayed shallow | PASS |
| Full `make verify` | orchestrator's independent run, not repeated here | 1369 passed, 98.00 %, exit 0 | accepted as given |

### Anti-Patterns Found

No `TBD`/`FIXME`/`XXX`/`TODO`/`HACK` in any file the phase touched; `make no-fake-done` exit 0.

Code review (`30-REVIEW.md`: 0 critical, 3 warning, 4 info) weighed against the must-haves:

| Finding | Severity | Undermines a must-have? |
|---------|----------|--------------------------|
| WR-01 no timeout or prompt guard on `git fetch` / probe in `gear_unchanged.py` | Warning | No. A failing fetch fails the check with the cause (red recorded, `/nonexistent` origin). A hung fetch is an unhandled robustness hole, not a false pass: it never reports green. It should be fixed before the hook is relied on offline. |
| WR-02 test can flake on racy index entries | Warning | No. Test-only; the check itself writes nothing. |
| WR-03 `parts.py` "one-line edit" claim is false: `_build_checked`, `_write_export` and `records._gear_fields` still read `GearParams` | Warning | No. No roadmap criterion depends on it. Today's signatures take `Part = GearParams` and are correct. It is a forward claim about Phase 31's cost, confirmed inaccurate (grep of `model.py` shows `_write_export(shape, p: GearParams...)`). Fix the docstring, or type those internals, when Phase 31 widens `Part`. |
| IN-01 to IN-04 | Info | No. IN-02 (any local `v0.6` tag, even lightweight, accepted) is worth a follow-up since the tag is the whole baseline. |

### Human Verification Required

None blocking. One thing cannot be observed here and is confirmed by the next CI run on the PR: the check inside GitHub's real `actions/checkout@v4` (A1). The mechanism is verified in a real shallow, tagless clone, and the tag exists on origin (`git ls-remote` shows `v0.6` at `b7f217f`, peeling to `792b45c`), so this is a confirmation, not a gap.

## Gaps Summary

No gaps. All four roadmap criteria hold in the code and by commands run here. The three review warnings are robustness and documentation issues in a check that fails closed, so they do not block the phase. Suggested follow-up, to file under `docs/tech_debt/active/`: WR-01 (timeouts and `GIT_TERMINAL_PROMPT=0`), IN-02 (require an annotated tag), WR-03 (correct the `parts.py` claim before Phase 31).

---

_Verified: 2026-10-23_
_Verifier: Claude (gsd-verifier)_
