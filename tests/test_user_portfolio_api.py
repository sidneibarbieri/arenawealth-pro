"""Integration: dashboard portfolio route mounted on main app."""

from fastapi.testclient import TestClient

from arenawealth.api.routers.user_portfolio import build_snapshot


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
        price_lookup=lambda tickers: {ticker: 1234.0 for ticker in tickers},
    )

    assert snapshot.price_source == "live"
    assert snapshot.positions
    assert all(position.current_price == 1234.0 for position in snapshot.positions)


def test_health_aggregate_exists(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json().get("status") == "healthy"


def test_portfolio_recommendation_offline_demo(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/portfolio/user/recommendation?offline_demo=true")

    assert response.status_code == 200
    body = response.json()
    assert body["provider_mode"] == "offline-demo"
    assert body["orders"]
    assert body["ranked_positions"]
