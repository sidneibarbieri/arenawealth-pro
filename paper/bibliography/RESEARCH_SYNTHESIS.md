# Research Synthesis: Deterministic Audit of AI Investment Advice

This note records scientific hypotheses and design insights extracted from the
local bibliography. It is a research ledger, not a paper draft. Claims should
enter the manuscript only after the artifact produces supporting evidence.

## Current Bibliography State

- `paper/bibliography/sources.json` tracks the bibliography source of truth.
- `paper/bibliography/PDF_INDEX.json` records local PDF hashes.
- `paper/bibliography/_order.txt` lists the remaining manual download.
- Current coverage: 34 local PDFs out of 35 tracked papers.

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
- `hu2025fintrust`
- `qian2026ama`
- `li2026finsaber`
- `gu2024spoofability`

### I5. Stronger LLM-finance benchmarks separate trust, regime, and deployment

The newly indexed EMNLP, WWW, and KDD papers sharpen the gap. `hu2025fintrust`
shows that finance LLMs need multi-axis trustworthiness evaluation, not only
task accuracy. `qian2026ama` moves LLM-agent evaluation toward live verified
streams and shows that agent architecture can matter more than model backbone.
`li2026finsaber` finds that apparent LLM investing advantages weaken under
longer horizons, broader universes, and regime analysis.

Computation-theory angle: the audit should be an interpreter for candidate
recommendation programs under a frozen information surface. Validity,
stability, agreement, grounding, and regime-aware outcome can be measured as
separate properties of the same candidate output.

Supporting papers:

- `hu2025fintrust`
- `qian2026ama`
- `li2026finsaber`
- `benhenda2026lookahead`

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

Current local status: the Azure pilot has been collected and frozen under
`paper/data/advisor_runs/azure/chat/`. Those JSON files include prompts, raw
responses, usage metadata, prompt hashes, and collection timestamps, and are now
listed in `paper/data/DATA_HASHES.txt`.

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
2. Add temporal-contamination controls inspired by point-in-time benchmark
   work: scenario facts must be dated, frozen, and unavailable facts must be
   rejected by the grounding checker.
3. Expand to 20 scenarios before making any paper-level claim about real LLMs.
4. Use price/backtest outcomes only after validity filtering, not as the first
   metric.

## Runtime verification and governance for LLM actions (SOTA positioning)

Studied in full (2026-06): the true intellectual home of this work is runtime
verification and neuro-symbolic governance of LLM-generated actions, not only
AI-for-finance. Four anchors:

- **AgentSpec** (Wang, Poskitt, Sun; ICSE 2026; arXiv:2503.18666). A DSL for
  runtime enforcement: rules are `trigger + check(predicate) + enforce`, hooked
  pre-execution. Its motivating example is a financial transfer. Closest mechanism
  to our typed contract.
- **VeriGuard** (Miculicich et al., Google; arXiv:2510.05156). Offline-synthesised,
  formally-verified policy plus an online monitor that validates each action before
  execution. Mirrors our verified-contract + per-action check.
- **Formal Methods Meet LLMs / TRAC** (Alamdari, Klassen, McIlraith; FAccT 2026;
  arXiv:2605.16198). LTL trajectory monitoring; the key result that small or
  deterministic labelers match or exceed frontier LLM judges directly supports our
  rejection of LLM-as-judge.
- **ProbGuard** (Wang, Poskitt, Wei, Sun; arXiv:2508.00500). Probabilistic,
  predictive monitoring via a DTMC with PAC-style guarantees.

**Our delta vs all four (the unquestionable contribution):** (1) executable
*financial* actions under an economic admissibility contract referenced to declared
quantities (subadditive tranche fee, economic floor, concentration), not generic
safety rules; (2) the empirical benchmark result that *agreement can be high while
validity is low* (0.42 agreement-only false-positive rate), which none of them
report; (3) the *arithmetic-not-judgment* localization with the bare/policy/scaffold
arms (validity 0.58 -> 0.93 when the fee arithmetic is pre-computed); (4) a fully
deterministic, replayable verifier (no LLM labeler as in TRAC, no probabilistic
prediction as in ProbGuard, no LLM-synthesised code as in VeriGuard). Position the
paper as the action-level, deterministic, financial instance of this lineage.
