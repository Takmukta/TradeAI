// Financial Analysis Prompt Template
// Used by FinancialAnalysisAgent to generate structured analysis from metrics data

const financialAnalysisPrompt = (ticker, metrics) => `
You are a senior financial analyst. Analyze the following financial metrics for ${ticker}
and provide a structured assessment.

Financial Metrics:
- P/E Ratio: ${metrics.pe_ratio ?? "N/A"}
- P/B Ratio: ${metrics.pb_ratio ?? "N/A"}
- Debt/Equity: ${metrics.debt_to_equity ?? "N/A"}
- ROE: ${metrics.roe ?? "N/A"}
- ROA: ${metrics.roa ?? "N/A"}
- Current Ratio: ${metrics.current_ratio ?? "N/A"}
- EPS: ${metrics.eps ?? "N/A"}
- Profit Margin: ${metrics.profit_margin ?? "N/A"}
- Revenue Growth: ${metrics.revenue_growth ?? "N/A"}
- Beta: ${metrics.beta ?? "N/A"}

Provide:
1. Valuation assessment (overvalued/fairly valued/undervalued)
2. Financial health assessment
3. Growth outlook
4. Key concerns

Format your response as JSON with keys: valuation, health, growth, concerns.
`;

module.exports = { financialAnalysisPrompt };
