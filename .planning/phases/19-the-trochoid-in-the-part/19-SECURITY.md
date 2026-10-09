---
phase: "19"
slug: "the-trochoid-in-the-part"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
block_on: high
register_authored_at_plan_time: true
created: "2026-10-09"
---

# Phase 19 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Written by secure-phase (state B: no prior SECURITY.md; every one of the 11 PLANs carries a `<threat_model>` block, so the register is plan-authored and the auditor was not spawned — `threats_open: 0` at ASVS L1 is the documented short-circuit). Evidence is grep-level (L1): each mitigation located in the shipped code, its test, or the record the plan named, on 2026-10-09 at `fbaeec6`. Every SUMMARY's `## Threat Flags` reads "None" for new surface and names its plan's threats as mitigated or accepted as planned.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| shared link / web form / CLI flags / API query → `GearParams` | `root_shape` and `root_fillet` arrive as untrusted strings and numbers and are validated once (19-04, 19-07) | parameter strings and floats; `Literal["radial","trochoid"]`, `root_fillet` bounded finite 0–3 mm |
| floats → kernel wire | a gap, a swing or a degenerate arc in the floats becomes a wrong or failing solid (19-05) | spline control points, junction vectors |
| kernel failure → user message | a modelling defect must not be reported as a parameter problem (19-05, 19-07) | `BuildError` text → 422 `build_error` / CLI exit 1 |
| calc result → a printed number or sentence | every number `derive()` prints is one someone will cut metal to (L08) (19-04, 19-06) | `root_form_d`, `root_waist`, null `root_thickness`/`root_gap`, the undercut sentence |
| composed request → one built solid | every feature's selector and proof must still take exactly its own edges with the hob root on (19-08) | edge selections, chamfer cap |
| a request → a worker within `SPUR_BUILD_TIMEOUT` | a heavier build turns into a 503 under load (19-01, 19-09) | build + export time |
| bench measurement / a measured price → a decision or record | a wrong measurement becomes a wrong cap, a hidden 503, or a bar tuned to pass (19-01, 19-02, 19-09) | bars, floors, timings |
| the merge gate → a green check | a gate silenced too broadly passes real failures (19-03) | `filterwarnings`, flake counts |
| the record → the next person who cuts a gear | the decision log, strategy docs, README and ideas are what a later phase trusts (19-10, 19-11) | L38, README geometry notes, Phase 20 skip |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-19-01 | Tampering | `bench/trochoid_part.py` spike outline diverging from what ships | medium | mitigate | 19-09 removed `trochoid_outline`; the bench builds through `model._gear_blank` / `model._outline` / `model._build_checked` (`bench/trochoid_part.py:9-10,128,136`); the chamfer law re-run on the real build gives the same 14 rows (`bench/RESULTS.md` "Chamfer law on the real build (19-09)") | closed |
| T-19-02 | Denial of service | heaviest corner rows over `SPUR_BUILD_TIMEOUT` | medium | mitigate | every corner row in both root shapes timed build + export: 34 requests inside 30 s, heaviest trochoid 14.64 s, radial twin 9.50 s (`bench/sweeps/trochoid.json`, `bench/RESULTS.md` 19-09; `tests/test_bench.py` pins the sweep) | closed |
| T-19-03 | Repudiation | kernel bar, guard bars, `ROOT_ARC_MIN`, waist floor tuned toward a pass | high | mitigate | `proposed_bar`, `deviation_b` are pure helpers (`bench/trochoid_part.py:584,597`) pinned in `tests/test_bench.py`; the bar, floor and guards went to the human (`take the recommendations`, 2026-10-09); `bench/RESULTS.md` "Bars adopted (19-02)" records headroom and words; `KERNEL_BAR_PER_MODULE = 2e-3` (`tests/test_model.py:64`) | closed |
| T-19-04 | Tampering | guard numbers from a stride-2 sample | medium | mitigate | `product_row` (`bench/trochoid_part.py:1093`) runs every trochoid case of the 31,446-case product; `bench/RESULTS.md` "Guard numbers over the product (19-02)" | closed |
| T-19-05 | Tampering | a blanket `pyproject.toml` `filterwarnings` ignore | high | mitigate | no filter was added: `filterwarnings` still `["error", "ignore::DeprecationWarning:starlette.*", "ignore:Using `httpx`"]`; `pyproject.toml` unchanged against `df4749e`; the human chose `debt-redefer` (19-03) | closed |
| T-19-06 | Tampering | `root_shape` / `root_fillet` carrying an unexpected value | medium | mitigate | `root_shape: Literal["radial", "trochoid"]` (`src/spur/params.py:59`), refused with 422 / argparse exit 2 (`tests/test_cli.py::test_an_unknown_root_shape_exits_2_on_the_cli_and_is_a_422_on_the_api`); `root_fillet` bounds unchanged (`tests/test_trochoid.py::test_a_tip_radius_that_is_not_a_finite_millimetre_value_is_refused_before_any_cap`) | closed |
| T-19-07 | Tampering | the default part changing for a link that omits `root_shape` | high | mitigate | default `"radial"` (`params.py:60`); `tests/regression/pre_v0_2.json` byte-identical to `df4749e` (SC1 checks 19-04 … 19-08 re-run green 2026-10-09); `tests/regression/test_pre_v0_2.py` replays the corpus | closed |
| T-19-08 | Tampering | `derive()` / `model._build` printing numbers for a part not built that way | high | mitigate | one `root_mode` per consumer; `_ROOT_SENTENCES["thickness not printed"]` (`src/spur/calc.py:1116,1710`); the oracle reads the built root with the printed `rho` (`tests/test_model.py::test_the_built_root_is_the_oracle_s_root_on_every_kernel_row`) | closed |
| T-19-09 | Denial of service | `model._trochoid_outline` building slower | low | accept | accepted at plan time; 19-09 re-timed the real build: heaviest 14.64 s of 30 s; L37's per-request timeout and 503 hold | closed (accepted) |
| T-19-10 | Tampering | a wire that opens or a spline that swings into a valid-looking wrong part | high | mitigate | `_guard_junction`, `_guard_spacing`, `_guard_annulus`, `_guard_area` (`src/spur/model.py:238,249,263,276`) with bars `ROOT_JUNCTION_BAR_RAD`, `ROOT_SPACING_RATIO_MAX`, `ROOT_AREA_REL_MAX` (`model.py:82,87,93`), each reached by a test (19-05 T2) | closed |
| T-19-11 | Denial of service | a typed backlash in `makeThreePointArc`'s dead band | medium | mitigate | `ROOT_ARC_MIN = 2e-6` and the shared-vertex branch (`src/spur/model.py:66,213`); the tuned-backlash test builds through `build(p)` (19-05 T1) | closed |
| T-19-12 | Tampering | the restated undercut sentence advising a shift that still undercuts | high | mitigate | `_ROOT_SENTENCES["undercut"]` / `["undercut out of range"]` (`src/spur/calc.py:1468-1470`); `tests/test_trochoid.py::test_the_advised_shift_is_rounded_up_and_flips_the_gear_out_of_undercut`, `::test_the_restated_undercut_sentence_fires_at_17_teeth_and_not_18` | closed |
| T-19-13 | Tampering | `root_form_d` / `root_waist` mislabelled or unproved | medium | mitigate | description "cutter-envelope junction; not an ISO 21771 form diameter" (`src/spur/calc.py:965`); `tests/test_api.py::test_root_form_d_is_never_labelled_an_iso_form_diameter_where_a_user_reads_it`; `_ROOT_SENTENCES["waist thin"]` (`calc.py:1155`) | closed |
| T-19-14 | Tampering | a case/whitespace variant of `root_shape` normalised | medium | mitigate | pydantic `Literal` and argparse `choices` exact; seven spellings pinned on both front ends (19-07 T2) | closed |
| T-19-15 | Information disclosure | the guard's `BuildError` text on a 422 | low | accept | accepted at plan time; the 422 carries `type: build_error` and the guard sentence only (`src/spur/app.py:439`); `tests/test_cli.py::test_a_root_guard_build_error_reads_the_same_on_the_api_and_the_cli` asserts the catch-all's text absent | closed (accepted) |
| T-19-16 | Tampering | a tip-chamfer cap the kernel cannot cut on a hob root | high | mitigate | `tip_chamfer_limit(p, rm)` reads the junction (`src/spur/calc.py:333`); `tests/test_model.py::test_the_largest_tip_chamfer_the_hob_root_junction_allows_builds`, `::test_the_kernel_fails_one_step_past_the_hob_root_junction` | closed |
| T-19-17 | Tampering | `_tip_edges`, `_bore_rim_edges`, `_groove_floor_edges` taking a root arc or nothing | medium | mitigate | selectors (`src/spur/model.py:657,681,714`); the selector matrix's trochoid twins assert the radial counts (19-08 T2, `each_edge_selector`) | closed |
| T-19-18 | Denial of service | the heaviest trochoid corner row over `SPUR_BUILD_TIMEOUT` | high | mitigate | `make bench.build SWEEP=bench/sweeps/trochoid.json`: all 34 requests inside 30 s, heaviest 14.64 s (`bench/RESULTS.md` 19-09) | closed |
| T-19-19 | Repudiation | the gate's cost read across hosts or trimmed to pass | medium | mitigate | before and after on the same Apple M5 Max with loads (`bench/RESULTS.md` "The gate, priced (19-09)"); the 66 s gate stopped for the human, who chose `accept-A` (no test trimmed); recorded in L38 | closed |
| T-19-20 | Repudiation | L38 or the strategy docs claiming what the code does not back | medium | mitigate | `git diff df4749e -- docs/architecture/decision_log.md` has 0 removed lines; every figure cited to a SUMMARY sha or a RESULTS subsection; both strategy docs name L38 (19-10 checks re-run green 2026-10-09) | closed |
| T-19-21 | Repudiation | README / ideas / Phase 20 skip claiming what the code does not back | medium | mitigate | README has 0 occurrences of "form diameter" and names the cutter-envelope junction (`README.md:234`); `test_readme_export_examples_run` green; Phase 20 row `Skipped (O4, flip deferred)` with L38 and D-09 in ROADMAP/STATE/REQUIREMENTS (19-11 checks re-run green) | closed |
| T-19-SC | Tampering | npm/pip/cargo installs | low | accept | accepted at plan time in every plan; nothing was installed; `requirements.txt` still 31 pins; stdlib maths only (SC1 checks) | closed (accepted) |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-19-01 | T-19-09 | A trochoid request builds slower than a radial one; measured inside the 30 s timeout (heaviest 14.64 s, 1.54× its radial twin) and covered by L37's per-request 503 contract | plan-time disposition (19-04 PLAN threat register, planner); confirmed by 19-09's measurement | 2026-10-08 |
| R-19-02 | T-19-15 | The guard's `BuildError` sentence names the check and the remedy only — no path, no stack; asserted by test | plan-time disposition (19-07 PLAN threat register, planner) | 2026-10-08 |
| R-19-03 | T-19-SC | No package installed in the phase; dependencies stay at the 31 pins the SC1 check asserts | plan-time disposition (every PLAN's threat register, planner) | 2026-10-08 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-09 | 22 | 22 | 0 | secure-phase (orchestrator, L1 grep-depth; auditor short-circuited: plan-authored register, ASVS 1, threats_open 0) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-09

## Security Audit 2026-10-09

| Metric | Count |
|---|---|
| Threats found | 22 |
| Closed | 22 |
| Open | 0 |
