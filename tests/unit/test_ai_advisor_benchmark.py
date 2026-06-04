from arenawealth.experiments.ai_advisor import (
    AdvisorRecommendation,
    AdvisorScenario,
    check_constraints,
    compare_to_policy,
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
