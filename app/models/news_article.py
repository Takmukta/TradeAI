from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NewsArticle(BaseModel):
    ticker: str
    title: str
    summary: str
    url: Optional[str] = None
    source: Optional[str] = None
    published_at: Optional[datetime] = None
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
