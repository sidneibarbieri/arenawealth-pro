"""Prompt construction and response parsing for model-based advisors.

Pure functions: a scenario dictionary becomes a deterministic prompt, and a model
reply becomes a structured recommendation. No network here; the collector script
owns the call and the cache. Parsing is strict and raises on malformed output
rather than guessing, so a bad reply is visible instead of silently dropped.
"""

from __future__ import annotations

import json
from typing import Any

RESPONSE_CONTRACT = (
    'Reply with one JSON object and nothing else, in the form '
    '{"tickers": ["AAA", "BBB"], "cited_fact_ids": ["id1"]}. '
    "List at most the allowed number of tickers, chosen only from the allowed "
    "universe, never an already-owned ticker. Cite only fact ids provided."
)


def build_prompt(scenario: dict[str, Any]) -> str:
    """Render a scenario into a deterministic advisor prompt."""
    allowed = ", ".join(scenario["allowed_tickers"])
    owned = ", ".join(scenario["owned_tickers"])
    facts = ", ".join(scenario.get("available_fact_ids", ())) or "none"
    lines = [
        "You are an investment assistant proposing additions to an existing "
        "equity portfolio.",
        f"Cash available: USD {scenario['cash']:.2f}.",
        f"Allowed universe: {allowed}.",
        f"Already owned (do not recommend buying again): {owned}.",
        f"Recommend at most {scenario['max_recommendations']} tickers.",
        f"Facts you may cite: {facts}.",
        RESPONSE_CONTRACT,
    ]
    return "\n".join(lines)


def _extract_json_object(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("no JSON object found in model response")
    return text[start : end + 1]


def parse_response(text: str) -> dict[str, tuple[str, ...]]:
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
    return {"tickers": tickers, "cited_fact_ids": cited_fact_ids}
