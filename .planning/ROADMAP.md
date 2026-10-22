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
- 🚧 **v0.6 Clean Ledger** — Phases 26–29 (in progress; Phase 29 is date-gated and may close
  with its item still active)

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)
- Numbering continues across milestones — v0.6 starts at Phase 26, after v0.5's Phase 25; the
  next milestone starts at Phase 30, after Phase 29 (Phase 29 keeps its number even if it closes
  with its item still active).

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

### 🚧 v0.6 Clean Ledger (In Progress)

**Milestone Goal:** Retire the open `must` debt and the cheap `nice` items, and triage every
open review info finding, so the gate either passes or fails with a cause — never hangs or
flakes unexplained — with no new `GearParams` field, the 44-record fixture and the golden
request pin byte-identical to the `v0.5` tag, and exactly one visible change: a link carrying
a value its form control cannot hold is refused instead of silently building the default part.

- [x] **Phase 26: Gate Fails With a Cause** - The false reds are fixed from reproductions or
      re-deferred with the measurement, a stalled test names itself, the image recipe tests
      what it claims, and Ubuntu 26 is pre-classified before the rollout reaches the repo (completed 2026-10-20)
- [x] **Phase 27: Ledger Tests and Harness** - Slug totality guarded in the commit slice, the (completed 2026-10-20)
      failed-build name test independent of cache order, `stop_group` signalling before it
      reads `ps`, and the harness's own records and launch message made true
- [x] **Phase 28: Refuse the Bad Link** - A link carrying a value its form control cannot hold (completed 2026-10-22)
      is refused visibly through the existing 422 path under a new `L44`, the `root_fillet`
      label follows the root, and every open review info finding ends dispositioned
- [x] **Phase 29: Ubuntu 26 Final Reading** - Date-gated and last: the first `ubuntu-latest` (closed, trigger not fired, 2026-10-22)
      run on Ubuntu 26.04 classified from its whole log; may close with the item still active

## Phase Details

### Phase 26: Gate Fails With a Cause

