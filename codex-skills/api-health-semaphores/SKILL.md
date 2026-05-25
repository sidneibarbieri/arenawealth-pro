---
name: api-health-semaphores
description: Use when a project integrates external APIs or data providers and needs a UI health indicator that distinguishes between not_configured, configured_but_untested, working, degraded, and error states without leaking secrets or blocking the user.
metadata:
  short-description: Visual API health status patterns
---

# API Health Semaphores

Use this skill when building workbenches, dashboards, or tools that depend on
external providers and need to show users whether each dependency is ready,
degraded, or missing — without exposing keys or blocking the UI.

## State Taxonomy

Use exactly these states; do not invent others:

| State | Color | Meaning |
|-------|-------|---------|
| `working` | green | Last probe succeeded within the cache TTL |
| `configured` | yellow | Key is present but no successful probe yet |
| `not_configured` | yellow | No key and no anonymous access possible |
| `degraded` | yellow | Probe succeeded but with warnings or slow response |
| `error` | red | Last probe failed with a hard error |
| `offline` | grey | Deliberately running in offline/fixture mode |

Never collapse `configured` and `not_configured` into a single yellow — they
have different remediation paths.

## Probe Design

1. Two probe modes:
   - `config`: checks environment only; fast and deterministic; no network.
   - `live`: bounded network call; 3-second timeout; catches auth errors.

2. Cache probes for at least 60 seconds to avoid hammering providers on
   every page load.

3. Return a typed `ProviderStatus` object, not raw strings:
   ```
   { provider: str, state: State, last_checked: datetime | None, message: str }
   ```

4. Expose a `/health/providers` endpoint or equivalent so status can be
   polled independently of the main data endpoints.

## UI Rules

1. Show the semaphore chip near the data surface it protects, not in a
   separate admin panel that users won't check.

2. On hover or click, show: state, last successful check time, and a
   one-line remediation hint (e.g., "Set FINNHUB_API_KEY in .env").

3. Never render the API key value, even partially masked, in the UI.

4. If all providers are green, hide the health panel or collapse it — only
   expand it when at least one is yellow or red.

5. Yellow is not a safe default. If a key is configured but has never
   successfully returned data, treat it as untested risk, not as ready.

## Remediation Hints

Map each state to a concrete, user-facing message:

- `not_configured`: "Optional. Set <KEY_NAME> in .env for live data."
- `configured`: "Key found. Run a live check to confirm access."
- `error`: "Provider returned <STATUS>. Check key and quota."
- `offline`: "Running on cached fixture. No live data."

## Validation

- Unit test: mock each provider response and assert the correct state is
  returned.
- Integration test: hit a free endpoint with a valid key and assert `working`.
- UI test: stub the health endpoint and assert chips render correct colors.

## Common Mistakes

- Using `configured` as if it means `working` — it does not.
- Calling the live probe on every render instead of caching.
- Showing error details that include key fragments or internal paths.
- Hiding the health panel entirely when providers are yellow — yellow needs
  user attention.
