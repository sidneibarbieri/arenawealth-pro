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
    FundamentalScore,
    Holding,
    Order,
    PositionAnalysis,
)
from arenawealth.analytics.scoring import analyze, score_fundamentals
from arenawealth.analytics.screening import CandidateAnalysis, screen_candidates
from arenawealth.analytics.workflow import analyze_holdings, fetch_fundamentals

__all__ = [
    "CandidateAnalysis",
    "DemoFundamentalsProvider",
    "DeploymentPlan",
    "FMPFundamentalsProvider",
    "FinnhubFundamentalsProvider",
    "FundamentalScore",
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
    "score_fundamentals",
    "screen_candidates",
]
