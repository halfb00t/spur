---
phase: 16-typing-validation-debt
reviewed: 2026-10-05T00:00:00Z
depth: standard
files_reviewed: 9
files_reviewed_list:
  - docs/architecture/decision_log.md
  - docs/architecture/solid-model/implementation.md
  - docs/tech_debt/active/2026-10-05-phase-07-nyquist-gaps.md
  - docs/tech_debt/INDEX.md
  - docs/tech_debt/resolved/2026-09-21-cadquery-shape-typing.md
  - Makefile
  - pyproject.toml
  - src/spur/model.py
  - tests/test_model.py
findings:
  critical: 0
  warning: 2
  info: 3
  total: 5
status: issues_found
---

# Phase 16: Code Review Report

**Reviewed:** 2026-10-05
**Depth:** standard
**Files Reviewed:** 9
**Status:** issues_found

## Summary

The diff against `085e5a6` does what plan 16-01 says. I found no bug in the narrowing itself.

- `_body` and `_shape_of` are correct. `isinstance(x, cq.Solid | cq.Compound)` is valid on 3.12.
- Every call site assigns the `Any` result of `fillet`/`chamfer` before returning, so `warn_return_any` stays satisfied.
- No geometry function changed.
- The two tests compare the full message with `==`, as intended.
- I re-ran `.venv/bin/python -m mypy src tests docker bench scripts`. It printed `Success: no issues found in 37 source files`, matching the claim in the debt file and L35.
- `git grep 'type: ignore' -- 'src/spur/*.py'` has no hits. The only remaining suppressions are the two deliberate ones in `tests/test_calc.py:1472` and `tests/test_cli.py:423`.
- Commits `4f7e8fe` and `c11213e` exist with the subjects the docs cite.
- cadquery ships `py.typed`. `cadquery-ocp` 7.9.3.1.1 has no `.pyi` or `py.typed`. Both claims in the `pyproject.toml` comment hold.

The defects are a leftover third narrowing that the new docs deny exists, and a weaker pin than its comment advertises. Neither affects correctness today.

## Warnings

### WR-01: A third `.val()` narrowing survives in `_cell_cutters`; it raises the wrong exception, carries a stale comment, and the docs say there are only two boundaries

**File:** `src/spur/model.py:352-358` (docs: `docs/architecture/solid-model/implementation.md:29`, `docs/architecture/decision_log.md:1761`)
**Issue:** `_cell_cutters` still narrows `Workplane.val()` by hand and raises a bare `TypeError`:

```python
# .val() is typed as a 4-way union; narrowed with isinstance for mypy only
# (cli.py's precedent) -- no new type-checker suppression added here.
if not isinstance(proto, cq.Solid):
    raise TypeError(f"honeycomb cell prototype is not a Solid: {type(proto)}")
```

This causes four problems.

1. **Wrong message to the user.** `_build_checked` catches any non-`BuildError` and rewrites it as "Geometry kernel failed (TypeError); try smaller fillets or chamfers." That is the catch-all remedy D-03 and the new test docstrings say a user must never read for a pipeline defect. The phase fixed this for the other five sites and left it in the sixth place that does the same thing. The plan said to note it as a tangent. It was not filed as debt, although CLAUDE.md requires non-blocking debt to be filed in `docs/tech_debt/active/` and the final reply to say so.
2. **Wrong claim in the docs.** `implementation.md` ("stops at two checked boundaries") and L35 ("Vendor shape typing stops at two checked boundaries") are false as written. There are three `isinstance` narrowings of vendor shapes in `model.py`, and only two use the helpers.
3. **Stale comment.** "for mypy only (cli.py's precedent)" contradicts the new house pattern a few hundred lines below. A reader now sees two different idioms for the same problem.
4. **Duplicated mechanism.** `_shape_of` does the same `.val()` check but cannot be reused because it returns `cq.Shape` rather than `cq.Solid`.

**Fix:** Either fold it into the pattern or file it. The minimal fold, with no new helper:

