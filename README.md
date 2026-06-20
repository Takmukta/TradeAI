# TradeAI

A multi-agent stock analysis dashboard powered by Claude AI. Enter 1–2 stock names or ticker symbols to get live news sentiment, financial ratios, and an AI-generated BUY / HOLD / SELL recommendation — with a real-time pipeline progress screen showing every step as it completes.

---

## 1. Project Description

TradeAI is a fully autonomous trading assistant built on a multi-agent architecture. When a user submits a stock name (e.g. "Apple" or "NVIDIA") or ticker symbol (e.g. "AAPL"), the system:

1. **Resolves** the input to a valid ticker via a two-tier normalization hook (local company map → Yahoo Finance autocomplete fallback).
2. **Scrapes** the latest financial news headlines using Bing News RSS, with Yahoo Finance RSS as a fallback.
3. **Scores** news sentiment using Claude AI (positive / neutral / negative per article).
4. **Fetches** live financial ratios from Yahoo Finance (P/E, ROE, EPS, Debt/Equity, etc.).
5. **Generates** a BUY / HOLD / SELL recommendation using Claude AI with professional analyst guardrails.
6. **Presents** results on a dark-themed dashboard with Analysis, Metrics, and News tabs per stock.

A real-time pipeline progress panel streams each step to the screen as it completes, with a PASSED / FAILED badge so the user can track exactly what is happening.

---

## 2. APIs and MCP Servers Used

### Anthropic Claude API
- **Model:** `claude-haiku-4-5-20251001`
- **Used for:**
  - News sentiment scoring — batches up to 8 headlines and returns a JSON array of sentiment scores (-1.0 to +1.0).
  - Trading recommendation generation — takes financial metrics + news summary and outputs BUY / HOLD / SELL with rationale, risks, and upsides.

### Yahoo Finance (via `yfinance` Python library)
- Direct Python calls to Yahoo Finance for stock fundamentals. No API key required.
- See Section 3 for the full list of data fields fetched.

### MCP Servers (configured in `.mcp.json`)

| MCP Server | Package | Purpose |
|---|---|---|
| **Apify MCP Server** | `@apify/actors-mcp-server` | Access to Apify's web scraping Actor marketplace, including news crawlers and data extraction tools |
| **Yahoo Finance MCP Server** | `yahoo-finance-mcp-server` | Structured access to Yahoo Finance data (quotes, financials, historical prices) via MCP protocol |

> MCP servers are configured for Claude Code integration. Set your `APIFY_TOKEN` in `.mcp.json` to enable Apify-powered scraping.

---

## 3. Data Pulled from Each Source

### From Yahoo Finance (`yfinance` / Yahoo Finance MCP)

| Field | Yahoo Finance Key | Description |
|---|---|---|
| P/E Ratio | `trailingPE` / `forwardPE` | Price-to-Earnings ratio |
| P/B Ratio | `priceToBook` | Price-to-Book ratio |
| EPS | `trailingEps` | Earnings per share |
| ROE | `returnOnEquity` | Return on equity |
| ROA | `returnOnAssets` | Return on assets |
| Profit Margin | `profitMargins` | Net profit margin |
| Revenue Growth | `revenueGrowth` | YoY revenue growth rate |
| Debt / Equity | `debtToEquity` | Leverage ratio |
| Current Ratio | `currentRatio` | Short-term liquidity |
| Beta | `beta` | Market volatility relative to S&P 500 |
| Dividend Yield | `dividendYield` | Annual dividend as % of price |
| 52-Week High/Low | `fiftyTwoWeekHigh` / `fiftyTwoWeekLow` | Annual price range |
| Average Volume | `averageVolume` | 3-month average daily volume |
| Company Name | `longName` / `shortName` | Full company name |
| Current Price | `currentPrice` | Latest market price |
| Market Cap | `marketCap` | Total market capitalisation |
| Sector | `sector` | Industry sector classification |

### From Bing News RSS (primary) / Yahoo Finance RSS (fallback)

- Headline titles (up to 10 per ticker)
- Article summaries
- Publication timestamps
- Source publication name
- Article URL

### From Apify (via MCP Server)
Available as an optional extension for more advanced scraping use cases (e.g. paywalled financial news, social media sentiment, SEC filings) through Apify's Actor marketplace.

