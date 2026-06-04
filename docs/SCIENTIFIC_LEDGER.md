# Scientific Ledger

This ledger records findings, negative results, hypotheses, and research gaps.
It is not a paper generator. Papers should consume this evidence, inspect the
generated artifacts, and report only what the experiments support.

## Current Findings

### F1. Broker fee subadditivity creates a diversification premium

The fee model is a step function: `f(a) = ceil(a / T) * c`. It is subadditive,
so splitting a fixed cash amount can never reduce fees. The experiment suite
measures the premium of naive splitting and verifies that the fee-aware planner
stays on the zero-premium frontier.

Evidence:

- `src/arenawealth/experiments/fee_landscape.py`
- `scripts/run_experiments.py`
- `paper/figures/fee_premium.png`
- regression tests in `tests/unit/test_analytics_deployment.py`

### F2. The minimum order is a fixed point, not a tuned constant

The order floor follows from the fee-impact constraint: `2.50 / 0.01 = 250`.
This is a closed-form guardrail that prevents microscopic orders from losing
too much to fixed fees.

Evidence:

- `MIN_ORDER_AMOUNT` in `src/arenawealth/analytics/deployment.py`
- `paper/figures/guardrail.png`

### F3. The fundamentals-weighted basket ranks third of five against allocator baselines

Backtested 2021-01-05 to 2026-05-28 (1355 days), the score-weighted basket beats
SPY (+4.80 pp CAGR, +0.15 Sharpe) and minimum variance on return (+4.16 pp CAGR),
but ranks third of five on Sharpe ratio: equal weight (1.19) and risk parity
(1.18) both beat the tuned weighting (1.10), while minimum variance gives the
shallowest drawdown (-19.1% vs -28.9%) at the cost of return. Two of the
strongest baselines (equal weight, risk parity) use no fundamental data. This is
a useful negative result consistent with the literature on naive diversification;
it clarifies that the contribution is methodological, not performance.

Evidence:

- `src/arenawealth/analytics/allocators.py` (min-variance, risk-parity)
- `tests/unit/test_analytics_allocators.py`
- `paper/data/price_backtest_reference.json` (`sota_baselines`, `sota_comparisons`)
- `paper/figures/backtest.png`
- `paper/main.tex` (Table 2)

### F4. Factor weights may be less important than selection

The deterministic ablation shows that equal thirds tracks the tuned baseline
closely while single-factor rankings diverge. This is mechanism evidence only,
because the ablation uses deterministic demo fundamentals.

Evidence:

- `src/arenawealth/experiments/ablation.py`
- `paper/figures/ablation.png`

## State-of-the-Art Reference Points

The project should be compared against these families, not against vague
"market tools":

- Quality factor research: profitability, quality-minus-junk, balance-sheet
  strength, and earnings quality.
- Moat index construction: wide-moat selection plus valuation discipline.
- Naive diversification: equal-weight and `1/N` benchmarks.
- Broad market baselines: SPY or a comparable broad benchmark.
- Portfolio operation tools: source provenance, provider health, audit logs,
  and replayability.

Reference anchors:

- Novy-Marx (2013), gross profitability premium.
- Asness, Frazzini, and Pedersen (2019), quality-minus-junk.
- DeMiguel, Garlappi, and Uppal (2009), naive `1/N` diversification.
- Morningstar Wide Moat Focus methodology, as a public moat-plus-valuation
  reference point.

Current honest position:

- We do not yet prove investment outperformance over the state of the art.
- We do show a reproducible optimization contribution around fee-aware cash
  deployment.
- We have evidence that the current weighting policy is not superior to equal
  weighting on the tested basket.
- The next scientific delta is a free point-in-time selection backtest with
  quality/moat baselines and ablations.

## Computation-Theory Strategies Used

| Strategy | Where it appears |
| --- | --- |
| Subadditive cost analysis | F1; diversification premium $\pi$ in `fee_landscape.py`. |
| Closed-form fixed point | F2; guardrail derivation MIN = c/τ in `deployment.py`. |
| Linear functional ablation | F4; recomposing the composite under alternative weight vectors without re-scoring. |
| Property-based testing across a grid | `test_planner_never_overpays_single_order_fee_across_grid`. |
| Rank correlation (Spearman) | Comparing orderings across weight sets without distributional assumptions. |
| Lipschitz-style stability check | Top-k stability under bounded weight perturbations. |

## Serendipity

- The lower edge of the fee-defect band that produced F1 is not a constant. It
  is `MIN / (1 - rho)`, the cash level at which the smaller leg first clears
  the order floor. Measurement preceded theory.
- F3 and F4 are two independent experiments that point the same way about
  weighting on this basket. The convergence was not designed.
- Reproducibility, framed initially as a compliance posture, became a
  scientific instrument: every figure in the paper exists because a pure
  function let us sweep its inputs exhaustively.

## Hypotheses to Test Next

1. A fee-aware planner reduces implementation cost versus naive split policies
   across realistic deposit sizes.
2. Moat/quality selection adds value beyond equal weighting only when evaluated
   point-in-time and out of sample.
3. Candidate screening improves decision quality more than fine-tuning weights
   inside a fixed portfolio.
4. Provider-health visibility improves reproducibility by making missing data
   states explicit.

## Backlog for Stronger Evidence

1. Free point-in-time SEC fundamentals with conservative filing-date lag.
2. A broad candidate universe with survivorship limitations stated.
3. Baselines: broad market, equal weight, quality factor, moat-like selection,
   and current-weight hold.
4. Ablations: moat, compounding, valuation, concentration caps, rebalance
   interval, and transaction costs.
5. Decision replay bundles: decision id -> frozen inputs -> regenerated output.

## Writing Discipline

- State the problem before the method.
- Use simple math only where it clarifies the mechanism.
- Report negative findings.
- Avoid adjectives that are not measured.
- Do not claim state-of-the-art performance without factor-adjusted and
  out-of-sample evidence.

## How to Add an Entry

1. Run the experiment or test that produced the observation.
2. Add a numbered finding under *Current Findings* with the source paths under
   *Evidence*. Keep the finding to one paragraph.
3. If a finding falsifies an earlier one, add a new finding that states the
   falsification and the source; do not silently revise older entries.
4. Update the paper only when the artifact already supports the claim.
