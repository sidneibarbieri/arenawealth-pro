from arenawealth.experiments.ai_advisor import (
    AdvisorRecommendation,
    AdvisorScenario,
    check_constraints,
    compare_to_policy,
    evaluate_run_set,
    normalize_tickers,
    stability,
)


def test_normalize_tickers_preserves_order_and_removes_duplicates() -> None:
    assert normalize_tickers((" ma ", "ADBE", "MA", "", "anet")) == (
        "MA",
        "ADBE",
        "ANET",
    )


def test_constraint_report_flags_invalid_ai_recommendations() -> None:
    scenario = AdvisorScenario(
        name="add_candidates",
        cash=1500.0,
        allowed_tickers=("MA", "ADBE", "ANET"),
        owned_tickers=("TSM", "MSFT"),
        max_recommendations=2,
    )
    recommendation = AdvisorRecommendation(
        run_id="model_run_1",
        tickers=("MA", "MSFT", "NVDA"),
    )

    report = check_constraints(scenario, recommendation)

    assert not report.is_valid
    assert report.violations == (
        "too_many_recommendations",
        "ticker_not_allowed:MSFT",
        "already_owned:MSFT",
        "ticker_not_allowed:NVDA",
    )


def test_policy_comparison_measures_overlap_and_extras() -> None:
    recommendation = AdvisorRecommendation(run_id="model_run_1", tickers=("MA", "NVDA", "ADBE"))

    comparison = compare_to_policy(recommendation, ("MA", "ADBE", "ANET"), k=3)

    assert comparison.overlap_at_k == 2
    assert comparison.jaccard == 0.5
    assert comparison.missing_policy_tickers == ("ANET",)
    assert comparison.extra_tickers == ("NVDA",)


def test_stability_uses_mean_pairwise_jaccard() -> None:
    report = stability(
        (
            AdvisorRecommendation(run_id="run_1", tickers=("MA", "ADBE")),
            AdvisorRecommendation(run_id="run_2", tickers=("MA", "ANET")),
            AdvisorRecommendation(run_id="run_3", tickers=("MA", "ADBE")),
        )
    )

    assert report.runs == 3
    assert round(report.mean_pairwise_jaccard, 3) == 0.556
    assert report.unique_tickers == ("ADBE", "ANET", "MA")


def test_single_run_stability_is_defined_as_one() -> None:
    report = stability((AdvisorRecommendation(run_id="run_1", tickers=("MA",)),))

    assert report.runs == 1
    assert report.mean_pairwise_jaccard == 1.0
    assert report.unique_tickers == ("MA",)


def test_constraint_report_flags_fee_wasting_cash_split() -> None:
    scenario = AdvisorScenario(
        name="subtranche_cash",
        cash=900.0,
        allowed_tickers=("TSM", "NVO"),
        owned_tickers=("TSM", "NVO"),
        policy_tickers=("TSM",),
        max_recommendations=2,
        add_only=False,
        amounts_required=True,
    )
    recommendation = AdvisorRecommendation(
        run_id="naive_split",
        tickers=("TSM", "NVO"),
        amounts=(540.0, 360.0),
    )

    report = check_constraints(scenario, recommendation)

    assert report.violations == ("unnecessary_split_fee",)


def test_constraint_report_flags_unsupported_fact_ids() -> None:
    scenario = AdvisorScenario(
        name="fact_check",
        cash=1500.0,
        allowed_tickers=("MA",),
        owned_tickers=(),
        available_fact_ids=("ma_policy_candidate",),
    )
    recommendation = AdvisorRecommendation(
        run_id="fact_hallucination",
        tickers=("MA",),
        cited_fact_ids=("ma_policy_candidate", "unsupported_dividend_fact"),
    )

    report = check_constraints(scenario, recommendation)

    assert report.violations == ("unsupported_fact:unsupported_dividend_fact",)


def test_evaluate_run_set_reports_validity_agreement_and_stability() -> None:
    scenario = AdvisorScenario(
        name="addition",
        cash=1511.18,
        allowed_tickers=("MA", "ADBE", "ANET", "NVDA"),
        owned_tickers=("TSM",),
        policy_tickers=("MA", "ADBE", "ANET"),
    )
    recommendations = (
        AdvisorRecommendation(run_id="run_1", tickers=("MA", "ADBE", "ANET")),
        AdvisorRecommendation(run_id="run_2", tickers=("MA", "NVDA", "ADBE")),
    )

    report = evaluate_run_set(scenario, "test_advisor", recommendations)

    assert report.scenario_name == "addition"
    assert report.advisor_label == "test_advisor"
    assert report.runs == 2
    assert report.valid_runs == 2
    assert report.valid_rate == 1.0
    assert report.mean_overlap_at_k == 2.5
    assert report.mean_policy_jaccard == 0.75
    assert report.stability.mean_pairwise_jaccard == 0.5
