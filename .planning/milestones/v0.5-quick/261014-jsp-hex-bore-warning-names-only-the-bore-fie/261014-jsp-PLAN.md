---
phase: quick-261014-jsp
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/spur/calc.py
  - tests/test_calc.py
  - tests/composition.py
  - tests/test_api.py
  - tests/test_cli.py
  - tests/test_relations.py
  - tests/test_browser.py
  - docs/architecture/decision_log.md
  - README.md
  - docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md
  - docs/tech_debt/resolved/2026-10-11-hex-bore-warns-about-default-bore-fields.md
  - docs/tech_debt/INDEX.md
autonomous: true
requirements:
  - "tech-debt:2026-10-11-hex-bore-warns-about-default-bore-fields"

estimate:
  tokens: 55000
  raw_tokens: 55000
  tasks: 3
  confidence: low

must_haves:
  truths:
    - "A hex link that leaves bore_d and bore_flat at their defaults (`?bore_hex=6`, `spur info --bore-hex 6`, a Hex pick in the form) answers no 'Hex bore replaces the round profile' warning (locked decision 1)"
    - "A hex link that sets bore_d or bore_flat away from both 0 and its schema default names exactly those fields with their values, in the unchanged sentence shape: `?bore_hex=6&bore_flat=3` -> 'Hex bore replaces the round profile: bore_flat (3 mm) is ignored.' (locked decision 1)"
    - "Zero is never named, and an explicit value equal to its default is silent (`?bore_hex=6&bore_d=9`), the blind spot that L27's amendment records (locked decisions 1 and 2)"
    - "The relation proofs in tests/test_relations.py (forward, reverse, driver) stay green and keep their power: removing bore_d, bore_flat or spoke_fillet from the declared set turns the reverse scan red"
    - "The browser step `warning rendered` still follows a link with one warning and checks that the page renders exactly the API's list"
    - "L27 carries a dated amendment, and the debt file is resolved, moved with git mv and indexed under Resolved in the same commit as the calc fix (locked decisions 2 and 3); pre_v0_2.json and golden_requests.json are unchanged; make verify passes"
  artifacts:
    - path: src/spur/calc.py
      provides: "the hex-bore warning rule in derive(): non-zero AND not the schema default"
      contains: "model_fields[name].default"
    - path: tests/test_calc.py
      provides: "the parametrized hex cases written as requirements; the composition test expecting no hex sentence on default hex rows"
      contains: "test_a_hex_bore_names_only_the_round_fields_set_away_from_their_defaults"
    - path: tests/test_relations.py
      provides: "reverse scan on a stepped base, driver-check fallback off the default, and the dropped-field meta-test parametrized over spoke_fillet, bore_d and bore_flat"
    - path: docs/architecture/decision_log.md
      provides: "the dated L27 amendment paragraph and the in-place pointer"
      contains: "Amended 2026-10-14"
    - path: docs/tech_debt/resolved/2026-10-11-hex-bore-warns-about-default-bore-fields.md
      provides: "the retired debt with Status: resolved, Resolved in:, and a Resolution section"
      contains: "Status: resolved"
  key_links:
    - from: src/spur/calc.py
      to: src/spur/params.py
      via: "type(p).model_fields[name].default is where the rule reads the default (9.0 and 8.0 today), never a literal"
      pattern: "type\\(p\\)\\.model_fields\\[name\\]\\.default"
    - from: tests/test_relations.py
      to: src/spur/calc.py
      via: "the reverse scan's stepped base and the driver check's fallback put bore_d and bore_flat at values calc names"
      pattern: "default.*step"
    - from: tests/test_browser.py
      to: /api/info
      via: "the one-warning link of the `warning rendered` step"
      pattern: "bore_hex=6&bore_d=12"
---

<objective>
Make the hex-bore warning name only the round-bore fields the request set away from their
defaults. Today `derive()` keeps every value `> 0`, and both defaults are non-zero (bore_d 9.0,
bore_flat 8.0), so every hex link warns about values nobody set. The plan also rewrites every
test that pinned the old sentence as a requirement, records the rule as a dated amendment to L27,
and retires the debt in the same commit.

