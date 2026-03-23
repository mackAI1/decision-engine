from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import uuid

from app.routers import analyze, signal, summarize, recommend, webhooks
from app.middleware.auth import APIKeyMiddleware
from app.middleware.logging import LoggingMiddleware

app = FastAPI(
    title="Decision Engine API",
    description="AI-powered backend for decision-making, signal generation, and data analysis.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)
app.add_middleware(APIKeyMiddleware)

app.include_router(analyze.router, prefix="/v1/analyze", tags=["Analysis"])
app.include_router(signal.router, prefix="/v1/signal", tags=["Signals"])
app.include_router(summarize.router, prefix="/v1/summarize", tags=["Summarize"])
app.include_router(recommend.router, prefix="/v1/recommend", tags=["Recommend"])
app.include_router(webhooks.router, prefix="/v1/webhooks", tags=["Webhooks"])


@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": time.time()}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": str(exc),
            "request_id": str(uuid.uuid4()),
        },
    )
