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

Backtested 2021-01-05 to 2026-06-04 (1360 days), the score-weighted basket beats
SPY (+4.80 pp CAGR, +0.15 Sharpe) and minimum variance on return (+3.8 pp CAGR),
but ranks third of five on Sharpe ratio: equal weight (1.19) and risk parity
(1.18) both beat the tuned weighting (1.10), while minimum variance gives the
shallowest drawdown (-19.2% vs -28.9%) at the cost of return. Two of the
strongest baselines (equal weight, risk parity) use no fundamental data. This is
a useful negative result consistent with the literature on naive diversification;
it clarifies that the contribution is methodological, not performance.

Robustness (F5 method): the equal-weight-beats-current result holds in 47 of 53
rolling one-year windows (89%); a 21-day block bootstrap (2000 resamples, fixed
seed) gives a Sharpe difference of +0.076 with 95% CI [-0.008, +0.168] and
P(equal better)=96%. Direction robust, magnitude not decisive at 5%.

Evidence:

- `src/arenawealth/analytics/allocators.py` (min-variance, risk-parity)
- `tests/unit/test_analytics_allocators.py`
- `paper/data/price_backtest_reference.json` (`sota_baselines`, `sota_comparisons`)
- `paper/main.tex` (performance table)

### F4. Factor weights may be less important than selection

The deterministic ablation shows that equal thirds tracks the tuned baseline
closely while single-factor rankings diverge. This is mechanism evidence only,
because the ablation uses deterministic demo fundamentals.

Evidence:

- `src/arenawealth/experiments/ablation.py`
- `paper/figures/ablation.png`

### F5. The fixed-cost guardrail is the small-cash analogue of the no-trade region

Classical transaction-cost theory shows proportional costs induce a no-trade
region: a band around the target where rebalancing is not worth the cost
(Constantinides 1986; Davis-Norman 1990). Our $250 fixed-cost floor is the same
idea under a quantized fee: below the floor the optimal action is to hold cash.
This connection situates a simple guardrail inside established theory and was the
serendipitous payoff of answering a reviewer's "missing related work" critique.

Evidence:

- `paper/main.tex` (Related Work, thread 2)
- `paper/references.bib` (`constantinides1986capital`, `davis1990portfolio`)

### F6. A competent reviewer misread the ceiling fee as a floor

The fee is correctly defined with a ceiling (per started tranche) in both code
(`math.ceil`) and paper (`\lceil`), and the subadditivity proof is valid. Yet a
reviewer read it as a floor and recommended rejection. Finding: being correct is
not enough; notation that can be misread will be. We added an explicit "ceiling,
not floor" statement, a worked example, and a proof that contrasts the
superadditive floor. Takeaway for the artifact: presentation robustness is a
first-class requirement, not a polish step.

Evidence:

- `paper/main.tex` (Section "The Fee Structure as an Object of Study")
- `src/arenawealth/analytics/deployment.py` (`order_fee`, `math.ceil`)

### F7. The fee result is not the winning scientific story

The fee model is correct, useful, and reviewable, but it is too narrow to carry
the paper alone. The stronger direction is to make the artifact a deterministic,
replayable benchmark for AI investment recommendations. In that framing, the fee
work becomes a demonstration of auditability and guardrail testing, while the
main scientific question becomes whether AI advisors improve, explain, or distort
buy-and-hold moat/quality/compounding decisions under the same frozen inputs and
constraints.

Evidence:

- `docs/AI_FINANCE_SOTA.md`
- `paper/bibliography/CATALOG.md` (Financial AI, robo-advisory, quality/moat
  threads)
- downloaded open-access PDFs in `paper/bibliography/pdfs/` (git-ignored)

### F8. AI should augment the decision workflow, not own the final policy

The state-of-the-art literature on financial LLMs and agents emphasizes workflow
automation, data access, reasoning, and risk profiling. That suggests a more
defensible architecture: deterministic policy produces and validates the
recommendation; AI summarizes evidence, proposes hypotheses, and explains trade
offs; deterministic replay and constraint checks decide whether the AI output is
admissible. This preserves auditability while creating a real AI-in-finance
research question.

Evidence:

- `docs/AI_FINANCE_SOTA.md` (Product Implication)
- `paper/references.bib` (`liu2024financialai`, `yang2024finrobot`,
  `chawla2025riskadvice`, `oehler2024chatgpt`, `ko2024chatgpt`)

