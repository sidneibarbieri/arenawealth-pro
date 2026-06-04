"""Price-history backtest helpers."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from arenawealth.analytics.allocators import (
    min_variance_weights,
    risk_parity_weights,
)
from arenawealth.analytics.backtest import (
    BacktestComparison,
    BacktestResult,
    compare_backtests,
    run_backtest,
)
from arenawealth.analytics.performance import to_returns


@dataclass(frozen=True)
class AlignedReturnSeries:
    dates: tuple[str, ...]
    returns: dict[str, tuple[float, ...]]


@dataclass(frozen=True)
class PriceBacktestReport:
    start_date: str
    end_date: str
    tickers: tuple[str, ...]
    benchmark_ticker: str
    strategy: BacktestResult
    benchmark: BacktestResult
    comparison: BacktestComparison


@dataclass(frozen=True)
class PriceBacktestStudy:
    start_date: str
    end_date: str
    tickers: tuple[str, ...]
    benchmark_ticker: str
    current_weight: BacktestResult
    equal_weight: BacktestResult
    benchmark: BacktestResult
    current_vs_equal_weight: BacktestComparison
    current_vs_benchmark: BacktestComparison
    rebalanced_current: BacktestResult | None = None
    current_vs_rebalanced: BacktestComparison | None = None
    min_variance: BacktestResult | None = None
    risk_parity: BacktestResult | None = None
    current_vs_min_variance: BacktestComparison | None = None
    current_vs_risk_parity: BacktestComparison | None = None
    sota_weights: dict[str, dict[str, float]] | None = None


def align_price_history(price_history: Mapping[str, Mapping[str, float]]) -> AlignedReturnSeries:
    if not price_history:
        raise ValueError("price_history must not be empty")

    common_dates: set[str] | None = None
    for ticker, series in price_history.items():
        if len(series) < 2:
            raise ValueError(f"price history for {ticker} must contain at least two dates")
        ticker_dates = {date for date, price in series.items() if price > 0}
        common_dates = ticker_dates if common_dates is None else common_dates & ticker_dates

    dates = tuple(sorted(common_dates or ()))
    if len(dates) < 2:
        raise ValueError("price histories must share at least two valid dates")

    returns = {
        ticker: to_returns([series[date] for date in dates])
        for ticker, series in price_history.items()
    }
    return AlignedReturnSeries(dates=dates[1:], returns=returns)


def run_price_backtest(
    price_history: Mapping[str, Mapping[str, float]],
    target_weights: Mapping[str, float],
    benchmark_ticker: str,
    periods_per_year: float = 252.0,
    rebalance_every: int = 0,
    cost_rate: float = 0.0,
) -> PriceBacktestReport:
    aligned = align_price_history(price_history)
    tickers = tuple(target_weights)
    strategy = run_backtest(
        aligned.returns,
        target_weights,
        periods_per_year=periods_per_year,
        rebalance_every=rebalance_every,
        cost_rate=cost_rate,
    )
    benchmark = run_backtest(
        aligned.returns,
        {benchmark_ticker: 1.0},
        periods_per_year=periods_per_year,
        rebalance_every=0,
        cost_rate=0.0,
    )
    return PriceBacktestReport(
        start_date=aligned.dates[0],
        end_date=aligned.dates[-1],
        tickers=tickers,
        benchmark_ticker=benchmark_ticker,
        strategy=strategy,
        benchmark=benchmark,
        comparison=compare_backtests(strategy, benchmark),
    )


def equal_weights(tickers: tuple[str, ...]) -> dict[str, float]:
    if not tickers:
        raise ValueError("tickers must not be empty")
    weight = 1.0 / len(tickers)
    return {ticker: weight for ticker in tickers}


def run_price_backtest_study(
    price_history: Mapping[str, Mapping[str, float]],
    target_weights: Mapping[str, float],
    benchmark_ticker: str,
    periods_per_year: float = 252.0,
    rebalance_every: int = 0,
    cost_rate: float = 0.0,
    include_sota_baselines: bool = True,
) -> PriceBacktestStudy:
    aligned = align_price_history(price_history)
    tickers = tuple(target_weights)
    asset_returns = {ticker: aligned.returns[ticker] for ticker in tickers}
    current_weight = run_backtest(
        aligned.returns,
        target_weights,
        periods_per_year=periods_per_year,
        rebalance_every=0,
        cost_rate=0.0,
    )
    equal_weight = run_backtest(
        aligned.returns,
        equal_weights(tickers),
        periods_per_year=periods_per_year,
        rebalance_every=0,
        cost_rate=0.0,
    )
    benchmark = run_backtest(
        aligned.returns,
        {benchmark_ticker: 1.0},
        periods_per_year=periods_per_year,
        rebalance_every=0,
        cost_rate=0.0,
    )
    rebalanced_current = None
    current_vs_rebalanced = None
    if rebalance_every:
        rebalanced_current = run_backtest(
            aligned.returns,
            target_weights,
            periods_per_year=periods_per_year,
            rebalance_every=rebalance_every,
            cost_rate=cost_rate,
        )
        current_vs_rebalanced = compare_backtests(current_weight, rebalanced_current)

    min_variance = None
    risk_parity = None
    current_vs_min_variance = None
    current_vs_risk_parity = None
    sota_weights: dict[str, dict[str, float]] | None = None
    if include_sota_baselines:
        min_variance_targets = min_variance_weights(asset_returns)
        risk_parity_targets = risk_parity_weights(asset_returns)
        min_variance = run_backtest(
            aligned.returns,
            min_variance_targets,
            periods_per_year=periods_per_year,
            rebalance_every=0,
            cost_rate=0.0,
        )
        risk_parity = run_backtest(
            aligned.returns,
            risk_parity_targets,
            periods_per_year=periods_per_year,
            rebalance_every=0,
            cost_rate=0.0,
        )
        current_vs_min_variance = compare_backtests(current_weight, min_variance)
        current_vs_risk_parity = compare_backtests(current_weight, risk_parity)
        sota_weights = {
            "min_variance": min_variance_targets,
            "risk_parity": risk_parity_targets,
        }

    return PriceBacktestStudy(
        start_date=aligned.dates[0],
        end_date=aligned.dates[-1],
        tickers=tickers,
        benchmark_ticker=benchmark_ticker,
        current_weight=current_weight,
        equal_weight=equal_weight,
        benchmark=benchmark,
        current_vs_equal_weight=compare_backtests(current_weight, equal_weight),
        current_vs_benchmark=compare_backtests(current_weight, benchmark),
        rebalanced_current=rebalanced_current,
        current_vs_rebalanced=current_vs_rebalanced,
        min_variance=min_variance,
        risk_parity=risk_parity,
        current_vs_min_variance=current_vs_min_variance,
        current_vs_risk_parity=current_vs_risk_parity,
        sota_weights=sota_weights,
    )
