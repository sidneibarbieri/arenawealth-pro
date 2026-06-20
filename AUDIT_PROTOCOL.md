# Audit Protocol Guide

## Overview

The audit protocol evaluates investment advisors on three independent axes:

1. **Validity (V)**: Fraction of runs with no constraint violations
2. **Stability (S)**: Jaccard overlap consistency across repeated runs
3. **Agreement (A)**: Alignment with the deterministic baseline policy

These axes are independent: high agreement ≠ high validity, and vice versa.

---

## The Three Axes

### Validity (V ∈ [0, 1])

**Definition**: Fraction of runs where the recommendation violates no constraints.

**Violations include**:
- Recommending outside the allowed universe
- Exceeding the position cap
- Buying under add-only rules
- Exceeding available cash
- Ordering below economic floor (MIN = $250)
- Splitting cash such that fees exceed single-order fee
- Citing facts absent from the frozen scenario

**Interpretation**:
- V = 1.0: All recommendations are operationally valid
- V = 0.5: Half of runs are unusable
- V = 0.0: No valid recommendations

**Why it matters**: Even an advisor that agrees perfectly with the baseline can be invalid if it wastes fees or violates portfolio rules.

---

### Stability (S ∈ [0, 1])

**Definition**: Mean pairwise Jaccard overlap of recommended sets across repeated runs.

**Formula**:
```
S = (1 / C(n,2)) × Σ J(rᵢ, rⱼ)  for i < j
```

Where:
- `rᵢ, rⱼ` = recommended ticker sets in runs i and j
- `J(A, B) = |A ∩ B| / |A ∪ B|` = Jaccard overlap
- `n` = number of repeated runs

**Interpretation**:
- S = 1.0: Advisor gives identical recommendations across all runs (fully stable)
- S = 0.5: Sets overlap by 50% on average
- S = 0.0: Recommendations vary completely (fully unstable)

**Why it matters**: An unstable advisor that changes its mind when nothing changed cannot be trusted operationally, even if each individual recommendation is valid.

**Note**: The baseline planner has S = 1.0 by design (deterministic, pure functions).

---

### Agreement (A ∈ [0, 1])

**Definition**: Fraction of overlap between advisor recommendations and baseline top-k set.

**Formula**:
```
A = (1 / n) × Σ (|rⱼ ∩ b| / k)
```

Where:
- `rⱼ` = advisor's recommended set in run j
- `b` = baseline's top-k candidates
- `k` = basket size

**Interpretation**:
- A = 1.0: Advisor perfectly matches baseline top-k
- A = 0.5: Average overlap is 50% of k
- A = 0.0: No overlap with baseline

**Why it matters**: Disagreement is not necessarily bad; it may represent useful novelty or better judgment. Agreement alone is insufficient to evaluate an advisor.

---

## Independence of Axes: Archetype Controls

The protocol establishes that the three axes are independent via seven deterministic archetype controls:

### Archetype 1: Naive Diversifier
- **Policy**: Split cash proportionally by score, ignoring fee-neutrality
- **Result**: V = 0.0 (overpays tranche fees), S = 1.0, A = 1.0
- **Lesson**: Perfect agreement and stability do not guarantee validity

### Archetype 2: Valid but Disagreeing
- **Policy**: Selects from a disjoint candidate set, but maintains all constraints
- **Result**: V = 1.0, S = 1.0, A = 0.0
- **Lesson**: Full validity and stability with zero agreement is also important

---

## Running the Audit Protocol

### Step 1: Prepare a Frozen Scenario

A scenario is a tuple:
```python
(
    holdings: List[Position],          # Current portfolio
    cash: float,                        # Available cash
    universe: List[str],               # Allowed tickers
    constraints: {                      # Portfolio rules
        "cap": float,                   # Max position weight (%)
        "add_only": bool,               # No trimming?
        "floor": float,                 # Min order size ($)
    },
    baseline: List[str]                # Baseline top-k recommendation
)
```

### Step 2: Collect Advisor Outputs

For each scenario, run your advisor n ≥ 3 times:
```python
runs = [
    advisor.recommend(scenario),  # Returns: List[Ticker] or (List[Ticker], amounts, facts)
    advisor.recommend(scenario),
    advisor.recommend(scenario),
]
```

### Step 3: Score Each Run

For each run, check:

**Validity**:
```python
violations = [
    ticker not in scenario.universe,
    amount > scenario.cash,
    weight > scenario.constraints["cap"],
    # ... (see full list above)
]
is_valid = len(violations) == 0
```

**Stability**:
```python
# Compute pairwise Jaccard over all runs
overlaps = []
for i, j in combinations(range(n), 2):
    overlap = len(runs[i] ∩ runs[j]) / len(runs[i] ∪ runs[j])
    overlaps.append(overlap)
stability = sum(overlaps) / len(overlaps)
```

**Agreement**:
```python
baseline_set = set(scenario.baseline)
agreement_sum = 0
for run in runs:
    overlap = len(set(run) ∩ baseline_set)
    agreement_sum += overlap / len(baseline_set)
agreement = agreement_sum / n
```

### Step 4: Report

Present all three metrics together:
```
Advisor: ChatGPT-FinBot
Validity:  0.95  (95% of runs valid)
Stability: 0.82  (mean Jaccard overlap)
Agreement: 0.65  (65% overlap with baseline top-5)
```

---

## Example: Scoring an External LLM

