from fastapi import APIRouter, HTTPException
from app.services.financial_service import fetch_stock_info, fetch_financial_metrics

router = APIRouter(prefix="/financial", tags=["financial"])


@router.get("/{ticker}/info")
def get_stock_info(ticker: str):
    ticker = ticker.strip().upper()
    if not ticker.isalpha() or len(ticker) > 10:
        raise HTTPException(status_code=422, detail=f"Invalid ticker: {ticker}")
    stock = fetch_stock_info(ticker)
    return stock.model_dump()


@router.get("/{ticker}/metrics")
def get_metrics(ticker: str):
    ticker = ticker.strip().upper()
    if not ticker.isalpha() or len(ticker) > 10:
        raise HTTPException(status_code=422, detail=f"Invalid ticker: {ticker}")
    metrics = fetch_financial_metrics(ticker)
    return metrics.model_dump()
