"""
FastAPI application entry point.
"""

import json
import logging
import logging.handlers
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.gzip import GZipMiddleware

from app.core import settings
from app.core.mongodb import MongoDB
from app.core.redis import close_redis
from app.core.database import engine, Base
from app.routers import sites, pages, blocks, uploads, auth, logs

# ============================================
# File-based logging setup
# ============================================
LOG_FILE = "/tmp/app.log"

def setup_file_logging():
    """Configure rotating file handler so /api/v1/logs/app can read logs."""
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)

    # Attach to root logger so all app logs are captured
    root = logging.getLogger()
    root.addHandler(file_handler)
    root.setLevel(logging.INFO)

    # Also attach to uvicorn loggers
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uv_logger = logging.getLogger(name)
        uv_logger.addHandler(file_handler)

setup_file_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown events."""
    # Startup
    MongoDB.connect()

    # Ensure tables exist (checkfirst=True skips existing tables)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all, checkfirst=True)
    except Exception as e:
        logging.getLogger("uvicorn.error").warning(f"Migrations warning - check logs: {e}")

    yield

    # Shutdown
    MongoDB.close()
    await close_redis()
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    docs_url="/api/v1/docs",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
)

# CORS
origins = json.loads(settings.CORS_ORIGINS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gzip
app.add_middleware(GZipMiddleware, minimum_size=1000)

logger = logging.getLogger("uvicorn.error")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Return detailed JSON error instead of plain 'Internal Server Error'."""
    tb = traceback.format_exc()
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}\n{tb}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "type": type(exc).__name__,
            "path": str(request.url.path),
        },
    )


# Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(sites.router, prefix="/api/v1")
app.include_router(pages.router, prefix="/api/v1")
app.include_router(blocks.router, prefix="/api/v1")
app.include_router(uploads.router, prefix="/api/v1")
app.include_router(logs.router, prefix="/api/v1")


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": settings.APP_NAME}


@app.get("/api/v1/server-info")
async def server_info():
    """Return server IP for DNS configuration instructions."""
    from app.core.ip_detect import get_server_ip
    ip = await get_server_ip()
    return {"serverIp": ip or ""}