Purpose: a warning that shows up on every hex part teaches users to skip warnings, and L08
puts the honest gaps in that list. Locked decision 1 is the rule, locked decision 2 is the L27
amendment and locked decision 3 is the debt retirement in the fix commit. The human took all
three at dispatch and they are not revisited here.

Output: one commit. It holds the calc rule, seven test files (some rewritten, some newly
pinned), the L27 amendment, one README sentence and the retired debt file with its INDEX row.

Scope found at planning beyond the dispatch's pin list. It was measured on a scratch copy of
HEAD 94dfc19 with the rule applied, running the whole suite except the browser test: 57 failed.
- tests/test_relations.py fails three tests under the rule. One is the reverse scan, which sees
  0 "ignored" sentences and trips its own `> 0` empty-scan guard. One is the driver check, which
  probes bore_d at its default 9 under a hex bore. The last is the dropped-field meta-test. Task 2
  fixes them without weakening any proof.
- tests/test_cli.py:115 is in `test_readme_export_examples_run`. tests/test_cli.py:295 is in
  `test_cli_and_api_print_the_same_hex_bore_document`. Both are in the dispatch's list.
- README.md:150-152 says `warnings` "names any round-bore field it ignored". That is no longer
  true for a field left at its default, so Task 3 fixes the sentence.
- The 48 hex rows of the composition test fail through `HEX_IGNORES_ROUND`.
- There were no regression-replay failures. No fixture record sets `bore_hex`.
</objective>

<execution_context>
@~/.claude/gsd-core/workflows/execute-plan.md
@~/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@CLAUDE.md
@docs/CODING_VALUES.md
@docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md
@docs/tech_debt/INDEX.md
@docs/tech_debt/TEMPLATE.md

Interface facts the executor relies on (read at planning, HEAD 94dfc19):
- src/spur/calc.py:12-16 imports `GearParams` only under `TYPE_CHECKING`. params.py imports calc
  lazily, from the model validator (params.py:257 and :283), so calc cannot name the class at
  runtime without changing that design. The class-level accessor `type(p).model_fields` needs no
  import. pydantic 2.11 deprecates the instance accessor `p.model_fields`, and this project's
  pytest config turns that warning into an error (see the comment at tests/test_calc.py around
  line 1455).
- src/spur/calc.py:1159-1167 is the `if p.bore_hex > 0:` branch of `derive()`. The sibling
  sentences at calc.py:1206-1247 (spokes, holes, honeycomb wall) use `> 0` on fields whose
  defaults ARE 0, which is correct. They are out of scope and must not be touched.
- `GearParams.model_fields["bore_d"].default` is 9.0 and `["bore_flat"].default` is 8.0
  (src/spur/params.py:134 and :137).
- The CLI flag for bore_d is `--bore-d`. Measured on the patched scratch copy:
  `spur info --bore-hex 6 --bore-d 12` prints exactly one warning,
  "Hex bore replaces the round profile: bore_d (12 mm) is ignored.", and
  `spur info --bore-hex 6` prints `"warnings": []`.
- The heavy test files excluded from `make verify.fast` (tests/test_hooks.py:25) are test_model,
  test_pool, test_api, test_cli and test_browser. test_calc and test_relations run at commit.
- A partial pytest run must pass `--no-cov`, because the coverage floor reads a partial run as a
  failure (see the Makefile comment above the `test:` target).
</context>

<tasks>

