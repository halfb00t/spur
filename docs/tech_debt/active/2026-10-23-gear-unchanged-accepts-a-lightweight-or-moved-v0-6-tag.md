# `gear.unchanged` accepts any local `v0.6` tag, including a lightweight or moved one

Severity: must
Status: active
Date: 2026-10-23
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
