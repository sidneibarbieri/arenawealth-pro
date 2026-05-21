# Claims Evidence Matrix

| Claim | Evidence | Status |
| --- | --- | --- |
| The Python package passes lint and tests. | `make verify` | Supported |
| The frontend builds and passes ESLint. | `make verify` | Supported |
| The reviewer can run a deterministic offline recommendation. | `scripts/moat_compounding_analysis.py --offline-demo` | Supported |
| The app exposes a live cash-deployment endpoint. | `GET /api/v1/portfolio/user/recommendation` | Supported |
| The live recommendation uses external data when provider keys are available. | Provider mode in CLI/API output | Supported with provider availability |
| The method beats market or advisor baselines. | Backtests and baselines are not implemented yet. | Not supported |
| The artifact executes MITRE campaigns. | No MITRE executor exists in this repository. | Not supported |
| The system is ready for regulated commercial advice. | Compliance, licensing, audit, and suitability workflows remain open. | Not supported |

## Required Before Performance Claims

- Out-of-sample backtests over multiple market regimes.
- Baselines against market-cap indexes, equal-weight portfolios, quality-factor
  screens, and common robo-advisor policies.
- Transaction cost, tax, slippage, and turnover modeling.
- Ablations for moat, compounding, valuation, concentration, and theme rules.
- Data-quality reporting for each provider and metric.
