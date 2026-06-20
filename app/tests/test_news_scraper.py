import pytest
from unittest.mock import patch, MagicMock
from app.services.news_service import fetch_news
from app.models.news_article import NewsArticle


def _mock_response():
    mock = MagicMock()
    mock.raise_for_status.return_value = None
    mock.json.return_value = {
        "news": [
            {
                "title": "AAPL hits record high",
                "summary": "Apple shares surged to an all-time high today.",
                "link": "https://example.com/1",
                "publisher": "Reuters",
                "providerPublishTime": 1700000000,
            }
        ]
    }
    return mock


def test_fetch_news_returns_articles():
    with patch("app.services.news_service.httpx.get", return_value=_mock_response()):
        articles = fetch_news("AAPL", max_articles=5)
    assert len(articles) == 1
    assert articles[0].ticker == "AAPL"
    assert "record high" in articles[0].title


def test_fetch_news_fallback_on_error():
    with patch("app.services.news_service.httpx.get", side_effect=Exception("network error")):
        articles = fetch_news("AAPL")
    assert len(articles) == 1
    assert articles[0].sentiment_score is None


def test_news_article_model():
    a = NewsArticle(ticker="MSFT", title="Test", summary="A summary")
    assert a.ticker == "MSFT"
    assert a.sentiment_score is None