---

## 4. Hooks and Guardrails

### Input Validation Hook — `app/utils/validators.py`
Runs on every user submission before any external call is made.
- Rejects empty input and enforces a maximum of 2 tickers per request.
- Passes each input through the ticker normalizer before format validation.
- **Decision impact:** Prevents malformed or injected inputs from reaching downstream agents.

### Ticker Normalization Hook — `app/utils/ticker_normalizer.py`
Two-tier resolution before touching any financial API:
- **Tier 1 (Local Map):** 50+ hardcoded company name → ticker mappings (e.g. `"apple" → "AAPL"`, `"nvidia" → "NVDA"`). Zero network latency.
- **Tier 2 (Yahoo Autocomplete):** If Tier 1 misses, queries `query2.finance.yahoo.com/v1/finance/search` to resolve the closest equity match dynamically (e.g. `"Snowflake" → "SNOW"`).
- **Fallback:** Returns uppercased raw input if both tiers fail.
- **Decision impact:** Ensures the correct company data is always fetched regardless of how the user spells the name.

### Financial Analysis Guardrails — `app/utils/calculations.py` + `app/services/recommendation_service.py`
Every recommendation is evaluated against industry-standard benchmark thresholds before being passed to Claude:

| Metric | BUY Signal | SELL Signal |
|---|---|---|
| P/E Ratio | < 15 | > 25 (> 40 = heavy penalty) |
| P/B Ratio | < 1.5 | > 3.0 |
| ROE | > 15% | < 8% |
| Profit Margin | > 10% | < 5% |
| Revenue Growth | > 10% YoY | Negative |
| Debt / Equity | < 1.0 | > 2.0 |
| Current Ratio | 1.5 – 3.0 | < 1.0 |

A quantitative **valuation score** (0–100) is derived from these thresholds and combined with a **sentiment score** (60% valuation / 40% sentiment weighting) to produce a **final score**. The Claude prompt includes the full guardrail matrix so the LLM reasons against the same benchmarks explicitly.

**Final Decision Logic:**
- **BUY (≥ 65):** Strong valuation or growth metrics with neutral-to-positive news sentiment.
- **HOLD (45–64):** Mixed metrics, fair-value zone, or ambiguous/insufficient data.
- **SELL (< 45):** Balance sheet red flags (Debt/Equity > 2.0, Current Ratio < 1.0), negative growth, or highly negative sentiment.

