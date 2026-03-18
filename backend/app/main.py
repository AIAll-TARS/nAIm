import time
import json
import os
from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_fastapi_instrumentator import Instrumentator
import structlog

from app.routers import services, ratings, crm, tools
import app.crm_models  # noqa: F401 — registers CRM tables with Base metadata

log = structlog.get_logger()

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

app = FastAPI(
    title="nAIm API",
    description=(
        "nAIm is a machine-first registry of AI agent API services. "
        "Agents can discover, compare, and rate APIs across categories like LLM, TTS, STT, "
        "embeddings, search, and AI safety tools. "
        "All public read endpoints are unauthenticated. "
        "Write endpoints require an X-API-Key header."
    ),
    version="1.0.0",
    contact={
        "name": "nAIm Registry",
        "url": "https://naim.janis7ewski.org",
        "email": "aiall@janis7ewski.org",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {"name": "services", "description": "Browse and register AI API services"},
        {"name": "ratings", "description": "Submit and retrieve service ratings"},
        {"name": "tools", "description": "Utility endpoints for AI agents"},
        {"name": "crm", "description": "Agent CRM — session tracking and interaction logs"},
        {"name": "meta", "description": "Health and meta endpoints"},
    ],
    servers=[
        {"url": "https://api.naim.janis7ewski.org", "description": "Production"},
    ],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

app.include_router(services.router)
app.include_router(ratings.router)
app.include_router(crm.router)
app.include_router(tools.router)

_start_time = time.time()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start) * 1000, 2)
    log.info(
        "request",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=duration_ms,
    )
    return response


@app.get("/openapi-public.json", include_in_schema=False)
def public_openapi():
    """Public OpenAPI spec — stripped of internal CRM and metrics routes. For apis.guru."""
    spec = app.openapi()
    skip = {"/metrics", "/v1/crm/sessions", "/v1/crm/agents",
            "/v1/crm/agents/{handle}/interactions"}
    public_paths = {}
    for path, methods in spec["paths"].items():
        if path in skip:
            continue
        if path == "/v1/categories":
            public_paths[path] = {"get": methods["get"]}
        else:
            public_paths[path] = methods
    spec = dict(spec)
    spec["paths"] = public_paths
    return JSONResponse(spec)


@app.get("/health", tags=["meta"])
def health():
    return {
        "status": "ok",
        "uptime_seconds": round(time.time() - _start_time),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
