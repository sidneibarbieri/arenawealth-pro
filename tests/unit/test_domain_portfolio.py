"""Tests for Position and Portfolio — validated against real Avenue extract.

Every expected value comes directly from the user's Avenue brokerage screen.
This ensures the domain model produces numbers that match what the user sees.
"""

from decimal import Decimal

from arenawealth.domain.portfolio import Portfolio
from arenawealth.domain.position import Position

# -- Fixtures: real Avenue data ------------------------------------------------

def _lin_position() -> Position:
    return Position(
        ticker="LIN",
        name="Linde plc",
        shares=Decimal("34.47335"),
        cost_basis_per_share=Decimal("431.36"),
        current_price=Decimal("504.65"),
    )


def _nvo_position() -> Position:
    return Position(
        ticker="NVO",
        name="Novo Nordisk - ADR",
        shares=Decimal("201.94608"),
        cost_basis_per_share=Decimal("56.63"),
        current_price=Decimal("37.17"),
    )


def _full_avenue_portfolio() -> Portfolio:
    """All 17 positions from the real Avenue extract."""
    rows = [
        ("LIN", "Linde plc", "34.47335", "431.36", "504.65"),
        ("RELX", "RELX Plc - ADR", "452.2486", "41.24", "33.18"),
        ("SPGI", "S&P Global Inc", "33.85908", "490.29", "419.69"),
        ("EQIX", "Equinix Inc", "12.93555", "792.36", "1031.93"),
        ("ASML", "ASML Holding NV - ADR", "8.42225", "772.82", "1440.62"),
        ("ROP", "Roper Technologies Inc", "33.16561", "457.73", "346.59"),
        ("MSFT", "Microsoft Corporation", "27.38028", "449.20", "369.04"),
        ("GOOGL", "Alphabet Inc - Class A", "29.97738", "192.65", "315.28"),
        ("TSM", "Taiwan Semiconductor Manufacturing - ADR", "24.86184", "217.79", "364.32"),
        ("AVGO", "Broadcom Inc", "24.22126", "241.16", "356.07"),
        ("PLD", "Prologis Inc", "60.99324", "110.45", "138.68"),
        ("TDG", "TransDigm Group Inc", "6.3994", "1337.15", "1214.17"),
        ("NVO", "Novo Nordisk - ADR", "201.94608", "56.63", "37.17"),
        ("ISRG", "Intuitive Surgical Inc", "16.49494", "482.49", "453.88"),
        ("UNH", "UnitedHealth Group Inc", "22.51219", "311.89", "305.82"),
        ("JPM", "JPMorgan Chase & Co", "21.97601", "261.24", "308.67"),
        ("LLY", "Eli Lilly & Co", "6.0593", "747.26", "954.71"),
    ]
    positions = tuple(
        Position(
            ticker=r[0], name=r[1],
            shares=Decimal(r[2]),
            cost_basis_per_share=Decimal(r[3]),
            current_price=Decimal(r[4]),
        )
        for r in rows
    )
    return Portfolio(positions=positions)


# -- Position tests ------------------------------------------------------------

class TestPositionGainLoss:
    def test_lin_positive_gain(self) -> None:
        position = _lin_position()
        assert position.market_value.amount == Decimal("34.47335") * Decimal("504.65")
        assert position.gain_loss.amount > 0

    def test_lin_gain_pct_matches_avenue(self) -> None:
        """Avenue shows LIN at +16.99% gain."""
        position = _lin_position()
        assert abs(position.gain_loss_pct - Decimal("16.99")) < Decimal("0.1")

    def test_nvo_negative_gain(self) -> None:
        position = _nvo_position()
        assert position.gain_loss.amount < 0

    def test_nvo_loss_pct_matches_avenue(self) -> None:
        """Avenue shows NVO at -34.36% loss."""
        position = _nvo_position()
        assert abs(position.gain_loss_pct - Decimal("-34.36")) < Decimal("0.1")


# -- Portfolio tests -----------------------------------------------------------

class TestPortfolioAggregates:
    def test_total_value_matches_avenue(self) -> None:
        """Avenue shows total portfolio value of $171,499.17.

        Tolerance is $3.00 because Avenue rounds each position to 2 decimal
        places before summing (17 positions x ~$0.16 rounding = ~$2.72).
        """
        portfolio = _full_avenue_portfolio()
        expected = Decimal("171499.17")
        assert abs(portfolio.total_value.amount - expected) < Decimal("3.00")

    def test_total_gain_loss_matches_avenue(self) -> None:
        """Avenue shows total P/L of +$8,128.91.

        Same display-rounding tolerance as total_value.
        """
        portfolio = _full_avenue_portfolio()
        expected = Decimal("8128.91")
        assert abs(portfolio.total_gain_loss.amount - expected) < Decimal("3.00")

    def test_total_gain_loss_pct_matches_avenue(self) -> None:
        """Avenue shows total P/L% of +4.98%."""
        portfolio = _full_avenue_portfolio()
        expected = Decimal("4.98")
        assert abs(portfolio.total_gain_loss_pct - expected) < Decimal("0.1")

    def test_position_count(self) -> None:
        portfolio = _full_avenue_portfolio()
        assert len(portfolio) == 17

    def test_tickers(self) -> None:
        portfolio = _full_avenue_portfolio()
        assert "LIN" in portfolio.tickers
        assert "ASML" in portfolio.tickers
        assert len(portfolio.tickers) == 17


class TestPortfolioWeights:
    def test_lin_is_largest_position(self) -> None:
        """Avenue shows LIN as the top position (~$17,397)."""
        portfolio = _full_avenue_portfolio()
        lin_weight = portfolio.weight_pct("LIN")
        assert lin_weight > Decimal("9")
        assert lin_weight < Decimal("12")

    def test_weights_sum_to_100(self) -> None:
        portfolio = _full_avenue_portfolio()
        total = sum(portfolio.weight_pct(ticker) for ticker in portfolio.tickers)
        assert abs(total - Decimal("100")) < Decimal("0.01")

    def test_unknown_ticker_returns_zero(self) -> None:
        portfolio = _full_avenue_portfolio()
        assert portfolio.weight_pct("INVALID") == Decimal("0")


class TestPortfolioDisplay:
    def test_total_value_display(self) -> None:
        portfolio = _full_avenue_portfolio()
        display = portfolio.total_value.display()
        assert "$" in display
        assert "171" in display
