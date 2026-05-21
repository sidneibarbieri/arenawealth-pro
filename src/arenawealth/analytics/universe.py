"""Portfolio universe metadata used by analysis and deployment."""

THEME_BY_TICKER = {
    "ASML": "Semiconductors",
    "AVGO": "Semiconductors",
    "TSM": "Semiconductors",
    "MSFT": "Platforms",
    "GOOGL": "Platforms",
    "LLY": "Pharma",
    "NVO": "Pharma",
    "ISRG": "MedTech",
    "UNH": "Managed Care",
    "JPM": "Banks",
    "SPGI": "Data & Analytics",
    "RELX": "Data & Analytics",
    "ROP": "Vertical Software",
    "TDG": "Aerospace",
    "LIN": "Industrial Gases",
    "EQIX": "Real Estate",
    "PLD": "Real Estate",
}

FINANCIAL_TICKERS = {"JPM"}

# Wide-moat compounders to screen as potential additions (not currently held).
# Each entry maps ticker to (display name, theme).
CANDIDATE_UNIVERSE = {
    "V": ("Visa Inc", "Payments"),
    "MA": ("Mastercard Inc", "Payments"),
    "COST": ("Costco Wholesale", "Consumer Staples"),
    "NVDA": ("NVIDIA Corporation", "Semiconductors"),
    "AAPL": ("Apple Inc", "Platforms"),
    "AMZN": ("Amazon.com Inc", "Platforms"),
    "META": ("Meta Platforms Inc", "Platforms"),
    "ADBE": ("Adobe Inc", "Vertical Software"),
    "NOW": ("ServiceNow Inc", "Vertical Software"),
    "INTU": ("Intuit Inc", "Vertical Software"),
    "ACN": ("Accenture plc", "IT Services"),
    "MCO": ("Moody's Corporation", "Data & Analytics"),
    "HD": ("Home Depot Inc", "Retail"),
    "CTAS": ("Cintas Corporation", "Industrials"),
    "SNPS": ("Synopsys Inc", "Vertical Software"),
    "CDNS": ("Cadence Design Systems", "Vertical Software"),
    "ANET": ("Arista Networks", "Networking"),
    "ODFL": ("Old Dominion Freight Line", "Industrials"),
}
