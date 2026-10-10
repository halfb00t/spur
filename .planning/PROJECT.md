# spur

## What This Is

A parametric involute spur gear generator. Set parameters (module, tooth count, pressure
angle, profile shift, backlash, bore, face recesses, root shape...) and get a live 3D preview, the
numbers you'd measure on the real part, and an STL (slicing) or STEP (CAD) download — from
a web UI, an HTTP API, or a CLI, all driven by one parameter model. Built on CadQuery
(OpenCascade), FastAPI, and three.js.

*Source: root `README.md`, via `.planning/intel/context.md` ("Product summary").*

## Core Value

A number this tool prints is a number someone will cut metal to — so every dimension is
either computed honestly or reported as a warning, never guessed (L08). Everything else
(the UI, the API, the CLI) exists to get parameters in and a trustworthy gear out.

## Current State

**Shipped: v0.4 True Root (2026-10-09).** The last two `must` debts retired by measurement and decision — the commit gate split into `make verify.fast` at pre-commit and the whole gate at pre-push, proved by a live SDK commit (L36); the same-slot timeout race reproduced on attempt 1, fixed by a two-fact guard and `_closed`, the heaviest composed row's limit recorded as documented behaviour (L37) — then the hob-cut trochoid root: the cutter defined once, the envelope generated or honestly refused by one predicate, proven against a swept-cutter oracle sharing no code with `calc`, freecad.gears and KISSsoft (Phase 18); in the part as the opt-in `root_shape=trochoid` through one `makeSpline` per side with four structural guards, every number beside it proved or warned (`root_form_d`, `root_waist` at the narrowest arc, null thickness/gap, the undercut sentence from the cutter), parity on all three interfaces, the default unmoved and Phase 20 skipped with the flip deferred to a named trigger (L38 supersedes L10, amends L09 and L33). The 44-record fixture byte-identical to the `v0.3` tag. Two `must` retired, four debt items filed (one `must`: the resource-tracker flake). Record: `.planning/MILESTONES.md`, `milestones/v0.4-ROADMAP.md`, `milestones/v0.4-MILESTONE-AUDIT.md` (status `tech_debt`: 14/14 requirements, 15/15 integration, 8/8 flows, 12 active debt items with triggers, 1 `must`).

Codebase at `767317b`: 4,040 lines of package Python, 12,268 of tests, 4,544 of bench, 372 lines of hand-written UI JS, 1,220 tests, 31 pinned runtime packages (unchanged since v0), `make verify` green at 97.92 % coverage — 162–240 s on the 18-CPU M5 Max against L34's 66 s bar, accepted (`accept-A`, L38) with the bar's re-set an open decision.

**Shipped: v0.3 Clean Ledger (2026-10-05).** The record is true and the gate is measured:
the ten-concurrent latency bar demonstrated on the unmodified harness (L32); the root lead-in
warned where it rises above the pitch circle and the filleted-spoke proof checked against a
closed form (L33); `make verify` profiled, on eight workers under `fail_under = 96`, CI
installing the pinned kernel pair (L34); `model.py` clean under mypy `--strict` with zero
suppressions and Phases 7–8 Nyquist-validated retroactively (L35). No new `GearParams`
field; the 44-record fixture byte-identical to the `v0.2` tag. Six debt items retired, five
filed; the one `must` left — the same-slot timeout race Phase 13 found and D-17 kept out of
scope — is the milestone's one known gap. Record: `.planning/MILESTONES.md`,
`milestones/v0.3-ROADMAP.md`, `milestones/v0.3-MILESTONE-AUDIT.md` (status `tech_debt`:
11/11 requirements, 9/9 integration, 5/5 flows, 9 active debt items with triggers, 1 `must`).

Codebase at `7a491bf`: 3,170 lines of package Python, 8,315 of tests, 2,067 of bench, 370
lines of hand-written UI JS, 929 tests, 31 pinned runtime packages (unchanged since v0),
`make verify` green (~64 s warm at `-n 8` with coverage, L34).

**Shipped: v0.2 Fit to Shaft (2026-10-01).** A generated gear mounts on a real shaft and
prints light: hex and keyway bores, a tooth-tip chamfer, and one body-cutout pattern per part
(spokes, holes, honeycomb), all additive on the shipped pipeline (L26–L31). The pre-v0.2
part is byte-unchanged through the whole milestone (44-record fixture); every cut has a
measured build time inside `SPUR_BUILD_TIMEOUT` (`spoke_count` `le` 32 from the composed
sweep); the three interfaces are proven in parity from the one `GearParams` model. Record:
`.planning/MILESTONES.md`, `milestones/v0.2-ROADMAP.md`, `milestones/v0.2-MILESTONE-AUDIT.md`
(status `tech_debt`: 20/20 requirements, 9/9 integration, 5/5 flows, 10 active debt items
with triggers, 4 `must`).

Codebase at `fd29c2c`: 3,131 lines of package Python, 7,889 of tests, 1,881 of bench, 370
lines of hand-written UI JS, 907 tests, 31 pinned runtime packages (unchanged since v0),
`make verify` green (~3.5 min).

**Shipped: v0.1 Hardening (2026-09-25).** The generator is operable under real load and
its contracts are honest: CAD builds run in worker processes off the event loop with a
measured memory ceiling (L17–L19); structured logging at the composition boundary (L20);
a typed `DerivedDimensions` contract with `disallow_any_explicit` on (L21); CI is the
structural merge gate on Python 3.12 only (L22, L23); the five debt items the milestone
itself surfaced are retired (L24, L25). Record: `.planning/MILESTONES.md`,
`milestones/v0.1-ROADMAP.md`, `milestones/v0.1-MILESTONE-AUDIT.md` (status `tech_debt`:
5/5 requirements, 14/14 integration, 6/6 flows, 6 deferred debt items with triggers).

Codebase at `1173d21`: 6,410 lines of Python, 361 lines of hand-written UI JS, 191 tests,
31 pinned runtime packages (unchanged over v0.1), `make verify` green.

## Current Milestone: v0.5 Honest Form

**Goal:** The web form tells the user up front what each field does and a browser proves
it — the deferred UI ideas taken in dependency order behind a real viewer test, the gate
bar re-set from a measurement, and the three small ledger items closed — with no new
`GearParams` field and the 44-record fixture byte-identical to the `v0.4` tag.

