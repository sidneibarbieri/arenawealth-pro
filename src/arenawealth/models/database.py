"""Database models and connection management.

Uses SQLModel for ORM with SQLite backend.
Follows repository pattern for data access.
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import event
from sqlmodel import Field, Session, SQLModel, create_engine

# Database configuration
DATABASE_URL = "sqlite:///./arenawealth.db"
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)

class Portfolio(SQLModel, table=True):
    """Portfolio entity - represents a user's investment portfolio."""

    __tablename__ = "portfolios"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str | None = None
    currency: str = Field(default="USD")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Cached totals (recalculated on position changes)
    total_market_value: Decimal = Field(default=Decimal("0"))
    total_cost_basis: Decimal = Field(default=Decimal("0"))
    available_cash: Decimal = Field(default=Decimal("0"))

class Position(SQLModel, table=True):
    """Position entity - represents a holding in a specific security."""

    __tablename__ = "positions"

    id: int | None = Field(default=None, primary_key=True)
    portfolio_id: int = Field(foreign_key="portfolios.id", index=True)

    # Security identification
    ticker: str = Field(index=True)
    name: str
    isin: str | None = None

    # Position data
    shares: Decimal = Field(decimal_places=8)
    average_cost_basis: Decimal = Field(decimal_places=4)
    current_price: Decimal = Field(default=Decimal("0"), decimal_places=4)

    # Timestamps
    opened_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def market_value(self) -> Decimal:
        """Calculate current market value."""
        return self.shares * self.current_price

    @property
    def cost_basis_total(self) -> Decimal:
        """Calculate total cost basis."""
        return self.shares * self.average_cost_basis

    @property
    def gain_loss(self) -> Decimal:
        """Calculate unrealized gain/loss."""
        return self.market_value - self.cost_basis_total

    @property
    def gain_loss_percent(self) -> Decimal:
        """Calculate gain/loss percentage."""
        if self.cost_basis_total == 0:
            return Decimal("0")
        return (self.gain_loss / self.cost_basis_total) * 100

class Transaction(SQLModel, table=True):
    """Transaction entity - records buy/sell operations."""

    __tablename__ = "transactions"

    id: int | None = Field(default=None, primary_key=True)
    portfolio_id: int = Field(foreign_key="portfolios.id", index=True)
    position_id: int | None = Field(foreign_key="positions.id")

    # Transaction details
    ticker: str = Field(index=True)
    transaction_type: str  # 'BUY', 'SELL', 'DIVIDEND', 'SPLIT'
    shares: Decimal = Field(decimal_places=8)
    price_per_share: Decimal = Field(decimal_places=4)
    total_amount: Decimal = Field(decimal_places=2)
    fees: Decimal = Field(default=Decimal("0"), decimal_places=2)

    # Metadata
    executed_at: datetime = Field(default_factory=datetime.utcnow)
    broker_order_id: str | None = None
    notes: str | None = None

class QuoteHistory(SQLModel, table=True):
    """Quote history - stores historical prices for analytics."""

    __tablename__ = "quote_history"

    id: int | None = Field(default=None, primary_key=True)
    ticker: str = Field(index=True)
    price: Decimal = Field(decimal_places=4)
    volume: int | None = None
    change_percent: Decimal | None = Field(default=None, decimal_places=4)
    recorded_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # 52-week data
    high_52_week: Decimal | None = Field(default=None, decimal_places=4)
    low_52_week: Decimal | None = Field(default=None, decimal_places=4)

def init_database() -> None:
    """Initialize database schema.

    Creates all tables if they don't exist.
    """
    SQLModel.metadata.create_all(engine)

def get_session() -> Session:
    """Get a database session.

    Returns:
        Session: SQLModel session for database operations.
    """
    return Session(engine)

# Event listeners for automatic timestamp updates
@event.listens_for(Portfolio, "before_update")
def update_portfolio_timestamp(mapper, connection, target):
    """Auto-update portfolio timestamp on modification."""
    target.updated_at = datetime.utcnow()

@event.listens_for(Position, "before_update")
def update_position_timestamp(mapper, connection, target):
    """Auto-update position timestamp on modification."""
    target.updated_at = datetime.utcnow()
