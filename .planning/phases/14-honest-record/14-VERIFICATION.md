---
phase: 14-honest-record
verified: 2026-10-03T12:00:00Z
status: human_needed
score: 4/5 must-haves verified
covered_files:
  - .planning/phases/14-honest-record/14-01-PLAN.md
  - .planning/phases/14-honest-record/14-01-SUMMARY.md
  - .planning/phases/14-honest-record/14-02-PLAN.md
  - .planning/phases/14-honest-record/14-02-SUMMARY.md
  - .planning/phases/14-honest-record/14-03-PLAN.md
  - .planning/phases/14-honest-record/14-03-SUMMARY.md
  - README.md
  - docs/architecture/decision_log.md
  - src/spur/calc.py
  - src/spur/model.py
  - tests/test_calc.py
  - tests/test_model.py
covered_digest: "v2:sha256:0ba6373cc2d3bdfe49d3b89ec2395f18efbfbd55884291949991430c16ee46e6"
behavior_unverified: 0
overrides_applied: 0
re_verification: false
gaps: []
human_verification:
  - test: "Decide on the plan 14-02 deviation: the shared cutout assertion gained opt-in volume_rel, and 15 composed rows (12 tip-chamfer, 3 single-sided-recess) assert at rel=1e-6 where the plan said abs=1e-9 'nowhere at a relative tolerance'"
    expected: "Accept it as an override (suggested YAML below), or require the 15 literals re-pinned at full precision"
    why_human: "An override must be accepted by a named person. SC3 as written is met; only the plan's stricter must-have is deviated from."
  - test: "Decide how to correct L33's sentence 'all three skip-the-cutout tripwire rows run at abs=1e-9' (WR-02). Either reword it, or make the rows discriminating (closed-form d_volume for holes and cells, or assert the volume delta directly)"
    expected: "L33 states only what the rows prove, or the rows prove what L33 states"
    why_human: "Doc-versus-code conflict in a phase whose purpose is an honest record (CLAUDE.md: stop and ask). Choosing between editing the log and editing the tests is a human call."
  - test: "Run the four abs=1e-9 rows on the platform CI uses (ubuntu-latest, x86_64) and record the gaps next to the arm64 ones (WR-01)"
    expected: "All four kernel-to-formula gaps stay far below 1e-9 mm3 on CI"
    why_human: "Cross-platform float behavior cannot be checked on this host. Measured margin here is about 100x, so a CI red is unlikely but unproven."
  - test: "Judge the unenforced test-tier prohibition: 'MUST NOT put a number in README that this plan's tests do not prove' (REQ-readme-root-zone-states-the-limit)"
    expected: "Accept the verifier's manual check (README bullet carries only 1.188, 1.25 and 0.125; every one is a test row's value; no micron figure), or ask for a repo test that guards README's numbers"
    why_human: "No repo test enforces it (grep of tests/ finds no README-number check). Only the plan-time verify command did. Flagged as unverified-prohibition, never silently passed."
---

# Phase 14: Honest Record Verification Report

**Phase Goal:** Every claim this tool or its docs make about geometry it already builds is either true or flagged: the root lead-in warns when it rises above the pitch circle, README states the real limit instead of the general "non-working root zone" claim, and the filleted-spoke removed-volume proof is checked against an independent closed form instead of a pinned literal.
**Verified:** 2026-10-03
**Status:** human_needed
**Re-verification:** No, initial verification

All four ROADMAP success criteria hold in the code. No gap blocks the goal. Four items need a human decision, listed under Human Verification Required.

## Gate

`make verify` (ruff, mypy --strict, import contracts, unfinished-work scan, pytest), run by the verifier after reading, no source modified:

```
======================= 927 passed in 227.16s (0:03:47) ========================
```

