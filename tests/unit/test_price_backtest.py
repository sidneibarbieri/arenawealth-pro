"""Unit tests for price-history backtest helpers."""

import pytest

from arenawealth.analytics.price_backtest import align_price_history, run_price_backtest


def test_align_price_history_uses_common_valid_dates():
    aligned = align_price_history(
        {
            "A": {"2024-01-01": 100.0, "2024-01-02": 110.0, "2024-01-03": 121.0},
            "B": {"2024-01-02": 50.0, "2024-01-03": 55.0, "2024-01-04": 60.0},
        }
    )

    assert aligned.dates == ("2024-01-03",)
    assert aligned.returns["A"] == pytest.approx((0.1,))
    assert aligned.returns["B"] == pytest.approx((0.1,))


def test_align_price_history_rejects_missing_overlap():
    with pytest.raises(ValueError, match="share at least two"):
        align_price_history(
            {
                "A": {"2024-01-01": 100.0, "2024-01-02": 110.0},
                "B": {"2024-01-02": 50.0, "2024-01-03": 55.0},
            }
        )


def test_run_price_backtest_compares_strategy_to_benchmark():
    report = run_price_backtest(
        {
            "A": {"2024-01-01": 100.0, "2024-01-02": 110.0, "2024-01-03": 121.0},
            "B": {"2024-01-01": 100.0, "2024-01-02": 100.0, "2024-01-03": 100.0},
            "SPY": {"2024-01-01": 100.0, "2024-01-02": 105.0, "2024-01-03": 110.25},
        },
        {"A": 0.5, "B": 0.5},
        benchmark_ticker="SPY",
        periods_per_year=1,
    )

    assert report.start_date == "2024-01-02"
    assert report.end_date == "2024-01-03"
    assert report.strategy.total_return == pytest.approx(0.105)
    assert report.benchmark.total_return == pytest.approx(0.1025)
    assert report.comparison.excess_total_return == pytest.approx(0.0025)
