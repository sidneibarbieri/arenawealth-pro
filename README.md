# ArenaWealth

ArenaWealth is a portfolio analysis system for international equities. The
repository contains a FastAPI backend, a Vite/React dashboard, deterministic
portfolio scoring utilities, and reviewer-facing validation scripts.

The supported artifact is the Python backend, the analysis CLI, the React
workbench, and reviewer-facing validation scripts.

## Requirements

- Python 3.11+
- Node 20+ for frontend checks

## Setup

```bash
make setup
```

Manual equivalent:

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
cd frontend && npm install && cd ..
```

To create a local `.env` template for free data-provider configuration:

```bash
make configure-env
```

The generated `.env` is ignored by Git. It contains no required paid services.

## One-Shot Reproduction

```bash
make all
```

This runs `setup`, `verify`, `experiments`, and `paper` in sequence: it installs
dependencies, runs the test suite, regenerates the manuscript figures from the
production engine, and compiles the PDF. Everything is offline; the backtest
figure reuses the tracked reference in `paper/data/`.

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
  --holdings tests/fixtures/seed_portfolio_broker.csv \
  --offline-demo
```

By default, fundamentals come from Yahoo Finance. If `FMP_API_KEY` is present in
`.env` or `~/.arenawealth/credentials.env`, the CLI uses Financial Modeling Prep
for structured financial statements. Live mode depends on external providers;
offline demo mode does not.

Private portfolio CSVs are intentionally ignored by Git. The default local path
is `data/carteira_atual.csv`; reviewers should use the fixture command above.

For broker exports, place the latest CSV under `data/inbox/`. The app reads the
newest CSV in that directory first, then falls back to `data/carteira_atual.csv`,
then to the tracked reviewer fixture. This lets a local user download a fresh
portfolio export without editing code or committing private data.

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

## Experiments and Manuscript Figures

```bash
make experiments
```

This regenerates the fee, guardrail, ablation, and backtest figures under
`paper/figures/` and writes an experiment JSON report under `exports/`. These
experiments use the production engine and are the source for the manuscript's
findings. The current research ledger is `docs/SCIENTIFIC_LEDGER.md`.

## Bibliography Library

```bash
make bibliography
```

This refreshes `paper/bibliography/CATALOG.md`,
`paper/bibliography/PDF_INDEX.json`, and `paper/bibliography/_order.txt` from
`paper/bibliography/sources.json`. The command downloads only open PDFs and
leaves paywalled or interactive sources in `_order.txt` for manual, licensed
download. PDFs are ignored by Git and are not required to reproduce the artifact.

## API

```bash
make api
```

Main routes:

- `GET /api/v1/health`
- `GET /api/v1/data-sources/health`
- `GET /api/v1/portfolio/user`
- `GET /api/v1/portfolios`

## Frontend

```bash
make ui
```

Open `http://127.0.0.1:5173`.

To run both API and frontend in one terminal:

```bash
./run.sh
```

`./run.sh` frees stale local ports, starts the API, waits for the health check,
then starts the frontend. It prints log file paths under `/tmp/` and stops both
processes on Ctrl+C. `make app` and `make run` call the same script.

End-to-end browser smoke test:

```bash
cd frontend
npx playwright install chromium
npm run test:e2e
```

The Playwright config starts the API and frontend when needed.

## Paper Scaffold

The LaTeX paper scaffold is under `paper/`. It is anonymous and names no
submission target, author, or institution. Submission-specific packets and
private strategy notes are not part of the publishable artifact.

## Scope Notes

Archived files in `archive/` are retained for recovery only. They are not part of
the supported reviewer artifact. Useful ideas mined from the archive are tracked
in `docs/reviewer/ARCHIVE_INSIGHT_LEDGER.md`.

This repository is not a registered investment adviser or broker-dealer system.
Commercial use requires legal, compliance, security, data-licensing, and
disclosure review before marketing recommendations to customers.
