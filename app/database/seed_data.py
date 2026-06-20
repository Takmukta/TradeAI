from app.database.db import kv_set


def seed():
    kv_set("sample_tickers", ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"])
    kv_set("config", {
        "max_news_articles": 10,
        "sentiment_threshold_positive": 0.2,
        "sentiment_threshold_negative": -0.2,
        "recommendation_weights": {"valuation": 0.6, "sentiment": 0.4},
    })
    print("Seed data loaded.")


if __name__ == "__main__":
    seed()
