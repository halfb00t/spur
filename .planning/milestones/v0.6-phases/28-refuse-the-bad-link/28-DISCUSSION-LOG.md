# Phase 28: Refuse the Bad Link - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-21
**Phase:** 28-refuse-the-bad-link
**Areas discussed:** Bad-value mechanism, Mark and clear rules, root_fillet label wording, Leftover triage scope

---

## Bad-value mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| Shared map only | One `rejected` map for selects and number boxes; controls show blank | ✓ |
| Map + stray select option | Map, plus a temporary option so the select shows the bad text | |
| Map + number placeholder | Map, plus the raw token as a greyed placeholder in a number box | |

**User's choice:** Shared map only.

| Option | Description | Selected |
|--------|-------------|----------|
| Control reads back '' | A non-empty token that reads back `''` after assignment is rejected | ✓ |
| Explicit per-type check | Enum membership plus a numeric regex | |

**User's choice:** Control reads back ''.

---

## Mark and clear rules

| Option | Description | Selected |
|--------|-------------|----------|
| Own-field edit, Reset, hashchange | Unrelated edits keep sending the bad token | ✓ |
| Any edit clears all | First edit drops every rejected token | |

| Option | Description | Selected |
|--------|-------------|----------|
| Message only, no outline | `mate_teeth=abc` shows the bare server message; `problems()` untouched; gap in L44 | ✓ |
| Outline it, touch problems() | Breaks the "problems() unchanged" boundary | |
| Outline it outside problems() | A second marking path | |

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, record it in L44 | Blank = default on the page; API 422 on `''` is a separate boundary | ✓ |
| Yes, and file debt for the API | Also file a nice item | |

**Notes:** D-05 adjusts success criterion 1's "mark the field" for the mate box. The human approved this.

---

## root_fillet label wording

| Option | Description | Selected |
|--------|-------------|----------|
| Hob tip radius used | Matches the "... used" pattern | ✓ |
| Root radius (hob tip) | Keeps "root" first | |
| Hob tip radius | Shortest | |

| Option | Description | Selected |
|--------|-------------|----------|
| From the info document | Label function of `d`, keyed on a hob-only value | ✓ |
| From the form's root_shape | Field name outside `DIMS`; shows the request, not the build | |

---

## Leftover triage scope

| Option | Description | Selected |
|--------|-------------|----------|
| Triage them here | Phase 26 IN-01..05 dispositioned; close grep extended to 26 | ✓ |
| Defer as one item | One nice item, no fixes | |
| Leave for v0.7 | Milestone closes with five open | |

| Option | Description | Selected |
|--------|-------------|----------|
| Next edit of trochoid code | Trigger for the Phase 18 nice item | ✓ |
| Hob-root default flip (L38) | Trigger tied to L38's flip | |

| Option | Description | Selected |
|--------|-------------|----------|
| Debt item, must, decision | 10 IN-02 in `docs/tech_debt/active/` | ✓ |
| Idea file | `docs/ideas/` | |

---

## Claude's Discretion

- Map and helper naming and placement, within the pinned tokens.
- New browser step names.
- Commit order, one concern per commit.

## Deferred Ideas

- Outline for the mate box on a 422 (gap recorded in L44).
- Showing the rejected token inside the control.
- Whether the API should accept `''` as default (recorded in L44).
