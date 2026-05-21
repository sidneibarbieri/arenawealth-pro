"""Deterministic portfolio upgrade review."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from arenawealth.analytics.models import PositionAnalysis
from arenawealth.analytics.screening import CandidateAnalysis

TARGET_MIN_POSITIONS = 18
TARGET_MAX_POSITIONS = 25
UPGRADE_SCORE_GAP = 8.0
VALUATION_TOLERANCE = 5.0
TRIM_SCORE_LIMIT = 70.0


@dataclass(frozen=True)
class AdditionReview:
    ticker: str
    name: str
    theme: str
    composite_score: float
    reason: str


@dataclass(frozen=True)
class ReplacementReview:
    current_ticker: str
    candidate_ticker: str
    candidate_name: str
    score_gap: float
    reason: str


@dataclass(frozen=True)
class TrimReview:
    ticker: str
    weight_pct: float
    composite_score: float
    reason: str


@dataclass(frozen=True)
class PortfolioReview:
    current_positions: int
    target_min_positions: int
    target_max_positions: int
    additions_needed: int
    add_candidates: tuple[AdditionReview, ...]
    replacement_watch: tuple[ReplacementReview, ...]
    trim_watch: tuple[TrimReview, ...]


def review_additions(
    candidates: Sequence[CandidateAnalysis],
    current_positions: int,
    target_min_positions: int,
    target_max_positions: int,
) -> tuple[int, tuple[AdditionReview, ...]]:
    additions_needed = max(0, target_min_positions - current_positions)
    if current_positions > target_max_positions:
        return additions_needed, ()
    reason = (
        "Portfolio is below the target range."
        if additions_needed
        else "Highest-scoring external candidate."
    )
    limit = max(3, additions_needed)
    additions = tuple(
        AdditionReview(
            ticker=candidate.ticker,
            name=candidate.name,
            theme=candidate.theme,
            composite_score=candidate.score.composite_score,
            reason=reason,
        )
        for candidate in candidates[:limit]
    )
    return additions_needed, additions


def review_replacements(
    held: Sequence[PositionAnalysis],
    candidates: Sequence[CandidateAnalysis],
) -> tuple[ReplacementReview, ...]:
    replacements: list[ReplacementReview] = []
    used_candidates: set[str] = set()
    weakest_holdings = sorted(held, key=lambda analysis: analysis.composite_score)
    ranked_candidates = sorted(
        candidates, key=lambda candidate: candidate.score.composite_score, reverse=True
    )
    for current in weakest_holdings:
        for candidate in ranked_candidates:
            if candidate.ticker in used_candidates:
                continue
            score_gap = candidate.score.composite_score - current.composite_score
            valuation_gap = candidate.score.valuation_points - current.valuation_points
            if score_gap >= UPGRADE_SCORE_GAP and valuation_gap >= -VALUATION_TOLERANCE:
                replacements.append(
                    ReplacementReview(
                        current_ticker=current.holding.ticker,
                        candidate_ticker=candidate.ticker,
                        candidate_name=candidate.name,
                        score_gap=score_gap,
                        reason="Candidate clears score gap without a material valuation penalty.",
                    )
                )
                used_candidates.add(candidate.ticker)
                break
        if len(replacements) == 3:
            break
    return tuple(replacements)


def review_trims(held: Sequence[PositionAnalysis]) -> tuple[TrimReview, ...]:
    if not held:
        return ()
    equal_weight = 100 / len(held)
    overweight_limit = equal_weight * 1.3
    trims = [
        TrimReview(
            ticker=analysis.holding.ticker,
            weight_pct=analysis.weight_pct,
            composite_score=analysis.composite_score,
            reason="Position is above the concentration limit with sub-threshold quality score.",
        )
        for analysis in held
        if analysis.weight_pct > overweight_limit and analysis.composite_score < TRIM_SCORE_LIMIT
    ]
    return tuple(sorted(trims, key=lambda item: item.weight_pct, reverse=True))


def review_portfolio(
    held: Sequence[PositionAnalysis],
    candidates: Sequence[CandidateAnalysis],
    target_min_positions: int = TARGET_MIN_POSITIONS,
    target_max_positions: int = TARGET_MAX_POSITIONS,
) -> PortfolioReview:
    additions_needed, additions = review_additions(
        candidates, len(held), target_min_positions, target_max_positions
    )
    return PortfolioReview(
        current_positions=len(held),
        target_min_positions=target_min_positions,
        target_max_positions=target_max_positions,
        additions_needed=additions_needed,
        add_candidates=additions,
        replacement_watch=review_replacements(held, candidates),
        trim_watch=review_trims(held),
    )
