# Research Paper Submission Packet

This folder tracks the paper-oriented path. It is not part of the runtime
artifact and should contain only submission preparation material.

## Purpose

This packet records submission preparation separately from the executable
artifact. It may be adapted to a target venue later, but the runtime artifact
must remain venue-neutral.

## Generic Requirements

- Keep the paper short enough to be read in one sitting.
- Keep claims tied to generated tables, figures, or source citations.
- Ensure the paper stands alone without relying on hidden supplementary claims.
- Keep the executable artifact free of venue-specific naming.

## Winning Thesis

Before this work, portfolio tools could generate recommendations, but the
decision path was hard to audit: live data changed, provider failures were
opaque, and historical studies often mixed current knowledge with past dates.
This work makes the recommendation path deterministic, replayable, and explicit
about data limits.

## Evidence That Must Exist Before Submission

- Point-in-time SEC fundamentals mapped into the moat and compounding score.
- Free price-history baselines against SPY and equal-weight holdings.
- Selection backtest over multiple rebalance dates.
- Ablations for moat, compounding, valuation, concentration, and rebalancing.
- Provider health and data-quality reporting.
- One command that regenerates every paper table and figure.

## Current Status

- Free price-history study: implemented through `make price-backtest`.
- Equal-weight and rebalancing ablations: implemented.
- SEC filing-date filter: implemented and unit tested.
- Full point-in-time selection backtest: not implemented yet.
- Factor-adjusted alpha: not implemented yet.
