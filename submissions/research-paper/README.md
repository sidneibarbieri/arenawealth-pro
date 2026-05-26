# ACM ICAIF Submission Packet

This folder tracks the paper-oriented path. It is not part of the runtime
artifact and should contain only submission preparation material.

## Target

ACM ICAIF 2026 is the best fit for the research paper because it is a
peer-reviewed venue focused on AI, machine learning, and finance.

## Current Public Requirements

- Paper deadline: August 2, 2026, Anywhere on Earth.
- Conference: Milan, November 14-17, 2026.
- Format: ACM `sigconf`.
- Length: 8 pages total in two-column format, including figures and references.
- Submission: PDF through CMT.
- Supplementary material: not accepted; the paper must be self-contained.

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

## Sources

- ICAIF 2026 call for papers: https://icaif2026.org/call-for-papers.html
- ICAIF 2025 awards: https://icaif25.org/awards/
