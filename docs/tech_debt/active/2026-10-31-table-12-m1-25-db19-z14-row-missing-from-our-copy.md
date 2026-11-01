# Table 12's m=1.25 d_B 19 z 14 nominal row is not printed in our copy of DIN 5480-2, so the table file has 720 size rows, not 721

Severity: must
Status: active
Date: 2026-10-31
Source: 34-14 (the two reads of Part 2 against each other): both reads left the key out by the exactly-once rule, and the human settled it from the page: the row is not printed in the copy and there is no other source, so it stays out.
Related files:
- scripts/din5480_tables_tool.py (`EXPECTED_COUNTS["sizes"]`, 720)
- tests/test_din5480_tables_tool.py (`test_the_expected_counts_are_the_standards_shape`)
- .planning/phases/34-fit-tables-and-tolerance-window/investigation/34-14-disagreements.log (the key, by location)
- docs/tech_debt/resolved/2026-10-26-din5480-anchor-rows-beyond-part-1-are-missing.md (the earlier scratch comparison that met the same page)

## Context
Part 2 module 1.25, Tables 12 and 13 (pages 18 and 19). Page 19 (inspection) prints the key d_B 19 z 14 once. Page 18 (nominal) prints no row for it; it prints the d_B 20 z 14 row twice. The human, who holds the copy, settled it: the d_B 19 z 14 nominal row is not printed, there is no source for it, leave it out. The d_B 20 z 14 key takes the single printed row. A size row carries the nominal page's form diameter as well as the inspection page's pin and M1, so no row is built from page 19 alone and no value is supplied from anywhere else (L08).

## Why it matters
A shaft at W 19x1.25x14 gets the off-the-tables tier: no tolerance window, a warning that DIN 5480-2 does not list the size, the theoretical pin. The standard may list it; our copy does not show it. The file, `EXPECTED_COUNTS` and anyone reading "721 rows" in older notes are off by this one key.

## Next step
Revisit when a second copy of DIN 5480-2 or the publisher's corrigendum becomes available: read the key from it, add the row to both reads, and set `EXPECTED_COUNTS["sizes"]` back to 721.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
