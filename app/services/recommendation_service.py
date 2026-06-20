import os
import json
from typing import List
from anthropic import Anthropic
from app.models.financial_metrics import FinancialMetrics
from app.models.news_article import NewsArticle
from app.utils.calculations import (
    score_valuation,
    score_sentiment,
    combined_score,
    recommendation_from_score,
)
from app.utils.logger import get_logger, audit_log

logger = get_logger(__name__)
_client = None


def _get_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    return _client


def _fmt(v, pct=False, prefix=""):
    if v is None:
        return "N/A"
    if pct:
        return f"{v * 100:.1f}%"
    return f"{prefix}{v}"


def generate_recommendation(
    ticker: str,
    metrics: FinancialMetrics,
    articles: List[NewsArticle],
    avg_sentiment: float,
) -> dict:
    val_score = score_valuation(metrics)
    sent_score = score_sentiment(avg_sentiment)
    final_score = combined_score(val_score, sent_score)
    rule_based = recommendation_from_score(final_score)

    news_summary = "\n".join(
        f"- [{a.sentiment_label or 'neutral'}] {a.title}" for a in articles[:8]
    ) or "No recent news available."

    prompt = f"""You are a professional financial analyst AI that evaluates stocks based on both quantitative financial metrics and qualitative news sentiment. Given the following input data, provide a detailed recommendation to either BUY, SELL, or HOLD the stock.

Stock: {ticker}

Financial Metrics (compared to industry norms and standards):
- P/E Ratio: {_fmt(metrics.pe_ratio)}
- P/B Ratio: {_fmt(metrics.pb_ratio)}
- EPS (Earnings Per Share): {_fmt(metrics.eps)}
- ROE (Return on Equity): {_fmt(metrics.roe, pct=True)}
- Profit Margin: {_fmt(metrics.profit_margin, pct=True)}
- Revenue Growth: {_fmt(metrics.revenue_growth, pct=True)}
- Debt / Equity Ratio: {_fmt(metrics.debt_to_equity)}
- Current Ratio: {_fmt(metrics.current_ratio)}
- Beta (Volatility): {_fmt(metrics.beta)}
- Dividend Yield: {_fmt(metrics.dividend_yield, pct=True)}
- 52-Week High: {_fmt(metrics.fifty_two_week_high, prefix="$")}
- 52-Week Low: {_fmt(metrics.fifty_two_week_low, prefix="$")}

Latest News Summary:
{news_summary}

Analysis Guidelines & Industry Standard Benchmarks:
Evaluate the provided metrics strictly using these standard financial baselines:

Valuation Multiples:
- P/E Ratio: <15 indicates undervalued/value stock (BUY signal); 15-25 is fairly valued (HOLD signal); >25 indicates overvalued or high-growth (SELL signal unless backed by >20% Revenue Growth).
- P/B Ratio: <1.5 suggests the stock is undervalued (BUY signal); >3.0 indicates it is overvalued relative to its balance sheet assets (SELL signal).

Profitability & Growth:
- ROE: >15% is considered strong, showing efficient management (BUY signal); <8% indicates poor capital efficiency (SELL signal).
- Profit Margin: >10% is healthy (BUY signal); <5% means thin margins vulnerable to economic shocks (SELL signal).
- Revenue Growth: >10% year-over-year indicates a healthy, expanding business (BUY signal); negative growth indicates contraction (SELL signal).

Financial Health & Risk:
- Debt / Equity: <1.0 indicates low leverage and safe debt levels (BUY signal); >2.0 signifies heavy debt dependency and higher insolvency risk (SELL signal).
- Current Ratio: 1.5-3.0 indicates ideal short-term liquidity to cover obligations (BUY signal); <1.0 indicates a high risk of a cash crunch (SELL signal).
- Beta: <1.0 means lower volatility than the market (defensive/stable); >1.0 means high volatility/high risk.

Qualitative News Sentiment:
- Positive Sentiment: Regulatory approvals, strong earnings beats, product launches, or insider buying supports a BUY.
- Negative Sentiment: SEC investigations, executive departures, product recalls, or macroeconomic headwinds favor a SELL.

Final Decision Logic Matrix:
- BUY: Must have strong valuation or growth metrics (e.g., low P/E, strong ROE, healthy Current Ratio) AND Neutral to Positive news sentiment.
- SELL: Triggered if there are major balance sheet red flags (Debt/Equity >2.0, Current Ratio <1.0), crashing growth metrics, or Highly Negative news sentiment.
- HOLD: Triggered if metrics are mixed (e.g., great growth but overvalued P/E), if metrics sit precisely within fair-value averages, or if data is insufficient/ambiguous.

Quantitative pre-assessment: {rule_based} (valuation score: {val_score:.1f}/100, sentiment score: {sent_score:.1f}/100, combined: {final_score:.1f}/100).

Respond ONLY with a valid JSON object using exactly these keys:
- "recommendation": one of "BUY", "SELL", or "HOLD"
- "rationale": 3-5 sentences explaining the decision, referencing specific metrics and news
- "risks": array of 2-3 concise risk bullet strings
- "upsides": array of 2-3 concise upside bullet strings

Return only the JSON object, no markdown fences, no extra text."""

    try:
        client = _get_client()
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        result = json.loads(raw)
    except Exception as e:
        logger.warning(f"LLM recommendation failed for {ticker}: {e}. Using rule-based fallback.")
        result = {
            "recommendation": rule_based,
            "rationale": (
                f"Rule-based assessment: valuation score {val_score:.1f}/100, "
                f"sentiment score {sent_score:.1f}/100, combined {final_score:.1f}/100."
            ),
            "risks": ["Insufficient data for full LLM analysis"],
            "upsides": [f"Quantitative model signals {rule_based}"],
        }

    result["ticker"] = ticker
    result["valuation_score"] = round(val_score, 2)
    result["sentiment_score"] = round(sent_score, 2)
    result["final_score"] = round(final_score, 2)
    audit_log("recommendation_generated", {"ticker": ticker, "recommendation": result.get("recommendation")})
    return result
