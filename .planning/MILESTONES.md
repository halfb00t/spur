# Milestones

## v0.4 True Root (Shipped: 2026-10-09)

**Delivered:** The hob-cut trochoid root in the part as an opt-in — `root_shape=trochoid` builds the root a hob with tip radius `root_fillet` cuts, proven against an independent swept-cutter oracle at the calc tier and on the built solid, every number printed beside it proved or warned, parity on the web form, the API and the CLI, the default unmoved and the 44-record fixture byte-identical to the `v0.3` tag (L38); before it, the last two `must` debts retired — the commit gate split and proved by a live SDK commit (L36), the same-slot timeout race reproduced, fixed and ended as a documented 503 with the worst row's margin logged (L37).

**Phases completed:** 17–19 (22 plans, 52 tasks); Phase 20 (The Flip) skipped under L38 — O4, flip deferred to a real fit report or a mating-pair request below z_min.

**Key accomplishments:**
- Debt first (Phase 17): `make verify.fast` (11.3 s warm) at pre-commit and the whole gate at pre-push, hooks self-installed, proved by SDK commit `5a3332f` (L36); the ten-identical-worst-row scenario reproduced the undocumented 500 on attempt 1, the two-fact guard plus `_closed` fixed it (red-then-green, 20/20 + 20/20 loops), zero 500s after; the 29.42 s row's limit recorded as documented behaviour with no default moved (L37); both `must` debts retired in their fixing commits.
- Trochoid maths, proved (Phase 18): the rack cutter defined once from `profile()`'s own expressions, the envelope generated in contact-normal angle or honestly refused by `root_mode`'s six named reasons, proven against a stdlib swept-cutter oracle (T2, worst 2.985e-12 mm over 10,326 curves), freecad.gears at ρ = 0 (T3, 1.8e-15 mm) and KISSsoft's form diameter (T4, 3.6e-5 in), a 31,446-case box sweep at commit; nothing a user can see changed; the human read the measured step and chose O4 (`d05-hold`).
- The trochoid in the part (Phase 19): `root_shape` (`Literal`, default `radial`) carries the curve through one `root_mode` call into the outline — one `makeSpline` per side, `ROOT_ARC_MIN` closing the kernel's arc dead band, four structural guards independent of `isValid()` — with the built root within 2e-3 × module of the oracle at 401 positions on seven rows (tripwire red at 0.05 mm); `root_form_d` as the cutter-envelope junction, `root_waist` at the narrowest arc under a 0.4 mm floor, thickness/gap null with a sentence, the undercut sentence from the cutter with `x_min`; parity proved the Phase 12 way; composes with every shipped feature (192 + 24 rows), heaviest trochoid row 14.64 s of 30 s.
- The record (Phase 19): L38 supersedes L10 and amends L09/L33 with every figure cited; README, the strategy docs and the ideas brought true; Phase 20 recorded skipped the way the roadmap's skip condition prescribes; the gate's cost measured on one host (192.94 s mean against L34's 66 s) and accepted by the human rather than a proof trimmed (`accept-A`).
- Review and close: Phase 19's review found `root_waist` read at the narrowest half-angle, 2–5 % high with the floor warning silent on sub-floor gears (CR-01) — fixed before verification with every pin re-measured (`e733cc2`), plus WR-01's kernel-exception wrap (`b51931c`); the milestone audit read 14/14 requirements, 15/15 integration seams, 8/8 flows, Nyquist and security clean on all three phases.

**Stats:**
- 169 files changed (+130,722 / −2,289) from the `v0.3` tag to the last squash; the bulk under `.planning/` (phase records, investigation logs, the 19-01 gate-flake log)
- 4,040 lines of package Python, 12,268 of tests, 4,544 of bench, 372 of hand-written UI JS; 1,220 tests in `make verify` (929 at v0.3), 97.92 % coverage against the 96 % floor
- 3 phases executed (+1 skipped by decision), 22 plans, 52 tasks; 3 PRs (#27–#29) through `make pr.land` after the start PR #26; 181 branch commits squashed
- 3 days from the milestone start commit (2026-10-06) to the last squash (2026-10-09)
- 0 runtime dependencies added (`requirements.txt` 31 → 31 pins; stdlib maths only under `src/spur/`)
- `make verify` ~64 s → 162–240 s warm on the M5 Max (192.94 s mean; L34's 66 s bar unmoved, `accept-A`)

**Git range:** `e64d764` (Milestone v0.4: True Root — start (#26)) → `767317b` (Phase 19: The Trochoid in the Part (#29))

**Closeout:** `override_closeout` in the tooling's terms — Phases 17 and 18 project `verification_status: stale` because Phase 19 changed files their reports cover (both reports `passed`, 5/5 and 6/6; cause proven per phase in the audit), and Phase 20 is an unstarted row by decision. Known verification overrides: 0 newly acknowledged, 0 carried forward.

**What's next:** `/gsd-new-milestone` — candidates: the gear family (helical first), the hob-root default flip on D-09's trigger, the L34 bar re-set, the Phase 18 review's eight info findings.

---

## v0.3 Clean Ledger (Shipped: 2026-10-05)

**Delivered:** The record made true and the gate measured — the ten-concurrent latency bar
demonstrated on the harness as it stands instead of waived, the root lead-in warned where it
rises above the pitch circle and README saying so, the filleted-spoke proof checked against a
closed form, `make verify` profiled and running on eight workers under a measured coverage
floor with CI installing the kernel pair the fixture pins, and `model.py` clean under mypy
`--strict` with zero suppressions — no new `GearParams` field, the 44-record pre-v0.2 fixture
byte-identical to the `v0.2` tag.

**Phases completed:** 13–16 (20 plans, 50 tasks).

**Key accomplishments:**
- Latency bar (Phase 13): a pre-registered twelve-run campaign ruled both observations L18
  left open (the second-run-worse effect not reproduced in this environment; the verdict
  floor real), then `bar-3` read 1.31× and 1.42× idle p95 on both concurrent runs of one
  decisive session — outcome (a), harness and bar unchanged. SC3 measured the composed worst
  row under ten concurrent builds exactly as it read (0/10 served) and filed the same-slot
  timeout race it exposed as `must` debt with no `src/` change (L32 amends L18).
- Honest record (Phase 14): `derive()` warns when the root fillet's straight chord ends
  above the pitch circle (default gear −1.188 mm, silent; `{1.0, 14.5°}` +0.562 mm, warns),
  README and `_outline` state the real condition; the filleted-spoke removed volume matches
  `_filleted_spoke_volume`, a polar closed form, to 2.73e-12 mm³ and all four plain cutout
  rows assert at `abs=1e-9` with a tripwire proving the bar load-bearing. UAT found two gaps
  and gap plan 14-04 closed them (L33 amends L09, L10, L30).
- The gate measured (Phase 15): serial profile 224.28 s (99.8 % pytest, 74 % of it
  `tests/test_model.py`); xdist knee N = 8 by a rule fixed before the read; the human set
  the bar at 66 s and refused all 15 priced cuts by name; the gate reads mean(B) 63.555 s at
  `-n 8` with coverage; `fail_under = 96` from a 96.99 % baseline with the red run recorded;
  CI's `make verify` under `PIP_CONSTRAINT: requirements.txt` prints `cadquery 2.8.0
  cadquery-ocp 7.9.3.1.1` (run 37181871926) and a conflicting pin fails closed (L34 amends
  L12, L13).
- Typing and validation (Phase 16): five `type: ignore`s in `model.py` replaced by two
  `isinstance` boundaries (`_body`, `_shape_of`) raising `BuildError`, `make no-fake-done`
  refusing a sixth, the mypy override scoped to `OCP.*`, no geometry change (fixture and the
  five-site gear tuple identical to `085e5a6`); Phases 7 and 8 got their retroactive
  `VALIDATION.md`s at `nyquist_compliant: true`, Phase 7's three Manual-Only rows filed as
  one `nice` debt file, the v0.2 audit amended in place (L35 amends L21).
- Ledger: six debt items retired in their fixing commits (`6709953`, `825095f`, `61e1bea`,
  `2aadcea`, `839dfea`, `4f7e8fe`) — all four `must` rows the milestone was scoped on plus
  two `nice`; five filed (one `must`, four `nice`, one of those by the close audit); active
  10 → 9.

**Stats:**
- 254 files changed (+394,938 / −1,615) from the v0.2 tag to the last squash — 218 of them
  under `.planning/`, mostly Phase 13's 123 committed run records; 36 outside it (+2,798 /
  −228), 13 of them code, tests, bench or config (+1,757 / −86)
- 3,170 lines of package Python, 8,315 of tests, 2,067 of bench, 370 of hand-written UI JS;
  929 tests in `make verify` (907 at v0.2), 97.24 % coverage against the 96 % floor
- 4 phases, 20 plans, 50 tasks; 4 PRs (#16–#19) through `make pr.land` after the start
  PR #15
- 4 days from the milestone start commit (2026-10-01) to the last squash (2026-10-05)
- 0 runtime dependencies added (`requirements.txt` 31 → 31 pins); `pytest-xdist` and
  `pytest-cov` added to the `[dev]` extra only
- ~7 h 35 min of executor time where measured (STATE.md per-plan table); 15-01's recorded
  10 h 41 m is wall time across an overnight human checkpoint with active time not measured,
  and is excluded
- `make verify` ~3.5 min → ~64 s warm (L34)

**Git range:** `9f26052` (Milestone v0.3: Clean Ledger — start (#15)) → `7a491bf` (Phase 16:
Typing & Validation Debt (#19))

**Closeout:** `override_closeout` (human decision, 2026-10-05). Phases 13–15 read `stale` in
`init.manager` because later phases legitimately changed files their reports fingerprint —
Phase 13: `bench/RESULTS.md`, `docs/architecture/decision_log.md`, `docs/tech_debt/INDEX.md`;
Phase 14: `README.md`, `decision_log.md`, `src/spur/model.py`, `tests/test_model.py`;
Phase 15: `Makefile`, `decision_log.md`, `pyproject.toml`. No plan, summary or verified
source of those phases changed; Phase 16 (`passed`, 16/16) ran `make verify` on the final
tree (`929 passed in 62.60s`, 97.24 %). Known verification overrides: 0 newly acknowledged,
0 carried forward (`audit-open` clear). Two verifier overrides accepted by the human on
record — Phase 14's eleven composed rows at `rel=1e-6` (14-UAT Test 1) and Phase 15's
`backstop` coverage-order truth (15-UAT item 1); human decisions on record: D-17 (SC3
recorded as read, no `src/` change), 14-04 (`abs=1e-8` on the three tip-chamfer rows), 15-03
(`N=8 bar=66 cuts=none`), 16-UAT test 2 (no `cast` pin).

### Known Gaps

- Success metric 1 ("`docs/tech_debt/INDEX.md` Active has zero `must` rows") is not met as
  written. The four `must` rows that existed at the v0.2 close are retired; Phase 13's SC3
  filed a new one — the same-slot timeout-cleanup race at `src/spur/pool.py:204` that returns
  an undocumented 500 instead of a 503
  (`docs/tech_debt/active/2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md`),
  kept out of scope by D-17. Accepted as a known gap by the human at the close; the trigger
  is named in the file.

**Audit:** `milestones/v0.3-MILESTONE-AUDIT.md` — status `tech_debt`; requirements 11/11,
phases 4/4, integration 9/9, flows 5/5, security 4/4 with 0 open threats, Nyquist compliant
(4/4; Phases 7–8 of v0.2 reconciled retroactively); 9 active debt items (1 `must`), each with
a trigger; 17 open review findings (14: 4, 15: 8, 16: 5), all warning or info.

**What's next:** v0.4 candidates carried from the v0.1 kickoff list and deferred at both the
v0.2 and v0.3 scoping decisions — a gear family (helical first; internal/ring and rack later,
one type per phase; bevel needs a product-scope decision first) or precision (the trochoidal
root fillet, L10/L33). `/gsd-new-milestone` decides.

---

## v0.2 Fit to Shaft (Shipped: 2026-10-01)

**Delivered:** A generated gear mounts on a real shaft and prints light — hex and keyway
bores, a tooth-tip chamfer, and one body-cutout pattern per part (spokes, holes or a
honeycomb), every one additive on the shipped pipeline with the pre-v0.2 part byte-unchanged,
every cut with a measured build time inside `SPUR_BUILD_TIMEOUT`, and all three interfaces in
parity from the one `GearParams` model.

**Phases completed:** 7–12 (34 plans, 82 tasks).

**Key accomplishments:**
- Foundation (Phase 7): the bore-rim and groove-floor selectors raise instead of silently
  selecting nothing; the 44-record `tests/regression/pre_v0_2.json` fixture replays every
  pre-v0.2 parameter set for identical `DerivedDimensions` and solid and stayed
  byte-unchanged through all six phases (L26).
- Hex and keyway bores (Phases 8–9): `bore_hex` replaces the round profile, warned not
  refused, with two measured root-circle rules at the chamfered corner (L27); the keyway is
  a slot after the chamfer with an explicit as-cut-wall depth datum, six refusals before any
  CAD, the recess yielding rather than refusing, and the round bore's own chamfer-reach gap
  closed at the kernel's measured contact (L28).
- Tooth-tip chamfer (Phase 10): a 3-D edge break capped at the smallest of tip land,
  addendum and a kernel boundary bisected to ~2 µm; help names no size because the
  research-era figure has no source (L29).
- Body cutouts (Phase 11): spokes with analytic tangent-arc corners, holes, and a
  whole-cell honeycomb capped at a measured `HEX_CELL_CAP = 120`; one pattern per part, every
  wall rule through `_under_min_wall` and pinned one step either side on the kernel; D-18's
  gate fired and set `hole_count`/`spoke_count` `le` 60/40 (L30).
- Composition pass (Phase 12): the 18-row composed sweep measured across four runs, D-02
  superseded for one gate on the human's word, `spoke_count` `le` 40 → 32 from a probe and
  every composed row inside 30 s (heaviest 29.42 s); 96 + 138 calc rows and 15 kernel rows
  prove the matrix; a model-driven field walk, a byte-identical composed document and 23
  identically routed refusals prove three-interface parity; L19 re-applied keeps
  `_GZIP_LEVEL = 1`; the phase's +28.28 s gate cost accepted against D-10's 30 s line (L31).
- Records kept honest: two cross-CLI review passes on Phase 12 (Codex lane) found and fixed
  14 findings — a regression test that could not fail, three over-claims in RESULTS.md and
  L31, the CLI's real 2/1/1 exit contract — before the close.

**Stats:**
- 185 files changed (+48,807 / −164) from the v0.1 tag to the last squash; 28 of them
  code, tests or bench (+11,623 / −62)
- 3,131 lines of package Python, 7,889 of tests, 1,881 of bench, 370 of hand-written UI JS;
  907 tests in `make verify` (191 at v0.1)
- 6 phases, 34 plans, 82 tasks; 6 PRs (#7–#13) through `make pr.land`
- 6 days from the milestone start commit (2026-09-26) to the last squash (2026-10-01)
- 0 runtime dependencies added (`requirements.txt` 31 → 31 pins)
- ~11 h 45 min of executor time where measured (Phases 7–10, STATE.md per-plan table;
  Phases 11–12 not timed per plan)

**Git range:** `b3ca789` (Milestone v0.2: Fit to Shaft — start (#7)) → `fd29c2c` (Phase 12:
Composition Pass (#13))

**Closeout:** `override_closeout` (human decision, 2026-10-01). Phases 7–11 read `stale` in
`init.manager` because Phase 12 legitimately changed files their reports fingerprint
(`src/spur/params.py`, the five test files, `bench/RESULTS.md`, the decision log); Phase 12's
own matrices and the byte-unchanged fixture re-exercise those phases on the final code, and
Phase 12 itself was re-verified on 2026-10-01 after its review fixes (`passed`, fresh digest).
Known verification overrides: 0 newly acknowledged, 0 carried forward (`audit-open` clear);
human decisions on record: D-06 (fixture cost), D-18 (`le` 60/40), D-02 superseded for one
gate, D-03 (`le` 32), D-10 (+28.28 s accepted).

**Audit:** `milestones/v0.2-MILESTONE-AUDIT.md` — status `tech_debt`; requirements 20/20,
phases 6/6, integration 9/9, flows 5/5, security 6/6 with 0 open threats; Nyquist partial
(Phases 7 and 8 predate the capability); 10 active debt items (4 `must`), each with a trigger.

**What's next:** v0.3 candidates carried from the v0.1 kickoff list and the v0.2 scoping
decision — a gear family (helical first; internal/ring and rack later, one type per phase)
or precision (trochoidal root fillet, the waived latency bar). `/gsd-new-milestone` decides.

---

## v0.1 Hardening (Shipped: 2026-09-25)

**Delivered:** The generator hardened for real load and honest contracts — CAD builds off
the event loop with a measured memory ceiling, structured logging, a typed
derived-dimensions contract with `disallow_any_explicit` on, CI as the structural merge
gate on Python 3.12 only, and the five debt items those phases surfaced retired.

**Phases completed:** 2–6 (21 plans, 59 tasks). Phase 1 is the pre-GSD v0 baseline,
recorded for context, not re-verified.

**Key accomplishments:**
- CAD builds run in `BuildPool` worker processes off the serving event loop, routed by
  parameter-hash affinity; `/api/health` p95 under one build within 2× idle on every
  recorded run; per-build timeout 30 s from the worst measured build, three failure-mode
  status codes, pool state on `/api/health`; `compose.yaml` `mem_limit: 4g` from an
  N=1/2/4 sweep of the real topology, not a formula (L17–L19 supersede L06/L07).
- Structured JSON logging (`records.py`) configured idempotently at both composition
  points; `build.started`/`build.failed`/`export.served`/`queue.refused`/`worker.replaced`
  proven by tests; `calc.py` provably log-free by an import-linter contract (L20).
- `derive()` returns a frozen 19-field `DerivedDimensions`; `HealthReport`/`PoolState`;
  mypy `disallow_any_explicit` on globally with no suppressions; `spur info --mate-teeth`
  refuses what the API refuses (L21 supersedes L14).
- CI is the merge gate: a repo-owned `commit-msg` hook refuses Actions skip tokens,
  `make pr.land PR=N` is the only path to `main`, a ruleset on `main` requires
  `test (3.12)`/`vendor-bundle`/`image` green on an up-to-date head plus a pull request;
  Python 3.12 only (L22, L23).
- Five debt records retired in Phase 6: the cached solid never carries a mesh
  (`shape.copy()`, L24); the hook reads git's whole buffer; `pr.land` refuses
  `conclusion != success`, resolves `jobs.<id>.name` in the drift test, and reports only
  what it observed after the merge (L25 amends L22).
- Tech-debt ledger 11 → 6 active items (1 `must`, 5 `nice`), 10 resolved during the
  milestone, every remaining item with a named trigger.

**Stats:**
- 169 files changed (+38,660 / −508) from the roadmap commit to the last squash; 64 of
  them outside `.planning/` (+7,524 / −381)
- 6,410 lines of Python (`src`, `tests`, `scripts`, `bench`, `docker`); 361 lines of
  hand-written UI JS; 191 tests in `make verify`
- 5 phases, 21 plans, 59 tasks; 64 commits on `main`; Phase 2 landed by direct push,
  Phases 3–6 as PRs #2–#5 (Phases 5–6 through `make pr.land`)
- 4 days from roadmap (2026-09-21) to ship (2026-09-25)
- 0 runtime dependencies added (`requirements.txt` 31 → 31 pins)
- ~8 h 45 min of executor time across the 21 plans (STATE.md per-plan table)

**Git range:** `f82a4d1` (docs: create milestone v0.1 roadmap) → `1173d21` (Phase 6:
Address tech debt: merge gate + solid cache (#5))

**Closeout:** `override_closeout` (human decision, 2026-09-25). Phase 1 has no phase
directory (pre-GSD baseline; `verification: missing` by construction). Phases 2–6 read
`stale` in `init.manager` because each VERIFICATION.md fingerprints `.planning/STATE.md`,
which GSD's own phase-complete step rewrites; for Phase 6 the declared `covered_digest`
recomputes exactly on `110b827` and only STATE.md changed afterwards (`4c39df8`,
`b35d7e9`). No source, test, plan or summary changed after any report. Known verification
overrides: 0 newly acknowledged, 0 carried forward (`audit-open` clear); 1 human waiver on
record — the Phase 2 ten-concurrent latency bar (WINDOWS.md item 1, L18, `must` debt).

**Audit:** `milestones/v0.1-MILESTONE-AUDIT.md` — status `tech_debt`; requirements 5/5,
phases 5/5, integration 14/14, flows 6/6, security 0 open; Nyquist partial (Phases 4 and 5
still `draft` — `/gsd-validate-phase 4`, `5` when convenient).

**Evidence:** PR #5 squash `1173d21`, run 36145323487 green on all three required jobs;
Phase 5 squash `b72b0e1`, run 36122394253.

**What's next:** Not yet defined — `/gsd-new-milestone`. Candidates gathered at v0.1
kickoff (`milestones/v0.1-REQUIREMENTS.md`, "Future Requirements"): helical, internal and
rack gears (bevel needs a product-scope decision first), tooth chamfers, keyway/hex bores,
spoke/hex body cutouts, the trochoidal root fillet (would supersede L10), a browser-driven
viewer test.

---
