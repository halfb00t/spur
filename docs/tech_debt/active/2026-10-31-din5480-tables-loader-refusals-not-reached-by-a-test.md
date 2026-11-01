# The table loader's refusal paths are not all reached by a test: din5480_tables.py reads 93.48 % in the gate

Severity: must
Status: active
Date: 2026-10-31
Source: 34-17 (the gate delta): the coverage rows of `34-17-verify.log` show `src/spur/din5480_tables.py` at 238 statements, 13 missed, 8 branch parts missed, `93.48%`, and `src/spur/shaft_calc.py` at 2 missed; the line numbers come from `coverage report -m` on the `.coverage` file that run left.
Related files:
- src/spur/din5480_tables.py (lines 181, 245-246, 254, 290, 296, 303, 306, 344-345, 353-354, 358)
- src/spur/shaft_calc.py (lines 394 and 405, two `LimitReading` returns)
- tests/test_din5480_tables.py (`test_a_broken_row_refuses_to_load`, the parametrised broken-row cases)
- bench/RESULTS.md (`### The gate delta (34-17)`)

## Context
The three other shaft modules and `pool.py` read 100 % in the same run. The loader's checks exist so that a broken table file refuses to start the server and the CLI instead of degrading quietly (D-04). Twelve of its refusal lines are never executed by the gate: the DIN 5480-2 module-set check, the positive `m1_mm` check, the two column-count checks, the module-bounds check, the `d_b_over_mm` below `d_b_upto_mm` check, the two `OSError` paths (open and read) and the file-size cap. Line 181 is a `return None`. `shaft_calc.py` lines 394 and 405 are two `LimitReading` returns. The 96.0 % floor is on the total (`97.80 %`), so the gate is green.

## Why it matters
A check no test reaches can be deleted or broken without a red run, and the file it guards is the one every number the tool prints from the tables comes from (L08). The structural-check family was seen red once as a group in 34-02 by disabling `problems()`; that proves the group is called, not that each of its lines refuses what it says.

## Next step
Add one broken-file case per missing line to the existing parametrised test (or one `OSError` and one oversized-file case for the I/O lines), and one case each for the two `shaft_calc.py` returns, then see each red against its line removed. Revisit when the loader is next edited or the table file is next regenerated.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