<task type="tracer" tdd="true">
  <name>Task 1: Name only the hex-ignored bore fields set away from their defaults, through calc, the API and the CLI (test pins rewritten first, seen red)</name>
  <files>src/spur/calc.py, tests/test_calc.py, tests/composition.py, tests/test_api.py, tests/test_cli.py</files>
  <precondition>The working tree has no tracked changes: `git diff --quiet HEAD` exits 0. The untracked `.DS_Store` at the repo root is not ours and is never added.</precondition>
  <read_first>
    - src/spur/calc.py lines 1-20 (the TYPE_CHECKING import) and lines 1155-1250 (the hex branch and its siblings)
    - tests/test_calc.py lines 1-30 (the import block), lines 230-265 (the parametrized hex test), lines 1425-1470 (the composition test)
    - tests/composition.py lines 15-30 (BORES) and lines 100-115 (the hex sentence constant)
    - tests/test_api.py lines 820-835 (the hex-with-D-flat test)
    - tests/test_cli.py lines 101-125 (`test_readme_export_examples_run`) and lines 284-296 (`test_cli_and_api_print_the_same_hex_bore_document`)
    - docs/architecture/decision_log.md lines 827-907 (L27; D-02 is the "Replaces, never refuses" paragraph)
  </read_first>
  <behavior>
    - `{"bore_hex": 6}`: no warning starts with "Hex bore replaces" (the defaults are silent)
    - `{"bore_hex": 6, "bore_d": 9, "bore_flat": 8}`: no hex sentence (an explicit default is silent; this is the blind spot L27's amendment records)
    - `{"bore_hex": 6, "bore_d": 12}`: the only hex sentence is "Hex bore replaces the round profile: bore_d (12 mm) is ignored."
    - `{"bore_hex": 6, "bore_flat": 3}`: the only hex sentence is "Hex bore replaces the round profile: bore_flat (3 mm) is ignored."
    - `{"bore_hex": 6, "bore_d": 0}`, `{"bore_hex": 6, "bore_flat": 0}` and `{"bore_hex": 6, "bore_d": 0, "bore_flat": 0}`: no hex sentence (zero is never named; the other field sits at its default)
    - `{"bore_hex": 6, "bore_d": 0, "bore_flat": 3}`: only bore_flat (3 mm) is named
    - `{"bore_hex": 6, "bore_d": 12.7, "bore_flat": 11.5}`: "Hex bore replaces the round profile: bore_d (12.7 mm) and bore_flat (11.5 mm) are ignored."
    - All nine were measured on the patched scratch copy at planning (2026-10-14) and gave exactly these outputs.
  </behavior>
  <action>
Implements locked decision 1 (the rule). This task also rewrites the test pins for it.

Step 0, before any edit: record the suite's collected count at HEAD with
`.venv/bin/python -m pytest --collect-only -q --no-cov | tail -1`. Task 3 compares against it.

Step A writes the tests first. Make these edits:

1. tests/test_calc.py, the parametrized test at about lines 245-264. Rename it to
   `test_a_hex_bore_names_only_the_round_fields_set_away_from_their_defaults`. Rewrite its cases
   as `pytest.param(kw, expected, id=...)`, one per `<behavior>` line above, so that each one
   reads as a requirement. Suggested ids: defaults-silent, explicit-default-silent,
   bore_d-set-named, bore_flat-set-named, zero-bore_d-silent, zero-bore_flat-silent,
   both-zero-silent, zero-beside-a-set-field-names-only-the-set-one, both-set-named.
   Strengthen the named-case assertion. The list of warnings that start with "Hex bore replaces"
   must equal `[expected]`, not merely contain it. Keep the existing None-case assertion. Rewrite
   the docstring to say that D-02, as amended 2026-10-14 (L27), names an ignored round field only
   when it is non-zero and differs from its schema default, and that no warning appears when
   none does.
2. tests/composition.py around lines 108-112. Delete the hex sentence constant and the comment
   above it. `BORES["hex"]` is `{"bore_hex": 6}` on the default part, so under the rule the hex
   rows carry no hex sentence at all.
3. tests/test_calc.py. Remove that constant from the `from composition import` block (line 17).
   In the composition test (about line 1461), drop the `radial_warnings` variable. The warnings
   assertion becomes the trochoid thickness sentence when `root == "trochoid"`, else the empty
   tuple. Add one clause to that test's docstring: a hex bore at the default bore_d and bore_flat
   implies no warning (L27, amended 2026-10-14).
4. tests/test_api.py, `test_a_hex_link_with_a_d_flat_builds_and_says_both_round_fields_are_ignored`.
   Rename it to `test_a_hex_link_builds_and_names_only_the_round_fields_it_sets`. Make it check
   three things in order:
   - GET /api/info with `bore_hex=6` alone returns 200 and no warning that starts with
     "Hex bore replaces". This is the debt's own reproduction.
   - With `bore_hex=6` and `bore_flat=3`, it returns 200, and the hex sentences in `warnings`
     equal ["Hex bore replaces the round profile: bore_flat (3 mm) is ignored."].
   - The existing preview STL request still returns 200.
   Update the docstring to match.
5. tests/test_cli.py, `test_readme_export_examples_run` (line 115). The README's hex example
   `--bore-hex 6` leaves both round fields at their defaults, so it now warns nothing. Replace
   the expected-sentence assertion with an assertion that the captured stderr does not contain
   "Hex bore replaces the round profile". Add a one-line why-comment citing L27, amended
   2026-10-14.
6. tests/test_cli.py, `test_cli_and_api_print_the_same_hex_bore_document` (lines 284-295). Keep it
   a parity test that still compares the D-02 warning. The CLI runs `info --bore-hex 6 --bore-d 12`
   and the API gets `{"bore_hex": 6, "bore_d": 12}`. The documents must be equal with the same
   key order, and "Hex bore replaces the round profile: bore_d (12 mm) is ignored." must be in
   the CLI's `warnings`. Update the docstring: it covers a hex link that sets a round field.

Step B is the red check. Run the Task 1 verify command (below) without the calc change.
Expected red:
- the five `<behavior>` cases whose expectation changes (defaults-silent,
  explicit-default-silent, bore_d-set-named, zero-bore_d-silent, zero-bore_flat-silent)
- every hex row of the composition test
- the renamed API test
- both CLI tests
Record the failure count for the SUMMARY.

Step C changes calc. In src/spur/calc.py, inside `derive()`'s `if p.bore_hex > 0:` branch, the
comprehension's filter keeps a field only if its value is non-zero AND differs from
`type(p).model_fields[name].default`. Read the default from the model, never a literal 9 or 8.
Use `type(p)` because calc imports `GearParams` only for type checking (params imports calc
lazily) and the instance accessor is deprecated. Leave the sentence's wording, its join and its
are/is agreement unchanged.

Rewrite the D-02 comment above the comprehension so that it carries the why and the
constraints:
- D-02's "naming only the fields the user set away from 0" used `> 0` as a proxy, which named
  the 9 mm and 8 mm defaults on every hex link (L27, amended 2026-10-14).
- The value is compared instead of using `model_fields_set` for two reasons. app.py's `_gear`
  rebuilds `GearParams` from a full `model_dump`, so the set is lost. And pydantic equality
  includes `model_fields_set`, which would split the build caches' keys.
- The blind spot: an explicit value equal to its default is silent.

Do not touch the spoke, hole or honeycomb-wall sentences further down. Their defaults are 0, so
`> 0` is already right there. Do not edit app.py, params.py, model.py, pool.py, cli.py or
static/app.js (locked decision 1).

Step D is the green check. Re-run the verify command; it must pass. Then confirm that both
fixture files are untouched.

Do NOT commit at the end of this task. CLAUDE.md retires a debt in the commit that fixes it, so
Task 3 makes the plan's one commit (locked decision 3).
  </action>
  <reversibility rating="reversible">Changes warning text only: no part, number, default or link moves (L05), and restoring the `> 0` filter brings the old sentence back byte for byte.</reversibility>
  <verify>
    <automated>make test PYTEST_ARGS="tests/test_calc.py tests/test_api.py tests/test_cli.py -n0 --no-cov -q -k 'hex or readme'" && git diff --exit-code tests/regression/pre_v0_2.json tests/regression/golden_requests.json</automated>
  </verify>
  <done>
- The red run (Step B) failed on the rewritten pins and its count is recorded.
- After the calc change the command passes.
- `derive(GearParams(bore_hex=6)).warnings` holds no hex sentence.
- The two regression fixtures show no diff.
- No commit has been made yet.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Keep the relation proofs honest under the rule, and give the browser step a hex link that still warns</name>
  <files>tests/test_relations.py, tests/test_browser.py</files>
  <read_first>
    - tests/test_relations.py lines 1-35 (module docstring), 150-235 (`_assert_relations_hold_in_calc`, `_assert_calc_ignores_only`), 236-311 (CUTOUT_STATES, BORE_STATES, `_assert_relations_name_the_driver_calc_obeys`), 419-501 (the tests that call them)
    - tests/test_browser.py lines 204-216 (`_follow_link`) and 801-840 (the `warning rendered` step)
  </read_first>
  <behavior>
    - The reverse scan (`_assert_calc_ignores_only` over the full declared set) sees at least one "ignored" sentence again. It returned 1 at HEAD and returns 1 with the stepped base under the new rule (both measured at planning, 2026-10-14).
    - Dropping bore_d, bore_flat or spoke_fillet from the declared set turns the reverse scan red with "no relation declares <field>". All three were measured red with the stepped base. With a base built from the `declared` argument instead, dropping bore_d or bore_flat was NOT red, which is why the base must not depend on it.
    - The driver check passes in all twelve states with bore_d probed at 9.05 and bore_flat at 8.05. All 24 combinations validate (measured).
    - In the browser step, the one-warning link `bore_hex=6&bore_d=12` gets exactly one API warning, and the page renders the same list.
  </behavior>
  <action>
This task carries locked decision 1's rule into the two harnesses that read the hex sentence
indirectly.

Step A is the red check. With Task 1's calc change in place, run
`make test PYTEST_ARGS="tests/test_relations.py -n0 --no-cov -q"`. Expect exactly three failures:
- `test_every_field_calc_ignores_is_declared`: the assertion 0 > 0 fails.
- `test_each_relation_names_the_driver_calc_obeys`: "bore_d in no cutout + hex bore: the
  relation says ignored, calc says used".
- `test_an_ignored_field_without_its_relation_goes_red`.
Record them.

Step B: tests/test_relations.py edits.

1. `_assert_calc_ignores_only` (the reverse scan). Before the loop, build a base dict. It holds
   every numeric (number or integer) property whose schema default is non-zero, each set one
   schema step above its default. Build it from `_properties()`, NOT from the `declared`
   argument: the meta-test drops fields from `declared`, and a base that follows `declared`
   loses bore_d and bore_flat exactly when the test needs them. Each perturbation then validates
   the base merged with `{name: value}` instead of `{name: value}` alone.
   Add a why-comment that carries the measurements:
   - Under L27's 2026-10-14 amendment, calc names bore_d and bore_flat only off their defaults.
     On the defaults the scan saw no sentence (measured: 0).
   - On the stepped base a perturbed bore_hex draws the sentence again (measured: 1, as at HEAD).
   - The base validates and warns nothing (measured 2026-10-14).
   - Zero defaults stay 0, because set off 0 every perturbation would carry its own cutout
     sentence.
   Update the docstring: "under defaults" becomes "on a base that holds every non-zero numeric
   default one schema step off it".
2. `_assert_relations_name_the_driver_calc_obeys` (the driver check). The fallback value for a
   dependent with a non-zero default becomes one schema step above that default instead of the
   default itself. The zero-default branch stays `minimum + step`. Update the docstring
   sentence that says a default is what a hex bore calls ignored: a hex bore now names bore_d
   only off its default (L27, amended 2026-10-14), so the probe steps one schema step off a
   non-zero default, and 0 would be named by nothing. Wrap the line at the 100-column limit.
3. `test_an_ignored_field_without_its_relation_goes_red`. Parametrize the dropped field over
   spoke_fillet, bore_d and bore_flat, with the `match` pattern built from the parameter. Keep
   the first full-set assertion. Update the docstring: spoke_fillet stands for the cutout
   sentences, and bore_d and bore_flat for the hex sentence, which only the stepped base keeps
   visible. This pins the power the old scan had implicitly.

Leave the forward check (`_assert_relations_hold_in_calc`) as it is. Its probes (`minimum + step`
and `maximum`) are already non-default, and it passed under the rule (measured).

Step C: tests/test_browser.py. In the `warning rendered` step, change the one-warning link from
`bore_hex=6` to `bore_hex=6&bore_d=12`. Change only the link; the step's assertions and comments
stay. `_follow_link` requires each link to differ from the current hash. The loop's order (the
two-warning link, then this one, then `teeth=23`, after a step that ended on `teeth=23`) still
meets that.

