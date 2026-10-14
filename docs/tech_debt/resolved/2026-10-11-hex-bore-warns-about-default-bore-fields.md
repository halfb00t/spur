# A hex bore warns that the default bore_d and bore_flat are ignored, on every hex link

Severity: nice
Status: resolved
Date: 2026-10-11
Resolved in: fix(calc): name only the hex-ignored bore fields set away from their defaults
Source: Phase 23 discuss-phase (`.planning/phases/23-conditional-form-fields/23-CONTEXT.md`) and REQUIREMENTS.md "Form follow-ups (v0.5.x)"
Related files:
- src/spur/calc.py:1166 (the "Hex bore replaces the round profile: ... ignored" sentence)
- src/spur/params.py:134 (`bore_d` default 9.0) and src/spur/params.py:137 (`bore_flat` default 8.0)
- tests/test_browser.py, the `warning rendered` step (its `bore_hex=6` link; a step name does not rot as a line number does)

## Context
`?bore_hex=6` answers `Hex bore replaces the round profile: bore_d (9 mm) and bore_flat
(8 mm) are ignored.` because the defaults are 9 and 8 (L05 keeps them), so every hex link
warns about values nobody set (PITFALLS M-7). Since L41 the form also dims both fields with
`Needs Hex bore A/F = 0`.

## Why it matters
A warning on every hex part trains users to skip warnings, which is where L08 puts what
could not be computed honestly.

## Next step
A `calc` change, never a filter in `app.js`: name only the bore fields the request set. Two
candidates for the human: `model_fields_set`, or a value that differs from its default. It
rewrites `warnings` for every hex link that omits them, and the `warning rendered` step's
`bore_hex=6` expectation (no fixture record sets `bore_hex`; re-check at the time).
Trigger fired: the selector shipped in 470b78a (choosing Hex leaves bore_d and bore_flat at their
defaults, so every selector-made hex part warns); fix as a /gsd-quick before Phase 25's reading.

## Resolution (2026-10-14)

- The rule: `derive()` names `bore_d` and `bore_flat` under a hex bore only when the value
  is non-zero and differs from the schema default, read from the model as
  `type(p).model_fields[name].default`. The human chose it at dispatch over
  `model_fields_set`, which `app.py`'s `_gear` loses (it rebuilds `GearParams` from a full
  `model_dump`) and which pydantic equality would let split the build caches' keys. Blind
  spot: an explicit value equal to its default is silent. L27 carries the dated amendment.
- Tests that moved, each written as a requirement and seen red first:
  - `tests/test_calc.py`: the parametrized hex test became
    `test_a_hex_bore_names_only_the_round_fields_set_away_from_their_defaults`, nine
    cases, and the named cases now require the hex sentences to equal `[expected]`.
  - The 48 hex rows of the composition test (`tests/composition.py`): the sentence
    constant was deleted, because a hex bore at the defaults implies no warning.
  - `tests/test_api.py`: the plain hex link answers no hex sentence, and
    `bore_hex=6&bore_flat=3` names exactly bore_flat.
  - `tests/test_cli.py`: the README's `--bore-hex 6` example now warns nothing, and the
    CLI/API parity test sets `--bore-d 12` so it still compares the D-02 sentence.
  - `tests/test_browser.py`: the `warning rendered` step follows `bore_hex=6&bore_d=12` and
    prints `[2, 1, 0]` warnings per link.
- Relation proofs (`tests/test_relations.py`): red before the adjustment were exactly three
  tests (the reverse scan on its empty-scan guard, the driver check at bore_d 9, and the
  dropped-field meta-test). The reverse scan now runs on a base holding every non-zero
  numeric default one schema step off it and sees 1 "ignored" sentence, as at HEAD; the
  driver check probes one schema step off a non-zero default; the meta-test is
  parametrized over spoke_fillet, bore_d and bore_flat, so dropping any of them from the
  declared set turns the scan red. Red before the calc change in Task 1: 57 failed.
- `pre_v0_2.json` and `golden_requests.json` are unchanged (`git diff --exit-code` clean
  after every task). No fixture record sets `bore_hex`.
- Collected tests: 1311 before, 1317 after.
- `make verify`: `1317 passed in 185.40s (0:03:05)`, coverage 97.99 % against the floor of
  96, ruff and mypy clean, import contracts 5 kept, 0 broken.
- Not done here: 24-REVIEW IN-04's other half, naming the fields by their form titles
  ("Bore Ø", "D-flat") instead of snake_case, was not in the locked scope, and the sentence
  still says `bore_d`/`bore_flat`. It is filed as
  `docs/ideas/2026-10-14-hex-warning-names-fields-by-form-title.md`.
