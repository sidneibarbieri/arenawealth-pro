"""Tests for Position and Portfolio using a brokerage-style seed fixture."""

from decimal import Decimal

from arenawealth.domain.portfolio import Portfolio
from arenawealth.domain.position import Position

# -- Fixtures: brokerage-style seed data ---------------------------------------


def _lin_position() -> Position:
    return Position(
        ticker="LIN",
        name="Linde plc",
        shares=Decimal("34.47335"),
        cost_basis_per_share=Decimal("431.36"),
        current_price=Decimal("504.40"),
    )


def _nvo_position() -> Position:
    return Position(
        ticker="NVO",
        name="Novo Nordisk - ADR",
        shares=Decimal("201.94608"),
        cost_basis_per_share=Decimal("56.63"),
        current_price=Decimal("44.46"),
    )


def _full_seed_portfolio() -> Portfolio:
    """All 17 positions from the seed fixture."""
    rows = [
        ("LIN", "Linde plc", "34.47335", "431.36", "504.40"),
        ("RELX", "RELX Plc - ADR", "510.60444", "40.44", "32.38"),
        ("SPGI", "S&P Global Inc", "38.52429", "482.83", "402.79"),
        ("EQIX", "Equinix Inc", "12.93555", "792.36", "1062.66"),
        ("ASML", "ASML Holding NV - New York Shares", "8.42225", "772.82", "1520.18"),
        ("ROP", "Roper Technologies Inc", "44.38372", "432.16", "324.29"),
        ("MSFT", "Microsoft Corporation", "32.17279", "444.45", "428.13"),
        ("GOOGL", "Alphabet Inc - Class A", "29.97738", "192.65", "396.86"),
        ("TSM", "Taiwan Semiconductor Manufacturing - ADR", "24.86184", "217.79", "408.46"),
        ("AVGO", "Broadcom Inc", "24.22126", "241.16", "427.82"),
        ("PLD", "Prologis Inc", "60.99324", "110.45", "140.88"),
        ("TDG", "Transdigm Group Incorporated", "7.26179", "1316.06", "1146.10"),
        ("NVO", "Novo Nordisk - ADR", "201.94608", "56.63", "44.46"),
        ("ISRG", "Intuitive Surgical Inc", "16.49494", "482.49", "425.74"),
        ("UNH", "Unitedhealth Group Inc", "22.51219", "311.89", "392.72"),
        ("JPM", "JPMorgan Chase & Co.", "21.97601", "261.24", "297.61"),
        ("LLY", "Lilly(Eli) & Co", "6.0593", "747.26", "999.75"),
    ]
    positions = tuple(
        Position(
            ticker=r[0],
            name=r[1],
            shares=Decimal(r[2]),
            cost_basis_per_share=Decimal(r[3]),
            current_price=Decimal(r[4]),
        )
        for r in rows
    )
    return Portfolio(positions=positions, cash_balance_amount=Decimal("190.05"))


# -- Position tests ------------------------------------------------------------


class TestPositionGainLoss:
    def test_lin_positive_gain(self) -> None:
        position = _lin_position()
        assert position.market_value.amount == Decimal("34.47335") * Decimal("504.40")
        assert position.gain_loss.amount > 0

    def test_lin_gain_pct_matches_seed_reference(self) -> None:
        position = _lin_position()
        assert abs(position.gain_loss_pct - Decimal("16.93")) < Decimal("0.1")

    def test_nvo_negative_gain(self) -> None:
        position = _nvo_position()
        assert position.gain_loss.amount < 0

    def test_nvo_loss_pct_matches_seed_reference(self) -> None:
        position = _nvo_position()
        assert abs(position.gain_loss_pct - Decimal("-21.49")) < Decimal("0.1")


# -- Portfolio tests -----------------------------------------------------------


class TestPortfolioAggregates:
    def test_total_value_matches_seed_reference(self) -> None:
        """Tolerance covers display rounding before summing."""
        portfolio = _full_seed_portfolio()
        expected = Decimal("190922.43")
        assert abs(portfolio.total_value.amount - expected) < Decimal("5.00")

    def test_total_assets_matches_seed_reference(self) -> None:
        portfolio = _full_seed_portfolio()
        expected = Decimal("191112.48")
        assert abs(portfolio.total_assets.amount - expected) < Decimal("5.00")

    def test_total_gain_loss_matches_seed_reference(self) -> None:
        portfolio = _full_seed_portfolio()
        expected = Decimal("16554.20")
        assert abs(portfolio.total_gain_loss.amount - expected) < Decimal("5.00")

    def test_total_gain_loss_pct_matches_seed_reference(self) -> None:
        portfolio = _full_seed_portfolio()
        expected = Decimal("9.49")
        assert abs(portfolio.total_gain_loss_pct - expected) < Decimal("0.1")

    def test_position_count(self) -> None:
        portfolio = _full_seed_portfolio()
        assert len(portfolio) == 17

    def test_tickers(self) -> None:
        portfolio = _full_seed_portfolio()
        assert "LIN" in portfolio.tickers
        assert "ASML" in portfolio.tickers
        assert len(portfolio.tickers) == 17


class TestPortfolioWeights:
    def test_lin_is_largest_position(self) -> None:
        portfolio = _full_seed_portfolio()
        lin_weight = portfolio.weight_pct("LIN")
        assert lin_weight > Decimal("8")
        assert lin_weight < Decimal("10")

    def test_weights_sum_to_100(self) -> None:
        portfolio = _full_seed_portfolio()
        total = sum(portfolio.weight_pct(ticker) for ticker in portfolio.tickers)
        assert abs(total - Decimal("100")) < Decimal("0.01")

    def test_unknown_ticker_returns_zero(self) -> None:
        portfolio = _full_seed_portfolio()
        assert portfolio.weight_pct("INVALID") == Decimal("0")


class TestPortfolioDisplay:
    def test_total_value_display(self) -> None:
        portfolio = _full_seed_portfolio()
        display = portfolio.total_value.display()
        assert "$" in display
        assert "190" in display
