# User Input Agent

*Role:*  
Receives and validates user input specifying the stock tickers for analysis.

*Responsibilities:*  
- Validate stock ticker formats.  
- Sanitize inputs to prevent injection or errors.  
- Pass valid inputs to News Scraper Agent.

*Interactions:*  
- Calls input validation hook.  
- Sends validated ticker list downstream.