Exit 0. Focused: `pytest tests/test_calc.py -k root_lead_in` gives `15 passed`. `pytest tests/test_model.py -k "each_cutout_is_exactly or cutout_proof_fails"` gives `8 passed`.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC1: `derive().warnings` carries the lead-in sentence naming the height (mm, 3 dp) and that the chord deviates from the involute, at the 3 debt configurations plus one field step either side; pure `calc.py`, no outline change | VERIFIED | `src/spur/calc.py:975-985`: `h = spline_start(pr, rfil) - pr.r`, `if round(h, 3) > 0`. Verifier re-ran the three configs: default h=-1.1875, `[]`; `{1.0, 14.5}` h=0.5625, "reaching 0.562 mm"; `{0.75, 20}` h=0.125, "reaching 0.125 mm". 15 test rows pass: three debt configs, three driver pairs (profile_shift, root_fillet, module), mid-tooth trio, zero fillet, print-resolution pair. No `cadquery` import in calc.py. Outline untouched (model.py diff is docstring-only). Wording question below. |
| 2 | SC2: README's root-fillets bullet states the real condition, cites `warnings`, no unmeasured number | VERIFIED | README diff: "1.188 mm below the pitch circle on the default gear, but above it ... when the root fillet exceeds half the dedendum, `(1.25 − x)·m / 2`, and the profile shift `x` exceeds 0.125 ... `warnings` says how far." Numbers are 1.188, 1.25, 0.125, each a tested row. Verifier swept 3,930 grid points (x -0.6..1.0, m 0.5..10, pa 14.5..35, z 8..120, fillet 0..3): warning fires iff effective fillet > (1.25-x)·m/2 and x > 0.125 (at 3 dp), 557 firings, 0 inconsistencies. README's condition is true. |
| 3 | SC3: filleted-spoke row asserted against an independent closed form at abs=1e-9; literal demoted; tripwire goes red on a perturbed `inside=True` root | VERIFIED | `_filleted_spoke_volume` (`tests/test_model.py:1126`) uses a polar construction; AST holds no `_fillet_corner` or `cq` name. Literal `2934.725405` appears once, in the proof's docstring. All four proof rows hit `pytest.approx(d_volume, abs=1e-9)` by default (`:1258`). Verifier measured oracle-vs-kernel on three further configs (8 spokes, 3 spokes, 6 spokes, fillets 0.8/1.5/0.3): gaps 2.3e-13, 3.6e-12, 1.8e-12, so the oracle is general and not tuned to one angle. Tripwire, re-run by hand: perturbed removed volume is off by -2.522e-4 mm3, passes `rel=1e-6`, fails `abs=1e-9`; loosening the bar back makes the test red. See deviation below. |
| 4 | SC4: both debt files retired with sha; fixture byte-unchanged; new Lxx answers L30 without touching it | VERIFIED | Both files are in `docs/tech_debt/resolved/` (`Resolved in: 825095f`, `61e1bea`), absent from `active/`, once each in INDEX Resolved with matching shas. `git diff --quiet 5d9e907 -- tests/regression/pre_v0_2.json src/spur/params.py` exits 0. `git diff --numstat 5d9e907 -- docs/architecture/decision_log.md` gives `97 0`, so append-only. L33 header names L09, L10, L30. `src/` differs from 5d9e907 only in calc.py and model.py (docstring). |
| 5 | Plan 14-02 must-have: `_assert_the_cutout_is_what_derive_prints` asserts at abs=1e-9 on all four rows "and nowhere at a relative tolerance" | UNCERTAIN (WARNING, override suggested) | The four rows are at abs=1e-9. The shared function also has `volume_rel`; `:1631` and `:1678` pass `volume_rel=1e-6` for 15 rows (12 + 3, counted). Literal plan text not met. Intent met, see below. |

**Score:** 4/5 must-haves verified (0 behavior-unverified, 1 deviation awaiting human acceptance)

### Point 1: SC1 wording, "and that the chord deviates from the involute there"

**Verdict: satisfied as written. No gap, no override needed.**