Before running the browser file, confirm the expectation is cheap to meet:
`.venv/bin/python -c "from spur.calc import derive; from spur.params import GearParams; print(derive(GearParams(bore_hex=6, bore_d=12)).warnings)"`
must print a one-element tuple holding the bore_d (12 mm) sentence.

Step D is the green check. Run the verify command. Also run the confirmation probe described in
the first `<behavior>` line: call `_assert_calc_ignores_only(frozenset(_relations()))` from a
`.venv/bin/python -c` with `tests` on `sys.path`, and record its return value for the SUMMARY.

Do NOT commit. Task 3 makes the one commit.
  </action>
  <verify>
    <automated>make test PYTEST_ARGS="tests/test_relations.py -n0 --no-cov -q" && make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q"</automated>
  </verify>
  <done>
- test_relations.py passes in full, including three parametrized cases of the dropped-field
  meta-test.
- The reverse scan returns at least 1 on the full declared set, with the value recorded.
- test_browser.py passes, with the `warning rendered` step's printed counts reading
  two-or-more, one, zero.
- No commit has been made yet.
  </done>
</task>

<task type="auto">
  <name>Task 3: Amend L27, correct the README sentence, retire the debt, run the gate, make the one commit</name>
  <files>docs/architecture/decision_log.md, README.md, docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md, docs/tech_debt/resolved/2026-10-11-hex-bore-warns-about-default-bore-fields.md, docs/tech_debt/INDEX.md</files>
  <read_first>
    - docs/architecture/decision_log.md lines 827-907 (L27 in full), lines 1629-1633 and 2806-2827 (two existing amendment paragraphs, for voice and shape), line 2739 (an in-place "superseded by the amendment of ... at the end of this entry" pointer)
    - .planning/milestones/v0.2-phases/08-hex-bore/08-DISCUSSION-LOG.md line 31 and 08-CONTEXT.md lines 79-85 (why Phase 8 rejected warning only for non-default fields)
    - docs/tech_debt/resolved/2026-10-05-no-fake-done-scan-is-blind-on-macos.md (a retirement in the same commit: its `Resolved in:` holds the commit subject; `## Resolution (date)` section; no trailing HTML comment)
    - docs/tech_debt/INDEX.md (Active row at line 39; Resolved table rows 45-48 for the row shape)
    - README.md lines 140-160
  </read_first>
  <action>
