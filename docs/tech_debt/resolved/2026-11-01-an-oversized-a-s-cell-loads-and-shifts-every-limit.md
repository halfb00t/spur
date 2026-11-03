# An oversized A_s cell loads and shifts every limit printed from it

Severity: must
Status: resolved
Date: 2026-11-01
Resolved in: 2fa48b8 fix(34.1-04): cap each A_s cell at 60 micrometres per millimetre of its column's module (D-01)
Source: Phase 34 code review (34-REVIEW.md WR-03, the part left after the fix in `d299fe3`)
Related files:
- src/spur/din5480_tables.py (`A_S_CAP_UM_PER_MM`, `problems()`)
- src/spur/shaft_calc.py

## Context
`d299fe3` refuses a tolerance row with a negative T_act or T_eff, which closes both probes WR-03
reproduced. The review's third probe was still open: the only bound on a Table 7 upper deviation was
`abs(v) <= UM_LIMIT` (1000 um), so one `A_s` cell transcribed as 900 um instead of a two-digit value
loaded clean, and the default shaft then printed an s_vmax of 3.513 against a nominal 2.613 (the
review's probe, run on the synthetic fixture).

The review's suggested guard, refusing a file whose derived `s_min <= s_max <= s_vmax` fails for a
listed size, is withdrawn (D-03). Besides needing the shaft maths in the loader, which `shaft_calc`
already imports, it cannot see this fault: `A_s` moves s_min, s_max and s_vmax together, so their
order holds with the slip in them. A startup check above the loader would not fix that, so none was
added; `src/spur/cli.py` and `src/spur/app.py` are unchanged. A rule on a deviation's sign was
considered and not added either (D-02): the letters' sign conventions are an assumption the copy was
not checked for, and a sign slip stays the two-reads diff's.

## Why it matters
Every limit printed for the affected column moves by the slip, and each one is a number someone cuts
metal to (L08). The two-reads diff (D-08) catches a slip made in one read only; a slip made the same
way in both reads, or in the file after assembly, loads.

## Next step
Done: see Resolution.

## Resolution
`problems()` refuses an `A_s` cell whose magnitude exceeds `A_S_CAP_UM_PER_MM` (60, D-01) times the largest `module_max_mm` of the column rows that select that cell's column, naming the deviation letter and the column and no value. The human chose 60 from an aggregate reading of the real file, with headroom over it. The cap is coarse on purpose and one global constant: it catches a tenfold slip, which still loads under `UM_LIMIT`. The residual D-01 accepts is that a tenfold slip on a cell whose ratio is small stays under the cap and loads; the two-reads diff stays the primary guard and no per-column cap was taken.

`UM_LIMIT` stays as the outer belt (D-04): wherever a column has a row the cap is at most 60 times DIN 5480-2's largest module, tighter than `UM_LIMIT`, so `UM_LIMIT` alone bounds a cell of a column no row selects.

The case `A_s ten times its cell, under the micrometre limit` (the fixture's f cell in column 1 at ten times its value) was seen failing with the cap's append replaced by `pass` (`DID NOT RAISE`; log `.planning/phases/34.1-address-tech-debt-din-5480-table-loader-and-gear-guard/investigation/34.1-04-red-a-s-cap.log`). The synthetic fixture is unchanged and loads clean under the cap.
