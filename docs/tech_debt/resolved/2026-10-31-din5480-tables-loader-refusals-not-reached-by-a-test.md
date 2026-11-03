# The table loader's refusal paths are not all reached by a test: din5480_tables.py reads 93.48 % in the gate

Severity: must
Status: resolved
Date: 2026-10-31
Resolved in: 7876797 test(34.1-03): the limit reading for a pin that misses the flanks; resolve the loader-refusals item (D-11)
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

## Resolution
Every listed line is now reached by a named case, deleted, or rewritten (line numbers as at e2299c4). From 34.1-01, each seen red with only its line disabled: `test_a_broken_row_refuses_to_load[module not one of the sixteen]` (245-246), `[m1 not positive]` (254), `[a deviation row one column wider]` (290), `[a class row one column wider]` (296), `[column module bounds reversed]` and `[column module bound not a DIN 5480-2 module]` (303), `[column d_B range reversed]` (306), `test_a_path_the_system_cannot_stat_refuses_naming_it` (344-345) and `test_fit_is_none_when_an_unchecked_document_names_a_missing_tolerance_row` (181). The file-size cap (353-354) is reached by `test_a_file_over_the_cap_is_refused_at_the_stat_before_it_is_opened`. `shaft_calc.py` 394 is reached by `test_a_pin_that_misses_the_flanks_at_a_limit_thickness_is_null_with_its_own_sentence`, seen red with its return removed; 405 was dead and was deleted under D-09. The read handler and post-read cap (357-358, 362) became the bounded read's handler and its one read-time check under D-10 (34.1-03 Task 2), reached by `test_a_read_error_after_the_stat_refuses_naming_the_path` and `test_a_file_that_grew_past_the_cap_after_the_stat_refuses`. The targeted coverage run (`investigation/34.1-03-coverage.log`) shows none of them missed: `din5480_tables.py` misses only the `if t.columns:` branch back to the sizes loop head and the tolerance row's micrometre line (`266->242, 283`, both reached in the gate by test files outside that run), and `shaft_calc.py` reads `100.00%`. The whole-gate 100 % reading is taken at 34.1-05 (D-12).
