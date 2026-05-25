"""Read-only portfolio snapshot used by the dashboard."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel
from sqlmodel import select

from arenawealth.analytics import (
    DemoFundamentalsProvider,
    FundamentalsProvider,
    Holding,
    PortfolioReview,
    analyze_holdings,
    build_fundamentals_provider,
    plan_deployment,
    review_portfolio,
    screen_candidates,
)
from arenawealth.analytics.universe import (
    CANDIDATE_UNIVERSE,
    FINANCIAL_TICKERS,
    THEME_BY_TICKER,
)
from arenawealth.domain.position import Position
from arenawealth.importers.csv_importer import import_csv
from arenawealth.importers.holdings_source import ROOT, resolve_holdings_path
from arenawealth.models.database import QuoteHistory, get_session
from arenawealth.providers.yahoo import YahooProvider

QUOTE_CACHE_TTL = timedelta(minutes=15)

router = APIRouter(
    prefix="/api/v1/portfolio",
    tags=["user-portfolio"],
)


class PositionResponse(BaseModel):
    ticker: str
    name: str
    shares: float
    current_price: float
    change_pct: float | None = None
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
    price_source: str
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


class CandidateResponse(BaseModel):
    ticker: str
    name: str
    theme: str
    live_price: float
    moat_class: str
    compounding_class: str
    composite_score: float
    valuation_points: float
    forward_pe: float | None
    roic: float | None


class ReviewAdditionResponse(BaseModel):
    ticker: str
    name: str
    theme: str
    composite_score: float
    reason: str


class ReviewReplacementResponse(BaseModel):
    current_ticker: str
    candidate_ticker: str
    candidate_name: str
    score_gap: float
    reason: str


class ReviewTrimResponse(BaseModel):
    ticker: str
    weight_pct: float
    composite_score: float
    reason: str


class PortfolioReviewResponse(BaseModel):
    current_positions: int
    target_min_positions: int
    target_max_positions: int
    additions_needed: int
    add_candidates: list[ReviewAdditionResponse]
    replacement_watch: list[ReviewReplacementResponse]
    trim_watch: list[ReviewTrimResponse]


class CandidatesResponse(BaseModel):
    provider_mode: str
    generated_at: str
    review: PortfolioReviewResponse
    candidates: list[CandidateResponse]


def holdings_path() -> Path:
    return resolve_holdings_path()


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


@dataclass(frozen=True)
class LiveQuote:
    price: float
    change_pct: float | None


def fetch_live_quotes(tickers: list[str]) -> dict[str, LiveQuote]:
    tickers = sorted({ticker.upper() for ticker in tickers})
    cached = read_cached_quotes(tickers, max_age=QUOTE_CACHE_TTL)
    missing = [ticker for ticker in tickers if ticker not in cached]
    if not missing:
        return cached

    try:
        fresh = fetch_remote_quotes(missing)
    except Exception:
        stale = read_cached_quotes(missing, max_age=None)
        if stale:
            return {**cached, **stale}
        raise

    write_cached_quotes(fresh)
    return {**cached, **fresh}


def fetch_remote_quotes(tickers: list[str]) -> dict[str, LiveQuote]:
    quotes = YahooProvider().get_quotes(tickers)
    return {
        quote.ticker: LiveQuote(
            price=float(quote.price),
            change_pct=float(quote.change_pct) if quote.change_pct is not None else None,
        )
        for quote in quotes
    }


def read_cached_quotes(
    tickers: list[str],
    max_age: timedelta | None,
) -> dict[str, LiveQuote]:
    if not tickers:
        return {}

    cutoff = datetime.now(UTC).replace(tzinfo=None) - max_age if max_age else None
    cached: dict[str, LiveQuote] = {}
    with get_session() as session:
        for ticker in tickers:
            statement = (
                select(QuoteHistory)
                .where(QuoteHistory.ticker == ticker)
                .order_by(QuoteHistory.recorded_at.desc())
                .limit(1)
            )
            row = session.exec(statement).first()
            if row is None:
                continue
            if cutoff and row.recorded_at < cutoff:
                continue
            cached[ticker] = LiveQuote(
                price=float(row.price),
                change_pct=float(row.change_percent) if row.change_percent is not None else None,
            )
    return cached


def write_cached_quotes(quotes: dict[str, LiveQuote]) -> None:
    if not quotes:
        return

    with get_session() as session:
        for ticker, quote in quotes.items():
            session.add(
                QuoteHistory(
                    ticker=ticker.upper(),
                    price=Decimal(str(quote.price)),
                    change_percent=(
                        Decimal(str(quote.change_pct)) if quote.change_pct is not None else None
                    ),
                )
            )
        session.commit()


def build_snapshot(
    live: bool = True,
    quote_lookup: Callable[[list[str]], dict[str, LiveQuote]] | None = None,
) -> PortfolioResponse:
    positions = load_positions()
    quotes: dict[str, LiveQuote] = {}
    if live:
        lookup = quote_lookup or fetch_live_quotes
        quotes = lookup([position.ticker for position in positions])
    price_source = "live" if quotes else "stored"

    def price_of(position: Position) -> Decimal:
        quote = quotes.get(position.ticker)
        return Decimal(str(quote.price)) if quote else position.current_price

    total_market_value = sum(position.shares * price_of(position) for position in positions)
    total_cost_basis = sum(position.cost_basis_total.amount for position in positions)
    total_gain_loss = total_market_value - total_cost_basis
    total_gain_loss_pct = (
        (total_gain_loss / total_cost_basis * Decimal("100"))
        if total_cost_basis
        else Decimal("0")
    )

    position_rows = []
    for position in positions:
        price = price_of(position)
        quote = quotes.get(position.ticker)
        market_value = position.shares * price
        cost_basis_total = position.cost_basis_total.amount
        gain_loss = market_value - cost_basis_total
        position_rows.append(
            PositionResponse(
                ticker=position.ticker,
                name=position.name,
                shares=decimal_to_float(position.shares),
                current_price=decimal_to_float(price),
                change_pct=quote.change_pct if quote else None,
                cost_basis_per_share=decimal_to_float(position.cost_basis_per_share),
                market_value=decimal_to_float(market_value),
                cost_basis_total=decimal_to_float(cost_basis_total),
                gain_loss=decimal_to_float(gain_loss),
                gain_loss_pct=decimal_to_float(
                    (gain_loss / cost_basis_total * Decimal("100"))
                    if cost_basis_total
                    else Decimal("0")
                ),
                weight_pct=decimal_to_float(
                    (market_value / total_market_value * Decimal("100"))
                    if total_market_value
                    else Decimal("0")
                ),
                currency=position.currency.value,
            )
        )

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
        price_source=price_source,
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


def review_to_response(review: PortfolioReview) -> PortfolioReviewResponse:
    return PortfolioReviewResponse(
        current_positions=review.current_positions,
        target_min_positions=review.target_min_positions,
        target_max_positions=review.target_max_positions,
        additions_needed=review.additions_needed,
        add_candidates=[
            ReviewAdditionResponse(
                ticker=item.ticker,
                name=item.name,
                theme=item.theme,
                composite_score=item.composite_score,
                reason=item.reason,
            )
            for item in review.add_candidates
        ],
        replacement_watch=[
            ReviewReplacementResponse(
                current_ticker=item.current_ticker,
                candidate_ticker=item.candidate_ticker,
                candidate_name=item.candidate_name,
                score_gap=item.score_gap,
                reason=item.reason,
            )
            for item in review.replacement_watch
        ],
        trim_watch=[
            ReviewTrimResponse(
                ticker=item.ticker,
                weight_pct=item.weight_pct,
                composite_score=item.composite_score,
                reason=item.reason,
            )
            for item in review.trim_watch
        ],
    )


@router.get("/user", response_model=PortfolioResponse)
async def get_user_portfolio(live: bool = Query(default=True)) -> PortfolioResponse:
    return build_snapshot(live=live)


@router.get("/user/summary", response_model=PortfolioSummaryResponse)
async def get_user_portfolio_summary(live: bool = Query(default=True)) -> PortfolioSummaryResponse:
    return build_snapshot(live=live).summary


@router.get("/user/positions")
async def get_user_positions(live: bool = Query(default=True)) -> dict[str, Any]:
    snapshot = build_snapshot(live=live)
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
    return build_snapshot(live=False).analysis


@router.get("/user/recommendation", response_model=RecommendationResponse)
async def get_user_recommendation(
    cash: float = Query(default=1511.18, gt=0),
    offline_demo: bool = Query(default=False),
) -> RecommendationResponse:
    return build_recommendation_response(cash, offline_demo)


def candidate_holdings() -> tuple[Holding, ...]:
    return tuple(
        Holding(ticker, name, 1.0, 100.0, 100.0, theme, False)
        for ticker, (name, theme) in CANDIDATE_UNIVERSE.items()
    )


def build_candidates_response(offline_demo: bool, limit: int) -> CandidatesResponse:
    holdings = positions_to_holdings(load_positions())
    owned = [holding.ticker for holding in holdings]
    if offline_demo:
        provider: FundamentalsProvider = DemoFundamentalsProvider(
            holdings + candidate_holdings()
        )
        provider_mode = "offline-demo"
    else:
        provider = build_fundamentals_provider()
        provider_mode = "live-auto"
    held_analyses = analyze_holdings(holdings, provider)
    candidates = screen_candidates(provider, owned=owned)[:limit]
    review = review_portfolio(held_analyses, candidates)
    return CandidatesResponse(
        provider_mode=provider_mode,
        generated_at=datetime.now(UTC).isoformat(),
        review=review_to_response(review),
        candidates=[
            CandidateResponse(
                ticker=candidate.ticker,
                name=candidate.name,
                theme=candidate.theme,
                live_price=candidate.live_price,
                moat_class=candidate.score.moat_class,
                compounding_class=candidate.score.compounding_class,
                composite_score=candidate.score.composite_score,
                valuation_points=candidate.score.valuation_points,
                forward_pe=candidate.score.forward_pe,
                roic=candidate.score.roic,
            )
            for candidate in candidates
        ],
    )


@router.get("/user/candidates", response_model=CandidatesResponse)
async def get_user_candidates(
    offline_demo: bool = Query(default=False),
    limit: int = Query(default=10, gt=0, le=50),
) -> CandidatesResponse:
    return build_candidates_response(offline_demo, limit)


@router.get("/user/health")
async def portfolio_health_check() -> dict[str, Any]:
    snapshot = build_snapshot(live=False)
    return {
        "status": "healthy",
        "service": "user-portfolio",
        "timestamp": datetime.now(UTC).isoformat(),
        "portfolio_value": snapshot.summary.total_market_value,
        "position_count": snapshot.summary.position_count,
        "last_updated": snapshot.last_updated,
    }
