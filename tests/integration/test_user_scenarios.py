"""Automated API user scenarios.

Scenario map:
- Operator: checks that the API is alive.
- Investor snapshot: reads the dashboard portfolio data under ``data/``.
- Investor persistence: creates a portfolio, adds positions, and checks errors.

Each test uses an isolated SQLite database through the ``api_client`` fixture.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration

# --- Operator -----------------------------------------------------------------


def test_scenario_operator_health(api_client: TestClient) -> None:
    """GET /api/v1/health returns an ok status."""
    r = api_client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


# --- Investor snapshot ---------------------------------------------------------


def test_scenario_dashboard_portfolio_snapshot(api_client: TestClient) -> None:
    """The dashboard can read the aggregate portfolio snapshot."""
    r = api_client.get("/api/v1/portfolio/user")
    assert r.status_code == 200
    body = r.json()
    assert body["summary"]["position_count"] >= 1
    assert isinstance(body["positions"], list)


def test_scenario_dashboard_portfolio_summary_only(api_client: TestClient) -> None:
    """The dashboard can read summary totals only."""
    r = api_client.get("/api/v1/portfolio/user/summary")
    assert r.status_code == 200
    assert "total_market_value" in r.json()


def test_scenario_dashboard_user_health_sub(api_client: TestClient) -> None:
    """The user portfolio snapshot service exposes health status."""
    r = api_client.get("/api/v1/portfolio/user/health")
    assert r.status_code == 200
    assert r.json().get("status") == "healthy"


# --- Investor CRUD -------------------------------------------------------------


def test_scenario_create_list_get_portfolio(api_client: TestClient) -> None:
    """Create a portfolio, list portfolios, and fetch it by id."""
    created = api_client.post(
        "/api/v1/portfolios",
        json={"name": "Test Portfolio", "currency": "USD", "initial_cash": "10000.00"},
    )
    assert created.status_code == 201
    pid = created.json()["id"]

    listed = api_client.get("/api/v1/portfolios")
    assert listed.status_code == 200
    assert any(p["id"] == pid for p in listed.json())

    one = api_client.get(f"/api/v1/portfolios/{pid}")
    assert one.status_code == 200
    assert one.json()["name"] == "Test Portfolio"


def test_scenario_add_position_and_list(api_client: TestClient) -> None:
    """Add a position and list the portfolio positions."""
    r = api_client.post(
        "/api/v1/portfolios",
        json={"name": "With Positions", "currency": "USD", "initial_cash": "50000.00"},
    )
    assert r.status_code == 201
    pid = r.json()["id"]

    pos = api_client.post(
        f"/api/v1/portfolios/{pid}/positions",
        json={
            "ticker": "AAPL",
            "name": "Apple Inc",
            "shares": "10",
            "average_cost_basis": "150.0000",
            "current_price": "175.0000",
        },
    )
    assert pos.status_code == 201
    assert pos.json()["ticker"] == "AAPL"

    rows = api_client.get(f"/api/v1/portfolios/{pid}/positions")
    assert rows.status_code == 200
    assert len(rows.json()) == 1
    assert rows.json()[0]["ticker"] == "AAPL"


def test_scenario_portfolio_analysis_empty_positions(api_client: TestClient) -> None:
    """Portfolio analysis works without network access for an empty portfolio."""
    r = api_client.post(
        "/api/v1/portfolios",
        json={"name": "Analyze Me", "currency": "USD", "initial_cash": "0"},
    )
    assert r.status_code == 201
    pid = r.json()["id"]

    ar = api_client.get(f"/api/v1/portfolios/{pid}/analysis")
    assert ar.status_code == 200
    body = ar.json()
    assert "metrics" in body
    assert body["metrics"]["total_value"] is not None


# --- Expected errors -----------------------------------------------------------


def test_scenario_unknown_portfolio_404(api_client: TestClient) -> None:
    """Unknown portfolio ids return 404."""
    r = api_client.get("/api/v1/portfolios/999999")
    assert r.status_code == 404


def test_scenario_duplicate_ticker_conflict(api_client: TestClient) -> None:
    """A duplicate ticker in the same portfolio returns a conflict."""
    r = api_client.post(
        "/api/v1/portfolios",
        json={"name": "Dup", "currency": "USD", "initial_cash": "100000"},
    )
    pid = r.json()["id"]
    payload = {
        "ticker": "MSFT",
        "name": "Microsoft",
        "shares": "1",
        "average_cost_basis": "300.0000",
        "current_price": "310.0000",
    }
    assert api_client.post(f"/api/v1/portfolios/{pid}/positions", json=payload).status_code == 201
    second = api_client.post(f"/api/v1/portfolios/{pid}/positions", json=payload)
    assert second.status_code == 409


def test_scenario_invalid_body_validation(api_client: TestClient) -> None:
    """Invalid request bodies return validation errors."""
    r = api_client.post("/api/v1/portfolios", json={"name": ""})
    assert r.status_code == 422
