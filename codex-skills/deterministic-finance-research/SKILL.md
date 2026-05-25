---
name: deterministic-finance-research
description: Use when building or reviewing financial research software that must make deterministic investment decisions, use free reproducible data sources, run baselines and ablations, and state limitations honestly.
metadata:
  short-description: Deterministic financial research workflows
---

# Deterministic Finance Research

Use this skill for research systems that evaluate portfolios, securities,
signals, or allocation policies.

## Workflow

1. Separate decision policy from data collection.
   - Policy functions must be deterministic: same inputs, same output.
   - Data freshness comes from timestamped snapshots, not from hidden state.

2. Prefer free reproducible sources.
   - Prices: adjusted historical prices from free providers.
   - Filings: regulator data with filing dates where available.
   - Macro: free public economic series.
   - Alternative data: free APIs only when the reviewer can obtain access.

3. Make the backtest defensible.
   - State the portfolio universe and survivorship limitations.
   - Apply realistic rebalance cadence, costs, turnover, and cash handling.
   - Lag fundamentals by filing date or a conservative delay.
   - Never use future restated fundamentals as if they were known.

4. Measure against baselines.
   - Market benchmark.
   - Equal-weight universe.
   - Current-weight or naive hold portfolio.
   - Known factor screens when relevant.

5. Run ablations.
   - Remove one signal family at a time.
   - Report when a signal adds no value.
   - Keep failed or null findings visible.

6. Keep claims tied to results.
   - Do not claim alpha, superiority, or state-of-the-art without tables.
   - If data is free but imperfect, state the bias directly.

## Output Standard

The final artifact should provide commands that regenerate metrics, tables, and
figures from free data or checked-in fixtures, and should distinguish live
operation from reproducible reviewer mode.

