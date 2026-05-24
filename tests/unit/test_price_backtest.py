"""Unit tests for price-history backtest helpers."""

import pytest

from arenawealth.analytics.price_backtest import (
    align_price_history,
    equal_weights,
    run_price_backtest,
    run_price_backtest_study,
)


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


def test_equal_weights_rejects_empty_universe():
    with pytest.raises(ValueError, match="must not be empty"):
        equal_weights(())


def test_run_price_backtest_study_adds_equal_weight_and_rebalance_ablations():
    study = run_price_backtest_study(
        {
            "A": {
                "2024-01-01": 100.0,
                "2024-01-02": 120.0,
                "2024-01-03": 132.0,
                "2024-01-04": 145.2,
            },
            "B": {
                "2024-01-01": 100.0,
                "2024-01-02": 100.0,
                "2024-01-03": 100.0,
                "2024-01-04": 100.0,
            },
            "SPY": {
                "2024-01-01": 100.0,
                "2024-01-02": 105.0,
                "2024-01-03": 110.25,
                "2024-01-04": 115.7625,
            },
        },
        {"A": 0.8, "B": 0.2},
        benchmark_ticker="SPY",
        periods_per_year=1,
        rebalance_every=1,
        cost_rate=0.001,
    )

    assert study.current_weight.total_return > study.equal_weight.total_return
    assert study.current_vs_equal_weight.excess_total_return > 0
    assert study.current_vs_benchmark.excess_total_return > 0
    assert study.rebalanced_current is not None
    assert study.current_vs_rebalanced is not None
    assert study.rebalanced_current.total_cost > 0
