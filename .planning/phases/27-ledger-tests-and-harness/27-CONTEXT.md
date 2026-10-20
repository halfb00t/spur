# Phase 27: Ledger Tests and Harness - Context

**Gathered:** 2026-10-20
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase makes the tests that guard the ledger unable to pass vacuously and the browser harness unable to
misdescribe itself. It delivers five requirements: REQ-slug-totality-guarded, REQ-failed-build-name-isolated,
REQ-stop-group-signals-first, REQ-group-floor-recorded-true and REQ-launch-message-true. It also fixes the info
findings listed under "Rides with this phase" in ROADMAP.md, in the files this phase touches, and starts a draft
triage table.

The roadmap's four success criteria, its boundaries and its phase-close rule are fixed. This file records only
the decisions the roadmap left to this discussion and the defaults taken around them. No new `GearParams` field.
`src/spur/` changes only at the one `model.py` line D-03 approves. `tests/regression/` stays byte-identical to
`v0.5`.

</domain>

<decisions>
## Implementation Decisions

### Group floor (REQ-group-floor-recorded-true)
- **D-01:** `MIN_GROUP_MEMBERS` stays `3`, with a comment-only fix. The comment at `tests/browser_session.py:49`
  names the members `ps` observed: uvicorn, `multiprocessing.resource_tracker` and one spawned worker on
  sequential builds, with any Linux difference recorded as read (D-05). The floor is still the kill's
  non-vacuity check: 3 live members before, 0 after. No second concurrent build is forced, and members are not
  matched by command. This answers the debt item's open "then decide whether the floor should name the tracker
  explicitly, or whether a second concurrent build should be forced" with neither.
- **D-02:** A dated correction goes under each of the two `bench/RESULTS.md` rows that say "3 (uvicorn and two
  pool workers)" (macOS row ~4768, ubuntu-latest row ~4902). No reading is rewritten:
  `git diff --numstat v0.5 -- bench/RESULTS.md` reports 0 deleted lines.

### 19 IN-01/02 in `model.py`
- **D-03:** Yes, the milestone touches `src/spur/model.py`. `_build` asks `root_mode` once (`model.py:773`), and
  `_chamfer_tips` receives that `rm` and passes it to `tip_chamfer_effective(p, rm)` (today `model.py:636` calls
  it without `rm` and re-solves the curve on a chamfered trochoid build). The "one answer" comment becomes true.
  This is the milestone's only `src/spur/` change. — **Reversibility:** reversible — a signature change to one
  private function and its two call shapes.
- **D-04:** Two test patches change shape with D-03, not one as the roadmap says:
  - `tests/test_model.py:899` patches `spur.model._chamfer_tips` with a 3-argument lambda.
  - `tests/test_model.py:926` patches `spur.model.tip_chamfer_effective` with `lambda _p: 2.9875`. It breaks if
    `rm` is passed positionally.

  The proof that nothing else changed is the 44-record fixture staying byte-identical
  (`git diff --exit-code v0.5 -- tests/regression/`) and the existing chamfer tests staying green. No call-count
  test: it would pin a private detail, not behaviour. The IN-02 bench half (`bench/trochoid_part.py` reads
  `rm.curve`, imports the test helpers instead of near-copies, drops the stale "does not exist until 19-04"
  paragraph) and `_host_state`'s `CalledProcessError`/`FileNotFoundError` catch ride in the same change, as the
  roadmap and the debt item's next step say.

