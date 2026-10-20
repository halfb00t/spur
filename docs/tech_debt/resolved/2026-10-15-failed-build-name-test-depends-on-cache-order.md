# A failed-build name test passes only while no other test downloads the same gear

Severity: must
Status: resolved
Resolved in: c47bfc4
Date: 2026-10-15
Source: phase 22 code review, finding WR-02 (`.planning/milestones/v0.5-phases/22-download-name-carries-the-root/22-REVIEW.md`); untriaged until the v0.5 milestone audit, filed at the human's call at the v0.5 close
Related files:
- tests/test_api.py:1296 (`test_a_failed_build_records_the_name_of_the_part_it_would_have_been`)
- tests/test_api.py:539 (`test_a_root_shape_link_is_served_with_the_root_it_cut`, same convention in its docstring)
- src/spur/app.py:88 (`_EXPORTS`, the module-level byte cache)

## Context
The test gets a 422 from its raising backend only if `spur.app._EXPORTS` holds no entry for
the request. Its isolation is a comment: the 25-tooth trochoid gear and the 33.5° tip-land
gear are "downloaded by no other test". A later test that downloads either at
`quality=preview` turns it into a 200, depending on order, and the per-process cache makes it
depend on xdist scheduling too.

## Why it matters
An order-dependent failure in the gate reads as a flake and costs a whole-suite rerun to
diagnose; the uniqueness rule is maintained by hand in two docstrings and nothing enforces it.

## Next step
Revisit when `tests/test_api.py` next gains a download test, or on the first run where this
test reads 200 instead of 422. The fix: make the cache key private by a field no other test
uses (for example `face_width=7.7`) in both rows, or clear `_EXPORTS` at the top of the test.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
