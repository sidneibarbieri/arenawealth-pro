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
suite, and regenerates every figure and JSON report from tracked inputs. This is
the science end to end; it needs no host setup beyond Docker.

## One-command reproduction on the host

```bash
make all
```

This runs, in order:

1. `setup` — virtualenv and dependencies (`pip install -e ".[dev]"`) plus frontend.
2. `verify` — lint and the full test suite (no network, isolated SQLite).
3. `experiments` — regenerate every paper figure under `paper/figures/` and the
   JSON report under `exports/` from the engine and the tracked return matrix.
4. `paper` — compile `paper/main.pdf` with `latexmk` (requires a TeX install).

Host reproduction:

```bash
make setup      # installs Python and frontend dependencies
make verify-data   # SHA-256 of tracked inputs vs paper/data/DATA_HASHES.txt
make verify        # tests + lint
make experiments   # regenerate figures and the JSON report
```

## What maps to what

| Paper element | Produced by |
| --- | --- |
| Fee propositions | `src/arenawealth/analytics/deployment.py` and deployment tests |
| Fee premium + guardrail figures | `src/arenawealth/experiments/fee_landscape.py` |
| Schedule table | `src/arenawealth/experiments/fee_sensitivity.py` |
| Ablation evidence | `src/arenawealth/experiments/ablation.py` |
| Backtest table | `paper/data/price_backtest_reference.json` |
| Robustness figure | `src/arenawealth/experiments/robustness.py` and tracked returns |
| Advisor audit | `src/arenawealth/experiments/ai_advisor.py` and frozen scenarios |
| Audit scenarios (frozen) | `paper/data/ai_advisor_scenarios.json` |
| Replay determinism | `tests/test_user_portfolio_api.py` |

## Determinism

The engine draws no random numbers; ranking ties break by ticker; the bootstrap
uses a fixed seed. Re-running `make experiments` reproduces identical figures and
statistics. The recommendation path is a pure function of
`(holdings, fundamentals, cash, policy version)`.

## Scope

The bibliography under `paper/bibliography/` catalogs all cited works; paywalled
PDFs are listed in `paper/bibliography/order.txt`. Findings are reported with
their limitations: the audit protocol is demonstrated on deterministic archetype
controls (not live model outputs); the backtest is a single-basket,
non-point-in-time study; and the weighting ablation uses deterministic synthetic
fundamentals to demonstrate mechanism.

Collecting real model advisors is optional and isolated in
`scripts/collect_advisor_runs.py`: it is budget-guarded, caches every run to
JSON, and makes no calls without `--live` and Azure credentials. The reported
results do not depend on it.
