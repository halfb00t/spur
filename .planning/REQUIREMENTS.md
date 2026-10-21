# Requirements: spur — milestone v0.6 Clean Ledger

**Defined:** 2026-10-15
**Core Value:** A number this tool prints is a number someone will cut metal to — every
dimension is computed honestly or reported as a warning, never guessed (L08).

Scope fixed in `PROJECT.md` ("Current Milestone: v0.6 Clean Ledger"). Research pass:
`.planning/research/SUMMARY.md` is the entry point; its "Conflicts Between the Four Files"
table is authoritative over any single research file, and every figure quoted below carries
its evidence tag (MEASURED / READ / UNVERIFIED; READ-from-STACK = a STACK.md measurement not
yet re-run). The human's kickoff choices (2026-10-15) are baked into the wording: the bad-link
refusal covers **enums and number boxes**, with **blank still meaning "use the default"**; the
`root_fillet` label **is fixed** (a second, text-only visible change); the Phase 18 and 10
info findings are **triaged cheaply**; Ubuntu 26 is **pre-classified now** on a throwaway PR.

REQ-IDs continue the project's `REQ-slug` convention.

## Rules every requirement lives by

- **Same part, same links.** `tests/regression/pre_v0_2.json` and
  `tests/regression/golden_requests.json` stay byte-identical to the `v0.5` tag through every
  commit (`git diff --exit-code v0.5 -- tests/regression/` empty at each phase close). No new
  `GearParams` field. Only a link carrying a value its form control cannot hold changes
  behaviour; every valid link sends the same fields and builds the same part (L05).
- **A flake or hang is fixed only from a captured reproduction.** Without one it is
  re-deferred with the measurement that failed to reproduce it. Never closed on a quiet run,
  never silenced by a `filterwarnings` entry or a rerun plugin (L08).
- **Every new guard test is seen red once** against the defect it guards, and the red is
  recorded in the commit or plan summary.
- **A debt item or idea is retired only in the commit that fixes it** (CLAUDE.md);
  `bench/RESULTS.md` readings are never rewritten — corrections are dated and appended.
- **No new runtime or dev dependency.** pytest 9.1.1, pytest-xdist 3.8.0, pytest-cov 7.1.0,
  `playwright==1.63.0`, CPython 3.12 held (L23).

## v0.6 Requirements

### Gate — fails with a cause or passes

- [x] **REQ-hook-pin-ignores-caller-args**: `tests/test_hooks.py`'s shared-recipe pin passes
  when the caller sets `PYTEST_ARGS`, in both the environment and the `make` command-line form;
  the new test is red for both forms before the fix
  (`docs/tech_debt/active/2026-10-10-hook-pin-reads-the-callers-pytest-args.md`).
- [x] **REQ-twin-selectors-race-fixed**: the browser step "twin selectors" no longer reds on
  `main` (runs 38347283201, 38680454993; PR runs of the same commits green). The request
  baseline is taken after the page's own STL request has settled past the 350 ms debounce;
  a delayed-route proof shows the old step red and the new one green. Filed as `must` debt and
  retired in the fixing commit; folds in info findings 24 CX-05 and 21 IN-04a.
- [x] **REQ-tracker-flake-fixed-from-repro**: STACK's stdlib reproduction and forced-GC check
  are re-run on this host before any fix (READ-from-STACK until then). The fix is in
  `tests/test_pool.py` only (no `src/spur/pool.py` change, no warning filter). Acceptance:
  forced-GC check red → green, plus one before/after run whose cap and arms are committed
  before it starts; effective `-n`, tool versions and signature-classified reds recorded in
  `bench/RESULTS.md`. If the reproduction does not hold, the item is re-deferred with that
  measurement instead (`2026-10-06-resource-tracker-flake-fails-the-gate.md`).
- [x] **REQ-hang-leaves-evidence**: a stalled test in `make verify` leaves its test id and a
  stack dump in the log (`faulthandler_timeout` dump-only, `-v --durations`), shown by a
  deliberately stalled test once; the timeout is set from a recorded `--durations` reading;
  the gate's cost is measured against the 300 s bar (L43). The hang item stays `active` with
  a runbook that states what the evidence cannot see (a stall after the last test)
  (`2026-10-10-make-verify-hung-at-98-percent-with-no-failure.md`).
- [x] **REQ-test-image-runs-what-it-claims**: `make test-image` is run once and its red set
  recorded before any fix; afterwards it passes, and every test it skips is skipped by a named
  reason, not by collection failure
  (`2026-10-10-test-image-collects-tests-that-read-host-files.md`).

### Ledger — tests and harness tell the truth

