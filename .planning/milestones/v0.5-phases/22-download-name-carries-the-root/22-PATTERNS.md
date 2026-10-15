# Phase 22: Download Name Carries the Root - Pattern Map

**Mapped:** 2026-10-11
**Files analyzed:** 11 (1 production, 4 test files, 6 docs/bench)
**Analogs found:** 11 / 11
**Verified against:** working tree, branch `gsd/phase-22-download-name-carries-the-root`. All analog paths are git-tracked (`git ls-files` checked for the idea file and `tests/test_calc.py`; the rest are ordinary tracked source).

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `src/spur/params.py` (`slug()`, `:190`) | model method | transform | `GearParams._feasible` (`params.py:179-180`, local `calc` import) + `calc.root_mode` callers (`calc.py:1086`, `model.py:773`) | exact |
| `tests/test_calc.py` (new `slug()` tests) | test | transform | `tests/test_trochoid.py:176-200` (`tip land gone` params, `_gear`, `root_mode` call) | exact |
| `tests/test_api.py` (flip `:411-412`, rewrite docstring `:376-381`) | test | request-response | same test, edited in place | exact |
| `tests/test_api.py` (new parametrized header test) | test | request-response | `test_model_download` (`:712-720`) | exact |
| `tests/test_api.py` (`build.failed` trochoid sibling) | test | event-driven | `test_a_failed_build_emits_build_failed_...` (`:1059-1100`) | exact |
| `tests/test_browser.py` (new `download name` step) | test (e2e) | request-response | `golden sweep` step (`:526-556`, own `browser.new_page()` + `finally: close`) and `first build drawn` (`:328-350`, href wait) | role-match |
| `tests/browser_session.py` (comment only, `:36-47`, `serve_stl_from`) | config/comment | n/a | its own `BUILD_WAIT_MS` comment | exact |
| `docs/architecture/http-api.md` (`:43`, `:93`) | doc | n/a | the existing table row | exact |
| `docs/architecture/decision_log.md` (new `L40`) | doc | n/a | `L39` (`:2299`), `L38` (`:2091`) | exact |
| `docs/ideas/2026-10-08-download-name-carries-the-root-shape.md` -> `retired/`, `docs/ideas/INDEX.md` | doc | n/a | `docs/ideas/retired/2026-09-21-browser-test-for-the-viewer.md` | exact |
| `bench/RESULTS.md` (new `## Download name carries the root (Phase 22)`) | doc | n/a | `### The browser test, priced (21-07)` (`:5030`) | exact |

Also edited per RESEARCH Open Question 3: `.planning/REQUIREMENTS.md:107` and the ROADMAP SC3 line (`docs/http-api.md` -> `docs/architecture/http-api.md`).

## Pattern Assignments

### `src/spur/params.py` `slug()` (model method, transform)

**Analog 1:** `GearParams._feasible`, `src/spur/params.py:179-180`. The local-import idiom (module-level would be circular: `calc` imports `GearParams` for typing only, `calc.py:14-16`).
```python
    @model_validator(mode="after")
    def _feasible(self) -> GearParams:
        from .calc import check  # local import: calc only needs the attributes
```

**Current body to replace** (`params.py:190-192`):
```python
    def slug(self) -> str:
        """Short, filename-safe identifier."""
        return f"spur_z{self.teeth}_m{self.module:g}_pa{self.pressure_angle:g}"
```

**Analog 2, the predicate call** (`calc.py:1086`, `calc.py:354`, `model.py:773` all read identically):
```python
rm = root_mode(p, pr, requested=p.root_shape, rho=p.root_fillet)
```
`root_mode` signature (`calc.py:1662-1663`): `def root_mode(p: GearParams, pr: Profile, *, requested: RootShape = "radial", rho: float = 0.0) -> RootMode`. It returns at `calc.py:1690` (`if requested != "trochoid":`) before the cutter is built, so a radial request costs no solver work. `RootMode.mode` is `"radial" | "trochoid"`.

**Target shape** (RESEARCH "Code Examples", prototyped; comment should carry the measured cost 2.3 us radial / 5.3 us ignored or refused / 39 us applies, per `docs/CODING_VALUES.md`):
```python
    def slug(self) -> str:
        from .calc import profile, root_mode  # local import: calc imports GearParams

        name = f"spur_z{self.teeth}_m{self.module:g}_pa{self.pressure_angle:g}"
        rm = root_mode(self, profile(self), requested=self.root_shape, rho=self.root_fillet)
        return f"{name}_trochoid" if rm.mode == "trochoid" else name
```
No `try/except` (D-02). Do not test `self.root_shape` alone (SL-2). `app.py:496`, `records.py:180`, `model.py:807` are not edited.

