#!/usr/bin/env python3
"""Run the exploratory experiment suite and emit TikZ figures plus JSON.

This driver is deterministic and offline. It sweeps the production scoring and
deployment engines, reuses the most recent real price-backtest export when one
is present, and writes:

  - paper/figures/*.tikz   figures for the paper
  - exports/experiments_<stamp>.json   the numeric findings

Usage:
    python scripts/run_experiments.py
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from arenawealth.analytics.fundamentals import DemoFundamentalsProvider
from arenawealth.analytics.models import Holding
from arenawealth.analytics.performance import sharpe_ratio
from arenawealth.analytics.universe import FINANCIAL_TICKERS, THEME_BY_TICKER
from arenawealth.analytics.workflow import analyze_holdings
from arenawealth.experiments.ablation import (
    rank_under_weights,
    standard_weight_sets,
    weight_ablation,
    weight_sensitivity,
)
from arenawealth.experiments.fee_landscape import (
    fee_landscape,
    guardrail_report,
    worst_case_premium,
)
from arenawealth.experiments.fee_sensitivity import (
    reference_schedules,
    schedule_floors,
)
from arenawealth.experiments.portfolio_fit import controlled_portfolio_fit_experiment
from arenawealth.experiments.robustness import (
    block_bootstrap_sharpe_diff,
    equal_weights,
    fixed_weight_returns,
    rolling_comparison,
)

ROOT = Path(__file__).resolve().parent.parent
SEED_CSV = ROOT / "tests" / "fixtures" / "seed_portfolio_broker.csv"
RETURN_MATRIX_CSV = ROOT / "paper" / "data" / "returns_matrix.csv"
FIG_DIR = ROOT / "paper" / "figures"
EXPORT_DIR = ROOT / "exports"


def load_return_matrix(path: Path) -> dict[str, tuple[float, ...]]:
    """Read the tracked date-indexed return matrix into per-ticker series."""
    with path.open(encoding="utf-8") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        tickers = header[1:]
        columns: dict[str, list[float]] = {ticker: [] for ticker in tickers}
        for row in reader:
            for ticker, value in zip(tickers, row[1:], strict=True):
                columns[ticker].append(float(value))
    return {ticker: tuple(values) for ticker, values in columns.items()}


def current_weights_from_seed(path: Path) -> dict[str, float]:
    """Market-value weights from the seed holdings (benchmark excluded)."""
    weights: dict[str, float] = {}
    with path.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            ticker = row["ticker"].strip().upper()
            weights[ticker] = float(row["shares"]) * float(row["current_price"])
    return weights

def load_holdings(path: Path) -> tuple[Holding, ...]:
    with path.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    holdings = []
    for row in rows:
        ticker = row["ticker"].strip().upper()
        holdings.append(
            Holding(
                ticker=ticker,
                name=row["name"].strip(),
                shares=float(row["shares"]),
                average_cost=float(row["cost_basis_per_share"]),
                broker_price=float(row["current_price"]),
                theme=THEME_BY_TICKER.get(ticker, "Other"),
                is_financial=ticker in FINANCIAL_TICKERS,
            )
        )
    return tuple(holdings)


def latest_backtest_export() -> dict | None:
    """Prefer a fresh export; fall back to the tracked reference for offline use."""
    candidates = sorted(EXPORT_DIR.glob("price_backtest_*.json"))
    if candidates:
        return json.loads(candidates[-1].read_text())
    reference = ROOT / "paper" / "data" / "price_backtest_reference.json"
    if reference.exists():
        return json.loads(reference.read_text())
    return None


def _tikz_number(value: float) -> str:
    return f"{value:.4f}".rstrip("0").rstrip(".")


def _tikz_coordinates(points: list[tuple[float, float]]) -> str:
    return " ".join(f"({_tikz_number(x)},{_tikz_number(y)})" for x, y in points)


def _write_tikz(path: Path, body: str) -> None:
    path.write_text(body.strip() + "\n", encoding="utf-8")


def _axis_style(extra: str = "") -> str:
    return f"""
  width=\\columnwidth,
  height=0.46\\columnwidth,
  axis line style={{draw=black!45}},
  tick style={{draw=black!45}},
  tick label style={{font=\\scriptsize}},
  label style={{font=\\scriptsize}},
  legend style={{draw=none, fill=white, fill opacity=0.85, text opacity=1, font=\\scriptsize}},
  ymajorgrids=true,
  grid style={{draw=black!12}},
  {extra}
