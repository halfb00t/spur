---
phase: "08"
slug: "hex-bore"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-09-27"
---

# Phase 08 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| planning docs → phase verifier | The verifier grades Phase 8 against REQ-hex-bore and ROADMAP SC2; stale text fails a correct D-01 implementation or passes a wrong one (08-01) | requirement and success-criterion text |
| client → `GearParams` | `bore_hex` arrives as an API query value, CLI flag or form field; Pydantic enforces `float`, `ge 0`, `le 200` before anything else runs (`params.py:58`) | one float, mm |
| `GearParams` → kernel | A validated, frozen `GearParams` drives one extra prism cut and 12 chamfered edges inside a `BuildPool` worker under `SPUR_BUILD_TIMEOUT` | validated parameters |
| client → `calc.check()` | Every hex combination is judged in pure arithmetic before a worker slot or the kernel is touched (`calc.py:176-203`) | validated parameters |
| `calc` → user | `derive()`'s two hex numbers, and the refusal / warning sentences, carry values someone cuts metal to (L08, L15) | floats rounded to 3 dp; static sentences with `:g` / `:.2f` floats |
| sweep file → kernel | `bench/sweeps/*.json` becomes `GearParams` (validated) and then kernel builds on the developer's host (`bench/build_time.py`) | JSON rows of parameter names/values |
| bench script → shell | One `git rev-parse --short HEAD` subprocess for the provenance line (`build_time.py:94`) | read-only `git` stdout |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-08-01 | Tampering | ROADMAP.md written outside the tooling | low | mitigate | `fddf9b8` touches ROADMAP.md in exactly three criteria (Phase 8 SC2, Phase 9 SC2, Phase 12 SC1; 14 changed lines, nothing else — re-read by the verifier via `git show fddf9b8 -- .planning/ROADMAP.md`); `roadmap.milestone-scope` read before and after the write, phases 7–12 / count 6 unchanged (`08-01-SUMMARY.md:79`); the human approved the exact texts at the Task 2 checkpoint before any write | closed |
| T-08-02 | Repudiation | Unrecorded criteria change | low | mitigate | Three Roadmap Evolution lines in `STATE.md` (`grep -cE '^- Phase (8\|9\|12) edited'` → 3, all citing 08-CONTEXT.md D-01); the human's answer ("approved", no wording changes) recorded in `08-01-SUMMARY.md:40` | closed |
| T-08-03 | Tampering | Integrity of the printed part: a hex dimension printed wrong, or through `bore_effective` | high | mitigate | One source for the number: `calc.hex_across_flats` (`calc.py:61`) feeds the cut (`model.py:203` `polygon(6, hex_across_flats(p), circumscribed=True)`), `bore_rim_limit`'s hex branch (`calc.py:81`, `/√3`) and both derived fields (`calc.py:388-389`); `test_a_hex_bore_measures_the_across_flats_and_corners_it_reports` (`test_model.py:159`) measures the built solid's vertices and flat midpoints against the printed values within `5e-4` mm (`:174`, `:179`); `bore_effective` is `None` whenever `bore_hex > 0` (`calc.py:387`, asserted over HTTP at `test_api.py:159`); the verifier's live `spur info --bore-hex 6` gave `(6.15, 7.101, None)` | closed |
| T-08-04 | Tampering | Pre-v0.2 parts changed by the new code path | high | mitigate | `test_a_pre_v0_2_parameter_set_derives_the_same_dimensions` (`test_pre_v0_2.py:42`) compares every recorded field exactly (`:48`) and requires every field added since to be `None` (`:49`); `git log 540f1a0..HEAD -- tests/regression/pre_v0_2.json` is empty (0 commits — byte-unchanged through all four plans); volume / bbox / face+edge counts replay per record | closed |
| T-08-05 | Denial of service | A hex link whose chamfered corners meet the recess wall reaching the kernel and failing after a timed build | medium | mitigate | `bore_mouth_limit(p)` (`calc.py:85`) is the chamfered mouth's farthest reach (`rim + 2c/√3` for a hex); `recess_radii()` sets `hub = bore_mouth_limit(p) + MIN_WALL` (`calc.py:112`) for every bore shape; `test_a_recess_at_its_hub_clearance_keeps_min_wall_from_the_chamfered_bore_mouth` (`test_model.py:246`) measures 0.4 mm of wall on the built solid at a 3 mm chamfer for round, D-flat and hex | closed |
| T-08-06 | Denial of service | Build cost of the hex cut | low | mitigate | 16-row sweep recorded in `bench/RESULTS.md` § "Hex bore build and export time (Phase 8, D-11)"; heaviest row 5.08 s of the 30 s budget (`RESULTS.md:565-568`); 0 rows over budget | closed |
| T-08-07 | Information disclosure | New field descriptions and help text | low | accept | `params.py:58` — title, help and examples are static literals; nothing from a request is echoed — see R-08-01 | closed |
| T-08-08 | Denial of service | A hex or chamfer the root cannot hold reaching the kernel and failing after a timed build in a worker slot | high | mitigate | Two rules in `calc.check()`'s hex branch, decided before any CAD: corners vs root (`calc.py:180`, `bore_rim_limit(p) > pr.rf - MIN_WALL`) and chamfered mouth vs root (`calc.py:195`, `bore_mouth_limit(p) > pr.rf - MIN_WALL`); one step past each limit is a 422 (`test_api.py:182` bore_hex 24.2 / `:190` 23.4; `test_api.py:196`), one step inside builds (`test_model.py:217-220`, 24.15 / 23.35); the bound sits on the root circle, not the side length, because the kernel chamfers a 0.375 mm side at the 3 mm field bound (`test_model.py:227`, comment `calc.py:186-194`) | closed |
| T-08-09 | Tampering | A requested chamfer or hex silently trimmed to fit (a different part than asked) | medium | mitigate | No capping expression exists in the hex branch (`calc.py:176-203` — grep for `min(`/cap: none); every conflict is `errors.append((sentence, fields))` → one `PydanticCustomError` each → 422 / exit 2 naming the fields (`test_api.py:196` names `bore_chamfer` and `bore_hex`); the only trimming path in `check()` is the pre-existing round-bore chamfer cap, unchanged | closed |
| T-08-10 | Information disclosure | Refusal and warning text | low | mitigate | Refusals interpolate only `:.2f` / `:g` floats and literal field names (`calc.py:182-184`, `:197-200`); the D-02 warning's `ignored` list is built from the fixed pairs `("bore_d", p.bore_d)`, `("bore_flat", p.bore_flat)` with `:g` (`calc.py:339-343`); no request string reaches a message | closed |
| T-08-11 | Repudiation | The API and CLI telling a user different things | low | mitigate | One source (`check()` / `derive()`); `test_cli_and_api_print_the_same_hex_bore_document` (`test_cli.py:116`) compares `spur info --bore-hex 6` with `/api/info`; `test_a_hex_bore_the_root_cannot_hold_exits_2_and_names_it` (`test_cli.py:105`) pins exit 2 with the same sentence | closed |
| T-08-12 | Denial of service | The hex feature's heaviest configuration versus `SPUR_BUILD_TIMEOUT` in production | medium | mitigate | Every one of the 16 D-11 rows recorded with build + slower export against the 30 s budget; heaviest named in `RESULTS.md:565` and L27 (`decision_log.md:890-891`): `teeth=200 module=1.75 bore_hex=200 recess_sides=both bore_chamfer=0.4` at 5.08 s; the over-budget halt (08-04 Task 2) never fired | closed |
| T-08-13 | Tampering | A narrowed or re-picked sweep hiding a slow row | medium | mitigate | `bench/sweeps/hex_bore.json` holds 16 rows; `test_the_hex_bore_sweep_is_every_combination_d_11_names` (`test_bench.py:50`) pins the file to D-11's full cross product, so a dropped row fails `make verify` | closed |
| T-08-14 | Elevation of privilege | Shell injection through the bench script's git call | low | mitigate | `build_time.py:94-97`: fixed argv `["git", "rev-parse", "--short", "HEAD"]`, `capture_output=True, text=True, check=True`, no `shell=` anywhere in the file; the sweep file's values only ever reach `GearParams` validation | closed |
| T-08-15 | Repudiation | Decisions and debt lost after the phase | low | mitigate | L27 present (`grep -c '^## L27 — '` → 1) and `decision_log.md` append-only (0 deletions since `540f1a0`); commit `2683396` carries `docs/tech_debt/active/2026-09-26-round-bore-chamfer-reach-is-not-checked.md` and its `INDEX.md` row together (2 files, 40 insertions) | closed |
| T-08-SC | Tampering | package installs | low | accept | `git diff 540f1a0..HEAD -- pyproject.toml requirements*.txt` is empty; `bench/build_time.py` imports the standard library, the already-pinned `pydantic`, and repo-local `bench` / `spur` modules — no new dependency in any of the four plans — see R-08-02 | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-08-01 | T-08-07 | The new field's title, help text and examples are static string literals in `params.py`; they carry no request data, so there is nothing to disclose beyond what the schema already publishes | plan 08-02 (`<threat_model>`), unchanged at audit | 2026-09-27 |
| R-08-02 | T-08-SC | No plan in the phase installs a package or changes a dependency range; the supply-chain surface is the one v0.1 and Phase 7 already audited | plans 08-01 / 08-02 / 08-03 / 08-04 (`<threat_model>`), unchanged at audit | 2026-09-27 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-27 | 16 | 16 | 0 | orchestrator (grep-depth, ASVS L1 short-circuit; tree `439bfa8`) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-27
