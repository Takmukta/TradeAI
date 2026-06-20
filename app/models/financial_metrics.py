from pydantic import BaseModel
from typing import Optional


class FinancialMetrics(BaseModel):
    ticker: str
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    debt_to_equity: Optional[float] = None
    roe: Optional[float] = None
    roa: Optional[float] = None
    current_ratio: Optional[float] = None
    eps: Optional[float] = None
    revenue_growth: Optional[float] = None
    profit_margin: Optional[float] = None
    dividend_yield: Optional[float] = None
    beta: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    avg_volume: Optional[float] = None
