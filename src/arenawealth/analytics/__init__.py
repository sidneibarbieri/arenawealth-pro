"""Analytics — moat and compounding scoring with deterministic deployment."""

from arenawealth.analytics.deployment import order_fee, plan_deployment
from arenawealth.analytics.fundamentals import (
    FMPFundamentalsProvider,
    FundamentalsProvider,
    YahooFundamentalsProvider,
    build_fundamentals_provider,
)
from arenawealth.analytics.models import (
    DeploymentPlan,
    Fundamentals,
    Holding,
    Order,
    PositionAnalysis,
)
from arenawealth.analytics.scoring import analyze

__all__ = [
    "DeploymentPlan",
    "FMPFundamentalsProvider",
    "Fundamentals",
    "FundamentalsProvider",
    "Holding",
    "Order",
    "PositionAnalysis",
    "YahooFundamentalsProvider",
    "analyze",
    "build_fundamentals_provider",
    "order_fee",
    "plan_deployment",
]
