"""API routers for resource endpoints."""

from arenawealth.api.routers.portfolios import router as portfolios_router
from arenawealth.api.routers.positions import router as positions_router
from arenawealth.api.routers.transactions import router as transactions_router
from arenawealth.api.routers.user_portfolio import router as user_portfolio_router

__all__ = [
    "portfolios_router",
    "positions_router",
    "transactions_router",
    "user_portfolio_router",
]
