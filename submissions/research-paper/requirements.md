# ICAIF Requirements Checklist

## Formatting

- [ ] Use ACM `acmart` with `sigconf`.
- [ ] Keep the paper to 8 pages total, including references.
- [ ] Remove supplementary-only claims; the paper must stand alone.
- [ ] Keep claims tied to generated tables or source citations.
- [ ] Avoid venue names in the executable artifact.

## Research Claims

- [ ] State the decision-support problem, not a regulated-advice claim.
- [ ] Explain why current portfolio recommendation workflows are hard to audit.
- [ ] Define deterministic replay: portfolio input, data snapshot, policy version,
      and rebalance instruction.
- [ ] State free-data limitations clearly: survivorship, ADR coverage, statement
      depth, and provider volatility.
- [ ] Avoid claiming state-of-the-art performance until backtests support it.

## Experiments

- [ ] Current-basket price study versus SPY.
- [ ] Equal-weight baseline.
- [ ] Rebalancing-cost ablation.
- [ ] Point-in-time SEC selection backtest.
- [ ] Moat-only, compounding-only, valuation-only, and full-policy ablations.
- [ ] Sensitivity to rebalance interval, costs, and concentration caps.
- [ ] Provider health report for each reproduced run.

## Artifact

- [ ] `make verify` passes.
- [ ] `make price-backtest` writes JSON under `exports/`.
- [ ] `make metrics` writes reviewer metrics.
- [ ] `./run.sh` starts API and UI after readiness checks.
- [ ] No private holdings, `.env`, or local framework material is committed.
