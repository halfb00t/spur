---
phase: "10"
slug: "tooth-tip-chamfer"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-09-28"
---

# Phase 10 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| probe / sweep file → kernel | `bench/tip_chamfer_spike.py`'s hard-coded sets and `bench/sweeps/tip_chamfer.json` become validated `GearParams` and then kernel builds on the developer's host; no user input crosses here | parameter names/values |
| measurement → decision record | The spike's boundary and the sweep's heaviest row become the cap rule 10-02 ships (`calc.py:247`), the number L29 quotes (`decision_log.md:1045`) and what `SPUR_BUILD_TIMEOUT` must hold in production | measured seconds and millimetres |
| client → `GearParams` | `tip_chamfer` arrives as an API query value, a CLI flag or a form field; Pydantic enforces `float`, `ge 0`, `le 3` before anything else runs (`params.py:49`) | one float, mm |
| `GearParams` → kernel | A validated, frozen `GearParams` drives one extra `chamfer()` call as the last step of `_build` (`model.py:368`), inside a `BuildPool` worker under `SPUR_BUILD_TIMEOUT` | validated parameters |
| `calc` → user | `derive()`'s `tip_chamfer_effective` and its two warning sentences carry a value someone checks on the printed part (L08) | one float rounded to 3 dp; static sentences with `:g` floats |
| kernel → printed part | The chamfered solid is what the user cuts or prints; its topology is read back and compared, not assumed (`test_model.py:630`) | face/edge counts, volume, bounding box |
| decision record → future work | L29, the README rows and the two architecture docs are what later phases and users rely on for the cap's meaning and the cost | static prose and one executed CLI example |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-10-01 | Tampering | The spike record: a failing configuration or a slow row dropped so the verdict reads held | high | mitigate | The script times every row (`ok()`, `tip_chamfer_spike.py:101`) and prints one verdict over all of them — `held` at `:377`, `FAILED` with reasons at `:381`, exit 1 on FAILED (`:9`); `bench/RESULTS.md:670` § "Tooth-tip chamfer spike (Phase 10, D-05)" carries the output (18/18 cost rows ok, 405-set grid 0 failures, 163 conservative); the re-pick prohibition sits in 10-01's must_haves | closed |
| T-10-02 | Denial of service | The heaviest configuration versus `SPUR_BUILD_TIMEOUT` in production, unknown until measured | medium | mitigate | The spike reads the timeout from the environment (`tip_chamfer_spike.py:305`, printed `:320`) and its verdict compares every 200-tooth row with it; heaviest request 15.90 s of 30 s (`RESULTS.md` § 670); the D-07 over-budget halt never fired | closed |
| T-10-03 | Denial of service | An 8-minute probe on the developer's host | low | accept | Measurement tooling outside `make verify` and outside the product, `bench/build_time.py`'s stance — see R-10-01 | closed |
| T-10-04 | Tampering | Integrity of the printed part: the chamfer cut differs from the number printed | high | mitigate | One source for cut and number: `_chamfer_tips` takes `c = tip_chamfer_effective(p)` (`model.py:261`), the helper `derive()` prints (`calc.py:273`, `:543`), rounded once to 3 dp; `test_the_tip_chamfer_breaks_only_the_tip_arcs_on_the_built_solid` (`test_model.py:630`) reads the cut back from the kernel; `test_a_tip_chamfer_link_is_served_with_the_chamfer_it_cut` (`test_api.py:235`) and `test_cli_and_api_print_the_same_tip_chamfer_document` (`test_cli.py:166`) pin the served number; the cap is pinned per limit with its full warning string (`test_calc.py:616`) | closed |
| T-10-05 | Tampering | Pre-v0.2 parts changed by the new code path (the involute start moved into `calc`, or the tip step running at 0) | high | mitigate | `_chamfer_tips` returns the solid untouched at `c <= 0` before the selector runs (`model.py:262`); `spline_start` keeps the outline's three expressions and their order (`calc.py:219`, `test_calc.py:689`); the replay compares every recorded field exactly and asserts `all(v is None for k, v in got.items() if k not in recorded)` (`tests/regression/test_pre_v0_2.py:49`); `git diff --exit-code 25b2216 HEAD -- tests/regression/pre_v0_2.json` is empty (fixture byte-unchanged across the whole phase); `test_the_tip_chamfer_changes_no_other_number` (`test_calc.py:670`); 455 tests green | closed |
| T-10-06 | Denial of service | An oversized `tip_chamfer` driving the kernel into a failure or a 422 on a trimmable size | medium | mitigate | Field bounds `_f(0.0, 0, 3, ...)` (`params.py:49`; `test_calc.py:655`); three-limit cap, never a refusal (`calc.py:247-280`); `test_a_rounded_tip_chamfer_cap_stays_inside_the_measured_kernel_boundary` (`test_calc.py:699`) and `test_the_largest_tip_chamfer_the_flank_limit_allows_builds` (`test_model.py:660`) pin the margin against the pinned kernel | closed |
| T-10-07 | Denial of service | A 200-tooth chamfered build (about 15 s of 30 s, independent of `c`) under load | medium | mitigate | Measured in 10-01 (15.90 s heaviest request) and 10-04's 9-row sweep (14.87 s heaviest, `RESULTS.md:790` § "Tooth-tip chamfer build and export time (Phase 10)"); the narrowed margin (~2× of 30 s) is filed as must-debt with a measured trigger, `docs/tech_debt/active/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md` | closed |
| T-10-08 | Information disclosure | New help text and field description | low | accept | `params.py:49` — title, help and group are static string literals; nothing from a request is echoed — see R-10-02 | closed |
| T-10-09 | Tampering | The tip selector picking a flank, root, bore, recess or keyway edge, or none, and shipping a wrong or unchamfered part | high | mitigate | `_tip_edges` selects `CIRCLE` edges at `ra` with both endpoints on an end face and raises `BuildError("Tip chamfer selected no tip-arc edges: a modelling defect in spur, ...")` on an empty selection (`model.py:332-354`); exact counts on 30 matrix rows and the real-pipeline spy (`test_model.py:243`); the guard as a build error (`test_model.py:264`), a 422 naming the defect (`test_api.py:785`) and a stopped export writing nothing (`test_cli.py:188`); the D-12 proof with the other selectors' counts unchanged (`test_model.py:630`: +38 CONE faces, +114 edges, −22.7557 mm³ on three bore shapes) and its tripwire (`test_model.py:648`) | closed |
| T-10-10 | Tampering | A kernel failure inside the cap reaching users as a 422 for a trimmable size | medium | mitigate | The flank limit is tested one step either side on the pinned kernel: 2.937 mm builds, 2.9875 mm fails (`test_model.py:660`; `10-03-SUMMARY.md`), so a kernel bump that moves the contact goes red; the cap carries `TIP_CHAMFER_MARGIN` = 0.001 mm inside the measured boundary (`calc.py:39`) | closed |
| T-10-11 | Denial of service | Two 200-tooth matrix rows adding `make verify` time | low | accept | `make verify` wall time recorded beside Phase 9's in `RESULTS.md` § 790 (453 tests / 97.2 s at 10-04, up from 396 / 78.2 s); 455 tests / ~100 s at audit — see R-10-03 | closed |
| T-10-12 | Denial of service | The heaviest tip-chamfer configuration versus `SPUR_BUILD_TIMEOUT` in production (a 503 instead of a part) | high | mitigate | 9-row sweep (`bench/sweeps/tip_chamfer.json`), every row recorded in `RESULTS.md` § 790; heaviest row `teeth=200 module=1.75 tip_chamfer=1.75 recess_sides=both` at 14.87 s of 30 s; the over-budget halt (10-04 Task 2) never fired; the margin is published and filed as must-debt with its trigger (7.5 s = a quarter of the timeout, crossed) and `docs/tech_debt/INDEX.md` row | closed |
| T-10-13 | Tampering | A narrowed or re-picked sweep hiding a slow row | medium | mitigate | `test_the_tip_chamfer_sweep_is_every_combination_d_06_names` (`test_bench.py:133`) pins the file to the full cross product with each largest chamfer exactly on its limit, so a dropped or shrunk row fails `make verify`; the prohibition in 10-04's must_haves | closed |
| T-10-14 | Repudiation | L29 misquoting a measured boundary or cost | medium | mitigate | L29 present (`decision_log.md:1045`); every number it carries is in `bench/RESULTS.md` (0.04 mm, 163 conservative of 405 sets, 2.937 / 2.9875 mm, 14.87 s — checked at audit); `git diff --numstat 277a98f HEAD -- docs/architecture/decision_log.md` → 0 deleted lines (append-only). Note: L29 cites its sources by RESULTS.md section and SUMMARY name, not by commit sha as 10-05's plan phrased the mitigation; traceability is met, the letter is not | closed |
| T-10-15 | Tampering | User-facing text presenting an unsourced chamfer size as guidance | medium | mitigate | Audit-time negative grep for the research-era range over `README.md`, `src` and `docs` → 0 hits; the README row (`README.md:158`) names purpose and cap, no size; L29 states the figure has no source and names none. Note: the grep is an audit check, not a committed test — a future edit that reintroduces a figure would not fail `make verify` | closed |
| T-10-16 | Information disclosure | New README and docs text | low | accept | Static documentation; no secrets or request data — see R-10-04 | closed |
| T-10-SC | Tampering | package installs | low | accept | `git diff --stat 277a98f HEAD -- pyproject.toml requirements.txt` → empty; new `import`/`from` lines in the `calc.py` / `model.py` / `params.py` diffs → none — see R-10-05 | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-10-01 | T-10-03 | The spike is measurement tooling run by hand on the developer's host, outside `make verify` and outside the product; its cost is recorded, not paid by users or CI | plan 10-01 (`<threat_model>`), unchanged at audit | 2026-09-28 |
| R-10-02 | T-10-08 | The field's title, help and group are static string literals in `params.py`; they carry no request data, so there is nothing to disclose beyond what the schema already publishes | plan 10-02 (`<threat_model>`), unchanged at audit | 2026-09-28 |
| R-10-03 | T-10-11 | Two 200-tooth proof rows cost about 5 s of bare builds inside `make verify`; the wall time is recorded beside Phase 9's so the trend is visible, and the gate stays well inside CI's budget | plan 10-03 (`<threat_model>`), recorded by 10-04 | 2026-09-28 |
| R-10-04 | T-10-16 | README and architecture-doc text is static documentation; no secrets and no request data | plan 10-05 (`<threat_model>`), unchanged at audit | 2026-09-28 |
| R-10-05 | T-10-SC | No plan in the phase installs a package or changes a dependency range; the supply-chain surface is the one v0.1 and Phases 7–9 already audited | plans 10-01 … 10-05, added at audit (Phase 9 precedent) | 2026-09-28 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-28 | 17 | 17 | 0 | orchestrator (grep-depth, ASVS L1 short-circuit; tree `b43ff7d`) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-28
