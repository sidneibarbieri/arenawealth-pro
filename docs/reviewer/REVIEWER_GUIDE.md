# Reviewer Guide

This guide is the intended first path through the artifact.

## Quick Start

```bash
python3.11 -m venv .venv
.venv/bin/pip install -e ".[dev]"
cd frontend && npm install && cd ..
make verify
make metrics
```

`make verify` runs Python lint, Python tests, frontend build, and frontend lint.
`make metrics` writes a timestamped JSON report under `exports/`.

To open the local workbench:

```bash
./run.sh
```

The runner starts the API first, waits for readiness, then starts the frontend.
It also clears stale local processes on the configured API and UI ports.

## Offline Analysis

```bash
.venv/bin/python scripts/moat_compounding_analysis.py \
  --cash 1511.18 \
  --holdings tests/fixtures/seed_portfolio_avenue.csv \
  --offline-demo
```

This path is deterministic and does not need API keys.

## Free Price Backtest

```bash
make price-backtest
```

This path uses free adjusted closes and writes a JSON report under `exports/`.
It compares the current basket against `SPY`, equal-weight holdings, and a
rebalancing ablation with transaction costs. It is useful for checking risk and
benchmark behavior of the current basket. It does not claim point-in-time
stock-selection performance.

## Local App

```bash
./run.sh
```

Open `http://127.0.0.1:5173`.

The Data Sources Health panel defaults to configuration checks. Use "Run live
check" to test free providers that have local credentials configured.

## End-to-End Smoke Test

```bash
cd frontend
npx playwright install chromium
npm run test:e2e
```

The Playwright config starts the API and frontend if they are not already
running.

## Scope

The artifact supports portfolio analysis, cash-deployment recommendations, and
reviewer metrics.