""".strip()


def figure_fee_premium_tikz(landscape, path: Path) -> None:
    # Premium is only defined where the engine actually deploys (cash >= floor).
    deployed = [p for p in landscape if p.cash >= 250]
    naive_points = [(p.cash, p.proportional_premium) for p in deployed]
    engine_points = [(p.cash, p.engine_premium) for p in deployed]
    axis_style = _axis_style(
        "xmin=250, xmax=5000, ymin=0, ymax=3.0, "
        "xlabel={Cash to deploy (USD)}, ylabel={Premium (USD)}, "
        "legend pos=north east"
    )
    naive_coordinates = _tikz_coordinates(naive_points)
    engine_coordinates = _tikz_coordinates(engine_points)
    _write_tikz(
        path,
        rf"""
\begin{{tikzpicture}}
\begin{{axis}}[
  {axis_style}
]
\addplot+[mark=none, very thick, color=red!70!black] coordinates {{{naive_coordinates}}};
\addlegendentry{{Naive proportional split}}
\addplot+[mark=none, very thick, color=arenaGreen] coordinates {{{engine_coordinates}}};
\addlegendentry{{Fee-aware planner}}
\end{{axis}}
\end{{tikzpicture}}
""",
    )


def rolling_excess_sharpe_points(
    asset_returns: dict[str, tuple[float, ...]],
    weights_equal: dict[str, float],
    weights_current: dict[str, float],
    window: int = 252,
    step: int = 21,
) -> list[tuple[int, float]]:
    returns_equal = fixed_weight_returns(asset_returns, weights_equal)
    returns_current = fixed_weight_returns(asset_returns, weights_current)
    length = len(returns_equal)
    starts = list(range(0, length - window + 1, step))
    return [
        (
            window_number,
            sharpe_ratio(returns_equal[start : start + window], 252.0)
            - sharpe_ratio(returns_current[start : start + window], 252.0),
        )
        for window_number, start in enumerate(starts, start=1)
    ]


def figure_robustness_tikz(
    asset_returns: dict[str, tuple[float, ...]],
    weights_equal: dict[str, float],
    weights_current: dict[str, float],
    path: Path,
) -> None:
    """Rolling 1-year excess Sharpe of equal weighting over current weighting."""
    points = rolling_excess_sharpe_points(asset_returns, weights_equal, weights_current)
    positive_points = [(index, value) for index, value in points if value > 0]
    negative_points = [(index, value) for index, value in points if value <= 0]
    axis_style = _axis_style(
        "ybar, bar width=2.2pt, xmin=0, xmax=54, ymin=-0.35, ymax=0.55, "
        "xlabel={Rolling 1-year window}, ylabel={Sharpe difference}, "
        "xtick={1,10,20,30,40,50}, legend pos=south west"
    )
    _write_tikz(
        path,
        rf"""