- [x] **REQ-slug-totality-guarded**: a seeded, millisecond test in the commit slice proves
  `slug()` raises nothing and ends `_trochoid` exactly when `root_mode` says trochoid, over
  draws stratified to reach every reachable refusal reason (each bucket asserted non-empty);
  `bracket degenerate` and `curve invalid` — unreachable by validated parameters (MEASURED) —
  are forced by patching and labelled forced; the test is red against a patched raising
  `_junction`/`_root_curve` (`2026-10-15-slug-totality-is-not-guarded-in-the-gate.md`).
- [x] **REQ-failed-build-name-isolated**: the failed-build name test reads 422 regardless of
  test order or xdist scheduling — `_EXPORTS` replaced per test — and is red when the cache is
  pre-seeded with its gear under the old code
  (`2026-10-15-failed-build-name-test-depends-on-cache-order.md`).
- [x] **REQ-stop-group-signals-first**: `stop_group` signals the group before it inspects it;
  a failed `ps` fails the teardown as "survivors unknown" with the group already signalled;
  the SIGTERM grace and the leader-only-break red are kept; a sub-second unit test outside
  the `*browser*` glob proves both paths and cleans up its own group
  (`2026-10-10-stop-group-reads-ps-before-it-signals.md`).
- [x] **REQ-group-floor-recorded-true**: the `MIN_GROUP_MEMBERS` comment names the members
  observed by `ps` on macOS and Linux (uvicorn, the resource tracker, one or two workers);
  dated corrections sit under both `bench/RESULTS.md` rows; no reading rewritten
  (`2026-10-10-group-floor-of-3-is-not-two-pool-workers.md`).
- [x] **REQ-launch-message-true**: the browser-launch failure message names a command that
  installs the browser when the stamp is present but the browser is not; text-only, the
  literal pinned by `tests/test_browser_pins.py` kept
  (`2026-10-10-launch-failure-message-names-a-stamp-that-skips-the-install.md`).

### Bad links — refused, never guessed

- [x] **REQ-bad-link-refused**: a link carrying a non-blank value its form control cannot hold
  — an enum outside its options (`root_shape=bogus`, `recess_sides=bogus`) or non-numeric
  text in a number box (`teeth=abc`, `mate_teeth=abc`) — keeps the token in the fragment,
  sends it, and is marked through the existing 422 path with the server's text; no part is
  built. Editing the field or Reset clears it. Generic over the schema: no field name in
  `app.js` outside `DIMS` (L02). A blank value (`teeth=`, `root_shape=`) still means "use the
  default", unchanged.
- [x] **REQ-bad-link-decision-logged**: `L44` records the boundary (what is refused, blank
  kept as default, unknown keys still ignored) and amends what L39 pinned; the browser step
  `root_shape=bogus as today` is rewritten in the same commit — the old pin seen red against
  the fix and the new one red with the fix reverted; `docs/architecture/web-ui.md` brought
  true; the debt item retired (`2026-10-10-root-shape-bogus-loads-a-blank-select.md`).
- [x] **REQ-root-fillet-label-follows-root**: the `root_fillet` derived-dimension label
  stops reading "Root fillet used" while a hob root is in force (Phase 19 IN-04a); text only —
  no part, number or request moves; own commit.

### Info findings — none left `open`

- [x] **REQ-info-findings-triaged**: every open review info finding of Phases 19 and 21–24
  carries one disposition in its `*-REVIEW-DISPOSITION.md`: `fixed` + sha, `deferred` + debt or
  idea path, or `skipped` + a one-line reason; zero `open` at the milestone close. Findings
  that let a test pass vacuously (24 CX-05, 23 IN-08, 23 IN-11, 21 IN-03, 21 IN-04) are fixed,
  not skipped.
- [x] **REQ-old-info-findings-triaged**: Phase 18 IN-01..08 and Phase 10 IN-01/02 are
  dispositioned the same way: overtaken ones closed with a reason (18 IN-02, IN-06), the
  18 IN-07 docstring fixed, the rest filed as one `nice` item with a named trigger, and 10 IN-02
  (it changes a printed value) filed as a decision for the human, not fixed.

### CI — Ubuntu 26

- [x] **REQ-ubuntu26-preclassified**: a throwaway PR that changes only `runs-on` to
  `ubuntu-26.04` runs all three CI jobs before the `ubuntu-latest` rollout reaches the repo;
  its whole logs are classified in `bench/RESULTS.md` (`Image:` line, per-job result) before
  any `ci.yml` edit lands; nothing from the PR merges but the record.
