---
name: decision-audit-trails
description: Use when adding provenance, snapshots, replay, decision logs, or auditability to software that makes recommendations, rankings, allocations, or other consequential decisions.
metadata:
  short-description: Add decision provenance and replay
---

# Decision Audit Trails

Use this skill when a system produces decisions that a reviewer, user, auditor,
or operator must later explain.

## Required Shape

Every consequential decision should record:

- timestamp in UTC;
- policy or model version;
- input source and source freshness;
- provider mode such as live, cached, offline, or demo;
- user-provided parameters;
- output summary;
- excluded or rejected alternatives;
- enough payload to replay or inspect the decision.

## Workflow

1. Define the decision boundary.
   - Log the decision response, not every render or page load.
   - Avoid logging secrets or full private documents.

2. Persist append-only rows.
   - Use a small table or JSONL file.
   - Never overwrite previous decisions.
   - Keep payloads schema-versioned.

3. Add read APIs and UI.
   - Provide a recent-decision endpoint.
   - Show policy, source, mode, parameters, and totals in the UI.
   - Keep detailed payload export behind an explicit action.

4. Test real state.
   - Verify that calling the decision endpoint creates a persisted row.
   - Verify that a low-value or rejected decision is also logged.
   - Verify that logs do not expose API keys.

5. Connect to reproducibility.
   - Pair logs with snapshots when possible.
   - A replay command should accept a decision id or snapshot id.

## Failure Modes

- Logging only HTTP 200 responses without checking database state.
- Recording live decisions but not the source or policy version.
- Mixing audit logs with analytics telemetry.
- Masking provider errors that explain why the decision changed.