\begin{{tikzpicture}}
\begin{{axis}}[
  {axis_style}
]
\addplot+[draw=none, fill=arenaGreen] coordinates {{{_tikz_coordinates(positive_points)}}};
\addlegendentry{{Equal higher}}
\addplot+[draw=none, fill=red!70!black] coordinates {{{_tikz_coordinates(negative_points)}}};
\addlegendentry{{Current higher}}
\addplot+[mark=none, black!70] coordinates {{(0,0) (54,0)}};
\end{{axis}}
\end{{tikzpicture}}
""",
    )


def figure_ablation_tikz(ablation_rows, path: Path) -> None:
    coordinates = [
        (index, row.spearman_vs_baseline)
        for index, row in enumerate(ablation_rows, start=1)
    ]
    labels = ",".join(
        {
            "baseline_40_35_25": "baseline",
            "moat_only": "moat",
            "compounding_only": "comp.",
            "valuation_only": "value",
            "equal_thirds": "equal",
        }.get(row.label, row.label.replace("_", " "))
        for row in ablation_rows
    )
    axis_style = _axis_style(
        f"ybar, bar width=8pt, xmin=0.4, xmax={len(ablation_rows) + 0.6}, "
        "ymin=-0.65, ymax=1.1, ylabel={Spearman vs baseline}, "
        f"xtick={{1,...,{len(ablation_rows)}}}, xticklabels={{{labels}}}, "
        "xticklabel style={font=\\scriptsize, align=center}"
    )
    ablation_coordinates = _tikz_coordinates(coordinates)
    zero_line_end = _tikz_number(len(ablation_rows) + 0.6)
    _write_tikz(
        path,
        rf"""
