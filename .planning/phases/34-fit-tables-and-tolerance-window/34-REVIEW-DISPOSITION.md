---
phase: 34
review: 34-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: fix
    resolution: "fixed in 9215f60"
    title: "`ensure_ignored` fails open on any git fatal error, and creates directories before it checks"
  - id: WR-02
    severity: warning
    disposition: fix
    resolution: "fixed in d3f339b"
    title: "The documented file mode makes the table file unreadable to the container's user"
  - id: WR-03
    severity: warning
    disposition: fix
    resolution: "fixed in d299fe3 (remaining A_s bound deferred: docs/tech_debt/active/2026-11-01-an-oversized-a-s-cell-loads-and-shifts-every-limit.md)"
    title: "`problems()` accepts tolerance rows whose signs and order make the printed limits impossible"
  - id: WR-04
    severity: warning
    disposition: fix
    resolution: "fixed in e98638b"
    title: "`assemble` accepts one read passed twice, so its \"two independent reads agree\" gate is one typo wide"
  - id: IN-01
    severity: info
    disposition: defer
    resolution: "deferred: docs/tech_debt/active/2026-11-01-limit-measurement-odd-confirmed-branch-is-dead.md"
    title: "`limit_measurement`'s `odd_confirmed` parameter and its odd-count branch are unreachable in production"
  - id: IN-02
    severity: info
    disposition: defer
    resolution: "deferred: docs/tech_debt/active/2026-11-01-din5480-comment-points-at-a-moved-debt-file.md"
    title: "A code comment still points at the debt file this phase moved to `resolved/`"
  - id: IN-03
    severity: info
    disposition: defer
    resolution: "deferred: docs/tech_debt/active/2026-11-01-schema-version-constant-is-never-used.md"
    title: "`SCHEMA_VERSION` is defined and never used"
  - id: IN-04
    severity: info
    disposition: defer
    resolution: "deferred: docs/tech_debt/active/2026-11-01-load-file-reads-the-whole-file-before-its-size-cap.md"
    title: "`load_file` reads the whole file before enforcing the size cap on what it read"
  - id: IN-05
    severity: info
    disposition: defer
    resolution: "deferred: docs/tech_debt/active/2026-11-01-two-real-file-and-anchor-assertions-are-tautologies.md"
    title: "Two real-file and anchor assertions are tautologies"
  - id: IN-06
    severity: info
    disposition: defer
    resolution: "deferred: docs/tech_debt/active/2026-11-01-table-7-partly-present-loads-and-prints-a-false-sentence.md"
    title: "A file with Table 7 only partly present loads and then prints a false sentence"
  - id: IN-07
    severity: info
    disposition: defer
    resolution: "deferred: docs/tech_debt/active/2026-11-01-read1-matches-digits-with-backslash-d.md"
    title: "Read 1 matches digits with `\d`, against the repository's own stated rule"
---

# Phase 34 — Review disposition

Every finding starts `open`; the human decides fix, defer (debt file) or accept.

Human ruling 2026-11-01: fix the four warnings with tests seen red first, file the seven info items as debt. Also fixed: the stale "721 of 721 rows" comment (e0708a7).
