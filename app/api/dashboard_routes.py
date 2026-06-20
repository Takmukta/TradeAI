import json
import queue
import threading
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
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


@router.post("/analyze/stream")
def analyze_stream(body: AnalysisRequest):
    """
    SSE endpoint.  Streams step events as:
      data: {"type": "step",   "step": "...", "status": "pass|fail", "detail": "..."}
      data: {"type": "result", "data": { ...full dashboard... }}
      data: {"type": "error",  "message": "..."}
    """
    event_queue: queue.Queue = queue.Queue()

    def on_step(event: dict):
        event_queue.put({"type": "step", **event})

    def run():
        try:
            result = run_analysis(body.tickers, on_step=on_step)
            event_queue.put({"type": "result", "data": result})
        except Exception as e:
            event_queue.put({"type": "error", "message": str(e)})
        finally:
            event_queue.put(None)  # sentinel

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

    def event_generator():
        while True:
            item = event_queue.get()
            if item is None:
                break
            yield f"data: {json.dumps(item)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/health")
def health():
    return {"status": "ok", "service": "TradeAI"}
