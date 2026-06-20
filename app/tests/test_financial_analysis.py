import pytest
from app.models.financial_metrics import FinancialMetrics
from app.utils.calculations import score_valuation, combined_score, recommendation_from_score


def make_metrics(**kwargs):
    return FinancialMetrics(ticker="TEST", **kwargs)


def test_score_valuation_baseline():
    m = make_metrics()
    assert score_valuation(m) == 50.0


def test_score_valuation_attractive():
    m = make_metrics(pe_ratio=12, debt_to_equity=0.3, roe=0.25, profit_margin=0.25, pb_ratio=1.2)
    assert score_valuation(m) > 65


def test_score_valuation_unattractive():
    m = make_metrics(pe_ratio=50, debt_to_equity=3.0, roe=0.02, profit_margin=-0.05)
    assert score_valuation(m) < 35


def test_recommendation_buy():
    assert recommendation_from_score(70) == "BUY"


def test_recommendation_hold():
    assert recommendation_from_score(55) == "HOLD"


def test_recommendation_sell():
    assert recommendation_from_score(30) == "SELL"


def test_combined_score_weights():
    result = combined_score(80, 60)
    assert result == pytest.approx(80 * 0.6 + 60 * 0.4)
