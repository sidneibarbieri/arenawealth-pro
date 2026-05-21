"""Read-only portfolio snapshot used by the dashboard."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel

from arenawealth.analytics import (
    DemoFundamentalsProvider,
    FundamentalsProvider,
    Holding,
    analyze_holdings,
    build_fundamentals_provider,
    plan_deployment,
)
from arenawealth.analytics.universe import FINANCIAL_TICKERS, THEME_BY_TICKER
from arenawealth.domain.position import Position
from arenawealth.importers.csv_importer import import_csv

ROOT = Path(__file__).resolve().parents[4]
PRIVATE_HOLDINGS = ROOT / "data" / "carteira_atual.csv"
FIXTURE_HOLDINGS = ROOT / "tests" / "fixtures" / "seed_portfolio_avenue.csv"

router = APIRouter(
    prefix="/api/v1/portfolio",
    tags=["user-portfolio"],
)


class PositionResponse(BaseModel):
    ticker: str
    name: str
    shares: float
    current_price: float
    cost_basis_per_share: float
    market_value: float
    cost_basis_total: float
    gain_loss: float
    gain_loss_pct: float
    weight_pct: float
    currency: str


class PortfolioSummaryResponse(BaseModel):
    total_market_value: float
    total_cost_basis: float
    total_gain_loss: float
    total_gain_loss_pct: float
    position_count: int
    currency: str


class PortfolioResponse(BaseModel):
    summary: PortfolioSummaryResponse
    positions: list[PositionResponse]
    analysis: dict[str, Any]
    last_updated: str


class RecommendationPositionResponse(BaseModel):
    ticker: str
    theme: str
    weight_pct: float
    moat_class: str
    compounding_class: str
    composite_score: float
    valuation_points: float
    forward_pe: float | None


class RecommendationOrderResponse(BaseModel):
    ticker: str
    amount: float
    shares: float
    fee: float


class RecommendationResponse(BaseModel):
    cash: float
    provider_mode: str
    generated_at: str
    orders: list[RecommendationOrderResponse]
    excluded_overweight: list[str]
    excluded_theme: list[str]
    ranked_positions: list[RecommendationPositionResponse]


def holdings_path() -> Path:
    if PRIVATE_HOLDINGS.exists():
        return PRIVATE_HOLDINGS
    return FIXTURE_HOLDINGS


def load_positions() -> list[Position]:
    return import_csv(holdings_path())


def positions_to_holdings(positions: list[Position]) -> tuple[Holding, ...]:
    return tuple(
        Holding(
            ticker=position.ticker,
            name=position.name,
            shares=float(position.shares),
            average_cost=float(position.cost_basis_per_share),
            broker_price=float(position.current_price),
            theme=THEME_BY_TICKER.get(position.ticker, "Other"),
            is_financial=position.ticker in FINANCIAL_TICKERS,
        )
        for position in positions
    )


def decimal_to_float(value: Decimal) -> float:
    return float(value)


def build_snapshot() -> PortfolioResponse:
    positions = load_positions()
    total_market_value = sum(position.market_value.amount for position in positions)
    total_cost_basis = sum(position.cost_basis_total.amount for position in positions)
    total_gain_loss = total_market_value - total_cost_basis
    total_gain_loss_pct = (
        (total_gain_loss / total_cost_basis * Decimal("100"))
        if total_cost_basis
        else Decimal("0")
    )
    position_rows = [
        PositionResponse(
            ticker=position.ticker,
            name=position.name,
            shares=decimal_to_float(position.shares),
            current_price=decimal_to_float(position.current_price),
            cost_basis_per_share=decimal_to_float(position.cost_basis_per_share),
            market_value=decimal_to_float(position.market_value.amount),
            cost_basis_total=decimal_to_float(position.cost_basis_total.amount),
            gain_loss=decimal_to_float(position.gain_loss.amount),
            gain_loss_pct=decimal_to_float(position.gain_loss_pct),
            weight_pct=decimal_to_float(
                (position.market_value.amount / total_market_value * Decimal("100"))
                if total_market_value
                else Decimal("0")
            ),
            currency=position.currency.value,
        )
        for position in positions
    ]

    return PortfolioResponse(
        summary=PortfolioSummaryResponse(
            total_market_value=decimal_to_float(total_market_value),
            total_cost_basis=decimal_to_float(total_cost_basis),
            total_gain_loss=decimal_to_float(total_gain_loss),
            total_gain_loss_pct=decimal_to_float(total_gain_loss_pct),
            position_count=len(positions),
            currency="USD",
        ),
        positions=position_rows,
        analysis={
            "source": str(holdings_path().relative_to(ROOT)),
            "largest_position": max(position_rows, key=lambda row: row.market_value).ticker
            if position_rows
            else None,
        },
        last_updated=datetime.now(UTC).isoformat(),
    )


def select_recommendation_provider(
    holdings: tuple[Holding, ...], offline_demo: bool
) -> tuple[FundamentalsProvider, str]:
    if offline_demo:
        return DemoFundamentalsProvider(holdings), "offline-demo"
    return build_fundamentals_provider(), "live-auto"


def build_recommendation_response(
    cash: float, offline_demo: bool
) -> RecommendationResponse:
    holdings = positions_to_holdings(load_positions())
    provider, provider_mode = select_recommendation_provider(holdings, offline_demo)
    analyses = analyze_holdings(holdings, provider)
    plan = plan_deployment(analyses, cash)
    ranked = sorted(analyses, key=lambda analysis: analysis.composite_score, reverse=True)
    return RecommendationResponse(
        cash=cash,
        provider_mode=provider_mode,
        generated_at=datetime.now(UTC).isoformat(),
        orders=[
            RecommendationOrderResponse(
                ticker=order.ticker,
                amount=order.amount,
                shares=order.shares,
                fee=order.fee,
            )
            for order in plan.orders
        ],
        excluded_overweight=list(plan.excluded_overweight),
        excluded_theme=list(plan.excluded_theme),
        ranked_positions=[
            RecommendationPositionResponse(
                ticker=analysis.holding.ticker,
                theme=analysis.holding.theme,
                weight_pct=analysis.weight_pct,
                moat_class=analysis.moat_class,
                compounding_class=analysis.compounding_class,
                composite_score=analysis.composite_score,
                valuation_points=analysis.valuation_points,
                forward_pe=analysis.forward_pe,
            )
            for analysis in ranked
        ],
    )


@router.get("/user", response_model=PortfolioResponse)
async def get_user_portfolio() -> PortfolioResponse:
    return build_snapshot()


@router.get("/user/summary", response_model=PortfolioSummaryResponse)
async def get_user_portfolio_summary() -> PortfolioSummaryResponse:
    return build_snapshot().summary


@router.get("/user/positions")
async def get_user_positions() -> dict[str, Any]:
    snapshot = build_snapshot()
    positions = [position.model_dump() for position in snapshot.positions]
    ranked = sorted(positions, key=lambda row: row["market_value"], reverse=True)
    return {
        "positions": positions,
        "top_5_concentration": sum(row["weight_pct"] for row in ranked[:5]),
        "largest_position": ranked[0] if ranked else None,
        "smallest_position": ranked[-1] if ranked else None,
    }


@router.get("/user/analysis")
async def get_user_analysis() -> dict[str, Any]:
    return build_snapshot().analysis


@router.get("/user/recommendation", response_model=RecommendationResponse)
async def get_user_recommendation(
    cash: float = Query(default=1511.18, gt=0),
    offline_demo: bool = Query(default=False),
) -> RecommendationResponse:
    return build_recommendation_response(cash, offline_demo)


@router.get("/user/health")
async def portfolio_health_check() -> dict[str, Any]:
    snapshot = build_snapshot()
    return {
        "status": "healthy",
        "service": "user-portfolio",
        "timestamp": datetime.now(UTC).isoformat(),
        "portfolio_value": snapshot.summary.total_market_value,
        "position_count": snapshot.summary.position_count,
        "last_updated": snapshot.last_updated,
    }