Implements locked decisions 2 and 3.

1. Amend L27 (locked decision 2: a dated amendment paragraph, not a new Lxx; Phase 25's reserved
   L43 is untouched). After L27's closing "**Reason:**" paragraph and before "## L28", append
   one paragraph in the log's voice. It opens with
   "**Amended 2026-10-14, from quick task 261014-jsp (`docs/tech_debt/resolved/2026-10-11-hex-bore-warns-about-default-bore-fields.md`).**"
   It must state each of the following:
   - (a) The rule. `bore_d` and `bore_flat` are named only when the value is non-zero and
     differs from the field's schema default. The default is read from the model (9.0 and 8.0
     today), never written as a literal. When neither qualifies there is no warning.
   - (b) Why `> 0` was wrong. D-02's own words were "naming only the fields the user set away
     from 0", but `> 0` stood in for that, and both defaults are non-zero. So `?bore_hex=6`, and
     since L42 every Hex pick in the selector, warned "bore_d (9 mm) and bore_flat (8 mm) are
     ignored." about values nobody set (PITFALLS M-7). That trains users to skip the list where
     L08 puts what could not be computed honestly.
   - (c) That it reverses the "Rejected: … a warning only for non-default fields" item in the
     "Replaces, never refuses" paragraph. Phase 8 rejected it as needing `model_fields_set`
     (08-DISCUSSION-LOG.md). A comparison of the value with the schema default needs no
     transport state.
   - (d) Why not `model_fields_set`. `app.py`'s `_gear` rebuilds `GearParams` from a full
     `model_dump`, so the set is gone before `derive()`. Pydantic v2 equality also includes
     `model_fields_set`, which would split the build caches' keys.
   - (e) The blind spot. An explicit `?bore_hex=6&bore_d=9` is silent, because after
     validation a 9 that was sent equals a 9 that was omitted.
   - (f) That the three interfaces agree. The form sends only fields that differ from their
     defaults (`gearQuery()` in `src/spur/static/app.js`), the CLI drops flags that were not
     given (`_params` in `src/spur/cli.py`), and a query omits what it does not set.
   - (g) What moved. Only `warnings` text: no part, number, default or link (L05). No fixture
     record sets `bore_hex`, so `pre_v0_2.json` and `golden_requests.json` are byte-identical.
     L41's relation still dims both fields under a hex bore at their defaults, because they are
     inert either way. The relation proofs now probe one schema step off a non-zero default,
     because a default is no longer what `calc` names.
   - (h) Reversibility: reversible, since it changes warning text only.

   Also append one parenthetical sentence at the end of L27's "**Replaces, never refuses**"
   paragraph, after its "(REQUIREMENTS.md "Out of Scope")." close, following line 2739's
   precedent. It says that the plain-hex-link example sentence and the rejected "warning only for
   non-default fields" are superseded by the amendment of 2026-10-14 at the end of this entry.
   Do not edit L41 or L42. Their citations of the active debt path are dated records; the log
   keeps such paths after retirement, for example decision_log.md:137 and :242.