- [ ] **REQ-ubuntu26-classified-on-migration**: the first `ubuntu-latest` run whose
  `Set up job` names 26.04 is classified from the whole log of all three jobs; green → dated
  reading and the item resolved; red → options to the human (pin `ubuntu-24.04` only on their
  call). If no migrated run happens by the close, the milestone closes with the item `active`
  and its trigger restated (`2026-10-10-ubuntu-latest-migrates-to-ubuntu-26-on-19-october.md`).

## Future Requirements

### Gate follow-ups (after a first captured hang)

- **REQ-hang-fails-named**: `faulthandler_exit_on_timeout` turns a hang into a named failure.
  Deferred: it changes gate semantics, drops coverage data (a second failure line under
  `fail_under = 96`) and raises the dev floor to `pytest>=9`; decide after the first captured
  hang (STACK).
- **REQ-hang-journal**: a flushed per-worker start/finish journal that survives SIGTERM — only
  if `-v` proves insufficient (SUMMARY C2).

### Carried candidates (triggers not fired)

- The gear family, helical first — the v0.7 candidate.
- The hob-root default flip — D-09's trigger (a real fit report or a mating-pair request below
  `z_min`).
- Selector stash invalidation (the behavioural half of 24 IN-01) — filed as an idea.
- Phase 10 IN-02 — `tip_chamfer_effective` gated on the raw request; changes a printed value.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Any change to what a valid link sends or builds | L05; the fixture and golden requests stay byte-identical to `v0.5` |
| Refusing a blank value in a link | blank means "use the default" today; refusing it would change existing links (human's pick) |
| Refusing unknown query keys | the API ignores them too; not a value the form misreads |
| Client-written error wording for bad links | the server's 422 text is the one source (L02) |
| A `filterwarnings` entry, a rerun plugin, or `shutdown(wait=True)` in `BuildPool` for the flake | symptom fixes; L08 |
| `pytest-timeout` or any new test dependency | `faulthandler_timeout` is built in (MEASURED under xdist + cov) |
| Upgrading Playwright to 1.64.0 or Python past 3.12 | moves the headless-shell revision and canvas bar; L23 |
| Running `playwright install` on every `make test` | changes the stamp contract and its pins; filed as an idea instead (SUMMARY C8) |
| A `GearParams` field or a `calc` warning on a fixture record | rewrites `pre_v0_2.json` (L26) |

## Traceability

Filled by the roadmap (2026-10-15). Phase numbers continue from v0.5's Phase 25. Phase 29 is
date-gated: if no `ubuntu-latest` run names Ubuntu 26.04 by the milestone close, it closes with
its item `active` and `REQ-ubuntu26-classified-on-migration` moves to Future Requirements by an
explicit edit with the human (ROADMAP.md, Phase 29 close condition).

| Requirement | Phase | Status |
|-------------|-------|--------|
| REQ-hook-pin-ignores-caller-args | Phase 26 | Complete |
| REQ-twin-selectors-race-fixed | Phase 26 | Complete |
| REQ-tracker-flake-fixed-from-repro | Phase 26 | Complete |
| REQ-hang-leaves-evidence | Phase 26 | Complete |
| REQ-test-image-runs-what-it-claims | Phase 26 | Complete |
| REQ-ubuntu26-preclassified | Phase 26 | Complete |
| REQ-slug-totality-guarded | Phase 27 | Complete |
| REQ-failed-build-name-isolated | Phase 27 | Complete |
| REQ-stop-group-signals-first | Phase 27 | Complete |
| REQ-group-floor-recorded-true | Phase 27 | Complete |
| REQ-launch-message-true | Phase 27 | Complete |
| REQ-bad-link-refused | Phase 28 | Complete |
| REQ-bad-link-decision-logged | Phase 28 | Complete |
| REQ-root-fillet-label-follows-root | Phase 28 | Complete |
| REQ-info-findings-triaged | Phase 28 | Complete |
| REQ-old-info-findings-triaged | Phase 28 | Complete |
| REQ-ubuntu26-classified-on-migration | Phase 29 | Pending |

Individual info-finding fixes ride the phase that touches their file (Phase 26: 24 CX-05, 21
IN-04a; Phase 27: 21 IN-01..03, 22 IN-01..03, 23 IN-08, 23 IN-11, 24 IN-03, 19 IN-01/02; Phase 28:
24 IN-01, 24 IN-02/CX-03); the triage requirements are assigned to Phase 28, where the last
disposition closes.

**Coverage:**
- v0.6 requirements: 17 total
- Mapped to phases: 17 (Phase 26: 6, Phase 27: 5, Phase 28: 5, Phase 29: 1)
- Unmapped: 0

---
*Requirements defined: 2026-10-15*
*Last updated: 2026-10-15 after roadmap creation*
