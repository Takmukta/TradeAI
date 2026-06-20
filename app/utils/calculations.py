from typing import Optional
from app.models.financial_metrics import FinancialMetrics


def score_valuation(m: FinancialMetrics) -> float:
    """Returns 0-100 valuation score; higher = more attractive valuation."""
    score = 50.0
    if m.pe_ratio is not None:
        if m.pe_ratio < 15:
            score += 15
        elif m.pe_ratio < 25:
            score += 5
        elif m.pe_ratio > 40:
            score -= 15
    if m.pb_ratio is not None:
        if m.pb_ratio < 1.5:
            score += 10
        elif m.pb_ratio > 5:
            score -= 10
    if m.debt_to_equity is not None:
        if m.debt_to_equity < 0.5:
            score += 10
        elif m.debt_to_equity > 2:
            score -= 10
    if m.roe is not None:
        if m.roe > 0.2:
            score += 10
        elif m.roe < 0.05:
            score -= 5
    if m.profit_margin is not None:
        if m.profit_margin > 0.2:
            score += 5
        elif m.profit_margin < 0:
            score -= 10
    return max(0.0, min(100.0, score))


def score_sentiment(avg_sentiment: float) -> float:
    """Normalize average sentiment (-1 to 1) to 0-100."""
    return (avg_sentiment + 1) / 2 * 100


def combined_score(valuation_score: float, sentiment_score: float) -> float:
    return valuation_score * 0.6 + sentiment_score * 0.4


def recommendation_from_score(score: float) -> str:
    if score >= 65:
        return "BUY"
    elif score >= 45:
        return "HOLD"
    else:
        return "SELL"
