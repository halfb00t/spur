"""Regenerates `tests/regression/golden_requests.json`: `make golden.regen`, never anything else.

Trigger and mechanism: the file pins the exact `api/info` query string the real page sends
for each record of `tests/regression/pre_v0_2.json`, so that Phases 23-24 prove "the form
sends the same fields" by an empty diff on it instead of asserting it. It is rewritten only
on a deliberate change to what the form sends. This script drives the shipped page in a
real browser against a real `uvicorn`, through the same `serve`, `launch` and `sweep` the
browser test uses (`tests/browser_session.py`): one sweep, and no Python copy of the page's
`gearQuery()` that could drift from it.

A regen is its own commit, saying what moved and why (D-09); a feature commit never
touches the pin, and the browser test only reads it. On unchanged code a regen is a
byte-identical rewrite, so any diff is a real change.

Run as a script, so `tests/` is first on `sys.path` and `browser_session` resolves the way
`capture.py`'s `corpus` does. Not collected by pytest (no `test_` prefix).
"""

from __future__ import annotations

import json

from browser_session import GOLDEN_PATH, fixture_hashes, launch, serve, sweep
from playwright.sync_api import sync_playwright

REGENERATE = (
    "Rewrite only with `make golden.regen`, in its own commit stating what moved and why "
    "(D-09) -- never as part of a feature commit."
)


def main() -> int:
    hashes = fixture_hashes()
    # The sweep aborts the STL route and builds nothing, so the pool never starts a worker
    # and the group floor `serve` checks at teardown does not apply.
    with serve(floor_applies=lambda: False) as base, sync_playwright() as pw:
        browser = launch(pw)
        try:
            sent = sweep(browser.new_page(), base, hashes)
        finally:
            browser.close()
    assert len(sent) == len(hashes), f"swept {len(sent)} of {len(hashes)} records"
    GOLDEN_PATH.write_text(
        json.dumps({"records": sent, "regenerate": REGENERATE}, indent=2, sort_keys=True) + "\n"
    )
    distinct = len(set(sent.values()))
    print(f"wrote {len(sent)} records ({distinct} distinct queries) to {GOLDEN_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
