import uuid
from typing import List, Callable, Optional
from app.agents.user_input_agent import UserInputAgent
from app.agents.news_scraper_agent import NewsScraperAgent
from app.agents.financial_analysis_agent import FinancialAnalysisAgent
from app.agents.dashboard_agent import DashboardAgent
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Step event shape: {"step": str, "status": "pass"|"fail", "detail": str}
StepCallback = Callable[[dict], None]


def run_analysis(raw_tickers: List[str], on_step: Optional[StepCallback] = None) -> dict:
    """
    Orchestrates the full TradeAI pipeline.
    Calls on_step(event) after each meaningful operation so callers can
    stream progress to the user.
    """
    def emit(step: str, status: str, detail: str = ""):
        if on_step:
            on_step({"step": step, "status": status, "detail": detail})

    request_id = str(uuid.uuid4())
    logger.info(f"Starting analysis workflow [{request_id}] for {raw_tickers}")

    # ── Step 1: Input validation & ticker normalization ─────────────────────
    try:
        tickers = UserInputAgent().run(raw_tickers)
        resolved = ", ".join(
            f"{r} → {t}" if r.upper() != t else t
            for r, t in zip(raw_tickers, tickers)
        )
        emit("Input Validation & Ticker Resolution", "pass", resolved)
    except Exception as e:
        emit("Input Validation & Ticker Resolution", "fail", str(e))
        raise

    # ── Step 2: News fetch ──────────────────────────────────────────────────
    news_data = {}
    for ticker in tickers:
        try:
            from app.services.news_service import fetch_news
            articles = fetch_news(ticker, max_articles=10)
            news_data[ticker] = articles
            emit(f"News Fetch ({ticker})", "pass", f"{len(articles)} articles retrieved")
        except Exception as e:
            emit(f"News Fetch ({ticker})", "fail", str(e))
            news_data[ticker] = []

    # ── Step 3: Sentiment analysis ─────────────────────────────────────────
    for ticker in tickers:
        try:
            from app.services.sentiment_service import analyze_sentiment
            news_data[ticker] = analyze_sentiment(news_data[ticker])
            scored = sum(1 for a in news_data[ticker] if a.sentiment_score is not None)
            emit(f"Sentiment Analysis ({ticker})", "pass", f"{scored} articles scored")
        except Exception as e:
            emit(f"Sentiment Analysis ({ticker})", "fail", str(e))

    # ── Step 4: Yahoo Finance metrics ──────────────────────────────────────
    financial_raw = {}
    for ticker in tickers:
        try:
            from app.services.financial_service import fetch_stock_info, fetch_financial_metrics
            stock = fetch_stock_info(ticker)
            metrics = fetch_financial_metrics(ticker)
            non_null = sum(
                1 for f in [metrics.pe_ratio, metrics.pb_ratio, metrics.eps,
                             metrics.roe, metrics.profit_margin, metrics.revenue_growth,
                             metrics.debt_to_equity, metrics.current_ratio, metrics.beta]
                if f is not None
            )
            financial_raw[ticker] = {"stock": stock, "metrics": metrics}
            emit(
                f"Yahoo Finance Data ({ticker})", "pass",
                f"{stock.company_name or ticker} · {non_null}/9 key metrics populated"
            )
        except Exception as e:
            emit(f"Yahoo Finance Data ({ticker})", "fail", str(e))
            from app.models.financial_metrics import FinancialMetrics
            from app.models.stock import Stock
            financial_raw[ticker] = {
                "stock": Stock(ticker=ticker),
                "metrics": FinancialMetrics(ticker=ticker),
            }

    # ── Step 5: AI recommendation ──────────────────────────────────────────
    analysis_data = {}
    for ticker in tickers:
        try:
            from app.services.sentiment_service import average_sentiment
            from app.services.recommendation_service import generate_recommendation
            articles = news_data.get(ticker, [])
            avg_sent = average_sentiment(articles)
            stock = financial_raw[ticker]["stock"]
            metrics = financial_raw[ticker]["metrics"]
            recommendation = generate_recommendation(ticker, metrics, articles, avg_sent)
            analysis_data[ticker] = {
                "stock": stock.model_dump(),
                "metrics": metrics.model_dump(),
                "recommendation": recommendation,
                "avg_sentiment": avg_sent,
            }
            emit(
                f"AI Recommendation ({ticker})", "pass",
                f"{recommendation['recommendation']} · score {recommendation['final_score']}/100"
            )
        except Exception as e:
            emit(f"AI Recommendation ({ticker})", "fail", str(e))
            analysis_data[ticker] = {
                "stock": financial_raw[ticker]["stock"].model_dump(),
                "metrics": financial_raw[ticker]["metrics"].model_dump(),
                "recommendation": {"recommendation": "HOLD", "rationale": "Analysis unavailable.", "risks": [], "upsides": []},
                "avg_sentiment": 0.0,
            }

    # ── Step 6: Dashboard compilation ─────────────────────────────────────
    try:
        dashboard = DashboardAgent().run(request_id, tickers, news_data, analysis_data)
        emit("Dashboard Compilation", "pass", f"Report ready for {', '.join(tickers)}")
    except Exception as e:
        emit("Dashboard Compilation", "fail", str(e))
        raise

    logger.info(f"Workflow [{request_id}] completed successfully")
    return dashboard
