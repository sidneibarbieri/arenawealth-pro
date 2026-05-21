"""Analytics — moat and compounding scoring with deterministic deployment."""

from arenawealth.analytics.deployment import order_fee, plan_deployment
from arenawealth.analytics.fundamentals import (
    DemoFundamentalsProvider,
    FinnhubFundamentalsProvider,
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
from arenawealth.analytics.workflow import analyze_holdings, fetch_fundamentals

__all__ = [
    "DemoFundamentalsProvider",
    "DeploymentPlan",
    "FMPFundamentalsProvider",
    "FinnhubFundamentalsProvider",
    "Fundamentals",
    "FundamentalsProvider",
    "Holding",
    "Order",
    "PositionAnalysis",
    "YahooFundamentalsProvider",
    "analyze",
    "analyze_holdings",
    "build_fundamentals_provider",
    "fetch_fundamentals",
    "order_fee",
    "plan_deployment",
]
