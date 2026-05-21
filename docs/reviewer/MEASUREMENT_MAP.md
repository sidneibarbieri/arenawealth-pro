# Measurement Map

This repository borrows the measurement discipline used in the external STICKS
artifact, but not its cybersecurity workload.

| STICKS measurement pattern | ArenaWealth equivalent | Command or file |
| --- | --- | --- |
| Runtime context capture | Lint, tests, source metrics, Git status | `scripts/reviewer_metrics.py` |
| Claim-evidence traceability | Claims mapped to executable evidence | `docs/reviewer/CLAIMS_EVIDENCE_MATRIX.md` |
| Campaign coverage matrix | Portfolio/universe coverage is not implemented yet | Planned |
| Findings summary | Reviewer metrics JSON under `exports/` | `make metrics` |
| Manuscript value sync | Paper macros/tables are not implemented yet | Planned |
| MITRE metadata audit | Not applicable to this investment artifact | `docs/reviewer/MITRE_STICKS_BOUNDARY.md` |

## Current Minimum

The current artifact produces reproducibility evidence for buildability,
deterministic analysis, and app health. It does not yet produce paper-grade
investment performance measurements.

## Next Measurements

- Historical backtest results by regime.
- Baseline comparisons and ablations.
- Portfolio turnover and cash-drag metrics.
- Provider data-quality and missingness tables.
- Recommendation audit logs with input hashes and model version.