2. README.md lines 150-152. Change the clause "and `warnings` names any round-bore field it
   ignored" so that it says `warnings` names each ignored round-bore field you set away from its
   default, and that a field left at its default is ignored without a warning. Rewrap only that
   sentence. Touch nothing else in the paragraph.

3. Retire the debt (locked decision 3).
   - `git mv docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md docs/tech_debt/resolved/`
   - In the moved file, set `Status: resolved`. Add the line
     `Resolved in: fix(calc): name only the hex-ignored bore fields set away from their defaults`
     directly after `Date:`. The retirement rides in the fix commit, which cannot name its own
     sha, so the field holds the commit subject, as the no-fake-done resolved file does.
   - Delete the trailing "On resolve" HTML comment.
   - Append `## Resolution (2026-10-14)` with these points:
     - the rule, and that it was chosen by the human at dispatch over `model_fields_set`
     - each test that moved, and why
     - the relation-proof adjustment, with the reverse-scan count measured in Task 2 and the
       red-before counts from Tasks 1 and 2
     - that the fixtures are unchanged
     - the collected test count before (recorded in Task 1, Step 0) and after (the same
       command on the final tree)
     - the `make verify` result line
     - one "not done here" sentence: 24-REVIEW IN-04's other half, naming the fields by their
       form titles instead of snake_case, was not in the locked scope, and the sentence still
       says `bore_d`/`bore_flat`
   - docs/tech_debt/INDEX.md: delete the Active row (line 39). Insert a row as the first row of
     the Resolved table. It links `resolved/2026-10-11-hex-bore-warns-about-default-bore-fields.md`
     with the same title, and its second cell reads
     "fix(calc): name only the hex-ignored bore fields set away from their defaults — see the file's own `Resolved in:` field".

