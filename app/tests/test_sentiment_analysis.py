import pytest
from unittest.mock import patch, MagicMock
from app.models.news_article import NewsArticle
from app.services.sentiment_service import analyze_sentiment, average_sentiment


def make_article(title, summary=""):
    return NewsArticle(ticker="AAPL", title=title, summary=summary or title)


def test_average_sentiment_empty():
    assert average_sentiment([]) == 0.0


def test_average_sentiment_scores():
    articles = [
        NewsArticle(ticker="X", title="t1", summary="s1", sentiment_score=0.8),
        NewsArticle(ticker="X", title="t2", summary="s2", sentiment_score=0.2),
    ]
    assert average_sentiment(articles) == pytest.approx(0.5)


def test_analyze_sentiment_llm_success():
    mock_resp = MagicMock()
    mock_resp.content = [MagicMock(text='[{"index": 1, "score": 0.7, "label": "positive"}]')]

    with patch("app.services.sentiment_service._get_client") as mock_client:
        mock_client.return_value.messages.create.return_value = mock_resp
        articles = [make_article("Apple beats earnings")]
        result = analyze_sentiment(articles)

    assert result[0].sentiment_score == pytest.approx(0.7)
    assert result[0].sentiment_label == "positive"


def test_analyze_sentiment_fallback_on_error():
    with patch("app.services.sentiment_service._get_client", side_effect=Exception("API error")):
        articles = [make_article("Some news")]
        result = analyze_sentiment(articles)
    assert result[0].sentiment_score == 0.0
    assert result[0].sentiment_label == "neutral"