**Target features:**
- Browser test for the viewer (`docs/ideas/2026-09-21-browser-test-for-the-viewer.md`) —
  the first decision is whether a headless browser belongs in `make verify` at all (gate
  cost against L34's bar; Node at test time where the runtime has none, L11), both routes
  priced at discuss-phase; then the test proves the form builds from `/api/schema`, an
  invalid field is marked, a warning renders and the STL loads into the scene. The
  prerequisite both UI ideas below named as their trigger.
- Conditional form fields (`2026-09-29-conditional-form-fields.md`) — an `enabled_when`
  relation as `json_schema_extra` on the model, rendered by `app.js` from `/api/schema`
  alone; covers the keyway/hex ignored-field cases and the three cutout groups. Supersedes
  08 D-09 by a new `Lxx`; L02 kept.
- Bore-shape selector (`2026-09-27-bore-shape-selector-in-the-web-form.md`) — a UI-only
  select in `app.js` deriving its state from the flat fields on load and still sending the
  flat fields; API, CLI and URL contract unchanged (L05).
- Download name carries `root_shape` (`2026-10-08-download-name-carries-the-root-shape.md`)
  — a slug change under its own `Lxx`, after reading what pins the old names (records,
  tests).
- L34 gate-bar re-set (Phase 19 review IN-03;
  `docs/tech_debt/active/2026-10-09-phase-19-review-info-findings-deferred.md`) — an
  idle-host reading before and after the browser test lands; one `Lxx` amends L34.
- Reverify recipe (`2026-09-28-reverify-after-post-verification-fixes.md`) — one paragraph
  in `HOW_TO_DEVELOP.md` §6, or `.ai_skills/reverify-phase` if the loop has hit three times.
- Soften the Pi 5 claim (`2026-09-22-measure-or-soften-the-pi5-claim.md`) — README states
  the hardware the numbers came from; no measurement, nobody has the board.
- Constrain `make venv` probe (`2026-10-03-constrain-make-venv-to-the-closure.md`) — a fresh
  venv under `PIP_CONSTRAINT=requirements.txt` on this arm64 host; adopt and amend L34 if
  `make verify` passes, else record which pins lack arm64 wheels.

**Rules this milestone lives by:**
- The form is generated from `/api/schema` and nothing else (L02, the spirit of 08 D-09): a
  field relation lives in schema metadata on the model, never hard-coded in `app.js`.
- No new `GearParams` field; the pre-v0.2 fixture stays byte-identical to the `v0.4` tag
  (L26); every shared link builds the same part and sends the same fields (L05).
- A gate cost is measured before it is accepted, and the bar is re-set by an `Lxx` with the
  reading, never tuned toward a pass (L08, L34).
- A debt item or idea is retired only in the commit that closes it (CLAUDE.md).

Picked 2026-10-10 as "the deferred ideas" over the gear family (helical first — still the
riskiest surface in the product, now the v0.6 candidate). Three ideas stay filed because
their triggers have not fired: the hob-root default flip (D-09), the cutout rotation field
(no real part has asked) and the teeth-dependent honeycomb cap (D-12 — needs a user and a
sweep).

<details>
<summary>v0.4 True Root — scope as set at kickoff (shipped 2026-10-09)</summary>

**Goal:** Retire the last two `must` items — the same-slot timeout race by a measured
reproduction and a narrow fix, the commit-timeout gap by a logged decision — then replace
the radial root below the base circle with the trochoid a hob cuts, proven against a
known-good profile, with the fixture rule (L26) honoured under its own `Lxx`, never bypassed.

**Target features:**
- Same-slot timeout race — Phase 13's deferred ten-identical-worst-row scenario reproduces
  the undocumented 500 without hash-affinity luck
  (`docs/tech_debt/active/2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md`);
  then `_run_with_timeout`'s `except TimeoutError` branch checks its `executor` local
  against the live slot before touching `_processes`, so a second same-slot timeout raises
  `BuildTimeout` (a documented `503`) instead of `AttributeError`. The margin finding — the
  worst composed row at 29.42 s alone and over 30 s under contention — gets a decision
  (`SPUR_BUILD_TIMEOUT`, a cap, or a recorded limit), not a silent pass.
  **Done — Phase 17 (L37):** reproduced on attempt 1, fixed by the locked two-fact guard +
  `_closed` (`0628182`), zero 500s after; the limit recorded as documented behaviour, no
  default moved (`7af75af`).
- Commit-timeout decision — one `Lxx` choosing between the upstream `COMMIT_TIMEOUT_MS`
  knob, a pre-push hook, or a sub-30 s pre-commit subset priced from the Phase 15 profile;
  L13's "one definition of passing in three places" amended, not ignored
  (`docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md`).
  **Done — Phase 17 (L36):** the sub-30 s pre-commit subset (`make verify.fast`, 11.3 s
  warm) plus the whole gate at pre-push (`c06749d`); SC1 proved by SDK commit `5a3332f`;
  upstream knob requested as open-gsd/gsd-core#5231.
- Trochoidal root fillet — the root below the base circle generated from the cutter's tip
  path, the analytic fillet kept for the normal case (L09), superseding L10; a test against
  a known-good undercut profile; `derive()`'s undercut warning re-stated or retired on
  evidence. Always-on for undercut gears (the fixture regenerates under its own `Lxx`;
  low-tooth-count links change part — L05 tension) vs a new default-off field (L05 and the
  fixture hold byte-for-byte): decided at discuss-phase with both priced, the human's call.
  **Done (the maths) — Phase 18 (2026-10-08):** the cutter defined once from `profile()`'s own
  expressions, the envelope generated in contact-normal angle, `root_mode` the single predicate
  with six named refusals, proven against a swept-cutter oracle sharing no code with `calc`
  (T2, worst 2.985e-12 mm over 10,326 curves), freecad.gears at ρ = 0 (T3, 1.8e-15 mm) and
  KISSsoft's form diameter (T4, 3.6e-5 in), a 31,446-case box sweep at commit (1.7 s), nothing a
  user can see changed and the fixture byte-identical; the part, the field and the root-mode
  `Lxx` are Phase 19's (the human read the measured step and held D-01/D-02: `d05-hold`).
  **Done (the part) — Phase 19 (2026-10-09, L38):** `root_shape` (`radial` default, `trochoid`)
  carries the hob root through `root_mode` into the outline (one `makeSpline` per side through
  `RootCurve`, four structural guards independent of `isValid()`, `ROOT_ARC_MIN` 2e-6 mm), the
  printed numbers (`root_thickness`/`root_gap` null with a sentence, `root_form_d` the
  cutter-envelope junction, `root_waist` the narrowest arc under a 0.4 mm floor — redefined after
  review CR-01, `e733cc2` — and the undercut sentence restated from the cutter with `x_min`) and
  all three interfaces (model-driven field walk, byte-identical documents, unknown value 422 /
  exit 2, a guard's `BuildError` 422 / exit 1 — `exit-documented`); the built root reads within
  2e-3 × module of the independent oracle on seven rows; composes with every shipped feature
  (192 calc rows, 24 kernel rows; heaviest trochoid corner row 14.64 s of 30 s); fixture
  byte-identical to `df4749e`; the default does not move (O4) — Phase 20 skipped, the flip
  deferred to D-09's trigger; gate cost 192.94 s mean against L34's 66 s accepted (`accept-A`).
  Verified 5/5, Nyquist 0 gaps, security 22/22 closed, review 1 critical / 1 warning fixed and
  4 info deferred (`19-REVIEW-FIX.md`), `make verify` 1220 tests at 97.92 %.

**Rules this milestone lives by:**
- The fixture changes only via `make fixture.regen`, in its own commit, under its own `Lxx`
  that says what moved and why (L26 D-03); a feature commit never touches it.
- A number printed is a number cut: the trochoid is proved against a known-good profile,
  and a closed form where one exists, or the warning stays (L08).
- A debt item is retired only in the commit that fixes it (CLAUDE.md).
- Phase 1 is the two `must` items, so every later commit of the milestone runs under the
  hook decision.

Picked 2026-10-06 over helical, now the v0.5 candidate (re-derives module, span and centre
distance — the riskiest surface in the product, needing its own research pass; internal/ring
and rack after it; bevel needs a product-scope decision first).

<details>
<summary>v0.3 Clean Ledger — scope as set at kickoff (shipped 2026-10-05)</summary>

**Goal:** Every `must` debt item retired by measurement or a logged decision, every false
claim in the record made true or warned, and the gate itself measured — no new user-facing
geometry, no new `GearParams` field, the 44-record pre-v0.2 fixture byte-unchanged
throughout.

**Target features:**
- Latency bar (L18) — both unexplained observations in
  `docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md` (the second run of a
  pair is always worse; the verdict sits at the harness's 0.1 ms floor) get a cause ruled in
  or out; then the bar reads ≤2.00× on both runs of one session, or the harness or the bar
  is changed by a logged `Lxx` and re-measured on the new harness. Never tuned toward a pass.
  **Done — Phase 13 (L32):** demonstrated outright on the unmodified harness; both observations ruled.
- CI kernel pin — CI installs the `cadquery`/`cadquery-ocp` pair the fixture's provenance
  header names; pin-to-`requirements.txt` vs. an upper bound in `pyproject.toml` decided and
  logged as `Lxx` against L12's rationale.
  **Done — Phase 15 (L34):** neither named option — `PIP_CONSTRAINT: requirements.txt` on
  CI's `make verify` step (D-13); run 37181871926 printed the pair; a conflicting pin fails closed.
- Root lead-in — a warning when `spline_start` rises above the pitch radius, and README's
  "non-working root zone" sentence states the real limit. No outline change (the human's
  choice over an outline fix with fixture regeneration; L10's trochoidal root stays an idea).
  **Done — Phase 14 (L33):** warns at `round(h, 3) > 0` (default gear −1.188 mm silent;
  `{1.0, 14.5°}` +0.562 mm warns); README and `_outline` corrected; debt retired `825095f`.
- Filleted-spoke proof — a closed-form removed volume (sector minus four circular-segment
  corrections) asserted at the 1e-9 mm³ bar the other three patterns meet; L30's "pinned,
  not derived" clause amended.
  **Done — Phase 14 (L33):** `_filleted_spoke_volume` agrees with the kernel to 2.73e-12 mm³;
  all four plain cutout rows at `abs=1e-9`; eleven composed rows stay at `rel=1e-6` as named
  `nice` debt; debt retired `61e1bea`.
- `make verify` profiled — per-file/per-marker timing recorded in `bench/RESULTS.md`, the
  heaviest contributors named, cuts proposed with their proof-value cost; the target number
  is set at discuss-phase from the profile, not before. First finding: pytest runs serially
  (no xdist; `addopts` is `--strict-markers --strict-config`).
  **Done — Phase 15 (L34):** serial profile 224.28 s; knee N = 8; the bar (66 s) set by the
  human at the 15-03 checkpoint and read at 63.555 s (`-n 8` with coverage), no cut accepted.
- Coverage floor — one baseline `pytest --cov` run, `fail_under` set just under it, gated in
  `make verify`.
  **Done — Phase 15 (L34):** baseline 96.99 %, `fail_under = 96`, `make test` runs `--cov`;
  the red run (90.24 %) recorded, not committed.
- Shape typing — the five `type: ignore`s in `model.py` retired by two `isinstance`
  boundaries (`_body`, `_shape_of`) that raise `BuildError`, as its own tested change;
  `make no-fake-done` refuses a new one.
  **Done — Phase 16 (L35):** five suppressions retired (lines 213, 237, 239, 411, 420 at
  `085e5a6`), tests 927 → 929, fixture byte-identical to `085e5a6`; `make no-fake-done`
  pins zero under `src/spur/`.
- Nyquist for Phases 7 and 8 — `VALIDATION.md` via `/gsd-validate-phase`.
  **Done — Phase 16 (L35):** both files exist at `status: validated`, `nyquist_compliant:
  true` as read for both; 3 gap rows for Phase 7 filed as one nice debt file
  (`2026-10-05-phase-07-nyquist-gaps.md`), 0 for Phase 8; the v0.2 audit's `nyquist`
  block amended to `missing_phases: []`, `overall: compliant`.

**Rules this milestone lives by:**
- No new `GearParams` field; the pre-v0.2 fixture stays byte-unchanged (L26) — every item
  is a proof, a pin, a warning or a record, never a different part.
- A debt item is retired only in the commit that fixes it: `Status: resolved`, the sha,
  `git mv` into `resolved/`, the INDEX row moved (CLAUDE.md).
- A bar is demonstrated or superseded by a logged decision with the measurement — never
  tuned toward a pass (L08).

Picked 2026-10-01 as "debt first" over the two feature candidates carried from the v0.1
kickoff list and the v0.2 scoping decision, which remain candidates for v0.4: the gear
family (helical first — re-derives module, span and centre distance, the riskiest surface
in the product; then internal/ring, then rack with a second parameter model; bevel needs a
product-scope decision first) and precision (the trochoidal root fillet, L10). Three of
the four `must` items are retired pre-emptively — their triggers have not fired — on the
human's call.

Outcome at close (2026-10-05): all eight target features done (Phases 13–16, L32–L35);
"Success Metric (Milestone v0.3)" below records the one metric not met as written.

</details>

<details>
<summary>v0.2 Fit to Shaft — scope as set at kickoff (shipped 2026-10-01)</summary>


**Goal:** A generated gear mounts on a real shaft and prints light — new bore profiles,
body cutouts and a tooth-tip chamfer, all additive on the shipped spur pipeline, with
tooth measurements untouched.

**Target features:**
- Keyway bore — explicit width, depth and clearance in mm; no standard-table lookup (the
  user reads the key size off the shaft; a looked-up size is a number someone cuts metal
  to, and would need the standard cited and its table verified)
- Hex bore — across-flats plus clearance
- Body cutouts, each with an explicit count and its own dimensions: spoke arms (arms, arm
  width, hub Ø, rim wall), circular lightening holes (holes, hole Ø, bolt-circle Ø),
  hexagonal pattern (cell size, wall thickness; the count follows from the web area and is
  capped and warned when the build cannot fit the timeout)
- Tooth-tip chamfer (the bore chamfer already ships)
- Features compose: cutouts combine with face recesses (cut through the recessed floor,
  floor fillet intact), with any bore profile, and with each other where geometry allows;
  the only refusal is a direct dimensional conflict named by field (L03)

**Rules this milestone lives by:**
- New parameters default to off — every pre-v0.2 shareable link produces the same part and
  the same numbers (L05); proven by a regression test, not assumed.
- Every new cut gets a measured build time at its heaviest allowed configuration (recess +
  hex pattern is the unknown) against `SPUR_BUILD_TIMEOUT=30s`; what cannot fit is
  capped-and-warned or refused, never silently truncated.
- `DerivedDimensions` grows additively; caliper, span and centre-distance formulas are not
  touched.

Picked 2026-09-25 from the candidates gathered at v0.1 kickoff
(`milestones/v0.1-REQUIREMENTS.md`, "Future Requirements") over "gear family" (helical /
internal / rack — re-derives module, span and centre distance, the riskiest surface in
the product, and rack needs a second parameter model) and "precision" (trochoidal fillet
plus the waived latency bar — no trigger has fired). Both stay candidates for v0.3.

</details>

</details>

## Requirements

### Validated

v0 items shipped in the baseline already in the tree; v0.1 items shipped 2026-09-25. All
confirmed by `make verify` (ruff, mypy `--strict`, import-linter, unfinished-work scan,
pytest — L13). Full list with sources and acceptance evidence:
`milestones/v0.1-REQUIREMENTS.md`.

- ✓ REQ-involute-geometry — involute tooth geometry from module/teeth/pressure
  angle/profile shift — v0
- ✓ REQ-bore-and-fillets — backlash, root fillets, D-flat/round bore with clearance and
  chamfer — v0
- ✓ REQ-face-recesses — annular face recesses, one or both sides, filleted floors,
  capped-not-refused when oversized — v0
- ✓ REQ-measurement-aids — caliper, span (Wildhaber), centre distance to a mate — v0
- ✓ REQ-shareable-links — every parameter lives in the URL — v0
- ✓ REQ-stl-step-export — STL and STEP export from all three interfaces — v0
- ✓ REQ-three-interfaces — web UI, HTTP API, and CLI on one `GearParams` model — v0
- ✓ REQ-error-contract — refuse (422 / exit 2) vs. cap-and-warn vs. report-nothing — v0
- ✓ REQ-no-auth-default — no built-in auth; binds to `127.0.0.1` by default — v0
- ✓ REQ-docker-multiarch — Docker/compose for `linux/amd64` and `linux/arm64` — v0
- ✓ REQ-cli-parity — `spur serve`/`info`/`export` match the API's numbers and errors — v0
- ✓ REQ-cad-off-event-loop — CAD builds run in `BuildPool` worker processes and the serving
  process is import-linter-forbidden from the kernel; `/api/health` p95 under one build
  within 2× idle on every run recorded, the ten-concurrent scenario accepted with caveat,
  not demonstrated (L18; waived on the Runs 1–8 evidence) — Phase 2
- ✓ REQ-measured-memory-ceiling — the N=1/2/4 container sweep measured the ceiling;
  `compose.yaml` `mem_limit: 4g` is N=2's 2878.5 MiB peak × 1.3 headroom, not L07's
  formula multiplied out (L17) — Phase 2
- ✓ REQ-structured-logging — `src/spur/records.py` (stdlib `logging`, project-owned JSON
  formatter, one object per line on stderr) configured idempotently at both composition
  points; `build.started`, `build.failed`, `export.served`, `queue.refused` and
  `worker.replaced` proven by `caplog`/`json.loads` tests; uvicorn's own records share the
  stream; post-review fix renders a `traceback` field for records that carry `exc_info`
  (L20) — Phase 3
- ✓ REQ-typed-derived-dimensions — `derive()` returns a frozen 19-field `DerivedDimensions`
  model (every key always present, `null` where it does not apply); `/api/health` is a
  `HealthReport` with `pool: PoolState | None`; `/api/schema` is pydantic's own
  `JsonSchemaValue`; mypy's `disallow_any_explicit` is on globally with `make verify` green
  (104 tests) via the pydantic plugin's `init_typed`/`init_forbid_extra`, no suppressions;
  `spur info --mate-teeth` refuses the range the API refuses (L21 supersedes L14) — Phase 4
- ✓ REQ-ci-verified — CI is the merge gate for `main`: a repo-owned `commit-msg` hook
  (`scripts/skip_tokens.py`) refuses the six GitHub Actions skip tokens; `make pr.land PR=N`
  refuses a red, missing, stale or token-carrying head and exits non-zero unless the squash
  commit gets a run, printing its URL; the ruleset on `main` requires `test (3.12)`,
  `vendor-bundle` and `image` green on an up-to-date head plus a pull request (read back
  live); Python 3.12 only (L23 supersedes L01's floor); the "CI workflow unverified"
  blocker retired citing runs 35963114939 and 36088409707; the pr.land cut-line bypass
  (05-REVIEW CR-01) closed by gap plan 05-06 and re-verified 5/5 (L22, L23) — Phase 5
- ✓ Phase 6 tech-debt closure (no REQ-ID: the phase was added to v0.1 after
  `REQUIREMENTS.md` was written; its contract is `06-CONTEXT.md` D-01…D-11) — the
  commit-msg hook scans the whole buffer git hands it (no cut line, no `GIT_EDITOR`
  read; refusals name the line and the `-v` way out); `make pr.land` refuses a run whose
  own `conclusion` is not `success` (proven live on run 36116930241), resolves
  `jobs.<id>.name` overrides in the drift test, and after the merge reports only what it
  observed (read error / Actions link / a token read from the squash commit); STL export
  meshes `shape.copy()` so the cached `cq.Solid` never carries a mesh (`.BoundingBox()`
  exact, content-equivalent exports, the autouse cache reset deleted); five debt files
  retired in their fixing commits; L24/L25 carry the measured numbers; verified 9/9,
  review clean, 13/13 threats closed, `make verify` 191 tests — Phase 6
- ✓ REQ-defaults-off-regression — `tests/regression/pre_v0_2.json` pins, for every
  pre-v0.2 hand-written parameter set (78 source-tagged entries → 44 records), `derive()`'s
  19 fields exactly and `build()`'s volume, bounding box and face/edge counts; written only
  by `make fixture.regen`, replayed as 85 pytest cases; proven to go red on a silently
  vanished chamfer (32 cases); costs 16.27 s on `make verify` (measured, accepted over the
  15.0 s line by the human — D-06). Export byte-identity is not pinned (L26) — Phase 7
- ✓ REQ-edge-selection-proven — `calc.bore_rim_limit(p)` is the exact per-shape rim bound
  (no kernel import); `BORE_RIM_SLACK` = 0.01 mm sits five orders above the measured
  1e-7 mm kernel tolerance and 40× below `MIN_WALL`; both position-based selectors raise
  `BuildError` on an empty selection while their feature is on; a 10-row `Counter`
  matrix asserts the exact selected edges per bore shape with and without recesses;
  the fixture stayed byte-unchanged through the change (L26) — Phase 7
- ✓ REQ-hex-bore + REQ-derived-dimensions-additive — `bore_hex` (across-flats, mm, default off) replaces the whole round/D-flat profile: `bore_d`/`bore_flat` ignored and warned, never refused (D-01 superseded the original `bore_flat` 422; hex × keyway 422 moved to Phase 9); two measured root-circle refusals at the chamfered corner (D-03); `hex_across_flats`/`hex_across_corners` added to `DerivedDimensions` with the 44-record pre-v0.2 fixture byte-unchanged and every post-fixture field required null on replay; heaviest allowed configuration 5.08 s of the 30 s budget via `make bench.build`; verified 30/30, `make verify` 330 tests, code review clean (1 info) (L27) — Phase 8
- ✓ REQ-keyway-bore + REQ-keyway-composes-with-d-flat + REQ-keyway-wall-refused (REQ-hex-rim-chamfer
  and REQ-bore-derived-numbers extended) — `keyway_width`/`keyway_depth` (mm, default off) cut one
  rectangular slot after the chamfered bore, so the rim selector never sees the keyway and the slot's
  own edges stay sharp; depth is measured from the as-cut bore wall `(bore_d + bore_clearance)/2`
  (the DIN 6885 / ISO R773 `t2` convention, D-14) and read back on the built solid within 1e-6 mm;
  the D-flat is kept; six refusals in `calc.check()` (hex × keyway, no bore, half-set, width ≥ bore,
  into the D-flat's wall, floor corner within MIN_WALL of the root — never capped) plus the round
  bore's chamfer-reach rule at the kernel's measured contact (`ROOT_CONTACT` 1e-9 mm; refuses no link
  that built before; closes the Phase 8 must-debt); the face recess yields to the keyway corner with
  the existing warnings; `keyway_floor_to_wall`/`keyway_width_effective` added to `DerivedDimensions`
  with the 44-record fixture byte-unchanged; heaviest of 32 sweep rows 4.85 s of 30 s; verified 12/12,
  `make verify` 396 tests (L28) — Phase 9
- ✓ REQ-tip-chamfer + REQ-tip-chamfer-capped — `tip_chamfer` (mm, 0–3 in 0.05 steps, default
  off) is a symmetric 45° edge break cut by `solid.chamfer()` on the `CIRCLE` edges at `ra`
  whose both endpoints lie on an end face, run last in `_build` after the keyway; the applied
  size is the smallest of three limits — `0.45 × face_width` (a land stays on the tip), the
  addendum `ra − r` (the footprint stays above the pitch circle) and the measured kernel
  boundary `ra − spline_start` (D-04: 10-01's spike bisected it to ~2 µm on five of six
  configurations, the sixth conservative by 0.04 mm, never optimistic) — capped and warned
  (L03), `tip_chamfer_effective` added to `DerivedDimensions`; proven on the built solid
  (+38 CONE faces, +114 edges, −22.7557 mm³ on three bore shapes; the proof goes red when the
  step is skipped; the boundary holds one step either side); the 44-record fixture
  byte-unchanged; help text names no size — the research-era sizing figure has no source;
  heaviest of 9 sweep rows 14.87 s of 30 s (must-debt filed: the timeout margin is now ~2×);
  verified 5/5, `make verify` 455 tests; review WR-01 (silent sub-resolution discard) and the
  Codex-found CR-01 (a warning naming a limit that was not binding) fixed, 2 info open (L29)
  — Phase 10
- ✓ REQ-spoke-cutout + REQ-hole-cutout + REQ-honeycomb-cutout + REQ-one-cutout-pattern +
  REQ-cutout-conflicts-refused-early + REQ-cutout-composes + REQ-cutout-derived-numbers — ten
  `GearParams` fields in three groups (Spokes, Holes, Honeycomb; every default 0/off); exactly
  one pattern per part (a 422 naming every set selector); each pattern's cutters subtracted in
  one `solid.cut(*cutters)` call in a new `_cut_body` step between the keyway and the tip
  chamfer, so the recess-floor fillet and bore-rim chamfer are already baked; spoke corners
  rounded by analytic tangent arcs (`spoke_fillet`, capped); honeycomb cuts whole cells only,
  count capped at the measured `HEX_CELL_CAP = 120` with `hex_cell` raised in 0.05 mm steps to
  fit and warned, never silently dropped; every wall rule (hub, rim, neighbour, and the human's
  own `0 < spoke_width < MIN_WALL` ruling) refused in `calc.check()` through `_under_min_wall`
  and pinned one field-step either side on the real kernel; `cutout_hub_wall`/`cutout_rim_wall`/
  `spoke_fillet_effective`/`hex_cell_effective`/`hex_cell_count` added to `DerivedDimensions`
  with the 44-record fixture byte-unchanged; `spoke_count`/`hole_count` `le` lowered to 40/60
  after D-18's build-time gate fired; heaviest measured rows 18.52 s (spokes) and 8.65 s
  (honeycomb, 1.15× its own 7.5 s share) of 30 s, both read under a loaded host and accepted
  at UAT; verified 7/7, UAT 5/5, `make verify` 621 tests; the six review findings (WR-01…WR-05,
  IN-01) were all fixed in `11-REVIEW-FIX.md` before the branch landed (L30) — Phase 11
- ✓ REQ-measured-build-time + REQ-three-interfaces-extended — the composed sweep
  (`bench/sweeps/composed.json`, 18 rows: each cutout pattern's heaviest row stacked with the
  tip chamfer at its cap and both recesses, on the largest hex bore and on a keyed round bore,
  at module 1.75 and 10) measured on four runs; the four `spoke_count=40` rows read over 30 s
  in every one regardless of load, so D-02 was superseded for that gate on the human's word,
  a probe found 32 the largest count inside budget and `spoke_count` `le` went 40 → 32; the
  re-run has every row inside `SPUR_BUILD_TIMEOUT` (heaviest 29.42 s), the two build-timeout
  debts resolved with that number; L19's gzip rule re-applied on the heaviest 17.3 MB fine STL
  keeps `_GZIP_LEVEL = 1`, L24's copy cost recorded (+52.9 ms, −56 MiB); 96 calc rows + 138
  refusal rows + 15 kernel rows prove every feature composes and every refusal reads the same
  with each other family on; one model-driven walk proves every field reaches the schema, the
  form and the CLI in one order, the composed document is byte-identical on `spur info` and
  `/api/info`, and all 23 refusals route identically to a 422 and to exit 2; `cli.md`'s exit
  contract corrected to the real 2/1/1 and pinned by a real-process test; the pre-v0.2 fixture
  byte-unchanged and green; the phase's +28.28 s `make verify` cost accepted against D-10's
  30 s line; verified 5/5, UAT 4/4, Nyquist and security audits clean, `make verify` 907 tests;
  ten review findings (WR-01…WR-05, IN-01…IN-05) at disposition `open` (L31) — Phase 12
- ✓ REQ-latency-observations-explained + REQ-latency-bar-demonstrated-or-superseded — a
  pre-registered twelve-run campaign through a split-process poller and a quiet-gated session
  driver (`.planning/phases/13-latency-bar/investigation/`, `13-LATENCY-INVESTIGATION.md`,
  predictions committed in `67eeefb` before any run) rules the two observations L18 left open:
  the second run of a pair reading worse is not reproduced in this environment (Pair A split
  between repetitions; `fleet-user` stopped where Runs 1–8 had it restart-looping), and the
  verdict floor is real (4 of 24 run×source verdict cells flip inside one percentile). The bar
  is demonstrated outright on the unmodified harness — `bar-3` Runs 13–14 at 1.31× and 1.42×
  idle p95 on both concurrent runs of one decisive session — after `bar-1`/`bar-2` capped out
  the D-05 quiet gate and were recorded non-decisive, never counted; outcome (b), D-09 and
  D-11 not reached, 13-05 not executed. SC3: the composed worst row (29.42 s alone) does not
  complete under ten concurrent builds in the shipped config — 0/10 served, 6 refused busy,
  4 admitted all past the 30 s timeout, 2 of them crashed to an undocumented 500 via a
  same-slot timeout-cleanup race at `pool.py:204`, filed as `must` debt with no `src/` change
  (D-17). L32 amends L18, the Dockerfile `HEALTHCHECK` comment says what was measured, and
  `2026-09-23-concurrent-latency-bar-waived.md` retired in `6709953`; verified 4/4, Nyquist
  and security audits clean, `make verify` 910 tests; two review findings (CR-01, WR-01) at
  disposition `open` (L32) — Phase 13
- ✓ REQ-root-lead-in-warned, REQ-readme-root-zone-states-the-limit,
  REQ-filleted-spoke-closed-form — the record is true as written: `derive()` warns when the
  root fillet's straight chord ends above the pitch circle (height at 3 dp; default gear
  −1.1875 mm silent, `{1.0, 14.5°}` +0.5625 mm and `{0.75, 20°}` +0.1250 mm warn, one field
  step either side proven), README and `_outline` say where the chord really ends; the
  filleted-spoke removed volume is checked against `_filleted_spoke_volume` (a polar closed
  form sharing no code with `_fillet_corner`, agreeing with the kernel to 2.73e-12 mm³) and
  all four plain cutout rows assert at `abs=1e-9` with a rim-corner tripwire proving the bar
  is load-bearing; L33 records both corrections and amends L09/L10/L30 by appending. UAT
  found two gaps — the skip-the-cutout tripwire's holes and cells rows proved nothing at
  `abs=1e-9`, and the debt file said a closed form "cannot exist" for four hole-through-web
  rows that have one — closed by 14-04: shared pure-math oracles `_holes_volume` /
  `_hex_cells_volume`, a control call on the unpatched build before the monkeypatch, the four
  rows on the web formula (tip-chamfer rows at `abs=1e-8` by the human's checkpoint answer
  over measured gaps of 5.85e-10 / 5.94e-10 / 6.55e-10 mm³; single-sided at `abs=1e-9`,
  gap 2.79e-12), every "cannot exist" reworded to "not derived here", the debt narrowed to
  eleven rows; verified 8/8, `make verify` 927 tests; three review findings (WR-01, IN-01,
  IN-02) at disposition `open` — Phase 14
- ✓ REQ-model-py-no-type-ignore + REQ-nyquist-phases-7-8 — `src/spur/model.py` carries
  zero `# type: ignore` (five retired at lines 213, 237, 239, 411, 420 of `085e5a6`)
  through two `isinstance` boundaries, `_body` at the three `fillet`/`chamfer` sites and
  `_shape_of` at the two `.val()` sites, each raising `BuildError` with one message that
  names a modelling defect, never a parameter; `make no-fake-done` refuses a new
  suppression under `src/spur/` (seen red against the five lines); the mypy override names
  `OCP.*` alone (cadquery ships `py.typed`); no geometry change — the five-site gear reads
  `('Solid', True, 4446.54642, 210, 604)` before and after and the 44-record fixture is
  byte-identical to `085e5a6`, `src`/`tests` differing only in `model.py` and
  `test_model.py`; the `Shape`-typing debt retired in `4f7e8fe`. Phases 7 and 8 have
  committed `VALIDATION.md`s at `status: validated`, `nyquist_compliant: true` as read
  (`5ba02d2`, `8ae468e`); Phase 7's three Manual-Only rows are one `nice` debt file,
  Phase 8 has none; the v0.2 audit's `nyquist` block amended in place and dated
  (`missing_phases: []`, `overall: compliant`); verified 16/16, UAT 3/3, Nyquist 0 gaps,
  security 15/15 closed, `make verify` 929 tests (L35) — Phase 16
- ✓ REQ-hook-and-commit-timeout-decided + REQ-same-slot-timeout-race-reproduced +
  REQ-same-slot-timeout-race-fixed + REQ-worst-row-margin-decided — the commit gate is split
  (L36, `c06749d`): the pre-commit hook runs `make verify.fast` (the four static steps plus
  pytest over every file but `test_model.py`/`test_pool.py`/`test_api.py`/`test_cli.py`,
  11.3 s warm, 19.9 s with an empty mypy cache), the whole `make verify` moves to pre-push,
  and the gate installs its own hooks from the main checkout only; proved by the phase's
  first live SDK commit `5a3332f` (`committed: true` in 13.57 s) and a real pre-push run
  (`Passed`, 63.97 s); the upstream request filed as open-gsd/gsd-core#5231; the `identical`
  scenario reproduced the same-slot undocumented 500 on attempt 1 (three `AttributeError`
  `build.failed` records) and read zero 500s after the two-fact guard + `_closed` fix
  (`0628182`; four tests red-then-green, 20/20 + 20/20 loops, `make verify` 2/3 with run 2
  the resource-tracker flake accepted by the human); L37 records the heaviest allowed
  composed row's limit as documented behaviour (29.42 s alone, 0.58 s margin,
  `BuildTimeout` at `duration_ms` 30004 under contention) with `SPUR_BUILD_TIMEOUT` 30 s and
  `spoke_count` `le` 32 unmoved; both `must` debts retired (`c06749d`, `7af75af`); verified
  5/5, Nyquist 0 gaps, security 17/17 closed, review 0 critical / 5 warning / 7 info, all 12 fixed (`17-REVIEW-FIX.md`, `9927f3c`…`366d6d4`), four further re-review items being fixed now,
  `make verify` 943 tests at 97.25 % — Phase 17
- ✓ REQ-root-mode-decided, REQ-outline-consumes-root-curve, REQ-derived-numbers-honest-under-trochoid,
  REQ-cutter-tip-radius-settable, REQ-undercut-warning-restated, REQ-trochoid-composes-and-is-priced —
  L38 (supersedes L10, amends L09 and L33): the hob-cut root is opt-in through `root_shape`,
  `root_fillet` is the hob's tip radius under it (capped and warned), the default does not move in
  v0.4 and Phase 20 is skipped with the flip's rules and trigger named; the outline consumes the
  Phase 18 curve with four guards and the dead band closed; every number beside the root is proved
  or warned (`root_waist` corrected to the narrowest arc by review CR-01); the undercut sentence
  comes from the cutter with `x_min`; parity proved the Phase 12 way; build time and gate cost
  measured and recorded (`bench/RESULTS.md` "Trochoid in the part (Phase 19)"); fixture
  byte-identical; verified 5/5, Nyquist 0 gaps, security 22/22 closed, `make verify` 1220 tests
  at 97.92 % — Phase 19
- ✓ A gear below the undercut limit has a trochoidal root that matches a known-good profile —
  Phase 19 (on request, `root_shape=trochoid`; the built root within 2e-3 × module of the
  swept-cutter oracle, L38)
- ✓ The root mode (always-on vs default-off field) is a logged decision, and the fixture rule is
  honoured either way — Phase 19 (L38: O4 — default-off `Literal` field now, the flip later under
  its own `Lxx` with `make fixture.regen`; fixture byte-identical through the milestone)
- ✓ A browser test proves the viewer's form, validation marks, warnings and STL load, and
  its place in `make verify` and CI is a logged decision with the measured cost (L39) — Phase 21

### Active

Milestone v0.5 Honest Form — hypotheses until shipped; REQ-IDs and acceptance live in
`REQUIREMENTS.md`.

- [ ] The web form tells the user before they type that a field is inert — conditional
  fields from schema metadata, a bore-shape selector over the flat fields — with the API,
  CLI and URL contracts unchanged.
- [ ] The download's file name tells a radial part from a trochoid one.
- [ ] L34's gate bar is re-set from an idle-host reading under its own `Lxx`.
- [ ] The three small ledger ideas (reverify recipe, Pi 5 claim, `make venv` constraint
  probe) are closed with a record each.

### Out of Scope

<!-- Not excluded as bad ideas — deferred, and already tracked under their own lifecycle per CLAUDE.md, not repeated here. -->

- An outline change that keeps the root lead-in below the active profile's start — the
  path L33 did not take (v0.3 decision: warned, not re-cut); revisit if the lead-in warning
  fires on gears people actually cut. The trochoidal root below the base circle is v0.4's
  scope (see Current Milestone), not this.
- The hob-root default flip, a cutout rotation field and a teeth-dependent honeycomb cap —
  the three `docs/ideas/` items v0.5 left filed: each has a named trigger that has not fired
  (D-09; a real part; D-12 plus a measured sweep), and taking one would supersede a logged
  decision on no evidence.
- Twelve `docs/tech_debt/active/` items at the v0.4 close (one `must`: the resource-tracker flake, filed 17-04, re-deferred 18-05 and 19-03 with a named trigger; eleven `nice`, three of them filed in v0.4 — the wedged worker, the xdist worker segfault at exit, the Phase 19 review deferral — each with its trigger; `milestones/v0.4-MILESTONE-AUDIT.md`). At the v0.4 start: ten `docs/tech_debt/active/` items (after the 2026-10-06 ledger pass,
  PRs #23–#25). The two `must` — the same-slot timeout-cleanup race (`pool.py:204`, D-17)
  and gsd's 30 s commit timeout against the ~64 s hook (trigger fired at L34) — retired in Phase 17
  (`c06749d` L36, `7af75af` L37). Eight `nice` stay deferred with their triggers: server-side
  cancellation, no authentication, Enji Guard, the eleven composed cutout literals at
  `rel=1e-6`, the sometimes-lost worker-coverage flush, Phase 7's three Manual-Only Nyquist
  rows, `Resolved in:` shas that live only on squashed branches, the English-throughout rule
  with no check in the gate. Resolved since the v0.3 close: `make no-fake-done` blind on
  macOS (#23), the stale `.planning/intel/` figures (#24) (`docs/tech_debt/INDEX.md`).
- Spline bores (v0.2 decision) — a standards surface (DIN 5480 and kin, many variants),
  not a cut; keyway and hex cover the shafts a hobbyist actually has.
- Helical, internal/ring and rack gears (v0.2 decision, deferred at v0.3, v0.4 and again at
  v0.5) — candidates for v0.6, one type per phase, helical first; bevel needs a
  product-scope decision before it is even a candidate (it contradicts "involute spur gear
  generator").

## Context

- **This product already ships.** `spur` is a working generator with a web UI, HTTP API,
  and CLI; `make verify` passes at the current commit. This PROJECT.md documents the
  shipped baseline (v0, v0.1, v0.2, v0.3) and the next milestone's candidates.
- The 2026-09-21 audit (`docs/review-2026-09-21.md`, findings F1–F8) is history: every
  finding — the unguarded Newton `centre_distance` solver, unbounded-by-bytes caches,
  infeasible absolute-mm defaults, no admission control, an under-pinned dependency
  closure, a `root_thickness` measured at the wrong radius, unused image weight, and
  assorted structure/test/CI gaps — was remediated per `docs/plan-2026-09-21.md` and is
  reflected as already-fixed in the live SPECs synthesized into `.planning/intel/`. Treated
  as history, not live requirements.
- Full codebase map: `.planning/codebase/ARCHITECTURE.md`, `STACK.md`, `TESTING.md`,
  `CONCERNS.md` (produced by `/gsd-map-codebase`, 2026-09-21, verified against the tree).
- Ingest intel: `.planning/intel/SYNTHESIS.md` (entry point), `decisions.md`,
  `requirements.md`, `constraints.md`, `context.md`; conflict report at
  `.planning/INGEST-CONFLICTS.md` (0 blockers, 0 warnings, 5 info).
- Tech debt (own lifecycle, `docs/tech_debt/INDEX.md`): 12 active at the v0.5 start — 1
  `must` (the resource-tracker flake, 17-04) and 11 `nice`; 24 resolved (10 in v0.1, 4 in
  v0.2, 6 in v0.3, 2 between v0.3 and v0.4, 2 in v0.4). Ideas backlog: `docs/ideas/` — 10
  items at the v0.5 start, 7 of them v0.5's scope (browser test for the viewer, conditional
  form fields, a bore-shape selector, the download name, a re-verification recipe, the Pi 5
  claim, constraining `make venv` to the closure) and 3 left filed with their triggers
  (trochoidal-root default flip, a cutout rotation field, a teeth-dependent honeycomb cap).
- Process since v0.1: phases run on `gsd/phase-NN-*` branches cut from `origin/main` and
  land only through `make pr.land PR=N` (L22/L25); `.planning/` rides the same PR as the
  code; the milestone close is its own PR and the tag sits on its squash. Every close so far
  (v0.1, v0.2, v0.3) was an `override_closeout` on proven-identical trees — the verifier's
  digests go stale when STATE.md is rewritten (v0.1) or when a later phase legitimately
  changes a shared file an earlier report covers (v0.2, v0.3); the cause is recorded per
  phase in `MILESTONES.md`.

## Constraints

- **Runtime**: Python 3.12 only — `cadquery-ocp` publishes wheels for nothing newer, and
  the floor is L23's; Docker image pins `python:3.12-slim-bookworm` (L01, L12, L23).
- **Stack**: CadQuery/OpenCascade for the solid, FastAPI + Pydantic v2 + uvicorn for the
  API, argparse for the CLI, vanilla JS + a vendored tree-shaken three.js bundle for the
  viewer (no Node at runtime), pytest, Docker + compose, GitHub Actions (L01, L11).
- **Module boundaries**: `calc.py` never imports the CAD kernel and does no I/O (runs on
  every keystroke); `model.py` is the only doorway to `cadquery`/`OCP`, no vendor object
  escapes it; `cli.py` never imports `app`/`fastapi`/`starlette`. Enforced by import-linter
  contracts, not discipline (L01/AGENTS.md, L04, L06).
- **Concurrency**: CAD builds run in `BuildPool` worker processes (`SPUR_BUILD_WORKERS`,
  default 2), routed by parameter-hash affinity, each build bounded by
  `SPUR_BUILD_TIMEOUT=30s` (~4× the worst measured build); the serving process cannot
  import the kernel (fourth import-linter contract). One `RLock` still wraps every
  OpenCascade call inside a worker (OCCT is not thread-safe), but it is per worker now, so
  concurrency across gears buys throughput too (L18 supersedes L06). Admission control
  (bounded build queue, `503` + `Retry-After`) lives in the web layer, never the CLI
  (L04); model-body gzip runs inside that slot at a measured `compresslevel=1` (L19).
- **Memory**: a parent byte budget (export cache, `SPUR_EXPORT_CACHE_MB`) plus N × the
  per-worker solid cache (`SPUR_SOLID_CACHE`); `compose.yaml` sets `mem_limit: 4g` from
  the N=2 sweep's 2878.5 MiB peak × 1.3 headroom, confirmed at zero failures — swept, not
  derived (L17 supersedes L07).
- **Defaults**: absolute millimetres, tuned to the 19-tooth m=1.75 gear this project
  started from; they never rescale — every shareable link that omits a field depends on
  them (L05).
- **Error contract**: a direct conflict between two explicit user choices is a `422`
  naming the fields; a trimmable dimension is capped and reported in `warnings`; an
  unsolvable centre distance is `None` plus a warning, never a plausible number (L03, L08).
- **Dependency pinning**: `requirements.txt` is the full resolved closure (31/31 packages),
  generated by `docker/refresh-requirements.sh`, installed `--no-deps`; never hand-edited
  (L12).
- **Gate**: `make verify` (ruff, mypy `--strict`, import-linter, unfinished-work scan,
  pytest on 8 xdist workers under `fail_under = 96`; 63.555 s warm measured on the dev host,
  bar 66 s — L34; no Docker) is the standard for "done"; `make check` adds the two
  container checks CI also runs (L13); `main` is landed only through `make pr.land PR=N`
  behind the ruleset (L22, L25). mypy strict with `disallow_any_explicit` on globally, no
  suppressions (L21 supersedes L14). `TRY003` off — error messages are the product (L15).
  No automatic formatter (L16).

## Key Decisions

Full log: `docs/architecture/decision_log.md` (single source of locked decisions — do not
re-litigate). Ingested verbatim into `.planning/intel/decisions.md`; carried here for
quick reference.

| ID | Decision | Outcome |
|----|----------|---------|
| L01 | Stack: Python 3.10–3.12, CadQuery/OCCT, FastAPI+Pydantic v2+uvicorn, argparse, vanilla JS + vendored three.js, pytest, Docker, GitHub Actions — detected, not chosen | ✓ Good — the 3.10 floor is superseded by L23 (3.12 only) |
| L02 | One `GearParams` model drives the web form, CLI flags, and API query params | ✓ Good |
| L03 | Cap and warn a trimmable dimension; refuse (422) a direct conflict — never guess | ✓ Good |
| L04 | Admission control (bounded build queue) lives in the web layer, not `model.py`; CLI never queues | ✓ Good |
| L05 | Defaults are absolute mm and never rescale; shareable links depend on them | ✓ Good |
| L06 | One `RLock` around every OpenCascade call; concurrency buys latency, not throughput | Superseded by L18 — the lock stays, its "not throughput" consequence is retired |
| L07 | Bounded caches (entries / bytes) + `malloc_trim(0)` after cache-missing export — measured 1.87 GiB → 1.5 GiB → 358 MiB | Superseded by L17 — ceiling re-swept on the N-worker topology |
| L08 | `centre_distance()` returns `None` (bisection, not Newton) rather than a confidently wrong number | ✓ Good |
| L09 | Root fillets solved analytically in the 2D outline, ~50× faster than OCCT's fillet operator | ✓ Good — amended by L38 (Phase 19): the analytic fillet stays for the radial root; the hob root is a spline per side through `RootCurve`, not a kernel fillet |
| L10 | Radial (not trochoidal) root below the base circle, with an undercut warning | Superseded by L38 (Phase 19) — the radial root stays the default; the hob-cut root is opt-in through `root_shape`; the undercut sentence is restated from the cutter in trochoid mode and unchanged in radial mode |
| L11 | three.js vendored as a committed, CI-byte-checked bundle; no Node at runtime | ✓ Good |
| L12 | `requirements.txt` is a generated, full pinned closure installed `--no-deps` | ✓ Good — L34 (Phase 15) also makes it CI's pip constraints file (`PIP_CONSTRAINT`), so CI resolves the kernel pair the fixture pins |
| L13 | `make verify` is the gate (dev shell, pre-commit, CI); `make check` adds container checks | ✓ Good — its "~11 s warm" was never measured; L34 (Phase 15) replaces it with 63.555 s at `-n 8` with coverage against a 66 s bar; L36 (Phase 17) splits it — `make verify.fast` at pre-commit, the whole gate at pre-push, CI and the ruleset still the wall |
| L14 | mypy strict, `disallow_any_explicit` off as a ratchet (`/api/info` is honest `dict[str, Any]`) | ✓ Superseded by L21 (Phase 4) — ratchet retired, debt file resolved |
| L15 | `TRY003` disabled; the rest of `TRY` on — error messages name the field and say what to change | ✓ Good |
| L16 | No automatic formatter — would flatten 648 lines of hand-set comment alignment | ✓ Good |
| L17 | Memory ceiling = parent byte budget + N × per-worker solid cache, swept on the real topology: `mem_limit: 4g` from N=2's 2878.5 MiB peak × 1.3 (supersedes L07) | ✓ Good — measured, zero failures at the limit |
| L18 | The `RLock` is per worker, not global; "concurrency buys latency, not throughput" retired. Single build within 2× idle p95 on every run; ten-concurrent accepted with caveat, not demonstrated (Runs 1–8: 1.31x–2.45x) (supersedes L06) | ✓ Caveat closed by L32 (Phase 13): demonstrated on `bar-3` (1.31×/1.42×), the debt retired in `6709953` |
| L19 | Model bodies gzip-encoded at measured `compresslevel=1` (51.5 ms vs 788 ms at level 9 on a 9 MB STL), inside the admission slot, cached once per encoding | ✓ Good |
| L20 | Structured JSON logging: stdlib `logging` + project-owned formatter, one object per line on stderr, `configure()` at both `cli.cmd_serve` and `app.lifespan()` (idempotent — uvicorn's spawn-based workers need the second site), parent process only, INFO default via `SPUR_LOG_LEVEL` | ✓ Good — post-review fix: records carrying `exc_info` render a `traceback` field (CR-01), `model()` catch-all logs `build.failed` (WR-01) |
| L21 | `disallow_any_explicit` on globally, no per-module override; the published responses are typed models (`DerivedDimensions`, `HealthReport`/`PoolState`); the pydantic mypy plugin's `init_typed`/`init_forbid_extra` retire the six class-line errors instead of six per-class suppressions; `Any` is never written — `object` narrowed at use, a library's own alias keeps the library's `Any` (supersedes L14) | ✓ Good — `make verify` green under the rule (104 tests); `--mate-teeth 0` now exits 2 like the API's 422; amended by L35 (Phase 16) — CadQuery's `Shape` typing stops at two checked boundaries, no suppression in `src/spur/` |
| L22 | CI is the merge gate: a ruleset on `main` requires `test (3.12)`, `vendor-bundle`, `image` green on an up-to-date head plus a pull request; a repo-owned `commit-msg` hook refuses the six skip tokens; the squash message is PR title + body; `main` is landed only via `make pr.land PR=N`, which refuses a red, stale, missing or token-carrying head and prints the squash commit's run URL | ✓ Good — ruleset read back live; gap plan 05-06 closed CR-01; the residual hand-typed cut line and the run-conclusion blind spot were retired in Phase 6 (L25 amends this entry); Phase 6 itself landed through the gate as PR #5 → `1173d21`, run 36145323487 |
| L23 | Python 3.12 only — `requires-python`, ruff `target-version`, the CI matrix, the Makefile interpreter and the README agree (supersedes L01's 3.10 floor; `cadquery-ocp` publishes wheels for nothing newer) | ✓ Good — `make verify` green on 3.12 (183 tests); CI job is `test (3.12)` alone |
| L24 | A cached solid never carries a mesh: STL export runs `exportStl` on `shape.copy()`, never on the process-global cached `cq.Solid` (`Clean_s` rejected: 4–13 % faster but leaves the mesh on the cached object for the whole export window); copy costs +1.4 to +17.6 ms per export and +3.2 to +7.7 MiB peak RSS on a 200-tooth fine export, measured; the autouse cache-reset fixture deleted | ✓ Good — `.BoundingBox()` exact after any export, a preview after a fine export is a preview (9,066 vs 46,278 triangles) |
| L25 | The merge gate reads the whole commit message and the run's own verdict (amends L22): the commit-msg hook takes git's entire buffer with no cut line; `pr.land` refuses `conclusion != success` and runs from an up-to-date `main`; after the merge it reports only what it observed; the read-to-merge window rests on the ruleset's up-to-date policy, not on anything `pr.land` reads (`--match-head-commit` pins the head, not the base) | ✓ Good — proven live on run 36116930241 and commits b72b0e1 / 20b63e4 |
| L26 | The pre-v0.2 part is pinned by a regression fixture (`tests/regression/pre_v0_2.json`, written only by `make fixture.regen`, 44 records / 85 cases, every later phase re-runs it unmodified), and an edge selector never silently selects nothing: `_bore_rim_edges` and `_groove_floor_edges` raise `BuildError` on an empty selection while their feature is on; the bore-rim bound lives in `calc.bore_rim_limit(p)` with a measured 0.01 mm slack in `model.py` | ✓ Good — fixture cost 16.27 s on `make verify`, accepted over the 15.0 s D-06 line (human decision); tripwire 32 red / 0 derive; `make verify` 289 tests |
| L27 | A hex bore replaces the whole round profile and its limits are the chamfered corner's, measured: `bore_hex` (0–200 mm, step 0.05, default 0) cuts `polygon(6, A/F + bore_clearance, circumscribed=True)` in place of the round/D-flat hole; `bore_d` and `bore_flat` are ignored with one warning naming each non-zero field (never a 422 — supersedes the original REQ-hex-bore sentence; hex × keyway stays a 422 and is Phase 9's); `check()` refuses a hex whose corners, or whose chamfered mouth (`bore_mouth_limit = rim + 2c/√3`), come within MIN_WALL of the root circle — no side-length rule, because the kernel chamfers a 0.375 mm side at the 3 mm bound; `recess_radii()` clears the chamfered mouth for every bore shape; the replay compares recorded fields exactly and requires later fields null; `make bench.build` runs a committed sweep file so Phases 9–12 reuse it | ✓ Good — 30/30 must-haves; `make verify` 330 tests; heaviest sweep row 5.08 s of 30 s (teeth 200, m 1.75, hex 200, recess both, chamfer 0.4); fixture byte-unchanged; round bore's own chamfer reach filed as `must` debt |
| L28 | A keyway is a slot cut after the bore's chamfer, its depth measured from the as-cut bore wall: `keyway_width`/`keyway_depth` (0–200 mm, step 0.05, default 0) cut a slot of width `keyway_width + bore_clearance` from the axis to a flat floor at `bore_radius(p) + keyway_depth` centred on +Y (a quarter turn from the D-flat), after `_cut_bore` so the rim selector's counts are the pre-keyway ones and the slot's edges are never chamfered; D-02/D-10/D-11 are the part's rules (arc wall to the D-flat's corner, floor corner vs the root, width < bore) and D-12 the kernel's measured contact; the recess yields to the keyway corner; no standard-table keyway size anywhere in help or docs | ✓ Good — 12/12 must-haves; `make verify` 396 tests; datum read back within 1e-6 mm; heaviest sweep row 4.85 s of 30 s (a 3 × 1.4 keyway that keeps its recess, lighter than the largest keyway); fixture byte-unchanged; Phase 8's round-chamfer debt resolved in `4b6a5b9` |
| L29 | The tooth-tip chamfer is a 3D edge break on the end-face tip arcs (`solid.chamfer()`, symmetric 45°, the last build step, selector requires both endpoints on an end face), capped at the smallest of the tip land (`0.45 × face_width`), the addendum (`ra − r`) and the measured kernel boundary (`ra − spline_start`, D-04, bisected to ~2 µm); help text names no size because the research-era sizing figure has no source; heaviest allowed configuration 14.87 s of 30 s | ✓ Good — measured; the ~2× timeout margin it left was filed as must-debt and resolved by Phase 12's composed sweep (`89304e2`) |
| L30 | Body cutouts are one pattern per part, cut in one boolean, and the honeycomb's cell count is capped at a measured constant: ten fields in three groups, `_cut_body` after the keyway and before the tip chamfer; spoke corners are analytic tangent arcs (`_fillet_corner(inside=)`); honeycomb whole cells only, `HEX_CELL_CAP = 120` written from the pre-implementation spike's row (7.15 s of D-11's 7.5 s share at 200 teeth, module 10; 150 cells read 7.95 s), raise-to-fit in the field's own 0.05 mm step; every `MIN_WALL` comparison goes through `_under_min_wall` (`round(wall, 6) < MIN_WALL` — float residue measured at 0.39999999999999947 at the tracer's hub boundary); `spoke_count`/`hole_count` `le` lowered from 200 to 40/60 after the build-time gate fired | ✓ Good — verified 7/7, UAT 5/5, `make verify` 621 tests; the cap and its 8.65 s row accepted as measured under a loaded host (UAT 2–3); the spokes' 33.39 s arithmetic total with the tip chamfer filed as must-debt and resolved by Phase 12's composed sweep (`89304e2`); the six review findings fixed in `11-REVIEW-FIX.md` before landing; the filleted-spoke row's pinned literal replaced by a closed form in L33 (Phase 14) |
| L31 | v0.2 composes: the 18-row composed sweep measured across four runs (the four over-budget `spoke_count=40` rows load-independent, so D-02 superseded for that one gate by the human); `spoke_count` `le` 40 → 32 from a probe (32 inside at 29.41 s, 33 over at 30.11 s); every composed row inside 30 s on the re-run (heaviest 29.42 s); L19's rule re-applied on the 17.3 MB heaviest fine STL keeps `_GZIP_LEVEL = 1`, L24's copy cost recorded only; 96 + 138 calc rows and 15 kernel rows prove the matrix; one field walk, a byte-identical composed document and 23 identically routed refusals prove three-interface parity; the CLI's real 2/1/1 exit contract moved into `cli.md`; export bytes are explicitly not compared by the fixture replay (L26); the phase's +28.28 s gate cost accepted against D-10's 30 s line | ✓ Good — verified 5/5, UAT 4/4, `make verify` 907 tests; all 14 review findings fixed before the v0.2 close (`12-REVIEW-DISPOSITION.md` 0 open, 2026-10-01) |
| L32 | The concurrent latency bar is demonstrated on the harness as it stands, not waived (amends L18): `bar-3` Runs 13–14 read 1.31× and 1.42× idle p95 on both concurrent runs of one decisive session behind the D-05 quiet gate, after two capped-out attempts recorded non-decisive; the two observations L18 left unexplained are ruled by a pre-registered twelve-run campaign — the second-run-worse effect not reproduced in this environment, the floor real; SC3 measured once: the composed worst row does not complete under ten concurrent builds (0/10 served; a same-slot timeout-cleanup race returns an undocumented 500, filed as debt, `src/` untouched); the Dockerfile `HEALTHCHECK` comment and the retired debt say what was measured | ✓ Good — verified 4/4; `make verify` 910 tests; `2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md` (must) retired by Phase 17 (`0628182` the race, `7af75af` the margin — L37); review CR-01/WR-01 open |
| L33 | The root lead-in is warned, not re-cut, and the filleted-spoke cutout is proved against a closed form (amends L09, L10 and L30): `derive()` appends one sentence when `round(spline_start(pr, root_fillet(p)) − pr.r, 3) > 0`, naming the height, instead of regenerating the pre-v0.2 fixture under a new entry (L05 keeps every shared link's part); the filleted-spoke removed volume is asserted against `_filleted_spoke_volume` at `abs=1e-9` (kernel agreement 2.73e-12 mm³), the pinned literal `2934.725405` demoted to a comment; the 15 composed cutout rows are named — four hole-through-web rows on the web formula (tip-chamfer rows at `abs=1e-8`, a bar the human set over measured gaps of ~6e-10 mm³ with 1.5× headroom at 1e-9; single-sided at `abs=1e-9`), eleven still at a 6 dp literal and `volume_rel=1e-6` because their closed form is not derived here | ✓ Good — verified 8/8, UAT 5/5 after gap plan 14-04, `make verify` 927 tests; `src/` untouched by 14-04 and the pre-v0.2 fixture byte-identical to `5d9e907`; review WR-01 (`volume_rel` shadows `volume_abs`), IN-01, IN-02 open; the prior platform-calibration finding (abs bars measured only on macOS arm64) is no longer in the ledger — see `8cfbc16`'s REVIEW.md — amended by L38 (Phase 19): the lead-in warning is evaluated only where a chord exists (the radial root) |
| L34 | The gate is measured, runs on eight workers under a coverage floor, and CI installs the pinned kernel (amends L12 and L13): the serial profile read 224.28 s (pytest 99.8 % of it, `tests/test_model.py` ~74 % of pytest); the xdist sweep's knee is N = 8 by a rule fixed before the read; the human set the bar at the profile checkpoint (`knee-headroom N=8 bar=66 cuts=none before=244.59`), read as mean(B) 63.555 s at `-n 8` with coverage — met with 2.445 s to spare, all 15 priced cuts refused by name, `tests/` untouched; `fail_under = 96` from C0's 96.99 % serial baseline (`precision = 2`; workers counted via `concurrency = ["multiprocessing", "thread"]`, `parallel`, `sigterm`), a red run at 90.24 % recorded and not committed; CI's `make verify` runs under `PIP_CONSTRAINT: requirements.txt` and prints `cadquery 2.8.0 cadquery-ocp 7.9.3.1.1` (run 37181871926), a conflicting pin fails closed (`ResolutionImpossible`) | ✓ Good — verified 15/16 with the one `backstop` truth accepted by the human, UAT 28/28, security 22/22 closed; `make verify` 927 tests at 97.21 %; two `must` debts retired (`2aadcea`, `839dfea`); the lost-worker-flush reading (96.99 %) filed as `nice` debt; the gsd commit-timeout debt retired by L36 (Phase 17, `c06749d`) — Phase 19's kernel-tier proofs put `make verify` at 192.94 s mean on the 18-CPU M5 Max against the 66 s bar read on the M2 Max; accepted (`accept-A`, L38), no test moved; the bar's re-set is an open decision |
| L35 | Vendor shape typing stops at two checked boundaries, and Phases 7 and 8 carry a Nyquist record (amends L21): `_body(shape) -> cq.Solid or cq.Compound` at the three `fillet`/`chamfer` sites and `_shape_of(wp) -> cq.Shape` at the two `.val()` sites, each one `isinstance` check raising `BuildError` with one message naming a modelling defect — never `typing.cast` (it checks nothing and gives a test nothing to see) or `TypeIs`; the pipeline's annotations stay `cq.Shape`, `_gear_blank` included (`-> cq.Solid` gave five `[assignment]` errors); `cadquery.*` left the mypy override because it ships `py.typed`, `OCP.*` stays; `make no-fake-done` refuses a suppression under `src/spur/` and only there; the error surfaces as a 422 `build_error` like the three selector guards; Phases 7 and 8 read `nyquist_compliant: true` from their committed `VALIDATION.md`s, Phase 7's three Manual-Only rows filed as one `nice` debt file, the v0.2 audit's `nyquist` block amended in place and dated by a rule written beside the rows | ✓ Good — five suppressions retired in `4f7e8fe`, 927 → 929 tests, the five-site gear tuple and the fixture unchanged against `085e5a6`, cold-cache mypy byte-identical before and after (`37 source files`); verified 16/16, UAT 3/3, Nyquist 0 gaps, security 15/15 closed; the cast clause rests on mypy strict + review by the human's choice (16-UAT test 2), no pin |
| L36 | The commit gate is split, measured, and self-installing (amends L13 and L34): `verify: verify.static test` and `verify.fast: verify.static test.fast` share one static prefix; `make verify.fast` (every test file but `test_model.py`/`test_pool.py`/`test_api.py`/`test_cli.py`, `--ignore=` exclusion, `--no-cov`) runs at pre-commit — 11.28/11.30/11.28 s warm, 19.94 s with an empty mypy cache, all under the SDK's 30 s kill — and the whole `make verify` runs at pre-push; `$(HOOKS)` installs the three hooks from `verify.static` in the main checkout only (pre-commit 4.6.2 writes into the shared git-common-dir and bakes the installing venv's python into the shim); nine pre-push scenarios measured in a scratch repo (tag-only, delete-only and `--no-verify`/`SKIP=` pushes run nothing; a fresh clone has no hook); a killed SDK commit is recovered by waiting for the orphaned hook, then one plain `git commit`, never a blind retry (D-07) | ✓ Good — hook commit `c06749d` passed `verify-fast` in 12.33 s; SC1: SDK commit `5a3332f` `committed: true` in 13.57 s; real pre-push `Passed` 63.97 s; `pre-commit install` on a shallow clone wrote all three hooks (macOS; read at ship on CI run 37460451701: all three lines printed, no hook fired); upstream request open-gsd/gsd-core#5231; the commit-timeout debt retired |
| L37 | The heaviest allowed composed row's limit is documented behaviour, not a moved default (amends L31 and L32): the row (module 10, keyed bore, tip chamfer 3, `spoke_count` 32) builds in 29.42 s alone — 0.58 s of `SPUR_BUILD_TIMEOUT`'s 30 s — and under ten identical concurrent requests the slot-holder ends `503 timeout` at `duration_ms` 30004; the contract under contention is the documented 503, `SPUR_BUILD_TIMEOUT` stays 30 s and `spoke_count`'s `le` stays 32 (raising the default and a third `le` cut both rejected; L05, L08); the same-slot timeout race is fixed by the two-fact guard (`executor_for(p) is executor and executor._processes is not None`) and a `_closed` flag `recreate_for` honours, so a second same-slot timeout raises `BuildTimeout`, never `AttributeError` | ✓ Good — reproduced on attempt 1 (three `AttributeError` records), zero 500s after `0628182`; four tests red→green, 40/40 loops, `make verify` 2/3 (run 2 the resource-tracker flake, `proceed-as-known-flake`); `params.py` byte-identical, `app.py` comment-only; race debt retired `7af75af`; review WR-01: the README/L37 clause "a bigger host raises the variable" was backwards (slower or busier host), corrected in `9927f3c` with the other 11 review findings (`17-REVIEW-FIX.md`, `9927f3c`…`366d6d4`); the incremental re-review's four further items are being fixed now |
| L38 | The hob-cut root is opt-in through `root_shape` (`radial` default, `trochoid`; a `Literal`, never a bool), `root_fillet` is the hob's tip radius under it, every number beside it is proved or warned (`root_form_d` the cutter-envelope junction, `root_waist` the narrowest arc under a 0.4 mm floor, `root_thickness`/`root_gap` null, the undercut sentence from the cutter with `x_min`), four structural guards and `ROOT_ARC_MIN` keep a broken outline out of the kernel, and the default does not move in v0.4 — Phase 20 skipped, the flip deferred to a real fit report or a mating-pair request below z_min, in one commit with `make fixture.regen` under its own `Lxx` (supersedes L10, amends L09 and L33) | ✓ Good — verified 5/5, Nyquist 0 gaps, security 22/22 closed; review CR-01 (`root_waist` read at the narrowest half-angle, 2–5 % high on crossing joins) and WR-01 fixed (`e733cc2`, `b51931c`), 4 info deferred; fixture byte-identical to `df4749e`; `make verify` 1220 tests at 97.92 %, 192.94 s mean against L34's 66 s (accepted, bar re-set open) |
| L39 | A headless browser runs the shipped viewer inside `make verify` and CI, out of the commit slice, at a measured price (amends L13 and L36, restates L11): `playwright==1.63.0` in the dev extra only, Chrome Headless Shell under `.venv/ms-playwright` on SwiftShader; the server fixture on a `127.0.0.1` socket passed by descriptor, `SPUR_*` scrubbed, killed by process group with a floor of 3 live members before the kill; the drawn canvas judged by a PNG byte ratio bar of 4.9 and the triangle count the page reports against the STL header; the 44 fixture records' requests pinned in `tests/regression/golden_requests.json`, written by `make golden.regen` only; `make test` depends on the shell stamp, `test.fast` and `test-image` exclude the file, AST pins forbid any skip path; the human kept the test in the gate at 21-07's price decision (`accept`, O1); every figure cited to a SUMMARY sha or to `bench/RESULTS.md` "Browser test of the viewer (Phase 21)", none restated here | ✓ Good — verified 5/5, Nyquist 0 gaps, security 25/25 closed; CI run 38059369744 green (1226 passed) at `88df5cf`; review 0 critical, 3 warnings filed as debt (`fc53e5c`), 4 info open in `21-REVIEW-DISPOSITION.md`; `make verify` hung once at the 600 s limit with no failure (filed `must`, `068358c`); `ubuntu-latest` moves to Ubuntu 26 on 2026-10-19 (filed `must`) |

## Success Metric (Milestone v0.1)

Set by the human at milestone start — no ingested document derived it. All four held at
close (2026-09-25); outcomes in italics:

1. **Measured event-loop latency.** `/api/health` p95 stays under an agreed threshold with
   a named build in flight, measured against the baseline on record (0.22 s → 0.76 s →
   2.00 s under one 200-tooth fine build, 12-core machine). *Met for the single-build
   scenario on every recorded run (L18); the ten-concurrent bar was waived on the Runs 1–8
   evidence and is `must` debt.*
2. **`disallow_any_explicit` on.** `make verify` passes with the rule enabled; L14's named
   ratchet is retired rather than re-deferred. *Met — L21, `make verify` green.*
3. **Logs answer an incident.** A named set of decision branches — build started, build
   failed, export served from cache or built, queue refused — is observable in structured
   output, proven by a test rather than by reading the console. *Met — L20, five records
   under `caplog` tests.*
4. **The three `must` debt files are resolved.** `Status: resolved`, commit sha recorded,
   `git mv`'d into `docs/tech_debt/resolved/`, INDEX rows moved — in the same commits as
   the fixes, per `CLAUDE.md`. *Met — retired in Phases 2–4; Phase 6 retired five more
   surfaced during the milestone (10 resolved in total).*

## Success Metric (Milestone v0.2)

Set by the human at milestone start (2026-09-25); outcome at close (2026-10-01): all three
met — (1) every feature shipped on UI/API/CLI from `GearParams` with its tests in the same
PR, proven by one model-driven field walk; (2) `bench/RESULTS.md` records build and export
time per feature and for the composed sweep, every row inside 30 s after `spoke_count` `le`
32; (3) the 44-record fixture is byte-unchanged and green — read as identical
`DerivedDimensions` and solid, export bytes not compared (L26, 12-01 SC5).

1. **Three interfaces, one change.** Each new feature ships on UI, API and CLI from the one
   `GearParams` model, with its tests, in the same change.
2. **A measured number per cut.** A recorded build time per feature at its heaviest allowed
   configuration — including recess + cutout combined — inside `SPUR_BUILD_TIMEOUT`, with
   the cap that keeps it there documented.
3. **Old links unchanged.** A test proves every parameter set valid before v0.2 yields
   identical derived dimensions and an identical export after v0.2.

## Success Metric (Milestone v0.3)

Derived from the kickoff summary the human confirmed 2026-10-01. Outcome at close
(2026-10-05): 2 and 3 met; 1 not met as written — the four `must` rows the milestone was
scoped on are retired (`6709953`, `825095f`, `61e1bea`, `839dfea`), and Phase 13 filed one
new `must` (the same-slot timeout race, D-17) that stays active with its trigger. Accepted
as a known gap by the human (`milestones/v0.3-MILESTONE-AUDIT.md`, `MILESTONES.md` Known
Gaps). Lesson recorded in `RETROSPECTIVE.md`: write the metric about the rows that exist at
kickoff.

1. **No `must` row left.** `docs/tech_debt/INDEX.md` "Active" has zero `must` rows, each
   retired file carrying the sha of the commit that fixed it.
2. **Every claim measured or warned.** The latency bar reads ≤2.00× on both runs of one
   session or is superseded by an `Lxx` with the measurement; the lead-in limit is a
   warning the user sees; the filleted-spoke volume matches a closed form; `make verify`'s
   wall time and the coverage baseline are numbers in `bench/RESULTS.md`, not estimates.
3. **Same part.** `tests/regression/pre_v0_2.json` byte-unchanged and green at the close;
   `GearParams` has no new field.

## Success Metric (Milestone v0.4)

Three clauses from the milestone goal, read at the close (`milestones/v0.4-MILESTONE-AUDIT.md`):

1. **The last two `must` items retired by measurement or decision.** Met — the commit-timeout gap (`c06749d`, L36, proved by SDK commit `5a3332f`) and the same-slot race (`0628182` fix, `7af75af` margin, L37) are in `docs/tech_debt/resolved/`. One `must` the milestone itself filed (the resource-tracker flake, 17-04) stays active with a named trigger — the same shape as v0.3's metric 1.
2. **The hob's trochoid root in the part, proven against an independent oracle.** Met — T1–T4 at the calc tier (Phase 18), the built root within 2e-3 × module of the swept-cutter oracle at 401 positions on seven rows with a tripwire (Phase 19); every number beside it proved or warned, `root_waist` corrected to the narrowest arc by review CR-01 before verification.
3. **The fixture rule honoured, never bypassed.** Met — `tests/regression/pre_v0_2.json` byte-identical to the `v0.3` tag; the default unmoved (O4); the flip deferred under L38 with `make fixture.regen` and its own `Lxx` as the only path.

Cost recorded, not hidden: `make verify` 52.89 s → 192.94 s mean on the M5 Max for Phase 19's kernel proofs (L34's 66 s bar unmoved, `accept-A`).

## Success Metric (Milestone v0.5)

Derived from the kickoff summary the human confirmed 2026-10-10; read at the close.

1. **The browser sees it.** A browser-driven test exercises the shipped `app.js` — the form
   builds from `/api/schema`, an invalid field is marked, a warning renders, the STL loads —
   and whether it runs inside `make verify` is an `Lxx` with the measured cost beside L34's
   re-set bar.
2. **Honest before, not after.** A field whose value would be ignored says so in the form
   before it is typed; a bore shape is picked, not inferred from a warning; the API, CLI and
   URL send and accept exactly the fields they do today (one model-driven field walk).
3. **Same part, same links.** `tests/regression/pre_v0_2.json` byte-identical to the `v0.4`
   tag; `GearParams` has no new field; every ledger idea taken is closed in the commit that
   closes it.

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-10-10 after Phase 21.*
