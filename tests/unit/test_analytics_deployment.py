"""Unit tests for the deterministic deployment planner (no network)."""

from arenawealth.analytics.deployment import MIN_ORDER_AMOUNT, order_fee, plan_deployment
from arenawealth.analytics.models import Holding, PositionAnalysis


def make_position(
    ticker: str, composite: float, weight: float, theme: str, price: float = 100.0
) -> PositionAnalysis:
    holding = Holding(ticker, ticker, 1.0, 1.0, price, theme, False)
    return PositionAnalysis(
        holding=holding,
        live_price=price,
        market_value=weight,
        weight_pct=weight,
        pnl_pct=0.0,
        price_gap_pct=0.0,
        roic=None,
        roe=None,
        margin_cv=None,
        revenue_cagr=None,
        eps_cagr=None,
        fcf_cagr=None,
        shares_change=None,
        fcf_yield=None,
        forward_pe=None,
        peg=None,
        moat_class="MODERATE",
        compounding_class="GOOD",
        moat_points=0.0,
        compounding_points=0.0,
        valuation_points=0.0,
        composite_score=composite,
    )


def test_order_fee_tiers():
    assert order_fee(0.0) == 0.0
    assert order_fee(500.0) == 2.50
    assert order_fee(1000.0) == 2.50
    assert order_fee(1000.01) == 5.00
    assert order_fee(1500.0) == 5.00
    assert order_fee(2000.0) == 5.00
    assert order_fee(2001.0) == 7.50


def test_excludes_overweight_and_picks_top_two_distinct_themes():
    positions = [
        make_position("A", 90.0, 30.0, "TA"),
        make_position("B", 80.0, 10.0, "TB"),
        make_position("C", 78.0, 10.0, "TC"),
        make_position("D", 70.0, 10.0, "TD"),
        make_position("E", 60.0, 10.0, "TE"),
    ]

    plan = plan_deployment(positions, 1511.18)

    assert "A" in plan.excluded_overweight
    assert tuple(order.ticker for order in plan.orders) == ("B", "C")
    assert plan.total_fee == 5.00
    assert sum(order.amount for order in plan.orders) == 1511.18
    assert all(order.amount <= 1000.0 for order in plan.orders)
    assert plan.orders[0].amount > plan.orders[1].amount  # higher score gets more


def test_theme_cap_blocks_saturated_theme():
    positions = [
        make_position("A", 90.0, 15.0, "Semis"),
        make_position("B", 85.0, 15.0, "Semis"),  # Semis = 30% >= cap
        make_position("C", 70.0, 10.0, "Pharma"),
        make_position("D", 60.0, 8.0, "Data"),
    ]

    plan = plan_deployment(positions, 1511.18)

    assert tuple(order.ticker for order in plan.orders) == ("C", "D")
    assert "A" in plan.excluded_theme
    assert "B" in plan.excluded_theme


def test_distinct_theme_dedup_under_cap():
    positions = [
        make_position("A", 90.0, 8.0, "Semis"),
        make_position("B", 85.0, 8.0, "Semis"),  # Semis = 16% < cap, still deduped
        make_position("C", 70.0, 8.0, "Pharma"),
    ]

    plan = plan_deployment(positions, 1511.18)

    assert tuple(order.ticker for order in plan.orders) == ("A", "C")
    assert "B" in plan.excluded_theme


def test_two_orders_cost_same_as_one():
    positions = [
        make_position("A", 80.0, 10.0, "TA"),
        make_position("B", 70.0, 10.0, "TB"),
    ]

    plan = plan_deployment(positions, 1511.18)

    assert plan.total_fee == order_fee(1511.18)


def test_does_not_deploy_cash_below_economic_minimum():
    positions = [
        make_position("A", 80.0, 10.0, "TA"),
        make_position("B", 70.0, 10.0, "TB"),
    ]

    plan = plan_deployment(positions, MIN_ORDER_AMOUNT - 0.01)

    assert plan.orders == ()
    assert plan.total_fee == 0.0


def test_uses_one_order_when_cash_cannot_fund_two_economic_orders():
    positions = [
        make_position("A", 80.0, 10.0, "TA"),
        make_position("B", 70.0, 10.0, "TB"),
    ]

    plan = plan_deployment(positions, MIN_ORDER_AMOUNT * 1.5)

    assert tuple(order.ticker for order in plan.orders) == ("A",)
    assert plan.orders[0].amount == MIN_ORDER_AMOUNT * 1.5
