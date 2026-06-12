# Vision

ArenaWealth Pro aims to make portfolio decisions easier to audit. The product
should expose the data, rules, and trade-offs behind each recommendation instead
of presenting opaque advice.

## Product Direction

- Keep portfolio data importable from common broker CSV exports.
- Keep scoring deterministic and explainable.
- Keep provider access replaceable through small interfaces.
- Keep reviewer validation simple: install, lint, test, run metrics.
- Separate implemented behavior from future research ideas.
- Treat model portfolios as policy templates, not universal prescriptions.
- Preserve determinism in advisor workflows by pinning portfolio input, data
  snapshot, and policy version.

## Current Focus

The current artifact focuses on:

- immutable domain models
- CSV import
- FastAPI portfolio workflows
- provider abstractions
- moat, compounding, and deployment analytics
- reproducibility metrics for reviewers
- deterministic candidate screening and portfolio review
- current-basket price-history baselines

## Future Work

- correlation-aware allocation
- web editing for imported and manually entered portfolios
- advisor-grade data isolation and audit logs
- liquidity and market-impact constraints
- tax-aware deployment
- transaction-fee capture for manual trades and broker promotions
- option-income overlays for holders, scoped as a separate derivatives layer
- broader provider coverage
- external experiment integration when the external artifacts are available
