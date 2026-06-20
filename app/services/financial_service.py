import yfinance as yf
from typing import Optional
from app.models.financial_metrics import FinancialMetrics
from app.models.stock import Stock
from app.utils.logger import get_logger, audit_log

logger = get_logger(__name__)


def fetch_stock_info(ticker: str) -> Stock:
    try:
        info = yf.Ticker(ticker).info
        return Stock(
            ticker=ticker,
            company_name=info.get("longName") or info.get("shortName"),
            sector=info.get("sector"),
            current_price=info.get("currentPrice") or info.get("regularMarketPrice"),
            market_cap=info.get("marketCap"),
        )
    except Exception as e:
        logger.warning(f"Could not fetch stock info for {ticker}: {e}")
        return Stock(ticker=ticker)


def fetch_financial_metrics(ticker: str) -> FinancialMetrics:
    try:
        info = yf.Ticker(ticker).info
        metrics = FinancialMetrics(
            ticker=ticker,
            pe_ratio=info.get("trailingPE") or info.get("forwardPE"),
            pb_ratio=info.get("priceToBook"),
            debt_to_equity=info.get("debtToEquity"),
            roe=info.get("returnOnEquity"),
            roa=info.get("returnOnAssets"),
            current_ratio=info.get("currentRatio"),
            eps=info.get("trailingEps"),
            revenue_growth=info.get("revenueGrowth"),
            profit_margin=info.get("profitMargins"),
            dividend_yield=info.get("dividendYield"),
            beta=info.get("beta"),
            fifty_two_week_high=info.get("fiftyTwoWeekHigh"),
            fifty_two_week_low=info.get("fiftyTwoWeekLow"),
            avg_volume=info.get("averageVolume"),
        )
        audit_log("financial_metrics_fetched", {"ticker": ticker})
        return metrics
    except Exception as e:
        logger.error(f"Error fetching metrics for {ticker}: {e}")
        return FinancialMetrics(ticker=ticker)
