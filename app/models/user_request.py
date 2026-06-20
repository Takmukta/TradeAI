from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime
from app.utils.ticker_normalizer import get_valid_ticker, VALID_TICKER_RE


class UserRequest(BaseModel):
    tickers: List[str]
    request_id: Optional[str] = None
    created_at: Optional[datetime] = None

    @field_validator("tickers")
    @classmethod
    def validate_tickers(cls, v: List[str]) -> List[str]:
        if len(v) < 1 or len(v) > 2:
            raise ValueError("Provide 1 or 2 stock tickers")
        normalized = []
        for t in v:
            resolved = get_valid_ticker(t)
            if not VALID_TICKER_RE.match(resolved):
                raise ValueError(f"'{t}' could not be resolved to a valid ticker symbol")
            normalized.append(resolved)
        return normalized


class AnalysisResponse(BaseModel):
    request_id: str
    tickers: List[str]
    recommendations: dict
    news_summary: dict
    financial_metrics: dict
    generated_at: datetime
