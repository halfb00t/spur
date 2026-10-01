---
phase: "09"
slug: "keyway-bore"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-09-27"
---

# Phase 09 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| planning docs → phase verifier | The verifier grades Phase 9 against REQ-keyway-* and ROADMAP SC1–SC5; stale text fails a correct D-09/D-14 implementation or passes a wrong datum (09-01) | requirement and success-criterion text |
| client → `GearParams` | `keyway_width`/`keyway_depth` arrive as API query values, CLI flags or form fields; Pydantic enforces `float`, `ge 0`, `le 200` before anything else runs (`params.py:59`, `:65`) | two floats, mm |
| client → `calc.check()` | Every keyway and chamfer combination is judged in pure arithmetic inside the model validator, before a worker slot or the kernel is touched (`calc.py:239-340`) | validated parameters |
| `GearParams` → kernel | A validated, frozen `GearParams` drives one extra box cut (`model.py:223`) after the chamfered bore, inside a `BuildPool` worker under `SPUR_BUILD_TIMEOUT` | validated parameters |
| `calc` → user | `derive()`'s two keyway numbers (`calc.py:407-`) and the refusal sentences carry values someone cuts metal to (L08, L15) | floats rounded to 3 dp; static sentences with `:g` / `:.2f` / `:.3f` floats |
| sweep file → kernel | `bench/sweeps/keyway_bore.json` becomes `GearParams` (validated) and then kernel builds on the developer's host, via the unchanged Phase 8 runner | JSON rows of parameter names/values |
| docs → user | README and field help are what a user reads before cutting a key to the printed numbers | static prose and one executed CLI example |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-09-01 | Tampering | ROADMAP.md written outside the tooling | low | mitigate | `69948df` touches exactly `REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md` (3 files, 45+/35−); the write went through edit-phase's `write_updated_phase` step with the milestone-scope check before and after (phases 7–12 unchanged; `09-01-SUMMARY.md:29`, `:46`, `:67`); the orchestrator verified `ROADMAP.md` byte-untouched at the Task 2 checkpoint, before the human's approval | closed |
| T-09-02 | Repudiation | Unrecorded criteria change | low | mitigate | One Roadmap Evolution line in `STATE.md` (`grep -c 'Phase 9 edited: edited fields: requirements, success_criteria (per 09-CONTEXT.md D-20)'` → 1); the human's answer ("approved", no wording changes) recorded at `09-01-SUMMARY.md:40`, `:103`, `:114` | closed |
| T-09-03 | Tampering | Integrity of the printed part: a keyway floor or number off the as-cut-wall datum | high | mitigate | One source for slot and number: `_cut_keyway` takes `w = keyway_width_effective(p)` and `floor = bore_radius(p) + p.keyway_depth` (`model.py:242-243`), the same helpers `derive()` prints (`calc.py:81`, `:407`); `test_a_keyway_floor_sits_keyway_depth_outside_the_as_cut_bore_wall` (`test_model.py:280`) reads the floor and the bore wall back from the kernel and asserts depth-from-wall within TOL; the verifier's live `spur info` on the default keyed link printed `10.55` / `3.15` (`09-VERIFICATION.md`) | closed |
| T-09-04 | Tampering | Pre-v0.2 parts changed by the new code path | high | mitigate | `bore_mouth_limit` is `max(rim + chamfer, keyway_corner_radius(p))` (`calc.py:153-154`) and `keyway_corner_radius` is `0.0` without a keyway (`calc.py:87`), so the first operand returns unchanged; the replay compares every recorded field exactly and asserts `all(v is None for k, v in got.items() if k not in recorded)` (`tests/regression/test_pre_v0_2.py:49`); `git diff --stat b522044..HEAD -- tests/regression/pre_v0_2.json` is empty; 396 tests green including the 44-record replay | closed |
| T-09-05 | Tampering | The rim selector picking the keyway's edges or none, shipping an unchamfered or wrongly chamfered bore | medium | mitigate | `_build` runs `_cut_bore` (which chamfers, `model.py:217`) then `_cut_keyway` (`model.py:316-317`); a spy on `spur.model._bore_rim_edges` (`test_model.py:265-270`) observes the pre-keyway counts (`Counter({'CIRCLE': 2, 'LINE': 2})` keyed D-flat, `Counter({'CIRCLE': 2})` keyed round) in the real chamfered pipeline; the zero-edge `BuildError` guards are unchanged (`model.py:270`, `:303`) | closed |
| T-09-06 | Denial of service | A keyway conflict reaching the kernel before 09-03's rules exist | low | accept | The window closed inside the branch: 09-03's rules landed in `45b800b` / `4b6a5b9` before the phase lands as one squash (D-18); `_cut_keyway` cuts nothing unless both fields are above 0 (`keyed = p.bore_d > 0 and keyway_corner_radius(p) > 0`, `calc.py:306`) — see R-09-01 | closed |
| T-09-07 | Information disclosure | New field descriptions and help text | low | accept | `params.py:59`, `:65` — title, help and group are static string literals; nothing from a request is echoed — see R-09-02 | closed |
| T-09-08 | Denial of service | A keyway or chamfer conflict reaching the kernel: a worker slot and a timed build spent before failing, with a message naming no field | medium | mitigate | Seven rules in `check()` decided before any CAD: hex × keyway (`calc.py:239`), no bore (`:244`), half-set (`:249`), D-12 chamfer reach (`:289`), too wide (`:309`), into the D-flat's wall (`:320-323`), too deep (`:334`); `test_a_keyway_conflict_is_422_naming_its_fields` (`test_api.py:287`) covers the API, `test_cli.py:112` / `:137` pin exit 2 with the same sentence; the verifier executed all six keyway refusals and the D-12 refusal live on the CLI | closed |
| T-09-09 | Tampering | A keyway silently capped into a part the key does not fit | high | mitigate | No capping expression in any keyway rule (`awk '/keyway/ && /min\(/' src/spur/calc.py` → 0 lines); every conflict is `errors.append((sentence, fields))` → one `PydanticCustomError` → 422 / exit 2 naming the fields; one step inside the root rule prints the depth in full — `keyway_floor_to_wall == 18.5` at depth 9.35 (`test_calc.py:378`) | closed |
| T-09-10 | Tampering | D-12 refusing a round or D-flat link that builds today (L05) | medium | mitigate | The rule sits at the kernel's measured contact, `r_bore + p.bore_chamfer > pr.rf - ROOT_CONTACT` with `ROOT_CONTACT = 1e-9` mm (`calc.py:18-29`, `:289`; re-measured 2026-09-27 on 12 configurations by 20-step bisection: last failing gap −3.8e-8 mm, first building +1.9e-8 mm); one step inside builds (`test_calc.py:393`, `:428`), the exact contacts are refused (`:395`, `:407-415`); the kernel's own failure at contact is a test (`test_model.py:465`); the 44-record replay constructs every pre-v0.2 record through `GearParams` and is green, so no record is refused (smallest fixture gap 1.775 mm) | closed |
| T-09-11 | Information disclosure | Refusal messages | low | accept | Every keyway and D-12 sentence interpolates only `:g` / `:.2f` / `:.3f` floats and literal field names (`calc.py:293`, `:309`, `:323`, `:334-`); no request string reaches a message — see R-09-03 | closed |
| T-09-12 | Denial of service | The keyway's heaviest configuration versus `SPUR_BUILD_TIMEOUT` in production | medium | mitigate | 32-row sweep, every row recorded in `bench/RESULTS.md` § "Keyway bore build and export time (Phase 9)"; heaviest row 4.85 s of 30 s (`RESULTS.md:656`), quoted in L28 (`decision_log.md:1026`); the over-budget halt (09-04 Task 2) never fired | closed |
| T-09-13 | Tampering | A narrowed or re-picked sweep hiding a slow row | medium | mitigate | `test_the_keyway_bore_sweep_is_every_combination_with_the_largest_keyway_each_rule_allows` (`test_bench.py:79`) pins the file to the full cross product and proves each large keyway is refused at +0.05 mm on either field (`:124-125`), so a dropped or shrunk row fails `make verify` | closed |
| T-09-14 | Tampering | A README datum or example that drifts from the code, so a user measures the wrong dimension | medium | mitigate | `README.md:206` states `(bore_d + bore_clearance)/2`, the formula `test_model.py:280` measures; the keyed example (`README.md:110`) is executed by `test_cli.py:97`; DIN 6885 / ISO R773 / ANSI B17.1 are named as conventions only (`README.md:159`, `:207`, `:212`), no size is given; the code reviewer independently reproduced the documented numbers (`09-REVIEW.md`) | closed |
| T-09-15 | Repudiation | The phase's decisions lost after it lands | low | mitigate | L28 present (`grep -c '^## L28 — '` → 1); `git diff --numstat b522044..HEAD -- docs/architecture/decision_log.md` → 137 added, 0 deleted (append-only); the Phase 8 debt record moved to `resolved/` with `Resolved in: 4b6a5b9` | closed |
| T-09-SC | Tampering | package installs | low | accept | `git diff --stat b522044..HEAD -- pyproject.toml requirements.txt` is empty; no new `import`/`from` line in the `calc.py` / `model.py` / `params.py` diffs (`math.acos`, `math.hypot`, `cq.Solid.makeBox` are stdlib or the pinned kernel) — see R-09-04 | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-09-01 | T-09-06 | The window in which a keyway conflict could reach the kernel existed only between 09-02 and 09-03 on the phase branch; both landed before the squash, and `_cut_keyway` cuts nothing unless both fields are set | plan 09-02 (`<threat_model>`), closed by 09-03 at audit | 2026-09-27 |
| R-09-02 | T-09-07 | The two new fields' title, help and group are static string literals in `params.py`; they carry no request data, so there is nothing to disclose beyond what the schema already publishes | plan 09-02 (`<threat_model>`), unchanged at audit | 2026-09-27 |
| R-09-03 | T-09-11 | Refusal sentences interpolate formatted floats and literal field names only; a request string never reaches a message | plan 09-03 (`<threat_model>`), unchanged at audit | 2026-09-27 |
| R-09-04 | T-09-SC | No plan in the phase installs a package or changes a dependency range; the supply-chain surface is the one v0.1, Phase 7 and Phase 8 already audited | plans 09-01 … 09-05 (`<threat_model>`), unchanged at audit | 2026-09-27 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-27 | 16 | 16 | 0 | orchestrator (grep-depth, ASVS L1 short-circuit; tree `d12b1ee`) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-27
