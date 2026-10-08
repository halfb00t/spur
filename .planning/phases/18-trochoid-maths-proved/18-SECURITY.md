---
phase: "18"
slug: "trochoid-maths-proved"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-08"
verified: "2026-10-08"
---

# Phase 18 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Register origin: authored at plan time (every PLAN.md carries a `<threat_model>` block; IDs T-18-01..T-18-16 each used once across the five plans, plus the reserved per-plan supply-chain row T-18-SC). Verification depth: ASVS L1 (grep-level evidence against the implementation and the plan SUMMARYs), run by the secure-phase step of the execute-phase verification sequence on 2026-10-08.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| `GearParams` → `calc` | every input is validated once at `GearParams`; `rho` is an explicit float argument no user can set in this phase | validated gear parameters, floats |
| `calc` result → a printed number (Phase 19) | a number this module returns is a number someone will cut metal to (L08) | `RootCurve` points, `RootMode.reason`, warning sentences |
| `root_mode` → Phase 19 consumers | the reason and the mode are what the outline, the printed numbers and the warnings will read | `RootMode` |
| the allowed box → the generator | every `GearParams`-valid gear and every rho a Phase 19 field could pass | the sweep product |
| the commit gate | the sweep's cost lands on every commit (L36's 30 s budget) | wall time |
| third-party code (freecad.gears, GPL-3.0) → this repository | only its printed numbers may cross, never its code | 60 literal points with provenance |
| a published table → a test bar | a four-decimal printed value is rounding-limited | KISSsoft / STACK figures |
| a measured figure → a human decision | the step and the costs are what Phase 19's planning reads | step tables, per-call costs |
| the gate's warning filter | `filterwarnings = error` is what makes the suite refuse unraisable exceptions | pytest config |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-18-01 | Tampering | `_trochoid_point`, `_junction` (NaN/inf/domain error reaching a returned number) | medium | mitigate | `beta_end = math.pi / 2 - c.pr.alpha` (`calc.py:1419`); `Profile.half_angle` called only at R ≥ rb (`test_profile_half_angle_is_never_asked_below_the_base_circle`); beta form has no `\|C − I\| = 0` division; tracer asserts every point finite (`test_trochoid.py:221`) | closed |
| T-18-02 | Denial of service | `_bisect`, `_waist` refinement | low | mitigate | fixed `for _ in range(60)` halvings (`calc.py:1206`) and 60 golden-section steps (`calc.py:1378`); fixed sample count; no data-dependent iteration | closed |
| T-18-03 | Tampering | `profile()` refactor moving the fixture (L05/L26) | high | mitigate | `_dedendum` / `_pitch_thickness` shared by `profile()` and `cutter()` (`calc.py:113,120,132-134,1283-1284`); pre-v0.2 fixture replays in `make verify.fast` at every commit; SC5 check printed `SC5 holds` after every task (fixture byte-identical) | closed |
| T-18-04 | Tampering | a plausible wrong curve (gouge or missed junction) | high | mitigate | oracle with neighbouring teeth reads every tracer point within 1e-9 mm (worst 9.99e-16 mm) and a negative control reads a gouge (−3.695e-3 mm); `curve invalid` refuses non-rising / over-tip / past-centreline / past-junction curves (`calc.py:1470`); refusals return `None` plus a named reason | closed |
| T-18-05 | Tampering | `root_mode` (wrong root silently, or the three undercuts mixed) | high | mitigate | one fixed order of six named reasons (`RootReason`, `calc.py:1242-1243`); edges pinned one tooth step and one field step either side; fixture's 44 records radial when nothing requested; shipped warning proven distinct from the cutter's onset (`test_the_cutter_s_undercut_is_not_the_shipped_warning_s_undercut`) | closed |
| T-18-06 | Repudiation | `root_warnings` sentence drift | low | mitigate | every expected sentence captured from `root_warnings` with its capture date 2026-10-08, never typed (`test_trochoid.py:140,185,486,525`) | closed |
| T-18-07 | Tampering | `_waist` (a severed tooth missed between samples) | high | mitigate | golden-section refinement between the smallest sample's neighbours (`calc.py:1356-1381`); oracle with neighbours (±3-span roll window after 18-04) agrees on all 73 severed teeth and the thin-but-whole rows | closed |
| T-18-08 | Tampering | `_junction` near the double root (degenerate bracket returning a plausible junction) | high | mitigate | decision is the sign of xi; bracket attempted only outside `TROCHOID_JOIN_EPS · rb` (`calc.py:71,1445`), the constant measured in 18-03 (worst loss 5.6e-6·rb vs 1e-4, > 10× headroom); a lost bracket is `bracket degenerate` (`calc.py:1447`), reached by a test | closed |
| T-18-09 | Denial of service | the gate sweep pushing the commit gate past 30 s (L36) | medium | mitigate | call time measured at `-n 8`: 1.7 s (D-13 line 2.0 s, no stride sample needed); `make verify.fast` wall 14.4–14.8 s, under 30 s (18-03 SUMMARY, RESULTS.md) | closed |
| T-18-10 | Tampering | an invalid construction hidden or clipped inside the box | high | mitigate | `curve invalid` refuses it; sweep counts and lists every refusal in the committed `investigation/18-03-refusals.tsv` (8,228 rows); unnamed reason would have stopped at Task 3 — the sweep reported none (0 degenerate, 0 invalid) | closed |
| T-18-11 | Tampering | bar constants placed to pass | medium | mitigate | each bar set from two recorded numbers with headroom beside it (`JUNCTION_BAR_*` 2.4e4× / 562×, `DIRECTION_BAR_RAD` 72×, `SWEEP_BAR`, `ORACLE_BAR_MM` 220× tripwire, T3 bars, T4 1.39× accepted at D-15); a tripwire per bar seen red; the L33 D-06 checkpoint was not reached (18-04 SUMMARY) | closed |
| T-18-12 | Repudiation / compliance | T3 — GPL-3.0 code entering the tree | high | mitigate | freecad.gears run in scratch directories outside the repository with `-I`; only 60 literals entered with source file, commit `4cc4b1a233c232e15c3fdfb8a35909aa0d828796` and licence; verified 2026-10-08: no tracked path names pygears/freecad (`git ls-files`), no tracked Python file imports them (`git grep`) | closed |
| T-18-13 | Tampering | a tautological oracle sharing the implementation | high | mitigate | `tests/trochoid_oracle.py` imports only `math` (and `__future__`), nothing from `spur` (AST-checked in 18-01's verify); three negative controls read gouges; 73 of 73 severed teeth agree over the whole product | closed |
| T-18-14 | Repudiation | cost figures without their load becoming stale claims | low | mitigate | every figure recorded with 1-minute load before/after and the date in `bench/RESULTS.md` and in `derive()`'s docstring (14.7 µs at load 14.4, 2026-10-08; 9.19 / 11.5 kept as history) | closed |
| T-18-15 | Tampering | the D-05 step line chosen after the numbers | medium | mitigate | `premise_holds` and its pin committed in `8badc55` (08:47:54) before the tables in `383d04b` (08:51:56); the plan's verify checks the commit order; both tables and the verdict went to the human with no default (`d05-hold`, 2026-10-08) | closed |
| T-18-16 | Tampering | `pyproject.toml filterwarnings` widened enough to hide a real failure | medium | mitigate | human chose `debt-redefer`; no `filterwarnings` change on the phase branch (`git diff 26b9505..HEAD -- pyproject.toml` empty for it) | closed |
| T-18-SC | Tampering | npm/pip/cargo installs (all five plans) | low | accept | nothing installed; stdlib `math`, `dataclasses`, `typing`, `random`, `statistics`, `csv`, `multiprocessing` only; `requirements.txt` stays at 31 pins; freecad.gears' numpy need met by the existing `.venv` for the one-off run and never declared | closed (accepted risk R-18-01) |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-18-01 | T-18-SC | Supply-chain row reserved per plan; the phase installs nothing, adds no dependency and keeps `requirements.txt` at 31 pins (SC5 held after every task). Residual risk is the existing pin set, owned by the milestone. | plan author (18-CONTEXT / plans), confirmed by secure-phase | 2026-10-08 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-08 | 17 | 17 | 0 | secure-phase step (execute-phase verification sequence), L1 grep-depth |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-08
