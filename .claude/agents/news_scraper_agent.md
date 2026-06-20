# News Scraper Agent

*Role:*  
Scrapes latest financial news articles related to provided stock tickers.

*Responsibilities:*  
- Fetch news using Apify crawlers or web search plugin.  
- Normalize and filter news content.  
- Provide news snippets for sentiment analysis.

*Interactions:*  
- Uses news_scraping_skill.  
- Audits scraping events.  
- Sends cleaned data to Financial Analysis Agent.