# `cli.md` claims exit 2 where `cmd_export` exits 1

Severity: must
Status: resolved
Date: 2026-09-28
Resolved in: docs(12-08): state the CLI's real exit contract in cli.md and pin it (D-13)
Source: Phase 10 planning — the D-14 exit-code conflict (10-CONTEXT.md D-14, amended 2026-09-28)
Related files:
- src/spur/cli.py:107 (unknown output extension: `raise SystemExit("error: …")`)
- src/spur/cli.py:111 (`BuildError` → `raise SystemExit(f"error: {exc}")`)
- docs/architecture/cli.md:35 ("Errors")
- tests/test_cli.py:159 (`test_unknown_output_extension_is_refused` asserts the message only)

## Context

`docs/architecture/cli.md` "Errors" says: *Exit 2 with `error: …` on stderr for bad
parameters and for an unknown output extension; `BuildError` becomes
`error: <kernel message>`.* Two of those three cases do not exit 2. A `SystemExit` raised
with a string message exits **1** (Python prints the string and uses status 1), and that is
what `cmd_export` raises both for an unknown output extension and for every `BuildError`.
Only argparse's parameter errors exit 2. The existing test for the extension case checks the
message, not the status, so the doc's claim has never been executed.

Surfaced while planning Phase 10: CONTEXT D-14 first said the empty tip-selection
`BuildError` "exits 2 on the CLI", copying the doc; the human decided 2026-09-28 to keep the
CLI's real contract (exit 1 for every `BuildError`) and amended D-14, and chose not to widen
Phase 10 to the doc fix.

## Why it matters

Someone scripting exports and branching on `$? == 2` for a bad extension, as the contract doc
tells them to, takes the wrong branch. The CLI contract is the doc's one job; a reader cannot
tell from it which exit status a kernel failure produces at all.

## Next step

Rewrite the "Errors" paragraph to state the three cases with their real statuses (parameter
error → 2 via argparse; unknown extension → 1; `BuildError` → 1), and add
`assert exc.value.code == "error: …"`-style status checks to the extension and `BuildError`
CLI tests so the doc cannot drift again. Revisit when `cmd_export`'s error handling or the
"Errors" section is next touched — or decide, as a logged `Lxx`, that build failures should
exit 2 too, which is the larger change D-14's first wording implied.

## Resolution (2026-09-30)

`docs/architecture/cli.md` "Errors" now states the three cases with their real statuses —
parameter error exit 2, unknown extension exit 1, `BuildError` exit 1 — instead of
claiming exit 2 for all three. No status changed (10 D-14's human decision stands): a
`SystemExit` raised with a string argument still exits 1; only argparse's own parameter
errors raise `SystemExit(2)`.

Pinned by three tests in `tests/test_cli.py`: `test_unknown_output_extension_is_refused`
now asserts `exc.value.code` equals the exact string;
`test_a_tip_chamfer_that_selects_no_tip_arcs_stops_the_export_and_writes_nothing` now
asserts `exc.value.code` is a string, not `2` (a `BuildError` exits 1); and the new
`test_an_unknown_output_extension_exits_1_from_the_real_process` runs the real
`python -m spur.cli export` subprocess end to end and asserts its own `returncode` is 1
with the sentence on stderr — the doc's claim executed once for real, not merely inferred
from `SystemExit`'s own `code` attribute, closing this file's own complaint.

`docs/architecture/cli.md`'s "Tests" section still says "4 tests" and is stale (it now
names three of the CLI's own dozens) — outside this debt's scope, noted as a tangent, not
fixed here.
