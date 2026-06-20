import os
import json
from typing import List
from anthropic import Anthropic
from app.models.news_article import NewsArticle
from app.utils.logger import get_logger, audit_log

logger = get_logger(__name__)
_client = None


def _get_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    return _client


def analyze_sentiment(articles: List[NewsArticle]) -> List[NewsArticle]:
    if not articles:
        return articles

    snippets = "\n".join(
        f"[{i+1}] {a.title}: {a.summary[:300]}" for i, a in enumerate(articles)
    )
    prompt = f"""Analyze the sentiment of each news snippet below for investing purposes.
For each item return a JSON array with objects: {{"index": 1, "score": <float -1 to 1>, "label": "<positive|neutral|negative>"}}.
Only return the JSON array, nothing else.

News snippets:
{snippets}"""

    try:
        client = _get_client()
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        results = json.loads(raw)
        for item in results:
            idx = item["index"] - 1
            if 0 <= idx < len(articles):
                articles[idx].sentiment_score = float(item["score"])
                articles[idx].sentiment_label = item["label"]
        audit_log("sentiment_analyzed", {"article_count": len(articles)})
    except Exception as e:
        logger.warning(f"Sentiment analysis failed: {e}. Defaulting to neutral.")
        for a in articles:
            if a.sentiment_score is None:
                a.sentiment_score = 0.0
                a.sentiment_label = "neutral"
    return articles


def average_sentiment(articles: List[NewsArticle]) -> float:
    scores = [a.sentiment_score for a in articles if a.sentiment_score is not None]
    return sum(scores) / len(scores) if scores else 0.0
