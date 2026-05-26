# FinTech World Cup Preparation Packet

This folder tracks the product and pitch path. It is separate from the research
paper packet.

## Target

FinTech World Cup is the best fit for product visibility and prize-oriented
startup pitching. Dubai FinTech Summit is the platform where the grand finale is
hosted.

## Product Thesis

ArenaWealth Pro turns portfolio management into an auditable workbench. Users
can load holdings, inspect live data readiness, run deterministic cash
deployment, and replay evidence instead of trusting an opaque recommendation.

## Pitch Positioning

- Customer: long-term international equity investors, independent advisors, and
  research-driven wealth teams.
- Pain: recommendations are hard to audit, provider health is opaque, and
  historical claims are often not reproducible.
- Product: deterministic portfolio workbench with free-data health, snapshots,
  candidate screening, and cash-deployment guardrails.
- Differentiator: every decision can be tied to inputs, provider status, policy
  version, and replayable evidence.

## Demo Flow

1. Start with `./run.sh`.
2. Show portfolio source/import status: latest broker CSV versus manual edits.
3. Show data source health and provider readiness.
4. Show portfolio summary and live/stored price status.
5. Run cash-deployment recommendation with economic guardrails.
6. Show the Decision Log row created by the recommendation run.
7. Record a small manual buy/sell edit and show the source changing to manual.
8. Clear manual override and return to the broker export.
9. Run candidate screen.
10. Show `make price-backtest` output as evidence discipline, not a performance
   guarantee.

## Three-Minute Judge Narrative

1. Most portfolio tools hide data provenance and make recommendations that are
   hard to audit.
2. ArenaWealth shows the active portfolio source, provider health, and policy
   guardrails before making any recommendation.
3. The same workbench supports real investor operation and reviewer-grade
   reproducibility: import, edit, inspect, recommend, audit, screen, and replay.

## Use Cases to Demonstrate

- Retail holder: import an Avenue CSV, enter available cash, and see whether an
  order is economically large enough after fees.
- Self-directed analyst: compare current holdings against external moat and
  compounding candidates.
- Independent advisor: run the same deterministic policy per client portfolio,
  with source tracking and replayable evidence.
- Research reviewer: run the offline deterministic path and free price baseline
  without paid APIs.

## Product Proof Points

- One-command local demo: `./run.sh`.
- Free-data-first operation.
- Visible data-source status: configured, working, or error.
- Portfolio source provenance: broker export, manual override, fixture.
- Decision log: recommendation runs are timestamped with policy and inputs.
- Economic guardrails: no microscopic orders that lose to fees.
- Reproducibility boundary: claims are separated from limitations.

## Current Public Sources

- FinTech World Cup: https://fintechworldcup.com/
- Dubai FinTech Summit ecosystem events:
  https://dubaifintechsummit.com/ecosystem-events/
