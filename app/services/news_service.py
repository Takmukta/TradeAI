import httpx
from typing import List
from datetime import datetime, timezone
from app.models.news_article import NewsArticle
from app.utils.logger import get_logger, audit_log

logger = get_logger(__name__)

# Uses Yahoo Finance news endpoint (no API key required)
YF_NEWS_URL = "https://query2.finance.yahoo.com/v1/finance/search"


def fetch_news(ticker: str, max_articles: int = 10) -> List[NewsArticle]:
    articles: List[NewsArticle] = []
    try:
        headers = {"User-Agent": "Mozilla/5.0 (TradeAI/1.0)"}
        params = {"q": ticker, "newsCount": max_articles, "quotesCount": 0}
        resp = httpx.get(YF_NEWS_URL, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        news_items = data.get("news", [])
        for item in news_items[:max_articles]:
            title = item.get("title", "")
            summary = item.get("summary") or title
            url = item.get("link") or item.get("url")
            source = item.get("publisher") or ""
            pub_ts = item.get("providerPublishTime")
            published_at = datetime.fromtimestamp(pub_ts, tz=timezone.utc) if pub_ts else None
            articles.append(NewsArticle(
                ticker=ticker,
                title=title,
                summary=summary,
                url=url,
                source=source,
                published_at=published_at,
            ))
        audit_log("news_fetched", {"ticker": ticker, "count": len(articles)})
    except Exception as e:
        logger.warning(f"News fetch failed for {ticker}: {e}")
        articles.append(NewsArticle(
            ticker=ticker,
            title=f"No recent news available for {ticker}",
            summary=f"Could not retrieve news for {ticker} at this time.",
        ))
    return articles
