# Dark-mode link text reads under WCAG AA's 4.5:1

Severity: must
Status: active
Date: 2026-10-29
Source: 33-10 planning measurement (the 33-UI-REVIEW contrast finding, found beside fix 3)
Related files:
- src/spur/static/style.css:27 (the dark `--accent`)
- src/spur/static/style.css:54 (`a { color: var(--accent) }`)

## Context
In dark mode `a { color: var(--accent) }` puts `#e0573f` on `--panel` `#1a1e23` for the header's API
link. Measured with the browser test's `_contrast` (the WCAG 2 formula) on 2026-10-29: 4.47:1, under
the 4.5:1 bar for 14 px text. Plan 33-10 fixed the dark primary button's text (`--accent-fg`, 4.85:1)
and left `--accent` alone on purpose: links and the invalid outline read it.

## Why it matters
The API link is the page's only link, and it is a hair under the bar in the dark theme. Small, but it
is a number the project measured and then shipped under the bar.

## Next step
Lighten the dark `--accent` until it reaches 4.5:1 on `--panel`; the dark button text then gains as
well, so re-read the step `primary button contrast`. Or give links a token of their own. Revisit when
the dark palette is next edited, or at the next UI review.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
