# Milestones

## v0.7 Splined Shaft (Shipped: 2026-11-03)

**Phases completed:** 6 phases, 49 plans, 101 tasks

**Key accomplishments:**
- `make gear.unchanged`: tag-baselined byte check of tests/regression/, ci.yml and the raw /api/schema response, read-only git plus `git archive`, wired into both gates at 0.46 s, seen red nine times
- L46 logs spur as a gear and spline generator (amends L02 and L05 by reference, old entries untouched), with the AGENTS.md brief and the roadmap's stale Phase 30 text fixed in one docs commit before any shaft module
- Five docstring-only shaft modules, `parts.py` and five import-linter contracts (10 kept) put in force before any shaft code, paired with three regex belts, a contract-name existence guard and a route and query-key pin, each seen red once
- `Part` at the shared entry points, `model()`'s serving body moved byte for byte into `_serve_model` (115 lines, proved mechanically), and a 503 queue-full text that counts parts, each in its own commit and each leaving `make gear.unchanged` green
- Phase 30 closed on evidence: `make verify` reads `1369 passed in 233.18s` (real 234.48 s, 98.00 % coverage) against v0.6's 236.23 s, and all seven phase-close checks read PASS with the D-20 order proved on a non-empty list
- Frozen ShaftParams (eight pinned fields) through check_shaft and derive_shaft into a typed ShaftDimensions for the default W 25x1.25x18x8f, with the profile shift derived from d_B in one pinned expression order and accepted through X_EPS at the float edges
- A not-collected stdlib oracle (basic rack plus a parametric involute placed by the base-thickness identity) agrees with din5480's shift, tip, both roots and thickness to 1e-9 over 192 cases, with KISSsoft and Hexagon rows as labelled cross-checks and five mutations seen red once
- The default shaft prints D_Re 2.73 and M_Re 27.999 from a closed-form theoretical pin rounded to 0.01 mm, an odd tooth count prints its pin and no M_Re, d_Ff stays null, and a pin-contact guard over an explicit pin waits for Phase 34, with 72-case oracle agreement and six mutations seen red once
- Every shaft prints `W 25x1.25x18x8f` in the shortest round-tripping numbers, and a strict ASCII-only parser reads it back (or refuses naming the token), with five codec guards seen red once and `parts.py` plus its debt item re-targeted to Phase 32
- The gate was green before the human was asked, and the copy's three approved W 120x3x38x8f values agree with the shipped code to the last printed digit (d_a1, M1 minimum) or as a limit (d_Ff1 maximum); the checkpoint is a partial pass, because DIN 5480 Part 1 holds no size tables, and one printed number (root_d) is process-dependent in the copy where the code states one process.
- The three copy values the human approved are pinned as cited tests and each was seen red once; every clause the copy confirmed replaced its marker, five markers stay for what it did not; `make verify` reads `2355 passed in 243.23s` (+4.3 % on Phase 30, inside the spread); and L47 closes the phase, which proved the maths on one designation and left d_Ff and odd-count M_Re null.
- A recorded `make verify` baseline on Phase 32's code (2644 passed in 229.17s, real 230.70) and a Chromium table of 91 tokens over 37 number inputs showing the four-condition server rule matches the box on every token it can see, with the human's picks A1/B1/C1 recorded for the plans that implement them.
- `_guard_volume` now reads the chamfer back off the solid's end face, so a cone the kernel never cut is a BuildError instead of a printed `end_chamfer_effective` that is not on the part; the one-valid-solid guard has a durable test, the dead re-raise is gone, and `shank_d` dims without a shank on bit-equal kernel evidence.
- The gear routes now answer `422 number_as_written` for any link number Chromium's number box would blank (`5.`, `+22`, ` 22`, `1_0`), through one request-only route dependency that runs before pydantic, so a blank form box can no longer sit over a non-default part; the rule is pinned to the 91-token Chromium table in a light walker and re-read on the page's own 30 inputs at every gate run.
- The shaft is on the API at `/api/shaft/schema`, `/info` and `/model.{stl,step}` through the gear's own `_serve_model`, its twelve result rows ride its schema as `dims`, and `designation=W 30x2x14x8f` takes the place of the four spline fields: a designation beside any of them is a `422 conflict` on key presence, and every bad or infeasible designation is a `422` at `designation`, never a `500`.
- `spur shaft info|export` serve the same shaft as the API through the API's own `resolve_shaft`, and a parity test over a fixed four-shaft set proves one document and one download name, seen red on a one-ulp change to `tip_d`
- A Gear | Shaft radio switch builds each part's form, preview, rows and downloads from its own routes through one PARTS descriptor, with the page's texts and mate box following the part and the gear page, its pins and its 44 golden queries untouched.
- A `part=shaft` link opens and round-trips on any page through `partOf` and `followHash`, a gear link stays `part`-free, and any other `part` is refused in the page's own words with nothing built until a switch or a new link, with the L49 record, web-ui.md and the rows idea written.
- The browser now proves the page's shaft table and download names equal the API's over the four-shaft set (42 rows, no tolerance, the `fmt` port checked against the browser's own rule), the as-written refusal holds on all seven shaft number fields, and a long shaft's invisible floor grid is fixed through a descriptor field that leaves every gear's grid as it was.
- The heaviest DIN 5480 shaft held ten concurrent requests through the real server with no timeout (slowest 200 10.16 s of 30 s), the phase's gate cost 2778 tests in 241.55 s against 2644 in 229.17 s, and twelve close checks passed.
- A refused-part link now dims the form and Reset and outlines the switch (CSS on `body[data-refused]`), the Gear | Shaft switch is ordered above the canvas under 820 px with `aside { display: contents; }`, and the dark primary buttons read 4.85:1 through a `--accent-fg` of the theme's own `--bg`; each seen red first in the browser.
- A logged `make verify` baseline on Phase 33's tree (2783 passed in 230.90s, real 232.23), `/private/` ignored by git and by the Docker build context before any file exists there, and a poppler reading toolchain proved on the human's copy with no value of the standard recorded.
- One checked, process-wide `Tables` object read once from `SPUR_DIN5480_TABLES`, with a strict pydantic schema, provenance on every row, a load-time M1 identity against `din5480.measure_over_pins`, and exact-key size and Table 7 fit lookups, all tested against a synthetic fixture that carries no value beyond the approved anchors.
- A `pdftotext -layout` parser that read 719 of the 721 DIN 5480-2 size rows from the human's copy into the ignored directory (every row through the M1 identity) and reported the two keys it would not guess, plus a locations-only diff and an assemble step that writes the table file only when both pairs of reads agree.
- With a table file loaded, a listed size and fit print s_vmax, s_max and s_min (DIN 5480-1 Table 6 over Table 7) and M_Re max and min at the tabulated pin, each agreeing with the independent oracle within 1e-9; with no file, an unlisted size or a fit outside Table 7, today's numbers stand, the five rows are null and one fixed sentence says why.
- A set-but-broken `SPUR_DIN5480_TABLES` stops every `spur` command and the server with `error: SPUR_DIN5480_TABLES=<path>: <reason>` (exit 1), and the parent's one loaded tables object reaches every build worker and every replaced worker through `ProcessPoolExecutor(initargs=...)`.
- With the tables loaded and the fit listed, build_shaft cuts the flank at the printed s_vmax (2.592 on the default, read back off the solid on all 36 flanks to 3.8e-8 mm), a build worker given the parent's tables builds the same part, and a real browser shows the five tolerance rows from the schema with no page code.
- 161 size rows of DIN 5480-2 read by eye from 300 ppi band crops of pages 8 to 15 into the ignored directory, every one through the loader's M1 identity on the first try, with no key left out and no row re-read; only counts reached the repository.
- Modules 1 to 1.75 (Tables 10 to 17, pages 16 to 23) read from page renders into a 202-row `Tables` document that passes `make tables.check` first time, with the two Table 12/13 keys left out by location.
- Modules 2, 2.5, 3 and 4 of DIN 5480-2 (Tables 18 to 25, pages 24 to 31) read from page images into a 179-row document that passes `make tables.check` on the first run, with only counts and locations committed.
- Modules 5, 6, 8 and 10 of DIN 5480-2 (Tables 26 to 33) read from 300 ppi page bands into 177 size rows in the ignored `private/reads/part2-read2-d.json`, blind to read 1 and to the other parts, `make tables.check` printing `ok` on the whole part.
- Read A of DIN 5480-1 Table 7 (an image-only page) read from 600 ppi crops into the ignored private/ directory as 18 deviation, 21 column, 8 class and 30 tolerance rows, checked by the loader and by the page's own worked example W 120x3x38x8f; the printed tolerance table has 30 rows, not the 24 the plan expected.
- Blind vision read B of DIN 5480-1 Table 7 (page 24) from 600 ppi crops into the loader's schema, checked by the T_G sum, the structural invariants and the page's own W 120x3x38x8f example; the page prints 30 tolerance rows where the plan and the tooling expect 24.
- The two reads of DIN 5480-2 and the two reads of Table 7 were settled by the human, diffed to 0 differences, and assembled into the ignored `private/din5480-tables.json`, which loads with 720 sizes, 18 letters, 8 classes, 30 tolerance rows and 21 column rows. No table value is in the repository.
- The real table file was swept through the guard and the tooth's buildability with nothing null and nothing closed; the human settled the range edge as `x < d_B <= y`, accepted both sweep findings as printed, and approved three designations, which now stand as tests, each seen red.
- One command, `make tables.test FILE=<table file>`, proves the human's table file holds the approved anchors to the last digit, is complete, agrees with M1 at every tabulated pin, produces exactly the sweep findings accepted at 34-15, and reads every printed range edge as x < d_B <= y; the gate never touches it.
- Phase 34 is closed with evidence: one green `make verify` on the final tree (`2934 passed in 213.54s`, `real 214.53`, 85.47 s under L43's bar by `real`), one decision entry (L50) that holds every decision of the phase and no table value, fifteen close checks that all read PASS, and 33 seen-red rows from the plans' SUMMARYs in one table.
- `make gear.unchanged` now bounds every git call (20 s) and the schema probe (60 s), turns git's terminal prompt off, and refuses a `v0.6` that is lightweight, moved off `792b45c`, or only a branch, each guard seen red once.
- `limit_measurement` loses its unreachable odd-count branch, `load_file` reads at most one byte past its 4 MiB cap with each of its two cap checks pinned by a test seen red, and three debt items are retired with shas.
- One logged green gate (2964 passed in 283.77s, real 284.91, 15.09 s under the 300 s bar, both touched modules at 100.00 %), the decision entry L51, sixteen PASS close checks with the leak review, and the 26-row seen-red table.


**Closeout:** override closeout. Known verification overrides: verification of Phases 30–34 reads stale (later phases edited files they cover; each report was `passed` when written). The v0.7 milestone audit (`tech_debt`, 24/24) and Phase 34.1's final gate run (`make verify`, 2964 passed in 283.77 s) postdate those edits. No deferred artifact items: the one open UAT gap (Phase 33, G-33-2) was closed by plan 33-10 and marked resolved at the close.

---

## v0.6 Clean Ledger (Shipped: 2026-10-23)

**Delivered:** The gate either passes or fails with a cause, and the debt ledger says what is true. The false reds were fixed from reproductions: the twin-selectors race and the `resource_tracker` flake. A stalled test now leaves its test id and stack in the log, and `make test-image` runs what it claims. The harness's tests and records were made true: slug totality, the failed-build name, `stop_group` signalling first, the group floor and the launch message. There is one deliberate visible change: a shared link carrying a value its form control cannot hold is refused through the API's own 422 instead of silently building the default part (L44). Two text corrections came with it: a tip chamfer asked for and not cut prints `null` (L45), and the `root_fillet` label follows the root. Every open review finding of Phases 10, 18, 19, 21–24 and 26–28 carries a disposition. No new `GearParams` field was added, and `tests/regression/` and `ci.yml` are byte-identical to the `v0.5` tag.

**Phases completed:** 26–29 (22 plans, 51 tasks); Phase 29 closed on its close condition (Ubuntu 26 trigger not fired).

**Key accomplishments:**
- Gate (Phase 26): the twin-selectors race was fixed after the real app showed a late `/api/info` response (20/20 local runs, then five green `main` runs). The `resource_tracker` flake was reproduced on demand by a forced `gc.collect()`: red 3/3 before the fix, green 3/3 after. `-v --durations=25` plus a dump-only `faulthandler_timeout` (170 s after CI's 83.55 s slowest phase) makes a stalled test name itself; the gate cost was −0.51 %. `make test-image` reads `1201 passed in 888.34s`, with six host-only files ignored by name. Ubuntu 26.04 was pre-classified green from a throwaway PR (#40, closed unmerged).
- Ledger (Phase 27): a seeded 1,300-draw `slug()` totality test sits in the commit slice. The failed-build name test gets a fresh `_BlobCache`. `stop_group` sends SIGTERM to the group before any `ps` read, and an unreadable `ps` fails the teardown as "survivors unknown". The group-floor text names the members `ps` listed. The launch failure names `rm -f .venv/.browser && make test`.
- Bad links (Phase 28): a link value a control cannot hold is kept in a `rejected` map, sent as given and refused by the API's 422 (L44). The `root_fillet` row reads "Hob tip radius used" under a hob root. `tip_chamfer_effective` is gated on the applied chamfer (L45, `6497c28`).
- Triage (Phase 28): 41 open review findings of Phases 10, 18, 19, 21–24, 26 and 27 each carry one evidenced disposition (28 fixed, 6 skipped with a reason, 7 deferred to a file that exists). Phase 28's own five findings were decided by the human (D-19..D-23).
- Ubuntu 26 (Phase 29): three dated reads of the `ubuntu-latest` window found 30 of 30 jobs on `ubuntu-24.04`. The phase closed on the human's `close`, and the item stays active with its trigger restated.
- Close: the milestone audit read 16/16 requirements, 11/12 integration seams and 5/6 flows; the partial one is the known WR-02 deferral, widened in its debt item at the close (`2226084`). Phases 26 and 27 were re-verified after later squashes (`3adc939`), and Phase 28's UAT was closed against its executed gap plans (`3e42e23`).

**Stats:**
- 307 files changed (+78,524 / −1,911) from the `v0.5` tag to the last squash; 51 outside `.planning/` (+3,067 / −290), 24 of them code, tests, bench or config (+2,336 / −252); `src/` +54 / −15 in `calc.py`, `model.py` and `app.js`
- 4,158 lines of package Python, 17,664 of tests, 4,548 of bench, 671 of hand-written UI JS; 1,348 tests in `make verify` (1,318 at v0.5)
- 4 phases, 22 plans, 51 tasks; 6 PRs (#41, #42, #44–#47) after the v0.5 close (#39); #40 the throwaway Ubuntu 26 PR, closed unmerged
- 8 days from the v0.5 close squash (2026-10-15) to the last squash (2026-10-23)
- 0 runtime dependencies added (`requirements.txt` 39 → 39 lines)

**Git range:** `26ddd74` (Milestone v0.5: Honest Form — close and archive (#39)) → `a620399` (Phase 29: Ubuntu 26 Final Reading (#47))

**Closeout:** `verified_closeout`. All four phases project `passed` (26 and 27 re-verified at the close), the open-artifact audit is clear, and the audit status is `tech_debt` (`milestones/v0.6-MILESTONE-AUDIT.md`). REQ-ubuntu26-classified-on-migration was deferred to Future Requirements by the human's approved Phase 29 close. Known verification overrides: 0 newly acknowledged, 0 carried forward.

**What's next:** `/gsd-new-milestone`. The Ubuntu 26 rollout window runs to 2026-11-19, and its item fires on the first `ubuntu-latest` run on 26.04. WR-02 (an accepted link token under a blank box) fires on the next edit of `refuse()` or `gearQuery()`. The `make verify` hang item has its own trigger. Nyquist is partial: run `/gsd-validate-phase` for 26 and 28 if their records matter.

---

## v0.5 Honest Form (Shipped: 2026-10-15)

**Delivered:** The web form tells the user up front what each field does, and a real browser proves it — a headless test of the shipped `app.js` inside `make verify` and CI with the request of every one of the 44 fixture links pinned (L39), the hob-root part downloading as `..._trochoid` (L40), eleven `enabled_when` relations dimming an ignored field before it is typed, each proved against `calc` (L41), and a schema-carried Bore shape select that writes only the flat fields (L42); then the gate bar re-set by the human under a rule committed before the first reading and `make venv` installing under the closure (L43), with the Pi 5 claim softened and the reverify loop made a skill — no new `GearParams` field, the 44-record fixture and `requirements.txt` byte-identical to the `v0.4` tag.

**Phases completed:** 21–25 (23 plans, 54 tasks); Phase 24 (discretionary) executed.

**Key accomplishments:**
- Browser test (Phase 21): `playwright` 1.63.0 pinned with its headless shell under `.venv`, a real uvicorn on a pre-bound socket; the form proven equal to `/api/schema`, both 422 marking paths, the rendered warnings and the link round trip, each assertion seen red once; the query of each of the 44 fixture links pinned in `tests/regression/golden_requests.json`; inside `make verify`, the pre-push hook and CI, green on a real `ubuntu-latest` run (38059369744, `1226 passed`); no gate cost above noise in a six-run interleaved A/B (B − A = −2.47 s) (L39).
- Download name (Phase 22): `GearParams.slug()` appends `_trochoid` exactly when `calc.root_mode` builds the hob root; radial parts and ignored trochoid requests keep today's name byte for byte; L40 lists every consumer of the old names; pinned by header, pure, record and real-browser tests.
- Conditional fields (Phase 23): eleven relations declared on `GearParams` in one `when()` vocabulary, carried in `/api/schema`, rendered dimmed-and-editable by generic `applyRelations()`; `tests/test_relations.py` proves each against `calc` in both directions at commit time; the golden sweep compares the dimmed set under all 44 links (L41).
- Bore-shape selector (Phase 24): a model-level `selectors` list reaching `/api/schema` only, built, derived and written back by generic `app.js` code; `tests/test_selector.py` proves totality, exclusivity and the per-state round trip; a request recorder on every page finds no key `GearParams` lacks; Codex cross-review findings fixed before the land (L42).
- Gate and ledger (Phase 25): the idle-host rule committed alone (`1d5ce8a`) before any reading; the host never quieted, the human waived the wait and set 300 s on the rule's `none` candidate from two non-decisive readings (A1 195.23 s, B1 179.21 s) (L43 amends L34); a GREEN `make venv` probe under `PIP_CONSTRAINT` in a linked worktree adopted; README names its two dev hosts and makes no Pi 5 claim; `.ai_skills/reverify-phase` from a five-hit count.
- Quick fix (#37) and close: a hex bore names only the bore fields set away from their defaults (L27 amended); the milestone audit read 24/24 requirements, 8/8 integration seams, 5/5 flows, security clean on all five phases; Phase 22's two untriaged review warnings filed as `must` debt at the close (`4ef9f15`).

**Stats:**
- 273 files changed (+55,043 / −1,256) from the `v0.4` tag to the last squash; 52 outside `.planning/` (+7,360 / −152), 22 of them code, tests, bench or config (+6,105 / −119)
- 4,145 lines of package Python, 16,560 of tests, 4,544 of bench, 645 of hand-written UI JS; 1,318 tests in `make verify` (1,220 at v0.4), 97.99 % coverage against the 96 % floor
- 5 phases, 23 plans, 54 tasks; 6 PRs (#33–#38, #37 a quick fix) through `make pr.land` after the start PR #31
- 5 days from the milestone start commit (2026-10-10) to the last squash (2026-10-15)
- 0 runtime dependencies added (`requirements.txt` 31 → 31 pins); `playwright` pinned exactly in the `[dev]` extra
- `make verify` bar 66 s → 300 s on the 18-CPU M5 Max (L43); readings 195.23 s and 179.21 s, non-decisive

**Git range:** `a310cd3` (Milestone v0.5: Honest Form — start (#31)) → `cbbe730` (Phase 25: Gate Bar Re-Set, Venv Probe, Ledger Close (#38))

**Closeout:** `override_closeout` in the tooling's terms — Phases 21–24 project `verification_status: stale` because later squashes (#34–#38, #37) changed files their reports cover (all four reports `passed`; per-file cause and no-regression evidence in `milestones/v0.5-MILESTONE-AUDIT.md`, status `tech_debt`); Phase 25 `passed` with three human-accepted overrides and Nyquist partial by the same waiver. Known verification overrides: 0 newly acknowledged, 0 carried forward.

**What's next:** `/gsd-new-milestone` — the `resource_tracker` flake's fallback trigger falls due at its start; the Ubuntu 26 runner migration fires 2026-10-19; candidates: the gear family (helical first), the hob-root default flip on D-09's trigger, the open review info findings of Phases 21–24.

---

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
