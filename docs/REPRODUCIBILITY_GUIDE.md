# Reproducibility Guide

This guide describes the supported reviewer workflow for ArenaWealth Pro.

## Environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cd frontend && npm install && cd ..
```

No API keys are required for the unit and integration tests.

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

## Portfolio Analysis

```bash
python scripts/moat_compounding_analysis.py \
  --cash 1511.18 \
  --holdings tests/fixtures/seed_portfolio_avenue.csv \
  --offline-demo
```

The offline demo path reads holdings from a tracked fixture, uses deterministic
demo fundamentals, and prints a deployment plan. Local holdings and generated
exports are ignored by Git because they may contain private portfolio data.

## Optional Data Providers

Provider priority is FMP, then Finnhub, then Yahoo Finance. The offline demo
mode avoids external providers entirely.

## Known Limits

This repository does not include `sticks-docker`, MITRE campaign execution, or
security experiment measurements. Those measurements must come from the external
artifact that actually implements them.

The current artifact also does not yet include investment backtests, benchmark
baselines, ablations, paper table generation, or manuscript-value
synchronization.
