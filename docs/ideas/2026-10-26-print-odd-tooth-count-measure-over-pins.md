# Print M_Re for an odd tooth count, now that DIN 5480-2 rows confirm the formula

Date: 2026-10-26
Source: The Phase 31 follow-up that anchored DIN 5480-2:2006-05 rows. The human approved four rows by name and chose to keep the odd-count gate for now.
Related files:
- src/spur/shaft_calc.py (`ODD_Z_UNCONFIRMED`, `pin_measurement`)
- src/spur/din5480.py (`measure_over_pins`, the `cos(pi/(2*z))` factor)
- tests/test_din5480_anchors.py (`test_anchor_part_2_measure_over_pins_at_the_tabulated_pin`, the W 26x1.25x19 row)
- tests/test_shaft_calc.py (`test_an_odd_tooth_count_prints_the_pin_and_no_measure_over_pins`)

## Context
`derive_shaft` prints no M_Re for an odd tooth count (D-13). The gate waited for a DIN 5480 row that confirms the odd-count factor. A scratch comparison with the DIN 5480-2:2006-05 size tables now agrees with `din5480.measure_over_pins`. The parser read 700 inspection rows and misses a few at page breaks.
- 208 of 208 odd-count rows and 492 of 492 even-count rows agree to the printed third decimal.
- The comparison uses the tabulated pin D_M and the nominal thickness.
- Two odd rows, W 26x1.25x19 and W 30x2x13, are committed as approved anchors.

The human kept the gate anyway: removing it changes what an odd-count shaft prints.

## Why it matters
An odd-count shaft is a normal DIN 5480 part (about 30 % of the Part 2 rows read). Today it has a pin diameter with no measurement, so the user cannot check the part.

## Next step
Remove the odd-count branch in `pin_measurement` and retire `ODD_Z_UNCONFIRMED`. Make the odd-count test assert an M_Re. Note that the printed M_Re is at the tool's theoretical pin, not the tabulated D_M: Part 2's pin matches the theoretical pin rounded to 0.01 mm in only 16 of 700 rows. Decide this together with Phase 34's switch to the tabulated pin, so an odd-count M_Re is printed at the standard's pin the first time it appears.
