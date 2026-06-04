# Reviewer Guide

This artifact accompanies the manuscript on deterministic cash deployment under a
subadditive fee. It is anonymous and self-contained: every figure, table, and
numerical claim in the paper is regenerated offline from the code and the tracked
data in this snapshot. No network access, API key, or private data is required.

## One-command reproduction

```bash
make all
```

This runs, in order:

1. `setup` — create a virtualenv and install dependencies (`pip install -e ".[dev]"`)
   plus the frontend packages.
2. `verify` — lint and the full test suite (no network, isolated SQLite).
3. `experiments` — regenerate every paper figure under `paper/figures/` and the
   numeric report under `exports/` from the production engine and the tracked
   return matrix (`paper/data/returns_matrix.csv`).
4. `paper` — compile `paper/main.pdf` with `latexmk` (requires a TeX install).

If you only want the science (no TeX, no frontend):

```bash
python3.11 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
make verify        # tests + lint
make experiments   # regenerate figures and the JSON report
```

## What maps to what

| Paper element | Produced by |
| --- | --- |
| Subadditivity, fee-worsening propositions | `src/arenawealth/analytics/deployment.py`, tests in `tests/unit/test_analytics_deployment.py` |
| Fee premium + guardrail figures | `src/arenawealth/experiments/fee_landscape.py` |
| Sensitivity figure + schedule table | `src/arenawealth/experiments/fee_sensitivity.py` |
| Ablation figure/table | `src/arenawealth/experiments/ablation.py` |
| Backtest table/figure | `paper/data/price_backtest_reference.json` (tracked) |
| Robustness figure + bootstrap CI | `src/arenawealth/experiments/robustness.py`, `paper/data/returns_matrix.csv` |
| Replay-determinism guarantee | `tests/test_user_portfolio_api.py::test_recommendation_is_replayable_from_same_inputs` |

## Determinism

The engine draws no random numbers; ranking ties break by ticker; the bootstrap
uses a fixed seed. Re-running `make experiments` reproduces identical figures and
statistics. The recommendation path is a pure function of
`(holdings, fundamentals, cash, policy version)`.

## Scope

The bibliography under `paper/bibliography/` catalogs all cited works; paywalled
PDFs are listed in `paper/bibliography/order.txt`. The findings are reported with
their limitations: the backtest is a single-basket, non-point-in-time study, and
the ablation uses deterministic synthetic fundamentals to demonstrate mechanism.
