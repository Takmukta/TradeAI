from fastapi import APIRouter, HTTPException, Query
from app.services.news_service import fetch_news
from app.services.sentiment_service import analyze_sentiment

router = APIRouter(prefix="/news", tags=["news"])


@router.get("/{ticker}")
def get_news(ticker: str, max_articles: int = Query(default=10, ge=1, le=50)):
    ticker = ticker.strip().upper()
    if not ticker.isalpha() or len(ticker) > 10:
        raise HTTPException(status_code=422, detail=f"Invalid ticker: {ticker}")
    articles = fetch_news(ticker, max_articles)
    articles = analyze_sentiment(articles)
    return {
        "ticker": ticker,
        "articles": [a.model_dump() for a in articles],
    }
