# Recommendation Skill

*Description:*  
Generates BUY / HOLD / SELL recommendations with rationale using Claude AI.

*Responsibilities:*  
- Combine valuation score and news sentiment score into a final composite score.  
- Call Claude (`claude-haiku-4-5-20251001`) with a structured prompt for LLM-generated rationale.  
- Fall back to rule-based recommendation if LLM call fails.  
- Return structured dict with recommendation, rationale, risks, upsides, and scores.

*Implementation:*  
`app/services/recommendation_service.py` — `generate_recommendation(ticker, metrics, articles, avg_sentiment)`.

*Scoring Weights:*  
- Valuation score: 60%  
- Sentiment score: 40%  
- BUY if composite ≥ 65, HOLD if 45–64, SELL if < 45