### Linux member listing
- **D-05:** The Linux `ps -o pid=,pgid=,command=` listing of the live group comes from **one throwaway CI run**.
  It is a temporary harness print on a throwaway PR whose workflow runs only the browser test with `-s -n0`, in
  the shape of 26-02's Ubuntu pre-classification. The listing is read from that run's whole log, the comment
  cites the run id, image and date, and the PR is closed unmerged. No permanent harness print, summary hook or
  CI artifact.
  - Why not a print in the harness: pytest captures a passing test's output and `make verify` runs without `-s`.
    Under xdist the output stays in the worker. A green CI log never shows a print; Phase 26's `twin selectors:`
    lines were absent from both post-merge `main` logs (`bench/RESULTS.md`, "The D-05 post-merge read
    (2026-10-20)").
  - The macOS listing is a local run, read the same way. The debt item flags its member set as the reviewer's
    listing plus the CPython explanation, not the orchestrator's (`ASSUMPTION:` in the item). Both listings are
    taken before the comment is written.

### Carried from the roadmap (locked, not re-asked)
- `slug()` totality: a seeded test, milliseconds, in the commit slice. Draws are stratified to reach every
  reachable refusal reason, with each bucket asserted non-empty. `bracket degenerate` and `curve invalid` are
  forced by patching and labelled forced. It is seen red against a raising `_junction` and a raising
  `_root_curve`, both recorded. `make verify.fast` stays under L36's 30 s.
- The failed-build name test: `_EXPORTS` is replaced per test by monkeypatching a fresh `_BlobCache`
  (`src/spur/app.py:46`, `:88`). It is seen red with the cache pre-seeded under the old code.
- `stop_group`: it signals the group before any `ps` read and before any `proc.poll()`/`wait()`. A failed `ps`
  fails the teardown as "survivors unknown" with the group already signalled. The SIGTERM grace and the
  leader-only-break red (row 21-01) are kept. A sub-second unit test in a file whose name has no `browser`
  proves both paths and cleans up its own group.
- The launch message: text-only. It names a command that installs the browser when the stamp is present but the
  browser is not, and keeps the literal `playwright install --only-shell chromium`
  (`tests/test_browser_pins.py:34`).
- 22 IN-03 is a dated amendment to L40, not a rewrite. Every new guard test is seen red once and the red is
  recorded.

### Taken at plan-phase (2026-10-20, from 27-RESEARCH.md Open Questions)
- **D-06:** `group_members`, `_signal_group`, `stop_group` and `_log_tail` move to a new `tests/process_group.py`,
  in their own commit before the reorder. The `stop_group` unit test (`tests/test_process_group.py`) imports it
  with a fake `group_members`, so it runs in `make test-image` (the image has neither playwright nor `ps`). No new
  `--ignore`.
- **D-07:** 19 IN-02's bench half does only the cheap part: `bench/trochoid_part.py` reads `rm.curve` and drops the
  stale "does not exist until 19-04" paragraph, plus the `_host_state` catch. Replacing the near-copies with the
  test helpers is recorded `skipped` in the triage table, with the reason: they differ in error type (assert vs
  `ValueError`), sample count (fixed 400 vs a `samples` parameter) and signature. This narrows D-04's last
  sentence.
- **D-08:** Only the failed-build name test gets the fresh-`_BlobCache` fixture. The three sibling tests
  (`tests/test_api.py` ~:1255, :1322, :1357) keep the unique-teeth convention.
- **D-09:** The new launch-failure text gets one pin in `tests/test_browser_pins.py`, seen red against the old
  text and recorded.

### Claude's Discretion
- The seed, draw count and stratification method for the slug test, within the millisecond budget.
- The throwaway PR's exact workflow edit for D-05, provided it changes only what runs, adds no fix and is closed
  unmerged.
- Which `test_model.py` patch form replaces each lambda in D-04 (for example `lambda _p, _rm=None: 2.9875`),
  provided each still patches the same name.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope
- `.planning/ROADMAP.md` § "Phase 27: Ledger Tests and Harness": goal, the 4 success criteria, rides-with list,
  boundaries, phase close.
- `.planning/REQUIREMENTS.md` lines 68-90: the five REQ-IDs.

### Debt items this phase retires
- `docs/tech_debt/active/2026-10-15-slug-totality-is-not-guarded-in-the-gate.md`
- `docs/tech_debt/active/2026-10-15-failed-build-name-test-depends-on-cache-order.md`
- `docs/tech_debt/active/2026-10-10-stop-group-reads-ps-before-it-signals.md`
- `docs/tech_debt/active/2026-10-10-group-floor-of-3-is-not-two-pool-workers.md`: D-01 answers its open
  question.
- `docs/tech_debt/active/2026-10-10-launch-failure-message-names-a-stamp-that-skips-the-install.md`
- `docs/tech_debt/active/2026-10-09-phase-19-review-info-findings-deferred.md`: IN-01, IN-02 and the
  `_host_state` half of IN-04 (D-03, D-04). The IN-04 `root_fillet` label is Phase 28's
  (REQ-root-fillet-label-follows-root).

### Locked decisions
- `docs/architecture/decision_log.md`: L36 (the commit slice and its 30 s), L40 (the slug's `_trochoid` rule; 22
  IN-03 amends it, dated), L05/L26 (the fixture), L08, L39 (the browser test in `make verify`).

### Precedent for D-05
- `.planning/phases/26-gate-fails-with-a-cause/26-02-SUMMARY.md`: the throwaway-PR pre-classification shape.
- `bench/RESULTS.md` "The D-05 post-merge read (2026-10-20)": captured output is absent from green CI logs.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tests/browser_session.py` `group_members(pgid)`, `_signal_group`, `stop_group`: the `stop_group` reorder
  (signal before the first `group_members`) happens here. `group_members` uses `check=True`, so a failed `ps`
  raises today, before any signal.
- `src/spur/app.py` `_BlobCache`: a fresh instance per test is the replacement for `_EXPORTS`.
- `src/spur/params.py:267` `slug()` and `calc.root_mode`: the slug test asserts the `_trochoid` suffix against
  `root_mode(...).mode`.

### Established Patterns
- Dated corrections under `bench/RESULTS.md` readings, never rewrites (L08, append-only).
- Comments carry the measurement, host, image and date that forced the value (see the `BUILD_WAIT_MS` and
  `PNG_RATIO_BAR` comments beside `MIN_GROUP_MEMBERS`).
- A debt item is retired in the commit that fixes it: `Status: resolved`, `Resolved in:`, `git mv` to
  `resolved/`, and the INDEX row moved.

### Integration Points
- The `*browser*` glob is both the no-skip scan's and the commit slice's exclusion. The new `stop_group` test
  must live in a file whose name avoids it, or it leaves the commit slice.
- `tests/test_model.py:899`, `:926`: the D-04 patches.

</code_context>

<specifics>
## Specific Ideas

The human picked the recommended option in every area. In the Linux-listing area the first recommendation (a
permanent harness print) was withdrawn in the discussion, because captured output never reaches a green CI log.
The human then chose the throwaway CI run.

</specifics>

<deferred>
## Deferred Ideas

None. The discussion stayed within phase scope.

</deferred>

---

*Phase: 27-ledger-tests-and-harness*
*Context gathered: 2026-10-20*
