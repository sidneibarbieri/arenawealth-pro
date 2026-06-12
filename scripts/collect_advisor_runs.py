#!/usr/bin/env python3
"""Collect repeated advisor outputs for the frozen audit scenarios.

Budget-guarded and cached. Each (model, scenario, run) result is written to a
JSON cache and never re-requested, so a small call budget is spent once and the
audit then runs offline forever. The default mode is a dry run that makes zero
API calls and reports what it would request; live collection requires an
explicit flag, Azure credentials in the environment, and stays under --max-calls.

Usage:
    # Dry run: shows the plan, makes no calls.
    python scripts/collect_advisor_runs.py --model gpt-4o --runs 3

    # Live: needs AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, and a deployment.
    python scripts/collect_advisor_runs.py --model gpt-4o --runs 3 --live --max-calls 10
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

import httpx
from dotenv import load_dotenv

from arenawealth.experiments.advisor_prompts import build_prompt, parse_response
from arenawealth.experiments.ai_advisor import (
    AdvisorRecommendation,
    AdvisorScenario,
    evaluate_run_set,
)

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

SCENARIOS_PATH = ROOT / "paper" / "data" / "ai_advisor_scenarios.json"
CACHE_ROOT = ROOT / "paper" / "data" / "advisor_runs"
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-06-01")


class CallBudget:
    """Hard cap on live API calls. Raises rather than silently overspending."""

    def __init__(self, limit: int) -> None:
        self.limit = limit
        self.used = 0

    def spend(self) -> None:
        if self.used >= self.limit:
            raise RuntimeError(f"call budget of {self.limit} exhausted")
        self.used += 1


def load_scenarios(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))["scenarios"]


def require_azure_configuration() -> None:
    missing = [
        name
        for name in ("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY")
        if not os.getenv(name)
    ]
    if missing:
        joined = ", ".join(missing)
        raise SystemExit(f"missing Azure OpenAI configuration: {joined}")


def cache_path(model: str, scenario_name: str, run_index: int) -> Path:
    safe_model = model.replace("/", "_")
    return CACHE_ROOT / safe_model / f"{scenario_name}__run{run_index}.json"


def call_azure(prompt: str, deployment: str, temperature: float) -> dict:
    """One chat completion against Azure OpenAI. Errors surface to the caller."""
    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/")
    api_key = os.environ["AZURE_OPENAI_API_KEY"]
    url = f"{endpoint}/openai/deployments/{deployment}/chat/completions"
    response = httpx.post(
        url,
        params={"api-version": API_VERSION},
        headers={"api-key": api_key, "content-type": "application/json"},
        json={
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        },
        timeout=60.0,
    )
    response.raise_for_status()
    body = response.json()
    return {
        "text": body["choices"][0]["message"]["content"],
        "usage": body.get("usage", {}),
    }


def collect_run(
    scenario: dict,
    model: str,
    run_index: int,
    temperature: float,
    live: bool,
    budget: CallBudget,
) -> dict:
    """Return the cached run if present; otherwise request it when live."""
    path = cache_path(model, scenario["name"], run_index)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    prompt = build_prompt(scenario)
    if not live:
        return {"status": "would_call", "scenario": scenario["name"], "run_index": run_index}
    budget.spend()
    completion = call_azure(prompt, model, temperature)
    record = {
        "status": "collected",
        "model": model,
        "scenario": scenario["name"],
        "run_index": run_index,
        "temperature": temperature,
        "prompt": prompt,
        "raw_response": completion["text"],
        "usage": completion["usage"],
        "collected_utc": datetime.now(UTC).isoformat(),
    }
    # A malformed reply is a measured outcome, not a crash: record it and mark
    # the run unparseable so the audit counts it as invalid.
    try:
        record["parsed"] = parse_response(completion["text"])
    except ValueError as error:
        record["parsed"] = {"tickers": [], "cited_fact_ids": []}
        record["parse_error"] = str(error)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return record


def scenario_from_dict(raw: dict) -> AdvisorScenario:
    return AdvisorScenario(
        name=raw["name"],
        cash=raw["cash"],
        allowed_tickers=tuple(raw["allowed_tickers"]),
        owned_tickers=tuple(raw["owned_tickers"]),
        policy_tickers=tuple(raw.get("policy_tickers", ())),
        available_fact_ids=tuple(raw.get("available_fact_ids", ())),
        max_recommendations=raw.get("max_recommendations", 3),
        add_only=raw.get("add_only", True),
        amounts_required=raw.get("amounts_required", False),
    )


def audit_collected(scenario: dict, model: str, records: list[dict]) -> dict | None:
    """Run the offline audit over the cached model outputs for one scenario."""
    usable = [record for record in records if record.get("status") == "collected"]
    if not usable:
        return None
    recommendations = tuple(
        AdvisorRecommendation(
            run_id=f"{model}_{scenario['name']}_{record['run_index']}",
            tickers=tuple(record["parsed"]["tickers"]),
            cited_fact_ids=tuple(record["parsed"]["cited_fact_ids"]),
        )
        for record in usable
    )
    report = evaluate_run_set(scenario_from_dict(scenario), model, recommendations)
    return asdict(report)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="Azure deployment name / advisor label.")
    parser.add_argument("--runs", type=int, default=3, help="Repeated runs per scenario.")
    parser.add_argument("--max-calls", type=int, default=10, help="Hard cap on live API calls.")
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--live", action="store_true", help="Make real API calls; off by default.")
    parser.add_argument("--scenarios", type=Path, default=SCENARIOS_PATH)
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    scenarios = load_scenarios(arguments.scenarios)
    if arguments.live:
        require_azure_configuration()
    budget = CallBudget(arguments.max_calls)
    planned = len(scenarios) * arguments.runs
    if arguments.live and planned > arguments.max_calls:
        # Cached runs do not spend budget, so this is a ceiling, not a guarantee.
        print(f"note: {planned} runs planned, budget {arguments.max_calls}; cached runs are free.")

    audits: list[dict] = []
    for scenario in scenarios:
        records = [
            collect_run(scenario, arguments.model, index, arguments.temperature,
                        arguments.live, budget)
            for index in range(1, arguments.runs + 1)
        ]
        audit = audit_collected(scenario, arguments.model, records)
        if audit is not None:
            audits.append(audit)

    print(f"live calls used: {budget.used} / {arguments.max_calls}")
    if not arguments.live:
        print("dry run: no API calls made. Re-run with --live and Azure credentials to collect.")
        return
    summary_path = CACHE_ROOT / f"{arguments.model.replace('/', '_')}_audit.json"
    summary_path.write_text(json.dumps(audits, indent=2), encoding="utf-8")
    print(f"wrote {summary_path}")


if __name__ == "__main__":
    main()
