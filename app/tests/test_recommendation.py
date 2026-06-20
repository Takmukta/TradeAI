import pytest
from unittest.mock import patch, MagicMock
from app.models.financial_metrics import FinancialMetrics
from app.models.news_article import NewsArticle
from app.services.recommendation_service import generate_recommendation


def make_metrics(**kwargs):
    return FinancialMetrics(ticker="AAPL", **kwargs)


def make_article(score=0.5):
    return NewsArticle(ticker="AAPL", title="Test", summary="Test summary", sentiment_score=score)


def test_recommendation_llm_success():
    mock_resp = MagicMock()
    mock_resp.content = [MagicMock(text='{"recommendation": "BUY", "rationale": "Strong fundamentals.", "risks": ["market risk"], "upsides": ["strong brand"]}')]

    with patch("app.services.recommendation_service._get_client") as mock_client:
        mock_client.return_value.messages.create.return_value = mock_resp
        result = generate_recommendation(
            "AAPL",
            make_metrics(pe_ratio=18, roe=0.35, profit_margin=0.28),
            [make_article(0.6)],
            0.6,
        )

    assert result["recommendation"] == "BUY"
    assert result["ticker"] == "AAPL"
    assert "valuation_score" in result
    assert "final_score" in result


def test_recommendation_fallback_on_llm_error():
    with patch("app.services.recommendation_service._get_client", side_effect=Exception("fail")):
        result = generate_recommendation(
            "TEST",
            make_metrics(pe_ratio=12, roe=0.25),
            [make_article(0.4)],
            0.4,
        )
    assert result["recommendation"] in ("BUY", "HOLD", "SELL")
    assert result["ticker"] == "TEST"
