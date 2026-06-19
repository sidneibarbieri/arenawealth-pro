# Product Strategy

ArenaWealth should remain a deterministic decision-support system. It should
not present one universal portfolio as suitable for every investor.

## Primary Mode

The primary product mode is a personal portfolio workbench:

- import or enter holdings;
- refresh prices and fundamentals;
- inspect quality, valuation, concentration, and candidate screens;
- receive proposed orders without placing them automatically;
- replay past snapshots to explain prior recommendations.

This mode is the best fit for both the current artifact and a publishable
research story because it ties every recommendation to observable inputs and
reproducible rules.

## Advisor Mode

Advisor mode should manage multiple portfolios, not merge them into one global
portfolio. Determinism is preserved when each run is defined by:

1. the portfolio input;
2. the data snapshot;
3. the policy version;
4. the cash or rebalance instruction.

The same policy can therefore produce different recommendations for different
clients without becoming discretionary or random. The open product work is data
isolation, authentication, audit logs, client suitability, and regulatory review.

## Institutional Mode

Institutional mode should be a model-portfolio and research-policy workspace. It
can publish deterministic portfolios for a stated mandate, such as quality
compounders under concentration limits, but it should not be framed as the
single best portfolio for all users.

## Fee Capture

Manual trades must capture the actual operation fee. The default should be
zero, because fee-free and promotional orders are common, while non-zero fees
should be entered explicitly. The deterministic deployment engine may still use
a policy fee schedule for planning, but recorded trades should reflect what the
broker charged.

## Derivatives Scope

Covered calls, protective puts, and collars may be useful for long-term holders,
but they should not be merged into the equity cash-deployment engine. Options
change the decision model: validity depends on option-chain snapshots,
bid-ask spread, expiry window, delta exposure, assignment risk, and nonlinear
payoff. The right product path is a separate derivatives layer after the
long-only equity audit benchmark is stable.

## Reviewer Stories

- As a reviewer, I can run the offline demo and reproduce a recommendation
  without credentials.
- As a reviewer, I can run the current-basket price backtest and inspect the
  limitations before reading performance claims.
- As a holder, I can load my own portfolio, refresh market data, and see why the
  system proposes additions, upgrades, or trims.
- As an advisor, I can keep client portfolios separate while applying the same
  deterministic policy.
- As a researcher, I can replay snapshots and extend the method with patent,
  macro, or factor baselines without changing the user workflow.
- As a holder, I can record the actual fee paid for a buy or sell, including
  fee-free promotional orders.

## Branding Direction

The strongest brand direction is the austere Arena wordmark with a restrained
`A` mark. Blue and gold can be used sparingly as signal colors for focus and
protection, but the reviewer artifact should avoid glossy backgrounds and
decorative brand boards. Binary brand assets stay outside the executable
artifact until selected for production use.