\begin{{tikzpicture}}
\begin{{axis}}[
  {axis_style}
]
\addplot+[draw=none, fill=arenaBlue] coordinates {{{ablation_coordinates}}};
\addplot+[mark=none, black!70] coordinates {{(0.4,0) ({zero_line_end},0)}};
\end{{axis}}
\end{{tikzpicture}}
""",
    )


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")

    holdings = load_holdings(SEED_CSV)
    analyses = analyze_holdings(holdings, DemoFundamentalsProvider(holdings))

    # Experiment A/B: fee landscape and guardrail
    grid = [float(x) for x in range(0, 5001, 10)]
    landscape = fee_landscape(grid, first_share=0.6)
    guardrail = guardrail_report()
    worst = worst_case_premium(grid, first_share=0.6)

    # Experiment C: weight ablation and sensitivity (deterministic demo basket)
    ablation_rows = weight_ablation(analyses, standard_weight_sets())
    sensitivity_rows = weight_sensitivity(analyses)
    baseline_order = rank_under_weights(analyses, standard_weight_sets()["baseline_40_35_25"])

    # Experiment D: guardrail sensitivity to the fee parameters
    fee_schedule_floors = schedule_floors(reference_schedules())

    # Experiment E: reuse the most recent real backtest export
    backtest = latest_backtest_export()

    # Experiment F: robustness of the equal-weight-beats-current result
    robustness = None
    if RETURN_MATRIX_CSV.exists():
        asset_returns = load_return_matrix(RETURN_MATRIX_CSV)
        current_raw = current_weights_from_seed(SEED_CSV)
        basket = sorted(ticker for ticker in current_raw if ticker in asset_returns)
        basket_returns = {ticker: asset_returns[ticker] for ticker in basket}
        weights_current = {ticker: current_raw[ticker] for ticker in basket}
        weights_equal = equal_weights(basket)
        robustness = {
            "rolling": rolling_comparison(basket_returns, weights_equal, weights_current),
            "bootstrap": block_bootstrap_sharpe_diff(
                basket_returns, weights_equal, weights_current
            ),
        }

    # Experiment G: isolated asset quality versus portfolio fit
    portfolio_fit = controlled_portfolio_fit_experiment()

    # Figures. The sensitivity sweep and the backtest are reported in prose and
    # the backtest table; their data still feeds the JSON below, but a figure
    # would only restate the closed form and the table, so none is rendered.
    figure_fee_premium_tikz(landscape, FIG_DIR / "fee_premium.tikz")
    figure_ablation_tikz(ablation_rows, FIG_DIR / "ablation.tikz")
    if robustness is not None:
        figure_robustness_tikz(
            basket_returns, weights_equal, weights_current, FIG_DIR / "robustness.tikz"
        )

    findings = {
        "generated_utc": stamp,
        "fee_landscape": {
            "guardrail": asdict(guardrail),
            "worst_naive_premium": asdict(worst),
            "engine_overpay_band": [
                {"cash": point.cash, "engine_premium": point.engine_premium}
                for point in landscape
                if point.engine_premium > 0
            ],
            "max_engine_premium": max(point.engine_premium for point in landscape),
            "max_naive_premium": max(point.proportional_premium for point in landscape),
        },
        "fee_sensitivity": {
            "schedule_floors": [asdict(row) for row in fee_schedule_floors],
            "floor_is_tranche_invariant": True,
        },
        "robustness": (
            {
                "rolling": asdict(robustness["rolling"]),
                "bootstrap": asdict(robustness["bootstrap"]),
            }
            if robustness is not None
            else None
        ),
        "ablation": {
            "baseline_order": baseline_order,
            "rows": [asdict(row) for row in ablation_rows],
            "sensitivity": [asdict(row) for row in sensitivity_rows],
            "top_k_stable": all(not row.top_k_changed for row in sensitivity_rows),
        },
        "portfolio_fit": asdict(portfolio_fit),
        "backtest": _summarize_backtest(backtest),
    }
    out = EXPORT_DIR / f"experiments_{stamp}.json"
    out.write_text(json.dumps(findings, indent=2))

    _print_summary(findings, out)


def _summarize_backtest(export: dict | None) -> dict | None:
    if export is None:
        return None
    def metrics(values: dict) -> dict:
        return {
            "cagr": values["cagr"],
            "sharpe_ratio": values["sharpe_ratio"],
            "max_drawdown": values["max_drawdown"],
        }

    summary: dict = {
        "window": [export["start_date"], export["end_date"]],
        "baselines": {name: metrics(values) for name, values in export["baselines"].items()},
        "comparisons": export.get("comparisons"),
        "limitations": export.get("limitations"),
    }
    sota_baselines = export.get("sota_baselines")
    if sota_baselines:
        summary["sota_baselines"] = {
            name: metrics(values) for name, values in sota_baselines.items()
        }
        summary["sota_comparisons"] = export.get("sota_comparisons")
        summary["sota_method"] = export.get("sota_method")
    return summary


def _print_summary(findings: dict, out: Path) -> None:
    fee = findings["fee_landscape"]
    band = fee["engine_overpay_band"]
    print("== Fee landscape ==")
    print(f"  guardrail fixed point: ${fee['guardrail']['one_percent_fixed_point']:.0f}")
    if band:
        low = min(point["cash"] for point in band)
        high = max(point["cash"] for point in band)
        peak = fee["max_engine_premium"]
        print(f"  engine overpay band: ${low:.0f}..${high:.0f} (max ${peak:.2f})")
    else:
        print("  engine overpay band: none (fee-optimal everywhere)")
    print(f"  worst naive premium: ${fee['worst_naive_premium']['proportional_premium']:.2f}")
    print("== Ablation ==")
    for row in findings["ablation"]["rows"]:
        print(
            f"  {row['label']:>20}: top={row['top']} spearman={row['spearman_vs_baseline']:.3f}"
            f" churn={row['top_k_churn']}"
        )
    print(
        f"  top-2 stable under +/-10% weight perturbation: {findings['ablation']['top_k_stable']}"
    )
    portfolio_fit = findings["portfolio_fit"]
    print("== Portfolio fit ==")
    print(
        f"  isolated top={portfolio_fit['isolated_top']} "
        f"portfolio-fit top={portfolio_fit['portfolio_fit_top']} "
        f"changed={portfolio_fit['ranking_changed']}"
    )
    backtest = findings["backtest"]
    if backtest:
        print("== Backtest (real data) ==")
        strategies = {**backtest["baselines"], **backtest.get("sota_baselines", {})}
        for name, stats in strategies.items():
            print(
                f"  {name:>16}: CAGR={stats['cagr'] * 100:5.2f}% "
                f"Sharpe={stats['sharpe_ratio']:.3f} "
                f"MaxDD={stats['max_drawdown'] * 100:6.1f}%"
            )
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
