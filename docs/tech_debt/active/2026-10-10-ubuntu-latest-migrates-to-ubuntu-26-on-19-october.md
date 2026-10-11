# CI's `ubuntu-latest` moves to Ubuntu 26 on 2026-10-19; the browser test's install has only run on 24.04

Severity: must
Status: active
Date: 2026-10-10
Source: plan 21-08, reading the real `ubuntu-latest` run 38059369744 of the phase branch (annotation on the run)
Related files:
- `.github/workflows/ci.yml` (`runs-on: ubuntu-latest`, `BROWSER_INSTALL_ARGS: --with-deps` on the `test` step)
- `Makefile` (the `$(BROWSER)` stamp: `playwright install $(BROWSER_INSTALL_ARGS) --only-shell chromium`)
- `bench/RESULTS.md` `### The Linux path on the real runner (21-08)`

## Context
Run 38059369744 carried the notice "The ubuntu-latest label will migrate to Ubuntu 26 beginning
October 19, 2026" (`actions/runner-images#14748`). Both green runs of the browser test (21-02, run
38044109910; 21-08, run 38059369744) were on image `ubuntu-24.04` `20261004.327.1`, where
`playwright install --with-deps --only-shell chromium` apt-installed 9 packages and downloaded Chrome
Headless Shell 153.0.8010.12 in about 14 s. After the migration `test (3.12)` runs on a different
image, with a different apt set, and no run of the browser test has been read there.

One static check was made: the pinned driver (`playwright` 1.63.0, `driver/package/lib/coreBundle.js`)
names `ubuntu26.04-x64` and `ubuntu26.04-arm64` as host platforms, with as many entries as
`ubuntu24.04-x64`. That says the platform is known to the driver, not that `--with-deps` installs a
complete library set there or that SwiftShader draws the same frame. ASSUMPTION: it does; unread.

## Why it matters
`make verify` fails closed when the shell is missing or cannot launch (D-02, no skip path), so a broken
install on the new image turns every pull request's `test (3.12)` red at once, with the failure in the
browser test and not in any code under review. The canvas PNG bar (4.9, set from two hosts' ratios) is
also read on one Linux renderer only.

## Next step
Revisit when the first CI run after 2026-10-19 reads `ubuntu-latest` as Ubuntu 26 (the `Set up job`
group names the image). If it is red, classify from the whole log (apt, WebGL, timeout) before any
fix, as 21-08 did; if it is green, record the image version and the install seconds under a new
`bench/RESULTS.md` reading and resolve this item. Pinning `runs-on: ubuntu-24.04` is the fallback; that is the
human's decision, not the executor's.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
