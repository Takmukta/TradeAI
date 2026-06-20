# Financial Analysis Skill

*Description:*  
Calculates key financial ratios and scores to assess stock investment attractiveness.

*Responsibilities:*  
- Compute valuation score from P/E, P/B, Debt/Equity, ROE, profit margin.  
- Normalize scores to 0–100 scale for comparison.  
- Provide numerical context for recommendation decisions.

*Implementation:*  
`app/utils/calculations.py` — `score_valuation(metrics)` returns float 0–100.  
`app/services/financial_service.py` — fetches metrics via yfinance.

*Usage:*  
Called by `FinancialAnalysisAgent.run()` for each ticker.

*Scoring Logic:*  
- P/E < 15 → +15pts, P/E > 40 → -15pts  
- Debt/Equity < 0.5 → +10pts, > 2.0 → -10pts  
- ROE > 20% → +10pts  
- Profit margin > 20% → +5pts, negative → -10pts
