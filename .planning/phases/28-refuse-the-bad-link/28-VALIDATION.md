---
phase: "28"
slug: "refuse-the-bad-link"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-21"
---

# Phase 28 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Source: `28-RESEARCH.md` § Validation Architecture.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 (+ xdist 3.8.0, cov 7.1.0); Playwright sync API for the browser file |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `.venv/bin/python -m pytest --no-cov -n0 -q -p no:cacheprovider tests/test_api.py -k "shareable_link or every_key_the_ui or root_form_d_is_never or root_shape"` |
| **Browser run command** | `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q"` |
| **Full suite command** | `make verify` |
| **Estimated runtime** | quick ~2 s; browser ~23 s; full under the 300 s bar (L43) |

---

## Sampling Rate

- **After every task commit:** quick `test_api.py` command; plus the browser command whenever `app.js` or `test_browser.py` moved.
- **After every plan wave:** `make verify`.
- **Before `/gsd-verify-work`:** `make verify` green, `git diff --exit-code v0.5 -- tests/regression/` empty, triage grep empty.
- **Max feedback latency:** 30 seconds (browser run).

---

## Per-Task Verification Map

Filled by the planner, 2026-10-21. "Quick" is the quick run command above; "browser" is
`make test PYTEST_ARGS="tests/test_browser.py tests/test_browser_pins.py -n0 --no-cov -q"` with the summary read for
`N passed in` and no `N failed|error`. Every task also carries its own `<automated>` checks in its PLAN.md.

| Task | Requirement | Behavior | Test Type | Automated Command | Fails when | File Exists | Status |
|------|-------------|----------|-----------|-------------------|------------|-------------|--------|
| 28-01-1 (tracer) | REQ-bad-link-refused | the rejected map sends a token its control cannot hold; pinned tokens hold; the old pin goes red at its own step | static + browser (red record) | quick; then a check of `investigation/28-01-red-old-pin.log` | a pin or guard fails; the log has no non-zero exit, more than one failure, or a note other than `step: root_shape=bogus as today` | extend existing tuple | ⬜ pending |
| 28-01-2 | REQ-bad-link-refused | four new steps green; red with only `app.js` reverted | browser | browser; then a check of `28-01-green.log` and `28-01-red-new-pin.log` | any failed step; the red log not one failure noted `step: bad link refused`; a timing line missing; the fix not restored | step rewrite | ⬜ pending |
| 28-01-3 | REQ-bad-link-decision-logged, REQ-info-findings-triaged (26 IN-03) | L44 last and append-only; RESULTS sections; web-ui true; item retired; one D-07 commit | grep + git | the three `<automated>` lines of the task | L44 missing or not last; a deleted line in the decision log or RESULTS since v0.5; the item not moved; a D-07 file outside the commit | n/a | ⬜ pending |
| 28-02-1 (tracer) | REQ-root-fillet-label-follows-root | the label follows `root_form_d` on 26/27/23 teeth; red first; row-only diff; Phase 19 item retired | browser + git | browser; then a check of `28-02-red-label.log` and the commit's `app.js` diff | the step fails; the red log not noted `step: root_fillet label`; the diff touches a line other than the row | new assertions | ⬜ pending |
| 28-02-2 | REQ-info-findings-triaged (24 IN-01) | the stash comment true; one value write in the selectors section; idea filed | static + git | quick; the comment-only diff check | a second value write; a non-comment line changed; the idea or its INDEX row missing | ✅ | ⬜ pending |
| 28-02-3 | REQ-info-findings-triaged (24 IN-02, CX-03) | "Could not build the form" for an unknown group; red first; gate | browser | browser; then a check of `28-02-red-wording.log` | the step fails; the red log not noted `step: form build error`; the old wording survives | new step | ⬜ pending |
| 28-03-1 (tracer) | REQ-info-findings-triaged (27 IN-11) | comment-only, same AST as `0efc87c` | static | AST compare; `pytest tests/test_browser_pins.py` | the AST differs; the old sentence survives | ✅ | ⬜ pending |
| 28-03-2 | REQ-info-findings-triaged (26 IN-04) | durable cites first; the Phase 21 path no longer dangles | static | comment-only diff check; `pytest tests/test_hooks.py tests/test_no_fake_done.py` | a recipe line changed; a cite missing; the archived log absent | ✅ | ⬜ pending |
| 28-03-3 | REQ-old-info-findings-triaged (18 IN-07) | docstring-only, same AST as `v0.5` with docstrings stripped; gate | static | AST compare; `pytest tests/test_trochoid.py`; `make verify` | code differs from v0.5; the sentence absent | ✅ | ⬜ pending |
| 28-04-1 (tracer) | REQ-old-info-findings-triaged | two items filed; the Phase 10 ledger reads them | static | the Phase 10 check of the task | a row not `deferred`; `open:` not 0; a template field or INDEX row missing | n/a | ⬜ pending |
| 28-04-2 | REQ-info-findings-triaged, REQ-old-info-findings-triaged | 41 rows closed with evidence; vacuous five fixed; parked-wait trigger restated | static | the 41-row ledger check; the `\| open \|` grep | an unbacked cell; a vacuous-pass finding not fixed; not 41 rows read; an open row left | n/a | ⬜ pending |
| 28-04-3 | all | retiring shas named; phase gate | full | `make verify`; `git diff --exit-code v0.5 -- tests/regression/` | a sha not found by subject; a failed test; a fixture moved | ✅ | ⬜ pending |

Requirement-level map (from research):

| Requirement | Behavior | Test Type | Automated Command | File Exists | Status |
|-------------|----------|-----------|-------------------|-------------|--------|
| REQ-bad-link-refused | four bad links: token kept and sent, server text, field marked (mate: message only), no STL, no new triangles; edit/Reset clear | browser | `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q"` | step rewrite | ⬜ pending |
| REQ-bad-link-refused | generic over the schema; pinned `app.js` tokens hold | static | quick command (`-k shareable_link`) | extend existing tuple | ⬜ pending |
| REQ-bad-link-refused | valid links unchanged | browser + diff | golden sweep step; `git diff --exit-code v0.5 -- tests/regression/` | ✅ | ⬜ pending |
| REQ-bad-link-decision-logged | old pin red vs fix; new pin red with fix reverted; L44; debt retired; web-ui.md true | manual-with-record + grep | logs in `investigation/`; `grep -n '^## L44' docs/architecture/decision_log.md` | n/a | ⬜ pending |
| REQ-root-fillet-label-follows-root | hob → "Hob tip radius used"; radial/fallback → "Root fillet used" | browser | browser command | new assertions | ⬜ pending |
| REQ-info-findings-triaged / REQ-old-info-findings-triaged | no `\| info \| open \|` rows in scope | grep | `grep -rn '\| info \| open \|'` over the in-scope `*-REVIEW-DISPOSITION.md` prints nothing | n/a | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements (framework, harness and browser all ran green during research).

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Red-first record: old pin red against the fix, new pin red with the fix reverted | REQ-bad-link-decision-logged | The red runs are a one-time evidence record, not a standing test | Run the browser command in each state; save logs under `.planning/phases/28-refuse-the-bad-link/investigation/` |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
