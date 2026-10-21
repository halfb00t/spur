# Phase 28: Refuse the Bad Link - Context

**Gathered:** 2026-10-21
**Status:** Ready for planning

<domain>
## Phase Boundary

A shared link carrying a non-blank value its form control cannot hold (an enum outside its options, non-numeric
text in a number box) is sent to the API and refused through the existing 422 path, never silently rebuilt as the
default part. Recorded as `L44`. The `root_fillet` derived-dimension label follows the root in force. Every open
review info finding of the milestone's scope ends dispositioned. Requirements: REQ-bad-link-refused,
REQ-bad-link-decision-logged, REQ-root-fillet-label-follows-root, REQ-info-findings-triaged,
REQ-old-info-findings-triaged.

The roadmap's five success criteria, its boundaries and its phase-close rule are fixed. This file records the
decisions the roadmap left open, and one adjustment to success criterion 1 (D-05) that the human approved.
Taken at kickoff and not re-asked: refusal covers enums and number boxes, blank means "use the default", unknown
keys are still ignored, the `root_fillet` label is fixed, the Phase 18 and Phase 10 findings are triaged cheaply.
No new `GearParams` field. The fix is client-side only. `problems()` and `fail()` stay unchanged.
`git diff --exit-code v0.5 -- tests/regression/` stays empty.

</domain>

<decisions>
## Implementation Decisions

### Bad-value mechanism (REQ-bad-link-refused)
- **D-01:** One shared `rejected` map (field name to raw token) covers selects and number boxes. `readHash`
  fills it, and `gearQuery` sends `rejected.get(name)` for a rejected field in place of the control's value. No
  stray `<option>` in the select, no placeholder in the number box: the control shows blank or empty, and the
  server's message plus the field outline say why. One code path.
  - Why not the stray option (ARCHITECTURE 3.7): kickoff put number boxes in scope, and a `type=number` box
    sanitises `abc` to `''` before code can read it (MEASURED, FEATURES A.2). A side map is needed regardless, so
    a select-only second mechanism adds cleanup rules for no contract gain.
  - The map is a `Map`/object, never rows in the `['word',` shape (they are harvested as `DIMS` keys,
    `tests/test_api.py:157-165`).
- **D-02:** Detection: assign the token, then read the control back. A non-empty raw token that reads back as
  `''` is rejected (select at `selectedIndex` -1, number box sanitised). No per-type enum or numeric check. This
  covers `bogus`, `Trochoid` (case) and `abc` with one rule. Values the control holds (`22.5`, `-5`, `1e1`)
  already reach the API and are refused there today, unchanged.
  - Scope is `fields` (GearParams form fields) plus the mate box (D-05). Selector selects
    (`buildSelectors`, `s.select`) also use `selectedIndex` -1 to mean "no option holds" (`app.js:341-369`). They
    are not link fields and must not be swept into the map.
  - The pre-pass runs around the pinned `readHash` line (`for (const [name, { input }] of fields) input.value =
    h.get(name) ?? defaults[name];`) and the pinned end (`mateInput.value = h.get('mate_teeth') ?? '';
    applyRelations(); deriveSelectors(); }`), not as a rewrite of them (`tests/test_api.py:240-241`).

### Mark and clear rules
- **D-03:** A rejected token leaves the map on: an edit of **that** field, Reset, or the next `readHash`
  (hashchange, back/forward). Editing a different field keeps sending the bad token, so the build stays refused
  and the address bar stays truthful. "Any edit clears all" was rejected: it is today's bug one keystroke later.
- **D-04:** The fragment keeps the raw token (it is rebuilt from `gearQuery`, which now sends it), so Copy link
  copies the link as given. The page sends no STL request for it and draws no default part. Both come from the
  existing path: info is fetched first and `fail()` returns before the STL request.
- **D-05:** `mate_teeth=abc`: the token is sent, the 422 blocks the build, and the server's bare message is shown
  ("Input should be a valid integer, unable to parse string as an integer", no "Mate teeth:" prefix). **The mate box gets no
  outline**, because `mate_teeth` is not in `fields` and `problems()` stays unchanged. `L44` records this gap, and
  the plan states it against success criterion 1 ("mark the field") as the approved reading for the mate box.
  The literal `'mate_teeth'` already appears in `app.js` and is not a `GearParams` field, so the "no quoted field
  name outside `DIMS`" rule does not apply to it.
