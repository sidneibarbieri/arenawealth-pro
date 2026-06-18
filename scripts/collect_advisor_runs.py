#!/usr/bin/env python3
"""Collect repeated advisor outputs for the frozen audit scenarios.

Budget-guarded and cached. Each (model, scenario, run) result is written to a
JSON cache and never re-requested, so a small call budget is spent once and the
audit then runs offline forever. The default mode is a dry run that makes zero
API calls and reports what it would request; live collection requires an
explicit flag, provider credentials in the environment, and stays under
--max-calls.

Usage:
    # Dry run: shows the plan, makes no calls.
    python scripts/collect_advisor_runs.py --provider azure --model chat --runs 3

    # Live: needs provider credentials, uses cache, and respects the call cap.
    python scripts/collect_advisor_runs.py \
      --provider azure --model chat --runs 3 --live --max-calls 10
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv

from arenawealth.experiments.advisor_prompts import build_prompt, parse_response
from arenawealth.experiments.ai_advisor import (
    AdvisorRecommendation,
    AdvisorScenario,
    evaluate_run_set,
)
from arenawealth.experiments.llm_clients import (
    DEFAULT_ANTHROPIC_MODEL,
    DEFAULT_OPENAI_MODEL,
    AdvisorLLMClient,
    build_llm_client,
)

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

SCENARIOS_PATH = ROOT / "paper" / "data" / "ai_advisor_scenarios.json"
CACHE_ROOT = ROOT / "exports" / "advisor_runs"


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


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    return slug.strip("._") or "unnamed"


def cache_path(
    provider: str,
    model: str,
    scenario_name: str,
    run_index: int,
    cache_root: Path = CACHE_ROOT,
) -> Path:
    return (
        cache_root
        / safe_slug(provider)
        / safe_slug(model)
        / f"{safe_slug(scenario_name)}__run{run_index}.json"
    )


def prompt_hash(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def model_label(provider: str, model: str | None) -> str:
    if model:
        return model
    normalized = provider.strip().lower()
    if normalized == "azure":
        return (
            os.getenv("AZURE_OPENAI_DEPLOYMENT")
            or os.getenv("AZURE_OPENAI_MODEL")
            or "azure-model"
        )
    if normalized == "openai":
        return os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
    if normalized == "anthropic":
        return os.getenv("ANTHROPIC_MODEL", DEFAULT_ANTHROPIC_MODEL)
    return "unknown-model"


def collect_run(
    scenario: dict,
    provider: str,
    model: str,
    run_index: int,
    temperature: float,
    live: bool,
    budget: CallBudget,
    cache_root: Path,
    client: AdvisorLLMClient | None,
) -> dict:
    """Return the cached run if present; otherwise request it when live."""
    prompt = build_prompt(scenario)
    current_prompt_hash = prompt_hash(prompt)
    path = cache_path(provider, model, scenario["name"], run_index, cache_root)
    if path.exists():
        cached = json.loads(path.read_text(encoding="utf-8"))
        if cached.get("prompt_hash") == current_prompt_hash:
            return cached
    if not live:
        return {
            "status": "would_call",
            "provider": provider,
            "model": model,
            "scenario": scenario["name"],
            "run_index": run_index,
            "prompt_hash": current_prompt_hash,
        }
    if client is None:
        raise RuntimeError("live collection requires a provider client")
    budget.spend()
    completion = client.complete(prompt, temperature)
    record = {
        "status": "collected",
        "provider": provider,
        "model": model,
        "scenario": scenario["name"],
        "run_index": run_index,
        "temperature": temperature,
        "prompt": prompt,
        "prompt_hash": current_prompt_hash,
        "raw_response": completion.text,
        "usage": completion.usage,
        "collected_utc": datetime.now(UTC).isoformat(),
    }
    # A malformed reply is a measured outcome, not a crash: record it and mark
    # the run unparseable so the audit counts it as invalid.
    try:
        record["parsed"] = parse_response(completion.text)
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
            amounts=tuple(record["parsed"].get("amounts", ())),
            cited_fact_ids=tuple(record["parsed"]["cited_fact_ids"]),
        )
        for record in usable
    )
    report = evaluate_run_set(scenario_from_dict(scenario), model, recommendations)
    return asdict(report)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--provider",
        choices=("azure", "openai", "anthropic"),
        default=os.getenv("ADVISOR_LLM_PROVIDER", "azure"),
    )
    parser.add_argument("--model", help="Provider model or Azure deployment. Defaults to env.")
    parser.add_argument("--runs", type=int, default=3, help="Repeated runs per scenario.")
    parser.add_argument("--max-calls", type=int, default=10, help="Hard cap on live API calls.")
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--live", action="store_true", help="Make real API calls; off by default.")
    parser.add_argument("--scenarios", type=Path, default=SCENARIOS_PATH)
    parser.add_argument("--cache-root", type=Path, default=CACHE_ROOT)
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    scenarios = load_scenarios(arguments.scenarios)
    model = model_label(arguments.provider, arguments.model)
    client = build_llm_client(arguments.provider, arguments.model) if arguments.live else None
    if client is not None:
        model = client.model
    budget = CallBudget(arguments.max_calls)
    planned = len(scenarios) * arguments.runs
    if arguments.live and planned > arguments.max_calls:
        # Cached runs do not spend budget, so this is a ceiling, not a guarantee.
        print(f"note: {planned} runs planned, budget {arguments.max_calls}; cached runs are free.")

    audits: list[dict] = []
    for scenario in scenarios:
        records = [
            collect_run(
                scenario,
                arguments.provider,
                model,
                index,
                arguments.temperature,
                arguments.live,
                budget,
                arguments.cache_root,
                client,
            )
            for index in range(1, arguments.runs + 1)
        ]
        audit = audit_collected(scenario, model, records)
        if audit is not None:
            audits.append(audit)

    print(f"live calls used: {budget.used} / {arguments.max_calls}")
    if not audits:
        print(
            "no audits produced: nothing cached and no live calls. "
            "Re-run with --live and credentials, or point --cache-root at cached runs."
        )
        return
    summary_path = (
        arguments.cache_root
        / safe_slug(arguments.provider)
        / safe_slug(model)
        / "audit_summary.json"
    )
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(audits, indent=2), encoding="utf-8")
    source = "live + cache" if arguments.live else "cache only (no API calls)"
    print(f"wrote {summary_path} from {source}")


if __name__ == "__main__":
    main()
