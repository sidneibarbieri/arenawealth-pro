# Architecture

ArenaWealth is organized around explicit boundaries:

- `arenawealth.domain`: immutable value objects for money, positions, and portfolios.
- `arenawealth.importers`: CSV ingestion and normalization.
- `arenawealth.providers`: market data provider contracts and adapters.
- `arenawealth.analytics`: pure moat, compounding, valuation, and deployment logic.
- `arenawealth.models` and `arenawealth.repositories`: SQLModel persistence.
- `arenawealth.services`: application service orchestration.
- `arenawealth.api`: FastAPI routes and DTOs.

The analytics package keeps network access at the provider boundary. Scoring and
deployment functions accept DTOs and return DTOs, which makes the core logic
deterministic and testable without API keys.