4. Run the gate: `make verify`. It runs ruff, mypy --strict, import-linter, the unfinished-work
   scan and the whole pytest suite at -n 8 with coverage, and takes about 165-195 s on this host.
   It must pass. Keep its final pytest result line for the SUMMARY (CLAUDE.md asks for the
   command and its result line). If it fails, fix the cause; never narrow the run. Then confirm
   that `git diff --exit-code tests/regression/pre_v0_2.json tests/regression/golden_requests.json`
   is clean.

5. Make the one commit on the current branch (`fix/hex-bore-warning-names-set-fields`). Stage
   explicit paths only: the ten modified paths in this plan's `files_modified`, plus the debt
   rename already staged by `git mv`. Never `git add -A`; the untracked `.DS_Store` stays out.
   - The subject is exactly
     `fix(calc): name only the hex-ignored bore fields set away from their defaults`
   - The body is Conventional Commits prose, not caveman. It covers the rule and why `> 0` named
     the defaults, why the value is compared rather than `model_fields_set`, the blind spot, the
     tests that moved (including the relation-proof base), that L27 is amended and that the debt
     is retired in this commit.
   - End with the `Co-Authored-By:` attribution line your session's attribution reminder gives.
     The dispatch named `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`; use that
     unless your session names another.
   - The pre-commit hook runs `make verify.fast`, about 15 s. Do not push.
  </action>
  <verify>
    <automated>d=docs/tech_debt/resolved/2026-10-11-hex-bore-warns-about-default-bore-fields.md && test -f "$d" && test ! -e docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md && grep -qx 'Status: resolved' "$d" && grep -qx 'Resolved in: fix(calc): name only the hex-ignored bore fields set away from their defaults' "$d" && grep -q '^## Resolution (2026-10-14)$' "$d" && awk '/^## L27 /,/^## L28 /' docs/architecture/decision_log.md | grep -q '^\*\*Amended 2026-10-14' && awk '/^## L27 /,/^## L28 /' docs/architecture/decision_log.md | grep -q 'amendment of 2026-10-14 at the end of this entry' && .venv/bin/python -c "t=open('docs/tech_debt/INDEX.md').read(); a,r=t.split('## Resolved'); s='2026-10-11-hex-bore-warns-about-default-bore-fields.md'; assert s not in a, 'still under Active'; assert '(resolved/'+s+')' in r, 'no Resolved row'" && git diff --exit-code tests/regression/pre_v0_2.json tests/regression/golden_requests.json && test "$(git log -1 --format=%s)" = "fix(calc): name only the hex-ignored bore fields set away from their defaults" && .venv/bin/python -c "import subprocess; f=subprocess.run(['git','show','--name-only','--format=','HEAD'],check=True,capture_output=True,text=True).stdout.split(); assert len(f)==11, f; assert '$d' in f, f" && test -z "$(git status --porcelain --untracked-files=no)"</automated>
  </verify>
  <done>
