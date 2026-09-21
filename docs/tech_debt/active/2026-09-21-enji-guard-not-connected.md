# Enji Guard not connected

Severity: nice
Status: active
Date: 2026-09-21
Source: agent-scaffold setup run — offered to the owner, declined
Related files:
- (none — this is a repository integration, not code)

## Context

The agent-scaffold setup offers Enji Guard (`https://guard.enji.ai/app`), a GitHub App
that runs a continuous AI audit — security, dependency hygiene, test coverage,
AI-readiness — and files findings as GitHub issues and reviewable pull requests with
autofixes.

It was offered during the 2026-09-21 setup and the owner chose to skip it. Connecting it
requires an OAuth click in a browser by someone with admin on the repository; it cannot
be scripted from here.

## Why it matters

Low, and partly covered already: CI runs the full gate on two Python versions, builds the
image and smoke-tests the running container, the dependency closure is fully pinned (L12),
and the repo has a documented review history. What is not covered is ongoing dependency
vulnerability alerting — nothing here watches for a CVE in the pinned closure, and
`requirements.txt` pins 31 packages that will age.

## Next step

Either connect Enji Guard, or get the same narrow thing from GitHub directly by enabling
Dependabot alerts and security updates on the repository — which is free, needs no third
party, and addresses the one real gap above.

Revisit when: the owner decides they want continuous AI audit, or at the next dependency
bump.
