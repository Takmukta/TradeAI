from pydantic import BaseModel, field_validator
from typing import Optional


class Stock(BaseModel):
    ticker: str
    company_name: Optional[str] = None
    sector: Optional[str] = None
    current_price: Optional[float] = None
    market_cap: Optional[float] = None

    @field_validator("ticker")
    @classmethod
    def ticker_must_be_valid(cls, v: str) -> str:
        v = v.strip().upper()
        if not v.isalpha() or len(v) > 5:
            raise ValueError(f"Invalid ticker symbol: {v}")
        return v
