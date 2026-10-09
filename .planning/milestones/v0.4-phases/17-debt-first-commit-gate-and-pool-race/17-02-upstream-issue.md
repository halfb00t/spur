Title: Make COMMIT_TIMEOUT_MS configurable -- a pre-commit hook longer than 30 s kills every SDK commit

## Summary

`query commit` runs `git commit` under a fixed timeout, `COMMIT_TIMEOUT_MS = 30_000` in `bin/lib/commands.cjs` (gsd-core 1.16.0). The same constant is used by every `git commit` the SDK runs (the three commit sites and their timeout messages). No config key reads it: there is none in `.planning/config.json` and none in the planning-config reference.

A project whose `pre-commit` hook legitimately takes longer than 30 s therefore gets `{committed: false, reason: 'commit_timeout'}` on every SDK commit, however the project configures gsd. #3886 introduced the 30 s band and the `commit_timeout` reason (thank you, that made the failure legible); this asks for the band to be adjustable.

## What I saw

- A test-suite gate wired as a `pre-commit` hook, about 64 s warm on a 12-core machine. Every `gsd-tools query commit` returned `commit_timeout`.
- Measured side effect (git 2.54.0, Node `spawnSync` with a 2 s timeout against a 6 s hook in a scratch repository): the child `git commit` is killed with SIGTERM (`ETIMEDOUT`), nothing is committed and no `index.lock` remains, but the hook process keeps running to completion, reparented to PID 1.
- That orphan is why the documented recovery does not work for a long hook: the retry starts a second copy of the hook while the first is still running. The two share the hook's stash and the test runner's coverage files, and the retry is killed at 30 s in turn.

## Request

One config key, for example `git.commit_timeout_ms`, with a default of `30000` so nothing changes for anyone who does not set it, honoured by every commit call site (and by the text of the timeout message, which already derives from the constant).

## What I do meanwhile

The hook that runs at commit time is a sub-30 s subset of the gate, and the whole gate runs at pre-push and in CI. That keeps SDK commits working, but it means the commit-time check is weaker than the project would otherwise choose, which is the cost this request would remove.
