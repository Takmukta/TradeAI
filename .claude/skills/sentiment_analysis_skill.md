# Sentiment Analysis Skill

*Description:*  
Scores news article sentiment for financial impact using Claude AI.

*Responsibilities:*  
- Send batched news snippets to Claude in a single prompt.  
- Parse returned JSON array of per-article sentiment scores (-1 to +1).  
- Assign `sentiment_score` and `sentiment_label` to each `NewsArticle`.  
- Default to neutral (0.0) if LLM call fails.

*Implementation:*  
`app/services/sentiment_service.py` — `analyze_sentiment(articles)` and `average_sentiment(articles)`.

*Model:*  
Uses `claude-haiku-4-5-20251001` for fast, cost-efficient batch scoring.

*Score Labels:*  
- positive: score > 0.2  
- neutral: -0.2 ≤ score ≤ 0.2  
- negative: score < -0.2