- The shipped sentence reads: "The flank starts with a straight chord reaching {h:.3f} mm above the pitch circle, where it deviates from the involute: the root fillet is larger than half the dedendum." It names the height at 3 dp and states that the chord deviates from the involute there. That is exactly SC1's two requirements.
- SC1 asks for the fact that it deviates. It does not ask for a deviation figure. The "up to ~35 µm" bound sits in REQUIREMENTS.md's parenthetical, which says "the phase re-measures before quoting a number, or quotes none." D-02 chose none: the 35.29/32.28/31.73 µm figures had no script in the repo behind them, and three points do not bound a field range.
- The plan's prohibition "MUST NOT quote a chord-to-involute deviation figure" is consistent with SC1 and enforced: every row asserts the full string, none of which carries a figure.
- Residual observation (IN-03, not a defect): README adds the `x > 0.125` clause that the warning's cause clause omits. The cause clause is true on every firing (the sweep confirms), so L08 is not violated.

### Point 2: the `volume_rel` deviation against SC3

**Verdict: SC3 met; the plan's stricter literal must-have is deviated from, intentionally and with disclosure. Override suggested, not applied.**

- SC3 and REQ-filleted-spoke-closed-form scope the 1e-9 bar to "the four cutout rows" of `test_each_cutout_is_exactly_what_derive_prints_on_the_built_solid`: holes, spokes-sharp, spokes-filleted, cells. All four assert `abs=1e-9`, and the default of the shared function is `abs=1e-9`, so a forgotten argument fails loudly.
- The 15 composed rows live in two other tests. Their `d_volume` values are 6 dp literals measured after an arbitrary boolean. A 6 dp literal is off by up to 5e-7 mm3, so it cannot meet 1e-9. Verifier measured the same effect on holes and cells literals: 3.5e-07 and 4.0e-07 mm3 off a correct build.
- The alternatives were re-pinning 15 literals at full precision (brittle on a kernel bump, no formula behind them) or dropping the check. The executor kept the bar those rows always had, filed `2026-10-03-composed-cutout-volume-literals-pinned-at-six-places.md` (nice, trigger named), and wrote the exception into L33 and the retired debt's Resolution. Nothing was silently loosened.
- This is a departure from plan text, not from the roadmap contract. It needs a named person to accept it. Suggested override:

```yaml
overrides:
  - must_have: "_assert_the_cutout_is_what_derive_prints asserts the removed volume at abs=1e-9 on all four rows and nowhere at a relative tolerance"
    reason: "15 composed-solid rows carry 6 dp literals with no closed form and cannot meet 1e-9; they keep their pre-phase rel=1e-6 via an explicit volume_rel argument, filed as debt 2026-10-03-composed-cutout-volume-literals-pinned-at-six-places.md. The four SC3 rows are at abs=1e-9."
    accepted_by: "{name}"
    accepted_at: "{ISO timestamp}"
```

### Point 3: WR-02, the skip-the-cutout tripwire and L33's claim

**Verdict: confirmed, and slightly worse than the review states. L33 overstates.**

- Confirmed: the `holes` (565.486678) and `cells` (1052.220866) rows pass 6 dp literals into the shared assertion at the default `abs=1e-9`. On a correct, unskipped build the volume assertion would fail for them (gaps 3.5e-07 and 4.0e-07 mm3, measured). So the volume line cannot be the thing that makes those rows green.
- Worse than the review: I ran the skip scenario (`_cut_body` patched to a no-op) on `holes` and `spokes-filleted`. In both, the first assertion to fire is `assert faces_delta == d_faces` (`tests/test_model.py:1250`). The volume line (`:1258`) is never reached in any of the three rows, `spokes-filleted` included. The reviewer called `spokes-filleted` fine; its literal is exact, but the volume bar is still not what makes it red.
- L33 says: "The four cutout rows ... and all three skip-the-cutout tripwire rows run at `abs=1e-9`." Literally true as the default parameter, but it reads as evidence that the tightened bar is exercised by those tripwires. It is not. The tripwire that does prove the bar is load-bearing is the separate rim-corner test, which I confirmed goes red only on the volume line (the perturbed solid passes `rel=1e-6` and fails `abs=1e-9`).
- Impact on the goal: none. SC3's tripwire requirement is met by the rim-corner test. The skip tripwire is pre-existing and still goes red, for the face-delta reason. The defect is a sentence in the decision log in a phase about honest records, so it is a WARNING and a human decision, not a blocker. Disposition file still lists WR-02 as `open`.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/spur/calc.py` | lead-in warning branch | VERIFIED | `:975-985`, after "Root fillet reduced", before tip chamfer; no new field or function |
| `tests/test_calc.py` | 15-row parametrized test | VERIFIED | 15 passed; rows assert fillet used, height and full string |
| `README.md` | corrected root-fillets bullet | VERIFIED | contains "1.188 mm below the pitch circle", cites `warnings` |
| `src/spur/model.py` | `_outline` docstring only | VERIFIED | diff is prose; says "calc.derive warns when the chord ends above it" |
| `tests/test_model.py` | oracle, abs=1e-9, rim-corner tripwire | VERIFIED | `_filleted_spoke_volume`, `test_the_cutout_proof_fails_when_a_rim_corner_tangent_root_moves` present and passing |
| both resolved debt files | Status resolved, sha | VERIFIED | `825095f`, `61e1bea`; INDEX agrees |
| `docs/architecture/decision_log.md` L33 | amends L09, L10, L30; append-only | VERIFIED with WR-02 caveat | 97 added, 0 deleted |

