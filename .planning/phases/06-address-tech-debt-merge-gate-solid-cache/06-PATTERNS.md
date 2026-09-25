# Phase 6: Address tech debt: merge gate + solid cache - Pattern Map

**Mapped:** 2026-09-25
**Files analyzed:** 11 (0 new — every file is an in-place edit)
**Analogs found:** 11 / 11 — every analog is in-file (the file's own pre-existing sibling
cases/functions), per CONTEXT.md/RESEARCH.md: this phase creates no new module, so the
"closest existing analog" for each touched file is almost always itself, at an earlier
line range.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|-----------------|---------------|
| `scripts/skip_tokens.py` (`main`, D-02/D-03) | utility (git hook entry) | transform (text in, exit code out) | itself — `find_skip_tokens` (already cut-free, called unchanged) | exact (in-file) |
| `tests/test_skip_tokens.py` (D-02/D-03 cases) | test | transform | itself — the existing `TOKEN_SUBJECTS`/cut-line parametrized cases (lines 25-38, 114-176) | exact (in-file) |
| `scripts/pr_land.py::head_refusals` (D-04) | service (pure decision core) | transform (parsed JSON in, `list[str]` refusals out) | itself — the per-job loop in the same function (lines 286-292) | exact (in-file) |
| `scripts/pr_land.py::land` step 5 (D-06) | service (thin network shell) | request-response (poll loop over `Runner`) | itself — the existing poll loop (lines 444-466) and step-6 `print`/refusal shape (467-510) | exact (in-file) |
| `scripts/pr_land.py` module docstring (D-07) | config/doc | — | itself — the docstring's own "Which of its checks the ruleset duplicates" paragraph (lines 10-23) | exact (in-file) |
| `tests/test_pr_land.py` (D-04/D-05/D-06 cases) | test | transform / request-response | itself — `head_refusals` pure cases (255-399), the drift test (188-209), the `land()` `FakeRunner` cases (564-769) | exact (in-file) |
| `src/spur/model.py::_write_export`/`export` (D-08) | service (CAD kernel doorway) | transform (solid in, bytes out; must not mutate its input) | itself — `_write_export` (267-276) / `build`/`export` (262-283) | exact (in-file) |
| `tests/test_model.py` (D-08 case) | test | transform | itself — `test_builds_one_valid_solid` (27-33, the `.BoundingBox().zlen` assertion) and `_stl_triangles`/`test_exported_stl_is_a_closed_consistently_oriented_shell` (65-91, the content-equivalence pattern) | exact (in-file) |
| `tests/conftest.py` (D-09, fixture deletion) | test fixture | — | itself — the `_reset_root_logger` autouse fixture (37-46) stays as the shape for "what an autouse fixture here looks like" once `_reset_solid_cache` (49-51) is gone | exact (in-file) |
| `docs/HOW_TO_DEVELOP.md` §6/§8 (D-03/D-04/D-07) | config/doc | — | itself — §0's existing `L22` bullet (lines 27-30) and §8's existing ruleset/`pr.land` prose (138-212) | exact (in-file) |
| `docs/architecture/decision_log.md` (D-10, new L24[+L25]) | config/doc | append-only | `## L23 — Python 3.12 only` (line ~483 onward) and `## L22` (line 453 onward) — the two most recent entries, both same file | exact (in-file) |
| `docs/tech_debt/active/*.md` -> `resolved/*.md` (D-01, 5 files) | config/doc | — | `docs/tech_debt/resolved/2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md` | exact |
| `docs/tech_debt/INDEX.md` (row moves, 5 rows) | config/doc | — | itself — the existing `## Resolved` table rows | exact (in-file) |
| `.planning/STATE.md` (D-11) | config/doc | — | itself — the existing "Resolved in Phase 5" parenthetical (line 174) | exact (in-file) |

## Pattern Assignments

### `scripts/skip_tokens.py::main` (D-02, D-03)

**Analog:** itself — `find_skip_tokens` (unchanged, lines 68-75) and the current `main`
(lines 78-117), read this session.

**Current shape to remove** (lines 90-102, the `editor_ran` cut):
```python
editor_ran = os.environ.get("GIT_EDITOR") != ":"
tokens = find_skip_tokens(message_to_check(raw) if editor_ran else raw)
```

**Target shape** (D-02 — whole buffer, no cut, `os` import and `_SCISSORS`/`message_to_check`
go with it per Claude's discretion on `message_to_check`'s fate):
```python
raw = Path(args.message_file).read_text(encoding="utf-8", errors="replace")
tokens = find_skip_tokens(raw)   # no cut, ever
```

