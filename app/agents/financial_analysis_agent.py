from typing import List, Dict
from app.models.financial_metrics import FinancialMetrics
from app.models.stock import Stock
from app.models.news_article import NewsArticle
from app.services.financial_service import fetch_stock_info, fetch_financial_metrics
from app.services.sentiment_service import average_sentiment
from app.services.recommendation_service import generate_recommendation
from app.utils.logger import get_logger

logger = get_logger(__name__)


class FinancialAnalysisAgent:
    """Fetches financial data, merges with news sentiment, generates recommendations."""

    def run(
        self,
        tickers: List[str],
        news_data: Dict[str, List[NewsArticle]],
    ) -> Dict[str, dict]:
        results: Dict[str, dict] = {}
        for ticker in tickers:
            logger.info(f"Running financial analysis for {ticker}")
            stock = fetch_stock_info(ticker)
            metrics = fetch_financial_metrics(ticker)
            articles = news_data.get(ticker, [])
            avg_sent = average_sentiment(articles)
            recommendation = generate_recommendation(ticker, metrics, articles, avg_sent)
            results[ticker] = {
                "stock": stock.model_dump(),
                "metrics": metrics.model_dump(),
                "recommendation": recommendation,
                "avg_sentiment": avg_sent,
            }
        return results
