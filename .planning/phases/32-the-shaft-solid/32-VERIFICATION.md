---
phase: 32-the-shaft-solid
verified: 2026-10-27T12:00:00Z
status: passed
score: 4/4 must-haves verified
covered_files:
  - ".planning/phases/32-the-shaft-solid/32-01-PLAN.md"
  - ".planning/phases/32-the-shaft-solid/32-01-SUMMARY.md"
  - ".planning/phases/32-the-shaft-solid/32-02-PLAN.md"
  - ".planning/phases/32-the-shaft-solid/32-02-SUMMARY.md"
  - ".planning/phases/32-the-shaft-solid/32-03-PLAN.md"
  - ".planning/phases/32-the-shaft-solid/32-03-SUMMARY.md"
  - ".planning/phases/32-the-shaft-solid/32-04-PLAN.md"
  - ".planning/phases/32-the-shaft-solid/32-04-SUMMARY.md"
  - ".planning/phases/32-the-shaft-solid/32-05-PLAN.md"
  - ".planning/phases/32-the-shaft-solid/32-05-SUMMARY.md"
  - ".planning/phases/32-the-shaft-solid/32-06-PLAN.md"
  - ".planning/phases/32-the-shaft-solid/32-06-SUMMARY.md"
  - "Makefile"
  - "bench/RESULTS.md"
  - "bench/__init__.py"
  - "bench/build_time.py"
  - "bench/export_cost.py"
  - "bench/sweeps/shaft.json"
  - "pyproject.toml"
  - "src/spur/din5480.py"
  - "src/spur/model.py"
  - "src/spur/parts.py"
  - "src/spur/records.py"
  - "src/spur/shaft_calc.py"
  - "src/spur/shaft_model.py"
  - "src/spur/shaft_params.py"
  - "tests/shaft_oracle.py"
  - "tests/test_bench.py"
  - "tests/test_din5480.py"
  - "tests/test_hooks.py"
  - "tests/test_pool.py"
  - "tests/test_records.py"
  - "tests/test_seam.py"
  - "tests/test_shaft_calc.py"
  - "tests/test_shaft_model.py"
  - "tests/test_shaft_params.py"
covered_digest: "v3:sha256:07c4e3453b2b3cea14c300ee266c1be8d81bbdcfd845ef3342f20a9b8200c3aa"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 32: The Shaft Solid Verification Report

**Phase Goal:** A shaft built from Phase 31's maths is a valid solid (splined section, plain shank, end chamfer) that exports to STL and STEP, whose volume matches a closed form, and whose heaviest allowed build is measured against the memory ceiling and the timeout, with the field bounds set from that sweep. The user reaches the downloads through Phase 33's interfaces.
**Verified:** 2026-10-27
**Status:** passed (with 2 open review warnings, see Advisory)
**Re-verification:** No, initial verification

## Goal Achievement

