# Research Synthesis: Deterministic Audit of AI Investment Advice

This note records scientific hypotheses and design insights extracted from the
local bibliography. It is a research ledger, not a paper draft. Claims should
enter the manuscript only after the artifact produces supporting evidence.

## Current Bibliography State

- `paper/bibliography/sources.json` tracks the bibliography source of truth.
- `paper/bibliography/PDF_INDEX.json` records local PDF hashes.
- `paper/bibliography/_order.txt` lists the remaining manual download.
- Current coverage: 30 local PDFs out of 31 tracked papers.

## Main Scientific Opportunity

The strongest contribution is not a claim that the portfolio policy beats the
market. The finance literature already has strong baselines for selection,
estimation, and trading under costs. The sharper contribution is:

> Treat AI investment advice as a nondeterministic candidate generator whose
> outputs must pass a deterministic contract system before they can become
> executable portfolio actions.

This reframes the project as a benchmark and certification problem. A language
model may propose tickers, rationales, and trades; the artifact supplies the
frozen information surface, transaction-cost semantics, constraint checker,
replay log, and deterministic policy baseline.

## Literature-Derived Insights

### I1. Fixed-cost cash deployment is a discrete no-trade region

Transaction-cost theory shows that proportional costs create no-trade regions:
it can be optimal to do nothing when the benefit of rebalancing is below cost.
Our broker fee model is more discrete: a quantized per-tranche fixed fee. The
economic order floor is therefore the small-cash, fixed-cost analogue of a
no-trade boundary.

Computation-theory angle: the planner is a deterministic optimizer over a
piecewise-constant cost function. Fee-aware deployment can be tested with
property-based sweeps because the cost frontier is enumerable.

Supporting papers:

- `constantinides1986capital`
- `davis1990portfolio`
- `liu2004transaction`
- `garleanu2013dynamic`
- `lobo2007portfolio`

### I2. Equal weight is a hard baseline, not a weak strawman

The naive `1/N` literature and our own price backtest point in the same
direction: weighting sophistication often fails to dominate simple allocation
after estimation error and turnover. That makes stock-picking superiority a weak
paper claim unless we add point-in-time selection evidence.

Computation-theory angle: use the deterministic policy as a reference contract,
not as an oracle of alpha. Report when sophisticated scoring is matched or
beaten by a simpler policy.

Supporting papers:

- `demiguel2009naive`
- `bailey2014pseudo`
- `asness2019qmj`
- `gu2020machine`
- `otero2025quality`

### I3. LLM finance papers need operational validity, not only returns

Recent LLM portfolio papers test return, alignment, or diversification. Bias and
product-preference papers show that language-model advice can be unstable or
systematically tilted even when it sounds plausible. Our benchmark separates:

- validity under executable constraints;
- agreement with the deterministic baseline;
- stability across repeated runs;
- grounding in facts available in the frozen scenario.

Computation-theory angle: this is a type system for investment advice. The
model emits a candidate action; the verifier rejects actions that violate the
portfolio contract, cost semantics, or evidence boundary.

Supporting papers:

- `dacunto2019robo`
- `oehler2024chatgpt`
- `ko2024chatgpt`
- `lee2025bias`
- `zhi2025productbias`
- `oh2025alpha`
- `spadea2025flarko`
- `chen2025stockbench`

### I4. The benchmark should be contamination-resistant and replayable

Agent and benchmark papers increasingly worry about contamination, changing
information surfaces, and inconsistent evaluation. The artifact's advantage is
that each scenario is small, frozen, and replayable: portfolio state, allowed
universe, policy output, available fact ids, and provider mode are explicit.

Computation-theory angle: a scenario is an immutable input object; the advisor
output is a candidate program; the audit is a deterministic interpreter.

Supporting papers:

- `saha2025agents`
- `yang2024finrobot`
- `chen2025stockbench`
- `gu2024spoofability`

## Proposed Best-Paper-Grade Experiment

### Research question

Under fixed information and portfolio constraints, when does an AI advisor add
valid novelty beyond a deterministic moat/quality/compounding policy, and when
does it introduce instability, bias, or non-executable trades?

### Design

1. Freeze 20--50 scenarios:
   - existing holdings;
   - cash;
   - allowed universe;
   - provider-health snapshot;
   - facts available to the advisor;
   - deterministic policy output;
   - explicit constraints.
2. Collect repeated model outputs:
   - start with 3 scenarios x 3 runs = 9 calls;
   - cache every prompt, raw response, parsed output, usage, and timestamp;
   - never re-call a cached run.
3. Score each run:
   - validity;
   - agreement;
   - stability;
   - fact-grounding;
   - fee dominance;
   - novelty among valid recommendations.
4. Compare:
   - deterministic policy;
   - synthetic failure-mode controls;
   - one real LLM advisor;
   - simple baselines such as equal-weight and current-hold.
5. Report negative results:
   - if the model is unstable, say so;
   - if it agrees but violates costs, say so;
   - if it adds valid novelty, isolate the scenario and rerun with ablations.

### Minimum proof of concept

The current collector supports the first real model test:

```bash
python scripts/collect_advisor_runs.py --model <azure-deployment> --runs 3 --live --max-calls 10
```

It requires:

- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- optional `AZURE_OPENAI_API_VERSION`

Current local status: the API key is configured, but the endpoint is missing.
No live call was made.

## Serendipities to Track

1. Agreement can be maximized by invalid advice. A naive split can match the
   policy tickers while overpaying fees.
2. Stability can be bad. A model that always makes the same invalid decision is
   stable but unsafe.
3. Novelty can be valid. A recommendation that disagrees with the policy may be
   useful if it stays inside constraints and cites available facts.
4. The best result may be a gate, not a picker. The artifact may be most valuable
   as a deterministic assurance layer around AI advice.

## Current Coverage and Immediate Next Deltas

Already implemented:

- explanation grounding: cited facts must be a subset of `available_fact_ids`;
- fee dominance: an output is invalid when split fees exceed the single-order
  lower bound for the same cash deployment;
- repeated-run stability and policy agreement.

Next:

1. Add scenario perturbations: same facts with reordered prompt, renamed fields,
   and equivalent cash formatting to test invariance.
2. Expand to 20 scenarios before making any paper-level claim about real LLMs.
3. Use price/backtest outcomes only after validity filtering, not as the first
   metric.
