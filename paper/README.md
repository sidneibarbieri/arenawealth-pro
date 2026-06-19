# Paper

A neutral anonymous manuscript for ArenaWealth. It names no submission
target, author, or institution.

## Reproducing the results

Every figure and table is recreated offline from the production engine. Regenerate
them, then build the PDF:

```bash
make experiments      # writes figures/*.tikz and exports/experiments_*.json
make paper            # latexmk -pdf main.tex
```

`figures/` is recreated with `scripts/run_experiments.py`; the backtest table
reuses the tracked reference data in `paper/data/price_backtest_reference.json`
(regenerate exploratory exports with `make price-backtest`). The experiment modules in
`src/arenawealth/experiments/` are pure and unit-tested
(`tests/unit/test_experiments.py`).

## Scope of claims

The manuscript's contribution is methodological (deterministic optimization under
a subadditive fee structure, with provable guardrails). Empirical sections are
explicitly bounded: the backtest is a current-basket study on free adjusted
closes (not point-in-time), and the ablation uses deterministic synthetic
fundamentals to demonstrate mechanism. No investment-outperformance claim is made
beyond these caveats.
