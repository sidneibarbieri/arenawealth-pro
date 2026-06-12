# AI-in-Finance Reading Notes

This note tracks recent and award-level AI-in-finance papers as research input.
It is not a submission-target file and it is not part of the runtime artifact.
The runtime artifact remains target-neutral.

## What the strongest papers tend to do

Recent strong papers share a pattern:

1. They do not merely apply a model; they define a measurable financial problem.
2. They build or expose a benchmark, simulator, dataset, or audit protocol.
3. They compare against credible baselines under the same information surface.
4. They report failure modes, not only performance.
5. Their contribution is narrow enough to test, but broad enough to matter.

This is the pattern ArenaWealth should follow. A fee-aware deterministic planner
is useful, but the stronger research object is a benchmark for AI investment
recommendations under replayable inputs and explicit constraints.

## Papers downloaded locally

Open-access PDFs are stored in `paper/bibliography/pdfs/` and are ignored by
Git. The BibTeX source of truth is `paper/references.bib`.

| BibKey | Role for ArenaWealth | Takeaway |
| --- | --- | --- |
| `gu2024spoofability` | Award-level style reference | Defines a focused market-mechanism question, controls a simulator, varies liquidity, and explains why a behavior appears. The paper wins by making a hidden financial risk observable. |
| `lee2024stockrec` | Closest non-LLM stock recommendation comparator | Frames individual stock recommendation around user preferences, diversification, temporal dynamics, and ROI. This directly challenges us to test user-specific constraints rather than only generic quality scores. |
| `spadea2025flarko` | Closest LLM asset-recommendation comparator | Combines LLMs with knowledge graphs and behavior alignment. Our opportunity is a simpler deterministic benchmark that tests whether such systems improve, violate, or merely rationalize decisions. |
| `lee2025bias` | Failure-mode comparator | Shows LLMs have latent investment biases and confirmation bias under evidence conflict. This motivates measuring stability, bias, and policy disagreement before trusting AI advice. |
| `oh2025alpha` | Retail LLM portfolio-construction comparator | Uses public media and LLMs to build portfolios; reports high outperformance but has short-horizon and media-source limitations. Our benchmark can test whether such gains survive replay and stronger baselines. |
| `yang2024finrobot` | Agent-platform comparator | Shows the product direction: LLM agents orchestrate data, reports, and workflows. Our contribution should be the deterministic verification layer around agent outputs. |
| `chawla2025riskadvice` | Risk-profile audit comparator | Measures correctness and consistency across profiles. We can adapt this design to investment recommendations: same scenario, repeated runs, constraint checks, and demographic/portfolio invariance tests. |
| `liu2024financialai` | Survey and taxonomy | Confirms that benchmark construction, deployment constraints, and practical evaluation are central gaps in Financial AI. |

## Recent accepted-paper patterns relevant to us

The 2025 program has a high density of papers on:

- LLM and agent benchmarks: financial QA, research agents, retrieval agents,
  tool-enhanced small models, agentic workflows, and agent-as-judge evaluation.
- Investment/recommendation: LLM-driven portfolio construction, asset
  recommendations, stock recommendations, portfolio optimization, sector
  rotation, and decision-focused covariance/return modeling.
- Trust and auditability: hidden bias in LLMs, positional bias, hallucination,
  ethical judgment, compliance, and bias mitigation.
- Simulation and digital twins: market simulation, RL execution, market making,
  and synthetic financial scenarios.

Serendipity: the program already contains both sides of our planned story:
LLM-based investment advice and concerns about bias, instability, and
faithfulness. ArenaWealth can become the deterministic harness that evaluates
that advice.

## Gap we can credibly target

Existing LLM investment papers often evaluate generated portfolios against
market returns or user-alignment metrics. They usually do not provide all of the
following together:

- a replayable deterministic baseline;
- explicit portfolio constraints and cash-deployment guardrails;
- source snapshots and provider health;
- repeated-run stability under the same scenario;
- constraint-violation accounting;
- comparison against equal-weight, risk-parity, minimum-variance, and
  quality/moat baselines;
- decision logs that can reproduce the final recommendation.

This is the gap ArenaWealth can fill.

## Candidate experiment: AI advice under deterministic audit

Freeze 20 to 50 scenarios:

- portfolio holdings;
- available cash;
- allowed universe;
- constraints, concentration caps, and no-buy/trim rules;
- deterministic recommendation from the policy engine;
- source snapshot and provider-health state.

For each scenario, collect repeated AI-advisor outputs from one or more models.
Then measure:

- validity: number and type of constraint violations;
- stability: pairwise overlap across repeated runs;
- policy agreement: overlap@k and Jaccard with deterministic policy;
- novelty: valid ideas not ranked by the deterministic policy;
- explanation faithfulness: whether the explanation cites facts present in the
  snapshot;
- realized outcome: returns under the same backtest harness, with equal-weight,
  risk-parity, minimum-variance, and quality/moat baselines.

The key question is not "Can an LLM pick stocks?" The stronger question is:

> Under fixed information and constraints, when does AI advice add value beyond
> a deterministic buy-and-hold policy, and when does it introduce instability or
> bias?

Implemented first step: `paper/data/ai_advisor_scenarios.json` freezes three
offline scenarios and `scripts/run_ai_advisor_audit.py` evaluates deterministic
outputs plus synthetic failure-mode controls. The reference output is
`paper/data/ai_advisor_audit_reference.json`. This is not yet a model study; it
is the measurement surface for future model outputs.

Serendipity: one synthetic baseline has top-k agreement 1.0 with the policy and
stability 1.0, but is still invalid because it splits sub-tranche cash and pays
an unnecessary fee. This shows why an AI-advisor benchmark cannot rely only on
recommendation overlap.

## Implications for the paper

The current fee paper should not be discarded. It becomes an internal case study
showing why determinism matters: a reproducible sweep caught a real defect. But
the main paper should move toward:

- benchmark construction;
- trustworthy AI advice;
- deterministic replay;
- constrained investment recommendations;
- moat/quality/compounding as the economic domain;
- failure analysis of LLM advice.

That framing is closer to the current state of AI-in-finance research and more
likely to produce a memorable contribution.
