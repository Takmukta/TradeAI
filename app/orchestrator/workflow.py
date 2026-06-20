import uuid
from typing import List
from app.agents.user_input_agent import UserInputAgent
from app.agents.news_scraper_agent import NewsScraperAgent
from app.agents.financial_analysis_agent import FinancialAnalysisAgent
from app.agents.dashboard_agent import DashboardAgent
from app.utils.logger import get_logger

logger = get_logger(__name__)


def run_analysis(raw_tickers: List[str]) -> dict:
    """
    Orchestrates the full TradeAI pipeline:
    1. Validate user input
    2. Scrape news + analyze sentiment
    3. Fetch financial data + generate recommendations
    4. Compile dashboard
    """
    request_id = str(uuid.uuid4())
    logger.info(f"Starting analysis workflow [{request_id}] for {raw_tickers}")

    # Step 1 — validate input
    tickers = UserInputAgent().run(raw_tickers)

    # Step 2 — news scraping + sentiment
    news_data = NewsScraperAgent().run(tickers)

    # Step 3 — financial analysis + recommendations
    analysis_data = FinancialAnalysisAgent().run(tickers, news_data)

    # Step 4 — dashboard compilation
    dashboard = DashboardAgent().run(request_id, tickers, news_data, analysis_data)

    logger.info(f"Workflow [{request_id}] completed successfully")
    return dashboard
