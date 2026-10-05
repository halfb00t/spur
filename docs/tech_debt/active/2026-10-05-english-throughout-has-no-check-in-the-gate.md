# The English-throughout rule has no check in the gate

Severity: nice
Status: active
Date: 2026-10-05
Source: PR #21 — translating `docs/HOW_TO_DEVELOP.md`, the last Russian-language document
Related files:
- AGENTS.md ("English throughout: identifiers, comments, commits, PR titles")
- Makefile:50 (`verify:` — the step list has no language check)
- Makefile:68 (`no-fake-done` — the neighbouring text scan, and its macOS caveats)
- docs/tech_debt/active/2026-10-05-no-fake-done-scan-is-blind-on-macos.md (same class:
  a text scan that silently matches nothing on the dev host)

## Context
`AGENTS.md` states the rule; nothing enforces it. `docs/HOW_TO_DEVELOP.md` — the human's
guide, pointed to from `AGENTS.md` and read by every onboarding agent — was Russian
(182 of 255 lines) from its creation until `cd1eddc` (PR #21), and no check ever flagged
it. The gsd intel described it as "in Russian" for the same span.

Finding the residue during PR #21 took three attempts, two of which reported "clean":

- `grep -P '[\x{0400}-\x{04FF}]'` — macOS BSD grep does not implement `-P`; with stderr
  discarded, the pipeline reported no matches for a repository that had ~10,000 Cyrillic
  characters.
- `rg '\p{Cyrillic}' .` — ripgrep skips dot-directories by default, so `.planning/` (91
  lines across 20 files) was never scanned.
- `git ls-files -z | xargs -0 rg -l '\p{Cyrillic}'` — the enumeration that reported
  honestly.

86 lines in 18 closed-milestone records under `.planning/milestones/` still quote the
old Russian text as edit anchors and grep probes. PR #21 kept them as historical record,
so any check has to exclude that tree.

## Why it matters
Honour-system only: the rule's one real violation lasted the project's whole life and
was found by a reader, not by the gate. Low stakes — prose language, not the part — which
is why this is `nice`, but the same "a scan that reports clean when it did not look" shape
as the `must` item above, and a 0.05 s check closes it.

## Next step
Add one step to `verify`, next to `no-fake-done`: enumerate with `git ls-files -z`,
exclude `.planning/milestones/`, fail with the file list when any tracked file contains a
character in U+0400–U+04FF. Measured on 2026-10-05 over 619 tracked files: 0.03–0.05 s
with `rg -l '\p{Cyrillic}'`, 0.06 s with a Python stdlib `re` scan over the bytes. Prefer
the Python form — `rg` on the GitHub runner is unverified, and macOS `grep -P` is the
trap above. Prove it with a staged probe file the way the `no-fake-done` item prescribes.
Scope it to Cyrillic, the one script that has actually occurred: a general "non-ASCII
letters" rule would false-positive on `×`, `—`, `µ`, `Ø`, `√` and Greek `α` that this
codebase uses legitimately (8,064 em-dashes, 432 `×` at the time of filing). Revisit when
a non-English line next lands in a tracked file, or when `no-fake-done` is next edited.
