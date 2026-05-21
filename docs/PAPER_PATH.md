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
make verify
make metrics
```

This validates lint, tests, and deterministic offline analysis. It does not
claim investment outperformance.

## Venue Scaffold

The current LaTeX scaffold is `paper/acm-icaif/main.tex`. It uses ACM `sigconf`
review format because the most coherent computing-and-finance target is ACM
ICAIF. See `docs/PAPER_TARGET.md` for the venue/prize distinction.