- **D-06:** Blank stays default (kickoff). `L44` states the deliberate mismatch: the page treats `root_shape=`
  and `teeth=` as "use the default" (a shared link that blanks a field relies on L05), while the API answers 422
  for `''` (`literal_error` / `int_parsing`, MEASURED). That is a stricter, separate boundary. No code change and
  no debt item.

### `L44` content (REQ-bad-link-decision-logged)
- **D-07:** `L44` records: what is refused (a non-blank token its control cannot hold, D-02), the mechanism
  (D-01), the clear rules (D-03), blank kept as default with the API mismatch (D-06), unknown keys still ignored,
  the mate box's message-without-outline (D-05). It amends L39's `root_shape=bogus as today` pin and supersedes
  L42's recorded observation that the `if (prop.enum)` / `gearQuery` / `readHash` lines are byte-identical.
  L39 and L42 get no edits: the amendment lives in L44 (append-only log). The pin flip, `docs/architecture/web-ui.md:80`,
  the debt item's retirement (`2026-10-10-root-shape-bogus-loads-a-blank-select.md` to `resolved/`, INDEX
  row moved) and the fix land in one commit.
- **D-08:** Red-first, per PITFALLS: (1) apply the fix with the old pin untouched and record the
  `root_shape=bogus as today` step's first failure line (that step, not an earlier one); (2) rewrite the pin to
  the new contract plus steps for `recess_sides=bogus`, `teeth=abc`, `mate_teeth=abc`, recovery on edit and
  Reset, and "valid link leaves nothing marked"; (3) revert only the `app.js` fix and record the new pin going
  red. Both lines go under "Seen red once". Old step names stay in `bench/RESULTS.md` as history.

### `root_fillet` label (REQ-root-fillet-label-follows-root)
- **D-09:** While a hob root is in force the row reads **"Hob tip radius used"**. A radial root keeps "Root
  fillet used". The value under the hob root is `rm.cutter.rho` (`calc.py:1091-1095`).
- **D-10:** The label is a function of the info document `d`, in the same shape as the `span` and
  `hex_cell_effective` rows (`app.js:17,39`). It keys on a value only the hob root produces: `root_form_d` is
  `None` exactly when `rm.curve is None` (`calc.py:1292`), so `d.root_form_d != null` is the candidate key.
  It follows the root the server built, not the one requested (a trochoid request can fall back to radial).
  Reading the form's `root_shape` was rejected: it puts a field name outside `DIMS` and shows the request,
  not the build.
  - ASSUMPTION: `rm.curve is not None` implies `rm.cutter is not None`, so `root_form_d` present means the hob
    branch at `calc.py:1091` ran. The researcher or planner confirms this in `root_mode` before relying on it.
  - Text only. No part, number or request moves. Its own commit.

### Triage scope (REQ-info-findings-triaged, REQ-old-info-findings-triaged)
- **D-11:** Phase 26 IN-01..05 (five `| info | open |` rows in `26-REVIEW-DISPOSITION.md`, listed in neither
  REQUIREMENTS nor the roadmap) are triaged in this phase with the same vocabulary. Cheap fixes only where this
  phase already edits the file. The rest are `deferred` + path or `skipped` + a one-line reason. The close grep
  extends to Phase 26: `grep -n '| info | open |'` over the Phase 10, 18, 19, 21-24 **and 26**
  `*-REVIEW-DISPOSITION.md` files prints nothing.
- **D-12:** The Phase 18 leftovers (everything except IN-02 and IN-06, closed as overtaken, and IN-07, whose
  docstring is fixed) go into one `nice` debt item whose trigger is **the next phase that changes the trochoid /
  hob-root maths in `calc.py` or its tests**.
- **D-13:** 10 IN-02 (`tip_chamfer_effective`'s null-gate reads `p.tip_chamfer`, not the applied `tch`; it
  changes a printed value) is filed as a `docs/tech_debt/active/` item, **Severity: must**, whose next step is a
  human decision: fix under a new `Lxx` with its own `make fixture.regen` commit, or keep it with a reason.
  Not fixed in this phase.
- **D-14:** The roadmap's in-phase fixes stand: 24 IN-01 (the stash comment), 24 IN-02 / CX-03 (the "Could not
  build the form" wording), each its own commit in `app.js`. The behavioural half of 24 IN-01 (selector stash
  invalidation) is filed as an idea. The disposition cells are written from `27-TRIAGE.md`'s draft, so the close
  is a reading.

### Claude's Discretion
- Exact name and placement of the map and its helper, provided the pinned tokens hold.
- New browser step names (e.g. `root_shape=bogus is refused`).
- Commit order inside the phase, keeping one concern per commit (fix + pin + L44 + docs + debt retirement as one;
  label; 24 IN-01; 24 IN-02 / CX-03; triage records).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope
