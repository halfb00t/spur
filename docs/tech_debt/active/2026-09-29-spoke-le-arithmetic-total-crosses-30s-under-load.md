# The heaviest spoke row's arithmetic total with Phase 10's tip-chamfer row crosses 30 s under load

Severity: must
Status: active
Date: 2026-09-29
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