### F9. Strong AI-in-finance papers make a hidden failure mode measurable

Recent award-level and accepted papers repeatedly turn a vague concern into a
measurable benchmark: market spoofability under liquidity variation,
behaviorally aligned stock recommendations, LLM investment bias under evidence
conflict, risk-profile consistency, and LLM-driven retail portfolios from public
media. The recurring pattern is not "use a larger model"; it is "define the
financial failure mode, freeze the information surface, compare against
baselines, and expose when the system fails." This pattern supports our pivot:
ArenaWealth should be the deterministic audit harness for AI investment advice.

Evidence:

- `paper/bibliography/AI_FINANCE_READING_NOTES.md`
- downloaded PDFs in `paper/bibliography/pdfs/` (git-ignored)
- `src/arenawealth/experiments/ai_advisor.py`

### F10. Advisor agreement is not enough without operational validity

The offline AI-advisor audit suite evaluates frozen scenarios with synthetic
failure-mode controls. It separates three quantities that are often conflated:
validity under constraints, agreement with the deterministic policy, and
repeated-run stability. The first result is a useful negative control:
`naive_diversifier` reaches policy agreement 1.0 and stability 1.0 in the
sub-tranche cash scenario, but remains invalid because it pays an
unnecessary split fee. Conversely, `valid_but_low_agreement` is fully valid and
stable while disagreeing with the policy. Takeaway: overlap@k cannot certify
investment advice; operational constraints must be measured beside ranking.
This is not yet an LLM result. It is the frozen measurement surface that future
LLM outputs must use. Sharpened: the three axes are \emph{independent}, shown by
two diagonal controls (`naive_diversifier` = agree 1.0 / stable 1.0 / invalid;
`valid_but_low_agreement` = valid / stable / agree 0.0).

Status: this is now the paper's lead contribution. The manuscript was reframed
(commit "Reframe paper around an AI-advisor audit benchmark") so the audit
protocol leads and the fee/guardrail work is repositioned as the reproducible
baseline that makes the protocol trustworthy. Next step: run real LLM advisors
through the same frozen scenarios.

Evidence:

- `paper/main.tex` (Section: The Audit Protocol; Table + figure)
- `paper/data/ai_advisor_scenarios.json`
- `paper/data/ai_advisor_audit_reference.json`
- `paper/figures/ai_advisor_audit.png`
- `scripts/run_ai_advisor_audit.py`
- tests in `tests/unit/test_ai_advisor_benchmark.py`

### F11. Top-finance related work narrows the claim to auditability

Adding anchors from empirical asset pricing, transaction-cost optimization, and
robo-advising clarified the defensible gap. Prior finance work already owns
stock-selection alpha, multi-asset trading with costs, and household
robo-advice outcomes. The project should not claim state-of-the-art investment
performance without factor-adjusted evidence. Its current delta is the
reproducible audit boundary between generated advice and executable portfolio
decisions: frozen inputs, deterministic replay, operational validity, stability,
and agreement reported as separate axes.

Evidence:

- `paper/main.tex` (Related Work)
- `paper/references.bib` (`gu2020machine`, `liu2004transaction`,
  `garleanu2013dynamic`, `dacunto2019robo`)
- `paper/figures/ai_advisor_audit.tikz`

### F12. AI advice can be treated as a candidate program with a deterministic verifier

The manually completed bibliography suggests a stronger computer-science
framing: a language model is not the final investment policy, but a
nondeterministic candidate generator. The artifact supplies the deterministic
contract: frozen facts, allowed universe, portfolio constraints, fee semantics,
and replayable policy output. This converts AI advice into a verification
problem: parse the candidate recommendation, reject non-executable or ungrounded
actions, and only then measure novelty or realized outcome. This is the current
best-paper-grade hypothesis to test with real model runs.

Evidence:

- `paper/bibliography/RESEARCH_SYNTHESIS.md`
- `paper/bibliography/PDF_INDEX.json` (30 local PDFs indexed)
- `paper/bibliography/_order.txt` (only `kanuri2016moat.pdf` remains manual)
- `scripts/collect_advisor_runs.py`

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
- AI-advisor baselines: LLM and robo-advisor recommendations evaluated against
  deterministic, replayable policy outputs.
- Recent AI-in-finance conference papers on recommendation, agent benchmarks,
  bias, market simulation, and LLM-driven portfolio construction.

Reference anchors:

