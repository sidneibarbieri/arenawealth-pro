"""Data Transfer Objects for API layer.

DTOs decouple internal models from API contracts.
All monetary values use Decimal for precision.
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class MoneyDecimal(Decimal):
    """Custom Decimal type for monetary values."""

    @classmethod
    def __get_pydantic_json_schema__(cls, _handler, _info):
        return {"type": "number", "format": "decimal"}

# ============================================================================
# Position DTOs
# ============================================================================

class PositionCreateRequest(BaseModel):
    """Request to create a new position."""

    model_config = ConfigDict(frozen=True)

    ticker: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=200)
    isin: str | None = Field(default=None, max_length=20)
    shares: Decimal = Field(..., gt=0, decimal_places=8)
    average_cost_basis: Decimal = Field(..., gt=0, decimal_places=4)
    current_price: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=4)

class PositionUpdateRequest(BaseModel):
    """Request to update an existing position."""

    model_config = ConfigDict(frozen=True)

    current_price: Decimal | None = Field(default=None, ge=0, decimal_places=4)
    shares: Decimal | None = Field(default=None, gt=0, decimal_places=8)

class PositionResponse(BaseModel):
    """Position data returned by API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    portfolio_id: int
    ticker: str
    name: str
    isin: str | None
    shares: Decimal
    average_cost_basis: Decimal
    current_price: Decimal
    market_value: Decimal
    cost_basis_total: Decimal
    gain_loss: Decimal
    gain_loss_percent: Decimal
    opened_at: datetime
    updated_at: datetime

class PositionSummary(BaseModel):
    """Simplified position for list views."""

    model_config = ConfigDict(from_attributes=True)

    ticker: str
    name: str
    shares: Decimal
    current_price: Decimal
    market_value: Decimal
    gain_loss_percent: Decimal
    weight_percent: Decimal

# ============================================================================
# Portfolio DTOs
# ============================================================================

class PortfolioCreateRequest(BaseModel):
    """Request to create a new portfolio."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    currency: str = Field(default="USD", max_length=3)
    initial_cash: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)

class PortfolioUpdateRequest(BaseModel):
    """Request to update portfolio metadata."""

    model_config = ConfigDict(frozen=True)

    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    available_cash: Decimal | None = Field(default=None, ge=0, decimal_places=2)

class PortfolioResponse(BaseModel):
    """Portfolio data returned by API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    currency: str
    created_at: datetime
    updated_at: datetime
    total_market_value: Decimal
    total_cost_basis: Decimal
    total_gain_loss: Decimal
    available_cash: Decimal
    position_count: int

class PortfolioSummary(BaseModel):
    """Summary for portfolio list views."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    currency: str
    total_market_value: Decimal
    total_gain_loss: Decimal
    position_count: int

# ============================================================================
# Transaction DTOs
# ============================================================================

class TransactionCreateRequest(BaseModel):
    """Request to record a new transaction."""

    model_config = ConfigDict(frozen=True)

    ticker: str = Field(..., min_length=1, max_length=20)
    transaction_type: str = Field(..., pattern="^(BUY|SELL|DIVIDEND|SPLIT)$")
    shares: Decimal = Field(..., gt=0, decimal_places=8)
    price_per_share: Decimal = Field(..., gt=0, decimal_places=4)
    fees: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    broker_order_id: str | None = Field(default=None, max_length=50)
    notes: str | None = Field(default=None, max_length=500)

class TransactionResponse(BaseModel):
    """Transaction data returned by API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    portfolio_id: int
    position_id: int | None
    ticker: str
    transaction_type: str
    shares: Decimal
    price_per_share: Decimal
    total_amount: Decimal
    fees: Decimal
    executed_at: datetime
    broker_order_id: str | None
    notes: str | None

# ============================================================================
# Quote DTOs
# ============================================================================

class QuoteResponse(BaseModel):
    """Current market quote for a security."""

    model_config = ConfigDict(frozen=True)

    ticker: str
    price: Decimal
    change: Decimal
    change_percent: Decimal
    volume: int | None
    high_52_week: Decimal | None
    low_52_week: Decimal | None
    timestamp: datetime

class QuoteHistoryResponse(BaseModel):
    """Historical quote data point."""

    model_config = ConfigDict(from_attributes=True)

    ticker: str
    price: Decimal
    volume: int | None
    change_percent: Decimal | None
    recorded_at: datetime

# ============================================================================
# Analysis DTOs
# ============================================================================

class PortfolioMetrics(BaseModel):
    """Calculated portfolio metrics."""

    model_config = ConfigDict(frozen=True)

    total_value: Decimal
    total_cost: Decimal
    unrealized_gain: Decimal
    unrealized_gain_percent: Decimal
    day_change: Decimal
    day_change_percent: Decimal
    diversification_score: Decimal  # 0-100
    concentration_risk: str  # LOW, MEDIUM, HIGH

class RebalanceSuggestion(BaseModel):
    """Suggestion for portfolio rebalancing."""

    model_config = ConfigDict(frozen=True)

    ticker: str
    current_weight: Decimal
    suggested_weight: Decimal
    action: str  # BUY, SELL, HOLD
    suggested_amount: Decimal
    reason: str

class PortfolioAnalysisResponse(BaseModel):
    """Complete portfolio analysis."""

    model_config = ConfigDict(frozen=True)

    portfolio: PortfolioResponse
    positions: list[PositionResponse]
    metrics: PortfolioMetrics
    rebalance_suggestions: list[RebalanceSuggestion]
    last_updated: datetime
