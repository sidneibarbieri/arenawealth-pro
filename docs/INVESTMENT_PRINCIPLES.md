# Investment Principles

ArenaWealth Pro is built around deterministic portfolio rules. The system should
only recommend trades that improve or preserve portfolio quality while
respecting concentration constraints.

## Core Rules

- Quality comes first: low-quality names should not be added only because they
  look statistically cheap.
- Position concentration is bounded before cash is deployed.
- Theme concentration is bounded so a deployment does not add the same risk twice.
- Cash deployment is fee-aware and deterministic.
- Scoring logic should be explainable from source data.

## Current Implementation

The supported implementation lives in `arenawealth.analytics`:

- `scoring.py` computes moat, compounding, valuation, and composite scores.
- `deployment.py` applies concentration, theme, and fee rules.
- `fundamentals.py` keeps network access behind provider classes.

The current deployment planner skips overweight positions, avoids selecting two
positions from the same theme, and sizes orders so fee tiers remain explicit.

## Known Gaps

- No portfolio-wide correlation matrix is implemented.
- No tax optimization is implemented.
- No liquidity or market-impact model is implemented.
- No external `sticks-docker` measurements are present in this repository.

These gaps should be described as future work unless implemented and tested.
