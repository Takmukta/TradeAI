from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.orchestrator.workflow import run_analysis

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class AnalysisRequest(BaseModel):
    tickers: List[str]


@router.post("/analyze")
def analyze(body: AnalysisRequest):
    try:
        result = run_analysis(body.tickers)
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/health")
def health():
    return {"status": "ok", "service": "TradeAI"}