### Observable Truths (ROADMAP success criteria, the contract)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A shaft built through `model` is a valid solid and exports valid STL and STEP of splined section, shank and chamfer; volume matches a kernel-free closed form within a recorded tolerance | VERIFIED | I built 5 shafts through `model.build` / `model.export` myself (default; shank_d = tip_d; W 10x0.5x18; W 14x2x6; W 84x1x82 with shank_d 84): all `isValid()`, volume vs `tests/shaft_oracle.py` closed form -4.0e-9, -4.2e-9, -1.3e-9, -1.5e-6, +3.2e-10; STEP starts `ISO-10303-21;` and carries `MANIFOLD_SOLID_BREP`; STL bytes returned. Oracle imports nothing from spur (stdlib only). Tolerance `VOLUME_REL = 1e-4` is recorded beside the constant with its measured worst and ratio. `pytest tests/test_shaft_model.py tests/test_shaft_calc.py tests/test_shaft_params.py tests/test_bench.py tests/test_seam.py`: 345 passed. |
| 2 | Joins and chamfer are honest: shank_d == tip_d builds valid; applied chamfer read back from the solid; chamfer past tooth height capped and warned, never a silent bad solid | VERIFIED | `test_every_shank_regime_builds_with_the_closed_form_volume` covers shank = tip, = root, tip +/- 1e-9, one ulp, 850, shank_length 0; seen red against `.clean()`. My own readback on the built solid: default eff 1.0 / end-face radius read-back 1.0; W 10x0.5x18 request 1.0 -> eff 0.5 / readback 0.5 with a warning naming `end_chamfer`, the cap and tooth height; request 3 on default -> 1.25 / 1.25 with warning; `end_chamfer=0` -> None, 0 CONE faces. Shaft_model uses `Shape.fuse` and `Shape.intersect` only (AST walk in close checks; I read the file: no clean/chamfer/union/glue). |
| 3 | Heaviest allowed shaft measured: build time, worker memory, STL size in `bench/RESULTS.md` within L17's ceiling and L37's 30 s; bounds set from the sweep and pinned by a test | VERIFIED | `### The heaviest shaft (32-05)` holds per-row `--fresh` tables on macOS and Linux (9 shaft rows + 199-tooth gear reference): heaviest 2.23 s macOS / 5.44 s Linux vs 30 s; peak RSS max 1066 / 1309 MiB vs gear 1356 / 1449 MiB in the same run; largest STL 3.3 MB. Sweep reaches all four solid-field `le` (pinned by `test_the_shaft_sweep_reaches_every_solid_field_bound_and_carries_the_gear_reference`); bound values pinned in `tests/test_shaft_params.py` with a comment citing the section. D-09 outcome "no bound moved" is recorded (`_f(...)` lines unchanged since Phase 31; the bounds were confirmed by sweep, not derived). Caveats are written in the section itself (see Advisory). |
| 4 | Gate delta recorded against Phase 31's/32-01 baseline on the same host; Phase 30 check green | VERIFIED | `### The gate baseline (32-01)` (2387 passed, 251.15 s) and `### The gate delta (32-06)` (2644 passed, 233.83 s, real 234.78 s, -7.25 %, inside the 8 % spread so no speed claim). Two interim plan readings above 300 s (358.81 s, 312.50 s) are written down and not trimmed. I re-ran `make lint-imports` (`Contracts: 10 kept, 0 broken.`) and `make gear.unchanged` (byte-equal to v0.6, 8723 bytes schema); `git diff --exit-code v0.6 -- tests/regression/ .github/workflows/ci.yml requirements.txt src/spur/calc.py src/spur/params.py` exits 0. Orchestrator's full `make verify` (2644 passed, coverage 98.22 %) not re-run by me; consistent with the 32-06 log and my subset run. |

**Score:** 4/4 truths verified (0 behavior-unverified)

### Plan-level must-haves spot-checked

| Must-have | Status | Evidence |
|-----------|--------|----------|
| `model._build` dispatches on `isinstance(p, ShaftParams)` as first statement; gear lines unchanged | VERIFIED | `src/spur/model.py:780`; diff vs b4cfd71 adds only the import, `Part` typing and the dispatch. |
| `Part = GearParams \| ShaftParams`; only edge `spur.model -> spur.shaft_model` ignored | VERIFIED | `parts.py`; `pyproject.toml:265`; lint-imports 10 kept. |
| `pool.py`, `app.py`, `cli.py`, `din5480_tables.py` untouched since Phase 31 | VERIFIED | `git diff --stat b4cfd71 HEAD` over the four files is empty. |
| No shaft route yet | VERIFIED | Phase 33 owns routes; close check 4 (grep) no match. |
| `end_chamfer_effective` as 13th key, human picks A1 B1 C1 D1 honoured | VERIFIED | 32-01-SUMMARY `## Decision result`; decision commits (8409e5a, f2141af) precede the feature commit 1923016. |
| Cone-start band guard and volume bracket guard exist and were seen red | VERIFIED | `shaft_model.py` guards; `### Seen red once (Phase 32)` rows for both. |
| Mesh readback of chamfer in STL, bars from measured worsts (MESH_PREVIEW_REL = 6e-3 human decision) | VERIFIED | `test_the_shaft_stl_carries_its_chamfer_at_the_end_face`; constants carry measurements. |

### Requirements Coverage

| Requirement | Source Plans | Description | Status | Evidence |
|-------------|--------------|-------------|--------|----------|
| REQ-shaft-solid | 32-01..32-04, 32-06 | valid STL and STEP of splined section, shank, chamfer; volume vs closed form; chamfer read back | SATISFIED | Truths 1 and 2. REQUIREMENTS.md already `[x]` / Complete. |
| REQ-shaft-build-measured | 32-01, 32-05, 32-06 | heaviest build measured in RESULTS.md within L17 and L37; bounds from sweep | SATISFIED | Truth 3. REQUIREMENTS.md `[x]` / Complete. |
| REQ-gate-cost-recorded | 32-01, 32-06 | per-phase gate time recorded; closes at milestone reading | OPEN BY DESIGN (confirmed) | REQUIREMENTS.md line `- [ ] REQ-gate-cost-recorded` and traceability row "Phase 34 / Pending"; the Traceability prose says it is cross-cutting and closes at Phase 34; 32-06 section states "stays open and closes at Phase 34's milestone reading". Phase 32's reading is recorded (truth 4). Not orphaned: no other REQUIREMENTS.md ID maps to Phase 32. |

