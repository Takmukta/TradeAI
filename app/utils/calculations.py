from typing import Optional
from app.models.financial_metrics import FinancialMetrics


def score_valuation(m: FinancialMetrics) -> float:
    """
    Rule-based valuation score 0-100 using industry standard benchmarks.
    Each metric contributes independently; final score is clamped to [0, 100].
    """
    score = 50.0

    # P/E Ratio: <15 BUY (+15), 15-25 HOLD (0), >25 SELL (-10), >40 heavy penalty (-20)
    if m.pe_ratio is not None:
        if m.pe_ratio < 15:
            score += 15
        elif m.pe_ratio <= 25:
            score += 0
        elif m.pe_ratio <= 40:
            score -= 10
        else:
            score -= 20

    # P/B Ratio: <1.5 BUY (+10), 1.5-3.0 neutral, >3.0 SELL (-10)
    if m.pb_ratio is not None:
        if m.pb_ratio < 1.5:
            score += 10
        elif m.pb_ratio <= 3.0:
            score += 0
        else:
            score -= 10

    # ROE: >15% BUY (+12), 8-15% neutral, <8% SELL (-10)
    if m.roe is not None:
        if m.roe > 0.15:
            score += 12
        elif m.roe >= 0.08:
            score += 0
        else:
            score -= 10

    # Profit Margin: >10% BUY (+10), 5-10% neutral, <5% SELL (-10)
    if m.profit_margin is not None:
        if m.profit_margin > 0.10:
            score += 10
        elif m.profit_margin >= 0.05:
            score += 0
        else:
            score -= 10

    # Revenue Growth: >10% BUY (+12), 0-10% neutral, negative SELL (-12)
    if m.revenue_growth is not None:
        if m.revenue_growth > 0.10:
            score += 12
        elif m.revenue_growth >= 0:
            score += 0
        else:
            score -= 12

    # Debt/Equity: <1.0 BUY (+10), 1.0-2.0 neutral, >2.0 SELL (-15)
    if m.debt_to_equity is not None:
        if m.debt_to_equity < 1.0:
            score += 10
        elif m.debt_to_equity <= 2.0:
            score += 0
        else:
            score -= 15

    # Current Ratio: 1.5-3.0 BUY (+8), 1.0-1.5 neutral, <1.0 SELL (-15)
    if m.current_ratio is not None:
        if 1.5 <= m.current_ratio <= 3.0:
            score += 8
        elif m.current_ratio >= 1.0:
            score += 0
        else:
            score -= 15

    return max(0.0, min(100.0, score))


def score_sentiment(avg_sentiment: float) -> float:
    """Normalize average sentiment (-1 to 1) to 0-100."""
    return (avg_sentiment + 1) / 2 * 100


def combined_score(valuation_score: float, sentiment_score: float) -> float:
    """60% quantitative, 40% sentiment — in line with Decision Logic Matrix."""
    return valuation_score * 0.6 + sentiment_score * 0.4


def recommendation_from_score(score: float) -> str:
    if score >= 65:
        return "BUY"
    elif score >= 45:
        return "HOLD"
    else:
        return "SELL"
