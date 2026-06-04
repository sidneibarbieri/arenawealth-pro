"""Unit tests for advisor prompt building and response parsing (no network)."""

import pytest

from arenawealth.experiments.advisor_prompts import build_prompt, parse_response

SCENARIO = {
    "name": "demo",
    "cash": 1511.18,
    "allowed_tickers": ["MA", "ADBE", "ANET"],
    "owned_tickers": ["MSFT", "AAPL"],
    "available_fact_ids": ["fact_a", "fact_b"],
    "max_recommendations": 3,
}


def test_prompt_lists_constraints_deterministically():
    prompt = build_prompt(SCENARIO)
    assert build_prompt(SCENARIO) == prompt  # deterministic
    assert "MA, ADBE, ANET" in prompt
    assert "MSFT, AAPL" in prompt
    assert "at most 3" in prompt
    assert "1511.18" in prompt


def test_parse_clean_json():
    parsed = parse_response('{"tickers": ["ma", "adbe"], "cited_fact_ids": ["fact_a"]}')
    assert parsed["tickers"] == ("MA", "ADBE")
    assert parsed["cited_fact_ids"] == ("fact_a",)


def test_parse_extracts_json_from_surrounding_prose():
    reply = 'Sure, here is my pick:\n{"tickers": ["ANET"]}\nHope this helps.'
    assert parse_response(reply)["tickers"] == ("ANET",)


def test_parse_missing_tickers_raises():
    with pytest.raises(ValueError):
        parse_response('{"cited_fact_ids": ["fact_a"]}')


def test_parse_no_json_raises():
    with pytest.raises(ValueError):
        parse_response("I cannot help with that.")
