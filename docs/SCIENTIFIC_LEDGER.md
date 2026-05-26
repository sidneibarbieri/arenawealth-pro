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

### F3. Equal weighting is hard to beat on the current basket

The current-basket price study shows equal weight outperforming current weight
over the tested window. This does not prove a general strategy; it is a useful
negative result consistent with the literature on naive diversification.

Evidence:

- `paper/data/price_backtest_reference.json`
- `paper/figures/backtest.png`
- `paper/main.tex`

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
