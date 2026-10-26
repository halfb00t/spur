# Roadmap: spur

## Milestones

- ✅ **v0.1 Hardening** — Phases 1–6 (shipped 2026-09-25) — full detail in
  `milestones/v0.1-ROADMAP.md`, audit in `milestones/v0.1-MILESTONE-AUDIT.md`
- ✅ **v0.2 Fit to Shaft** — Phases 7–12 (shipped 2026-10-01) — full detail in
  `milestones/v0.2-ROADMAP.md`, audit in `milestones/v0.2-MILESTONE-AUDIT.md`
- ✅ **v0.3 Clean Ledger** — Phases 13–16 (shipped 2026-10-05) — full detail in
  `milestones/v0.3-ROADMAP.md`, audit in `milestones/v0.3-MILESTONE-AUDIT.md`
- ✅ **v0.4 True Root** — Phases 17–20 (shipped 2026-10-09; Phase 20 skipped under L38) — full
  detail in `milestones/v0.4-ROADMAP.md`, audit in `milestones/v0.4-MILESTONE-AUDIT.md`
- ✅ **v0.5 Honest Form** — Phases 21–25 (shipped 2026-10-15) — full detail in
  `milestones/v0.5-ROADMAP.md`, audit in `milestones/v0.5-MILESTONE-AUDIT.md`
- ✅ **v0.6 Clean Ledger** — Phases 26–29 (shipped 2026-10-23; Phase 29 closed, trigger not
  fired) — full detail in `milestones/v0.6-ROADMAP.md`, audit in `milestones/v0.6-MILESTONE-AUDIT.md`
- 🚧 **v0.7 Splined Shaft** — Phases 30–34 (in progress; Phase 34 is blocked until the human
  supplies the DIN 5480 copy's local path, and Phase 31 needs anchor rows from it)

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)
- Numbering continues across milestones — v0.6 starts at Phase 26, after v0.5's Phase 25;
  v0.7 starts at Phase 30, after Phase 29 (Phase 29 keeps its number even if it closes with its
  item still active); the next milestone starts at Phase 35.

<details>
<summary>✅ v0.1 Hardening (Phases 1–6) — SHIPPED 2026-09-25</summary>

- [x] Phase 1: v0 Baseline (Shipped) (no plans — built and verified directly against `make verify` before GSD)
- [x] Phase 2: CAD Off the Event Loop (5/5 plans) — completed 2026-09-24
- [x] Phase 3: Structured Logging at the Composition Boundary (3/3 plans) — completed 2026-09-24
- [x] Phase 4: Typed Derived-Dimensions Contract (3/3 plans) — completed 2026-09-24
- [x] Phase 5: CI Observed Green (6/6 plans) — completed 2026-09-25
- [x] Phase 6: Address tech debt: merge gate + solid cache (4/4 plans) — completed 2026-09-25 (added 2026-09-25 after the Phase 5 review and the first milestone audit)

Goals, success criteria and plan lists: `milestones/v0.1-ROADMAP.md`. Phase artifacts:
`milestones/v0.1-phases/`. Quick tasks: `milestones/v0.1-quick/`.

</details>

<details>
<summary>✅ v0.2 Fit to Shaft (Phases 7–12) — SHIPPED 2026-10-01</summary>

**Milestone Goal:** A generated gear mounts on a real shaft and prints light — new bore
profiles, body cutouts and a tooth-tip chamfer, all additive on the shipped spur pipeline,
with tooth measurements untouched.

- [x] Phase 7: Foundation — Generalized Edge Selection + Regression Fixture (2/2 plans) — completed 2026-09-26
- [x] Phase 8: Hex Bore (4/4 plans) — completed 2026-09-26
- [x] Phase 9: Keyway Bore (5/5 plans) — completed 2026-09-27
- [x] Phase 10: Tooth-Tip Chamfer (5/5 plans) — completed 2026-09-28
- [x] Phase 11: Body Cutouts (9/9 plans) — completed 2026-09-29
- [x] Phase 12: Composition Pass (9/9 plans) — completed 2026-09-30 (re-verified 2026-10-01 after the review fixes)

Goals, success criteria and plan lists: `milestones/v0.2-ROADMAP.md`. Phase artifacts:
`milestones/v0.2-phases/`. Decisions: L26–L31 in `docs/architecture/decision_log.md`.
Landed as PRs #7–#13 through `make pr.land`; the close is its own PR.

</details>

