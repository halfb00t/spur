# The twin-selectors fix has not yet been read on a `main` run

Severity: must
Status: active
Date: 2026-10-15
Source: Phase 26 D-05, 26-03
Related files:
- `docs/tech_debt/resolved/2026-10-15-twin-selectors-step-reds-main.md` (the retired item)
- `tests/test_browser.py` (the "twin selectors" step, `DEBOUNCE_SETTLE_MS`)
- `bench/RESULTS.md` (`### Twin selectors (26-03)`)

## Context
Both reds of the twin-selectors step were `main` push runs (38347283201 at `94dfc19`, 38680454993 at `26ddd74`) whose
`pull_request` runs of the same trees were green. So neither the local runs of 26-03 nor the draft phase PR's run reads
the place and event where the step failed. D-05 asks for the post-merge `main` run to be read green; that run exists only
after `make pr.land` lands Phase 26, which is after the phase's verification, so no task inside the phase can perform it.
The mechanism was proved on the real app by the three-run `/api/info` response arms and the CX-05 control, recorded in
`bench/RESULTS.md`. The 20 local runs at `-n 8` are 20 of 20 green, which is consistent with the fix but does not separate
it from a fast host: the old step was not run 20 times here, and it failed on `main` CI (a runner about twice as slow) in 2
of 8 runs (`bench/RESULTS.md`, `### Twin selectors (26-03)`; the resolved twin item files the same runs under "Not proven by
this commit"). They are not proof that the `main` red is fixed.

## Why it matters
Until the `main` run is read, the mechanism is proved on the real app locally, not on the runner and event that failed. The
only proof that the `main` red is fixed is the post-merge `main` CI read below; the local arms prove the mechanism, and the
20 local runs prove nothing about the red. One green `main` run is consistent with the fix, not conclusive: at the observed
2 reds in 8 runs, a single run is green about 75 % of the time by luck. So this read is the check that the place that
failed no longer does, and further green `main` runs add to it.

## Next step
Trigger: the first `main` CI run after `make pr.land` lands Phase 26.

1. `gh run list --branch main --workflow ci --limit 1 --json databaseId,headSha,conclusion`
2. `gh run view {id} --log --job {test-job-id}`, grepped for `twin selectors`.
3. Append a dated reading to `bench/RESULTS.md` on the next phase branch.
4. Green: retire this item in that commit (Status, `Resolved in:`, `git mv` to `resolved/`, move the INDEX row).
   Red at the twin step: stop and ask (re-open the twin item), no patch.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
