# An oversized A_s cell loads and shifts every limit printed from it

Severity: must
Status: active
Date: 2026-11-01
Source: Phase 34 code review (34-REVIEW.md WR-03, the part left after the fix in `d299fe3`)
Related files:
- src/spur/din5480_tables.py:285
- src/spur/shaft_calc.py

## Context
`d299fe3` refuses a tolerance row with a negative T_act or T_eff, which closes both probes WR-03
reproduced. The review's third probe is still open: the only bound on a Table 7 upper deviation is
`abs(v) <= UM_LIMIT` (1000 um), so one `A_s` cell transcribed as 900 um instead of a two-digit value
loads clean, and the default shaft then printed an s_vmax of 3.513 against a nominal 2.613 (the
review's probe, run on the synthetic fixture). The review's suggested guard, refusing a file whose
derived `s_min <= s_max <= s_vmax` fails for a listed size, was not added: it needs the shaft maths in
the loader, and `shaft_calc` already imports the loader, so the check would be circular.

## Why it matters
Every limit printed for the affected column moves by the slip, and each one is a number someone cuts
metal to (L08). The two-reads diff (D-08) catches a slip made in one read only; a slip made the same
way in both reads, or in the file after assembly, loads.

## Next step
Bound `A_s` by what Table 7 can hold rather than by the generic 1000 um limit (for example by the
letter's sign and a magnitude bound per module range), or run the derived-order check at startup from
a module that may import both the loader and `shaft_calc` (the CLI and app lifespan already sit above
both). Revisit when the loader is next edited or when a transcription is next redone.
