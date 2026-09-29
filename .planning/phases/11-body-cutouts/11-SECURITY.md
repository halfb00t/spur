---
phase: "11"
slug: "body-cutouts"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-09-29"
verified: "2026-09-29"
audited_at_head: "8c05b42"
---

# Phase 11 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.
> Register authored at plan time (21 threats across 11-01 … 11-09, every disposition `mitigate`);
> verified at L1 grep depth after execution — every mitigation is present in the implementation or
> its record, so `threats_open: 0` and no auditor was spawned (secure-phase § 3 short-circuit).

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| query string / CLI flags → `GearParams` | Untrusted `hole_*`, `spoke_*`, `hub_d`, `rim_wall`, `hex_*` numbers become cutter geometry; Pydantic bounds (`ge`/`le`, `src/spur/params.py:136`, `src/spur/params.py:110`) then `GearParams._feasible` → `check()` are the single validation point | floats/ints, mm |
| `GearParams` → kernel | Only `check()`-accepted sets reach `_cut_body` (`src/spur/model.py:364`) inside a `BuildPool` worker under `SPUR_BUILD_TIMEOUT`; the honeycomb's lattice is enumerated in the serving process on every `/api/info` | validated parameters; a bounded cell enumeration |
| `calc` → user | `derive()`'s `cutout_hub_wall`, `cutout_rim_wall`, `spoke_fillet_effective`, `hex_cell_effective`, `hex_cell_count` and the warning sentences are numbers someone cuts metal to (L08) | floats rounded once; static sentences |
| kernel → printed part | Each pattern's solid is read back (faces, edges, volume, walls, fillet survival) and compared, not assumed (`tests/test_model.py:1188`) | topology counts, volumes |
| probe / sweep files → kernel | `bench/honeycomb_spike.py` and `bench/sweeps/{hole_cutout,spoke_cutout,honeycomb}.json` are hard-coded sets built on the developer's host; no user input crosses here | parameter names/values |
| measurement → published bound | The spike's cap becomes `HEX_CELL_CAP` (`src/spur/calc.py:51`); the sweep's over-budget rows became the `le` 60 / 40 every link is validated against | measured seconds → one constant, two bounds |
| a shareable link → a worker | Anyone who can reach the service can request any allowed set; its build time is bounded by the measured `le`s and by `SPUR_BUILD_TIMEOUT` | parameter sets |
| planning docs → phase verifier | The verifier grades against REQ-spoke-cutout and ROADMAP SC1–SC5 as amended by 11-01 | requirement text |
| records → the next reader | README, L30, the two architecture docs and RESULTS are what later phases plan from | static prose, executed CLI examples |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-11-01 | Tampering | ROADMAP.md written outside the tooling | low | mitigate | Task 3's commit `f0db74a` touches exactly `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md` (`git show --name-only f0db74a`); written through edit-phase's `write_updated_phase` with the milestone-scope read identical before and after (11-01-SUMMARY.md); SC2 edited by a scoped `Edit`, never a whole-file rewrite | closed |
| T-11-02 | Repudiation | Unrecorded criteria change or rule answer | low | mitigate | One Roadmap Evolution line in STATE.md (`.planning/STATE.md:294`); the human's `approved` answer on the spoke-arm `MIN_WALL` rule is recorded verbatim under Decisions Made in 11-01-SUMMARY.md, and 11-04 implements it (`tests/test_calc.py:956`) | closed |
| T-11-03 | Tampering | The spike record: a slow row dropped or re-run so the cap reads higher | high | mitigate | `bench/honeycomb_spike.py` times every row twice and keeps the slower (`bench/honeycomb_spike.py:94`); RESULTS § "Honeycomb cell-count spike (Phase 11, D-24)" carries the output verbatim, cap derived from the first over-budget row (120 at 7.15 s; next row 150 at 7.95 s, `bench/RESULTS.md:933`); the sweep-file pin `tests/test_bench.py:269` fails `make verify` if the cap row is dropped | closed |
| T-11-04 | Denial of service | A honeycomb at its cap overrunning SPUR_BUILD_TIMEOUT in production, unknown until measured | medium | mitigate | Cap set from measured rows inside 7.5 s at the heaviest web (module 10, 200 teeth, both recesses) and confirmed at module 1.75 (7.25 s); 11-06 re-measured every honeycomb sweep row at the cap — heaviest 8.65 s under load, 21 s inside the 30 s absolute (RESULTS § "Body cutout build and export time (Phase 11)"); the 1.15× overrun of the D-11 quarter-share was accepted by the human at 11-06's checkpoint and is recorded | closed |
| T-11-05 | Tampering | A hole set that breaches a wall reaching the kernel (a detached tooth or a sliver wall shipped as a valid-looking part) | high | mitigate | `check()`'s hub, rim and neighbour rules refuse before any build — 422 (`tests/test_api.py:336`) / exit 2 (`tests/test_cli.py:214`); the boundary one step either side (`tests/test_calc.py:758`); field bounds `_f(0, 0, 60, …)` (`src/spur/params.py:136`); pinned on the kernel by `tests/test_model.py:1026` | closed |
| T-11-06 | Tampering | A printed wall that differs from the cut part (L08) | medium | mitigate | `cutout_walls()` (`src/spur/calc.py:294`) reads the same datums `check()` refuses on; 11-08's built-solid proof reads the walls back off the solid (`tests/test_model.py:1188`) with a tripwire that fails when the cut is skipped while `derive()` still prints (`tests/test_model.py:1265`) | closed |
| T-11-07 | Denial of service | 200 holes on a large gear occupying a worker | medium | mitigate | Stronger than planned: D-18's gate fired (200 holes crossing the recess groove read 41.85 s) and the `le` is now 60 (`src/spur/params.py:136`; `tests/test_calc.py:854`); heaviest re-run row 11.79 s of 30 s (RESULTS § "Re-run after the gate"); `SPUR_BUILD_TIMEOUT` still bounds any one build (`src/spur/app.py:146`) | closed |
| T-11-08 | Tampering | A sector wire that self-intersects (bars overlapping at the hub, a fillet too large for its corner) shipped or crashing the kernel | high | mitigate | Opening, annulus, hub, rim and arm rules refuse before any build (`tests/test_calc.py:956`); fillet capped to 0.45 of the shared dimension (`src/spur/calc.py:227`; `tests/test_calc.py:1000`); the cap builds on the most awkward sectors the rules allow (`tests/test_model.py:1088`); `_fillet_corner`'s tangent-arc algebra hand-checked against a 3-4-5 case (11-04-SUMMARY.md) | closed |
| T-11-09 | Tampering | The fillet printed differs from the fillet cut | medium | mitigate | `model.py` and `derive()` both read `spoke_fillet_effective(p)` (`src/spur/calc.py:356`; used at `src/spur/model.py:44`); served number pinned by `tests/test_api.py:351`; 11-08 reads the filleted-spoke row back off the built solid as a pinned kernel measurement (`tests/test_model.py:1188`) | closed |
| T-11-10 | Denial of service | 200 sectors with a recess cost about a minute (planning probe) | high | mitigate | Measured 63–69 s at 200 sectors crossing the recess band; D-18's gate lowered `spoke_count` to `le` 40 (`src/spur/params.py:110`); heaviest re-run row 18.52 s of 30 s under load 32 (RESULTS § "Re-run after the gate"); the arithmetic stack with Phase 10's 14.87 s chamfer row (33.39 s) is filed as must-debt with Phase 12's composed measurement as its trigger (`docs/tech_debt/active/2026-09-29-spoke-le-arithmetic-total-crosses-30s-under-load.md`) — see R-11-02 | closed |
| T-11-11 | Denial of service | A tiny hex_cell on a 2 m gear asking the serving process to enumerate hundreds of thousands of cells per keystroke | high | mitigate | `cell_count_floor` skips every size that cannot fit without enumerating (`src/spur/calc.py:444`); exact enumeration runs only near the cap (`src/spur/calc.py:485`); `derive()`'s cost at the heaviest input measured at 7.371 ms best-of-5 (RESULTS § "Honeycomb cell-count spike"); field bounds (`tests/test_calc.py:1288`) | closed |
| T-11-12 | Denial of service | A honeycomb at its cap overrunning SPUR_BUILD_TIMEOUT | medium | mitigate | `HEX_CELL_CAP = 120` written from the measured record (`src/spur/calc.py:51`); the identity between the constant and RESULTS' `**Cap:**` line is checked by 11-05's verify; 11-06's honeycomb sweep runs at the cap (`tests/test_bench.py:269`), heaviest 8.65 s of 30 s | closed |
| T-11-13 | Tampering | A count, size or wall printed that differs from the cells cut | medium | mitigate | One `hex_cells(p, rf)` result feeds `check()`, `derive()` and `model.py` (`src/spur/model.py:349`); walls measured on the cut cells, not the circumradius (`tests/test_model.py`); 11-08 reads count and walls back off the built solid with a tripwire (`tests/test_model.py:1265`) | closed |
| T-11-14 | Denial of service | An allowed cutout configuration that takes over 30 s holds a worker to the timeout and is killed, a 503/504 for a link the tool said was valid | high | mitigate | The sweep measured each pattern's heaviest allowed rows (24 rows, RESULTS § "Body cutout build and export time (Phase 11)"); four rows over 30 s halted for D-18's decision; the human chose `lower-le` (spoke 40, hole 60) and the re-run proves every allowed row inside 30 s (heaviest 18.52 s spoke, 11.79 s hole, 8.65 s honeycomb); the sweep files pin the new bounds (`tests/test_bench.py:189`) | closed |
| T-11-15 | Tampering | An over-budget row dropped or re-run until green so the gate stays quiet | high | mitigate | `bench/build_time.py` times every row before deciding (runner unchanged since `b86a0e9`, checked by 11-06's verify); the first run is never overwritten — the re-run is appended (`git diff --numstat 3e00496 7980b4d -- bench/RESULTS.md` → 244 added, 0 deleted); the four over-budget rows stand in the record with the decision beneath them | closed |
| T-11-16 | Tampering | A selector that silently takes a cutout edge (an unchamfered or wrongly chamfered part shipped as valid) | high | mitigate | Real-pipeline spy pins every selector's exact edges with every pattern, bore shape and recess setting — 19 rows (`tests/test_model.py:314`); tip selector takes exactly 2×teeth arcs with each cutout (216/264/338 measured faces, 11-07-SUMMARY.md); the existing empty-selection `BuildError` guards stay (`src/spur/model.py:440`) | closed |
| T-11-17 | Denial of service | A tangent or boundary configuration the rules allow that the kernel cannot cut, surfacing as a BuildError after a timed build | medium | mitigate | 18 boundary rows built one field-step either side of every wall rule (`tests/test_model.py:999`, `tests/test_model.py:1026`); 10 tangent-cutter rows built without a fuzzy boolean — no `tol=` in `model.py` (0 hits), measurement comment above `_cut_body`'s `cut()` instead (`src/spur/model.py:364`) | closed |
| T-11-18 | Tampering | A cut silently skipped or misplaced while derive() prints its numbers | high | mitigate | Built-solid proof reads faces, edges, volume and walls back off each pattern's solid — sharp-spoke and honeycomb volumes against closed-form formulas to 1e-9 mm³ (`tests/test_model.py:1188`); hole 0 / arm 0 on +X and cell flats on ±X probed; tripwire with `_cut_body` patched to a no-op (`tests/test_model.py:1265`); same link builds the same solid twice (`tests/test_model.py:1289`) | closed |
| T-11-19 | Tampering | A cutout that strips the recess floor fillet from surviving edges, shipped as a valid part | medium | mitigate | Survival proof counts zero sharp floor-to-wall circles and pins the TORUS count across 13 pattern × bore-shape rows with both recesses (`tests/test_model.py:1352`); its tripwire (`recess_fillet` patched to 0.0) shows `assert sharp == 0` catch the skip (11-08-SUMMARY.md) | closed |
| T-11-20 | Repudiation | A number in L30 or the README that no measurement backs | medium | mitigate | L30 present (`docs/architecture/decision_log.md:1140`); every number cites a SUMMARY sha or a RESULTS section (21 citation hits in the section at audit); the README's three cutout examples run in the gate (`tests/test_cli.py:81`), each asserting a >1000-byte file and no warning | closed |
| T-11-21 | Tampering | A decision-log entry edited instead of appended | low | mitigate | `git diff --numstat b86a0e9 HEAD -- docs/architecture/decision_log.md` → 146 added, 0 deleted (append-only); 11-09's verify asserts the 0 | closed |
| T-11-SC | Tampering | package installs | low | accept | `git diff --stat b86a0e9 HEAD -- pyproject.toml requirements.txt uv.lock` → empty; new third-party `import`/`from` lines in the `src/spur/` diff since `b86a0e9` → 0 — see R-11-01 | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

Register notes: T-11-07's plan-time mitigation read "le 200 per D-18"; the executed mitigation is stronger (`le` 60 after the gate fired). Every other row's mitigation is as planned. No SUMMARY carries a `## Threat Flags` section — no executor surfaced a new threat during execution.

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-11-01 | T-11-SC | No dependency or lockfile changed and no new third-party import entered `src/spur/` in this phase; nothing to verify beyond the diff | orchestrator (audit) | 2026-09-29 |
| R-11-02 | T-11-10 | The heaviest `le`-40 spoke row (18.52 s) plus Phase 10's 14.87 s chamfer row sums to 33.39 s — an arithmetic total under load 32, not a composed build. Accepted for this phase because the row is inside 30 s alone; filed as must-debt with Phase 12's composed measurement as the trigger (`docs/tech_debt/active/2026-09-29-spoke-le-arithmetic-total-crosses-30s-under-load.md`, `docs/tech_debt/INDEX.md:30`) | human (11-06 Task 2 decision) + orchestrator | 2026-09-29 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-29 | 22 (21 planned + T-11-SC) | 22 | 0 | execute-phase orchestrator (secure-phase § 3 short-circuit: register authored at plan time, ASVS L1, grep-depth evidence per row; `make verify` 621 passed in 177.62s at `8c05b42`) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-29
