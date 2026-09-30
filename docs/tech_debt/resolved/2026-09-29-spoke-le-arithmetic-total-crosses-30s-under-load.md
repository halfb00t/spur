# The heaviest spoke row's arithmetic total with Phase 10's tip-chamfer row crosses 30 s under load

Severity: must
Status: resolved
Date: 2026-09-29
Resolved in: docs(12-03): record the composed sweep's gate and resolve its two build-time debts (D-03, D-05)
Source: 11-06's Task 3 re-run (D-18's gate)
Related files:
- src/spur/params.py (`spoke_count`)
- bench/RESULTS.md ("Body cutout build and export time (Phase 11)" -- "### Re-run after
  the gate (lower-le)")

## Context
D-18's gate lowered `spoke_count`'s `le` from 200 to 40 (11-06-PLAN.md Task 2's human
decision), accepted on the rationale that 40 sectors would leave "~2 s margin" beside
Phase 10's 14.87 s tip-chamfer row when Phase 12 stacks both features on one gear. The
re-run measured the heaviest `le`-40 spoke row (module 10, `spoke_width` 0.4, both
recesses) at 18.52 s of `SPUR_BUILD_TIMEOUT`=30 s -- comfortably inside budget alone. But
this reading was taken under load average 32.17 at the run's start, the highest recorded
anywhere in this project's bench history and well past the "quiet" bar (>1.5) or even the
first run's own 5-10. The naive arithmetic total (18.52 + 14.87 = 33.39 s) crosses 30 s by
3.39 s -- not the ~2 s margin the accepted decision anticipated.

This is an arithmetic sum, not a real combined build (Phase 12 composes both features on
one gear and measures the actual cost, which need not equal the sum of two separate
single-feature builds); and the reading itself is plausibly inflated by the exceptional
load at capture time. Neither of those facts contradicts the gap -- they are reasons it
might not recur, not proof that it will not.

## Why it matters
If Phase 12's real composed build reads anywhere near this arithmetic total, a link
combining `spoke_count` near 40 with `tip_chamfer` near its own heaviest row would cross
`SPUR_BUILD_TIMEOUT` and return a 503/504 for a configuration the schema says is valid
(the same class of risk D-18's gate exists to catch, T-11-14).

## Next step
Re-measure the heaviest spoke row (module 10, `spoke_width` 0.4, `hub_d` 52, `rim_wall`
0.4, both recesses) on a genuinely quiet host (`uptime` load < 1.5) to separate the
load-inflation hypothesis from a real margin problem. If it still reads near 18 s quiet,
fold it into Phase 12's composed sweep explicitly rather than waiting for the general
composed measurement to surface it.

## Revisit when
Phase 12's composed sweep runs (it will measure the real total directly), or a
`BuildTimeout` is logged in production for a gear combining `spoke_count` near 40 with
another heavy feature.

## Resolution (2026-09-30)

Phase 12's composed sweep measured the real combined build this file's own "Next step"
asked for, rather than the arithmetic sum: the module=10 keyed-bore spokes row
(`spoke_count` 40, `tip_chamfer` 3, both recesses) read 32.03 s of `SPUR_BUILD_TIMEOUT`=30 s
on Run 4 (`bench/RESULTS.md` "### Against the single-feature baselines") -- close to, and
confirming, the naive arithmetic total this file recorded (18.52 s + 14.87 s = 33.39 s
crossed 30 s by 3.39 s; the real composed build crossed it by 2.03 s instead, -1.36 s from
the naive sum, not a load artefact). D-02 was superseded for this gate (`### Gate`): four
runs at loads 12.66 down to 1.54 all found the same four `spoke_count=40` rows over budget
within a roughly 2 s band that did not track load, so the human treated Run 4 as decisive
rather than waiting on a fifth quiet run.

D-03's probe (`### Gate probe`) found `spoke_count` 32 the largest count that keeps that
same row inside budget (29.41 s of 30 s; 33 read 30.11 s, over again). The human chose that
offer (12-03-SUMMARY.md, Task 2, verbatim: "lower-le: spoke_count 32 (Recommended)").
`spoke_count`'s `le` moved from 40 to 32 (`547214e`), and the re-run (`bench/RESULTS.md`
"### Re-run after the gate (lower-le: spoke_count 32)") confirms every row of the composed
sweep now reads inside 30 s -- heaviest 29.42 s of 30 s, 0.58 s of margin, the same pattern
that was over budget at `spoke_count=40`.

Decision: a lowered `le` on `spoke_count` (40 -> 32), the first offer D-03's order
prescribes.
