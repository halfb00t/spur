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
- 🚧 **v0.5 Honest Form** — Phases 21–25 (in progress; Phase 24 is discretionary and may be
  skipped by the human's decision)

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)
- Numbering continues across milestones — v0.5 starts at Phase 21 (Phase 20 keeps its number
  although it was skipped); the next milestone starts at Phase 26, after Phase 25 (Phase 24
  keeps its number even if it is skipped).

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

### 🚧 v0.5 Honest Form (In Progress)

**Milestone Goal:** The web form tells the user up front what each field does and a browser
proves it — the deferred UI ideas taken in dependency order behind a real viewer test, the
gate bar re-set from a measurement under a rule written first, and the three small ledger
items closed — with no new `GearParams` field and the 44-record pre-v0.2 fixture
byte-identical to the `v0.4` tag.

- [x] **Phase 21: Browser Test of the Viewer** - A real headless browser exercises the shipped (completed 2026-10-10)
      `app.js` inside `make verify` and CI: the form builds from `/api/schema`, an invalid
      field is marked, a warning renders, the first STL is drawn; the Linux path is proved on
      a real runner, the gate cost is measured A/B, and the request each of the 44 fixture
      records makes is pinned before any form change lands
- [ ] **Phase 22: Download Name Carries the Root** - A hob-root part downloads as
      `..._trochoid`; every radial part, and every request whose trochoid is ignored, keeps
      today's name byte for byte, and the `Lxx` lists every consumer of the old names first
- [ ] **Phase 23: Conditional Form Fields** - A field whose value would be ignored (or
      refused) says so in the form before it is typed: an `enabled_when` relation on the
      model, proved against `calc`, rendered dimmed-and-editable by generic `app.js` code, the
      pins tightened and not removed
- [ ] **Phase 24: Bore-Shape Selector** - Discretionary: a bore shape is picked, not inferred
      from a warning: a schema-carried select derived from the flat fields on load, writing
      only the flat fields; skippable without breaking anything else
- [ ] **Phase 25: Gate Bar Re-Set, Venv Probe, Ledger Close** - The gate is measured once on
      the shipped HEAD under a rule written first, the human sets the bar, L34 is amended
      once; `PIP_CONSTRAINT` is probed in a scratch checkout; the Pi 5 claim is softened and
      the reverify recipe written

## Phase Details

### Phase 21: Browser Test of the Viewer

