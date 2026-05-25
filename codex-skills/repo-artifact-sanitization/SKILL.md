---
name: repo-artifact-sanitization
description: Use when cleaning a repository for external review by removing AI markers, legacy clutter, irrelevant pasted requirements, secrets, generated debris, and ambiguous artifact structure.
metadata:
  short-description: Sanitize repositories for review
---

# Repo Artifact Sanitization

Use this skill before sharing a repository with reviewers, judges, customers, or
collaborators.

## Workflow

1. Inventory the root.
   - Identify canonical code, docs, tests, scripts, data, and generated output.
   - Flag duplicate files named with superlatives or stale version labels.
   - Flag copied requirements from unrelated projects.

2. Preserve before deletion.
   - Archive or document legacy material before removal when value is unknown.
   - Delete only caches, build output, logs, and regenerated files.
   - Never delete user data without explicit direction.

3. Mine legacy for value.
   - Look for real algorithms, datasets, rules, scripts, or UI patterns.
   - Ignore superlative reports, empty scientific folders, and generated dumps.
   - Promote only ideas that have tests or a clear implementation path.

4. Remove AI markers.
   - Hype adjectives and superlatives.
   - Emojis in technical docs.
   - "Step 1 / Step 2" scaffolding when unnecessary.
   - Generic comments that repeat code.
   - try/except blocks that mask real errors.
   - Mentions of unrelated domains.

5. Validate reviewer path.
   - Fresh run command.
   - Tests and lint.
   - UI smoke if applicable.
   - Artifact text scan.
   - Clean git status.

## Bundled Helper

Use `../scripts/check_artifact_text.py` from the exported package to scan for
common text hygiene problems.
