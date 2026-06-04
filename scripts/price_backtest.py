"""Run a free price-history backtest for the current basket versus a benchmark."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yfinance

from arenawealth.analytics import (
    BacktestComparison,
    BacktestResult,
    PriceBacktestStudy,
    align_price_history,
    run_price_backtest_study,
)

DEFAULT_HOLDINGS = Path("data/carteira_atual.csv")
DEFAULT_FIXTURE = Path("tests/fixtures/seed_portfolio_avenue.csv")
DEFAULT_OUTPUT_DIR = Path("exports")
RETURN_MATRIX_PATH = Path("paper/data/returns_matrix.csv")


def write_return_matrix(
    histories: dict[str, dict[str, float]], path: Path = RETURN_MATRIX_PATH
) -> Path:
    """Persist the aligned daily-return matrix as a date-indexed CSV.

    One row per trading date, one column per ticker. This is the tracked,
    offline input for the robustness experiments, so a reviewer can reproduce
    rolling-window and bootstrap analyses without network access.
    """
    aligned = align_price_history(histories)
    tickers = sorted(aligned.returns)
    path.parent.mkdir(parents=True, exist_ok=True)
    header = "date," + ",".join(tickers)
    lines = [header]
    for index, date in enumerate(aligned.dates):
        cells = [f"{aligned.returns[ticker][index]:.10f}" for ticker in tickers]
        lines.append(date + "," + ",".join(cells))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def holdings_path(path: Path) -> Path:
    if path.exists():
        return path
    if path == DEFAULT_HOLDINGS:
        return DEFAULT_FIXTURE
    raise FileNotFoundError(path)


def load_target_weights(path: Path) -> dict[str, float]:
    with holdings_path(path).open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    market_values = {
        row["ticker"].strip().upper(): float(row["shares"]) * float(row["current_price"])
        for row in rows
    }
    total = sum(market_values.values())
    if total <= 0:
        raise ValueError("holdings market value must be positive")
    return {ticker: value / total for ticker, value in market_values.items()}


def fetch_close_history(
    tickers: list[str], start: str, end: str | None
) -> dict[str, dict[str, float]]:
    histories: dict[str, dict[str, float]] = {}
    for ticker in tickers:
        data = yfinance.download(
            ticker,
            start=start,
            end=end,
            auto_adjust=True,
            progress=False,
        )
        if data.empty:
            raise ValueError(f"Yahoo Finance returned no historical prices for {ticker}")
        close_data = data["Close"]
        series = close_data[ticker] if hasattr(close_data, "columns") else close_data
        series = series.dropna()
        histories[ticker] = {
            index.strftime("%Y-%m-%d"): float(value)
            for index, value in series.items()
            if value > 0
        }
    return histories


def result_to_payload(result: BacktestResult) -> dict[str, Any]:
    return {
        "periods": result.periods,
        "rebalances": result.rebalances,
        "total_return": result.total_return,
        "cagr": result.cagr,
        "annualized_volatility": result.annualized_volatility,
        "sharpe_ratio": result.sharpe_ratio,
        "max_drawdown": result.max_drawdown,
        "total_cost": result.total_cost,
    }


def comparison_to_payload(comparison: BacktestComparison) -> dict[str, Any]:
    return {
        "excess_total_return": comparison.excess_total_return,
        "excess_cagr": comparison.excess_cagr,
        "sharpe_delta": comparison.sharpe_delta,
        "max_drawdown_delta": comparison.max_drawdown_delta,
    }


def study_to_payload(study: PriceBacktestStudy, generated_utc: str) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "generated_utc": generated_utc,
        "start_date": study.start_date,
        "end_date": study.end_date,
        "tickers": list(study.tickers),
        "benchmark_ticker": study.benchmark_ticker,
        "baselines": {
            "current_weight": result_to_payload(study.current_weight),
            "equal_weight": result_to_payload(study.equal_weight),
            "benchmark": result_to_payload(study.benchmark),
        },
        "comparisons": {
            "current_vs_equal_weight": comparison_to_payload(study.current_vs_equal_weight),
            "current_vs_benchmark": comparison_to_payload(study.current_vs_benchmark),
        },
        "limitations": [
            "Current-basket backtest; not a point-in-time stock-selection backtest.",
            "Uses free Yahoo Finance adjusted closes.",
            "Survivorship and selection bias are not eliminated.",
        ],
    }
    if study.rebalanced_current is not None and study.current_vs_rebalanced is not None:
        payload["ablations"] = {
            "rebalanced_current": result_to_payload(study.rebalanced_current),
            "current_vs_rebalanced": comparison_to_payload(study.current_vs_rebalanced),
        }
    if study.min_variance is not None and study.risk_parity is not None:
        payload["sota_baselines"] = {
            "min_variance": result_to_payload(study.min_variance),
            "risk_parity": result_to_payload(study.risk_parity),
        }
        payload["sota_comparisons"] = {
            "current_vs_min_variance": comparison_to_payload(study.current_vs_min_variance),
            "current_vs_risk_parity": comparison_to_payload(study.current_vs_risk_parity),
        }
        if study.sota_weights is not None:
            payload["sota_weights"] = study.sota_weights
    return payload


def report_to_payload(study: PriceBacktestStudy, generated_utc: str) -> dict[str, Any]:
    return study_to_payload(study, generated_utc)


def write_payload(payload: dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"price_backtest_{payload['generated_utc'].replace(':', '')}.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--holdings", type=Path, default=DEFAULT_HOLDINGS)
    parser.add_argument("--benchmark", default="SPY")
    parser.add_argument("--start", default="2021-01-01")
    parser.add_argument("--end", default=None)
    parser.add_argument("--rebalance-every", type=int, default=63)
    parser.add_argument("--cost-rate", type=float, default=0.001)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    weights = load_target_weights(arguments.holdings)
    tickers = sorted({*weights, arguments.benchmark.upper()})
    histories = fetch_close_history(tickers, arguments.start, arguments.end)
    study = run_price_backtest_study(
        histories,
        weights,
        benchmark_ticker=arguments.benchmark.upper(),
        rebalance_every=arguments.rebalance_every,
        cost_rate=arguments.cost_rate,
    )
    generated_utc = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    payload = study_to_payload(study, generated_utc)
    output_path = write_payload(payload, arguments.output_dir)
    matrix_path = write_return_matrix(histories)
    print(f"Return matrix {matrix_path}")
    print(
        "Price backtest study "
        f"{study.start_date}..{study.end_date} "
        f"current={study.current_weight.total_return:.2%} "
        f"equal_weight={study.equal_weight.total_return:.2%} "
        f"benchmark={study.benchmark.total_return:.2%} "
        f"excess_vs_benchmark={study.current_vs_benchmark.excess_total_return:.2%}"
    )
    print(f"Output {output_path}")


if __name__ == "__main__":
    main()