---

### `tests/test_calc.py` new pure `slug()` tests (test, transform)

**Analog:** `tests/test_trochoid.py:85-88` (`_gear` helper) and `:176-200` (the refused case).

`_gear` (`test_trochoid.py:85-88`); `test_calc.py` has no such helper, so build the params inline or copy it:
```python
def _gear(**fields: object) -> GearParams:
    """A test gear with the bore off: the default 9 mm bore refuses small gears."""
    return GearParams.model_validate(
        {"bore_d": 0, "bore_flat": 0, "bore_chamfer": 0, "recess_sides": "none", **fields})
```
`tip land gone` fields (`test_trochoid.py:176-179`; CONTEXT's `:188` is the docstring, the params are here):
```python
pytest.param({"teeth": 19, "module": 1.75, "profile_shift": -0.4, "backlash": 0.10,
              "pressure_angle": 33.5}, False, "The cutter has no tip land ...",
             id="default-backlash-33.5-has-none"),
```
`root_mode` call in tests (`test_trochoid.py:195`): `rm = root_mode(p, profile(p), requested="trochoid", rho=0.0)`.

**Imports available in `tests/test_calc.py`:** `from spur.calc import (..., profile, ...)` at `:29-56` (no `root_mode` yet; add it only if a test asserts against the predicate) and `from spur.params import GearParams` at `:58`. File sits in the commit slice (`make test.fast`).

**Cases to assert (literal names, a filename pin is a literal by design):** refused (`teeth=19, ... pressure_angle=33.5, root_shape=trochoid`, bore off) -> `spur_z19_m1.75_pa33.5`; 40 teeth trochoid -> `spur_z40_m1.75_pa25`; 23 teeth trochoid -> `spur_z23_m1.75_pa25_trochoid`; optionally the radial default -> `spur_z21_m1.75_pa25`. Threshold: hob root applies up to 26 teeth at defaults, ignored from 27 (RESEARCH). Parametrize over the three cases.

---

### `tests/test_api.py` flip of the existing pin (test, request-response)

**Analog:** the test itself, `test_a_root_shape_link_is_served_with_the_root_it_cut`, `:371-412`.

Docstring sentence to rewrite (`:376-381`, now false): "The download's slug is the same as the radial gear's: it ignores root_shape (19-RESEARCH Open Question 6, filed as an idea by 19-11, not changed here)."

Assertions (`:407-412`):
```python
    radial = client.get("/api/model.stl", params={"teeth": 23, "quality": "preview"})
    r = client.get("/api/model.stl", params={"teeth": 23, "root_shape": "trochoid",
                                             "quality": "preview"})
    assert r.status_code == 200
    assert r.headers["content-type"] == "model/stl"
    assert len(r.content) > 84
    assert r.content != radial.content  # a different root is a different part
    assert r.headers["content-disposition"] == radial.headers["content-disposition"]   # :411 now FALSE, delete (or invert to !=)
    assert 'filename="spur_z23_m1.75_pa25.stl"' in r.headers["content-disposition"]    # :412 -> ..._trochoid.stl
```
Keep `:410` (`r.content != radial.content`; it proves the cache did not answer both). `:411` is not in CONTEXT; RESEARCH Open Question 2 covers it.

---

### `tests/test_api.py` new parametrized header test (test, request-response)

**Analog:** `test_model_download`, `tests/test_api.py:712-720`. Copy the `(fmt, ctype, magic)` table and the header-equality shape.
```python
@pytest.mark.parametrize(("fmt", "ctype", "magic"), [
    ("stl", "model/stl", None),
    ("step", "model/step", b"ISO-10303-21;"),
])
def test_model_download(fmt: str, ctype: str, magic: bytes | None) -> None:
    r = client.get(f"/api/model.{fmt}", params={"quality": "preview", "teeth": 21})
    assert r.status_code == 200
    assert r.headers["content-type"] == ctype
    assert r.headers["content-disposition"] == f'attachment; filename="spur_z21_m1.75_pa25.{fmt}"'
    if magic:
        assert r.content.startswith(magic)
```
Add a second stacked `parametrize(("teeth", "stem"), [(23, "spur_z23_m1.75_pa25_trochoid"), (40, "spur_z40_m1.75_pa25")])`, send `root_shape=trochoid` with `quality=preview`, assert `== f'attachment; filename="{stem}.{fmt}"'`. Do NOT touch `:720`. Full draft is in RESEARCH "Code Examples".

---

### `tests/test_api.py` `build.failed` trochoid sibling (test, event-driven)

**Analog:** `test_a_failed_build_emits_build_failed_naming_the_class_and_the_level`, `:1059-1100`. Copy the override pattern, `caplog.set_level(logging.INFO)`, the `finally` restore, and the `_event_records` / `_field` helpers.
```python
    async def backend(p: GearParams, fmt: str, quality: str) -> bytes:
        raise exc

    app.dependency_overrides[build_backend] = lambda: backend
    try:
        r = client.get("/api/model.stl", params={"quality": "preview", "teeth": 71})
    finally:
        app.dependency_overrides[build_backend] = lambda: _inline_backend
    assert r.status_code in (422, 503)
    assert caplog.records  # Pitfall 1: an empty caplog would pass with nothing proven

    failed = _event_records(caplog, "build.failed")
    assert len(failed) == 1
    ...
    assert _field(failed[0], "slug")
```
Sibling changes: request `{"quality": "preview", "teeth": 25, "root_shape": "trochoid"}` (25: no other test downloads it and the hob root applies; 26 is taken by `tests/test_cli.py:646,682`, 23 by `test_api.py:404-405`), `exc=BuildError(...)`, and assert `_field(failed[0], "slug") == "spur_z25_m1.75_pa25_trochoid"` (literal). The byte-cache comment at `:1073-1077` is the reason for the unique count; repeat it.

---

### `tests/test_browser.py` `download name` step (test e2e, request-response)

**Insert** between the `golden sweep` step (ends `:555`) and `with step("root_shape=bogus as today"):` (`:557`), inside the single scenario function (`test_the_shipped_viewer_in_a_real_browser(server: str)`, `:257`).

**Analog A, own page with `finally: close`** (`golden sweep`, `:536-541`):
```python
                sweep_page = browser.new_page()
                try:
                    swept = sweep(sweep_page, server, hashes)
                finally:
                    sweep_page.close()
```
**Analog B, content-based href wait** (`first build drawn`, `:329-340`):
```python
                expect(page.locator("#dl-stl")).to_have_attribute(
                    "href", re.compile(r"^api/model\.stl"), timeout=BUILD_WAIT_MS
                )
```
**Step wrapper** (`browser_session.py:373-383`) already prints `step {name}: N.NN s`, which is the D-06 reading; `step` and `BUILD_WAIT_MS` are already imported in `test_browser.py` (`:33-34`), as are `expect` and `Page` (`:51`).

**Target** (RESEARCH, typed for `mypy --strict`):
```python
            with step("download name"):
                fresh = browser.new_page()   # not `page`: its STL route has no Content-Disposition
                try:
                    fresh.goto(server + "/#teeth=23&root_shape=trochoid")
                    expect(fresh.locator("#dl-stl")).to_have_attribute(
                        "href", "api/model.stl?teeth=23&root_shape=trochoid", timeout=BUILD_WAIT_MS)
                    with fresh.expect_download(timeout=BUILD_WAIT_MS) as download:
                        fresh.click("#dl-stl")
                    name = download.value.suggested_filename
                finally:
                    fresh.close()
                assert name == "spur_z23_m1.75_pa25_trochoid.stl", f"the download is named {name!r}"
```
Two traps (RESEARCH Pitfalls 1 and 2): the main `page` carries `serve_stl_from(page, stl)` whose `**/api/model.stl*` route fulfils with no `Content-Disposition` (download would be `model.stl`), hence the fresh page; and a hash set after `goto("/")` can be erased, hence the fragment in the `goto` URL. No `expect_download` exists anywhere in `tests/` yet; this is the first. `filterwarnings = error` applies.

**Comment-only edits in `tests/browser_session.py`:** the `BUILD_WAIT_MS` block `:38-47` ("Slowest build-bound step (`first build drawn`) ... 2.53 s on macOS") is no longer true once this step reads about 3.28 s; update with the new reading. Also the `serve_stl_from` docstring / `test_browser.py:416` wording "after the first real build every step builds nothing".

---

### `docs/architecture/http-api.md` (doc)

**Analog:** the existing row at `:43`:
```
| `GET /api/model.{stl,step}?…` | the bytes, with `Content-Disposition` from `params.slug()` |
```
State the new truth there (name ends `_trochoid` exactly when the hob root is built; an ignored or refused request keeps today's name). `:93` ("records carry the gear's `slug`") gets matching wording.

---

### `docs/architecture/decision_log.md` new `L40` (doc)

**Analog:** `## L39 — A headless browser runs the shipped viewer ... (amends L13 and L36, restates L11)` at `:2299`; `## L38 — ...` at `:2091`. Shape: `## L40 — <title> (amends L38)`, then `Date: 2026-10-11.`, then a body whose figures are cited and not re-estimated. Next free id is L40 (last heading is L39; nothing reserved). L39 states no build count, so cite it, do not amend it. Body checklist: RESEARCH "The Lxx and the retirement" and CONTEXT D-10 (every consumer, flips vs untouched pins, no cache keyed by slug, effective-vs-requested rule with 2.3/5.3/39 us, totality sweep 17,567 cases 0 raised, log greps, CLI non-involvement, doc-path correction, the step's 3.28 s and own page). Reversibility line: costly. Open Question 1: it cannot cite its own commit sha; cite base `dc72f6c`.

---

### Idea retirement (doc)

**Analog:** `docs/ideas/retired/2026-09-21-browser-test-for-the-viewer.md`.
```
# A browser test for the viewer

Date: 2026-09-21
Status: retired
Retired in: docs(21): log L39 and retire the browser-test idea -- a headless browser runs in make verify and CI
Source: ...
```
Steps: `git mv docs/ideas/2026-10-08-download-name-carries-the-root-shape.md docs/ideas/retired/`; add `Status: retired` and `Retired in: <commit subject>` after `Date:`; add an `## Outcome` section; delete the row in `docs/ideas/INDEX.md` `## Open` (last row, the 2026-10-08 one) and add to `## Retired`:
```
| 2026-10-08 | [The download's file name does not carry the root shape](retired/2026-10-08-download-name-carries-the-root-shape.md) | <commit subject> |
```

---

### `bench/RESULTS.md` (doc, second commit allowed by D-11)

**Analog:** `### The browser test, priced (21-07)` at `:5030`: intro paragraph, `#### Host state` bullets (machine from `bench.machine_facts()`, Python/playwright/pytest versions, UTC read window, honest note on background load), then a readings table with columns including "1-minute load before -> after" and "UTC start". Heading for this phase: `## Download name carries the root (Phase 22)`. Three readings of the `step download name: N.NN s` line, HEAD sha, no cross-host comparison (this session's host was an M2 Max, Phase 21's an M5 Max).

## Shared Patterns

### Local import of `calc` in `params.py`
**Source:** `src/spur/params.py:180`. **Apply to:** `slug()` only. Import-linter contracts unaffected (`spur.params` -> `spur.calc` is already a live edge).

### One predicate (L38)
**Source:** `calc.root_mode` call at `calc.py:1086`, `model.py:773`. **Apply to:** `slug()` (third caller). Always `requested=p.root_shape, rho=p.root_fillet`.

### Literal filename pins
**Source:** `tests/test_api.py:720`. **Apply to:** all new name assertions in `test_api.py`, `test_calc.py`, `test_browser.py`. Names are literals, not recomputed from `slug()`.

### Fresh-page-per-special-need in the scenario
**Source:** `tests/test_browser.py:536-541`. **Apply to:** the download step.

### Wait on content, never an empty status (21 D-04)
**Source:** `tests/test_browser.py:329-340`. **Apply to:** the pre-click href wait (exact href, not bare).

### Byte-cache-dodging test counts
**Source:** `tests/test_api.py:1073-1077`. **Apply to:** the `build.failed` trochoid sibling (teeth=25).

## No Analog Found

None. The only first-of-kind item is `page.expect_download()`, which no test uses yet; Playwright 1.63.0 types are `Page.expect_download(predicate=None, *, timeout=None) -> EventContextManager[Download]` and `Download.suggested_filename -> str` (RESEARCH, installed `_generated.py`). Compose it from the `golden sweep` and `first build drawn` analogs above, with the `with page.expect_request(...)` context-manager shape at `test_browser.py:564-571` as the closest existing use of an `expect_*` block.

## Drift Corrections (trust the tree)

- `step()` is in `tests/browser_session.py:373`, not `tests/test_browser.py:373`. The scenario file is `tests/test_browser.py`; `tests/browser_scenarios.py` does not exist.
- `tip land gone` params are `tests/test_trochoid.py:176-179` (call at `:195`), not `:188`.
- `tests/test_api.py:411` (header equality radial vs trochoid) also becomes false; CONTEXT omits it.
- L39 has no "one real build" sentence; the invariant lives in `tests/browser_session.py` comments.
- `docs/http-api.md` is `docs/architecture/http-api.md`.

## Metadata

**Analog search scope:** `src/spur/`, `tests/`, `docs/architecture/`, `docs/ideas/`, `bench/RESULTS.md`
**Files read for excerpts:** `params.py`, `calc.py` (root_mode), `test_api.py`, `test_browser.py`, `browser_session.py`, `test_trochoid.py`, `test_calc.py`, `decision_log.md`, `docs/ideas/*`, `http-api.md`, `bench/RESULTS.md`
**Pattern extraction date:** 2026-10-11
