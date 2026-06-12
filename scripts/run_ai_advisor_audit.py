#!/usr/bin/env python3
"""Run the offline AI-advisor audit benchmark.

The benchmark does not call an LLM. It evaluates frozen advisor outputs and
synthetic failure-mode baselines against deterministic constraints so future
model outputs can be compared without changing the measurement surface.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from arenawealth.experiments.ai_advisor import (
    AdvisorRecommendation,
    AdvisorRunSetReport,
    AdvisorScenario,
    evaluate_run_set,
)

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SCENARIOS = ROOT / "paper" / "data" / "ai_advisor_scenarios.json"
REFERENCE_OUTPUT = ROOT / "paper" / "data" / "ai_advisor_audit_reference.json"
FIGURE_OUTPUT = ROOT / "paper" / "figures" / "ai_advisor_audit.png"
TIKZ_OUTPUT = ROOT / "paper" / "figures" / "ai_advisor_audit.tikz"
EXPORT_DIR = ROOT / "exports"

CARBON = "#11161c"
GOLD = "#f5c84c"
BLUE = "#3ba4ff"
SUCCESS = "#00c78a"
MUTED = "#6b6b61"
PAPER = "#f7f6f2"
RED = "#a33a3a"


def load_suite(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def scenario_from_payload(payload: dict[str, Any]) -> AdvisorScenario:
    return AdvisorScenario(
        name=payload["name"],
        cash=float(payload["cash"]),
        allowed_tickers=tuple(payload["allowed_tickers"]),
        owned_tickers=tuple(payload["owned_tickers"]),
        policy_tickers=tuple(payload.get("policy_tickers", ())),
        available_fact_ids=tuple(payload.get("available_fact_ids", ())),
        max_recommendations=int(payload.get("max_recommendations", 3)),
        add_only=bool(payload.get("add_only", True)),
        amounts_required=bool(payload.get("amounts_required", False)),
    )


def recommendation_from_payload(payload: dict[str, Any]) -> AdvisorRecommendation:
    return AdvisorRecommendation(
        run_id=payload["run_id"],
        tickers=tuple(payload["tickers"]),
        amounts=tuple(float(amount) for amount in payload.get("amounts", ())),
        cited_fact_ids=tuple(payload.get("cited_fact_ids", ())),
    )


def evaluate_suite(suite: dict[str, Any]) -> tuple[AdvisorRunSetReport, ...]:
    reports: list[AdvisorRunSetReport] = []
    for scenario_payload in suite["scenarios"]:
        scenario = scenario_from_payload(scenario_payload)
        for advisor_label, recommendation_payloads in scenario_payload[
            "recommendations"
        ].items():
            recommendations = tuple(
                recommendation_from_payload(payload)
                for payload in recommendation_payloads
            )
            reports.append(evaluate_run_set(scenario, advisor_label, recommendations))
    return tuple(reports)


def summarize_reports(
    suite: dict[str, Any], reports: tuple[AdvisorRunSetReport, ...]
) -> dict[str, Any]:
    return {
        "version": suite["version"],
        "description": suite["description"],
        "scenario_count": len(suite["scenarios"]),
        "advisor_count": len({report.advisor_label for report in reports}),
        "overall": overall_summary(reports),
        "by_advisor": summarize_by_advisor(reports),
        "reports": [report_payload(report) for report in reports],
    }


def overall_summary(reports: tuple[AdvisorRunSetReport, ...]) -> dict[str, Any]:
    return {
        "run_sets": len(reports),
        "mean_valid_rate": mean(report.valid_rate for report in reports),
        "mean_policy_jaccard": mean(report.mean_policy_jaccard for report in reports),
        "mean_stability": mean(report.stability.mean_pairwise_jaccard for report in reports),
        "violation_counts": flatten_violation_counts(reports),
    }


def summarize_by_advisor(
    reports: tuple[AdvisorRunSetReport, ...]
) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[AdvisorRunSetReport]] = defaultdict(list)
    for report in reports:
        grouped[report.advisor_label].append(report)
    return {
        advisor_label: {
            "scenarios": len(items),
            "mean_valid_rate": mean(item.valid_rate for item in items),
            "mean_policy_jaccard": mean(item.mean_policy_jaccard for item in items),
            "mean_stability": mean(
                item.stability.mean_pairwise_jaccard for item in items
            ),
            "violation_counts": flatten_violation_counts(tuple(items)),
        }
        for advisor_label, items in sorted(grouped.items())
    }


def flatten_violation_counts(
    reports: tuple[AdvisorRunSetReport, ...]
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for report in reports:
        for violation, count in report.violation_counts:
            counts[violation] = counts.get(violation, 0) + count
    return dict(sorted(counts.items()))


def report_payload(report: AdvisorRunSetReport) -> dict[str, Any]:
    payload = asdict(report)
    payload["valid_rate"] = report.valid_rate
    return payload


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# AI Advisor Audit Reference",
        "",
        "This file is generated from frozen offline scenarios. It does not contain",
        "live model outputs or investment advice.",
        "",
        "## Overall",
        "",
        f"- Scenarios: {summary['scenario_count']}",
        f"- Advisor labels: {summary['advisor_count']}",
        f"- Mean valid rate: {summary['overall']['mean_valid_rate']:.3f}",
        f"- Mean policy Jaccard: {summary['overall']['mean_policy_jaccard']:.3f}",
        f"- Mean stability: {summary['overall']['mean_stability']:.3f}",
        "",
        "## By Advisor",
        "",
        "| Advisor | Valid rate | Policy Jaccard | Stability | Violations |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for advisor_label, values in summary["by_advisor"].items():
        violations = ", ".join(
            f"{violation}={count}"
            for violation, count in values["violation_counts"].items()
        )
        if not violations:
            violations = "none"
        lines.append(
            f"| {advisor_label} | {values['mean_valid_rate']:.3f} | "
            f"{values['mean_policy_jaccard']:.3f} | "
            f"{values['mean_stability']:.3f} | {violations} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def figure_advisor_audit(summary: dict[str, Any], path: Path) -> None:
    labels = sorted(summary["by_advisor"], key=advisor_sort_key)
    valid = [summary["by_advisor"][label]["mean_valid_rate"] for label in labels]
    jaccard = [summary["by_advisor"][label]["mean_policy_jaccard"] for label in labels]
    stable = [summary["by_advisor"][label]["mean_stability"] for label in labels]
    x_positions = range(len(labels))
    width = 0.24

    fig, axis = plt.subplots(figsize=(9.5, 3.8), dpi=150)
    fig.patch.set_facecolor("white")
    axis.set_facecolor(PAPER)
    axis.bar([x - width for x in x_positions], valid, width, color=SUCCESS, label="Valid")
    axis.bar(x_positions, jaccard, width, color=GOLD, label="Policy agreement")
    axis.bar([x + width for x in x_positions], stable, width, color=BLUE, label="Stability")
    axis.set_ylim(0, 1.05)
    axis.set_ylabel("Score")
    axis.set_title(
        "Deterministic audit exposes advisor failure modes",
        color=CARBON,
        fontweight="bold",
    )
    axis.set_xticks(list(x_positions))
    axis.set_xticklabels([display_label(label) for label in labels], fontsize=8)
    axis.legend(frameon=False, ncols=3, loc="upper right")
    axis.grid(True, axis="y", color="#d8d6cd", linewidth=0.5)
    for spine in ("top", "right"):
        axis.spines[spine].set_visible(False)
    axis.tick_params(colors=MUTED)
    fig.tight_layout()
    fig.savefig(path, facecolor="white")
    plt.close(fig)


def write_advisor_audit_tikz(summary: dict[str, Any], path: Path) -> None:
    labels = sorted(summary["by_advisor"], key=advisor_sort_key)
    rows = [
        (
            display_label(label).replace("\n", "\\\\"),
            summary["by_advisor"][label]["mean_valid_rate"],
            summary["by_advisor"][label]["mean_policy_jaccard"],
            summary["by_advisor"][label]["mean_stability"],
        )
        for label in labels
    ]
    coordinates = {
        "valid": " ".join(
            f"({index + 1},{valid:.3f})"
            for index, (_, valid, _, _) in enumerate(rows)
        ),
        "agreement": " ".join(
            f"({index + 1},{agreement:.3f})"
            for index, (_, _, agreement, _) in enumerate(rows)
        ),
        "stability": " ".join(
            f"({index + 1},{stability:.3f})"
            for index, (_, _, _, stability) in enumerate(rows)
        ),
        "labels": ",".join(label for label, *_ in rows),
    }
    path.write_text(
        rf"""\begin{{tikzpicture}}
