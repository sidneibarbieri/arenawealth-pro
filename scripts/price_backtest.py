"""Run a free price-history backtest for the current basket versus a benchmark."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yfinance

from arenawealth.analytics import PriceBacktestReport, run_price_backtest

DEFAULT_HOLDINGS = Path("data/carteira_atual.csv")
DEFAULT_FIXTURE = Path("tests/fixtures/seed_portfolio_avenue.csv")
DEFAULT_OUTPUT_DIR = Path("exports")


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
    data = yfinance.download(
        tickers,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False,
        group_by="column",
        threads=True,
    )
    if data.empty:
        raise ValueError("Yahoo Finance returned no historical prices")

    close_data = data.get("Close", data)
    if len(tickers) == 1:
        close_data = close_data.to_frame(name=tickers[0])

    histories: dict[str, dict[str, float]] = {}
    for ticker in tickers:
        series = close_data[ticker].dropna()
        histories[ticker] = {
            index.strftime("%Y-%m-%d"): float(value)
            for index, value in series.items()
            if value > 0
        }
    return histories


def report_to_payload(report: PriceBacktestReport, generated_utc: str) -> dict[str, Any]:
    return {
        "generated_utc": generated_utc,
        "start_date": report.start_date,
        "end_date": report.end_date,
        "tickers": list(report.tickers),
        "benchmark_ticker": report.benchmark_ticker,
        "strategy": {
            "periods": report.strategy.periods,
            "rebalances": report.strategy.rebalances,
            "total_return": report.strategy.total_return,
            "cagr": report.strategy.cagr,
            "annualized_volatility": report.strategy.annualized_volatility,
            "sharpe_ratio": report.strategy.sharpe_ratio,
            "max_drawdown": report.strategy.max_drawdown,
            "total_cost": report.strategy.total_cost,
        },
        "benchmark": {
            "total_return": report.benchmark.total_return,
            "cagr": report.benchmark.cagr,
            "annualized_volatility": report.benchmark.annualized_volatility,
            "sharpe_ratio": report.benchmark.sharpe_ratio,
            "max_drawdown": report.benchmark.max_drawdown,
        },
        "comparison": {
            "excess_total_return": report.comparison.excess_total_return,
            "excess_cagr": report.comparison.excess_cagr,
            "sharpe_delta": report.comparison.sharpe_delta,
            "max_drawdown_delta": report.comparison.max_drawdown_delta,
        },
        "limitations": [
            "Current-basket backtest; not a point-in-time stock-selection backtest.",
            "Uses free Yahoo Finance adjusted closes.",
            "Survivorship and selection bias are not eliminated.",
        ],
    }


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
    parser.add_argument("--rebalance-every", type=int, default=0)
    parser.add_argument("--cost-rate", type=float, default=0.0)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    weights = load_target_weights(arguments.holdings)
    tickers = sorted({*weights, arguments.benchmark.upper()})
    histories = fetch_close_history(tickers, arguments.start, arguments.end)
    report = run_price_backtest(
        histories,
        weights,
        benchmark_ticker=arguments.benchmark.upper(),
        rebalance_every=arguments.rebalance_every,
        cost_rate=arguments.cost_rate,
    )
    generated_utc = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    payload = report_to_payload(report, generated_utc)
    output_path = write_payload(payload, arguments.output_dir)
    print(
        "Price backtest "
        f"{report.start_date}..{report.end_date} "
        f"strategy={report.strategy.total_return:.2%} "
        f"benchmark={report.benchmark.total_return:.2%} "
        f"excess={report.comparison.excess_total_return:.2%}"
    )
    print(f"Output {output_path}")


if __name__ == "__main__":
    main()