- `.planning/ROADMAP.md` § Phase 28: goal, five success criteria, boundaries, triage ride-along list
- `.planning/REQUIREMENTS.md` § "Bad links — refused, never guessed" and § "Info findings — none left `open`"

### Bad-link design and evidence
- `.planning/research/FEATURES.md` Part A: measured behaviour per link (A.2), why it drops (A.3), the 422 path (A.4), the map mechanism (A.5)
- `.planning/research/ARCHITECTURE.md` §3.7: pinned tokens, Reset, browser step rewrite, downstream docs; F6
- `.planning/research/PITFALLS.md` (lines ~218-240): the refused value must survive the page; red-first order for the pin flip
- `docs/tech_debt/active/2026-10-10-root-shape-bogus-loads-a-blank-select.md`: the debt item retired by the fix
- `docs/architecture/decision_log.md` L39 (line ~2330) and L42 (line ~2715): what L44 amends or supersedes; also L02, L03, L05, L08
- `docs/architecture/web-ui.md:80`: the "pinned as today's behaviour" sentence to bring true

### Code and pins
- `src/spur/static/app.js`: `DIMS` (13-40), `readHash` (105-111), `gearQuery` (114-120), `problems` (187-202), selectors (300-470), Reset (615-622)
- `tests/test_api.py`: `app.js` source pins (157-165 row harvest, 240-241 `readHash` lines, 277-283 no field name outside `DIMS`). Run early; the regexes were not fully read in research
- `tests/test_browser.py`: step `root_shape=bogus as today` (~1754-1808), `BOGUS_LINK` / `TODAY` (~97-103), `_api_get`, `_expected_422`
- `src/spur/calc.py:1084-1100, 1292`: `root_fillet` value under the hob root, `root_form_d` gate

### Triage
- `.planning/phases/27-ledger-tests-and-harness/27-TRIAGE.md`: draft table to finalise
- `.planning/phases/26-gate-fails-with-a-cause/26-REVIEW.md`, `26-REVIEW-DISPOSITION.md`: IN-01..05
- `.planning/milestones/v0.4-phases/18-trochoid-maths-proved/18-REVIEW.md`: IN-01..08
- `.planning/milestones/v0.2-phases/10-tooth-tip-chamfer/10-REVIEW.md`: IN-01, IN-02
- `*-REVIEW-DISPOSITION.md` for Phases 19 and 21-24 (v0.4 / v0.5 milestone phase dirs)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `problems()` / `fail()`: field-agnostic 422 marking keyed on `d.loc[1]` and `d.ctx.fields`. It already marks
  any `fields` entry, so a sent enum or number token is outlined with no per-field code.
- `DIMS` label functions (`span`, `hex_cell_effective`): the existing shape for a document-dependent label.
- Browser test oracles `_api_get` and `_expected_422`: compare the page's message to the API's own text (L02).

### Established Patterns
- Pre-pass around pinned lines, never a rewrite of them (`tests/test_api.py` token pins).
- No quoted `GearParams` field name outside `DIMS`; new tables are objects, not `['word',` rows.
- A pin is changed by the commit that fixes its debt, seen red both ways.
- `stash` (`app.js:300`) is the precedent for a side map cleared on Reset (`stash.clear()` on the pinned Reset line).
  The rejected map's Reset clear goes on a new line before that pinned line.

### Integration Points
- `readHash` (fill the map), `gearQuery` and the `infoQ` mate branch (`app.js:244-246`, send the token), the
  form `input` listener and `mateInput`'s listener (clear own field), Reset (clear all).

</code_context>

<specifics>
## Specific Ideas

- The address bar and Copy link must keep exactly what the link said. The evidence of the bad value never
  leaves the fragment.
- Message text is the server's, verbatim. No "got 'bogus'" suffix (that would change `_expected_422`).

</specifics>

<deferred>
## Deferred Ideas

- Outlining the mate box on a `mate_teeth` 422 (needs `problems()` to know a non-`fields` input). Recorded in
  `L44` as a known gap, not filed. Raise it if a user reports it.
- Showing the rejected token inside the control (stray select option, number placeholder). Considered, rejected
  for D-01.
- Whether the API should accept `''` as "default". Recorded in `L44` (D-06), not filed.

</deferred>

---

*Phase: 28-refuse-the-bad-link*
*Context gathered: 2026-10-21*
