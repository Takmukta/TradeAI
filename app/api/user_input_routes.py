from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.utils.validators import validate_tickers

router = APIRouter(prefix="/input", tags=["input"])


class TickerInput(BaseModel):
    tickers: List[str]


@router.post("/validate")
def validate_input(body: TickerInput):
    try:
        cleaned = validate_tickers(body.tickers)
        return {"valid": True, "tickers": cleaned}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
