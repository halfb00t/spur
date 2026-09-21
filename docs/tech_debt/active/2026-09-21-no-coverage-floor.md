# No coverage floor in the gate

Severity: nice
Status: active
Date: 2026-09-21
Source: setting up the gate (L13)
Related files:
- pyproject.toml (`[tool.coverage.run]`)
- Makefile (`verify`)

## Context

`[tool.coverage.run]` is configured with `branch = true` and `source = ["src/spur"]`, but
nothing measures coverage in `make verify` and there is no `fail_under`. `pytest-cov` is
installed.

The reason is deliberate: a floor picked before measuring is a number, not a guarantee,
and a floor set too low is worse than none because it reads as approval.

## Why it matters

Low, today: 50 tests cover the geometry, the API, the CLI and the STL topology, and the
existing suite was written against a review that measured what it was testing. The risk
is drift — new code landing with no test and nothing noticing until someone looks.

## Next step

Run `pytest --cov` once, read the real number, set `fail_under` just under it, and add
`--cov --cov-fail-under` to the `test` target so it gates. Then this file moves to
`resolved/`.

Revisit when: immediately after one measured baseline run — this is a ten-minute item
being held only until the number exists.
