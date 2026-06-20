# News Scraping Skill

*Description:*  
Fetches and structures the latest financial news for a stock ticker.

*Responsibilities:*  
- Query Yahoo Finance search API for recent news headlines and summaries.  
- Normalize and deduplicate results into `NewsArticle` objects.  
- Handle fetch failures gracefully with fallback placeholder articles.

*Implementation:*  
`app/services/news_service.py` — `fetch_news(ticker, max_articles)` returns `List[NewsArticle]`.

*Usage:*  
Called by `NewsScraperAgent.run()` for each ticker before sentiment analysis.

*Data Source:*  
Yahoo Finance search API (`query2.finance.yahoo.com/v1/finance/search`) — no API key required.
