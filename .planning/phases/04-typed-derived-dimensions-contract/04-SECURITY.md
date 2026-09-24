---
phase: "04"
slug: "typed-derived-dimensions-contract"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-09-24"
---

# Phase 04 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Register source: the `<threat_model>` blocks of `04-01-PLAN.md`, `04-02-PLAN.md` and
`04-03-PLAN.md` (authored at plan time, 16 rows). No SUMMARY carried a `## Threat Flags`
section. ASVS level 1 with `register_authored_at_plan_time: true` and every row closed at
grep depth took the workflow's short-circuit: no auditor agent was spawned; the evidence
column below is what the orchestrator checked in the tree at `67d74a5`.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| `derive()` → UI / CLI stdout / API clients | A published response shape leaves the process; readers parse it by key name and trust the numbers enough to cut metal | `DerivedDimensions` (19 fields, mm / counts / warnings) |
| client → `/api/info` query string | Untrusted input; `InfoQuery`/`GearParams` remain the one validation boundary (ASVS V5) | gear parameters, `mate_teeth` |
| container orchestrator → `/api/health` | Docker `HEALTHCHECK` and the UI parse this; a moved `status` marks a healthy container unhealthy | `HealthReport` (`status`, `version`, `pool`) |
| event loop → spawned build worker (`pool.py`) | Arguments are pickled across a process boundary | callable + args/kwargs bound in a `functools.partial` |
| shell user → `spur info --mate-teeth` | Untrusted CLI input; refused on the same terms the API refuses it | integer tooth count |
| planning artefacts → `docs/architecture/decision_log.md` | A claim becomes a locked decision later agents treat as settled | L21 text |
| `docs/tech_debt/active/` → `resolved/` | A `must` item leaves the watched set | debt file + INDEX row |
| `pyproject.toml` → every future commit | Gate configuration decides what later changes are checked against | mypy / pydantic-mypy settings |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-04-01 | Tampering | response shape (`DerivedDimensions`) | medium | mitigate | `tests/test_api.py::test_openapi_documents_the_typed_contracts` (D-11), `::test_every_key_the_ui_reads_is_a_derived_dimensions_field` (D-12), `tests/test_cli.py::test_cli_and_api_print_the_same_document` (D-13); all run under `make verify` | closed |
| T-04-02 | Tampering | numbers the tool publishes | high | mitigate | No `default=`/`default_factory=` on any of the 19 fields (`src/spur/calc.py` class body); `test_api.py:87` asserts `set(component["required"]) == fields`; `tests/test_calc.py::test_impossible_pairs_have_no_centre_distance` keeps `centre_distance` null; `::test_default_dimensions` pins existing numbers | closed |
| T-04-03 | Denial of Service | `/api/info` on every debounced keystroke | low | accept | Per-call cost of `derive()` measured with `timeit` before/after and recorded in `calc.py`'s docstring and `04-01-SUMMARY.md` ("derive()'s per-call cost") — microseconds against an HTTP round trip | closed |
| T-04-04 | Information Disclosure | two always-present `null` keys (`mate_teeth`, `centre_distance`) | low | accept | Keys carry nothing the client did not send; no secret exists in the application (REQ-no-auth-default) | closed |
| T-04-05 | Tampering | `spur info --mate-teeth` unranged (pre-existing) | high | transfer | Transferred to T-04-14 (Plan 04-03 Task 1, human decision R-2 of 2026-09-24); kept byte-identical in 04-01 | closed |
| T-04-06 | Tampering | `/api/health` published contract | medium | mitigate | `tests/test_api.py::test_health` unchanged and passing; `tests/test_pool.py` health tests run the real lifespan; `test_api.py:98` asserts `HealthReport.required == {status, version, pool}` | closed |
| T-04-07 | Tampering | `pool._run_with_timeout` forwarding | medium | mitigate | `src/spur/pool.py:181` `run_in_executor(executor, functools.partial(func, *args, **kwargs))` — keyword arguments cannot be dropped silently; `tests/test_pool.py` drives the real spawn boundary | closed |
| T-04-08 | Elevation of Privilege | type narrowing in `smoke.py` / `cli.py` / tests | low | mitigate | `git diff 538d26f..HEAD -- src tests docker` adds zero `cast(`; `cli.py` narrows with `is not None`; tests narrow with `isinstance` | closed |
| T-04-09 | Denial of Service | `/api/health` latency (Phase 2's headline criterion) | low | accept | Two small frozen models per call, microseconds against the 0.7–2.3 ms under-load p95 in `bench/RESULTS.md`; handler stays synchronous, lock-free, constant-time; no latency claim changed | closed |
| T-04-10 | Repudiation | `docs/architecture/decision_log.md` | medium | mitigate | `git diff 34897f9..HEAD -- docs/architecture/decision_log.md` shows 0 removed lines; L21 appended (21 `## L` entries); 04-03 Task 2's exact-prefix verify against HEAD | closed |
| T-04-11 | Spoofing | debt item marked resolved without the work | high | mitigate | `cfe5f8d` carries `pyproject.toml` (`disallow_any_explicit = true`), the `git mv` to `docs/tech_debt/resolved/` and the `INDEX.md` row in one commit; pre-commit `make verify` ran with the rule on; `Resolved in: 013900d` passes `git cat-file -e`; wave 3 ran after the code-carrying plans | closed |
| T-04-12 | Tampering | the ratchet weakened later | medium | mitigate | `pyproject.toml`: `disallow_any_explicit = true` with no per-module override of it (the only `[[tool.mypy.overrides]]` is the pre-existing `ignore_missing_imports` for `cadquery.*`/`OCP.*`); zero explicit-Any suppressions in `src tests docker bench`; L21 and `docs/CODING_VALUES.md:50` state why re-adding either is a regression | closed |
| T-04-13 | Elevation of Privilege | `[tool.pydantic-mypy]` settings changing runtime behaviour | low | mitigate | `init_typed`/`init_forbid_extra` are read only by the mypy plugin; every `model_config` in `src/spur` is `ConfigDict(frozen=True)` — no model gained `extra="forbid"`; full suite (104) passes under the new config | closed |
| T-04-14 | Tampering | numbers `spur info` publishes for an out-of-range mate (from T-04-05) | high | mitigate | `src/spur/cli.py::_mate_teeth` argparse `type=` enforces `6..1000`, exit 2, no `centre_distance` printed; `tests/test_cli.py::test_info_rejects_a_mate_the_api_would_reject` reads the bounds from `InfoQuery.model_json_schema()` so the copies cannot drift | closed |
| T-04-SC | Tampering | package-manager installs (04-01, 04-02, 04-03) | low | accept | No install in any plan; pydantic, FastAPI and starlette were already declared, installed and imported | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-04-01 | T-04-03 | Model validation adds ~2 µs to a ~10 µs call, measured and recorded; negligible next to the HTTP round trip | Plan 04-01 threat model (plan approved by the human) | 2026-09-24 |
| R-04-02 | T-04-04 | The added `null` keys expose nothing the client did not send; the application holds no secrets | Plan 04-01 threat model | 2026-09-24 |
| R-04-03 | T-04-09 | Two frozen models per `/api/health` call cost microseconds against a millisecond p95 bar; handler unchanged in shape | Plan 04-02 threat model | 2026-09-24 |
| R-04-04 | T-04-SC | No package was installed in any of the three plans | Plans 04-01/02/03 threat models | 2026-09-24 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-24 | 16 | 16 | 0 | /gsd-secure-phase 4 orchestrator (L1 short-circuit; no auditor agent) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-24
