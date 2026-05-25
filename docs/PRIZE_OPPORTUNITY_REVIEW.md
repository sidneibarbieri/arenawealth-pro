# Prize Opportunity Review

This review applies the reusable Codex skills exported in `codex-skills/`.

## Current Position

The strongest current asset is not investment performance. It is trust:
portfolio source provenance, free-data readiness, deterministic guardrails,
decision logs, and a reviewer-friendly run path. That is a strong fit for a
FinTech product pitch and a credible foundation for a research paper.

## Highest-Value Deltas

### 1. Public Demo Proof Pack

Why it matters: product judges need to see that the app works without waiting
for a local setup.

Deliverables:

- short walkthrough video;
- hosted or downloadable demo page;
- dated validation memo with `make verify`, screenshots, provider health, and
  command outputs;
- fallback screenshots for no-internet demos.

Status: screenshots and deck exist; video and validation memo are still missing.

### 2. Business Model One-Pager

Why it matters: FinTech competitions score the path to revenue.

Deliverables:

- customer segment: self-directed international equity holders first;
- expansion: advisor workspace after compliance and data isolation;
- pricing hypothesis: individual subscription, advisor seat, or research lab
  license;
- compliance boundary: decision-support until licensing is resolved.

Status: partial in pitch outline; needs one concise standalone page.

### 3. Free Point-in-Time Backtest

Why it matters: this is the main scientific delta for a paper. The product can
win trust now; the paper needs empirical evidence.

Deliverables:

- SEC filing-date fundamentals with conservative availability lag;
- price-history baseline;
- equal-weight and current-weight baselines;
- moat, compounding, valuation, concentration, and rebalance ablations;
- limitations on survivorship and ADR coverage stated plainly.

Status: price baseline path exists; full selection backtest remains the largest
research gap.

### 4. Replay Bundle per Decision

Why it matters: decision logs are useful; replay bundles make them stronger.

Deliverables:

- export a decision id into a JSON bundle;
- include portfolio source, provider mode, policy version, inputs, outputs, and
  provider health summary;
- add a replay command that regenerates the recommendation from the bundle.

Status: decision log exists; export/replay by decision id is the next audit
upgrade.

### 5. Multi-Portfolio Boundary for Advisor Mode

Why it matters: advisor use is commercially attractive but regulated.

Deliverables:

- local portfolio switcher;
- per-portfolio source, decision log, and settings;
- no authentication claims until auth and data isolation are real;
- compliance note that multi-client use requires legal review.

Status: repository layer supports multiple portfolios; UI workflow is not built.

## Recommended Sequence

1. Build the public demo proof pack.
2. Add one-page business model and pricing hypothesis.
3. Add decision replay bundle export.
4. Implement free point-in-time selection backtest.
5. Add advisor-mode portfolio switcher after replay is stable.

This order favors prize readiness first while preserving the research path.

