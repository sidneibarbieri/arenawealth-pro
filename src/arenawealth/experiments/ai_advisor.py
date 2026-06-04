"""Offline metrics for AI-advisor recommendation benchmarks."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from statistics import mean


@dataclass(frozen=True)
class AdvisorScenario:
    """Frozen constraints for one AI-advisor benchmark prompt."""

    name: str
    cash: float
    allowed_tickers: tuple[str, ...]
    owned_tickers: tuple[str, ...]
    max_recommendations: int = 3
    add_only: bool = True


@dataclass(frozen=True)
class AdvisorRecommendation:
    """One model or advisor output reduced to auditable tickers."""

    run_id: str
    tickers: tuple[str, ...]


@dataclass(frozen=True)
class ConstraintReport:
    run_id: str
    violations: tuple[str, ...]

    @property
    def is_valid(self) -> bool:
        return not self.violations


@dataclass(frozen=True)
class PolicyComparison:
    run_id: str
    overlap_at_k: int
    jaccard: float
    missing_policy_tickers: tuple[str, ...]
    extra_tickers: tuple[str, ...]


@dataclass(frozen=True)
class StabilityReport:
    runs: int
    mean_pairwise_jaccard: float
    unique_tickers: tuple[str, ...]


def normalize_tickers(tickers: tuple[str, ...]) -> tuple[str, ...]:
    """Uppercase tickers and remove duplicates while preserving first occurrence."""
    seen: set[str] = set()
    normalized: list[str] = []
    for ticker in tickers:
        clean_ticker = ticker.strip().upper()
        if not clean_ticker or clean_ticker in seen:
            continue
        seen.add(clean_ticker)
        normalized.append(clean_ticker)
    return tuple(normalized)


def jaccard(left: tuple[str, ...], right: tuple[str, ...]) -> float:
    left_set = set(left)
    right_set = set(right)
    union = left_set | right_set
    if not union:
        return 1.0
    return len(left_set & right_set) / len(union)


def check_constraints(
    scenario: AdvisorScenario, recommendation: AdvisorRecommendation
) -> ConstraintReport:
    tickers = normalize_tickers(recommendation.tickers)
    allowed = set(normalize_tickers(scenario.allowed_tickers))
    owned = set(normalize_tickers(scenario.owned_tickers))
    violations: list[str] = []
    if len(tickers) > scenario.max_recommendations:
        violations.append("too_many_recommendations")
    for ticker in tickers:
        if ticker not in allowed:
            violations.append(f"ticker_not_allowed:{ticker}")
        if scenario.add_only and ticker in owned:
            violations.append(f"already_owned:{ticker}")
    return ConstraintReport(run_id=recommendation.run_id, violations=tuple(violations))


def compare_to_policy(
    recommendation: AdvisorRecommendation, policy_tickers: tuple[str, ...], k: int
) -> PolicyComparison:
    advisor_top = normalize_tickers(recommendation.tickers)[:k]
    policy_top = normalize_tickers(policy_tickers)[:k]
    advisor_set = set(advisor_top)
    policy_set = set(policy_top)
    return PolicyComparison(
        run_id=recommendation.run_id,
        overlap_at_k=len(advisor_set & policy_set),
        jaccard=jaccard(advisor_top, policy_top),
        missing_policy_tickers=tuple(ticker for ticker in policy_top if ticker not in advisor_set),
        extra_tickers=tuple(ticker for ticker in advisor_top if ticker not in policy_set),
    )


def stability(recommendations: tuple[AdvisorRecommendation, ...]) -> StabilityReport:
    normalized = [normalize_tickers(recommendation.tickers) for recommendation in recommendations]
    unique = tuple(sorted({ticker for tickers in normalized for ticker in tickers}))
    if len(normalized) < 2:
        return StabilityReport(
            runs=len(normalized),
            mean_pairwise_jaccard=1.0,
            unique_tickers=unique,
        )
    scores = [jaccard(left, right) for left, right in combinations(normalized, 2)]
    return StabilityReport(
        runs=len(normalized),
        mean_pairwise_jaccard=mean(scores),
        unique_tickers=unique,
    )
