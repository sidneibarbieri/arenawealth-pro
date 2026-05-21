# Compounding Logic

The compounding score uses revenue growth, EPS growth, free cash flow growth,
and share count change. Buybacks improve the score when shares outstanding fall;
dilution reduces it.

The logic is implemented as pure functions in `arenawealth.analytics.scoring`:

- `compound_annual_growth_rate`
- `shares_change`
- `compounding_classification`
- `compounding_points`

Pure functions are tested directly in `tests/unit/test_analytics_scoring.py`.
