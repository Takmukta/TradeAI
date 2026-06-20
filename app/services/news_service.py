import httpx
import xml.etree.ElementTree as ET
from typing import List
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from app.models.news_article import NewsArticle
from app.utils.logger import get_logger, audit_log

logger = get_logger(__name__)


def fetch_news(ticker: str, max_articles: int = 10) -> List[NewsArticle]:
    """Fetch ticker-specific news using Yahoo Finance RSS (most reliable free source)."""
    articles: List[NewsArticle] = []

    # Primary: Bing News RSS — returns ticker-specific, relevant news
    try:
        articles = _fetch_bing_news(ticker, max_articles)
    except Exception as e:
        logger.warning(f"Bing news failed for {ticker}: {e}")

    # Fallback: Yahoo Finance RSS
    if len(articles) < 3:
        try:
            articles += _fetch_yahoo_rss(ticker, max_articles - len(articles))
        except Exception as e:
            logger.warning(f"Yahoo RSS fallback failed for {ticker}: {e}")

    if not articles:
        articles.append(NewsArticle(
            ticker=ticker,
            title=f"No recent news available for {ticker}",
            summary=f"Could not retrieve news for {ticker} at this time.",
        ))

    audit_log("news_fetched", {"ticker": ticker, "count": len(articles)})
    return articles[:max_articles]


def _fetch_yahoo_rss(ticker: str, max_articles: int) -> List[NewsArticle]:
    """Yahoo Finance RSS feed — ticker-specific news."""
    resp = httpx.get(
        "https://feeds.finance.yahoo.com/rss/2.0/headline",
        params={"s": ticker, "region": "US", "lang": "en-US"},
        headers={"User-Agent": "Mozilla/5.0 (TradeAI/1.0)"},
        timeout=10,
        follow_redirects=True,
    )
    resp.raise_for_status()

    root = ET.fromstring(resp.text)
    items = root.findall(".//item")
    articles = []

    for item in items[:max_articles]:
        title_el = item.find("title")
        desc_el = item.find("description")
        link_el = item.find("link")
        source_el = item.find("source")
        pubdate_el = item.find("pubDate")

        title = title_el.text.strip() if title_el is not None and title_el.text else ""
        summary = desc_el.text.strip() if desc_el is not None and desc_el.text else title
        url = link_el.text.strip() if link_el is not None and link_el.text else None
        source = source_el.text.strip() if source_el is not None and source_el.text else "Yahoo Finance"

        published_at = None
        if pubdate_el is not None and pubdate_el.text:
            try:
                published_at = parsedate_to_datetime(pubdate_el.text).astimezone(timezone.utc)
            except Exception:
                pass

        if title:
            articles.append(NewsArticle(
                ticker=ticker,
                title=title,
                summary=summary,
                url=url,
                source=source,
                published_at=published_at,
            ))

    return articles


def _fetch_bing_news(ticker: str, max_articles: int) -> List[NewsArticle]:
    """Bing News RSS as a fallback for ticker-specific news."""
    company_map = {
        "AAPL": "Apple stock", "MSFT": "Microsoft stock", "GOOGL": "Google Alphabet stock",
        "AMZN": "Amazon stock", "TSLA": "Tesla stock", "NVDA": "NVIDIA stock",
        "META": "Meta stock", "NFLX": "Netflix stock", "AMD": "AMD stock",
    }
    query = company_map.get(ticker, f"{ticker} stock")
    resp = httpx.get(
        "https://www.bing.com/news/search",
        params={"q": query, "format": "rss"},
        headers={"User-Agent": "Mozilla/5.0 (TradeAI/1.0)"},
        timeout=10,
        follow_redirects=True,
    )
    resp.raise_for_status()

    root = ET.fromstring(resp.text)
    items = root.findall(".//item")
    articles = []

    for item in items[:max_articles]:
        title_el = item.find("title")
        desc_el = item.find("description")
        link_el = item.find("link")
        pubdate_el = item.find("pubDate")

        title = title_el.text.strip() if title_el is not None and title_el.text else ""
        summary = desc_el.text.strip() if desc_el is not None and desc_el.text else title
        # Strip HTML tags from Bing descriptions
        import re
        summary = re.sub(r"<[^>]+>", "", summary).strip()
        url = link_el.text.strip() if link_el is not None and link_el.text else None

        published_at = None
        if pubdate_el is not None and pubdate_el.text:
            try:
                published_at = parsedate_to_datetime(pubdate_el.text).astimezone(timezone.utc)
            except Exception:
                pass

        if title:
            articles.append(NewsArticle(
                ticker=ticker,
                title=title,
                summary=summary,
                url=url,
                source="Bing News",
                published_at=published_at,
            ))

    return articles