### Input Sanitization Hook — `app/utils/validators.py` (`sanitize_string`)
Strips dangerous characters (`<`, `>`, `"`, `'`, `;`, `&`, `|`, `` ` ``, `$`, `\`) from any free-text input to prevent injection attacks before data reaches any service.

### Governance / Audit Hook — `app/utils/logger.py` (`audit_log`)
Every significant decision point is written to the audit log:

| Event | Trigger |
|---|---|
| `user_input_validated` | Tickers accepted after normalization |
| `news_fetched` | Source and article count per ticker |
| `financial_metrics_fetched` | Successful Yahoo Finance call |
| `recommendation_generated` | Final recommendation and ticker |
| `dashboard_generated` | Request ID and tickers for full run |

---

## 5. Tracing and Observing Activities

### Structured Application Logging — `app/utils/logger.py`
Every module uses a named logger (`get_logger(__name__)`) producing timestamped structured log lines:
```
2026-06-20 07:00:12,345 | INFO | app.services.news_service | Tier 1 matched 'Apple' -> AAPL
2026-06-20 07:00:14,201 | INFO | app.services.financial_service | financial_metrics_fetched for AAPL
```

Log levels:
- `DEBUG` — internal routing decisions (ticker format checks)
- `INFO` — normal pipeline progress (news fetched, metrics loaded)
- `WARNING` — recoverable failures (Bing news timeout, LLM fallback triggered)
- `ERROR` — unexpected failures with full exception context

### Real-Time Pipeline Progress Screen (frontend)
When the user clicks Analyze, the dashboard streams live step events over **Server-Sent Events (SSE)** from the `/dashboard/analyze/stream` endpoint. Each pipeline step appears in the UI with:
- **RUNNING** badge (animated spinner) while in progress
- **PASSED** (green) or **FAILED** (red) badge on completion
- A human-readable detail message per step

Steps streamed to the UI per analysis run (up to 10 events for 2 tickers):

| Step | Example detail |
|---|---|
| Input Validation & Ticker Resolution | `Apple → AAPL, NVIDIA → NVDA` |
| News Fetch (per ticker) | `10 articles retrieved` |
| Sentiment Analysis (per ticker) | `10 articles scored` |
| Yahoo Finance Data (per ticker) | `Apple Inc. · 9/9 key metrics populated` |
| AI Recommendation (per ticker) | `HOLD · score 55.2/100` |
| Dashboard Compilation | `Report ready for AAPL, NVDA` |

### Audit Log
`audit_log(event, payload)` writes a JSON-structured record for every critical decision point, enabling post-hoc traceability of what data drove each recommendation.

---

## 6. Evaluation Metrics

### Quantitative Scoring

| Metric | Range | How it is calculated |
|---|---|---|
| **Valuation Score** | 0 – 100 | Weighted sum of signals from P/E, P/B, ROE, Profit Margin, Revenue Growth, Debt/Equity, and Current Ratio against industry benchmarks |
| **Sentiment Score** | 0 – 100 | Average Claude sentiment score across all articles for the ticker, normalised from [−1, +1] to [0, 100] |
| **Final Score** | 0 – 100 | `0.6 × Valuation Score + 0.4 × Sentiment Score` |

### Recommendation Thresholds
- **BUY** — Final Score ≥ 65
- **HOLD** — Final Score 45 – 64
- **SELL** — Final Score < 45

### News Quality Indicators
- Articles retrieved per ticker (target: ≥ 5 for reliable sentiment averaging)
- Sentiment label distribution shown in the News tab (positive / neutral / negative)
- Source used: Bing News RSS (primary) or Yahoo Finance RSS (fallback)

### Pipeline Health (visible per run in the progress screen)
- Steps passed vs failed out of the total step events emitted
- Number of financial metrics populated out of 9 key fields (shown in Yahoo Finance step detail)
- Whether LLM recommendation succeeded or fell back to rule-based scoring (logged as WARNING)

---

## 7. Local Deployment

### Prerequisites
- Python 3.9+
- Node.js (for `localtunnel` public URL — optional)
- An [Anthropic API key](https://console.anthropic.com)

### Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/Takmukta/TradeAI.git
cd TradeAI

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your API key
cp .env.example .env
# Open .env and set:
# ANTHROPIC_API_KEY=sk-ant-...

# 5. Start the server
bash run.sh
# or directly:
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

### Local Access
```
http://localhost:8080
```

### Public Shareable Link (optional)
To share a temporary public URL without deploying to a server, run this in a second terminal while the app is running:

```bash
npx localtunnel --port 8080
# Prints something like: your url is: https://some-name.loca.lt
```

Open the printed URL in any browser. The link is active as long as the tunnel process is running. Re-running the command generates a new URL.

> **Note:** On first visit, localtunnel shows a one-click splash page — click through to reach the app.

---

## Project Structure

```
TradeAI/
├── app/
│   ├── agents/              # UserInputAgent, NewsScraperAgent,
│   │                        # FinancialAnalysisAgent, DashboardAgent
│   ├── api/                 # FastAPI route handlers (dashboard, news, financial)
│   ├── models/              # Pydantic models (Stock, UserRequest,
│   │                        # FinancialMetrics, NewsArticle)
│   ├── orchestrator/        # workflow.py — chains all agents, emits SSE step events
│   ├── services/            # financial_service, news_service,
│   │                        # sentiment_service, recommendation_service
│   ├── static/              # Single-page frontend (index.html)
│   ├── utils/               # validators.py, ticker_normalizer.py,
│   │                        # calculations.py, logger.py
│   └── main.py              # FastAPI app entry point
├── .env.example
├── requirements.txt
├── run.sh
└── README.md
```

---

## Requirements

- Python 3.9+
- Anthropic API key — [get one free](https://console.anthropic.com)
- All Python packages in `requirements.txt` (FastAPI, uvicorn, yfinance, httpx, anthropic, pydantic)

---

*TradeAI is for informational purposes only. Not financial advice.*
