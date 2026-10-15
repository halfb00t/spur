# Ideas

Good ideas that are not for now, so they survive past the session that had them.
One file per item, `YYYY-MM-DD-short-slug.md`, from `TEMPLATE.md`. Add the row here in
the same commit as the file.

## Open

| Date | Item | Why it is not now |
|---|---|---|
| 2026-09-21 | [Trochoidal root fillets for undercut gears](2026-09-21-trochoidal-root-fillets.md) | The opt-in hob root shipped in Phase 19 (`root_shape`, L38); the default flip waits on a real fit report or a mating-pair request below `z_min` (D-09), because it would move every shared link's part |
| 2026-09-29 | [A rotation field for spoke arms and lightening holes](2026-09-29-cutout-rotation-field.md) | D-03 fixes +X and nobody has asked for another angle yet; the additive field is the safe undo when someone does |
| 2026-09-29 | [A teeth- or module-dependent honeycomb cell-count cap](2026-09-29-teeth-dependent-honeycomb-cap.md) | D-12 rejected it for one constant; revisit only if a small gear needs more cells and a sweep shows cost falling with gear size |
| 2026-10-11 | [The two relations calc does not back: recess_* under recess_sides=none, bore_flat at bore_d=0](2026-10-11-the-two-relations-calc-does-not-back.md) | A relation needs a calc warning first, which would rewrite warnings for 14 fixture records (kickoff decision 8); revisit when a user reports a recess or D-flat value that did nothing |
| 2026-10-14 | [The hex-bore warning names its fields by form title](2026-10-14-hex-warning-names-fields-by-form-title.md) | A warning text that reads the schema titles couples `calc` to form metadata, and it was outside quick task 261014-jsp's locked scope |

## Retired

An idea that shipped moves here in the commit that ships it, the way `docs/tech_debt/` keeps resolved
items: the file goes to `retired/` with `Status: retired` and `Retired in:` naming that commit's subject.

| Date | Item | Retired in |
|---|---|---|
| 2026-09-21 | [A browser test for the viewer](retired/2026-09-21-browser-test-for-the-viewer.md) | docs(21): log L39 and retire the browser-test idea -- a headless browser runs in make verify and CI |
| 2026-10-08 | [The download's file name does not carry the root shape](retired/2026-10-08-download-name-carries-the-root-shape.md) | feat(22): a hob-root part downloads as _trochoid -- log L40 and retire the download-name idea |
| 2026-09-29 | [Conditional form fields ("disabled when")](retired/2026-09-29-conditional-form-fields.md) | test(23): one flip link per gate, the refused pair and Reset -- retire the conditional-fields idea |
| 2026-09-27 | [A bore-shape selector in the web form](retired/2026-09-27-bore-shape-selector-in-the-web-form.md) | test(24): every pick from every bore shape, the stash across links and the keyed bore -- retire the bore-shape idea |
| 2026-10-03 | [Constrain `make venv` to the pinned closure, the way CI is](retired/2026-10-03-constrain-make-venv-to-the-closure.md) | docs(25): log L43 -- the gate bar re-set on an idle host amends L34, stale gate figures rewritten, IN-03 closed |
| 2026-09-22 | [Measure the Raspberry Pi 5 claim, or soften it](retired/2026-09-22-measure-or-soften-the-pi5-claim.md) | docs(25): name the hardware behind every README number and make no Pi 5 claim -- retire the Pi 5 idea |
| 2026-09-28 | [A recipe (or skill) for re-verifying a phase after post-verification fixes](retired/2026-09-28-reverify-after-post-verification-fixes.md) | docs(25): add the reverify-phase skill and point HOW_TO_DEVELOP section 6 at it -- retire the reverify idea |
