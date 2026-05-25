---
name: free-data-source-readiness
description: Use when a project depends on free public APIs or datasets and needs setup, health checks, provider status, optional key configuration, no-secret UI, or reviewer-friendly source readiness.
metadata:
  short-description: Free data provider readiness
---

# Free Data Source Readiness

Use this skill for projects that must run with free data sources and optional
API keys.

## Workflow

1. Classify providers.
   - Required free source.
   - Optional free enhancement.
   - Paid or unsupported source.
   - Offline fixture or cache.

2. Make configuration explicit.
   - Provide `.env.example`.
   - Load `.env` automatically where appropriate.
   - Do not commit `.env` or secrets.
   - Show only configured/not configured status, never key values.

3. Add health modes.
   - Config mode: checks environment only, fast and deterministic.
   - Live mode: makes bounded network calls with timeout.
   - Cache mode: reports last successful observation and age.

4. Design health responses.
   - name, status, configured, last_check, error, metadata.
   - status values should be simple: working, configured, not_configured, error.
   - Errors should be visible and actionable.

5. Add UI status.
   - Green for working.
   - Yellow for configured/not tested or not configured optional.
   - Red for errors.
   - Avoid auto-running slow live checks on every page load.

6. Test without network by default.
   - Unit tests should use config mode or fakes.
   - Live tests should be manual or explicitly marked.

## Reviewer Standard

A reviewer should understand which free sources are active, which are optional,
and which results are live versus cached or offline.

