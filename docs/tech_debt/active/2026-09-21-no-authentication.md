# The service has no authentication

Severity: nice
Status: active
Date: 2026-09-21
Source: README ("The app has no authentication"), compose.yaml
Related files:
- src/spur/app.py
- compose.yaml

## Context

There is no authentication, no authorisation and no rate limiting beyond the build queue.
This is a known, documented position, not an oversight: `compose.yaml` binds to
`127.0.0.1` on purpose, the container runs non-root with `read_only`, `cap_drop: ALL`,
`no-new-privileges` and a tmpfs `/tmp`, and the README says to put a reverse proxy with
auth in front to expose it.

It is recorded here so that the decision gets re-taken rather than inherited.

## Why it matters

The posture is sound while the binding is localhost. Two things would change that
quietly: someone editing the port mapping to `8000:8000` for convenience, or a deployment
that skips compose. At that point an unauthenticated endpoint that can be made to build a
200-tooth gear is a denial-of-service primitive — each request costs seconds of CPU and
hundreds of megabytes.

## Next step

Nothing now. If it is ever exposed: the proxy carries auth (Caddy/Traefik/Cloudflare
Access/Tailscale), and the app should additionally rate-limit by client on the model
endpoints, because `SPUR_MAX_QUEUED_BUILDS` bounds concurrency but not cost per client.

Revisit when: the port mapping changes, or the service is deployed anywhere but one
person's machine.
