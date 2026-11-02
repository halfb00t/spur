# `gear.unchanged` accepts any local `v0.6` tag, including a lightweight or moved one

Severity: must
Status: resolved
Date: 2026-10-23
Resolved in: 9653865 fix(34.1-02): gear.unchanged requires an annotated v0.6 that peels to 792b45c (D-06)
Source: Phase 30 code review, IN-02 (raised by the verifier as worth a follow-up)
Related files:
- scripts/gear_unchanged.py:84-87 (`ensure_tag`)

## Context
`ensure_tag` only checks that `v0.6^{commit}` resolves. `git tag v0.6` on HEAD, or a force-moved
tag, makes the check compare the tree with itself and read green.

## Why it matters
That tag is the whole baseline of the gear-safety proof (REQ-gear-unchanged-proof, L08's standing
rule). A self-comparison is a silent false green, which the module's own docstring says never
happens. It takes a local developer mistake, and CI fetches the tag from origin, so it is filed as
`must`, not `blocker`. Promote it if any CI path is found that can see a local tag.

## Next step
Assert the tag is annotated (`git cat-file -t v0.6` prints `tag`) and peels to `792b45c`, or that
the peeled commit is not HEAD and is an ancestor of HEAD. Add a scratch-repo test with a
lightweight tag at HEAD that must fail. Revisit when `scripts/gear_unchanged.py` is next touched.

## Resolution
`ensure_tag` now reads the tag by its full ref, `refs/tags/v0.6`, and refuses unless `git cat-file -t` on it prints `tag` and it peels to `BASELINE_SHA`, the full sha of `792b45c`; a deliberate re-baseline edits that one constant (D-06). There is no ancestor check. Reading the full ref means a branch named `v0.6` is never taken for the tag. Pinned by `test_a_lightweight_v0_6_tag_is_refused`, `test_a_moved_annotated_tag_is_refused` and `test_a_branch_named_v0_6_is_not_taken_for_the_tag`, each seen red with its check removed (logs under `.planning/phases/34.1-address-tech-debt-din-5480-table-loader-and-gear-guard/investigation/`).