**Refusal-message pattern to extend** (lines 106-116 — keep the shape, add the D-03 `-v`
sentence and name the matched token + its line number, per CONTEXT.md D-03 "names the
matched token and line"):
```python
print("make: this commit message carries a GitHub Actions skip token:")
for token in tokens:
    print(f"      {token!r}")
print("      A skip token here silences CI on this commit, and on a PR head it")
print("      leaves the PR with zero checks.")
print('      Describe it in words instead ("a GitHub Actions skip token") -- do not')
print("      write the literal token.")
print(
    "      See docs/tech_debt/resolved/"
    "2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md."
)
return 1
```
D-03 adds one more `print(...)` line here: the `-v` caveat ("if this came from `-v`'s
appended diff, commit without `-v`"), plus — per D-03's "names the matched token and
line" — locating each token's 1-based line number in `raw` (e.g.
`raw[: m.start()].count("\n") + 1` per match) and printing it alongside the token.

**Import-block pattern** (lines 30-35, unchanged except `os` drops once `GIT_EDITOR` is
no longer read):
```python
from __future__ import annotations

import argparse
import re
from pathlib import Path
```

**Docstring pattern to correct** (lines 15-22, 47-58 — the module docstring's own
description of the two-caller/cut design must be rewritten to say there is no cut,
matching D-02; the `_SCISSORS` comment block, lines 47-58, is deleted with the regex).

---

### `tests/test_skip_tokens.py` (D-02 new/flipped cases)

**Analog:** itself — the existing parametrized/cut-line cases in the same file.

**Case shape to keep as-is** (lines 35-38, every token form — untouched, `find_skip_tokens`
does not change):
```python
@pytest.mark.parametrize("message", TOKEN_SUBJECTS)
def test_each_token_form_alone_in_a_one_line_subject_is_found(message: str) -> None:
    """Every one of the six tokens GitHub Actions honours (D-02) is found on its own."""
    assert find_skip_tokens(message) != []
```

**Cases to invert** (lines 114-139 and 160-177 — these currently assert `main([...]) == 0`
for a token below a cut line in an editor session; D-02 flips the assertion to `== 1` and
the docstrings to "refused below a cut line", collapsing the `GIT_EDITOR` parametrization
since editor-vs-not no longer matters):
```python
@pytest.mark.parametrize("git_editor", ["vi", None])
def test_token_only_below_the_scissors_line_gives_no_tokens(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, git_editor: str | None,
) -> None:
    ...
    assert main([str(path)]) == 0
```
becomes (per CONTEXT.md D-02: "A new test proves a token *below* a git-shaped cut line is
refused regardless of `GIT_EDITOR`"): parametrize the same two `git_editor` values, keep
the same message fixture, assert `main([str(path)]) == 1` and that the token is named in
`capsys` output — one `FakeRunner`-style case per value, same pattern as
`test_hook_without_an_editor_refuses_a_token_below_a_cut_line` (lines 160-177) already
does for the `GIT_EDITOR=":"` case.

**Case to remove:** `test_message_to_check_returns_all_of_raw_when_there_is_no_scissors_line`
(179-181) — only if `message_to_check` is deleted (Claude's discretion, D-02 notes).

**`-v`-caveat assertion to add** (D-03 — extend
`test_token_above_and_below_the_scissors_line_is_found_once`-style, lines 142-157, which
already captures `capsys` on a refusal):
```python
def test_token_above_and_below_the_scissors_line_is_found_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    ...
    assert main([str(path)]) == 1
    assert capsys.readouterr().out.count("'[skip ci]'") == 1
```
D-03's new assertion in a case that puts the token in the `-v`-diff-shaped tail: the
output contains the caveat sentence (e.g. `"-v"` and `"commit without"` both present).

**Subprocess-entry pattern to reuse unchanged** (`_run_hook`, lines 188-195 — every new
`main()`-level case can use this helper exactly as the existing `test_hook_entry_*` cases
do, lines 198-229).

---

### `scripts/pr_land.py::head_refusals` (D-04)

**Analog:** itself — the function's own existing per-job loop, same file, lines 256-293
(already read live, reproduced in RESEARCH.md's "Code Examples" verbatim from this
session).

**Signature and current core** (lines 256-293):
```python
def head_refusals(
    sha: str,
    compare: tuple[int, int],
    run: WorkflowRun | None,
    jobs: list[dict[str, str]],
    required: frozenset[str],
) -> list[str]:
    ...
    if run is None:
        refusals.append(f"pr.land: no {WORKFLOW} run for head {sha}.")
        return refusals
    if run.status != "completed":
        refusals.append(f"pr.land: the newest run for {sha} is still running: {run.html_url}")
        return refusals
    by_name = {job["name"]: job["conclusion"] for job in jobs}
    for name in sorted(required):
        conclusion = by_name.get(name)
        if conclusion is None:
            refusals.append(f"pr.land: required job {name!r} is missing from the run.")
        elif conclusion != "success":
            refusals.append(f"pr.land: required job {name!r} is {conclusion}, not success.")
    return refusals
```

**D-04's insertion point** — after the `status != "completed"` early return, before the
per-job loop, in addition to it (not instead of it, per D-04: "in addition to the per-job
check, which stays because it is what names a *missing* job"):
```python
if run.conclusion != "success":
    refusals.append(
        f"pr.land: the newest run for {sha} concluded {run.conclusion!r}, not "
        f"success: {run.html_url}"
    )
```
`run.conclusion` is already parsed as `str | None` by `parse_runs` (lines 149-168,
`WorkflowRun.conclusion` field, line 94) — no parser change needed, only a new read in
`head_refusals`.

**No-signature-change note:** `head_refusals` already receives `run: WorkflowRun | None`
in full — D-04 is a body-only change, no new parameter (unlike D-04's neighbour, `compare`,
which RESEARCH.md's own example comment notes was added by an earlier task).

---

### `tests/test_pr_land.py` — `head_refusals` cases (D-04)

**Analog:** itself — `test_head_refusals_one_red_job_names_it_and_its_conclusion`
(284-297) and `test_head_refusals_several_problems_at_once_prints_both_lines` (349-362),
same file.

**Case shape to copy** (lines 284-297 — the exact structure a new
`test_head_refusals_run_conclusion_failure_is_refused_even_with_every_job_green`-style
case follows):
```python
def test_head_refusals_one_red_job_names_it_and_its_conclusion() -> None:
    run = WorkflowRun(id=1, status="completed", conclusion="failure", html_url="u")
    jobs = [
        {"name": "test (3.12)", "conclusion": "failure"},
        {"name": "vendor-bundle", "conclusion": "success"},
        {"name": "image", "conclusion": "success"},
    ]
    refusals = head_refusals(PR3_HEAD_SHA, NOT_BEHIND, run, jobs, REQUIRED)
    assert len(refusals) == 1
    assert "test (3.12)" in refusals[0]
    assert "failure" in refusals[0]
```
D-04's new case: `run = WorkflowRun(id=1, status="completed", conclusion="failure",
html_url="u")` (the "unlisted failing job" scenario the debt file names) with `jobs` all
`success` for every name in `REQUIRED` — asserts the new run-conclusion refusal fires even
though the per-job loop alone would find nothing. Fixture data pattern to reuse:
`NOT_BEHIND` (line 159), `REQUIRED` (line 155), the `WorkflowRun` dataclass import
already at the top (line 31).

---

### `scripts/pr_land.py::land` step 5 (D-06)

**Analog:** itself — the existing poll loop (444-466) and the final report branch
(502-510), same file.

**Current poll + report shape** (444-466, 502-510):
```python
found_run: WorkflowRun | None = None
for attempt in range(attempts):
    poll_result = run([...])
    if poll_result.returncode == 0:
        try:
            found_run = newest_run(parse_runs(poll_result.stdout))
        except ValueError:
            found_run = None
        if found_run is not None:
            print(found_run.html_url)
            break
    if attempt < attempts - 1:
        sleep(interval_s)
...
if found_run is not None and not step6_failed:
    return 0
if found_run is None:
    print(
        f"pr.land: PR #{pr_number} IS merged as {squash_sha}, but no {WORKFLOW} run "
        f"appeared within {attempts * interval_s:.0f} s -- a skip token reached "
        "main (L22)"
    )
return 1
```

**D-06's three-branch replacement** (keep the poll loop's structure; track the last read
error the way `check_head` already does — `f"...failed: {result.stderr.strip()}"`, same
message-building idiom as lines 310/327/346-349 — then branch the final report):
```python
last_error: str | None = None
found_run: WorkflowRun | None = None
for attempt in range(attempts):
    poll_result = run([...])
    if poll_result.returncode != 0:
        last_error = poll_result.stderr.strip()
    else:
        try:
            found_run = newest_run(parse_runs(poll_result.stdout))
        except ValueError as exc:
            last_error = str(exc)
            found_run = None
        if found_run is not None:
            print(found_run.html_url)
            break
    if attempt < attempts - 1:
        sleep(interval_s)
...
if found_run is not None and not step6_failed:
    return 0
if found_run is None:
    if last_error is not None:
        print(
            f"pr.land: PR #{pr_number} IS merged as {squash_sha}, but no {WORKFLOW} run "
            f"was observed within {attempts * interval_s:.0f} s; last error: {last_error}"
        )
    else:
        msg_result = run(
            ["gh", "api", f"repos/{{owner}}/{{repo}}/commits/{squash_sha}",
             "--jq", ".commit.message"]
        )
        tokens = find_skip_tokens(msg_result.stdout) if msg_result.returncode == 0 else []
        if tokens:
            print(
                f"pr.land: PR #{pr_number} IS merged as {squash_sha}, but its commit "
                f"message carries a GitHub Actions skip token: {tokens[0]!r}."
            )
        else:
            print(
                f"pr.land: PR #{pr_number} IS merged as {squash_sha}, but no {WORKFLOW} "
                f"run appeared within {attempts * interval_s:.0f} s. Check "
                f"https://github.com/{{owner}}/{{repo}}/actions."
            )
return 1
```
(Placeholder `{{owner}}/{{repo}}` matches the module's existing convention at lines
303-304, 320-321, 340, 450-451 — same literal string, not f-string-interpolated, confirmed
by reading those call sites this session.) The exact `gh api` call and JSON path is
verified live in RESEARCH.md's Code Examples section:
`gh api repos/{owner}/{repo}/commits/<squash_sha> --jq '.commit.message'`.

**`find_skip_tokens` reuse** — already imported at line 48
(`from scripts.skip_tokens import find_skip_tokens`) and already called unchanged at line
248 in `message_refusals`; D-06 is the second call site in this module, same import, no
new dependency.

---

### `tests/test_pr_land.py` — `land()` poll-report cases (D-06)

**Analog:** itself — `_happy_runner` (564-595) and
`test_land_poll_timeout_reports_merged_but_no_run` (617-627), same file.

**`FakeRunner` queue pattern to copy** (`.on(..., cp(...), cp(...))` — first response then
repeats, already documented in the `FakeRunner` docstring, lines 55-59, and exercised at
579-587 for the "no run, then a run" shape):
```python
.on(
    "runs?head_sha=deadbeef1234",
    cp(0, "[]"),
    cp(0, '[{"id":1,"status":"completed","conclusion":"success", ...}]'),
)
```

**Existing timeout case to extend into three** (617-627 — this is the one to split per
D-06's three branches):
```python
def test_land_poll_timeout_reports_merged_but_no_run(capsys: pytest.CaptureFixture[str]) -> None:
    runner = _happy_runner().replace("runs?head_sha=deadbeef", cp(0, "[]"))
    sleeps: list[float] = []
    result = land(3, runner, attempts=3, interval_s=1.0, sleep=sleeps.append)
    assert result == 1
    assert sleeps == [1.0, 1.0]  # attempts - 1
    out = capsys.readouterr().out
    assert "IS merged" in out
    assert "deadbeef1234" in out
    assert "no ci.yml run appeared" in out
```
D-06's three variants, same `_happy_runner().replace(...)` idiom:
1. **Reads failed:** `.replace("runs?head_sha=deadbeef", cp(1, "", "gh: rate limited"))` —
   assert `"last error"` and `"gh: rate limited"` in output.
2. **Reads succeeded, empty:** the existing case above (rename to
   `test_land_poll_reads_succeed_but_no_run_appears_names_the_actions_url`), assert the
   Actions URL is printed, per D-06.
3. **Token named:** add a `.on("commits/deadbeef1234", cp(0, '"chore [skip ci]"'))`
   handler (the `gh api commits/<sha> --jq .commit.message` shape) on top of the
   empty-runs replace; assert the token is named in the output. `.replace()`'s substring
   match (line 73-77) already supports layering a new handler this way.

---

### `scripts/pr_land.py` module docstring (D-07)

**Analog:** itself — the docstring's existing "Which of its checks the ruleset
duplicates" paragraph, lines 10-23.

**Text to extend, not replace** (per RESEARCH.md Pitfall 2's warning about D-03's
"correction" language — the docstring is accurate today, D-07 *adds* the split, it does
not fix a wrong claim):
```
Steps, in order: (1) read and parse the PR, refuse on its state/base; (2) refuse a
dirty working tree; (3) `check_head` -- refuse a behind, run-less, unfinished or
non-green head, and refuse a skip token in the checked subject/body
(`message_refusals`); (4) squash-merge with the exact subject and body just
checked; (5) poll for a run on the squash commit (~60 s,
`POLL_ATTEMPTS * POLL_INTERVAL_S`) and print its URL; (6) the local follow-up --
```
D-07 adds one paragraph after this: step 5 proves the run *appeared* for the squash
commit, not that the merge landed the checked tree — that half rests on the ruleset's
strict up-to-date policy (Phase 5 D-12, no bypass actors); `--match-head-commit` pins
the merge to the head `pr.land` itself checked, not to `main`'s current tip.

---

### `src/spur/model.py::_write_export` (D-08)

**Analog:** itself — the current function, lines 267-276.

**Current shape:**
```python
def _write_export(shape: cq.Solid, p: GearParams, fmt: Format, quality: Quality) -> bytes:
    with tempfile.TemporaryDirectory(prefix="spur-") as d:
        path = Path(d) / f"{p.slug()}.{fmt}"
        if fmt == "stl":
            tol, ang = TESSELLATION[quality]
            shape.exportStl(str(path), tolerance=tol, angularTolerance=ang,
                            ascii=False, relative=False)
        else:
            shape.exportStep(str(path))
        return path.read_bytes()
```

**Target shape — D-08 amended-at-plan-time decision: `solid.copy()`, not `Clean_s`**
(CONTEXT.md's plan-time amendment overrides RESEARCH.md's `Clean_s` recommendation; copy
is the one whose invariant holds even before `build()` releases `_LOCK`):
```python
def _write_export(shape: cq.Solid, p: GearParams, fmt: Format, quality: Quality) -> bytes:
    with tempfile.TemporaryDirectory(prefix="spur-") as d:
        path = Path(d) / f"{p.slug()}.{fmt}"
        if fmt == "stl":
            tol, ang = TESSELLATION[quality]
            # Copy before meshing: exportStl attaches a mesh to whatever cq.Solid it is
            # called on. _build_cached hands out one process-global object per
            # GearParams (lru_cache) -- meshing it in place would leave every later
            # .BoundingBox() on the cache reading through the coarsest quality's mesh
            # instead of the exact BREP (measured drift: 7.5000 -> 7.5877mm zlen,
            # docs/tech_debt/resolved/2026-09-24-shared-solid-cache-corrupts-later-boundingbox.md).
            shape.copy().exportStl(str(path), tolerance=tol, angularTolerance=ang,
                                    ascii=False, relative=False)
        else:
            shape.exportStep(str(path))  # STEP export never attaches a mesh -- unaffected
        return path.read_bytes()
```
Pitfall 3 (RESEARCH.md) applies here: call `shape.copy()` with no positional argument
(`mesh` defaults to `False`) — never `shape.copy(True)`, which would copy the mesh too.

**Boundary discipline to preserve** (module docstring, lines 1-13, and `build`/`export`,
lines 262-283 — unchanged): the fix stays entirely inside `_write_export`; `cq.Solid`
still never crosses out of this module.

---

### `tests/test_model.py` (D-08 proof)

**Analog A — the `.BoundingBox()` assertion to extend:** `test_builds_one_valid_solid`
(27-33):
```python
def test_builds_one_valid_solid(kw: dict[str, object]) -> None:
    p = GearParams.model_validate(kw)
    s = build(p)
    assert s.isValid()
    bb = s.BoundingBox()
    assert bb.zlen == pytest.approx(p.face_width)
    assert max(bb.xlen, bb.ylen) <= p.module * (p.teeth + 2 + 2 * p.profile_shift) + 1e-6
```
D-08's new case reproduces the debt file's exact defect shape (RESEARCH.md's "Specifics":
`GearParams()` teeth=19, preview-then-fine export): `build()` once, `export(p, "stl",
"preview")` then `export(p, "stl", "fine")` on the *same* `p`, then re-read `.BoundingBox()`
on the object `build(p)` returns (same lru_cache entry) and assert `zlen ==
pytest.approx(p.face_width)` — proving the cache's own object is untouched after two
exports at different qualities.

**Analog B — content-equivalence, not byte-diff** (per CONTEXT.md's plan-time amendment
and RESEARCH.md Pitfall 1): `_stl_triangles` (65-70) and
`test_exported_stl_is_a_closed_consistently_oriented_shell` (73-91):
```python
def _stl_triangles(data: bytes) -> Iterator[Facet]:
    n = int.from_bytes(data[80:84], "little")
    assert len(data) == 84 + 50 * n, "truncated binary STL"
    for i in range(n):
        v = struct.unpack("<12fH", data[84 + 50 * i:134 + 50 * i])
        yield v[3:6], v[6:9], v[9:12]
```
D-08's proof, per the amendment, asserts on the *same* fixed export (triangle count via
`stl[80:84]`, the decoded-volume idiom at lines 85-87, and the watertight/consistently
oriented check at lines 89-91 — all already present in this file for exactly this
purpose) rather than a raw-byte diff against an independently-built control (which
RESEARCH.md's live 20-trial rerun found matches only 8/20 times on this toolchain).

**Import to add:** `_stl_triangles` and the `Facet` type alias (line 12) are already
module-level in this file — no new import needed if the D-08 test lives in the same file
(which it does per RESEARCH.md's Project Structure).

---

### `tests/conftest.py` (D-09)

**Analog:** itself — `_reset_root_logger` (37-46), the fixture that stays, as the shape
for what an autouse fixture here looks like once `_reset_solid_cache` is gone.

**To delete** (49-51, plus its docstring paragraph, lines 12-24, and the now-unused
`from spur.model import _build_cached` import, line 34):
```python
@pytest.fixture(autouse=True)
def _reset_solid_cache() -> None:
    _build_cached.cache_clear()
```
Per D-09: deletion is the fixing commit's own proof (the suite passing without it, run via
`make verify`, is the cross-test evidence the collision the debt file named — `test_model.py`'s
`kw={}` case against `test_api.py`'s default-gear export — is gone now that D-08 makes the
cache's object immutable regardless of export order).

---

### `docs/HOW_TO_DEVELOP.md` (D-03, D-04, D-07)

**Analog:** itself. This is a Russian-language doc; new sentences must match voice/register.

**§6 insertion point** (lines 119-124, the existing ship-note paragraph — D-03 adds one
sentence after it, in Russian, per CONTEXT.md D-03; no existing paragraph to correct, per
RESEARCH.md Pitfall 2 — this is new content, not a fix):
```
Коммит ship-note несёт `[ci skip]` в теме, и `no-skip-token`-хук (D-02) его отказывает:
`gsd-ship` печатает предупреждение и оставляет `.planning/STATE.md` изменённым, но
незакоммиченным. Закоммить руками: `docs(NN): ship phase N — PR #M`, без токена, и
`git push`.
```
D-03's added sentence (paraphrase of the hook's own `-v` caveat, in Russian): explain that
a `git commit -v` whose appended diff quotes a token is refused, and to commit without
`-v` or reword in that case.

**§8 insertion point** (lines 138-212 — D-04's rule and D-07's split both land in the
`make pr.land` prose paragraph starting "По порядку оно:", ~line 180-190): extend the list
of refusal conditions already narrated there ("отказывает, если у головы нет завершённого
зелёного прогона `ci.yml` на каждой проверке...") with the run-conclusion check (D-04), and
add D-07's split (`pr.land` proves the run appeared; the window before `gh pr merge` rests
on the ruleset, not on a second read) near the existing "merged, but no run appeared"
paragraph (~line 195-198).

---

### `docs/architecture/decision_log.md` (D-10)

**Analog:** `## L23 — Python 3.12 only (supersedes L01's floor)` (tail of file) and
`## L22 — CI is the merge gate...` (line 453) — both read in full this session; L23's own
structure (Date / body / "What changes" / "Rejected" / "Reversibility" / "Reason") is the
template to copy, since it is the most recent entry and explicitly supersedes/amends a
prior one the same way D-10 amends L22.

**Entry header pattern:**
```
## L23 — Python 3.12 only (supersedes L01's floor)

Date: 2026-09-25.

L01 recorded 3.10-3.12 as "detected, not chosen": ...
```
D-10's L24 (amends L22, stays additive per "L22 stays as written; a new entry amends"):
title along the lines of `## L24 — pr.land's run verdict includes the run's own
conclusion; the commit-msg hook has no cut (amends L22)`, Date: 2026-09-25, body
naming D-02 (whole-buffer hook) and D-04 (run-conclusion check) as what changed and why,
ending with a **Reversibility** paragraph (both D-02 and D-04 are individually marked
"reversible" in CONTEXT.md — carry that through). A second entry, L25, for the solid-cache
invariant (D-08) as "a design secret of `model.py`" per D-10 — its own **Reversibility**
paragraph: "reversible — local to `_write_export`" (from CONTEXT.md D-08).

**Append-only discipline** (confirmed this session: `git log`/file read shows L22, L23 are
both still present verbatim, never edited by a later entry) — new entries go at the file's
end, nothing above is touched.

---

### `docs/tech_debt/active/*.md` → `resolved/*.md` (D-01, 5 files)

**Analog:** `docs/tech_debt/resolved/2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md`
(full file read this session) — the canonical resolved-file shape.

**Frontmatter pattern (lines 1-11):**
```
# The ship-note's CI skip token leaks into the squash-merge commit and skips CI on `main`

Severity: must
Status: resolved
Date: 2026-09-25
Resolved in: fac76f5
Source: /gsd-ship 4 (PR #3) — observed on PR #2's history while shipping Phase 4
Related files:
- .github/workflows/ci.yml (`on: push: branches: [main]`, `pull_request`)
```
Each of the phase's five debt files gets: `Status: active` → `Status: resolved`,
`Resolved in: <sha>` added (the commit that fixes it, per CLAUDE.md — "a file cannot carry
its own commit's sha", so this is the *next* commit's sha if the fix and the doc move are
the very same commit, or note the pattern this analog uses when they are not identical).

**"## Resolution (date)" section pattern (lines 56-89):** a new trailing section, dated,
naming which option from the file's own "Next step" was taken, what now exists (module +
function + test file, one sentence each), and — per this analog's own final paragraph
(84-89) — the original "Context"/"Why it matters" sections stay as written, never edited to
match what is true after the fix.

**`git mv` + INDEX.md row move (D-01):** in the same commit as the fix, per CLAUDE.md and
D-01. `docs/tech_debt/INDEX.md`'s own `## Resolved` table (last section) is the row-shape
analog:
```
| [The ship-note's CI skip token leaks into the squash-merge commit and skips CI on `main`](resolved/2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md) | `fac76f5` — see the file's own `Resolved in:` field |
```
Each of the five active rows (already present in `## Active`, read this session — see
excerpt below) moves to a new row of this exact shape; the `## Active` table's own row for
that item is deleted in the same edit.

**The five active rows to move (verbatim, from `docs/tech_debt/INDEX.md`'s `## Active` table
read this session):**
```
| must | [A cached solid's `.BoundingBox()` reads wrong after it has been STL-exported](active/2026-09-24-shared-solid-cache-corrupts-later-boundingbox.md) | ... |
| must | [The commit-msg hook trusts a cut line typed by hand in an editor session](active/2026-09-25-commit-msg-hook-trusts-a-hand-typed-cut-line.md) | ... |
| must | [`make pr.land` judges a run by the listed jobs only, never by the run's own conclusion](active/2026-09-25-pr-land-admits-a-run-with-a-failing-unlisted-job.md) | ... |
| nice | [The required-jobs drift test reads job ids, so a `name:` override slips past it](active/2026-09-25-required-jobs-drift-test-ignores-job-name-overrides.md) | ... |
| nice | [`make pr.land` reports "a skip token reached main" for any run it failed to observe](active/2026-09-25-pr-land-blames-a-skip-token-for-any-missed-post-merge-run.md) | ... |
```

---

### `.planning/STATE.md` (D-11)

**Analog:** itself — the existing "Resolved in Phase 5" parenthetical, line 174.

**Text to extend (line 174-178, read this session):**
```
- *(Resolved in Phase 5: "CI workflow unverified" — the premise was false: main push run
  <https://github.com/halfb00t/spur/actions/runs/35963114939> (`59f02c3`, all four jobs
  green) and PR #3 head run <https://github.com/halfb00t/spur/actions/runs/36088409707>
  (`2c4b544`, tree-identical to `bfc9110`); L22's merge gate keeps it true, and this
  phase's own squash-commit run is recorded after `make pr.land` prints it.
```
D-11 appends, within the same parenthetical or immediately after it: a citation of run
36122394253 (push of `b72b0e1`, the three current jobs — `test (3.12)`, `vendor-bundle`,
`image` — green), matching the existing citation style (run URL + head sha + job-set
description).

## Shared Patterns

### Pure decision core / thin network shell (`scripts/pr_land.py`, established Phase 5)
**Source:** `scripts/pr_land.py` lines 70-76 (the `Runner` type alias) and the whole
`head_refusals`/`pr_refusals`/`message_refusals` trio (227-293).
**Apply to:** D-04 (new refusal inside `head_refusals`) and D-06 (new report branches
inside `land`'s step 5) — both extensions of this one seam; do not open a second way to
reach `gh`.
```python
Runner = Callable[[list[str]], "subprocess.CompletedProcess[str]"]
```
Every new `gh api` call (D-06's `commits/<sha>` read) goes through the `run: Runner`
parameter `land()` already threads through, exactly like every existing call at lines
369-377, 397-402, 413-427, 433-435, 446-455.

### `FakeRunner` test seam (`tests/test_pr_land.py`, established Phase 5)
**Source:** lines 54-87.
**Apply to:** every new `land()`-level test case (D-04's run-conclusion scenario surfaced
through `check_head`, D-06's three report-branch cases). Register a handler with
`.on(substring, *responses)`; use `.replace(substring, *responses)` (lines 69-77) to swap
one leg of the existing `_happy_runner()` fixture without rebuilding it, exactly as the
existing poll-timeout/local-follow-up variant tests already do (lines 618, 630, 640).

### One doorway to the kernel (`src/spur/model.py`, established Phase 2)
**Source:** module docstring lines 1-13; enforced by import-linter contracts at
`pyproject.toml:150-165` (model.py exempted from the `spur.cadquery`-forbidden rule that
binds `spur.calc`/`spur.params`/`spur.cli`/`spur.app`).
**Apply to:** D-08 — the fix must stay inside `_write_export`; no `cq.Solid` or `OCP` type
may leak into `app.py`/`pool.py`/any other module.

### `find_skip_tokens` as the single skip-token authority (established 05-06)
**Source:** `scripts/skip_tokens.py` lines 68-75 (the function itself, unchanged by this
phase) — already called from two sites: `scripts/skip_tokens.py::main` (the hook) and
`scripts/pr_land.py::message_refusals` (line 248).
**Apply to:** D-06's new third call site (the squash-commit-message check in `land`'s
step 5) — reuse the same function, same import shape
(`from scripts.skip_tokens import find_skip_tokens`, already present at
`scripts/pr_land.py:48`), never a second regex.

### Tech-debt resolution lifecycle (established, every prior resolved file)
**Source:** `docs/tech_debt/resolved/2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md`
(frontmatter + trailing "## Resolution" section), `docs/tech_debt/INDEX.md`'s
`## Resolved` table shape.
**Apply to:** all five debt files this phase closes (D-01) — `Status: resolved` +
`Resolved in: <sha>` + `git mv` into `resolved/` + INDEX row moved, all in the commit that
fixes the underlying issue (never a follow-up, per CLAUDE.md and D-01).

## No Analog Found

None. Every file this phase touches already exists with a same-file sibling
pattern to copy (RESEARCH.md's own "Key insight": every "Next step" in the five debt
files is a small, local, same-file edit — there is no new module, no new role, and
therefore no file lacking an in-file precedent).

## Metadata

**Analog search scope:** `scripts/`, `tests/`, `src/spur/model.py`, `docs/HOW_TO_DEVELOP.md`,
`docs/architecture/decision_log.md`, `docs/tech_debt/{active,resolved}/`,
`docs/tech_debt/INDEX.md`, `.planning/STATE.md`, `.github/workflows/ci.yml` — every
directory CONTEXT.md/RESEARCH.md name as touched by this phase; no other directory was
searched because RESEARCH.md's own Architecture Patterns section already confirms no new
file/module is created.
**Files scanned:** 11 touched files read in full this session (`scripts/skip_tokens.py`,
`scripts/pr_land.py`, `tests/test_skip_tokens.py`, `tests/test_pr_land.py`,
`src/spur/model.py`, `tests/test_model.py`, `tests/conftest.py`), plus
`docs/HOW_TO_DEVELOP.md` (§0, §6-§8), `docs/architecture/decision_log.md` (tail, L22-L23),
`docs/tech_debt/INDEX.md`, `docs/tech_debt/resolved/2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md`,
`.planning/STATE.md` (line 168-180), `.github/workflows/ci.yml` (lines 1-63).
**Pattern extraction date:** 2026-09-25.
</content>
