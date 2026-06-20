from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime


class UserRequest(BaseModel):
    tickers: List[str]
    request_id: Optional[str] = None
    created_at: Optional[datetime] = None

    @field_validator("tickers")
    @classmethod
    def validate_tickers(cls, v: List[str]) -> List[str]:
        if len(v) < 1 or len(v) > 2:
            raise ValueError("Provide 1 or 2 stock tickers")
        cleaned = []
        for t in v:
            t = t.strip().upper()
            if not t.isalpha() or len(t) > 5:
                raise ValueError(f"Invalid ticker: {t}")
            cleaned.append(t)
        return cleaned


class AnalysisResponse(BaseModel):
    request_id: str
    tickers: List[str]
    recommendations: dict
    news_summary: dict
    financial_metrics: dict
    generated_at: datetime
