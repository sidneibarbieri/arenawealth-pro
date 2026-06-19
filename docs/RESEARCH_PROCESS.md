# Research Process

This project treats the software artifact as an instrument for producing
scientific evidence. The artifact does not generate the paper. It produces
replayable observations that can later be inspected, challenged, and reported.

## Claim Lifecycle

Every scientific claim should pass through this sequence:

1. Observation: a behavior appears in code, data, paper review, or product use.
2. Measurement: a script, test, or frozen snapshot reproduces the behavior.
3. Finding: the observation becomes a numbered entry in `docs/SCIENTIFIC_LEDGER.md`.
4. Evidence link: the entry names the exact code, data, figure, test, or command.
5. Paper claim: the manuscript reports only what the artifact already supports.
6. Limitation: the manuscript states what the evidence does not prove.

If a step is missing, the statement stays as a hypothesis or backlog item.

## Vocabulary

Insight: a compact explanation that clarifies why a result matters.

Serendipity: an unplanned observation that changes the research direction.
Example: the equal-weight and risk-parity baselines outperforming the tuned
fundamentals weighting on the tested basket.

Finding: an observation supported by executable evidence. Findings are numbered
in the scientific ledger.

Takeaway: the practical consequence of a finding for research, product, or
reviewer experience.

Hypothesis: a plausible statement that still needs a test.

Computation-theory strategy: a formal device that makes a financial decision
auditable, such as subadditivity, fixed points, deterministic replay,
constraint verification, rank correlation, or bounded perturbation analysis.

## Current Research Spine

The strongest current framing is not that the artifact beats the market. The
evidence does not support that claim. The stronger claim is:

AI investment advice should be treated as a candidate-generation problem, and a
deterministic portfolio layer should verify whether each candidate is executable,
fee-aware, stable, and portfolio-valid under frozen inputs.

This framing converts vague investment advice into a replayable verification
problem:

- The AI or screener proposes candidate actions.
- The artifact freezes facts, portfolio state, fees, constraints, and source
  health.
- The deterministic layer rejects actions that violate ownership, cash, fee,
  concentration, or portfolio-fit constraints.
- Experiments measure validity, agreement, stability, and performance
  separately.

## Why the Portfolio-Fit Layer Matters

A high-scoring asset can still be a bad addition to a specific portfolio. It may
increase concentration, reinforce an already crowded theme, consume cash
inefficiently, or mismatch the investor profile. The portfolio layer therefore
asks a different question from the screener:

Does this candidate improve the portfolio as a whole?

This distinction is now part of the artifact through the portfolio-fit review
layer and is tracked as Finding F13 in the ledger. The controlled portfolio-fit
experiment keeps this claim bounded: it shows one reproducible disagreement
between isolated quality rank and portfolio-valid rank, not a general
performance claim.

## Writing Discipline

The paper should be deep without becoming ornate. Use formalism only when it
creates a checkable obligation or removes ambiguity. Avoid adjectives that are
not measured. Prefer short claims tied to commands, files, tables, or figures.

Figures should be kept only when they communicate a pattern more efficiently
than prose or a table. A figure that repeats a table should be removed.

Negative findings are valuable when they narrow the claim honestly. The current
evidence that equal-weight and risk-parity baselines outperform the tuned
fundamentals weighting is not a weakness; it prevents an unsupported performance
claim and pushes the contribution toward auditability.

## Reviewer Contract

A reviewer should be able to answer these questions without private context:

- What problem does the artifact make measurable?
- Which claims are supported by executable evidence?
- Which data are frozen and hash-checked?
- Which model outputs are real, cached, and provenance-preserved?
- Which results are synthetic controls rather than live model results?
- Which limitations remain open?

Any result that cannot satisfy this contract should not appear as a result in
the paper.