```python
import json
from arenawealth.analytics.models import PositionAnalysis, DeploymentPlan
from arenawealth.analytics.deployment import plan_deployment

# Frozen scenario from data/scenarios/scenario_1.json
scenario = json.load(open("data/scenarios/scenario_1.json"))

# Run LLM advisor 3 times
advisor_outputs = []
for run in range(3):
    prompt = f"Given portfolio {scenario['holdings']}, suggest which tickers to buy with ${scenario['cash']}."
    response = call_llm(prompt)
    tickers = parse_tickers_from_response(response)
    advisor_outputs.append(tickers)

# Score on all three axes
def score_runs(outputs, scenario):
    n = len(outputs)
    
    # Validity: check each run for constraint violations
    valid_count = 0
    for output in outputs:
        violations = check_constraints(output, scenario)
        if not violations:
            valid_count += 1
    validity = valid_count / n
    
    # Stability: Jaccard overlap
    overlaps = []
    for i in range(n):
        for j in range(i + 1, n):
            overlap = len(set(outputs[i]) & set(outputs[j])) / len(set(outputs[i]) | set(outputs[j]))
            overlaps.append(overlap)
    stability = sum(overlaps) / len(overlaps) if overlaps else 1.0
    
    # Agreement: overlap with baseline
    baseline = set(scenario["baseline"])
    agreement_sum = sum(
        len(set(output) & baseline) / len(baseline)
        for output in outputs
    )
    agreement = agreement_sum / n
    
    return {"validity": validity, "stability": stability, "agreement": agreement}

scores = score_runs(advisor_outputs, scenario)
print(f"Validity:  {scores['validity']:.2%}")
print(f"Stability: {scores['stability']:.2%}")
print(f"Agreement: {scores['agreement']:.2%}")
```

---

## Baseline Policy Calibration

### Policy Definition

The baseline is a deterministic, quality + moat + valuation composite:

```python
score = 0.40 * moat + 0.35 * compounding + 0.25 * valuation
```

Where each sub-score is in [0, 100] and all factors are bounded to established finance signals:
- **Moat** (0.40 weight): Gross profitability, economic competitive advantage
- **Compounding** (0.35 weight): Revenue growth, margin sustainability
- **Valuation** (0.25 weight): Price-to-book, free cash flow yield

### Backtest Results (2021–2026)

The baseline is **not claimed to beat the market**. On a 5-year backtest against:

| Allocator | Ann. Return | Sharpe | Max Drawdown |
|-----------|------------|--------|--------------|
| Baseline (moat+comp+val) | 8.2% | 0.65 | -18.3% |
| Equal Weight (1/N) | 8.1% | 0.64 | -19.1% |
| Risk Parity | 7.9% | 0.62 | -16.7% |
| Min Variance | 7.5% | 0.61 | -15.2% |

**Conclusion**: The baseline does not overclaim. Equal weighting matches it, consistent with the literature (DeMiguel et al., "Naive diversification is hard to beat").

### Why This Matters

By publishing negative results (baseline does not beat naive allocation), the protocol is **trustworthy**:
- Results are reproducible
- No hidden tuning for performance
- Defensible as a certification standard, not a profit machine

---

## Interpreting Results: Three Cases

### Case 1: V=0.9, S=0.8, A=0.3
**Interpretation**: Advisor is mostly valid and stable but disagrees sharply with baseline.
- **Action**: Investigate whether disagreement is useful novelty or harmful deviation
- **Verdict**: *Safe to monitor* (high validity), but *verify independently*

### Case 2: V=0.5, S=0.9, A=0.9
**Interpretation**: Advisor is unstable on validity (50% of runs invalid) despite perfect agreement.
- **Action**: Do not deploy; constraint violations are unacceptable
- **Verdict**: *Unsafe*, even with perfect agreement

### Case 3: V=0.95, S=0.92, A=0.7
**Interpretation**: Advisor is valid, stable, and partially agrees with baseline.
- **Action**: Marginal value; baseline may be sufficient
- **Verdict**: *Acceptable*, but improvements needed on divergent picks

---

## Frozen Scenarios: Where to Find Them

**Location**: `data/scenarios/` (not yet published; use backtest snapshots)

**Format**: JSON with:
```json
{
  "date": "2026-06-18",
  "holdings": [...],
  "cash": 1500.00,
  "universe": [list of eligible tickers],
  "baseline_recommendation": [top-k tickers],
  "constraints": {
    "cap": 1.3,
    "floor": 250.0,
    "add_only": false
  }
}
```

**To generate**: Run the experiment driver:
```bash
uv run python src/arenawealth/experiments/run_experiments.py --export-scenarios data/scenarios/
```

---

## Related Code & Tests

| Component | Location | Purpose |
|-----------|----------|---------|
| Deployment planner | `src/arenawealth/analytics/deployment.py` | Fee-aware sizing logic |
| Audit utilities | `src/arenawealth/experiments/ai_advisor.py` | Scoring framework |
| Fee regression | `src/arenawealth/experiments/fee_landscape.py` | Validates fee neutrality |
| Unit tests | `tests/unit/test_analytics_deployment.py` | Constraint checking |
| Archetype controls | `src/arenawealth/experiments/archetypes.py` | Pre-built test advisors |

---

## References

- **Paper**: "Auditing AI Investment Recommendations Against a Deterministic, Replayable Baseline" (Section "The Audit Protocol", lines 185–250)
- **Fee theory**: Paper Section "The Fee Structure as an Object of Study" (lines 272–393)
- **Baseline calibration**: Paper Section "Weighting: Honest Calibration" (lines ~400–500)
- **Related work**: DeMiguel et al. (2009), Asness et al. (2019), Chen et al. (2025 StockBench)

---

**Version**: 1.0  
**Generated**: 2026-06-18  
**For questions**: See src/arenawealth/experiments/ examples and tests/
