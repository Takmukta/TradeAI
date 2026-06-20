// News Scraping Prompt Template
// Used to summarize and structure scraped news articles

const newsSummaryPrompt = (ticker, articles) => `
You are a financial news analyst. Summarize the following news articles about ${ticker}.

Articles:
${articles.map((a, i) => `[${i + 1}] ${a.title}: ${a.summary}`).join("\n")}

Provide:
1. A 2-3 sentence overall market narrative for ${ticker}
2. Notable positive catalysts
3. Notable risk factors

Return JSON with keys: narrative, catalysts, risks.
`;

module.exports = { newsSummaryPrompt };
