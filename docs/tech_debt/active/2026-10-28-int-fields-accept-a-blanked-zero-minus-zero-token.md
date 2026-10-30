# An int field accepts `0-0`, a token the number box blanks

Severity: must
Status: active
Date: 2026-10-28
Source: Phase 33 code review IN-01 (`.planning/phases/33-interfaces-and-parity/33-REVIEW.md`), reproduced by the execute-phase orchestrator; deferred by the human at `/gsd-validate-phase 33`
Related files:
- src/spur/app.py (the as-written dependency, L49 rule A1)
- tests/number_box_tokens.py (the 91-token table)
- tests/test_number_as_written.py

## Context
L49's as-written rule (A1: outer whitespace, `_`, a leading `+`, a trailing `.`) was pinned
against the 91 tokens 33-01 probed. Pydantic 2.13.5 parses `"0-0"` and `"00-0"` as the int `0`
(`TypeAdapter(int).validate_python("0-9")` is `-9`), and Chromium's number box shows both blank.
Measured on 2026-10-28 against `/api/info`:

- `spoke_count=0-0` → 200, `hole_count=0-0` → 200, `hole_count=00-0` → 200
- `teeth=0-0` → 422 (bound), `spoke_count=0-9` → 422 (`greater_than_equal`), `1-1`/`2-0` → 422 (`int_parsing`)

So L49's claim "no blanked token gets a 200" is false for two tokens on the two int fields whose
lower bound is 0. The table has no token with an interior minus between digits, so the walker
test cannot see it.

## Why it matters
Today the built part is the default part, because `spoke_count` and `hole_count` both default
to 0 — the only value these tokens can reach without tripping a bound. Nobody gets a different
part than the blank box implies. The day either default moves off 0, or an int field with a
negative lower bound is added, a link carrying `0-0` builds a part the page cannot show: the
WR-02 class this phase closed.

## Next step
Revisit when L49's rule is next touched, an int field's default moves off 0, or an int field
with a lower bound below 0 is added. Then: add `Token("0-0", True)` and `Token("0-9", True)` to
`tests/number_box_tokens.py` (re-probe Chromium for both), watch
`test_every_blanked_token_is_refused_and_no_held_token_is_by_the_rule` go red, and extend the
rule to refuse a minus after a digit that does not follow an exponent `e`/`E`.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
