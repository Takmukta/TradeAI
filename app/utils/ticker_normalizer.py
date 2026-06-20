"""
Ticker normalization hook.

Two-tier lookup:
  Tier 1 — hardcoded local map of common company names to tickers
  Tier 2 — Yahoo Finance autocomplete API for anything not in the map
  Fallback — return uppercased raw input unchanged
"""

import re
import httpx
from app.utils.logger import get_logger

logger = get_logger(__name__)

# --- Tier 1: local company-name → ticker map ---
_NAME_TO_TICKER: dict[str, str] = {
    # Company name variants → ticker
    "apple": "AAPL",
    "nvidia": "NVDA",
    "microsoft": "MSFT",
    "google": "GOOGL",
    "alphabet": "GOOGL",
    "amazon": "AMZN",
    "tesla": "TSLA",
    "meta": "META",
    "facebook": "META",
    "netflix": "NFLX",
    "amd": "AMD",
    "advanced micro devices": "AMD",
    "intel": "INTC",
    "salesforce": "CRM",
    "adobe": "ADBE",
    "paypal": "PYPL",
    "uber": "UBER",
    "lyft": "LYFT",
    "airbnb": "ABNB",
    "spotify": "SPOT",
    "twitter": "X",
    "x": "X",
    "shopify": "SHOP",
    "zoom": "ZM",
    "snap": "SNAP",
    "snapchat": "SNAP",
    "pinterest": "PINS",
    "palantir": "PLTR",
    "coinbase": "COIN",
    "robinhood": "HOOD",
    "jp morgan": "JPM",
    "jpmorgan": "JPM",
    "bank of america": "BAC",
    "goldman sachs": "GS",
    "morgan stanley": "MS",
    "berkshire": "BRK-B",
    "berkshire hathaway": "BRK-B",
    "johnson and johnson": "JNJ",
    "johnson & johnson": "JNJ",
    "pfizer": "PFE",
    "moderna": "MRNA",
    "eli lilly": "LLY",
    "walmart": "WMT",
    "target": "TGT",
    "costco": "COST",
    "disney": "DIS",
    "exxon": "XOM",
    "exxonmobil": "XOM",
    "chevron": "CVX",
    "boeing": "BA",
    "ford": "F",
    "general motors": "GM",
    "gm": "GM",
    "at&t": "T",
    "att": "T",
    "verizon": "VZ",
}

# Ticker format: 1-10 uppercase letters (allows hyphens for e.g. BRK-B)
# Public alias used by validators and models
VALID_TICKER_RE = re.compile(r"^[A-Z]{1,10}(-[A-Z]{1})?$")
_TICKER_RE = VALID_TICKER_RE


def get_valid_ticker(raw: str) -> str:
    """
    Normalize raw user input to a valid stock ticker.

    Steps:
      1. Strip whitespace, uppercase.
      2. If it already looks like a ticker, return it immediately.
      3. Check Tier 1 local map (case-insensitive company name lookup).
      4. Check Tier 2 Yahoo Finance autocomplete.
      5. Fallback: return uppercased raw input.
    """
    if not raw or not raw.strip():
        return raw

    cleaned = raw.strip()
    upper = cleaned.upper()

    # Tier 1: local map lookup first (lowercase key) — takes priority over ticker-format check
    # so "APPLE" maps to AAPL rather than being returned as-is
    lower = cleaned.lower()
    if lower in _NAME_TO_TICKER:
        ticker = _NAME_TO_TICKER[lower]
        logger.info(f"Tier 1 matched '{raw}' -> {ticker}")
        return ticker

    # If it's already a valid short ticker format (<=5 chars), return as-is
    # Longer strings (e.g. "NVIDIA" = 6 chars) fall through to Tier 2
    if _TICKER_RE.match(upper) and len(upper) <= 5:
        logger.debug(f"'{raw}' already looks like a ticker: {upper}")
        return upper

    # Tier 2: Yahoo Finance autocomplete
    ticker = _yahoo_autocomplete(cleaned)
    if ticker:
        logger.info(f"Tier 2 Yahoo matched '{raw}' -> {ticker}")
        return ticker

    # Fallback
    logger.warning(f"Could not resolve '{raw}' to a ticker; using uppercase fallback: {upper}")
    return upper


def _yahoo_autocomplete(query: str) -> str | None:
    """Query Yahoo Finance autocomplete API and return the best equity match."""
    try:
        resp = httpx.get(
            "https://query2.finance.yahoo.com/v1/finance/search",
            params={"q": query, "quotesCount": 5, "newsCount": 0, "listsCount": 0},
            headers={"User-Agent": "Mozilla/5.0 (TradeAI/1.0)"},
            timeout=5,
            follow_redirects=True,
        )
        resp.raise_for_status()
        data = resp.json()
        quotes = data.get("quotes", [])
        # Prefer quotes with quoteType EQUITY and a short symbol
        for q in quotes:
            symbol = q.get("symbol", "")
            qtype = q.get("quoteType", "")
            # Skip funds, indexes, options
            if qtype in ("EQUITY", "ETF") and symbol and "." not in symbol:
                return symbol.upper()
        # If no ideal match, return first quote symbol anyway
        if quotes:
            return quotes[0].get("symbol", "").upper() or None
    except Exception as e:
        logger.warning(f"Yahoo autocomplete failed for '{query}': {e}")
    return None
