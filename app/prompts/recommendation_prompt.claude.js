// Recommendation Prompt Template
// Used by RecommendationSkill to generate BUY/SELL/HOLD with rationale

const recommendationPrompt = (ticker, metrics, avgSentiment, valuationScore) => `
You are a professional investment analyst. Based on the data below, generate a trading recommendation for ${ticker}.

Quantitative Scores:
- Valuation Score: ${valuationScore}/100 (higher = more attractive)
- Sentiment Score: ${((avgSentiment + 1) / 2 * 100).toFixed(1)}/100

Key Metrics:
- P/E: ${metrics.pe_ratio ?? "N/A"}, ROE: ${metrics.roe ?? "N/A"}, Debt/Equity: ${metrics.debt_to_equity ?? "N/A"}
- EPS: ${metrics.eps ?? "N/A"}, Profit Margin: ${metrics.profit_margin ?? "N/A"}
- Beta: ${metrics.beta ?? "N/A"}

Respond with JSON: { "recommendation": "BUY|HOLD|SELL", "rationale": "...", "risks": [...], "upsides": [...] }
`;

module.exports = { recommendationPrompt };