**Goal**: `make verify` and `main` CI stop failing for reasons that are not the product, and
the failures and stalls that remain leave their cause in the log — the false reds are fixed
from reproductions (or honestly re-deferred with the measurement that failed to reproduce
them), a hang leaves its test id and a stack dump, the image recipe tests what it claims, and
the Ubuntu 26 runner is read before the migration reaches the repo.
**Depends on**: Nothing new — builds on shipped v0.5 (the `v0.5` tag on `26ddd74` is the
fixture baseline). Every false red this phase removes pollutes every later gate reading of the
milestone, so it goes first. The order inside the phase is fixed: (1) the hook pin, first —
every later gate reading runs through the recipe it guards; (2) the Ubuntu 26 throwaway PR,
second, because its clock is external (the `ubuntu-latest` rollout begins 2026-10-19 and the
PR's three jobs must have run before it does; the human pushes the PR); then (3) the twin
selectors race, (4) the flake, (5) the hang evidence and (6) `make test-image`, in that order.
**Requirements**: REQ-hook-pin-ignores-caller-args, REQ-twin-selectors-race-fixed,
REQ-tracker-flake-fixed-from-repro, REQ-hang-leaves-evidence,
REQ-test-image-runs-what-it-claims, REQ-ubuntu26-preclassified
**Success Criteria** (what must be TRUE):

  1. The recipes under the gate tell the truth. `tests/test_hooks.py`'s shared-recipe pin
     passes when the caller sets `PYTEST_ARGS`, in the environment and as a `make`
     command-line variable; the new test is seen red for both forms before the fix. `make
     test-image` is run once and its red set recorded before any fix (the research saw two
     `tests/test_bench.py` tests exit 128 for want of a `.git`; the recorded set is the
     reading, not that guess); afterwards it passes, and every test it skips is skipped for a
     named reason, never by a collection failure. Both debt items are retired in their
     fixing commits.
  2. The "twin selectors" red on `main` is gone and its mechanism is proved. The request
     baseline is taken after the page's own STL request for the link has been seen and the
     350 ms debounce has passed; a delayed STL route makes the old step red and the new step
     green, both recorded (runs 38347283201 and 38680454993 are the capture, the mechanism an
     ASSUMPTION from two logs — if the delayed route does not turn the old step red, the plan
     says so before any fix lands). The same change fixes info findings 24 CX-05 (the
     zero-request assertion could pass before the debounce fires) and 21 IN-04a
     (`_follow_link` on Playwright's 30 s default instead of `BUILD_WAIT_MS`). The browser
     file passes repeatedly at `-n 8` with the count recorded. The `must` debt item
     `2026-10-15-twin-selectors-step-reds-main.md` is retired in the fixing commit (status,
     sha, `git mv`, INDEX row).
  3. The `resource_tracker` flake is located and fixed from a reproduction — or re-deferred
     with the measurement. STACK's stdlib reproduction and forced-GC check are re-run on this
     host and recorded before any fix (READ-from-STACK until then). The fix is in
     `tests/test_pool.py` only: `git diff v0.5 -- src/spur/pool.py` is empty, no
     `filterwarnings` line changes, no rerun plugin, no `shutdown(wait=True)`. The forced-GC
     check reads red before and green after; one interleaved before/after run, whose cap and
     arms are committed before it starts, records the effective `-n`, tool versions and
     signature-classified reds in `bench/RESULTS.md`; the item is retired in the fixing
     commit quoting that table, and the success line reads "located and fixed from a
     reproduction", never "gone". If the reproduction does not hold on this host, the item
     stays `active` and is re-deferred in the commit that records the measurement that
     failed to reproduce it, its trigger restated (L08).
  4. A stalled test names itself. A deliberately stalled test, run once at `-n 8` with
     coverage, leaves its test id (from `-v`) and a stack dump (from `faulthandler_timeout`,
     dump-only) in the log; the timeout is set from a recorded `--durations` reading
     (research's 120 s is a starting point sized from local timings, to be confirmed against
     the first CI `--durations`); the gate's cost with the added flags is measured and
     recorded against L43's 300 s bar. The hang item
     (`2026-10-10-make-verify-hung-at-98-percent-with-no-failure.md`) stays `active` with a
     runbook that states what the evidence cannot see — a stall after the last test —
     because no cause was found and none is claimed.
  5. Ubuntu 26 is pre-classified. A throwaway PR that changes only `runs-on` to
     `ubuntu-26.04` ran `test (3.12)`, `vendor-bundle` and `image` before the `ubuntu-latest`
     rollout reached the repo; the whole log of each job is read and classified in
     `bench/RESULTS.md` (the `Image:` line from `Set up job`, and each job's result) before
     any `ci.yml` edit lands. Nothing from the PR merges but the record; the PR is closed
     unmerged and its branch is the human's to delete (the `spike/21-linux-runner`
     precedent). A red job is not fixed here: options go to the human, who alone may pin
     `ubuntu-24.04`. The Ubuntu 26 debt item stays `active` for Phase 29.

**Decisions the human takes at this phase's discuss-phase**:
  - `make test-image`: mount `bench/` and `scripts/` read-only with `PYTHONPATH=/app/src:/app`
    and `--ignore` only the files that need `make`, git, the Dockerfile or `.github`
    (ARCHITECTURE and PITFALLS recommend), or exclude by name (which would drop
    `tests/test_calc.py` and `tests/test_trochoid.py`, both import `bench`, and gut the image
    suite). Open until the first run's red set has been read.
  - The hook-pin fix's shape: strip `PYTEST_ARGS` in `_make_env()`, or pass `PYTEST_ARGS=` on
    the dry-run command line. Either works (both MEASURED on GNU Make 4.4.1); the planner's
    call, with both forms tested.
  - Taken at kickoff, confirmed and recorded: the hang evidence is dump-only
    (`faulthandler_exit_on_timeout` waits for a first captured hang — REQUIREMENTS "Future
    Requirements"); Ubuntu 26 is pre-classified now on a throwaway PR.

**Boundaries**: no `src/spur/pool.py` change; no `filterwarnings` entry, rerun plugin or
`shutdown(wait=True)` for the flake; no new test or runtime dependency (`pytest-timeout` is out;
`faulthandler_timeout` is built in); `tests/test_hooks.py`'s other pins (the recipe prefix, the
five heavy files, the `test-image` `--ignore`, the stamps) hold or are tightened, never deleted.
Every new guard test is seen red once, the red recorded in the commit or plan summary.
`bench/RESULTS.md` is appended to, never rewritten. One concern per commit; each debt item is
retired in the commit that fixes it. **Phase close**: `make verify` result line recorded and
`git diff --exit-code v0.5 -- tests/regression/` empty.
**Research flag**: No research phase. Three first measurements, each the first task of its
item: the `make test-image` red set (never run in research), the CI `--durations` that sets the
timeout, and the flake reproduction re-run on this host.
**Plans**: 7/7 plans complete

Plans:
**Wave 1**
- [x] 26-01-PLAN.md — hook pin ignores the caller's `PYTEST_ARGS`: both forms red, `_make_env()` strips it, item retired

**Wave 2** *(blocked on Wave 1 completion)*
- [x] 26-02-PLAN.md — Ubuntu 26 pre-classified: spike branch from `v0.5`, the human pushes, whole logs classified (D-16 branch written)

**Wave 3** *(blocked on Wave 2 completion)*
- [x] 26-03-PLAN.md — twin selectors: real-app arms first (SC2 wording corrected on record), STL-request baseline + settle, CX-05, IN-04a, 20 runs

**Wave 4** *(blocked on Wave 3 completion)*
- [x] 26-04-PLAN.md — resource-tracker flake: reproduction re-run, forced-GC gate test red then green, B + C, 10 + 10 under a committed rule

**Wave 5** *(blocked on Wave 4 completion)*
- [x] 26-05-PLAN.md — hang evidence: `-v --durations=25`, `faulthandler_timeout` from a reading, throwaway stall, 3 + 3 cost, runbook

**Wave 6** *(blocked on Wave 5 completion)*
- [x] 26-06-PLAN.md — `make test-image`: first red set recorded, mounts + named ignores, pin tightened, item retired, CI idea filed

**Wave 7** *(blocked on Wave 6 completion)*
- [x] 26-07-PLAN.md — phase close gate and the phase's first CI run: D-07's durations rule, the twin step on CI, D-16 follow-through

### Phase 27: Ledger Tests and Harness

**Goal**: The tests that guard the ledger cannot pass vacuously and the browser harness cannot
lie: `slug()` totality is guarded in the commit slice, the failed-build name test no longer
depends on cache order, `stop_group` signals the group before it inspects it, and the records
and messages that describe the harness say what was observed.
**Depends on**: Phase 26 (soft — its hook-pin, flake and twin-selectors fixes keep the gate
readings of this phase free of false reds). Must precede Phase 28: the `stop_group` fix lands
first because Phase 28's red-first protocol runs the browser repeatedly.
**Requirements**: REQ-slug-totality-guarded, REQ-failed-build-name-isolated,
REQ-stop-group-signals-first, REQ-group-floor-recorded-true, REQ-launch-message-true
**Success Criteria** (what must be TRUE):

  1. `slug()` totality is guarded in the commit slice. A seeded test, milliseconds, proves
     `slug()` raises nothing and ends `_trochoid` exactly when `calc.root_mode` says trochoid,
     over draws stratified to the undercut region so that every reachable refusal reason is
     hit, each bucket asserted non-empty; `bracket degenerate` and `curve invalid` —
     unreachable by validated parameters (MEASURED, `tests/test_calc.py:1603-1604`) — are
     forced by patching and labelled forced. The test is seen red against a patched
     `_junction` that raises and against a patched `_root_curve` that raises, both recorded;
     `make verify.fast` still reads under L36's 30 s.
  2. The failed-build name test reads 422 regardless of test order or xdist scheduling.
     `_EXPORTS` is replaced per test (`monkeypatch` of a fresh `_BlobCache`, no reliance on a
     unique-key convention), and the test is seen red when the cache is pre-seeded with its
     gear under the old code.
  3. `stop_group` signals before it reads. The group is signalled before any `ps` read and
     before any `proc.poll()` or `wait()` (a reaped PID can be reused); a failed `ps` fails the
     teardown as "survivors unknown" with the group already signalled; the SIGTERM grace and
     the leader-only-break red (`bench/RESULTS.md`, row 21-01) are kept. A sub-second unit
     test in a file whose name carries no `browser` (the `*browser*` glob is the no-skip scan's
     and the commit slice's exclusion) proves both paths — the group signalled first, the
     failed `ps` failing — and cleans up its own group.
  4. The harness describes itself truthfully. The `MIN_GROUP_MEMBERS` comment names the members
     `ps` observed on macOS and on Linux (uvicorn, the resource tracker, one or two workers —
     the Linux listing from a member-command print in a CI log), and a dated correction sits
     under each of the two `bench/RESULTS.md` rows, no reading rewritten
     (`git diff --numstat v0.5 -- bench/RESULTS.md` reports 0 deleted lines). The
     browser-launch failure message names a command that installs the browser when the stamp
     is present but the browser is not; the change is text-only and the literal
     `playwright install --only-shell chromium` that `tests/test_browser_pins.py` requires
     is kept.

**Rides with this phase** (info findings fixed in the files this phase touches; the disposition
cell names the fixing sha; the triage is counted and closed in Phase 28): 21 IN-01, IN-02 and
IN-03; 22 IN-01 and IN-02; 22 IN-03 as a dated amendment to L40 (not a rewrite); 23 IN-08
(`CUTOUT_STATES` gives the honeycomb gate one open value) and 23 IN-11 (`_js_number` range,
`-0.0`); 24 IN-03; and 19 IN-01/02 with the bench `_host_state` cleanup — the one `model.py`
touch of the milestone, a fixture-guarded one-line change that also changes `tests/test_model.py`'s
3-argument `_chamfer_tips` lambda, the lowest-risk row to drop to `skipped` with a reason if the
human wants no `model.py` diff. A draft triage table is started here so Phase 28's close is a
reading, not a first pass.

**Decisions the human takes at this phase's discuss-phase**: whether the group floor stays at 3
with a comment-only fix (taken in REQUIREMENTS as the record's correction; a forced second build
is the alternative) and whether 19 IN-01/02 touches `model.py` at all.

**Boundaries**: `src/spur/` is untouched except the optional 19 IN-01/02 line; the new
`stop_group` test lives outside the `*browser*` glob and the new slug test is milliseconds, so
`make verify.fast` stays under L36's 30 s; `bench/RESULTS.md` is append-only with dated
corrections; L40 takes a dated amendment, not a rewrite. Every new guard test is seen red once,
the red recorded. **Phase close**: `make verify` result line recorded and
`git diff --exit-code v0.5 -- tests/regression/` empty.
**Research flag**: No — standard patterns.
**Plans**: 6/6 plans complete

Plans:
**Wave 1**
- [x] 27-01-PLAN.md — D-05 group listing: spike branch from the phase head, local macOS listing, the human pushes, whole logs recorded, PR closed unmerged

**Wave 2** *(blocked on Wave 1 completion)*
- [x] 27-02-PLAN.md — ledger guards: seeded stratified `slug()` totality test (red x2), fresh `_BlobCache` for the failed-build name test (red), 24 IN-03, 22 IN-01, 23 IN-08; two items retired

**Wave 3** *(blocked on Wave 2 completion)*
- [x] 27-03-PLAN.md — `stop_group` signals first: teardown moved to playwright-free `tests/process_group.py`, sub-second unit test red then green, leader-only red kept, 21 IN-01; item retired

**Wave 4** *(blocked on Wave 3 completion)*
- [x] 27-04-PLAN.md — the one `model.py` touch (D-03/D-04) with the fixture byte-identical, bench reads `rm.curve`, `_host_state` names an unknown HEAD; Phase 19 item edited in place

**Wave 5** *(blocked on Wave 4 completion)*
- [x] 27-05-PLAN.md — launch message names a working reinstall (pin red, D-09), 21 IN-02, 21 IN-03, 22 IN-02, 23 IN-11; item retired

**Wave 6** *(blocked on Wave 5 completion)*
- [x] 27-06-PLAN.md — `MIN_GROUP_MEMBERS` comment and two dated corrections from both listings, L40 amendment, "Seen red once (Phase 27)", draft triage, phase-close gate; item retired

### Phase 28: Refuse the Bad Link

**Goal**: A shared link carrying a value its form control cannot hold is refused visibly,
through the existing 422 marking path, instead of silently building the default part — decided
and recorded as `L44` — and, in this last code phase, every open review info finding of the
milestone ends dispositioned, none left `open`.
**Depends on**: Phase 27 (the `stop_group` fix must land before this phase's red-first protocol
runs the browser repeatedly) and Phase 26 (false reds out of the gate). Discuss-phase comes
first: it settles the mechanism, the label wording and `L44`'s text on the human's kickoff
choices below.
**Requirements**: REQ-bad-link-refused, REQ-bad-link-decision-logged,
REQ-root-fillet-label-follows-root, REQ-info-findings-triaged,
REQ-old-info-findings-triaged
**Success Criteria** (what must be TRUE):

  1. A bad link is refused, visibly. In a real browser, `#root_shape=bogus`,
     `#recess_sides=bogus`, `#teeth=abc` and `#mate_teeth=abc` each keep the offending token in
     the fragment, send it, and mark the field through the existing 422 path with the server's
     own text (equal to the API's, never client-written wording — L02); the page sends no STL
     request for the link and draws no default part. Editing the field, or Reset, clears the
     mark.
  2. Every valid link is unchanged. A blank value (`teeth=`, `root_shape=`) still means "use
     the default"; an unknown query key is still ignored; the query the form sends for each of
     the 44 golden request sets is unchanged — `git diff --exit-code v0.5 -- tests/regression/`
     is empty (`golden_requests.json` and `pre_v0_2.json`). The change is generic over the
     schema: `app.js` carries no field name outside `DIMS`, and `tests/test_api.py`'s pins on
     the `readHash` line, the `readHash` end, the `gearQuery` token and the Reset line, and its
     rule that no quoted field name appears outside `DIMS`, hold or are tightened under `L44`,
     never deleted or allow-listed to get green.
  3. The decision is logged and the old pin is flipped in the same commit. `L44` records the
     boundary (what is refused, blank kept as default, unknown keys still ignored) and amends
     what L39 pinned; the browser step `root_shape=bogus as today` is rewritten with the old
     pin seen red against the fix and the new pin seen red with the fix reverted, both
     recorded; `docs/architecture/web-ui.md` is brought true; the debt item
     `2026-10-10-root-shape-bogus-loads-a-blank-select.md` is retired in that commit.
  4. The `root_fillet` label follows the root. The derived-dimension label stops reading "Root
     fillet used" while a hob root is in force (Phase 19 IN-04a), its wording settled at
     discuss-phase; text only — no part, number or request moves (the golden sweep and the
     fixture are the proof); its own commit.
  5. No review info finding is left `open`. Every open info finding of Phases 19 and 21–24
     carries one disposition in its `*-REVIEW-DISPOSITION.md` — `fixed` + sha, `deferred` +
     debt or idea path, or `skipped` + a one-line reason — and the vacuous-pass findings (24
     CX-05, 23 IN-08, 23 IN-11, 21 IN-03, 21 IN-04) are `fixed`, not skipped. Phase 18
     IN-01..08 and Phase 10 IN-01/02 are dispositioned the same way: 18 IN-02 and IN-06 closed
     as overtaken with a reason, the 18 IN-07 docstring fixed, the rest filed as one `nice`
     item with a named trigger, and 10 IN-02 (it changes a printed value) filed as a decision
     for the human, not fixed. `grep -n '| info | open |'` over the Phase 10, 18, 19 and 21–24
     `*-REVIEW-DISPOSITION.md` files prints nothing at the milestone close.

**Triage, and where each fix rides**: the triage closes here, the last code phase; individual
fixes land in the phase that touches their file and are only counted here — Phase 26: 24 CX-05
and 21 IN-04a; Phase 27: the list under that phase; Phase 28 itself: 24 IN-01 (the comment),
24 IN-02 and CX-03 (the "Could not build the form" wording, the same case), each a separate
commit in the same file. The one `file` row is the behavioural half of 24 IN-01 (selector stash
invalidation), filed as an idea.

**Decisions the human takes at this phase's discuss-phase**:
  - Taken at kickoff, confirmed and recorded in `L44`: the refusal covers enums and number
    boxes; blank still means "use the default"; unknown keys still ignored; the `root_fillet`
    label is fixed (a second, text-only visible change); the Phase 18 and Phase 10 info
    findings are triaged cheaply.
  - Open: the mechanism (a shared `rejected` map per FEATURES, or a stray option per
    ARCHITECTURE), what exactly is marked and when it clears, and the label wording.

**Boundaries**: the bad-link code is a pre-pass around the pinned `app.js` lines, generic over
the schema's enums and number boxes; a new table in `app.js` is an object, never rows of the
`['word',` shape (they are harvested as `DIMS` keys); `problems()` and `fail()` stay unchanged;
run `tests/test_api.py` early — its `app.js` regexes were not fully read in research. No new
`GearParams` field. `GET /api/info?root_shape=bogus` already answers 422 (`literal_error`), so
the fix is client-side only. **Phase close**: `make verify` result line recorded and
`git diff --exit-code v0.5 -- tests/regression/` empty.
**Research flag**: No — it needs the discuss-phase decisions above, not research.
**Plans**: 8/8 plans complete (28-05..28-08 close UAT gaps G-28-1, G-28-2)

Plans:
**Wave 1**
- [x] 28-01-PLAN.md — the rejected-token map in `app.js` (D-01..D-05), the old pin seen red against it, four new browser steps seen red without it, L44, web-ui.md, the bad-link debt item retired: one commit (D-07)

**Wave 2** *(blocked on Wave 1 completion)*
- [x] 28-02-PLAN.md — the `root_fillet` label keyed on `root_form_d` (red first, Phase 19 item retired), the 24 IN-01 stash comment plus its idea, the 24 IN-02 / CX-03 "Could not build the form" wording (red first): three commits

**Wave 3** *(blocked on Wave 2 completion)*
- [x] 28-03-PLAN.md — comment- or docstring-only fixes: 27 IN-11 climb comment, 26 IN-04 durable citations, 18 IN-07 `root_mode` docstring

**Wave 4** *(blocked on Wave 3 completion)*
- [x] 28-04-PLAN.md — the Phase 18/10 `nice` item and the 10 IN-02 `must` decision filed, 41 ledger rows closed across Phases 10, 18, 19, 21-24, 26, 27, retiring shas written, phase gate

**Gap closure (UAT G-28-1, G-28-2)** *(sequential: each wave blocked on the one before)*
- [x] 28-05-PLAN.md — wave 5: blocking-human decision on 28-REVIEW WR-01, WR-02, WR-03 (= G-28-2 = 10 IN-02), IN-01, IN-02; recorded as D-19..D-23, deferrals filed as debt
- [x] 28-06-PLAN.md — wave 6: D-21 carried out once: L45 + the tch gate + red test + fixture check + item retired, or kept with a reason and an event trigger
- [x] 28-07-PLAN.md — wave 7: D-19, D-20, D-22 in app.js, one red-first commit per `fix`, L44 dated amendments
- [x] 28-08-PLAN.md — wave 8: IN-02 re-wrap per D-23, the retiring sha, 28-REVIEW-DISPOSITION.md closed, phase gate

**UI hint**: yes

### Phase 29: Ubuntu 26 Final Reading

**Goal**: The first `ubuntu-latest` run that runs on Ubuntu 26.04 is read from its whole log,
all three jobs, before any fix — resolved on a green reading, handed to the human on a red one.
**Depends on**: Phase 26 (its pre-classification record in `bench/RESULTS.md` is the baseline the
migrated run is read against). Date-gated, so it is last and cannot be scheduled: the rollout
runs 2026-10-19 → 2026-11-19. Phases 27 and 28 land through CI on `ubuntu-latest`, so the first
migrated run may come from one of their PRs — read each such run's `Set up job` `Image:` line at
ship so the first 26.04 run is not missed; a red migrated run on a phase PR is a
stop-and-ask, not a fix.
**Requirements**: REQ-ubuntu26-classified-on-migration
**Close condition (discretionary, like v0.5's Phase 24)**: if no `ubuntu-latest` run names 26.04
by the time the human calls the milestone close, this phase closes `Closed — trigger not fired`
and the milestone closes with the item `active`. The Progress row says so; STATE.md's Roadmap
Evolution gets a dated line; the criteria below are marked not applicable; the debt item
(`2026-10-10-ubuntu-latest-migrates-to-ubuntu-26-on-19-october.md`) stays `active` with its
trigger restated (the first `ubuntu-latest` run whose `Set up job` names 26.04, Phase 26's
record attached); and REQ-ubuntu26-classified-on-migration moves from the Traceability table to
REQUIREMENTS.md's Future Requirements by an explicit edit with the human, so it is neither
orphaned silently nor reported complete. This phase never holds Phases 26–28 or the milestone
close unless the human chooses to wait.
**Success Criteria** (what must be TRUE; not applicable when closed on the condition above):

  Not applicable: closed 2026-10-22 on the close condition: no ubuntu-latest run named Ubuntu 26.04 by the milestone close (last read 2026-10-22T13:13Z, bench/RESULTS.md).

  1. The migrated run is classified from the whole log. The first `ubuntu-latest` run whose
     `Set up job` names 26.04 has its run id, head sha and `Image:` line recorded in
     `bench/RESULTS.md`, and all three jobs (`test (3.12)`, `vendor-bundle`, `image`) are read
     whole and classified against Phase 26's pre-classification, before any `ci.yml` edit.
  2. Green ends the item. A green classification is a dated reading in `bench/RESULTS.md` and
     the debt item is retired in the commit that records it (status, sha, `git mv`, INDEX row).
  3. Red goes to the human. A red classification lists the options with their cost and waits;
     `runs-on: ubuntu-24.04` is pinned only on the human's call, and no `ci.yml` edit lands
     before it.

**Boundaries**: one run is not the migration — the `Image:` line of each run in the window is
recorded; no fix before classification. **Phase close**: `git diff --exit-code v0.5 -- tests/regression/`
empty.
**Research flag**: No — the procedure is fixed by the debt file.
**Plans**: 1/1 plans complete

Plans:
**Wave 1**
- [x] 29-01-PLAN.md — read every `ci` run since 2026-10-19 from each job's own log, classify the first `ubuntu-latest` run on 26.04 whole against 26-02; green retires the item in the reading's commit, red goes to the human (pin with L46, or hold), not fired or pending goes to the human (wait, resumable; or the close condition)

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
  `docs/architecture/decision_log.md`, append-only (the next free id is `L44`).
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
| 26. Gate Fails With a Cause | v0.6 | 7/7 | Complete    | 2026-10-20 |
| 27. Ledger Tests and Harness | v0.6 | 6/6 | Complete    | 2026-10-20 |
| 28. Refuse the Bad Link | v0.6 | 8/8 | Complete    | 2026-10-22 |
| 29. Ubuntu 26 Final Reading | v0.6 | 1/1 | Closed — trigger not fired | 2026-10-22 |
