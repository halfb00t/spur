# Ideas

Good ideas that are not for now, so they survive past the session that had them.
One file per item, `YYYY-MM-DD-short-slug.md`, from `TEMPLATE.md`. Add the row here in
the same commit as the file.

## Open

| Date | Item | Why it is not now |
|---|---|---|
| 2026-09-21 | [Trochoidal root fillets for undercut gears](2026-09-21-trochoidal-root-fillets.md) | The opt-in hob root shipped in Phase 19 (`root_shape`, L38); the default flip waits on a real fit report or a mating-pair request below `z_min` (D-09), because it would move every shared link's part |
| 2026-09-22 | [Measure the Raspberry Pi 5 claim, or soften it](2026-09-22-measure-or-soften-the-pi5-claim.md) | Needs hardware nobody here has; Phase 2's numbers all come from a 12-core dev machine |
| 2026-09-27 | [A bore-shape selector in the web form](2026-09-27-bore-shape-selector-in-the-web-form.md) | Judged "not taken" at Phase 12 (08 D-09 stands); a browser test now exists (L39) and Phase 24 takes it; otherwise revisit when a user reports the ignored-field warnings as insufficient |
| 2026-09-28 | [A recipe (or skill) for re-verifying a phase after post-verification fixes](2026-09-28-reverify-after-post-verification-fixes.md) | Process, not product; one HOW_TO_DEVELOP paragraph or a project skill once it repeats a third time |
| 2026-09-29 | [A rotation field for spoke arms and lightening holes](2026-09-29-cutout-rotation-field.md) | D-03 fixes +X and nobody has asked for another angle yet; the additive field is the safe undo when someone does |
| 2026-09-29 | [A teeth- or module-dependent honeycomb cell-count cap](2026-09-29-teeth-dependent-honeycomb-cap.md) | D-12 rejected it for one constant; revisit only if a small gear needs more cells and a sweep shows cost falling with gear size |
| 2026-09-29 | [Conditional form fields ("disabled when")](2026-09-29-conditional-form-fields.md) | Judged "not taken" at Phase 12 (08 D-09 stands); a browser test now exists (L39) and Phase 23 takes it; otherwise revisit when a user reports the ignored-field warnings as insufficient |
| 2026-10-03 | [Constrain `make venv` to the pinned closure, the way CI is](2026-10-03-constrain-make-venv-to-the-closure.md) | Phase 15 pins CI only (D-14); the closure was resolved on linux/amd64 and its arm64 wheel availability is unproven — revisit when a fresh constrained `make venv` passes `make verify` on this host |
| 2026-10-08 | [The download's file name does not carry the root shape](2026-10-08-download-name-carries-the-root-shape.md) | A radial and a trochoid download of one gear share a name, but nobody has reported mixing them up, and a slug change renames every download, so it needs its own decision |

## Retired

An idea that shipped moves here in the commit that ships it, the way `docs/tech_debt/` keeps resolved
items: the file goes to `retired/` with `Status: retired` and `Retired in:` naming that commit's subject.

| Date | Item | Retired in |
|---|---|---|
| 2026-09-21 | [A browser test for the viewer](retired/2026-09-21-browser-test-for-the-viewer.md) | docs(21): log L39 and retire the browser-test idea -- a headless browser runs in make verify and CI |
