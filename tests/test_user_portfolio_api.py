"""Integration: dashboard portfolio route mounted on main app."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from fastapi.testclient import TestClient

from arenawealth.api.routers.user_portfolio import (
    LiveQuote,
    build_snapshot,
    read_cached_quotes,
    write_cached_quotes,
)
from arenawealth.models.database import QuoteHistory, get_session


def test_portfolio_user_returns_payload(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/portfolio/user?live=false")
    assert response.status_code == 200
    body = response.json()
    assert "summary" in body
    assert "positions" in body
    assert "analysis" in body
    assert body["price_source"] == "stored"
    assert body["summary"]["position_count"] >= 1


def test_build_snapshot_overlays_live_prices() -> None:
    snapshot = build_snapshot(
        live=True,
        quote_lookup=lambda tickers: {ticker: LiveQuote(1234.0, 1.5) for ticker in tickers},
    )

    assert snapshot.price_source == "live"
    assert snapshot.positions
    assert all(position.current_price == 1234.0 for position in snapshot.positions)
    assert all(position.change_pct == 1.5 for position in snapshot.positions)


def test_quote_cache_round_trip(api_client: TestClient) -> None:
    write_cached_quotes({"AAPL": LiveQuote(price=123.45, change_pct=1.2)})

    quotes = read_cached_quotes(["AAPL"], max_age=timedelta(minutes=15))

    assert quotes["AAPL"] == LiveQuote(price=123.45, change_pct=1.2)


def test_quote_cache_respects_ttl(api_client: TestClient) -> None:
    with get_session() as session:
        session.add(
            QuoteHistory(
                ticker="MSFT",
                price=Decimal("300.00"),
                change_percent=Decimal("0.5"),
                recorded_at=datetime.now(UTC).replace(tzinfo=None) - timedelta(days=1),
            )
        )
        session.commit()

    quotes = read_cached_quotes(["MSFT"], max_age=timedelta(minutes=15))

    assert quotes == {}


def test_health_aggregate_exists(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json().get("status") == "healthy"


def test_provider_status_never_returns_secret_values(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/providers/status")

    assert response.status_code == 200
    body = response.json()
    assert body
    assert {provider["provider_id"] for provider in body} >= {"yahoo", "sec_edgar"}
    assert all("api_key" not in provider for provider in body)
    assert all("configured" in provider for provider in body)


def test_data_sources_health_config_mode_hides_secret_values(
    api_client: TestClient,
) -> None:
    response = api_client.get("/api/v1/data-sources/health")

    assert response.status_code == 200
    body = response.json()
    assert body["live"] is False
    assert body["sources"]
    assert all("api_key" not in source for source in body["sources"])
    assert all(source["status"] in {"configured", "not_configured"} for source in body["sources"])


def test_portfolio_recommendation_offline_demo(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/portfolio/user/recommendation?offline_demo=true")

    assert response.status_code == 200
    body = response.json()
    assert body["provider_mode"] == "offline-demo"
    assert body["orders"]
    assert body["ranked_positions"]


def test_portfolio_candidates_offline_demo(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/portfolio/user/candidates?offline_demo=true&limit=5")

    assert response.status_code == 200
    body = response.json()
    assert body["provider_mode"] == "offline-demo"
    assert body["review"]["current_positions"] >= 1
    assert body["review"]["target_min_positions"] == 18
    assert 1 <= len(body["candidates"]) <= 5
    scores = [candidate["composite_score"] for candidate in body["candidates"]]
    assert scores == sorted(scores, reverse=True)
