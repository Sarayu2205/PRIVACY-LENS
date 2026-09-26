"""
PrivacyLens – FastAPI Application Entry Point
Run with: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import create_tables
from app.routes import auth, scan, history, dashboard, report

# ── Logging ───────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("PrivacyLens API starting up…")
    try:
        create_tables()
        logger.info("Database tables verified / created.")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        logger.warning("API will start but database operations will fail. Check DATABASE_URL.")
    yield
    logger.info("PrivacyLens API shutting down.")


# ── App ───────────────────────────────────────────────────────────────────
app = FastAPI(
    title="PrivacyLens API",
    description=(
        "AI-Based Detection and Prevention of Sensitive Data Exposure. "
        "B.Tech Cybersecurity Project."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(scan.router)
app.include_router(history.router)
app.include_router(dashboard.router)
app.include_router(report.router)


# ── Health check ──────────────────────────────────────────────────────────
@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "PrivacyLens API", "version": "1.0.0"}


# ── Global error handler ──────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again."},
    )
