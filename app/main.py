from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api import user_input_routes, news_routes, financial_analysis_routes, dashboard_routes

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(
    title="TradeAI",
    description="Multi-agent trading assistant powered by Claude AI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_input_routes.router)
app.include_router(news_routes.router)
app.include_router(financial_analysis_routes.router)
app.include_router(dashboard_routes.router)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def root():
    return FileResponse(STATIC_DIR / "index.html")
