"""Tests for CSV importer — validates it reads the real Avenue seed fixture correctly."""

from decimal import Decimal
from pathlib import Path

import pytest

from arenawealth.importers.csv_importer import import_csv

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
AVENUE_CSV = FIXTURES_DIR / "seed_portfolio_avenue.csv"


class TestCsvImporter:
    def test_reads_avenue_fixture(self) -> None:
        positions = import_csv(AVENUE_CSV)
        assert len(positions) == 17

    def test_first_position_is_lin(self) -> None:
        positions = import_csv(AVENUE_CSV)
        assert positions[0].ticker == "LIN"
        assert positions[0].name == "Linde plc"

    def test_shares_precision_preserved(self) -> None:
        positions = import_csv(AVENUE_CSV)
        lin = positions[0]
        assert lin.shares == Decimal("34.47335")

    def test_cost_basis_correct(self) -> None:
        positions = import_csv(AVENUE_CSV)
        lin = positions[0]
        assert lin.cost_basis_per_share == Decimal("431.36")

    def test_all_tickers_present(self) -> None:
        positions = import_csv(AVENUE_CSV)
        tickers = {pos.ticker for pos in positions}
        expected = {
            "LIN", "RELX", "SPGI", "EQIX", "ASML", "ROP", "MSFT",
            "GOOGL", "TSM", "AVGO", "PLD", "TDG", "NVO", "ISRG",
            "UNH", "JPM", "LLY",
        }
        assert tickers == expected

    def test_missing_ticker_column_raises(self, tmp_path: Path) -> None:
        csv = tmp_path / "bad.csv"
        csv.write_text("wrong_col,shares\nAAPL,10\n")
        with pytest.raises(ValueError, match="No ticker column found"):
            import_csv(csv)
