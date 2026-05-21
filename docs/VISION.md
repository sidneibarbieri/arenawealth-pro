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

## Current Focus

The current artifact focuses on:

- immutable domain models
- CSV import
- FastAPI portfolio workflows
- provider abstractions
- moat, compounding, and deployment analytics
- reproducibility metrics for reviewers

## Future Work

- correlation-aware allocation
- liquidity and market-impact constraints
- tax-aware deployment
- broader provider coverage
- external experiment integration when the external artifacts are available