\begin{{axis}}[
  ybar,
  width=\columnwidth,
  height=0.42\columnwidth,
  ymin=0,
  ymax=1.05,
  bar width=2.6pt,
  enlarge x limits=0.08,
  ylabel={{Score}},
  symbolic x coords={{1,2,3,4,5,6,7}},
  xtick={{1,2,3,4,5,6,7}},
  xticklabels={{{coordinates["labels"]}}},
  x tick label style={{font=\scriptsize, align=center}},
  ymajorgrids=true,
  grid style={{draw=black!12}},
  axis line style={{draw=black!45}},
  tick style={{draw=black!45}},
  legend style={{draw=none, fill=none, font=\scriptsize, at={{(0.98,0.98)}}, anchor=north east}},
  legend columns=3,
]
\addplot+[draw=none, fill=arenaGreen] coordinates {{{coordinates["valid"]}}};
\addplot+[draw=none, fill=arenaGold] coordinates {{{coordinates["agreement"]}}};
\addplot+[draw=none, fill=arenaBlue] coordinates {{{coordinates["stability"]}}};
\legend{{Valid,Agreement,Stability}}
\end{{axis}}
\end{{tikzpicture}}
""",
        encoding="utf-8",
    )


def advisor_sort_key(label: str) -> tuple[int, str]:
    order = {
        "deterministic_policy": 0,
        "valid_but_low_agreement": 1,
        "drifting_advisor": 2,
        "naive_diversifier": 3,
        "underdeploying_advisor": 4,
        "popularity_chaser": 5,
        "constraint_breaker": 6,
    }
    return order.get(label, 99), label


def display_label(label: str) -> str:
    names = {
        "constraint_breaker": "breaks",
        "deterministic_policy": "policy",
        "drifting_advisor": "drift",
        "naive_diversifier": "naive\nsplit",
        "popularity_chaser": "popular",
        "underdeploying_advisor": "underdeploy",
        "valid_but_low_agreement": "valid\nlow-agree",
    }
    return names.get(label, label.replace("_", "\n"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenarios", type=Path, default=DEFAULT_SCENARIOS)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--reference", action="store_true")
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--figure", type=Path, default=FIGURE_OUTPUT)
    parser.add_argument("--tikz", type=Path, default=TIKZ_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    suite = load_suite(args.scenarios)
    reports = evaluate_suite(suite)
    summary = summarize_reports(suite, reports)
    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    output = args.output or EXPORT_DIR / f"ai_advisor_audit_{stamp}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if args.reference:
        REFERENCE_OUTPUT.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    markdown = args.markdown or output.with_suffix(".md")
    write_markdown(summary, markdown)
    args.figure.parent.mkdir(parents=True, exist_ok=True)
    figure_advisor_audit(summary, args.figure)
    args.tikz.parent.mkdir(parents=True, exist_ok=True)
    write_advisor_audit_tikz(summary, args.tikz)
    print(
        "AI advisor audit: "
        f"valid={summary['overall']['mean_valid_rate']:.3f} "
        f"policy_jaccard={summary['overall']['mean_policy_jaccard']:.3f} "
        f"stability={summary['overall']['mean_stability']:.3f}"
    )
    print(f"Wrote {output}")
    print(f"Wrote {markdown}")
    print(f"Wrote {args.figure}")
    print(f"Wrote {args.tikz}")


if __name__ == "__main__":
    main()
