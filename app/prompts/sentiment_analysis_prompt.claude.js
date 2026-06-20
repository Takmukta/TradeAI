// Sentiment Analysis Prompt Template
// Used to score news article sentiment for financial impact

const sentimentPrompt = (articles) => `
Analyze the investment sentiment of each news snippet below.
For each item return a JSON array: [{"index": 1, "score": <-1.0 to 1.0>, "label": "<positive|neutral|negative>"}]

Score guide:
- +1.0 = strongly bullish (earnings beat, major contract win, strong guidance)
-  0.0 = neutral (routine announcements, mixed signals)
- -1.0 = strongly bearish (earnings miss, legal trouble, CEO resignation, recession fears)

News snippets:
${articles.map((a, i) => `[${i + 1}] ${a.title}: ${a.summary?.slice(0, 300)}`).join("\n")}

Return ONLY the JSON array, no other text.
`;

module.exports = { sentimentPrompt };
