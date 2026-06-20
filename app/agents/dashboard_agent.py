from typing import List, Dict
from datetime import datetime, timezone
from app.models.news_article import NewsArticle
from app.utils.logger import get_logger, audit_log

logger = get_logger(__name__)


class DashboardAgent:
    """Compiles all analysis results into a structured dashboard report."""

    def run(
        self,
        request_id: str,
        tickers: List[str],
        news_data: Dict[str, List[NewsArticle]],
        analysis_data: Dict[str, dict],
    ) -> dict:
        logger.info(f"Building dashboard for request {request_id}")
        recommendations = {}
        news_summary = {}
        financial_metrics = {}

        for ticker in tickers:
            analysis = analysis_data.get(ticker, {})
            recommendations[ticker] = analysis.get("recommendation", {})
            financial_metrics[ticker] = {
                "stock_info": analysis.get("stock", {}),
                "metrics": analysis.get("metrics", {}),
                "avg_sentiment": analysis.get("avg_sentiment", 0.0),
            }
            articles = news_data.get(ticker, [])
            news_summary[ticker] = [
                {
                    "title": a.title,
                    "summary": a.summary,
                    "source": a.source,
                    "published_at": a.published_at.isoformat() if a.published_at else None,
                    "sentiment_label": a.sentiment_label,
                    "sentiment_score": a.sentiment_score,
                    "url": a.url,
                }
                for a in articles
            ]

        dashboard = {
            "request_id": request_id,
            "tickers": tickers,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "recommendations": recommendations,
            "news_summary": news_summary,
            "financial_metrics": financial_metrics,
        }
        audit_log("dashboard_generated", {"request_id": request_id, "tickers": tickers})
        return dashboard