<details>
<summary>✅ v0.3 Clean Ledger (Phases 13–16) — SHIPPED 2026-10-05</summary>

**Milestone Goal:** Every `must` debt item retired by measurement or a logged decision,
every false claim in the record made true or warned, and the gate itself measured — no new
user-facing geometry, no new `GearParams` field, the 44-record pre-v0.2 fixture
byte-unchanged throughout.

- [x] Phase 13: Latency Bar (7/7 plans; 13-05 not executed by design — outcome (a)) — completed 2026-10-02
- [x] Phase 14: Honest Record (4/4 plans; 14-04 a gap-closure plan after UAT) — completed 2026-10-03
- [x] Phase 15: The Gate, Measured and Pinned (6/6 plans) — completed 2026-10-04
- [x] Phase 16: Typing & Validation Debt (3/3 plans) — completed 2026-10-05

Goals, success criteria and plan lists: `milestones/v0.3-ROADMAP.md`. Phase artifacts:
`milestones/v0.3-phases/`. Decisions: L32–L35 in `docs/architecture/decision_log.md`.
Landed as PRs #16–#19 through `make pr.land` after the start PR #15; the close is its own
PR. Outcome against PROJECT.md's three success metrics: 2 and 3 met; 1 ("zero `must` rows")
not met as written — the four `must` rows the milestone was scoped on are retired, and the
one `must` Phase 13 itself filed (the same-slot timeout race, D-17) stays active with its
trigger (`milestones/v0.3-MILESTONE-AUDIT.md`).

</details>

<details>
<summary>✅ v0.4 True Root (Phases 17–20) — SHIPPED 2026-10-09</summary>

**Milestone Goal:** Retire the last two `must` items — the same-slot timeout race by a
measured reproduction and a narrow fix, the commit-timeout gap by a logged decision — then
replace the radial root below the base circle with the trochoid a hob cuts, proven against
an independent oracle, with the fixture rule (L26) honoured under its own `Lxx`, never
bypassed.

- [x] Phase 17: Debt First — Commit Gate and Pool Race (5/5 plans) — completed 2026-10-06
- [x] Phase 18: Trochoid Maths, Proved (6/6 plans; 18-06 a gap-closure plan after UAT) — completed 2026-10-08
- [x] Phase 19: The Trochoid in the Part (11/11 plans; review CR-01/WR-01 fixed before verification) — completed 2026-10-09
- [x] Phase 20: The Flip (conditional) — skipped under L38 (O4, flip deferred to D-09's trigger: a real fit report or a mating-pair request below z_min); criteria not applicable; the flip owned by `milestones/v0.4-REQUIREMENTS.md` "Trochoid follow-ups"

Goals, success criteria and plan lists: `milestones/v0.4-ROADMAP.md`. Phase artifacts:
`milestones/v0.4-phases/`. Decisions: L36–L38 in `docs/architecture/decision_log.md`.
Landed as PRs #27–#29 through `make pr.land` after the start PR #26; the close is its own
PR. Outcome against the milestone goal's three clauses: all met (the two scoped `must` rows
retired; the hob root in the part proven against the swept-cutter oracle; the fixture
byte-identical to `v0.3`); one `must` the milestone itself filed (the resource-tracker flake,
17-04) stays active with its trigger, and L34's 66 s gate bar sits against a gate that reads
~193 s after the kernel-tier proofs — accepted (`accept-A`), its re-set an open decision
(`milestones/v0.4-MILESTONE-AUDIT.md`, status `tech_debt`).

</details>

<details>
<summary>✅ v0.5 Honest Form (Phases 21–25) — SHIPPED 2026-10-15</summary>

- [x] Phase 21: Browser Test of the Viewer (8/8 plans) — completed 2026-10-10
- [x] Phase 22: Download Name Carries the Root (2/2 plans) — completed 2026-10-11
- [x] Phase 23: Conditional Form Fields (4/4 plans) — completed 2026-10-11
- [x] Phase 24: Bore-Shape Selector (4/4 plans; discretionary, executed) — completed 2026-10-13
- [x] Phase 25: Gate Bar Re-Set, Venv Probe, Ledger Close (5/5 plans) — completed 2026-10-14