**Goal**: A real headless browser loads the shipped page inside `make verify` and CI and
proves what the Python tests structurally cannot see — the form builds from `/api/schema`,
an invalid field is marked, a warning renders, the first STL is drawn — at a measured gate
price, failing loudly when it cannot run, with the request each of the 44 fixture records
makes pinned before any later phase changes the form.
**Depends on**: Nothing new — builds on the shipped v0.1–v0.4 pipeline (Phases 1–19; Phase 20
was skipped). Every commit of the milestone runs under L36's split hook. The order inside the
phase is fixed: the spike first (WebGL, the Linux runner, strict typing), then the server
fixture and the scenarios, then the gate admission in one commit, then the cost and the
`Lxx`. Both UI ideas (Phases 23 and 24) named "a browser test exists" as their trigger, and
the dim, derive and write-through behaviour of Phases 23–24 is visible to nothing else.
**Requirements**: REQ-browser-server-fixture, REQ-browser-form-from-schema,
REQ-browser-first-build-drawn, REQ-browser-invalid-field-marked, REQ-browser-warning-rendered,
REQ-browser-link-round-trip, REQ-browser-golden-request-sets, REQ-browser-fails-closed,
REQ-browser-in-the-gate, REQ-browser-stack-pinned
**Success Criteria** (what must be TRUE):

  1. A fresh load builds the page the schema describes and draws the first part. Against a
     real `uvicorn`, a `webgl2` context is asserted before anything else (`app.js:229` builds
     the renderer at module top level, so no WebGL means no form); the rendered form carries
     exactly the groups and fields of `/api/schema`, in its order, every count read from the
     schema at test time and none hard-coded, with the CSS custom properties the renderer
     reads non-empty; `#dl-stl`'s href is set only after `showModel` returns; the canvas is
     non-blank against a blank control at a bar recorded with the reading that set it
     (starting points, not bars: 38,908 B against 3,393 B PNG, 11,478 distinct pixels, on
     SwiftShader); and `canvas.dataset.triangles` equals the triangle count of the STL the
     page loaded — the one production line this milestone adds to `app.js`, named in the
     `Lxx`.
  2. The interactions, the links and the baselines are proved. An out-of-range value marks its
     field through the 422 `detail[].ctx.fields` path and the rendered message names the
     field; a warning-producing link renders exactly the `warnings` text `/api/info` returns
     for the same query (equality, not containment); every field set in the hash reaches the
     form and the query `app.js` sends equals the hash on fresh load, Reset and `hashchange`,
     with the debounce waited out on content and never on an empty status or a bare href; for
     each of the 44 fixture records' parameter sets the query string the form sends is pinned
     and committed before any form change in Phases 23–24; `#root_shape=bogus` (which becomes
     the default through the blank select where the API returns 422) is pinned as it behaves
     today and filed as debt, not fixed. Each assertion was seen red once against a deliberate
     break, recorded.
  3. The harness cannot lie. The test runs against a real `uvicorn` subprocess on a socket the
     fixture pre-binds on `127.0.0.1` and passes down with `--fd`, started with
     `start_new_session=True` and torn down by killing the process group; a check proves no
     `BuildPool` child survives teardown (children outlived a plain `SIGKILL` by 6 s,
     measured); the file passes repeatedly at `-n 8` with the count recorded. A missing
     headless shell fails the test with a message naming
     `playwright install --only-shell chromium` — seen red with the shell removed — with no
     `importorskip`, no skip marker and no environment opt-out, a pin failing if one appears.
     `playwright` is pinned exactly in the `[dev]` extra, `pytest-playwright` is absent, the
     default Chrome Headless Shell is used and never `channel="chromium"`, and
     `mypy --strict` passes with typed wrappers around `page.evaluate`.
  4. The gate admits the browser at a measured price. `tests/test_browser.py` runs inside
     `make verify` and CI's `test (3.12)` job, the browser installed by a Makefile stamp with
     `PLAYWRIGHT_BROWSERS_PATH` isolated or `--no-remove`, so the `chromium-1228` another
     project holds on this host survives (checked); it is excluded from `make verify.fast`
     and `make test-image` by name in the same commit that adds the file, `tests/test_hooks.py`'s
     `HEAVY_TEST_FILES` pin extended and seen red when the `--ignore` is missing, and
     `make verify.fast` still reads under L36's 30 s; `bench/RESULTS.md` records the file's
     isolated cost (3.21 s serial and 3.80 s at `-n 2` were the research figures) and its A/B
     cost under the full gate (with and without the file, N, host, load and `HEAD` beside each)
     next to L34's 66 s bar — this reading admits the file and sets no bar (Phase 25 does);
     if it contradicts the research figure by an order of magnitude the admission goes back to
     the human before the phase closes; one `Lxx` records the admission, amends L13 and L36
     and restates L11 unchanged (the driver ships in the wheel and runs at test time only; the
     31-pin runtime closure, the Dockerfile and `refresh-requirements.sh` do not move); the
     browser-test idea is retired in the commit that closes it.
  5. The Linux path is proved on a real runner. A real `ubuntu-latest` run of `test (3.12)`
     installs the headless shell, runs `tests/test_browser.py` green with `webgl2` asserted,
     and its run id and wall time are recorded in `bench/RESULTS.md` before the phase closes —
     not predicted from the `ubuntu:24.04` container the research measured.

**Decisions the human takes at this phase's discuss-phase** (SUMMARY "Decisions Reserved for
the Human", numbers kept; REQUIREMENTS.md records the kickoff choices, so discuss-phase
confirms and records them, and reopens one only if a measurement contradicts it):
  - 1 — whether a headless browser belongs in `make verify` (O1 inside `test`, excluded from
    `test.fast`; O2; O3, which breaks `test_hooks.py:92`; O4, which needs `required-jobs.txt`
    and the GitHub ruleset). Taken at kickoff as O1 (REQ-browser-in-the-gate); the pricing
    goes in front of the human and the one `Lxx` records it.
  - 2 — a missing browser: hard failure, or hard failure plus a printed, CI-refused opt-out.
    Taken at kickoff as a hard failure with no opt-out (REQ-browser-fails-closed).
  - 3 — the one production line `canvas.dataset.triangles`. Written into
    REQ-browser-first-build-drawn; discuss-phase confirms it against the init-script draw
    count the architecture file proposed.
  - 4 — whether to adopt `pytest-playwright`. Taken as no (REQ-browser-stack-pinned).

