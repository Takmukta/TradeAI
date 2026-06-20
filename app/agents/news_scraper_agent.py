from typing import List, Dict
from app.models.news_article import NewsArticle
from app.services.news_service import fetch_news
from app.services.sentiment_service import analyze_sentiment
from app.utils.logger import get_logger

logger = get_logger(__name__)


class NewsScraperAgent:
    """Fetches and sentiment-scores latest news for provided tickers."""

    def __init__(self, max_articles: int = 10):
        self.max_articles = max_articles

    def run(self, tickers: List[str]) -> Dict[str, List[NewsArticle]]:
        results: Dict[str, List[NewsArticle]] = {}
        for ticker in tickers:
            logger.info(f"Fetching news for {ticker}")
            articles = fetch_news(ticker, self.max_articles)
            articles = analyze_sentiment(articles)
            results[ticker] = articles
            logger.info(f"Got {len(articles)} articles for {ticker}")
        return results