Orphaned requirements: none (Phase 32 maps exactly REQ-shaft-solid and REQ-shaft-build-measured).

### Prohibitions

| Prohibition | Tier | Verdict |
|-------------|------|---------|
| 32-01: no subtraction from unsourced 2387 / 221.86 s | test | Held: RESULTS.md states the figure is unused; delta is against the logged 32-01 reading. |
| 32-02 / 32-03 / 32-04 (applied chamfer never above caps or printed when nothing cut; no cap without warning, no 422; no fillet/notch claim; no invalid or plausible-wrong solid; no clean/union/chamfer/glue; no non-nominal thickness; gear unchanged; kernel doorway only via model) | test | Held: each has a named test seen red once (table above), re-run green; AST check and lint-imports confirm the routes. |
| 32-01: no chamfer number/key/slug before the human picks | judgment | Non-authoritative LLM verdict: held. Git order shows the human's decision recorded before the first src commit. Flagged for completeness as a judgment-tier item; evidence is a git-history fact. |
| 32-05: no 503 documented, no spline bound moved without asking | judgment | Non-authoritative LLM verdict: held. The D-09 trigger never fired; `_f(...)` bounds in `shaft_params.py` are unchanged vs Phase 31 and no 503 text appears in the Phase 32 RESULTS sections. Flagged as judgment-tier, deterministic evidence. |

### Anti-Patterns Found

TBD/FIXME/XXX/TODO scan over `shaft_model.py`, `shaft_calc.py`, `shaft_params.py`, `bench/build_time.py`, `tests/test_shaft_model.py`: no match. No stubs; `shaft_model.py` coverage 96.77 % (two unreached guard lines, filed as nice debt `2026-10-27-shaft-model-two-guard-lines-no-passing-test-reaches.md`).

### Advisory (warnings, not blocking)

1. **WR-01 (review, open): `_guard_volume` bounds the cone's removal only from above.** I read `shaft_model.py:136-141` and confirm the reviewer's reading: the bracket is `[upper - c*(area - pi rf^2), upper]`, so a solid whose chamfer was never cut sits on `upper` and passes the build-time guard. Judgment: this does **not** undermine the goal's "end chamfer" claim or L08 as shipped. (a) The cone is one deterministic `Shape.intersect`; my four builds with a chamfer and the reviewer's ~400 random builds all cut it, and I read the applied chamfer back from the built end face on each of my rows (equal to `end_chamfer_effective` to 6 places). (b) The test suite reads the applied chamfer back from the solid and the STL (`test_the_default_shaft_reads_back_its_applied_chamfer`, `test_the_shaft_stl_carries_its_chamfer_at_the_end_face`), and the volume tests on the cap rows are against the cut closed form, so a regression that dropped the cone fails there. (c) What is missing is a run-time belt for a future kernel no-op. Recommend fixing before Phase 33 exposes downloads (`cut <= 0` check when `c > 0`, plus a test); not a blocker, and the disposition is still `open`.
2. **WR-02 (review, open): bench `_time_fresh` swallows child stderr.** Bench tooling only; no effect on the solid or the recorded numbers.
3. **Measurement caveats, recorded in the RESULTS section itself:** Linux sweep is linux/amd64 emulated on arm64 (walls inflated, memory figures unaffected by emulation of timing only in principle); one run per host; the 4-entry solid-cache fill (up to 4 x ~850 MiB resident on Linux) is not measured, though the shared cache is the gear's own existing behaviour and one shaft entry holds about what one 199-tooth gear entry does (869 vs 844 MiB). The 30 s and ceiling margins (5.5x on emulated Linux) are wide enough that none of these changes a verdict.
4. IN-01, IN-02 (info): stale comments; `"part": "gear"` row wording. Open, cosmetic.

### Human Verification Required

None. Everything the phase claims is exercised by a test or a command I ran. Phase 33 owns the user-facing download interfaces.

### Gaps Summary

No gaps. All four ROADMAP success criteria and both phase requirement IDs are met in the codebase. REQ-gate-cost-recorded is correctly open until Phase 34. The two warnings (WR-01, WR-02) are carried in `32-REVIEW-DISPOSITION.md` as open and should be triaged (WR-01 ideally fixed before Phase 33).

---

_Verified: 2026-10-27_
_Verifier: Claude (gsd-verifier)_