Goals, success criteria and plan lists: `milestones/v0.5-ROADMAP.md`. Phase artifacts:
`milestones/v0.5-phases/`; the quick task (#37) in `milestones/v0.5-quick/`. Decisions:
L39–L43 in `docs/architecture/decision_log.md`, L27 amended by #37. Landed as PRs #33–#38
through `make pr.land` after the start PR #31; the close is its own PR. Outcome against the
milestone goal: met — the browser test in the gate, the UI ideas taken in dependency order,
the bar re-set by the human under a rule committed first (300 s, L43), the three ledger items
closed, no new `GearParams` field, the fixture byte-identical to `v0.4`. Phases 21–24 read
`stale` by fingerprint, cause proven per file (`milestones/v0.5-MILESTONE-AUDIT.md`, status
`tech_debt`); Phase 22's two review warnings filed as `must` debt at the close.

</details>

<details>
<summary>✅ v0.6 Clean Ledger (Phases 26–29) — SHIPPED 2026-10-23</summary>

- [x] Phase 26: Gate Fails With a Cause (7/7 plans) — completed 2026-10-20 (re-verified 2026-10-21 and 2026-10-23 after later squashes)
- [x] Phase 27: Ledger Tests and Harness (6/6 plans) — completed 2026-10-20 (re-verified 2026-10-23)
- [x] Phase 28: Refuse the Bad Link (8/8 plans; 28-05..28-08 gap-closure plans after UAT) — completed 2026-10-22
- [x] Phase 29: Ubuntu 26 Final Reading (1/1 plan) — closed 2026-10-22 on its close condition, trigger not fired; REQ-ubuntu26-classified-on-migration deferred to Future Requirements, the debt item still active

Goals, success criteria and plan lists: `milestones/v0.6-ROADMAP.md`. Phase artifacts:
`milestones/v0.6-phases/`. Decisions: L44 (a bad link is refused through the 422 path) and
L45 (a tip chamfer not cut prints no number) in `docs/architecture/decision_log.md`. Landed
as PRs #41, #42, #44–#47; #40 the throwaway Ubuntu 26 PR, closed unmerged; the close is its
own PR. Outcome against the milestone goal: met. The gate passes or fails with a cause, the
`must` debt in scope retired, every open review finding dispositioned, no new `GearParams`
field, `tests/regression/` byte-identical to `v0.5`. Besides the refused bad link, the L45
null print and the `root_fillet` label also changed visible text, both by the human's
decision. Audit `tech_debt`, 16/16; the one partial flow is the known WR-02 deferral.

</details>

### 🚧 v0.7 Splined Shaft (In Progress)

**Milestone Goal:** Generate an external DIN 5480 involute splined shaft with a plain shank as a
second part type beside the gear — every printed number derived from the standard (or from the
copy of it the human supplies) or warned with no number, the same STL/STEP download, preview and
numbers from the web page, the API and the CLI — with every existing gear link's part untouched:
no new `GearParams` field, `tests/regression/` and `ci.yml` byte-identical to the `v0.6`
baseline, the gear `/api/schema` response byte-equal.

- [x] **Phase 30: Scope, Seam and Gear-Safety Guard** - The widening to a gear and spline (completed 2026-10-23)
      generator is a logged decision, the shaft is walled off from the gear by import contracts
      and its own route prefix, and one check proves at every phase close that no gear link moved
- [ ] **Phase 31: Shaft Maths, Parameters and Designation** - A pure, oracle-proved `ShaftParams`
      with frozen field names: profile shift from d_B, tip, root and thickness, M_Re at nominal,
      d_Ff `null` until proven, and a designation that round-trips; needs anchor rows from the copy
- [ ] **Phase 32: The Shaft Solid** - Splined section, plain shank and end chamfer as a valid solid
      that exports to STL and STEP, its volume matched to a closed form, its heaviest build
      measured against the memory ceiling and the timeout
- [ ] **Phase 33: Interfaces and Parity** - The shaft served under `/api/shaft/...`, by
      `spur shaft` and by a part switch on the web page, one parametrised test proving the three
      agree, the designation accepted as input, and WR-02 fixed on the same edit
- [ ] **Phase 34: Fit Tables and Tolerance Window** - The human's DIN 5480 values in a private
      gitignored file, transcribed twice and checked; tooth-thickness windows, M_Re limits and the
      maximum-material solid with them, `null` and warned without them; blocked until the copy's
      local path is supplied

## Phase Details

### Phase 30: Scope, Seam and Gear-Safety Guard

**Goal**: The product is declared a gear and spline generator, in the decision log, before any
shaft code exists; the shaft is walled off from the gear by import contracts and its own route
prefix; and one check, run at every phase close, proves that no existing gear link builds a
different part. Every later phase adds shaft code under that guard instead of hoping.
**Depends on**: Nothing new — builds on shipped v0.6 (`792b45c`, the close squash on `main`). The
`v0.6` tag exists, annotated and pushed, and peels to `792b45c` (found at discuss-phase), so every
"byte-identical to `v0.6`" rule in REQUIREMENTS.md names a real baseline. Later phases make only
additive edits to the shared modules `model.py`, `pool.py` and `app.py`, each proved by
`make gear.unchanged`; `calc.py`, `params.py`, `tests/regression/`, `.github/workflows/ci.yml` and
`requirements.txt` are not edited for the rest of the milestone (D-11).
**Requirements**: REQ-scope-decision-logged, REQ-gear-unchanged-proof, REQ-shaft-routes-separate
**Success Criteria** (what must be TRUE):

  1. The scope is a logged decision before any shaft code lands. A new `L46` in
     `docs/architecture/decision_log.md` widens the product from "involute spur gear generator"
     to a gear and spline generator, amends L02 to one parameter model per part type and L05 to a
     second frozen link contract (shaft field names and defaults), says what it supersedes and
     what it leaves alone, and its commit precedes the first commit that adds a shaft module.
  2. "Same gear, same links" is one command the human can run at any phase close. It fails when
     `tests/regression/` or `.github/workflows/ci.yml` differ from the baseline, or when the gear
     `/api/schema` response is not byte-equal to the baseline's; it reads green on the tree as it
     stands and is seen red on a deliberate edit of each watched item, the reds recorded in
     `bench/RESULTS.md`. Any gear-file edit this phase makes (see the seam work below) leaves it
     green.
  3. The shaft cannot leak into the gear. Import-linter contracts declare that the shaft maths
     imports no `cadquery`, no logger and no gear maths, and that the shaft solid is reachable
     only through `model`; a route-table pin states that every `/api/` route beyond the v0.6 set
     lives under `/api/shaft/` while the gear routes' query keys and responses stay as they were.
     Each contract and the pin is seen red once against a deliberate violation.
  4. The gate delta is recorded: the `make verify` time of this phase against v0.6's close on the
     same host, in `bench/RESULTS.md` (REQ-gate-cost-recorded, closed at Phase 34).

**Seam work the research puts here (input, not requirement)**: a part-type seam (`parts.py`),
type widening in `pool`/`records`/`model`, and `_serve_model` extracted from `app.py`'s `model()`
as a pure-move commit — the move is a stop-and-ask for the planner, and each such edit is
proved by criterion 2, never by reading the diff. ASSUMPTION to check in the plan: import-linter
errors on a contract that names a module that does not exist, so either this phase creates the
empty shaft module files or the contracts ride with the commit that creates them; if that
changes Phase 31's file layout, ask before choosing.
**Boundaries**: no shaft maths, no `ShaftParams`, no route that answers a shaft; no new
`GearParams` field; `make fixture.regen` and `make golden.regen` are not run in v0.7;
`requirements.txt` byte-identical. **Phase close**: `make verify` result line recorded; the
Phase 30 check green.
**Research flag**: No — standard patterns (research Phases 1 and 4).
**Plans**: 5/5 plans complete, run one at a time (one shared working tree; deliberate red edits)

Plans:
**Wave 1**
- [x] 30-01-PLAN.md — `make gear.unchanged`: the tracer check against the `v0.6` tag, wired into both gates, tested on scratch repos, seen red per watched item, priced

**Wave 2** *(blocked on Wave 1 completion)*
- [x] 30-02-PLAN.md — L46 (gear and spline generator; amends L02/L05), AGENTS.md brief, roadmap D-11 amendment, one docs commit before any shaft module

**Wave 3** *(blocked on Wave 2 completion)*
- [x] 30-03-PLAN.md — the wall: five docstring-only shaft modules, `parts.py`, five import contracts, belts, existence guard, route-table pin, each seen red

**Wave 4** *(blocked on Wave 3 completion)*
- [x] 30-04-PLAN.md — the seam: `Part` at the shared entry points, `_serve_model` pure move (own commit), part-neutral 503 text with its pin

**Wave 5** *(blocked on Wave 4 completion)*
- [x] 30-05-PLAN.md — phase-close checks (D-20 order, byte-identical paths, no shaft behaviour) and the `make verify` gate delta

### Phase 31: Shaft Maths, Parameters and Designation

**Goal**: A user can ask the pure maths for a DIN 5480 external shaft from reference diameter,
module, tooth count and tolerance field and get honest numbers: the profile shift the standard
derives, tip and root diameters, nominal tooth thickness, measurement over pins at nominal
thickness — each proved against an independent oracle and against rows of the copy, with the form
diameter and odd-z M_Re `null` until proven — and a designation that prints and parses back to
the same shaft. No solid, no route, no page yet.
**Depends on**: Phase 30 (the contracts are in force before the maths module exists). **Needs the
human before it can close**: the DIN 5480 (2006 series) copy's formulas confirmed by clause, the
`h_fP` convention (hobbing 0.60, vendors differ), and **anchor rows from the copy** — at least two
for the basic dimensions, one that reproduces (or fails to reproduce) the form-diameter
construction, one with an odd tooth count if odd-z M_Re is to print a number, and ideally the
range-edge W30x2x14. Anchor values the human approves by name may be committed with their part,
clause and table; nothing else from the copy is. Without the rows the plan builds the maths and
the oracle, then stops at a checkpoint: no number ships unproved (L08).
**Requirements**: REQ-shaft-params, REQ-profile-shift-from-dB, REQ-shaft-basic-dims,
REQ-form-diameter-honest, REQ-mre-nominal, REQ-designation-codec
**Success Criteria** (what must be TRUE):

  1. The shaft's inputs are one frozen contract and the profile shift comes from d_B.
     `ShaftParams` (d_B, module, tooth count, tolerance field, splined length, end chamfer,
     shank diameter and length) is validated once at its boundary, and a pinned test fails if
     any field name or default changes, tolerance fields included (L46's second frozen link
     contract). The shift is x·m = (d_B − z·m)/2 − 0.55·m (ASSUMPTION until checked by clause
     against the copy, the check recorded in the plan summary); W30x2x14 (x = −0.05, computed as
     −0.05000000000000004) is accepted by an epsilon, and a combination outside the standard's
     shaft range is refused with an error naming the range (the same refusal the API serves as a
     `422` in Phase 33). `GearParams` and `calc.py` are untouched.
  2. The user sees d_B, tip diameter, root diameter and nominal tooth thickness, and each agrees
     with an independent stdlib oracle that shares no code with the shaft maths (seen red once
     against a mutated formula) and with at least two anchor rows from the copy.
  3. A number that cannot be proved is absent, with a reason. The form diameter d_Ff prints
     `null` with a sentence naming why, unless the oracle reproduces the copy's construction on an
     anchor row, in which case it prints the number. M_Re and the pin diameter D_Re at nominal
     thickness agree with the oracle for even z, and pin contact is checked to lie between the
     form and tip diameters or the value is `null` with a warning; odd z stays `null` until an
     odd-z anchor row confirms it.
  4. The designation round-trips. `W <d_B>x<m>x<z>x<fit>` is printed for every shaft and parsed
     back to the same parameters, with `.` and `,` decimals; an unparseable string is refused
     naming the bad token. A tolerance token is checked for shape only — whether the fit exists
     in the tables cannot be known until Phase 34.
  5. The gate delta is recorded: this phase's `make verify` time against Phase 30's on the same
     host, in `bench/RESULTS.md`; the Phase 30 check is green.

**Boundaries**: no `cadquery` import and no logger in the shaft maths (the Phase 30 contracts);
shaft maths copied from, never imported out of, `calc.py` (`_involute_angle` precedent), so gear
and shaft numbers stay uncoupled; no scipy; no table value in the repo; every guard test seen
red once, the red recorded. **Phase close**: `make verify` result line recorded and
`git diff --exit-code v0.6 -- tests/regression/ .github/workflows/ci.yml` empty.
**Research flag**: Yes — needs the human's copy (research Phase 2): formula confirmation by
clause, `h_fP`, anchor rows incl. one odd z, the d_Ff construction.
**Plans**: 6/6 plans executed, run one at a time (one shared working tree; deliberate red edits); 31-05 stops at the
DIN 5480 checkpoint and 31-06 cannot start until the human answers

Plans:
**Wave 1**
- [x] 31-01-PLAN.md — tracer: the default shaft through `ShaftParams` -> `derive_shaft` -> `din5480` to its basic dimensions; the frozen contract, the range refusal and the epsilon cases pinned and seen red

**Wave 2** *(blocked on Wave 1 completion)*
- [x] 31-02-PLAN.md — the independent stdlib oracle; shift, tip, root and thickness on a 192-case grid and the two vendor sets; each comparison seen red against a mutated formula

**Wave 3** *(blocked on Wave 2 completion)*
- [x] 31-03-PLAN.md — the theoretical pin, M_Re at nominal for even and odd z, d_Ff null with its reason, the pin-contact guard over an explicit pin; oracle-proved and seen red

**Wave 4** *(blocked on Wave 3 completion)*
- [x] 31-04-PLAN.md — the designation codec (print, parse, round trip, refusals naming the token); `parts.py` docstring and the WR-03 debt item re-targeted to Phase 32

**Wave 5** *(blocked on Wave 4 completion)*
- [x] 31-05-PLAN.md — the gate green and the prediction table, then `checkpoint:human-action`: the human confirms each formula by clause and approves the anchor rows

**Wave 6** *(blocked on Wave 5 completion)*
- [x] 31-06-PLAN.md — anchor rows as cited tests, D-09 for any contradiction, the conditional d_Ff / odd-z outcomes, the gate delta, the close checks and the closing `Lxx`

### Phase 32: The Shaft Solid

**Goal**: A shaft built from Phase 31's maths is a valid solid — splined section, plain shank and
end chamfer — that exports to STL and STEP, whose volume matches a closed form, and whose
heaviest allowed build is measured against the memory ceiling and the timeout, with the field
bounds set from that sweep. The user reaches the downloads through Phase 33's interfaces.
**Depends on**: Phase 31 (parameters and outline maths); Phase 30 (the kernel dispatches by part
type inside `model._build`, under the one lock, through the same pool and caches). The solid
carries the **nominal** tooth thickness until Phase 34 switches it to the effective
maximum-material thickness. Its edits to `model._build` and `pool._warm` are additive and proved
by `make gear.unchanged`; when `model.py` first imports `shaft_model` statically, the contract
"The kernel doorways are model and shaft_model" gains
`ignore_imports = ["spur.model -> spur.shaft_model"]` in that same commit (30-RESEARCH Pitfall 4:
it errors if added earlier).
**Requirements**: REQ-shaft-solid, REQ-shaft-build-measured
**Success Criteria** (what must be TRUE):

  1. A shaft built through `model` is a valid solid and exports a valid STL and STEP of the
     splined section, the plain shank and the end chamfer; its volume matches a closed form
     derived without the kernel, within a tolerance recorded beside the test.
  2. The joins and the chamfer are honest. A shank whose diameter equals the tip diameter still
     builds a valid solid (the case research found invalid through `Workplane.union` + `.clean()`);
     the applied end chamfer is read back from the solid, not assumed; a chamfer past the tooth
     height is refused naming the field or capped and warned, never an invalid solid with a wrong
     volume and no error (research: `Solid.chamfer` does that silently).
  3. The heaviest allowed shaft is measured: build time, worker memory and STL size are recorded
     in `bench/RESULTS.md` within L17's memory ceiling and L37's timeout, the field bounds are set
     from that sweep (swept, not derived), and the bounds are pinned by a test.
  4. The gate delta is recorded: this phase's `make verify` time against Phase 31's on the same
     host, in `bench/RESULTS.md`; the Phase 30 check is green.

**Boundaries**: `cadquery` objects do not escape `model.py`; the shank joins by `Shape.fuse`, the
end chamfer by a revolved-cone `intersect` (the research spike's findings, to be re-proved at real
DIN proportions); the existing gear caches and pool are reused, not forked. **Phase close**:
`make verify` result line recorded and `git diff --exit-code v0.6 -- tests/regression/
.github/workflows/ci.yml` empty.
**Research flag**: Yes — a kernel spike at real DIN proportions first (research Phase 3);
build times so far were measured on placeholder proportions only.
**Plans**: TBD

### Phase 33: Interfaces and Parity

**Goal**: The same shaft — preview, numbers, designation and STL/STEP — comes from the web page,
the API and the CLI, one set of numbers for all three, the designation can be given in place of
the fields, and WR-02 is fixed on the same edit of the part switch that would otherwise trip it.
**Depends on**: Phase 30 (route prefix and contracts), Phase 31 (maths, parameters, designation),
Phase 32 (the solid). Does not depend on the tables: table-dependent numbers arrive in Phase 34
through the same schema-carried row list, and no number printed here is a table value. Its routes
are additions to `app.py` under `/api/shaft/`, calling `_serve_model` as its second caller, proved
by `make gear.unchanged` and Phase 30's route-table pin.
**Requirements**: REQ-shaft-api, REQ-shaft-cli, REQ-shaft-web, REQ-designation-input,
REQ-shaft-parity, REQ-wr02-fixed
**Success Criteria** (what must be TRUE):

  1. The API and the CLI serve the shaft. `/api/shaft/schema`, `/api/shaft/info`,
     `/api/shaft/model.stl` and `/api/shaft/model.step` answer with the gear routes' admission,
     cache and error contract (an invalid shaft is a `422` naming the field); `spur shaft ...`
     builds the same part and prints the same numbers for the same parameters. Both accept a
     designation in place of the fields; a designation together with an explicit field it
     contradicts is a `422` naming the fields (L03); an unparseable designation names the bad token.
     The gear routes, their query keys and the gear `/api/schema` response are unchanged.
  2. The web page serves the shaft. A part switch changes between gear and shaft; the shaft shows
     its preview, its numbers (from a schema-carried row list, not a second row table in
     `app.js`) and its designation, and downloads STL and STEP; a shaft link (`part=shaft&...`)
     round-trips; a gear link carries no `part` key; any other `part` value is refused visibly; a
     browser test in `make verify` proves each.
  3. Web, API and CLI agree. One parametrised test, over a fixed set of shafts, proves they report
     the same value for every shaft number and the same download name, and is seen red once on a
     deliberately perturbed number.
  4. WR-02 is fixed where the part switch edits `refuse()`/`gearQuery()`. A link token the number
     box blanks but the API accepts no longer builds a non-default part under a blank box — the
     page and the part agree — proved in the browser over every number field and `mate_teeth`
     (the debt item says the token list is wider than its table); the debt item
     `2026-10-21-an-accepted-link-token-builds-under-a-blank-box.md` is retired in the fixing
     commit (status, sha, `git mv` into `resolved/`, INDEX row).
  5. The gate delta is recorded: this phase's `make verify` time against Phase 32's on the same
     host, in `bench/RESULTS.md`, browser test included; the Phase 30 check is green and the 44
     fixture links still send the requests `tests/regression/golden_requests.json` pins.

**Decisions the human takes at this phase's discuss-phase**: WR-02's shape (the debt item says the
wording and placement of any notice have more than one honest shape — a discuss-phase choice, not
a gap closure), logged as a new `Lxx` if it amends L44's "The server decides"; where the part
switch sits (outside `#params`, per research).
**Boundaries**: the shaft's rows live in a schema-carried `dims` key — two `app.js` pins forbid a
second row table and quoted field names (`tests/test_api.py:176-180`, `:314-340`); the gear
`/api/schema` stays byte-equal; no `part` key on any gear link; the CLI never imports
`app`/`fastapi`/`starlette` (L04); no new dependency. **Phase close**: `make verify` result line
recorded and `git diff --exit-code v0.6 -- tests/regression/ .github/workflows/ci.yml` empty.
**Research flag**: No — standard patterns (research Phase 4).
**Plans**: TBD
**UI hint**: yes

### Phase 34: Fit Tables and Tolerance Window

**Goal**: With the human's DIN 5480 (2006 series) values transcribed into a private, gitignored
file, the user sees the tooth-thickness windows and the measurement-over-pins limits at the
chosen fit, and the solid carries the effective maximum-material thickness; without the file, or
for a size the tables do not list, the part still builds from the formulas and every
table-dependent number is `null` with a warning that says why. The milestone releases as one
unit when this phase closes.
**Depends on**: Phase 33 (the new rows ride its schema-carried list and its parity test), Phase 31
(the maths the tables extend). **Blocked until the human supplies the DIN 5480 copy's local
path** — the transcription cannot start without it, and nothing here may be guessed from memory or
from a vendor page (L08). If the path is not available when Phase 33 closes, stop and ask before
anything else is planned.
**Requirements**: REQ-tables-private-file, REQ-tables-transcribed-twice, REQ-fit-tolerance-window,
REQ-mre-limits, REQ-solid-max-material, REQ-off-table-builds, REQ-gate-cost-recorded
**Success Criteria** (what must be TRUE):

  1. The tables are private and their absence is honest. Transcribed values load from a
     gitignored file whose path is set by config or environment; with no such file every
     table-dependent number is `null` with a warning naming the missing file, and the part still
     builds. The repository holds no transcribed value beyond the anchors the human approved by
     name.
  2. The transcription is checked, not trusted. The file is produced by two independent reads
     diffed to zero; every row carries its part, clause and table; a loader check enforces
     structural invariants (`T_G = T_act + T_eff`, µm-versus-mm range, no Unicode minus) and is
     seen red once against a deliberately broken row.
  3. For a tabulated size and fit the user sees the effective and actual tooth-thickness windows
     and M_Re max and min with D_Re from the copy, each proved against the oracle on the anchor
     rows; a fit outside the tables is a warning and `null`; a d_B/m/z absent from the size tables
     builds from the formulas with every table-dependent number `null` and warned. The new
     numbers reach web, API and CLI through Phase 33's row list, and the parity test stays green
     and covers them.
  4. The solid follows the tables. With them loaded it carries the effective maximum-material
     tooth thickness (s + es), read back from the solid; without them it carries the nominal
     thickness and a warning says so.
  5. The gate cost is recorded and read (REQ-gate-cost-recorded): each phase's `make verify` time
     is on record against its predecessor's, and the milestone close reading is inside L43's 300 s
     bar or the human decides — a reading above it is surfaced, not trimmed silently. The Phase 30
     check is green at the milestone close.

**Decisions the human takes at this phase's discuss-phase**: the config key or environment
variable that names the private file; the method of the two independent reads; which anchor
values the human approves by name for the public repo.
**Boundaries**: no licensed value committed; no interpolation, no snapping to the nearest size
(L08); no ISO-style `f8` aliases for DIN fit letters (one spelling per field, the frozen link
contract); `make fixture.regen` still not run. **Phase close**: `make verify` result line
recorded, `git diff --exit-code v0.6 -- tests/regression/ .github/workflows/ci.yml` empty, and
`git ls-files` holds no table file.
**Research flag**: Yes — transcription risk (research Phase 5); the 2006 edition's tolerance
system is in Part 1 and its size tables in Part 2, so the plan names which part each table
comes from.
**Plans**: TBD

## Process Notes (carried forward)

- Phases run on `gsd/phase-NN-*` branches cut from `origin/main` and land only through
  `make pr.land PR=N` (L22/L25); `.planning/` rides the same PR as the code, never a
  separate planning-only commit. The milestone close is itself a PR.
- `make verify` (ruff, mypy `--strict`, import-linter, unfinished-work scan, pytest on 8
  xdist workers under `fail_under = 96`) is the gate for every phase, no exceptions (L13,
  L34). Since Phase 17 (L36) it runs as the pre-push hook; the pre-commit hook runs
  `make verify.fast` (~11 s warm, under `gsd_run query commit`'s 30 s timeout — proved by SDK
  commit `5a3332f`). The bar is 300 s on the 18-CPU M5 Max, set by the human in Phase 25
  from two non-decisive readings (195.23 s, 179.21 s) under a rule committed first (L43 amends
  L34). A killed SDK commit still leaves the hook running as
  an orphan: wait for it, then one plain `git commit`, never a blind retry (D-07).
- Every phase that adds a decision logs it as a new `Lxx` in
  `docs/architecture/decision_log.md`, append-only (the next free id is `L46`).
- New parameters default to off (L05); the pre-v0.2 regression fixture is the standing
  proof, re-run by every later phase. It changes only through `make fixture.regen`, in its
  own commit, under its own `Lxx` that says what moved and why (L26 D-03) — a feature commit
  never touches it. The hob-root default flip, if it ever comes, is that one commit (L38).
- A debt item is retired only in the commit that fixes it: `Status: resolved`, the sha,
  `git mv` into `resolved/`, the INDEX row moved (CLAUDE.md).

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1–6 | v0.1 | 21/21 | Complete | 2026-09-25 |
| 7–12 | v0.2 | 34/34 | Complete | 2026-10-01 |
| 13–16 | v0.3 | 20/20 | Complete | 2026-10-05 |
| 17–20 | v0.4 | 22/22 (Phase 20 skipped under L38) | Complete | 2026-10-09 |
| 21–25 | v0.5 | 23/23 | Complete | 2026-10-15 |
| 26–29 | v0.6 | 22/22 (Phase 29 closed, trigger not fired) | Complete | 2026-10-23 |
| 30. Scope, Seam and Gear-Safety Guard | v0.7 | 5/5 | Complete    | 2026-10-23 |
| 31. Shaft Maths, Parameters and Designation | v0.7 | 6/6 | In Progress (needs anchor rows from the DIN 5480 copy) | - |
| 32. The Shaft Solid | v0.7 | 0/? | Not started | - |
| 33. Interfaces and Parity | v0.7 | 0/? | Not started | - |
| 34. Fit Tables and Tolerance Window | v0.7 | 0/? | Not started (blocked until the copy's local path is supplied) | - |