**Boundaries**: the only production change is the `canvas.dataset.triangles` line; no
`GearParams` field, no `calc`, `model`, `pool`, `app` or `cli` edit;
`git diff --exit-code tests/regression/pre_v0_2.json` is clean after every task. A `.gitignore`
entry covers the browser artifacts. Every failed gate log during this phase is kept and
classified against the four recorded occurrences of the resource-tracker flake (`must` debt),
and no `filterwarnings` entry is added. The pin in
`tests/test_api.py::test_the_shareable_link_round_trips_every_field_through_generic_code` and
the DIMS-key pin are not touched here. The CI browser cache is out of scope (Playwright's own
docs advise against it), and `xdist_group` is a no-op under the current `--dist load` — a
plan-phase call, flagged, because changing suite scheduling is a gate-time change.
**Research flag**: Yes — a spike as the first task, not a research phase. The headless shell on
a real `ubuntu-latest` runner (`--with-deps` through `sudo`, the apt libraries), strict mypy on
the Playwright-typed file, and the gate cost under eight-worker load on a 4-vCPU runner (the
research measured an `ubuntu:24.04` container and a 3.2–3.8 s isolated cost; the
architecture file's 10–25 s is an assumption). Also unverified and settled by the spike: canvas
readback without `preserveDrawingBuffer`, the `expect` default timeout, and coverage on a
`SIGKILL`ed child.
**Plans**: 8/8 plans complete, in 8 waves (each wave depends on the one before: the roadmap fixes the order, and the
scenario module, `tests/browser_session.py` and `bench/RESULTS.md` are touched by nearly every plan, so there is
no honest parallelism here)

- [x] 21-01-PLAN.md — The spike's tracer: the legitimacy check, then the exact `playwright` pin, the `.venv` stamp,
  the `canvas.dataset.triangles` line, the server fixture and the first three steps (webgl2, first build drawn,
  href after showModel) under the staging name `tests/browser_scenarios.py`; each seen red once *(wave 1)*
- [x] 21-02-PLAN.md — The Linux runner: a throwaway `spike/21-linux-runner` draft PR the human pushes; the canvas
  bar and the build wait set from the macOS and `ubuntu-latest` readings *(wave 2)*
- [x] 21-03-PLAN.md — Form from schema, both 422 marking paths and the rendered warnings, every expectation read
  from the server *(wave 3)*
- [x] 21-04-PLAN.md — The link round trip on fresh load, Reset and `hashchange`; `#root_shape=bogus` pinned as
  today and filed as `must` debt *(wave 4)*
- [x] 21-05-PLAN.md — The golden request pin: the query each of the 44 fixture links sends, captured by the real
  page through `make golden.regen` and asserted *(wave 5)*
- [x] 21-06-PLAN.md — The fail-closed and stack pins, then the gate admission in one commit (rename to
  `tests/test_browser.py`, every exclusion, `--with-deps` in CI), `make verify.fast` read under 30 s *(wave 6)*
- [x] 21-07-PLAN.md — The price: isolated cost and a six-run interleaved A/B; the human accepts it or reopens the
  placement *(wave 7)*
- [x] 21-08-PLAN.md — SC5 on a real `ubuntu-latest` run of the phase branch (the human pushes), then L39 and the
  idea retired in the closing commit *(wave 8)*
**UI hint**: yes

### Phase 22: Download Name Carries the Root

**Goal**: The name of a downloaded file says which root the part has: a part built with the
hob root ends `_trochoid`, and every radial part, and every request whose trochoid is
silently ignored, keeps today's name byte for byte.
**Depends on**: Phase 21 (soft — it reuses Phase 21's `expect_download` harness while it is
fresh; nothing else blocks it, and it can move later in the milestone at no cost).
**Requirements**: REQ-slug-carries-effective-root, REQ-slug-consumers-read-first
**Success Criteria** (what must be TRUE):

  1. The suffix follows the part, not the request. At 23 teeth `root_shape=trochoid` downloads
     as `..._trochoid` (STL and STEP, `Content-Disposition` read in `tests/test_api.py` and
     the browser's `expect_download` on the same link); at 40 teeth, where `calc.root_mode`
     ignores the request, and for the default radial gear, the name equals today's
     byte for byte. The radial-default `tests/test_api.py` pin is unchanged; the trochoid pin
     flips deliberately in the same commit.
  2. `slug()` stays total. It is called inside failure-path log records, so a test calls it on
     a request `root_mode` refuses and on one it ignores and gets a name both times, and the
     `build.failed` record for such a request still carries its `slug`.
  3. The record is written before the names move. The `Lxx` lists every consumer of the old
     names — `Content-Disposition` (`app.py`), the record's `slug` (`records.py`),
     `docs/http-api.md`, the two `test_api.py` pins — and states that no cache is keyed by slug
     (the export cache key is `(params, fmt, quality, encoding)`); `docs/http-api.md` says the
     new truth; `git diff --exit-code tests/regression/pre_v0_2.json` is clean (the slug is
     not in the fixture); the idea file is retired in the same commit (status, sha, `git mv`,
     INDEX row).

**Decisions the human takes at this phase's discuss-phase**:
  - 12 — the suffix follows the requested root or the effective root. Taken at kickoff as
    effective (REQ-slug-carries-effective-root); discuss-phase confirms it with its cost in
    front of it: `slug()` now depends on a solver (about 10–30 µs, measured in Phase 19) and
    must stay total.

**Boundaries**: a suffix, not a prefix; nothing for a non-default root other than the trochoid
exists to name, so no other root value is invented here.
**Research flag**: No — standard patterns; the one small decision is above.
**Plans**: TBD

### Phase 23: Conditional Form Fields

**Goal**: The form says a field is inert before it is typed: a relation lives on the model as
schema metadata, is proved against `calc` row by row, and is rendered by generic `app.js`
code as dimmed-and-editable — and no link sends a different field or a different value than
it does today.
**Depends on**: Phase 21 — it is this phase's regression net (the 44 golden request sets and
the browser's view of the dim state). Not Phase 22. This phase defines the relation evaluator
and the condition vocabulary that Phase 24 reuses; building the two separately would state
"hex wins" twice.
**Requirements**: REQ-enabled-when-metadata, REQ-relations-calc-backed, REQ-dim-and-editable,
REQ-form-walk-proves-relations
**Success Criteria** (what must be TRUE):

  1. `/api/schema` carries every declared relation as the model wrote it. `_f()` accepts an
     `enabled_when` relation in `json_schema_extra` and `model_json_schema()` emits it
     unchanged (nested dicts and lists verbatim, key-sorted at every level, so a relation never
     depends on key order); the two bare-`Field` `Literal` fields carry it the same way; the
     grammar is project-defined and AND-only as fixed at discuss-phase; a test proves the key
     collides with no JSON Schema vocabulary word; `GearParams` gained no field and `app.js`
     carries no `GearParams` field name outside `DIMS`.
  2. Every declared relation is one `calc` backs, and a test goes red when they drift. The set:
     `bore_d`/`bore_flat` under `bore_hex > 0` and each cutout group's dimensions while its
     count is 0 (inert, warned), and `keyway_width`/`keyway_depth` under `bore_hex > 0`
     (refused, a 422 with its own wording, never gated on each other — each alone is 422). The
     parity test proves per row that with the relation false, changing the dependent field
     changes nothing in `derive()` except `warnings` (or yields the 422 for the refused
     class), and was seen red against a deliberately wrong relation. The `recess_*`-under-`none`
     and `bore_flat`-at-`bore_d=0` relations are not declared; no `calc` warning fires on a
     fixture record; `git diff --exit-code tests/regression/pre_v0_2.json` is clean after
     every task. A row that fails the parity proof is dropped with its reason recorded, never
     declared on a guess.
  3. In a real browser an inert field is dimmed and is still a field. `.field.inactive` with a
     reason built from the gate field's `title`; the field stays editable, keeps its value and
     is still sent, so the query the form sends equals the Phase 21 golden request set for
     every one of the 44 records, and `#spoke_count=0&hub_d=40` loads with `hub_d` editable
     and sent; the state is re-evaluated on `input`, `readHash`, Reset and `hashchange`; the
     browser test asserts the dim state of each declared relation under the golden request
     sets.
  4. The pins are tightened, not removed. The model-driven field walk extends to every relation
     (schema to form, generic code only); `tests/test_api.py`'s `app.js` pins are tightened
     under one `Lxx` that supersedes 08 D-09 and keeps L02, and none is deleted or
     allow-listed to get green; the idea file for the two unbacked relations and the debt file
     for the hex warning that fires on default `bore_d`/`bore_flat` (`?bore_hex=6` warns every
     time — a `calc` change, never filtered in `app.js`) are filed with their INDEX rows; the
     conditional-fields idea is retired in the commit that closes it.

**Decisions the human takes at this phase's discuss-phase**:
  - 5 — dim-and-editable, or `disabled` limited to default values. Taken at kickoff as
    dim-and-editable (REQ-dim-and-editable; a disabled field cannot be cleared, so
    `#spoke_count=0&hub_d=40` would load stuck).
  - 6 — the relation grammar's scope. Open: the four research files propose four shapes
    (nested `all/any`; a JSON-Schema-flavoured fragment; a list of `{field, op, value}`;
    `{field, gt|eq}` plus `all`); all say AND-only suffices. It is also the vocabulary Phase 24's
    selector is written in.
  - 7 — whether the keyway gets a relation and a separate "refused" style. Taken in part: the
    keyway pair is declared as the refused class (REQ-relations-calc-backed) and distinct
    styling is deferred (REQUIREMENTS.md "Form follow-ups"); open is the reason wording a
    refused field shows.
  - 8 — unbacked relations stay undimmed or get a warning first. Taken at kickoff: dropped,
    because the warning would rewrite 14 fixture records; the idea is filed in this phase.

**Boundaries**: a pin is tightened under the `Lxx` and never deleted (PITFALLS CF-1);
`test_every_key_the_ui_reads_is_a_derived_dimensions_field` harvests `['word',` lines from
`app.js` as DIMS keys, so any new JS table is an object, not rows of that shape.
**Research flag**: No — standard patterns. The parity proof will surface relation rows that are
not inert; the plan budgets for dropping them.
**Plans**: TBD
**UI hint**: yes

### Phase 24: Bore-Shape Selector

**Goal**: A user picks a bore shape instead of inferring it from a warning — a select whose
options come from the schema, whose state is derived from the flat fields on load, and which
writes only the flat fields — with the API, the CLI and the URL contract unchanged (L05).
**Depends on**: Phase 21 (the trigger the idea named, and the golden request sets); Phase 23
(the relation evaluator and the condition vocabulary the selector reuses).
**Requirements**: REQ-selector-schema-carried, REQ-selector-derives-and-writes-through,
REQ-selector-round-trips-per-state
**Skip condition**: the milestone's most discretionary item — nothing in Phases 22, 23 or 25
depends on it, so it can be cut without breaking anything else. Skipped — never deleted — when
the human defers it at discuss-phase (decision 9), or when the schema-carried route cannot be
built without weakening the field-name pin (the choice is then the human's, not a quiet
`BORE_SHAPES` constant). A skipped phase keeps its number and its row: the Progress entry reads
`Skipped (cut)`, STATE.md's Roadmap Evolution gets a dated line, its criteria are marked not
applicable, and its three requirements move from the Traceability table to REQUIREMENTS.md's
Future Requirements by an explicit edit with the human, so nothing is orphaned silently; the
idea file stays filed with its trigger restated; Phase 25 then measures the `HEAD` that
shipped without it. PROJECT.md's success metric 2 ("a bore shape is picked, not inferred from
a warning") then closes as partly met, recorded in the audit (the v0.3 precedent).
**Success Criteria** (what must be TRUE; not applicable when skipped):

  1. The selector is schema-carried. Its options (round, D-flat, hex; "no bore" and the
     keyway's place as settled at discuss-phase) are in `/api/schema` in the same condition
     vocabulary as `enabled_when`; `app.js` renders it with no bore field name in JS, and the
     existing `tests/test_api.py` field-name pin and DIMS-key pin hold with an empty diff.
  2. Loading never writes; changing writes the minimum. On load the select shows the state
     derived from the flat fields, and the 44 golden request sets from Phase 21 are unchanged
     by its presence; a change writes only the minimum switch-off fields, as explicit `"0"` and
     never `''`, restores the values the user typed, and adds no entry to the `fields` map; the
     browser test asserts no non-`GearParams` key in any `/api/*` request and none in the hash.
  3. Each selector state round-trips. A model-driven test per state proves the composed
     `derive()` document identical whether the shape is reached through the selector or
     through the flat fields; `git diff --exit-code tests/regression/pre_v0_2.json` is clean
     after every task; the bore-shape idea is retired in the commit that closes it.

**Decisions the human takes at this phase's discuss-phase** (before planning; this is the
phase the research flags as needing a human decision):
  - 9 — the selector's logic home. S1, schema-carried, was taken at kickoff
    (REQ-selector-schema-carried); open is whether to defer the selector at all, which is the
    skip decision above.
  - 10 — a fifth "no bore" option, with the keyway kept outside the select. Open
    (REQ-selector-schema-carried leaves it to discuss-phase).
  - 11 — what Hex or D-flat writes when its own field is 0: a pending UI state (all the
    research files lean this way) or a starter value (`bore_flat`'s default is 8). Open
    (REQ-selector-derives-and-writes-through leaves it to discuss-phase).

**Boundaries**: UI-only in the sense that no `GearParams` field, no API shape and no CLI flag
changes; the select is not a field and never appears in the URL. Option tables, if the
implementation has any, are objects and not `['word', ...]` rows (PITFALLS BS-4).
**Research flag**: No — it needs the human decisions above, not research.
**Plans**: TBD
**UI hint**: yes

### Phase 25: Gate Bar Re-Set, Venv Probe, Ledger Close

**Goal**: The gate is measured once on the shipped `HEAD` under a rule written before the
first reading, the human sets the bar from the readings, L34 is amended once, `make venv` is
probed once under `PIP_CONSTRAINT` without touching the main checkout's hooks, and the two
small ledger items (the Pi 5 claim, the reverify recipe) are closed.
**Depends on**: Phases 21–23 landed, and Phase 24 unless it was skipped. The re-set must
measure the shipped `HEAD`, so this phase is last. The order inside the phase is fixed: the
rule, the readings, the bar; the venv probe only after the last reading, because it loads the
host and must never run during one. The re-set and the probe both amend L34, so they share this
phase and L34 is amended once.
**Requirements**: REQ-gate-rule-pre-registered, REQ-gate-bar-reset, REQ-venv-constraint-probe,
REQ-pi5-claim-softened, REQ-reverify-recipe
**Placement of three requirements**: REQ-venv-constraint-probe is here because its green
branch amends L34 in the same `Lxx` as the bar, and because its constraint on the host (not
during a reading, not in the main checkout) is a sequencing rule of this phase. REQ-reverify-recipe
is here, although one paragraph is cheap early (the research placed it in Phase 21), because its
fork — a paragraph or `.ai_skills/reverify-phase` — turns on whether the record shows the loop
has hit three times, and that count is only readable once Phases 21–24 have shipped.
REQ-pi5-claim-softened has no stronger reason to be anywhere else and lands with the other
ledger items.
**Success Criteria** (what must be TRUE):

  1. The rule exists before any reading. `bench/RESULTS.md` carries the idle threshold
     (precedent: load below 1.5, Phase 12), the cool-down between runs, N of at least 5 per
     arm, the give-up rule and the A/B design (the full gate with and without
     `tests/test_browser.py`, interleaved), and says it is a new method rather than L34's
     loaded-host one (Phase 15 D-04 read loads of 5–30 and took the largest of three); `git log`
     shows that commit before the first reading's.
  2. The human sets the bar from the readings. Each reading is recorded with its load, machine
     and `HEAD` (min, median and max per arm); the bar is the human's call from those numbers,
     recorded as such and never tuned toward a pass (L08, L34); if the give-up rule fires, the
     absence of an idle host is recorded and the human decides what it means.
  3. L34 is amended once. One `Lxx` carries the new bar and, if the probe is green, the widened
     CI sentence; the stale `63.555 s` and `~64 s` sentences in `Makefile`,
     `.pre-commit-config.yaml` and `docs/HOW_TO_DEVELOP.md` are rewritten and IN-03 is retired
     in the same commit (the finding closed with the sha in
     `docs/tech_debt/active/2026-10-09-phase-19-review-info-findings-deferred.md`; its other
     three findings stay open); a search for the stale figures in those three files prints
     nothing.
  4. The probe is safe and recorded. `make venv` under `PIP_CONSTRAINT=requirements.txt` runs
     in a linked worktree or scratch clone, never the main checkout; `make verify`'s result
     line, `pip check` and the freeze diff are recorded (its wall time is not a gate reading and
     never enters the bar); `.git/hooks/pre-commit` still names `.venv/bin/python` afterwards,
     checked and recorded; the record's timestamps put the probe after the last reading. Green:
     `$(STAMP)` gains the constraint. Red: the pins that fail are recorded and the idea stays
     filed.
  5. The small ledger is closed. README states the hardware every number in it came from and
     makes no Raspberry Pi 5 claim without a measurement; `docs/HOW_TO_DEVELOP.md` §6 carries
     the reverify paragraph beside the ship-note workaround (a fix after verification re-stales
     the report; re-dispatch `gsd-verifier` with the delta, commit, re-ship), or
     `.ai_skills/reverify-phase` if the record shows the loop has hit three times, the count
     read from the record; each idea is retired in the commit that closes it (status, sha,
     `git mv`, INDEX row).

**Decisions the human takes at this phase's discuss-phase**:
  - 13 — the idle threshold X (precedent 1.5), the cool-down, N (REQ-gate-rule-pre-registered
    sets at least 5 per arm; the architecture file said 3) and the give-up rule, all fixed
    before any reading. Open. The human then sets the bar from the readings.
  - 14 — whether to re-sweep the xdist knee on the 18-CPU host (the N = 8 knee was swept on 12
    CPUs). Deferred in REQUIREMENTS.md "Form follow-ups"; discuss-phase confirms, and if it is
    reopened it happens before the rule is written, because it changes the gate being measured.
  - 15 — whether to adopt `PIP_CONSTRAINT` in `make venv` if the probe passes. Taken as yes on
    green (REQ-venv-constraint-probe); discuss-phase confirms. The constraint downgrades
    `fastapi`, `starlette` and `uvicorn` to the pins, and a green macOS arm64 run says nothing
    about the Docker `linux/arm64` image or a Pi 5.

**Boundaries**: the probe never runs during a gate reading and never in the main checkout
(`make venv VENV=...` there runs `pre-commit install` and bakes that venv's python into the
shared hook shim; the Makefile skips the install in a linked worktree). No Raspberry Pi
measurement is taken (nobody has the board). The idea and debt files close only in the commit
that closes them.
**Research flag**: No — standard patterns; the threshold, cool-down and N are decisions, not
research.
**Plans**: TBD

## Process Notes (carried forward)

- Phases run on `gsd/phase-NN-*` branches cut from `origin/main` and land only through
  `make pr.land PR=N` (L22/L25); `.planning/` rides the same PR as the code, never a
  separate planning-only commit. The milestone close is itself a PR.
- `make verify` (ruff, mypy `--strict`, import-linter, unfinished-work scan, pytest on 8
  xdist workers under `fail_under = 96`) is the gate for every phase, no exceptions (L13,
  L34). Since Phase 17 (L36) it runs as the pre-push hook; the pre-commit hook runs
  `make verify.fast` (~11 s warm, under `gsd_run query commit`'s 30 s timeout — proved by SDK
  commit `5a3332f`). Since Phase 19 the whole gate reads 162–240 s on the 18-CPU M5 Max
  (192.94 s mean, 19-09) against L34's 66 s bar, a cost the human accepted (`accept-A`, L38);
  the bar's re-set is an open decision. A killed SDK commit still leaves the hook running as
  an orphan: wait for it, then one plain `git commit`, never a blind retry (D-07).
- Every phase that adds a decision logs it as a new `Lxx` in
  `docs/architecture/decision_log.md`, append-only.
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
| 21–25 | v0.5 | 0/? | Not started | — |
