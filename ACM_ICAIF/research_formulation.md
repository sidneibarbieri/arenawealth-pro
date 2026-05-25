# Research Formulation Checklist

This checklist is derived from project-formulation principles. It does not copy
private study material.

## Problem

- What painful workflow existed before this work?
- Who experiences the pain: reviewer, holder, researcher, or advisor?
- Why are current approaches insufficient: opaque data, non-replayable
  recommendations, provider fragility, or look-ahead bias?

## Insight

- What is the central insight that changes the system?
- Why does determinism matter more than model complexity here?
- How do snapshots reconcile fresh data with reproducible decisions?

## Mechanism

- What exactly is deterministic?
- What input tuple reproduces a decision?
- Which data can be free and point-in-time, and where do limitations remain?

## Evidence

- What table or figure proves each claim?
- Which baseline would make the claim harder to win against?
- Which ablation would falsify the mechanism?

## Boundary

- What does the system not claim?
- Which results are current-basket only?
- Which results are not yet point-in-time?
- Which use cases require compliance review before commercialization?

## Reader Takeaway

The reader should leave with one concrete shift: portfolio decision systems can
be treated as reproducible computational artifacts, not only as dashboards or
opaque advisory outputs.
