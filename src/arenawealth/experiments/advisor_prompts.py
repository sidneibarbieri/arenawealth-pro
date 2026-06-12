"""Prompt construction and response parsing for model-based advisors.

Pure functions: a scenario dictionary becomes a deterministic prompt, and a model
reply becomes a structured recommendation. No network here; the collector script
owns the call and the cache. Parsing is strict and raises on malformed output
rather than guessing, so a bad reply is visible instead of silently dropped.
"""

from __future__ import annotations

import json
from typing import Any


def build_prompt(scenario: dict[str, Any]) -> str:
    """Render a scenario into a deterministic advisor prompt."""
    allowed = ", ".join(scenario["allowed_tickers"])
    owned = ", ".join(scenario["owned_tickers"])
    facts = ", ".join(scenario.get("available_fact_ids", ())) or "none"
    add_only = scenario.get("add_only", True)
    ownership_rule = (
        "Do not recommend already-owned tickers."
        if add_only
        else "You may recommend already-owned tickers when they are in the allowed universe."
    )
    amount_rule = (
        'Include an "amounts" array with one USD amount per ticker.'
        if scenario.get("amounts_required", False)
        else 'Do not include an "amounts" field unless explicitly required.'
    )
    response_contract = (
        "Reply with one JSON object and nothing else, in the form "
        '{"tickers": ["AAA", "BBB"], "amounts": [500.0, 750.0], '
        '"cited_fact_ids": ["id1"]}. '
        f"{ownership_rule} {amount_rule} Cite only fact ids provided."
    )
    lines = [
        "You are an investment assistant proposing additions to an existing equity portfolio.",
        f"Cash available: USD {scenario['cash']:.2f}.",
        f"Allowed universe: {allowed}.",
        f"Already owned: {owned}.",
        f"Recommend at most {scenario['max_recommendations']} tickers.",
        f"Facts you may cite: {facts}.",
        response_contract,
    ]
    return "\n".join(lines)


def _extract_json_object(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("no JSON object found in model response")
    return text[start : end + 1]


def parse_response(text: str) -> dict[str, tuple[str, ...] | tuple[float, ...]]:
    """Parse a model reply into normalized tickers and cited fact ids.

    Raises ValueError if the reply has no JSON object or no ticker list, so an
    unusable response is recorded as a parse failure rather than an empty pick.
    """
    payload = json.loads(_extract_json_object(text))
    if "tickers" not in payload or not isinstance(payload["tickers"], list):
        raise ValueError("model response has no 'tickers' list")
    tickers = tuple(str(item).strip().upper() for item in payload["tickers"] if str(item).strip())
    cited = payload.get("cited_fact_ids", [])
    cited_fact_ids = tuple(str(item).strip() for item in cited if str(item).strip())
    amounts = tuple(float(item) for item in payload.get("amounts", []) if str(item).strip())
    return {"tickers": tickers, "amounts": amounts, "cited_fact_ids": cited_fact_ids}
