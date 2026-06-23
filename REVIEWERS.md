# Reviewer Guide

This artifact accompanies the manuscript on auditing AI investment
recommendations against a deterministic, replayable baseline. It is anonymous and
self-contained: every figure, table, and numerical claim is regenerated offline
from the code and the tracked data in this snapshot. No network access, API key,
or private data is required.

## Bit-exact reproduction in a container

```bash
make repro-docker
```

Builds a pinned Python image, verifies the data hashes, runs lint and the test
suite, runs the privacy scanner, and regenerates every figure and JSON report
from tracked inputs. This is the science end to end; it needs no host setup
beyond Docker.

## One-command reproduction on the host

```bash
make all
```

This runs, in order:

1. `setup` - virtualenv and dependencies (`pip install -e ".[dev]"`) plus frontend.
2. `verify-data` - SHA-256 check of frozen tracked inputs.
3. `privacy-audit` - high-confidence scan for author identity, local paths,
   private fixture sentinels, emails, and secret tokens.
4. `verify` - lint and the full test suite (no network, isolated SQLite).
5. `price-backtest-reference` - regenerate the offline backtest reference from
   `paper/data/returns_matrix.csv`.
6. `experiments` - regenerate every paper figure under `paper/figures/` and the
   JSON report under `exports/` from the engine and the tracked return matrix.
7. `ai-advisor-audit` and `advisor-run-audit` - replay frozen advisor scenarios
   and cached provider outputs without API calls.
8. `figure-audit` - verify generated PDF figures are vector and font-embedded.
9. `paper` - compile `paper/main.pdf` with `latexmk` (requires a TeX install).

Host reproduction:

```bash
make setup      # installs Python and frontend dependencies
make verify-data   # SHA-256 of tracked inputs vs paper/data/DATA_HASHES.txt
make privacy-audit # anonymity, private-data, and secret-token gate
make verify        # tests + lint
make price-backtest-reference
make experiments   # regenerate figures and the JSON report
make ai-advisor-audit
make advisor-run-audit   # re-audit cached paid-provider outputs, no live calls
make figure-audit
```

## Dashboard path

The dashboard is a reviewer aid, not required for the paper claims. To run it
against the tracked fixture and a clean temporary SQLite database:

```bash
rm -f tmp/reviewer-dashboard.db
ARENAWEALTH_PORTFOLIO_INBOX="$PWD/tests/fixtures" \
ARENAWEALTH_DATABASE_PATH="$PWD/tmp/reviewer-dashboard.db" \
./run.sh
```

Open `http://127.0.0.1:5173/?offline_demo=true&cash=1500.00` and click
`Analyze`. The UI exposes the same evidence path as the paper: tracked input
source, deterministic reviewer mode, proposed orders, guardrails, and a decision
log.

## What maps to what

| Paper element | Produced by |
| --- | --- |
| Fee rules and guardrail | `src/arenawealth/analytics/deployment.py` and deployment tests |
| Fee premium figure | `src/arenawealth/experiments/fee_landscape.py` |
| Planner optimality vs MIP | `src/arenawealth/experiments/planner_optimality.py` (in `make experiments`) |
| Schedule table | `src/arenawealth/experiments/fee_sensitivity.py` |
| Ablation evidence | `src/arenawealth/experiments/ablation.py` |
| Backtest table | `paper/data/price_backtest_reference.json` |
| Robustness figure | `src/arenawealth/experiments/robustness.py` and tracked returns |
| Advisor audit | `src/arenawealth/experiments/ai_advisor.py` and frozen scenarios |
| Audit scenarios (frozen) | `paper/data/ai_advisor_scenarios.json` |
| Cached paid-provider pilot | `paper/data/advisor_runs/azure/chat/*.json` |
| Replay determinism | `tests/test_user_portfolio_api.py` |
| Privacy gate | `scripts/check_artifact_privacy.py` |

## Determinism

The engine draws no random numbers; ranking ties break by ticker; the bootstrap
uses a fixed seed. Re-running `make experiments` reproduces identical figures and
statistics. The recommendation path is a pure function of
`(holdings, fundamentals, cash, policy version)`.

The tracked holdings CSV is synthetic: the tickers are public companies, but the
share counts, prices, cost bases, and cash amount are reviewer fixtures rather
than private portfolio data.

## New experiments

Fresh free-price experiments are opt-in:

```bash
make price-backtest
```

That command fetches current Yahoo Finance adjusted closes and writes ignored
JSON under `exports/`. It is useful for exploratory reviewer checks, but it does
not change the paper unless the result is promoted to a tracked reference and
the data manifest is rewritten.

Paid-provider advisor collection is also opt-in. Use `make advisor-budget`
first, then run `scripts/collect_advisor_runs.py` with `--live`, credentials,
and an explicit call cap. Cached outputs are replayed by default, so ordinary
review never spends money.

## Scope

The bibliography under `paper/bibliography/` catalogs all cited works; paywalled
PDFs are listed in `paper/bibliography/_order.txt`. Findings are reported with
their limitations: the audit protocol is demonstrated on deterministic archetype
controls plus a small cached provider pilot; the backtest is a single-basket,
non-point-in-time study; and the weighting ablation uses deterministic synthetic
fundamentals to demonstrate mechanism.

Collecting real model advisors is optional and isolated in
`scripts/collect_advisor_runs.py`: it is budget-guarded, caches every run to
JSON, and makes no calls without `--live` and Azure credentials. The reported
results do not depend on it.