- Novy-Marx (2013), gross profitability premium.
- Asness, Frazzini, and Pedersen (2019), quality-minus-junk.
- DeMiguel, Garlappi, and Uppal (2009), naive `1/N` diversification.
- Gu, Kelly, and Xiu (2020), machine learning asset pricing.
- Liu (2004), multi-asset trading with transaction costs.
- Garleanu and Pedersen (2013), dynamic trading with predictable returns and
  transaction costs.
- D'Acunto, Prabhala, and Rossi (2019), robo-advising benefits and limits.
- Morningstar Wide Moat Focus methodology, as a public moat-plus-valuation
  reference point.
- Financial AI and robo-advisory work tracked in `docs/AI_FINANCE_SOTA.md`.
- AI-in-finance reading notes tracked in `paper/bibliography/AI_FINANCE_READING_NOTES.md`.

Current honest position:

- We do not yet prove investment outperformance over the state of the art.
- We do show a reproducible optimization contribution around fee-aware cash
  deployment.
- We have evidence that the current weighting policy is not superior to equal
  weighting on the tested basket.
- The next scientific delta is a free point-in-time selection backtest plus an
  AI-advisor benchmark against the deterministic policy.

## Computation-Theory Strategies Used

| Strategy | Where it appears |
| --- | --- |
| Subadditive cost analysis | F1; diversification premium $\pi$ in `fee_landscape.py`. |
| Closed-form fixed point | F2; guardrail derivation MIN = c/τ in `deployment.py`. |
| Linear functional ablation | F4; recomposing the composite under alternative weight vectors without re-scoring. |
| Property-based testing across a grid | `test_planner_never_overpays_single_order_fee_across_grid`. |
| Rank correlation (Spearman) | Comparing orderings across weight sets without distributional assumptions. |
| Lipschitz-style stability check | Top-k stability under bounded weight perturbations. |
| Constraint-product audit | F10; a recommendation must satisfy ranking, cash, fee, ownership, and fact constraints together. |

## Serendipity

- The lower edge of the fee-defect band that produced F1 is not a constant. It
  is `MIN / (1 - rho)`, the cash level at which the smaller leg first clears
  the order floor. Measurement preceded theory.
- F3 and F4 are two independent experiments that point the same way about
  weighting on this basket. The convergence was not designed.
- Reproducibility, framed initially as a compliance posture, became a
  scientific instrument: every figure in the paper exists because a pure
  function let us sweep its inputs exhaustively.
- The best-paper pattern from recent AI-in-finance work is not maximum model
  complexity. It is a clean evaluation object plus a failure mode that becomes
  measurable.
- The advisor audit exposed a metric trap: a recommendation can be stable and
  agree with the policy while still being operationally invalid. This gives the
  paper a stronger reason to insist on deterministic constraints rather than
  only comparing top-k recommendations.

## Hypotheses to Test Next

1. A fee-aware planner reduces implementation cost versus naive split policies
   across realistic deposit sizes.
2. Moat/quality selection adds value beyond equal weighting only when evaluated
   point-in-time and out of sample.
3. Candidate screening improves decision quality more than fine-tuning weights
   inside a fixed portfolio.
4. Provider-health visibility improves reproducibility by making missing data
   states explicit.
5. AI-generated recommendations will be less stable and less replayable than the
   deterministic policy unless constrained by a logged policy-and-snapshot
   interface.
6. Option-income overlays can add user value for long-term holders, but they
   require a separate validity model because bid-ask spread, expiry, delta, and
   nonlinear payoff constraints replace the current fixed-fee equity model.

## Backlog for Stronger Evidence

1. Free point-in-time SEC fundamentals with conservative filing-date lag.
2. A broad candidate universe with survivorship limitations stated.
3. Baselines: broad market, equal weight, risk parity, minimum variance, quality
   factor, moat-like selection, and current-weight hold.
4. AI-advisor benchmark: frozen scenarios now exist; next collect repeated
   model outputs, add explanation-faithfulness scoring, and connect valid
   outputs to performance under the same backtest harness.
5. Ablations: moat, compounding, valuation, concentration caps, rebalance
   interval, transaction costs, and AI augmentation.
6. Decision replay bundles: decision id -> frozen inputs -> regenerated output.
7. Optional derivatives layer: covered-call, protective-put, and collar
   scenarios with option-chain snapshots, spread checks, expiry constraints, and
   payoff diagrams. This should be a separate study after the equity audit
   benchmark is stable.

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
