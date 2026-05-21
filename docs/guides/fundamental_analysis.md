# Fundamental Analysis

The supported analysis path is `scripts/moat_compounding_analysis.py`.

The CLI reads holdings from `data/carteira_atual.csv`, obtains fundamentals from
the configured provider, computes position-level scores, and emits a deployment
plan. The scoring logic lives in `arenawealth.analytics.scoring`.

For reviewer runs without network access:

```bash
python scripts/moat_compounding_analysis.py \
  --cash 1511.18 \
  --holdings tests/fixtures/seed_portfolio_avenue.csv \
  --offline-demo
```

## Inputs

- shares
- average cost
- broker price
- current fundamentals
- historical revenue, EBIT, EPS, free cash flow, shares, and invested capital

## Outputs

- moat class
- compounding class
- valuation points
- composite score
- deterministic buy plan

## Provider Selection

Yahoo Finance is the default provider. If `FMP_API_KEY` is configured,
`FMPFundamentalsProvider` is used for structured statement data.
