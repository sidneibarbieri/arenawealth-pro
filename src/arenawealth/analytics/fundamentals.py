"""Fundamentals providers."""

from __future__ import annotations

import math
from typing import Protocol

import httpx
import yfinance

from arenawealth.analytics.models import Fundamentals
from arenawealth.config.settings import ProviderKeys, load_provider_keys


class FundamentalsProvider(Protocol):
    """Contract for any source of company fundamentals and FX rates."""

    def get_fundamentals(self, ticker: str) -> Fundamentals: ...

    def exchange_rate(self, base: str, quote: str) -> float: ...


class YahooFundamentalsProvider:
    """Fundamentals from Yahoo Finance. Network errors propagate to the caller."""

    def __init__(self) -> None:
        self._exchange_rates: dict[str, float] = {}

    def get_fundamentals(self, ticker: str) -> Fundamentals:
        handle = yfinance.Ticker(ticker)
        info = handle.info
        income = handle.income_stmt
        cash_flow = handle.cashflow
        balance = handle.balance_sheet
        return Fundamentals(
            live_price=float(handle.fast_info.last_price),
            market_cap=info.get("marketCap"),
            return_on_equity=info.get("returnOnEquity"),
            gross_margin=info.get("grossMargins"),
            operating_margin=info.get("operatingMargins"),
            forward_pe=info.get("forwardPE"),
            fifty_two_week_high=info.get("fiftyTwoWeekHigh"),
            analyst_target=info.get("targetMeanPrice"),
            free_cash_flow=info.get("freeCashflow"),
            financial_currency=info.get("financialCurrency"),
            trading_currency=info.get("currency"),
            revenue_series=statement_row(income, "Total Revenue", "Operating Revenue"),
            ebit_series=statement_row(income, "EBIT", "Operating Income"),
            tax_rate_series=statement_row(income, "Tax Rate For Calcs"),
            operating_income_series=statement_row(
                income, "Operating Income", "Total Operating Income As Reported"
            ),
            eps_series=statement_row(income, "Diluted EPS", "Basic EPS"),
            fcf_series=statement_row(cash_flow, "Free Cash Flow"),
            diluted_shares_series=statement_row(
                income, "Diluted Average Shares", "Basic Average Shares"
            ),
            invested_capital_series=statement_row(balance, "Invested Capital"),
        )

    def exchange_rate(self, base: str, quote: str) -> float:
        pair = f"{base}{quote}=X"
        if pair not in self._exchange_rates:
            self._exchange_rates[pair] = float(yfinance.Ticker(pair).fast_info.last_price)
        return self._exchange_rates[pair]


