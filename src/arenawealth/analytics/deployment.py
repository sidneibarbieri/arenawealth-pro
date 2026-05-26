"""Deterministic, fee-aware cash deployment.

Rules, in order:
1. Concentration: skip positions already above 1.3x equal weight.
2. Fee: the broker charges per started 1,000 of an order, so one order above a
   tranche costs the same as two orders below it. Fund the top two candidates.
3. Selection: rank eligible positions by composite score; size by score share.
4. Theme: the two picks come from distinct themes, and a theme already at the
   concentration cap is skipped, so the dollar goes somewhere additive.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from arenawealth.analytics.models import DeploymentPlan, Order, PositionAnalysis

OVERWEIGHT_MULTIPLE = 1.3
THEME_CONCENTRATION_CAP = 20.0
TRANCHE_SIZE = 1000.0
FEE_PER_TRANCHE = 2.50
MAX_FEE_PCT = 1.0
MIN_ORDER_AMOUNT = FEE_PER_TRANCHE / (MAX_FEE_PCT / 100)


def order_fee(amount: float) -> float:
    if amount <= 0:
        return 0.0
    return math.ceil(amount / TRANCHE_SIZE) * FEE_PER_TRANCHE


def theme_weights(analyses: Sequence[PositionAnalysis]) -> dict[str, float]:
    weights: dict[str, float] = {}
    for analysis in analyses:
        theme = analysis.holding.theme
        weights[theme] = weights.get(theme, 0.0) + analysis.weight_pct
    return weights


def pick_top_two(
    ranked: Sequence[PositionAnalysis], theme_weight: dict[str, float]
) -> tuple[list[PositionAnalysis], list[str]]:
    """Take the two highest scores from distinct, non-saturated themes."""
    picks: list[PositionAnalysis] = []
    blocked: list[str] = []
    used_themes: set[str] = set()
    for analysis in ranked:
        if len(picks) == 2:
            break
        theme = analysis.holding.theme
        if theme_weight.get(theme, 0.0) >= THEME_CONCENTRATION_CAP or theme in used_themes:
            blocked.append(analysis.holding.ticker)
            continue
        picks.append(analysis)
        used_themes.add(theme)
    return picks, blocked


def build_order(analysis: PositionAnalysis, amount: float) -> Order:
    return Order(
        ticker=analysis.holding.ticker,
        amount=amount,
        shares=amount / analysis.live_price,
        fee=order_fee(amount),
    )


def size_orders(picks: Sequence[PositionAnalysis], cash: float) -> tuple[Order, ...]:
    if not picks or cash < MIN_ORDER_AMOUNT:
        return ()
    single = build_order(picks[0], cash)
    if len(picks) == 1 or cash < MIN_ORDER_AMOUNT * 2:
        return (single,)
    first, second = picks[0], picks[1]
    first_share = first.composite_score / (first.composite_score + second.composite_score)
    first_amount = cash * first_share
    second_amount = cash - first_amount
    if first_amount < MIN_ORDER_AMOUNT or second_amount < MIN_ORDER_AMOUNT:
        return (single,)
    # Align one leg to a whole tranche. Because the fee is subadditive
    # (ceil(a/T) + ceil(b/T) >= ceil((a+b)/T)), this is the only split that can
    # preserve the single-order fee when cash spans more than one tranche.
    if first_amount > TRANCHE_SIZE:
        first_amount, second_amount = TRANCHE_SIZE, cash - TRANCHE_SIZE
    elif second_amount > TRANCHE_SIZE:
        second_amount, first_amount = TRANCHE_SIZE, cash - TRANCHE_SIZE
    split = (build_order(first, first_amount), build_order(second, second_amount))
    # Diversify only when it is fee-neutral; otherwise consolidate. This keeps
    # the planner on the fee-optimal frontier even for sub-tranche cash, where a
    # naive proportional split would pay an extra tranche (see
    # experiments.fee_landscape and tests/unit/test_analytics_deployment.py).
    if sum(order.fee for order in split) > single.fee:
        return (single,)
    return split


def plan_deployment(analyses: Sequence[PositionAnalysis], cash: float) -> DeploymentPlan:
    equal_weight = 100 / len(analyses)
    overweight_limit = equal_weight * OVERWEIGHT_MULTIPLE
    eligible = [item for item in analyses if item.weight_pct <= overweight_limit]
    overweight = tuple(
        item.holding.ticker for item in analyses if item.weight_pct > overweight_limit
    )
    ranked = sorted(eligible, key=lambda item: item.composite_score, reverse=True)
    picks, theme_blocked = pick_top_two(ranked, theme_weights(analyses))
    orders = size_orders(picks, cash)
    return DeploymentPlan(
        orders=orders,
        total_fee=sum(order.fee for order in orders),
        excluded_overweight=overweight,
        excluded_theme=tuple(theme_blocked),
        top_candidates=tuple((item.holding.ticker, item.composite_score) for item in ranked[:6]),
    )
