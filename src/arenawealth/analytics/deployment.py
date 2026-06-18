"""Deterministic, fee-aware cash deployment.

This module implements a fee-optimal cash allocation strategy that respects:
1. Concentration limits: positions above 1.3x equal weight are ineligible.
2. Fee efficiency: splits are only diversified when fee-neutral.
3. Theme diversification: top two picks are from distinct themes.
4. Determinism: ties broken by ticker for reproducible ordering.

The key insight is Proposition "Sub-tranche fee-worsening": naive proportional
splits in the range [$625, $1000] incur an extra tranche fee. The fix ensures
diversification only when fee-neutral, keeping the planner on the optimal
frontier everywhere it deploys (see CORRECTIONS.md).
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from arenawealth.analytics.models import DeploymentPlan, Order, PositionAnalysis


@dataclass(frozen=True)
class FeeParameters:
    """Immutable fee model constants.

    Broker charges a fixed cost per started tranche of size T in a single-symbol
    order. A partially used tranche is billed in full (ceiling, not floor).
    """

    tranche_size_usd: float = 1000.0
    fee_per_tranche_usd: float = 2.50
    max_fee_impact_pct: float = 1.0

    @property
    def min_order_amount_usd(self) -> float:
        """Economic order floor: minimum cash where fee impact is tolerable."""
        return self.fee_per_tranche_usd / (self.max_fee_impact_pct / 100)


@dataclass(frozen=True)
class ConcentrationLimits:
    """Portfolio concentration rules."""

    overweight_multiple: float = 1.3
    theme_concentration_cap_pct: float = 20.0


def compute_order_fee(amount_usd: float, fee_params: FeeParameters) -> float:
    """Compute broker fee for a single order.

    Args:
        amount_usd: Order size in USD.
        fee_params: Fee model configuration.

    Returns:
        Fee amount in USD, rounded up to nearest tranche.
    """
    if amount_usd <= 0:
        return 0.0
    tranches_used = math.ceil(amount_usd / fee_params.tranche_size_usd)
    return tranches_used * fee_params.fee_per_tranche_usd


def compute_theme_weights(
    analyses: Sequence[PositionAnalysis],
) -> dict[str, float]:
    """Aggregate portfolio weight by theme.

    Args:
        analyses: Current position analyses.

    Returns:
        Mapping from theme to cumulative weight percentage.
    """
    theme_weight_map: dict[str, float] = {}
    for analysis in analyses:
        theme = analysis.holding.theme
        theme_weight_map[theme] = theme_weight_map.get(theme, 0.0) + analysis.weight_pct
    return theme_weight_map


def select_eligible_for_purchase(
    ranked_analyses: Sequence[PositionAnalysis],
    theme_weights: dict[str, float],
    concentration_limits: ConcentrationLimits,
    max_picks: int = 2,
) -> tuple[list[PositionAnalysis], list[str]]:
    """Select top candidates respecting theme and concentration rules.

    Args:
        ranked_analyses: Candidates sorted by composite score (descending).
        theme_weights: Current weight by theme.
        concentration_limits: Portfolio rules.
        max_picks: Maximum candidates to select (typically 2 for fee efficiency).

    Returns:
        Tuple of (selected analyses, blocked ticker symbols).
    """
    selected_picks: list[PositionAnalysis] = []
    blocked_tickers: list[str] = []
    used_themes: set[str] = set()

    for analysis in ranked_analyses:
        if len(selected_picks) >= max_picks:
            break

        theme = analysis.holding.theme
        is_theme_saturated = (
            theme_weights.get(theme, 0.0) >= concentration_limits.theme_concentration_cap_pct
        )
        is_theme_used = theme in used_themes

        if is_theme_saturated or is_theme_used:
            blocked_tickers.append(analysis.holding.ticker)
            continue

        selected_picks.append(analysis)
        used_themes.add(theme)

    return selected_picks, blocked_tickers


def build_single_order(
    analysis: PositionAnalysis,
    amount_usd: float,
    fee_params: FeeParameters,
) -> Order:
    """Create a buy order for a single security.

    Args:
        analysis: Position analysis with current price.
        amount_usd: Dollar amount to allocate.
        fee_params: Fee model.

    Returns:
        Order with computed shares and fee.
    """
    fee_usd = compute_order_fee(amount_usd, fee_params)
    shares = amount_usd / analysis.live_price
    return Order(
        ticker=analysis.holding.ticker,
        amount=amount_usd,
        shares=shares,
        fee=fee_usd,
    )


def compute_score_based_split(
    first_analysis: PositionAnalysis,
    second_analysis: PositionAnalysis,
    total_cash_usd: float,
) -> tuple[float, float]:
    """Allocate cash between two securities by score share.

    Args:
        first_analysis: Primary candidate.
        second_analysis: Secondary candidate.
        total_cash_usd: Total budget to split.

    Returns:
        Tuple of (first_amount_usd, second_amount_usd) summing to total_cash_usd.
    """
    total_score = first_analysis.composite_score + second_analysis.composite_score
    first_fraction = first_analysis.composite_score / total_score
    first_amount = total_cash_usd * first_fraction
    second_amount = total_cash_usd - first_amount
    return first_amount, second_amount


def is_split_fee_neutral(
    split_orders: Sequence[Order],
    single_order: Order,
) -> bool:
    """Check if a multi-order split incurs the same total fee as consolidation.

    By Proposition k-way fee-neutrality, a split is fee-neutral iff the sum
    of tranche counts equals the single-order tranche count. Splits are only
    viable when fee-neutral; otherwise, consolidation is cost-efficient.

    Args:
        split_orders: Multi-order split.
        single_order: Consolidated single-order alternative.

    Returns:
        True if split fee equals single-order fee.
    """
    split_fee_total = sum(order.fee for order in split_orders)
    return split_fee_total <= single_order.fee


def size_orders_for_cash(
    candidates: Sequence[PositionAnalysis],
    cash_usd: float,
    fee_params: FeeParameters,
) -> tuple[Order, ...]:
    """Size orders to deploy cash while maintaining fee efficiency.

    Implements the latent-defect fix: diversifies only when fee-neutral.
    For sub-tranche cash ($250-$1000), naive proportional splits incur an
    extra fee. This function aligns splits to fee-optimal boundaries.

    Args:
        candidates: Eligible positions ranked by score.
        cash_usd: Available cash to deploy.
        fee_params: Fee model with floor and tranche sizes.

    Returns:
        Tuple of orders. Typically 0 (insufficient), 1 (single), or 2 (split).
    """
    min_order = fee_params.min_order_amount_usd

    if not candidates or cash_usd < min_order:
        return ()

    single_order = build_single_order(candidates[0], cash_usd, fee_params)

    if len(candidates) < 2 or cash_usd < min_order * 2:
        return (single_order,)

    first_amount, second_amount = compute_score_based_split(
        candidates[0], candidates[1], cash_usd
    )

    if first_amount < min_order or second_amount < min_order:
        return (single_order,)

    first_order = build_single_order(candidates[0], first_amount, fee_params)
    second_order = build_single_order(candidates[1], second_amount, fee_params)
    split_orders = (first_order, second_order)

    if not is_split_fee_neutral(split_orders, single_order):
        return (single_order,)

    return split_orders


def plan_deployment(
    analyses: Sequence[PositionAnalysis],
    cash_usd: float,
    fee_params: FeeParameters | None = None,
    concentration_limits: ConcentrationLimits | None = None,
) -> DeploymentPlan:
    """Generate a deterministic, fee-efficient cash deployment plan.

    Args:
        analyses: Current portfolio position analyses.
        cash_usd: Available cash to deploy.
        fee_params: Fee model (uses defaults if None).
        concentration_limits: Portfolio rules (uses defaults if None).

    Returns:
        Deployment plan with orders, fees, and exclusion reasons.

    Raises:
        ValueError: If analyses is empty.
    """
    if not analyses:
        raise ValueError("analyses cannot be empty")

    fee_params = fee_params or FeeParameters()
    concentration_limits = concentration_limits or ConcentrationLimits()

    equal_weight_pct = 100.0 / len(analyses)
    overweight_threshold = equal_weight_pct * concentration_limits.overweight_multiple

    eligible_analyses = [
        analysis
        for analysis in analyses
        if analysis.weight_pct <= overweight_threshold
    ]
    overweight_tickers = tuple(
        analysis.holding.ticker
        for analysis in analyses
        if analysis.weight_pct > overweight_threshold
    )

    ranked_by_score = sorted(
        eligible_analyses,
        key=lambda analysis: (-analysis.composite_score, analysis.holding.ticker),
    )

    theme_weights_map = compute_theme_weights(analyses)
    candidates, theme_blocked_tickers = select_eligible_for_purchase(
        ranked_by_score, theme_weights_map, concentration_limits
    )

    orders = size_orders_for_cash(candidates, cash_usd, fee_params)

    top_six_candidates = tuple(
        (analysis.holding.ticker, analysis.composite_score)
        for analysis in ranked_by_score[:6]
    )

    return DeploymentPlan(
        orders=orders,
        total_fee=sum(order.fee for order in orders),
        excluded_overweight=overweight_tickers,
        excluded_theme=tuple(theme_blocked_tickers),
        top_candidates=top_six_candidates,
    )


# ===== Backwards Compatibility Layer (Deprecated) =====
_default_fee_params = FeeParameters()
MIN_ORDER_AMOUNT: float = _default_fee_params.min_order_amount_usd
TRANCHE_SIZE: float = _default_fee_params.tranche_size_usd
FEE_PER_TRANCHE: float = _default_fee_params.fee_per_tranche_usd
OVERWEIGHT_MULTIPLE: float = ConcentrationLimits().overweight_multiple
THEME_CONCENTRATION_CAP: float = ConcentrationLimits().theme_concentration_cap_pct
MAX_FEE_PCT: float = _default_fee_params.max_fee_impact_pct


def order_fee(amount: float) -> float:
    """Deprecated: use compute_order_fee with FeeParameters instead."""
    return compute_order_fee(amount, _default_fee_params)


def theme_weights(analyses: Sequence[PositionAnalysis]) -> dict[str, float]:
    """Deprecated: use compute_theme_weights instead."""
    return compute_theme_weights(analyses)


def pick_top_two(
    ranked: Sequence[PositionAnalysis], theme_weight: dict[str, float]
) -> tuple[list[PositionAnalysis], list[str]]:
    """Deprecated: use select_eligible_for_purchase instead."""
    concentration_limits = ConcentrationLimits()
    return select_eligible_for_purchase(ranked, theme_weight, concentration_limits, max_picks=2)


def build_order(analysis: PositionAnalysis, amount: float) -> Order:
    """Deprecated: use build_single_order instead."""
    return build_single_order(analysis, amount, _default_fee_params)


def size_orders(picks: Sequence[PositionAnalysis], cash: float) -> tuple[Order, ...]:
    """Deprecated: use size_orders_for_cash instead."""
    return size_orders_for_cash(picks, cash, _default_fee_params)
