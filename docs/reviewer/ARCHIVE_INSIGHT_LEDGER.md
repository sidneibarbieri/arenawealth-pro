# Archive Insight Ledger

Historical directories are inspected for recovery, not used for reviewer
execution. Useful ideas are either implemented, documented as backlog, or left
out when they add noise without evidence.

| Idea mined from historical work | Current treatment |
| --- | --- |
| Free-cash-flow yield as a valuation gate | Implemented in analytics scoring where provider data supports it |
| Moat plus compounding instead of price-only ranking | Implemented in the recommendation workflow |
| Theme and concentration caps | Implemented in deployment planning |
| Candidate universe screening | Implemented with a curated free-data universe and deterministic review workflow |
| Additional quality candidates from the old universe database | Salvaged into `CANDIDATE_UNIVERSE` when they fit the moat/compounding policy |
| Multi-portfolio administration | Implemented in the API and database layer; frontend editing remains product backlog |
| Broker CSV import and manual position editing | CSV import is implemented; richer web editing remains product backlog |
| Institutional model portfolio mode | Reframed as a deterministic policy template, not a universal portfolio |
| Behavioral prompts | Reframed as deterministic policy guardrails; emotion classification is not claimed |
| Snapshot and replay discipline | Implemented for reproducible scoring and future backtests |
| Raw provider response capture | Not implemented; useful future audit trail for data-quality studies |
| Patent activity as a moat proxy | Not implemented; requires issuer mapping and PatentsView validation |
| Macro context from FRED | Not implemented; should be added as a separate provider and ablation |
| Claim-evidence tables for reviewers | Added under `docs/reviewer/` |
| Timestamped excellence reports | Archived only; not part of supported evidence |

Only implemented and tested ideas should appear as claims in the paper.
