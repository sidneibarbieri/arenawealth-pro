# ArenaWealth Pro

ArenaWealth Pro is a portfolio analysis system for international equities. The
repository contains a FastAPI backend, a Vite/React dashboard, deterministic
portfolio scoring utilities, and reviewer-facing validation scripts.

The supported artifact is the Python backend, the analysis CLI, the React
workbench, and reviewer-facing validation scripts.

## Requirements

- Python 3.11+
- Node 20+ for frontend checks

## Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cd frontend && npm install && cd ..
```

Equivalent shortcut:

```bash
make setup
```

## Backend Validation

```bash
ruff check .
pytest -q
```

The test suite uses isolated SQLite databases and does not require API keys.

Full local verification:

```bash
make verify
```

## Analysis CLI

```bash
python scripts/moat_compounding_analysis.py --cash 1511.18
```

Reviewer-safe offline run:

```bash
python scripts/moat_compounding_analysis.py \
  --cash 1511.18 \
  --holdings tests/fixtures/seed_portfolio_avenue.csv \
  --offline-demo
```

By default, fundamentals come from Yahoo Finance. If `FMP_API_KEY` is present in
`.env` or `~/.arenawealth/credentials.env`, the CLI uses Financial Modeling Prep
for structured financial statements. Live mode depends on external providers;
offline demo mode does not.

Private portfolio CSVs are intentionally ignored by Git. The default local path
is `data/carteira_atual.csv`; reviewers should use the fixture command above.

## Cash Recommendation API

```bash
curl "http://127.0.0.1:8000/api/v1/portfolio/user/recommendation?cash=1511.18"
```

For a deterministic reviewer run without external market data:

```bash
curl "http://127.0.0.1:8000/api/v1/portfolio/user/recommendation?cash=1511.18&offline_demo=true"
```

## Reviewer Metrics

```bash
python scripts/reviewer_metrics.py
```

This writes a JSON report under `exports/` with lint status, test status, source
file counts, and line counts. Generated reports are not committed.

## Price Backtest

```bash
make price-backtest
```

This compares the current basket against `SPY` and an equal-weight baseline
using free adjusted closes from Yahoo Finance. It also reports a rebalancing
ablation with transaction costs. The output is a JSON report under `exports/`.
It is a current-basket price study, not a point-in-time stock-selection study.
The data limitations are listed in `docs/DATA_SOURCES.md`.

## API

```bash
make api
```

Main routes:

- `GET /api/v1/health`
- `GET /api/v1/portfolio/user`
- `GET /api/v1/portfolios`

## Frontend

```bash
make ui
```

Open `http://127.0.0.1:5173`.

To run both API and frontend in one terminal:

```bash
make app
```

End-to-end browser smoke test:

```bash
cd frontend
npx playwright install chromium
npm run test:e2e
```

The Playwright config starts the API and frontend when needed.

## Paper Scaffold

The LaTeX paper scaffold is under `paper/`. It uses the `acmart` document class
in anonymous review mode and names no venue, author, or institution.

## Scope Notes

Archived files in `archive/` are retained for recovery only. They are not part of
the supported reviewer artifact. Useful ideas mined from the archive are tracked
in `docs/reviewer/ARCHIVE_INSIGHT_LEDGER.md`.

This repository is not a registered investment adviser or broker-dealer system.
Commercial use requires legal, compliance, security, data-licensing, and
disclosure review before marketing recommendations to customers.
