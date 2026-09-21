# No server-side cancellation on client abort

Severity: nice
Status: active
Date: 2026-09-21
Source: docs/review-2026-09-21.md F4 (related note); plan's "Deliberately not done"
Related files:
- src/spur/static/app.js (the update loop's `AbortController`)
- src/spur/app.py (`model`)

## Context

The UI aborts its in-flight fetch on every parameter change and drops out-of-order
responses with a sequence counter, so the *browser* behaves correctly. The server does
not find out: the build proceeds to completion and the bytes are produced for nobody.
Dragging a slider therefore queues work that is already irrelevant.

## Why it matters

It wastes the one scarce resource this service has — the serialised kernel — and it makes
the bounded queue (L04) fill with requests nobody is waiting for, so a real request gets
a `503` behind abandoned ones. Today the debounce keeps this small.

## Next step

Check `await request.is_disconnected()` before taking a build slot, and again before
starting the export. That catches the cheap case without needing cancellation inside the
kernel call, which is not interruptible anyway.

Revisit when: slider-dragging actually saturates the queue in practice, or after the
process pool lands, which would make real cancellation possible.
