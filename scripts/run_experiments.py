#!/usr/bin/env python3
"""Run the exploratory experiment suite and emit figures + JSON.

This driver is deterministic and offline. It sweeps the production scoring and
deployment engines, reuses the most recent real price-backtest export when one
is present, and writes:

  - paper/figures/*.png   figures for the paper
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

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from arenawealth.analytics.fundamentals import DemoFundamentalsProvider
from arenawealth.analytics.models import Holding
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

ROOT = Path(__file__).resolve().parent.parent
SEED_CSV = ROOT / "tests" / "fixtures" / "seed_portfolio_avenue.csv"
FIG_DIR = ROOT / "paper" / "figures"
EXPORT_DIR = ROOT / "exports"

# Arena palette
CARBON = "#11161c"
GOLD = "#f5c84c"
BLUE = "#3ba4ff"
SUCCESS = "#00c78a"
MUTED = "#6b6b61"
PAPER = "#f7f6f2"
RED = "#a33a3a"


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


def _style_axes(ax) -> None:
    ax.set_facecolor(PAPER)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(colors=MUTED)
    ax.grid(True, color="#d8d6cd", linewidth=0.5, axis="y")


def figure_fee_premium(landscape, path: Path) -> None:
    # Premium is only defined where the engine actually deploys (cash >= floor).
    deployed = [p for p in landscape if p.cash >= 250]
    cash = [p.cash for p in deployed]
    naive = [p.proportional_premium for p in deployed]
    engine = [p.engine_premium for p in deployed]
    fig, ax = plt.subplots(figsize=(7, 3.6), dpi=150)
    fig.patch.set_facecolor("white")
    ax.plot(cash, naive, color=RED, linewidth=2, label="Naive proportional split")
    ax.plot(cash, engine, color=SUCCESS, linewidth=2, label="Fee-aware planner")
    ax.fill_between(cash, naive, engine, color=GOLD, alpha=0.15)
    ax.set_xlabel("Cash to deploy (USD)")
    ax.set_ylabel("Diversification fee premium (USD)")
    ax.set_title("Subadditive fees penalize naive splitting", color=CARBON, fontweight="bold")
    ax.legend(frameon=False)
    _style_axes(ax)
    fig.tight_layout()
    fig.savefig(path, facecolor="white")
    plt.close(fig)


def figure_guardrail(landscape, fixed_point: float, path: Path) -> None:
    pts = [p for p in landscape if p.cash > 0]
    cash = [p.cash for p in pts]
    fee_pct = [p.engine_fee_pct for p in pts]
    fig, ax = plt.subplots(figsize=(7, 3.6), dpi=150)
    fig.patch.set_facecolor("white")
    ax.plot(cash, fee_pct, color=BLUE, linewidth=2, label="Engine fee as % of cash")
    ax.axhline(1.0, color=RED, linestyle="--", linewidth=1, label="1% tolerance")
    ax.axvline(
        fixed_point,
        color=GOLD,
        linestyle=":",
        linewidth=1.5,
        label=f"Guardrail fixed point ${fixed_point:.0f}",
    )
    ax.set_xlabel("Cash to deploy (USD)")
    ax.set_ylabel("Fee impact (%)")
    ax.set_title("The $250 guardrail is the 1% fee fixed point", color=CARBON, fontweight="bold")
    ax.set_ylim(0, 1.5)
    ax.legend(frameon=False)
    _style_axes(ax)
    fig.tight_layout()
    fig.savefig(path, facecolor="white")
    plt.close(fig)


def figure_ablation(ablation_rows, path: Path) -> None:
    labels = [row.label.replace("_", "\n") for row in ablation_rows]
    spearman = [row.spearman_vs_baseline for row in ablation_rows]
    colors = [GOLD if row.label.startswith("baseline") else BLUE for row in ablation_rows]
    fig, ax = plt.subplots(figsize=(7, 3.6), dpi=150)
    fig.patch.set_facecolor("white")
    bars = ax.bar(labels, spearman, color=colors)
    for bar, row in zip(bars, ablation_rows, strict=True):
        height = bar.get_height()
        offset = 0.03 if height >= 0 else -0.08
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + offset,
            f"churn {row.top_k_churn}",
            ha="center",
            fontsize=8,
            color=MUTED,
        )
    ax.set_ylabel("Spearman rank corr. vs baseline")
    ax.set_title("How each factor reshapes the ranking", color=CARBON, fontweight="bold")
    ax.set_ylim(min(0, min(spearman)) - 0.1, 1.1)
    _style_axes(ax)
    fig.tight_layout()
    fig.savefig(path, facecolor="white")
    plt.close(fig)


def figure_backtest(export: dict, path: Path) -> None:
    baselines = export["baselines"]
    names = list(baselines.keys())
    cagr = [baselines[n]["cagr"] * 100 for n in names]
    sharpe = [baselines[n]["sharpe_ratio"] for n in names]
    palette = {"current_weight": GOLD, "equal_weight": BLUE, "benchmark": MUTED}
    colors = [palette.get(n, CARBON) for n in names]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3.6), dpi=150)
    fig.patch.set_facecolor("white")
    ax1.bar(names, cagr, color=colors)
    ax1.set_title("CAGR (%)", color=CARBON, fontweight="bold")
    ax2.bar(names, sharpe, color=colors)
    ax2.set_title("Sharpe ratio", color=CARBON, fontweight="bold")
    for ax in (ax1, ax2):
        ax.set_xticks(range(len(names)))
        ax.set_xticklabels([n.replace("_", "\n") for n in names], fontsize=8)
        _style_axes(ax)
    fig.suptitle(
        f"Basket vs baselines, {export['start_date']}..{export['end_date']}",
        color=CARBON,
        fontweight="bold",
    )
    fig.tight_layout()
    fig.savefig(path, facecolor="white")
    plt.close(fig)


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

    # Experiment E: reuse the most recent real backtest export
    backtest = latest_backtest_export()

    # Figures
    figure_fee_premium(landscape, FIG_DIR / "fee_premium.png")
    figure_guardrail(landscape, guardrail.one_percent_fixed_point, FIG_DIR / "guardrail.png")
    figure_ablation(ablation_rows, FIG_DIR / "ablation.png")
    if backtest is not None:
        figure_backtest(backtest, FIG_DIR / "backtest.png")

    findings = {
        "generated_utc": stamp,
        "fee_landscape": {
            "guardrail": asdict(guardrail),
            "worst_naive_premium": asdict(worst),
            "engine_overpay_band": [
                {"cash": p.cash, "engine_premium": p.engine_premium}
                for p in landscape
                if p.engine_premium > 0
            ],
            "max_engine_premium": max(p.engine_premium for p in landscape),
            "max_naive_premium": max(p.proportional_premium for p in landscape),
        },
        "ablation": {
            "baseline_order": baseline_order,
            "rows": [asdict(row) for row in ablation_rows],
            "sensitivity": [asdict(row) for row in sensitivity_rows],
            "top_k_stable": all(not row.top_k_changed for row in sensitivity_rows),
        },
        "backtest": _summarize_backtest(backtest),
    }
    out = EXPORT_DIR / f"experiments_{stamp}.json"
    out.write_text(json.dumps(findings, indent=2))

    _print_summary(findings, out)


def _summarize_backtest(export: dict | None) -> dict | None:
    if export is None:
        return None
    return {
        "window": [export["start_date"], export["end_date"]],
        "baselines": {
            name: {
                "cagr": values["cagr"],
                "sharpe_ratio": values["sharpe_ratio"],
                "max_drawdown": values["max_drawdown"],
            }
            for name, values in export["baselines"].items()
        },
        "comparisons": export.get("comparisons"),
        "limitations": export.get("limitations"),
    }


def _print_summary(findings: dict, out: Path) -> None:
    fee = findings["fee_landscape"]
    band = fee["engine_overpay_band"]
    print("== Fee landscape ==")
    print(f"  guardrail fixed point: ${fee['guardrail']['one_percent_fixed_point']:.0f}")
    if band:
        lo = min(p["cash"] for p in band)
        hi = max(p["cash"] for p in band)
        print(
            f"  engine overpay band: ${lo:.0f}..${hi:.0f} (max ${fee['max_engine_premium']:.2f})"
        )
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
    bt = findings["backtest"]
    if bt:
        print("== Backtest (real data) ==")
        for name, v in bt["baselines"].items():
            print(f"  {name:>16}: CAGR={v['cagr'] * 100:5.2f}% Sharpe={v['sharpe_ratio']:.3f}")
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