### Key Link Verification

| From | To | Status | Details |
|------|----|--------|---------|
| `derive()` | `spline_start`, `root_fillet`, `pr.r` | WIRED | `h = spline_start(pr, rfil) - pr.r` |
| `derive().warnings` | `/api/info`, `spur info` | WIRED | `DerivedDimensions.warnings` unchanged surface; plan tracer checks passed at commit time |
| filleted proof row and skip tripwire row | `_filleted_spoke_volume` | WIRED | `:1333`, `:1361` |
| rim-corner tripwire | `spur.model._fillet_corner` | WIRED | `monkeypatch.setattr("spur.model._fillet_corner", perturbed)`; `_spoke_sector` resolves it via module global |
| `_assert_the_cutout_is_what_derive_prints` | all four rows | WIRED | default `abs=1e-9` |

### Data-Flow Trace (Level 4)

Not applicable: no rendered dynamic data. The warning's `h` flows from `spline_start`, the same value `_outline` builds from (docstring: "calc.spline_start places the spline's start"), through `derive()` to the API and CLI.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Three debt configs through `derive()` | scratch script, `derive(GearParams(...)).warnings` | `[]`; "0.562 mm"; "0.125 mm" | PASS |
| README condition equals the code's condition | 3,930-point sweep | 557 firings, 0 inconsistencies | PASS |
| Oracle vs kernel on three extra spoke configs | scratch script, `_build_checked` vs `_filleted_spoke_volume` | 2.3e-13, 3.6e-12, 1.8e-12 mm3 | PASS |
| Perturbed root is invisible at rel=1e-6, visible at abs=1e-9 | scratch script, patched `_fillet_corner` +1e-6 mm | gap -2.522e-4 mm3, rel True, abs False | PASS |
| Skip-tripwire first failing assertion | scratch script, `_cut_body` no-op | `faces_delta == d_faces` on holes and spokes-filleted | confirms WR-02 |
| Literal vs kernel on a correct build | scratch script | holes 3.5e-07, cells 4.0e-07 mm3 off, fail abs=1e-9 | confirms WR-02 |

### Probe Execution

No probes declared by any PLAN (`probe-*.sh` not referenced). Step 7c: SKIPPED.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| REQ-root-lead-in-warned | 14-01, 14-03 | `derive()` warns when the chord ends above the pitch circle, height 3 dp, deviation stated | SATISFIED | Truth 1; fixture byte-unchanged; `test_pre_v0_2` passes inside `make verify` |
| REQ-readme-root-zone-states-the-limit | 14-01, 14-03 | README states the real condition, cites the warning, no unmeasured number | SATISFIED | Truth 2; debt retired with `825095f`. Number-guard prohibition flagged, see below |
| REQ-filleted-spoke-closed-form | 14-02, 14-03 | filleted-spoke row vs closed form at 1e-9, literal demoted, tripwire, L30 answered | SATISFIED | Truth 3 and 4; deviation on 15 composed rows disclosed |

