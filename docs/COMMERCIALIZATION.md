# Commercialization Notes

ArenaWealth Pro can be developed as commercial software, but it should not be
marketed as personalized investment advice until the legal and compliance model
is resolved.

## Minimum Work Before Sale

- Define whether the product is education, analytics, model portfolio software,
  or regulated advisory activity.
- Review broker-dealer and investment-adviser obligations in each target market.
- Confirm data-provider licenses allow commercial redistribution or display.
- Add audit logs for recommendations, inputs, provider responses, and model version.
- Add user suitability, risk tolerance, and disclosure workflows if advice is personalized.
- Add production security controls for API keys and portfolio data.
- Add backtests, benchmark comparisons, and ablation studies before making performance claims.

## Claims Policy

Do not claim that the system beats the state of the art, wins awards, or produces
superior returns unless those statements are supported by reproducible evidence.

Acceptable current claim:

> ArenaWealth Pro provides deterministic portfolio analytics that combine moat,
> compounding, valuation, concentration, and fee-aware cash deployment rules.

## Current Commercial Demo

```bash
uvicorn arenawealth.api.main:app --host 127.0.0.1 --port 8000
cd frontend && npm run dev
```

Open `http://127.0.0.1:5173`.
