# Paper Path

The current artifact is a portfolio analytics system. It is not yet evidence
that the method beats the state of the art.

## Plausible Venue Fit

- AI and computational finance venues for tool and method papers.
- Finance venues only after a strong empirical contribution is added.

## Evidence Still Needed

- Out-of-sample backtests across multiple market regimes.
- Baselines against factor portfolios, quality screens, equal-weight portfolios,
  market-cap indexes, and common robo-advisor logic.
- Transaction cost, fee, tax, turnover, and slippage modeling.
- Ablations for moat, compounding, valuation, concentration, and theme rules.
- Sensitivity analysis for thresholds and provider data quality.
- Reproducible datasets or licensed data access instructions.
- Reviewer scripts that regenerate every table and figure used in the paper.

## Current Reviewer Command

```bash
python scripts/reviewer_metrics.py
```

This validates lint, tests, and deterministic offline analysis. It does not
claim investment outperformance.