All three IDs in PLAN frontmatter appear in REQUIREMENTS.md and ROADMAP.md (checked `[x]`, traceability table "Complete"). No orphaned requirement: REQUIREMENTS.md maps no other ID to Phase 14.

### Prohibitions (ADR-550 D3 routing)

| Prohibition | Tier | Result |
|-------------|------|--------|
| No deviation figure or remedy number in the warning | test | Enforced: all rows assert the full string |
| No new `GearParams` / `DerivedDimensions` field; fixture byte-unchanged | test | Enforced: fixture replay test plus byte diff, params.py byte diff |
| No number in README the tests do not prove | test | UNVERIFIED-PROHIBITION, flagged. Verifier checked the diff by hand (1.188, 1.25, 0.125 only, all tested rows, no micron figure). No repo test guards it. Human review recommended. |
| No loosening of the 1e-9 bar from a measured gap without D-06 | test | Held for the four rows (D-06 not reached, largest gap 8.87e-12). The `volume_rel` exception is the separate disclosed deviation above. |
| No `_fillet_corner` / `cq` use in the oracle | test | Enforced by the plan's AST check; I re-read the function, none present. No standing repo test. |
| L09, L10, L30 and earlier entries untouched | test | Verified: numstat `97 0` |
| No number in L33 absent from tests or SUMMARYs | test | e-notation figures match `tests/test_model.py` docstrings (2.39e-12, 1.36e-12, 2.73e-12, 8.87e-12, 2.522e-4, 8.59e-8); the "0 of 44" count is recomputed in 14-03-SUMMARY |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (modified files, `TBD`/`FIXME`/`XXX`/`TODO`/`HACK` in added lines) | | none found | none | the gate's unfinished-work scan passed |
| `docs/tech_debt/resolved/2026-09-28-...md` | 67-68 | leftover "On resolve" template comment (IN-01) | Info | cosmetic |
| `docs/architecture/decision_log.md` L33 | tripwire sentence | overstates what skip-tripwire rows prove (WR-02) | Warning | see Point 3 |

### Human Verification Required

#### 1. Accept or reject the `volume_rel` deviation

**Test:** Review the override YAML under Point 2.
**Expected:** Add it with your name, or ask for the 15 literals to be re-pinned at full precision.
**Why human:** Overrides need a named acceptor; the roadmap contract is met either way.

#### 2. Correct L33's tripwire sentence (WR-02)

**Test:** Choose: reword L33 to say only the four proof rows and the rim-corner tripwire exercise `abs=1e-9`, or change the `holes` and `cells` skip-tripwire rows to closed-form `d_volume` and assert the volume delta directly so they discriminate.
**Expected:** L33 and the tests agree about what the skip tripwire proves.
**Why human:** Doc versus code conflict; editing an append-only log entry versus editing tests is a decision.

#### 3. Confirm the 1e-9 bar on the CI platform (WR-01)

**Test:** Run the four abs=1e-9 rows on ubuntu-latest and record gaps.
**Expected:** Gaps stay about 1e-11 or below, as on arm64 (largest 8.87e-12).
**Why human:** Cannot be run on this host; a CI-only red would tempt someone to loosen the bar.

#### 4. README number guard

**Test:** Decide whether a repo test should pin README's numbers.
**Expected:** Accept the manual check, or add a guard.
**Why human:** A test-tier prohibition with no wired enforcement is flagged, not passed.

### Gaps Summary

No gaps. All four ROADMAP success criteria are verified in code and by independent re-measurement. The phase left four items for a human: one plan-text deviation to accept (15 composed rows at `rel=1e-6`, disclosed and filed as debt), one decision-log sentence that overstates what the skip-the-cutout tripwire proves (confirmed, and it applies to all three rows, not two), one cross-platform measurement not yet taken, and one prohibition with no standing test.

Housekeeping, not a gap: ROADMAP.md line 64 still shows `- [ ] **Phase 14: Honest Record**` although all three plans are `[x]`; the phase-complete step will flip it.

---

_Verified: 2026-10-03_
_Verifier: Claude (gsd-verifier)_