- `make verify` passed before the commit, and its result line is recorded.
- HEAD is the one commit with the exact subject. `git show --name-status HEAD` lists the ten
  modified files plus the debt file's rename from active/ to resolved/, and nothing else.
- L27 holds the dated amendment and the in-place pointer.
- The debt file is resolved and moved, and its INDEX row sits under Resolved.
- The fixtures are byte-identical and the tracked tree is clean.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| HTTP query / CLI argv / form hash -> GearParams | Untrusted input crosses here. Validation is unchanged by this plan: range checks are field metadata, and cross-field feasibility is `check()`. |
| calc.derive() -> `warnings` -> API JSON / CLI stderr / page | The hex sentence is built from validated floats formatted with `:g` and two fixed field names. app.js renders each warning through `textContent` (static/app.js:183), never as HTML. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-261014-01 | Tampering | calc.derive() hex sentence | low | accept | The only input is the already-validated `GearParams`. The change adds a comparison with the class-level schema default and no new parsing or input path, and the page renders the string as text. |
| T-261014-02 | Information disclosure | `warnings` text | low | accept | The sentence names two public schema field names and the requester's own values, nothing else. |
| T-261014-03 | Denial of service | derive() on every keystroke | low | accept | The rule adds two dict lookups on `type(p).model_fields` per hex request: no loop, no allocation that grows with input. |
| T-261014-04 | Repudiation (honesty of output, L08) | the blind spot: an explicit default is silent | low | accept | The field is inert under a hex bore whatever its value, so no printed number is wrong and the part does not change. The blind spot is recorded in L27's amendment and pinned by the explicit-default-silent test case. |
| T-261014-SC | Tampering | npm/pip/cargo installs | low | accept | This plan installs no package, so no legitimacy gate is needed. |
</threat_model>

<verification>
- The Task 1 red run failed on the rewritten pins before the calc change, and the same command
  passes after it.
- The Task 2 red run showed the three relation failures. test_relations.py and test_browser.py
  pass after the edits.
- `make verify` passes on the final tree before the commit. Its result line is quoted in the
  SUMMARY.
- `git diff --exit-code tests/regression/pre_v0_2.json tests/regression/golden_requests.json`
  is clean after every task.
- One commit, with the exact subject and file set from Task 3.
</verification>

<success_criteria>
- `GET /api/info?bore_hex=6` and `spur info --bore-hex 6` answer `"warnings": []`.
- `?bore_hex=6&bore_flat=3` answers exactly "Hex bore replaces the round profile: bore_flat (3 mm) is ignored.".
- The reverse relation scan is non-empty and goes red when bore_d, bore_flat or spoke_fillet
  loses its relation.
- L27 is amended (dated, additive, with an in-place pointer). The debt is resolved in the fix
  commit with its INDEX row moved. The README sentence is accurate.
- `make verify` passes.
</success_criteria>

<output>
Create `.planning/quick/261014-jsp-hex-bore-warning-names-only-the-bore-fie/261014-jsp-SUMMARY.md` when done. It must include:
- the red-before failure counts from Tasks 1 and 2
- the reverse-scan count
- the collected test count before and after
- the `make verify` command and its result line
- the commit sha
- the statement that no new debt or idea item was filed. Any tangent goes to the human, not
  silently into a file.
</output>
