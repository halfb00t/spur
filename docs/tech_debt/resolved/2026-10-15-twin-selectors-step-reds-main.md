# The browser step "twin selectors" reds `main` CI with one extra request

Severity: must
Status: resolved
Date: 2026-10-15
Resolved in: fix(26): take the twin-selectors baseline after the link's own STL request and settle past the debounce
Source: v0.6 kickoff research (ARCHITECTURE.md, STACK.md); the two runs read by the orchestrator with `gh run view --log-failed`
Related files:
- tests/test_browser.py (the "twin selectors" step: the baseline `requests_before = len(seen)` and the failing assert; lines at filing: 1576 and 1611)
- `.planning/milestones/v0.5-phases/24-bore-shape-selector/` review finding CX-05 (same step)

## Context
`test_the_shipped_viewer_in_a_real_browser` failed on `main` twice, both at step
"twin selectors" with `AssertionError: twin selectors: 1 request(s) sent by two pending picks`:
run 38347283201 at `94dfc19` (Phase 24 squash, `assert 269 == 268`) and run 38680454993 at
`26ddd74` (the v0.5 close squash, carrying the `v0.5` tag, `assert 266 == 265`). The PR runs of
the same trees were green. Two of the last eight `main` runs are red on this step; no other
step failed in either run.

ASSUMPTION (ARCHITECTURE.md, from the two logs, no local reproduction): the baseline at
line 1576 is taken right after `goto()`, before the page's own STL request for the link has
arrived, so that request lands inside the window the assert counts. CI is ~2x slower than the
dev host, which would widen the gap.

## Why it matters
`main` CI is the record the `v0.5` tag points at, and it reads red on a defect in the test,
not the product. Every red that is "just the flake" trains readers to ignore red, which is
how a real regression gets merged.

## Next step
v0.6 REQ-twin-selectors-race-fixed: prove the mechanism with a delayed STL route (old step red),
take the baseline only after the link's own build request has been seen and the 350 ms
debounce has passed, fold in 24 CX-05 and 21 IN-04a, and retire this item in that commit.

## Resolution (2026-10-15)

The assumption above was half right and the lever was wrong. `app.js` runs `update()` directly at load (`app.js:643-644`),
so no 350 ms timer is pending at the baseline; `update()` fetches `/api/info` and only after that response fetches
`/api/model.stl` (`app.js:262-272`). The old baseline waited for the info request, so on a slow runner the STL request
landed after it, inside the counted window. The step now waits for the link's own `/api/model.stl` request
(`BUILD_WAIT_MS`), settles `DEBOUNCE_SETTLE_MS` (1 000 ms), takes the baseline, and settles again before the zero-request
assertion (24 CX-05). `_follow_link`'s `/api/info` wait carries `timeout=BUILD_WAIT_MS` (21 IN-04a). `src/` is untouched.

Proven in this commit, on the real app (`.planning/phases/26-gate-fails-with-a-cause/investigation/26-03-arms.md`, three
runs per arm, every log kept):

| Arm | Result |
|---|---|
| delayed (parked) STL route, old step | green 3 of 3 |
| parked `/api/info` released after the old baseline, old step | red 3 of 3: `twin selectors: 1 request(s) sent by two pending picks` (`assert 279 == 278`) |
| the same parked `/api/info`, new baseline | green 3 of 3 |

SC2's wording ("a delayed STL route makes the old step red") does not hold on the real app: the lever is the `/api/info`
response, after which the STL request is issued. The CX-05 control (a stray `input` event after the two picks): the old
assert-at-once step passes, the settled step is red, the stray `/api/info` request arriving 354 ms after its event. The
browser files read `5 passed`. The mechanism was located on the real app and fixed from that reproduction.

Not proven by this commit: the 20 local runs at `-n 8` (26-03 Task 3, recorded in `bench/RESULTS.md`
`### Twin selectors (26-03)`); the draft phase PR's CI read (26-07), supporting only, since the `pull_request` runs of both
red `main` trees were green; and D-05's post-merge `main` read, carried by the active item
`docs/tech_debt/active/2026-10-15-twin-selectors-fix-awaits-the-post-merge-main-read.md`.
