# Reproducibility Guide

This guide describes the supported reviewer workflow for ArenaWealth.

## Environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cd frontend && npm install && cd ..
```

No API keys are required for the unit and integration tests.

Optional free provider credentials can be configured with:

```bash
make configure-env
```

The generated `.env` is ignored by Git.

## Validation

```bash
make verify
```

Expected result in the current artifact: Python lint, Python tests, frontend
build, and frontend lint pass.

## Metrics

```bash
make metrics
```

The script records:

- lint command and return code
- test command and return code
- Git working tree status
- Python source file count
- test file count
- source and test line counts
- deterministic offline recommendation command status

The output is written to `exports/reviewer_metrics_<timestamp>.json`.

## Reviewer Dashboard

Run the web workbench with tracked fixture data and a clean temporary decision
log:

```bash
rm -f tmp/reviewer-dashboard.db
ARENAWEALTH_PORTFOLIO_INBOX="$PWD/tests/fixtures" \
ARENAWEALTH_DATABASE_PATH="$PWD/tmp/reviewer-dashboard.db" \
./run.sh
```

Open `http://127.0.0.1:5173/?offline_demo=true&cash=1511.18` and click
`Analyze`. The dashboard shows the tracked input source, deterministic reviewer
mode, proposed orders, guardrails, and the decision log.

## Portfolio Analysis

```bash
python scripts/moat_compounding_analysis.py \
  --cash 1511.18 \
  --holdings tests/fixtures/seed_portfolio_broker.csv \
  --offline-demo
```

The offline demo path reads holdings from a tracked fixture, uses deterministic
demo fundamentals, and prints a deployment plan. Local holdings and generated
exports are ignored by Git because they may contain private portfolio data.

## Free Price Study

```bash
make price-backtest
```

This uses free Yahoo Finance adjusted closes. The report compares the current
basket against `SPY`, an equal-weight basket, and a rebalancing ablation with
transaction costs. It is reproducible as a price-history study, but it is not a
point-in-time stock-selection backtest.

## Optional Data Providers

Provider priority is FMP, then Finnhub, then Yahoo Finance. The offline demo
mode avoids external providers entirely.

The local app exposes provider readiness without returning secret values:

```bash
curl http://127.0.0.1:8000/api/v1/providers/status
curl http://127.0.0.1:8000/api/v1/data-sources/health
curl "http://127.0.0.1:8000/api/v1/data-sources/health?live=true"
```

Optional keys can be stored in `.env` or `~/.arenawealth/credentials.env`.
Reviewer runs do not require them.

## Cached Advisor Outputs

The paper's small paid-provider pilot is preserved under
`paper/data/advisor_runs/azure/chat/`. Re-audit those cached outputs without
making provider calls:

```bash
make advisor-run-audit
```

To estimate a future live run before spending money:

```bash
make advisor-budget
```

## Known Limits

The current artifact includes a current-basket price study and regenerated
paper figures. It does not include a point-in-time fundamental selection
backtest or factor-adjusted alpha. Performance claims require that empirical
work first.
