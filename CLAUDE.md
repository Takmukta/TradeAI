# CLAUDE.md

# TradeAI — Claude Code AI Integration and Architecture Documentation

---

## 1. Project Overview

TradeAI is a multi-agent trading assistant designed to:

- Accept user input specifying 1-2 stock tickers.
- Scrape relevant financial news for those tickers.
- Compute key financial ratios from Yahoo Finance data via MCP Server.
- Analyze news sentiment and generate trading recommendations.
- Present results on a dashboard with thorough explanations.

Claude Code AI is used as the core reasoning engine orchestrated via multiple dedicated agents, each encapsulating domain-specific skills.

---

## 2. Claude Code Model and Execution

- **Model:** TradeAI leverages Claude Code, an advanced AI designed for local execution and agent orchestration workflows rather than remote API calls.
- **Execution:**  
  Claude Code processes and chains prompts dynamically in the local environment, invoking agents and skills as code modules.
- **Benefits:**  
  - No dependency on remote Claude API keys or external calls.  
  - Full control over prompt composition, execution, and tooling interaction.  
  - Enhanced observability and debugging within the local runtime environment.

---

## 3. Detailed Multi-Agent Flow with Skills

| Step | Agent / Skill                            | Purpose & Role                                                                    | Tools / Integration                        |
|-------|----------------------------------------|-----------------------------------------------------------------------------------|--------------------------------------------|
| 1     | **User Input Agent**                    | Collect and validate user input stock tickers.                                   | Validation skill (inputValidationHook)     |
| 2     | **News Scraper Agent**                  | Scrape latest financial news for tickers, clean and prepare news snippets.       | Puppeteer / Apify Crawlers; scrapeHelpers  |
| 3     | **Sentiment Analysis Skill**            | Analyze sentiment of news snippets, scoring positive/negative/neutral impact.    | Claude Code prompts invoking sentiment skill |
| 4     | **MCP Server Client Skill**             | Query Yahoo Finance MCP Server to retrieve financial data and ratios.             | MCP Server querying skill (mcpClient)      |
| 5     | **Financial Analysis Agent**            | Calculate ratios, integrate news sentiment, apply rule-based governance policies.| financialCalculations + governanceHook     |
| 6     | **Recommendation Skill**                 | Generate buy/sell/hold recommendation with detailed explanations.                 | Claude Code prompts using recommendation_skill |
| 7     | **Dashboard Agent**                     | Aggregate all data and produce final report/dashboard for user consumption.       | Output formatting + outputValidationHook   |

---

## 4. Domain-Specific Skills

- **inputValidationHook:** Ensures user inputs are cleaned, valid tickers, sanitized to prevent injection.  
- **scrapeHelpers:** Reliable scraping functions for news extraction with formatting and de-duplication.  
- **sentimentAnalysisSkill:** Encodes sentiment analysis as reusable Claude Code prompt modules.  
- **mcpClient:** Interfaces with MCP Server to securely fetch financial data.  
- **financialCalculations:** Functions implementing formulae for P/E, Debt/Equity, ROE, etc.  
- **governanceHook:** Validates all decisions against financial and regulatory rules from MCP.  
- **recommendationSkill:** Standardized Claude prompt for consistency and explanation generation.  
- **auditHook:** Records detailed logs of data, prompts, and outputs for traceability and governance.  
- **outputValidationHook:** Ensures dashboard outputs are complete, consistent, and user-friendly.

---

## 5. Tools and Plugins Used

- **Claude Code:** Local AI orchestration and reasoning engine running the logic and prompt processing.  
- **MCP Server for Yahoo Finance:** Free read-only data source providing real-time and historical financial data.  
- **Apify Crawlers / Puppeteer:** For web scraping latest financial news.  
- **Apify Key-Value Store:** Storage of session data, audit logs, past recommendations, and intermediate data.  
- **OpenTelemetry (optional):** For tracing and monitoring execution flows in local environment.  
- **Locust:** Load testing tool simulating multiple user requests against your system.

---

## 6. Governance in Claude Code Workflow

- **Data Governance:**  
  - Input validation and PII detection applied consistently at intake via hooks.  
  - Audit hooks log all steps and decisions securely into KVS for accountability.  
  - Access control configured via environment variables and secure config.

- **AI Governance:**  
  - Prompts designed to always output rationale, enhancing explainability.  
  - Governance hook enforces compliance with policy rules from MCP Server prior to final decision.  
  - Human-in-the-loop strategy logs uncertain or borderline cases for manual review.  
  - Monitoring and evaluation modules measure fairness and reliability over time.

---

## 7. Prompt Engineering Practices with Claude Code

- Modular prompt templates stored and reused for consistency and ease of updates.  
- Clear, concise instructions with structured factual context (financial data + sentiment scores).  
- Explicit request for step-by-step reasoning and explanations.  
- Fallback instructions include sensible defaults if data missing or ambiguous.  
- Output format templates guarantee structured outputs suitable for dashboards.

---

## 8. Expected Result

- A fully autonomous multi-agent trading assistant that provides timely, accurate, and explainable buy/sell/hold recommendations for user-provided stock tickers.  
- Transparent and auditable decision trail supporting regulatory requirements.  
- Scalable architecture supporting additional stocks or metrics with minimal re-engineering.

---

## 9. Future Expansion

- Integrate additional financial data sources or premium datasets.  
- Enable interactive multi-turn conversations with users via Claude Code conversational agents.  
- Enhance governance with automated fairness bias detection.

---

# End of CLAUDE.md