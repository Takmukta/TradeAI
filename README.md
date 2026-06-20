# TradeAI

Multi-agent stock analysis dashboard powered by Claude AI. Enter 1–2 stock tickers to get live news sentiment, financial metrics, and a BUY / HOLD / SELL recommendation.

## Setup & Run Locally

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/TradeAI.git
cd TradeAI
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your Anthropic API key
```bash
cp .env.example .env
# Edit .env and paste your key:
# ANTHROPIC_API_KEY=sk-ant-...
```

Get a free API key at https://console.anthropic.com

### 4. Start the app
```bash
bash run.sh
```

Or run directly:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

### 5. Open in your browser
```
http://localhost:8080
```

---

## Project Structure

```
TradeAI/
├── app/
│   ├── agents/          # User input, news scraper, financial analysis, dashboard agents
│   ├── api/             # FastAPI route handlers
│   ├── models/          # Pydantic data models
│   ├── orchestrator/    # Multi-agent workflow pipeline
│   ├── services/        # News, financial, sentiment, recommendation services
│   ├── static/          # Frontend (index.html)
│   ├── utils/           # Validators, calculations, logger
│   └── main.py          # FastAPI app entry point
├── requirements.txt
├── run.sh
└── .env.example
```

## Requirements

- Python 3.9+
- An [Anthropic API key](https://console.anthropic.com)
