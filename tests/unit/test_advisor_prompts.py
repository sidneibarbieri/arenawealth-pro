"""Unit tests for advisor prompt building and response parsing (no network)."""

import pytest

from arenawealth.experiments.advisor_prompts import build_prompt, parse_response

SCENARIO = {
    "name": "demo",
    "cash": 1500.00,
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
    assert "1500.00" in prompt
    assert "Do not recommend already-owned tickers" in prompt


def test_parse_clean_json():
    parsed = parse_response('{"tickers": ["ma", "adbe"], "cited_fact_ids": ["fact_a"]}')
    assert parsed["tickers"] == ("MA", "ADBE")
    assert parsed["amounts"] == ()
    assert parsed["cited_fact_ids"] == ("fact_a",)


def test_prompt_allows_owned_tickers_when_add_only_is_false():
    prompt = build_prompt(
        {
            "name": "top_up",
            "cash": 900.0,
            "allowed_tickers": ["TSM", "NVO"],
            "owned_tickers": ["TSM", "NVO", "MSFT"],
            "available_fact_ids": [],
            "max_recommendations": 2,
            "add_only": False,
            "amounts_required": True,
        }
    )

    assert "You may recommend already-owned tickers" in prompt
    assert 'Include an "amounts" array' in prompt


def test_parse_amounts_when_present():
    parsed = parse_response('{"tickers": ["TSM"], "amounts": [900.0], "cited_fact_ids": []}')

    assert parsed["tickers"] == ("TSM",)
    assert parsed["amounts"] == (900.0,)


def test_parse_extracts_json_from_surrounding_prose():
    reply = 'Sure, here is my pick:\n{"tickers": ["ANET"]}\nHope this helps.'
    assert parse_response(reply)["tickers"] == ("ANET",)


def test_parse_missing_tickers_raises():
    with pytest.raises(ValueError):
        parse_response('{"cited_fact_ids": ["fact_a"]}')


def test_parse_no_json_raises():
    with pytest.raises(ValueError):
        parse_response("I cannot help with that.")


def test_prompt_arms_form_a_hierarchy():
    bare = build_prompt(SCENARIO, arm="bare")
    policy = build_prompt(SCENARIO, arm="policy")
    scaffold = build_prompt(SCENARIO, arm="scaffold")
    for prompt in (bare, policy, scaffold):
        assert "Allowed universe: MA, ADBE, ANET" in prompt
        assert "Reply with one JSON object" in prompt
    assert "Do not recommend already-owned tickers" not in bare
    assert "Fee arithmetic" not in bare
    assert "Do not recommend already-owned tickers" in policy
    assert "Fee arithmetic" not in policy
    assert "Do not recommend already-owned tickers" in scaffold
    assert "Fee arithmetic" in scaffold


def test_scaffold_precomputes_fee_and_floor():
    prompt = build_prompt(SCENARIO, arm="scaffold")
    assert "USD 5.00" in prompt  # one order of 1500 spans two 1000-tranches
    assert "250.00" in prompt  # economic floor c/tau
    assert "2.50" in prompt  # fee per tranche


def test_prompts_are_deterministic_per_arm():
    for arm in ("bare", "policy", "scaffold"):
        assert build_prompt(SCENARIO, arm=arm) == build_prompt(SCENARIO, arm=arm)


def test_unknown_arm_raises():
    with pytest.raises(ValueError):
        build_prompt(SCENARIO, arm="zero_shot")


def test_default_arm_is_policy():
    assert build_prompt(SCENARIO) == build_prompt(SCENARIO, arm="policy")
