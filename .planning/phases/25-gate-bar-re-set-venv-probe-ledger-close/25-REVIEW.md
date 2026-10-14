---
phase: 25-gate-bar-re-set-venv-probe-ledger-close
reviewed: 2026-10-14T00:00:00Z
depth: standard
files_reviewed: 8
files_reviewed_list:
  - .ai_skills/reverify-phase/SKILL.md
  - .pre-commit-config.yaml
  - Makefile
  - README.md
  - bench/RESULTS.md
  - docs/architecture/decision_log.md
  - docs/tech_debt/active/2026-10-09-phase-19-review-info-findings-deferred.md
  - tests/test_hooks.py
findings:
  critical: 0
  warning: 1
  info: 0
  total: 1
status: issues_found
---

# Phase 25: Code Review Report (re-review of the fix pass)

**Reviewed:** 2026-10-14
**Depth:** standard
**Files Reviewed:** 8
**Status:** issues_found

## Summary

Scope was the delta `3e7269e..HEAD` over the eight files. I did not re-run `make verify`; I rely on the fixer's
run on 4d61923 (exit 0, `1318 passed`) for "tests pass". I did run `tests/test_hooks.py` alone: `7 passed`.

Checked and found sound:

- **New test** (`test_the_dev_venv_installs_under_the_closure_and_reinstalls_when_it_moves`). `make -n -W
  requirements.txt .venv/.installed` prints the stamp recipe only if `requirements.txt` is a prerequisite of
  `$(STAMP)`. The `next(..., None)` plus the `is not None` assert fails if the recipe is absent. The `" -m pip install -e "`
  needle matches the one editable-install line and not the `--upgrade pip` line. The `-c` count and the
  `-c requirements.txt` substring assert the flag. It cannot pass vacuously. I ran the real dry run and the printed line
  is `... pip install -e '.[dev]' -c requirements.txt`.
- **Makefile and `.pre-commit-config.yaml`**: with comment lines stripped, the old and new files are identical
  (`diff` silent for both), so no recipe, prerequisite or hook block changed. `_hook_blocks` splits on `- id: `, which
  the comment edit does not touch.
- **Phase 24 figures in L43**: 296.91 s (red, `1 failed, 1294 passed`, load 15.6), 272.91 s, 294.40 s and 336.15 s (load
  averages 5.36 4.71 6.68) all match `24-0{1,2,3}-SUMMARY.md` and `bench/RESULTS.md` 5538-5543. The M2 Max attribution
  (24-01 line 213, 24-03 line 167) and "24-02 names no host" are right. "merged 2026-10-13" matches commit `94dfc19`.
- **RESULTS.md / L43 venv-probe rewording**: the cited pip 2026-07-29 news is at `.planning/research/PITFALLS.md:389`,
  and no 25-03 log mentions `hatchling` or isolation.
- **README, SKILL.md, debt item (`34270c8`), L34 pointer**: correct.
- **README / HOW_TO_DEVELOP / packaging "bar 300 s on an 18-CPU Apple M5 Max"**: still true and not contradicted
  by the new L43 wording (the bar is a figure the human set on that host).

One defect, introduced by the WR-03 fix itself.

## Warnings

### WR-04: L43 "The bar" says the M5 Max has no loaded full-gate reading; the record, including L43's own, says it has

**File:** `docs/architecture/decision_log.md:2894-2902` (the added sentences "It is not a ceiling the gate has been read
under: this host has no loaded full-gate reading. The only loaded full-gate readings in `bench/RESULTS.md` are Phase
24's ..." and "what the gate reads on the M5 Max under load is unread"); same premise in `.pre-commit-config.yaml:10-12`
only by implication (it is correct there).

**Issue:** Three claims are false against the repo's own text, in a log whose rule is that a printed number is one someone
will cut metal to (L08).

1. "this host has no loaded full-gate reading". "This host" is the 18-CPU Apple M5 Max. L43's own next paragraph
   ("The readings", `decision_log.md:2881-2883`) records the two Phase 25 readings, 195.23 s and 179.21 s, as taken "at
   1-minute loads of 4.18 to 7.33". Those are loaded full-gate readings on the M5 Max.
2. "The only loaded full-gate readings in `bench/RESULTS.md` are Phase 24's". L38 (`decision_log.md:2287-2293`, citing
   `### The gate, priced (19-09)`) records three Phase 19 `make verify` readings on the same M5 Max, 208.52, 161.71 and
   208.60 s, plus a 166.25 s fourth, with "loads ... 4 to 9". Older loaded gate readings on the M2 Max also exist
   (`bench/RESULTS.md:1535`, 177.62 s at load ~3 to 4; `:2170-2173`, 216.90 s at load 8 to 9).
3. "what the gate reads on the M5 Max under load is unread". It is read, at 161.71 to 208.60 s (Phase 19, 1210 tests) and
   179.21 and 195.23 s (Phase 25, 1315 and 1317 tests), every one below 300 s.

The result is a bar paragraph that points the reader at the four M2 Max Phase 24 readings (two of which are 294 s and
above 300 s) as the only evidence under load, and hides that the M5 Max readings under load sit 100 s lower. That tilts
the picture the other way and contradicts L38 and L43's own readings paragraph. The fixer's WR-03 note ("this host has no
loaded full-gate reading") apparently took "decisive" (idle, rule-conforming) to mean "unloaded"; the two are not the same,
since all ten rule slots were waived at loads of 4 to 7.

The true and still useful statement is narrower: no M5 Max reading has been taken under the Phase 25 idle rule (n = 0
decisive), and the only readings at or above 300 s (294.40 s and 336.15 s, 296.91 s red) are from the M2 Max, at other test
counts. That keeps the human-set caveat without asserting an absence the record refutes.

**Fix:** Replace the added sentences, keeping the Phase 24 quotation and its caveats, along these lines:

```
It is not a ceiling the gate has been read under on an idle host: no run met the rule's idle clause, so n = 0 decisive.
The M5 Max has loaded full-gate readings, none above 300 s: L38's 208.52, 161.71 and 208.60 s at loads 4 to 9 (1210
tests, `### The gate, priced (19-09)`) and the two non-decisive readings below at loads 4.18 to 7.33. The readings at or
above 300 s in `bench/RESULTS.md` are Phase 24's, on a 12-CPU Apple M2 Max (24-01 and 24-03 name it; 24-02's names no
host), at other HEADs and test counts, and as pytest's own seconds rather than `real`, so none is comparable with this
host's (L08). They are quoted as read: ... [unchanged list] ... The last is above 300 s. So 300 s is a figure the human
set; it was not read as a ceiling, and no check enforces it.
```

and drop "what the gate reads on the M5 Max under load is unread".

---

_Reviewed: 2026-10-14_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