```python
proto = _shape_of(cq.Workplane("XY").polygon(6, size, circumscribed=True)
                  .extrude(p.face_width))
if not isinstance(proto, cq.Solid):
    raise BuildError(_NOT_A_BODY.format(type(proto).__name__))
```

Then correct the "two boundaries" sentence in `implementation.md` and L35. If you leave the code (D-16 forbids touching cuts), file `docs/tech_debt/active/YYYY-MM-DD-cell-cutters-typeerror-is-relabelled.md`, add the INDEX row, and reword the two doc sentences to "the two helpers" instead of "two boundaries".

### WR-02: The `no-fake-done` pin misses the spellings and files mypy accepts

**File:** `Makefile:74`
**Issue:** The pin is `git grep -nE 'type: ignore' -- 'src/spur/*.py'`. The comment above it and the L35 text claim "a sixth cannot arrive unseen". It can, in three ways.

1. mypy accepts `# type:ignore[...]` with no space, and the pin does not match it.
2. `# mypy: ignore-errors` (whole-file) and `# pyright: ignore` pass the pin untouched.
3. `git grep` without `--untracked` only searches tracked files. A new, not yet `git add`ed module under `src/spur/` is invisible to a `make verify` run by hand.

A plain `type:ignore` is the likeliest accidental form, since an editor or LLM can emit it without the space. L35 states the pin's reach as fact, and the reach is smaller than stated.

**Fix:**

```make
@if git grep -nEi --untracked 'type:[[:space:]]*ignore|mypy:[[:space:]]*ignore-errors' -- 'src/spur/*.py'; then \
```

Keep the existing echo text. Re-prove it RED against `085e5a6`'s five lines as before. Then either keep L35's wording, or narrow it to "refuses `type: ignore` and `mypy: ignore-errors`".

## Info

### IN-01: `_body`'s comment overstates what it asserts

**File:** `src/spur/model.py:420-426`
**Issue:** The comment says `_body` "asserts the invariant _build()'s end check asserts". `_build`'s end check asserts `len(solids) == 1 and solids[0].isValid()`. `_body` asserts that the shape is a `Solid` or `Compound`, which is a weaker and different property. "cannot fire from any settable field" is stated as fact, but the measurement cited covers only the default gear. The 44-record fixture replay is the real evidence for the other rows, and the comment does not cite it. This matters here because the comments are meant to carry the measurement behind each claim.
**Fix:** Reword to "the type the pipeline already guarantees (a Solid after `_gear_blank`, a Compound after every boolean)". Cite the fixture replay as the evidence beyond the default gear, or drop "cannot fire from any settable field".

### IN-02: The mypy comparison behind D-04 covers only the pinned kernel, while `pyproject.toml` declares `cadquery>=2.5`

**File:** `pyproject.toml:13` and `pyproject.toml:111-117`
**Issue:** Dropping `cadquery.*` from the override is verified byte-identical at cadquery 2.8.0 only. That is the version `requirements.txt` pins, and the gate installs it. The declared range reaches back to 2.5. ASSUMPTION, not checked: if any version in that range lacks `py.typed`, a developer on an unpinned install now gets `missing library stubs or py.typed marker` for every `import cadquery`, where the old override silenced it. The comment states "cadquery ships py.typed" without saying from which version.
**Fix:** Say "cadquery 2.8.0 ships py.typed" in the comment. Optionally check the first release that carries the marker and raise the lower bound to it.

### IN-03: The refusal tests prove the helpers in isolation, not that the call sites reach them

**File:** `tests/test_model.py:250-273`
**Issue:** Both tests call `_body` and `_shape_of` directly. mypy would catch removal of a `_body` call at a fillet/chamfer site. Nothing catches replacing the `_shape_of` call in `_ring` or `_cut_bore` with a different `.val()` path. That is acceptable under D-06, and the AST check in the plan covered it once. I note it because the AST check was a one-off in the plan's verify step and nothing keeps it in the suite.
**Fix:** No change needed if D-06 stands. Otherwise add one test that monkeypatches `spur.model._shape_of` to raise and asserts `build(GearParams(recess_depth=...))` fails with that message, which proves the wiring.

---

_Reviewed: 2026-10-05_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
