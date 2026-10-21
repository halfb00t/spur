# tip_chamfer_effective prints 0.0 for a chamfer that was not cut, because its null-gate reads the request

Severity: must
Status: resolved
Resolved in: fix(28): print no tip chamfer when none is cut -- log L45 (gsd/phase-28-refuse-the-bad-link)
Date: 2026-10-21
Source: 10-REVIEW IN-02, triaged in Phase 28 (D-13)
Related files:
- src/spur/calc.py:1294

## Context
`derive()` builds `tip_chamfer_effective=r3(tch) if p.tip_chamfer > 0 else None` (`src/spur/calc.py:1294`). The gate
reads the request (`p.tip_chamfer`), not the applied value `tch`. Measured in Phase 28 on this tree:

```
derive(GearParams(tip_chamfer=0.0004)).tip_chamfer_effective  ->  0.0
    warning: "Tip chamfer 0.0004 mm is below the 0.001 mm resolution it is cut at and was not cut."
derive(GearParams(tip_chamfer=0.0)).tip_chamfer_effective     ->  None
```

So a chamfer that was asked for and not cut prints `0.0`, beside a warning that says it was not cut, while no chamfer
at all prints `null`. Phase 10's WR-01 fix already made the case loud (the warning always ships); CR-01 fixed the
warning's text. What is left is only which value the field prints. No record in
`tests/regression/pre_v0_2.json` or `tests/regression/golden_requests.json` names `tip_chamfer`, so changing the gate
moves no pinned record today.

## Why it matters
A printed value (L08: a number the tool prints is a number someone will cut metal to). `0.0` for a chamfer that was
not cut can be read as "a chamfer of zero was cut"; `null` reads as "no number". Which is more honest is a judgment
about the field's contract, not a bug with an obvious answer, which is why Phase 28 did not change it.

## Next step
A decision for the human, not taken here: either fix it under a new Lxx (gate on the applied `tch`, so the unapplied
case prints `null`), with its own `make fixture.regen` commit if any record moves, or keep the current output and log
the reason. Revisit at that decision, or at the next phase that touches `tip_chamfer` or `derive()`'s printed fields.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
