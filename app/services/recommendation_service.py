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

    metrics_text = "\n".join([
        f"- P/E Ratio: {metrics.pe_ratio}",
        f"- P/B Ratio: {metrics.pb_ratio}",
        f"- Debt/Equity: {metrics.debt_to_equity}",
        f"- ROE: {metrics.roe}",
        f"- Profit Margin: {metrics.profit_margin}",
        f"- EPS: {metrics.eps}",
        f"- Beta: {metrics.beta}",
        f"- Revenue Growth: {metrics.revenue_growth}",
        f"- Current Ratio: {metrics.current_ratio}",
    ])

    top_headlines = "\n".join(f"- {a.title} ({a.sentiment_label})" for a in articles[:5])

    prompt = f"""You are a financial analyst. Given the data below for {ticker}, provide:
1. A trading recommendation: BUY, HOLD, or SELL
2. A concise rationale (3-5 sentences)
3. Key risk factors (2-3 bullets)
4. Key upside factors (2-3 bullets)

Use the rule-based pre-assessment as guidance: {rule_based} (valuation score: {val_score:.1f}/100, sentiment score: {sent_score:.1f}/100).

Financial Metrics:
{metrics_text}

Recent News Sentiment (avg: {avg_sentiment:.2f}):
{top_headlines}

Respond in JSON with keys: "recommendation", "rationale", "risks", "upsides".
Only return the JSON, no markdown fences."""

    try:
        client = _get_client()
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw)
    except Exception as e:
        logger.warning(f"LLM recommendation failed for {ticker}: {e}. Using rule-based.")
        result = {
            "recommendation": rule_based,
            "rationale": f"Based on quantitative scoring: valuation {val_score:.1f}/100, sentiment {sent_score:.1f}/100.",
            "risks": ["Insufficient data for full analysis"],
            "upsides": ["Quantitative model signals " + rule_based],
        }

    result["ticker"] = ticker
    result["valuation_score"] = round(val_score, 2)
    result["sentiment_score"] = round(sent_score, 2)
    result["final_score"] = round(final_score, 2)
    audit_log("recommendation_generated", {"ticker": ticker, "recommendation": result.get("recommendation")})
    return result
