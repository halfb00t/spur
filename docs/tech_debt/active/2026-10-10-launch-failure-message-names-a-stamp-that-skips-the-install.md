# The launch failure message names a stamp that skips the install

Severity: nice
Status: active
Date: 2026-10-10
Source: phase 21 code review, finding WR-03 (`.planning/phases/21-browser-test-of-the-viewer/21-REVIEW.md`)
Related files:
- tests/browser_session.py:217 (the message: "`make test` runs the install stamp for you")
- Makefile:91 (`$(BROWSER): $(STAMP)` — the stamp `.venv/.browser` is touched after the install and depends only on the venv stamp)

## Context
`launch()` fails the test with "the headless shell is not installed ... `make test` runs the
install stamp for you". The stamp only re-runs when `pyproject.toml` changes. If
`.venv/ms-playwright` is removed (a cache clean-up) while `.venv/.browser` stays, `make test`
treats the shell as installed and the test fails again with the same advice. The message
also attributes every `Error` from `pw.chromium.launch()` to a missing install, including
missing shared libraries on Linux, where the fix is `playwright install --with-deps`, not a
reinstall.

## Why it matters
Cosmetic until someone hits it: the advice sends them in a loop once, then they read
Playwright's own error (printed after the advice) and fix it. No gate outcome changes.

## Next step
Either make the stamp depend on the shell's own marker (the revision directory under
`.venv/ms-playwright`) or have the message say `rm .venv/.browser && make test`; print
Playwright's error before the advice so a library error reads as one.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
