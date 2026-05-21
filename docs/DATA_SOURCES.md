# Data Sources and Known Biases

Every data source is free and re-runnable, so the artifact reproduces without
paid subscriptions.

## Sources

- Prices: Yahoo Finance (`yfinance`), split- and dividend-adjusted historical
  closes.
- Fundamentals (live analysis): Yahoo Finance statements, about four to five
  fiscal years.
- Point-in-time fundamentals (for backtests): SEC EDGAR company facts, which
  carry filing dates and so avoid look-ahead for US filers.
- Risk factors (for factor-adjusted alpha): Kenneth French Data Library.
- Innovation signal: PatentsView API.

## Known Biases and Limitations

- Survivorship: a fixed current universe omits delisted names, so a backtest
  over a fixed known set overstates returns. Results state this explicitly.
- Restatement and look-ahead: Yahoo statements are as-restated, not
  point-in-time. Fundamental backtests must use SEC EDGAR filing dates.
- ADR coverage: SEC EDGAR covers US filers; foreign issuers have thinner
  point-in-time coverage and are flagged or excluded in backtests.
- History depth: free statement history is shorter than paid point-in-time
  vendors, which limits market-regime coverage.

Performance is reported only with these biases stated and, where possible,
bounded.