class FMPFundamentalsProvider:
    """Fundamentals from Financial Modeling Prep.

    FMP is preferred when an API key is available because the statement history
    is structured and more reproducible than scraped market pages.
    """

    BASE_URL = "https://financialmodelingprep.com/api/v3"

    def __init__(self, api_key: str, client: httpx.Client | None = None) -> None:
        if not api_key:
            raise ValueError("FMP_API_KEY is required for FMPFundamentalsProvider")
        self._client = client or httpx.Client(timeout=60.0, base_url=self.BASE_URL)
        self._api_key = api_key
        self._exchange_rates: dict[str, float] = {}

    def get_fundamentals(self, ticker: str) -> Fundamentals:
        quote = first_item(self._get(f"/quote/{ticker}"))
        profile = first_item(self._get(f"/profile/{ticker}"))
        income = self._get(f"/income-statement/{ticker}", limit=10)
        cash_flow = self._get(f"/cash-flow-statement/{ticker}", limit=10)
        balance = self._get(f"/balance-sheet-statement/{ticker}", limit=10)
        metrics = self._get(f"/key-metrics/{ticker}", limit=10)
        latest_metrics = first_item(metrics)
        market_cap = optional_float(quote.get("marketCap") or profile.get("mktCap"))

        return Fundamentals(
            live_price=require_float(quote.get("price"), f"{ticker} quote price"),
            market_cap=market_cap,
            return_on_equity=optional_float(latest_metrics.get("roe")),
            gross_margin=optional_float(latest_metrics.get("grossProfitMargin")),
            operating_margin=optional_float(latest_metrics.get("operatingProfitMargin")),
            forward_pe=optional_float(quote.get("pe")),
            fifty_two_week_high=optional_float(quote.get("yearHigh")),
            analyst_target=None,
            free_cash_flow=latest_field(cash_flow, "freeCashFlow"),
            financial_currency=profile.get("currency") or profile.get("reportedCurrency"),
            trading_currency=profile.get("currency"),
            revenue_series=field_series(income, "revenue"),
            ebit_series=field_series(income, "ebitda", "operatingIncome"),
            tax_rate_series=tax_rate_series(income),
            operating_income_series=field_series(income, "operatingIncome"),
            eps_series=field_series(income, "epsdiluted", "eps"),
            fcf_series=field_series(cash_flow, "freeCashFlow"),
            diluted_shares_series=field_series(
                income, "weightedAverageShsOutDil", "weightedAverageShsOut"
            ),
            invested_capital_series=invested_capital_series(balance),
        )

    def exchange_rate(self, base: str, quote: str) -> float:
        pair = f"{base}{quote}=X"
        if pair not in self._exchange_rates:
            self._exchange_rates[pair] = float(yfinance.Ticker(pair).fast_info.last_price)
        return self._exchange_rates[pair]

    def close(self) -> None:
        self._client.close()

    def _get(self, endpoint: str, **params: int | str) -> list[dict[str, object]]:
        response = self._client.get(endpoint, params={**params, "apikey": self._api_key})
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list):
            raise ValueError(f"FMP returned non-list payload for {endpoint}")
        return payload


def build_fundamentals_provider(keys: ProviderKeys | None = None) -> FundamentalsProvider:
    loaded_keys = keys or load_provider_keys()
    if loaded_keys.fmp_api_key:
        return FMPFundamentalsProvider(loaded_keys.fmp_api_key)
    return YahooFundamentalsProvider()


def statement_row(statement, *labels: str) -> tuple[float, ...]:
    """Return one statement row ordered oldest to newest, skipping blanks."""
    if statement is None or statement.empty:
        return ()
    for label in labels:
        if label in statement.index:
            newest_first = statement.loc[label].tolist()
            return tuple(float(value) for value in reversed(newest_first) if is_number(value))
    return ()


def is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not math.isnan(value)


def first_item(rows: list[dict[str, object]]) -> dict[str, object]:
    if not rows:
        return {}
    return rows[0]


def optional_float(value: object) -> float | None:
    if value is None:
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def require_float(value: object, label: str) -> float:
    parsed = optional_float(value)
    if parsed is None:
        raise ValueError(f"Missing numeric value: {label}")
    return parsed


def field_series(rows: list[dict[str, object]], *fields: str) -> tuple[float, ...]:
    values = []
    for row in reversed(rows):
        for field in fields:
            value = optional_float(row.get(field))
            if value is not None:
                values.append(value)
                break
    return tuple(values)


def latest_field(rows: list[dict[str, object]], *fields: str) -> float | None:
    for row in rows:
        for field in fields:
            value = optional_float(row.get(field))
            if value is not None:
                return value
    return None


def tax_rate_series(rows: list[dict[str, object]]) -> tuple[float, ...]:
    values = []
    for row in reversed(rows):
        income_before_tax = optional_float(row.get("incomeBeforeTax"))
        tax_expense = optional_float(row.get("incomeTaxExpense"))
        if income_before_tax and tax_expense is not None:
            values.append(tax_expense / income_before_tax)
    return tuple(values)


def invested_capital_series(rows: list[dict[str, object]]) -> tuple[float, ...]:
    values = []
    for row in reversed(rows):
        explicit = optional_float(row.get("investedCapital"))
        if explicit is not None:
            values.append(explicit)
            continue
        debt = optional_float(row.get("totalDebt")) or 0.0
        equity = optional_float(row.get("totalStockholdersEquity")) or 0.0
        cash = optional_float(row.get("cashAndCashEquivalents")) or 0.0
        invested = debt + equity - cash
        if invested > 0:
            values.append(invested)
    return tuple(values)
