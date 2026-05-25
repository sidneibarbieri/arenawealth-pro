# User Stories and Demonstration Flows

The app serves two audiences: a reviewer who needs reproducible evidence and an
operator who manages a real portfolio. Product features must support both
without mixing their claims.

## Reviewer Stories

1. As a reviewer, I can run the full validation gate with one command so I can
   verify that the artifact is executable.
   - Demo: `make verify`
   - Evidence: lint, unit tests, integration tests, frontend build, ESLint.

2. As a reviewer, I can run the offline recommendation path without API keys so
   I can reproduce a deterministic decision.
   - Demo: `python scripts/moat_compounding_analysis.py --offline-demo`
   - Evidence: deterministic provider mode and stable output.

3. As a reviewer, I can inspect data-source readiness without seeing secrets so
   I can judge which free sources are available.
   - Demo: app Data Sources Health panel or `/api/v1/data-sources/health`
   - Evidence: configured/not configured by provider, live check on demand.

4. As a reviewer, I can run a free price-history baseline so I can see what is
   measured and what is not claimed.
   - Demo: `make price-backtest`
   - Evidence: SPY, equal-weight, current-weight, rebalance ablation.

## Portfolio Operator Stories

1. As an investor, I can open the workbench quickly so I can see portfolio state
   before running expensive analysis.
   - Current support: cached quotes and analysis on demand.
   - Next support: visible cache age and stale/live badges by data source.

2. As an investor, I can run live analysis only when I ask for it so the UI does
   not block on external providers.
   - Current support: cash deployment analysis runs from the Analyze button.
   - Next support: background job status for longer screens.

3. As an investor, I can record a buy or sell so the tracked portfolio matches
   reality.
   - Current support: Portfolio Editor records buy/sell events into a local
     normalized CSV under `data/inbox`.
   - Next support: full transaction ledger, cash ledger, and portfolio switcher.

4. As an investor, I can drop a broker CSV into a local inbox so the app uses
   the freshest exported portfolio automatically.
   - Current support: `data/inbox/*.csv`, newest file wins.
   - Next support: in-app import status, validation errors, and import history.

5. As an investor, I can add a new candidate to the watched universe so I can
   compare it against current holdings.
   - Current support: curated candidate screen.
   - Next support: editable watchlist with provider-backed validation.

6. As an advisor, I can evaluate multiple client portfolios independently so
   deterministic rules are applied per client.
   - Current support: repository layer supports multiple portfolios.
   - Next support: UI portfolio switcher, data isolation, audit log, and
     compliance workflow.

## Product Pitch Stories

1. As a judge, I can see the app start locally with one command.
   - Demo: `./run.sh`

2. As a judge, I can see whether free data sources are ready.
   - Demo: Data Sources Health, live check on demand.

3. As a judge, I can see the product make a transparent recommendation.
   - Demo: cash deployment, guardrails, ranked holdings, exclusions.

4. As a judge, I can see why the product is not a black box.
   - Demo: moat, compounding, valuation, concentration rules, and data limits.

## Interface Principles

- Load the operating surface before running slow network analysis.
- Cache collected observations with timestamps and show freshness.
- Keep live checks explicit; do not surprise the user with expensive calls.
- Separate editable portfolio state from reproducible reviewer fixtures.
- Use restrained branding: distinctive enough for a pitch, quiet enough for
  repeat analytical work.
