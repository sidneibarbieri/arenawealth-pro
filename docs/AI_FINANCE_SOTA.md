# AI-in-Finance State-of-the-Art Map

This document tracks the research position of the artifact. It is not a paper
generator and it is not a submission-specific document. The paper should consume
results from the artifact and from this map only after experiments support them.

## Current Scientific Direction

The fee-optimization result is correct and useful, but it is too narrow to be
the winning scientific story by itself. The stronger direction is:

> A deterministic, replayable buy-and-hold recommendation benchmark for
> trustworthy AI-in-finance systems.

The artifact should become the transparent baseline that AI advisors, LLM
agents, and robo-advisory workflows must beat or faithfully augment. This keeps
the system aligned with AI-in-finance while preserving the core strength:
determinism, auditability, reproducibility, and clear limitations.

## Literature Threads

### 1. Financial AI platforms and agents

Recent financial-AI work emphasizes foundation models, LLM agents, workflow
automation, and financial task orchestration. Representative works include:

- `liu2024financialai`: survey of Financial AI architectures and open
  challenges.
- `yang2023fingpt`: FinGPT, an open-source financial LLM direction.
- `yang2024finrobot`: FinRobot, an LLM-agent platform for financial analysis.
- `elalami2025mlfinance`: systematic review of ML and deep learning in
  computational finance.

Gap for us: these systems often optimize workflow capability, language
reasoning, or prediction, but they do not provide a simple, replayable
buy-and-hold decision baseline with fixed inputs, constraints, and audit logs.

### 2. AI advice and robo-advisory

The closest application-level papers evaluate whether LLMs can provide risk
profiles, portfolio advice, or asset-selection support:

- `chawla2025riskadvice`: credibility of AI systems for assessing investment
  risk.
- `oehler2024chatgpt`: ChatGPT versus robo-advisors for profile-based advice.
- `ko2024chatgpt`: ChatGPT as a portfolio-management aid.
- `spadea2025flarko`: LLM and knowledge-graph asset recommendation aligned with
  investor behavior.
- `lee2025bias`: latent LLM biases in investment analysis under evidence
  conflict.
- `oh2025alpha`: LLM-driven retail portfolio construction from public financial
  media.

Gap for us: the field lacks a deterministic replay benchmark that can test
whether AI advice is stable, faithful to constraints, and better than a
transparent moat/quality/compounding baseline.

The latest conference reading notes are tracked in
`paper/bibliography/CONFERENCE_SOTA.md`.

### 3. Quality, moat, and compounding

The investment substance of the artifact should be grounded in quality and
competitive-advantage literature:

- `novyMarx2013`: gross profitability premium.
- `asness2019qmj`: Quality Minus Junk.
- `kanuri2016moat`: wide-moat stock performance.
- `otero2025quality`: quality investing combined with economic moat.

Gap for us: current experiments use a single survivor basket. The next
scientific step is to test whether a point-in-time quality/moat/compounding
policy improves over equal-weight, risk-parity, quality-only, and LLM-advisor
baselines across more than one basket.

### 4. Reproducibility and overfitting

The artifact's strongest scientific discipline is not a performance claim; it is
how claims are generated and audited:

- `bailey2014pseudo`: backtest overfitting risk.
- `demiguel2009naive`: the difficulty of beating `1/N` diversification.
- The artifact's deterministic replay tests, fee sweeps, rolling windows, and
  bootstrap checks.

Gap for us: point-in-time selection remains incomplete. Until it exists, the
paper should avoid claims of superior stock selection.

## Candidate Winning Contribution

The best current candidate is not:

- "we beat the market";
- "we beat equal weight";
- "fees are subadditive";
- "an LLM picks stocks."

The best candidate is:

> A reproducible benchmark and workbench for testing whether AI investment
> advisors improve, explain, or distort deterministic buy-and-hold
> moat/quality/compounding decisions.

This can become memorable because it turns AI advice into something falsifiable:
same portfolio, same constraints, same cash, same policy version, same source
snapshot. An AI layer may propose narratives or alternative candidates, but the
artifact verifies whether those suggestions improve the decision without
breaking constraints, changing hidden assumptions, or losing replayability.

## Experiments That Matter Next

1. **Point-in-time quality/moat backtest.**
   Use free filings with filing dates and conservative availability lags. Compare
   against equal-weight, risk-parity, minimum-variance, quality-only, moat-only,
   and current basket baselines.

2. **LLM-advisor benchmark.**
   Use a small, frozen set of investor/portfolio scenarios. Ask an LLM for
   candidate additions or allocation advice. Measure:
   - constraint violations;
   - stability across repeated runs;
   - agreement with deterministic policy;
   - realized performance in the same backtest harness;
   - explanation faithfulness to logged facts.

   Initial offline metric support lives in
   `src/arenawealth/experiments/ai_advisor.py`. Frozen scenario support now
   lives in `paper/data/ai_advisor_scenarios.json`, with the reference audit in
   `paper/data/ai_advisor_audit_reference.json` and
   `paper/figures/ai_advisor_audit.png`. This first version deliberately does
   not call an LLM; it evaluates deterministic-policy outputs and synthetic
   failure-mode controls so model access can be optional and future model runs
   use the same measurement surface.

   First observation: policy agreement is insufficient. A naive split can agree
   with the policy ticker and remain stable while still violating fee
   constraints. Validity, stability, and agreement must therefore be reported
   separately.

3. **Advisor workflow audit.**
   Treat a consultant as a multi-portfolio operator. Test whether the same policy
   remains deterministic per client while allowing separate constraints, cash,
   holdings, and replay bundles.

4. **Free-data readiness.**
   Keep the artifact runnable without paid APIs. Optional keys may improve live
   operation, but reviewer-mode experiments must rely on checked-in snapshots or
   free public data.

## Product Implication

For a product, the AI layer should not own the final decision. The defensible
architecture is:

1. deterministic policy produces the recommendation;
2. AI summarizes evidence, highlights risks, and proposes hypotheses;
3. deterministic checks validate constraints and replayability;
4. the user or advisor accepts, edits, or rejects the action;
5. every decision is logged with source, policy version, inputs, outputs, and
   health state.

This framing supports individual users and consultants without sacrificing
determinism. Multi-portfolio advisor mode is a product/compliance extension, not
a mathematical contradiction.
