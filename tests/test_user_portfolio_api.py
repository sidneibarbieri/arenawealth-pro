"""Integration: dashboard portfolio route mounted on main app."""

from fastapi.testclient import TestClient


def test_portfolio_user_returns_payload(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/portfolio/user")
    assert response.status_code == 200
    body = response.json()
    assert "summary" in body
    assert "positions" in body
    assert "analysis" in body
    assert body["summary"]["position_count"] >= 1


def test_health_aggregate_exists(api_client: TestClient) -> None:
    r = api_client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json().get("status") == "healthy"


def test_portfolio_recommendation_offline_demo(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/portfolio/user/recommendation?offline_demo=true")

    assert response.status_code == 200
    body = response.json()
    assert body["provider_mode"] == "offline-demo"
    assert body["orders"]
    assert body["ranked_positions"]
