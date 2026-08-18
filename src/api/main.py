import logging
import sqlite3
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "db" / "nifty100.db"

API_VERSION = "1.0.0"
START_TIME = time.time()


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("nifty100-api")


# ============================================================
# DATABASE CONNECTION
# ============================================================


def get_db_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Nifty 100 Financial Intelligence Platform API",
    description="REST API for Nifty 100 financial analytics.",
    version=API_VERSION,
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST LOGGING
# ============================================================


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    elapsed_time = time.time() - start_time

    logger.info(
        "%s %s - %.4f seconds",
        request.method,
        request.url.path,
        elapsed_time,
    )

    return response


# ============================================================
# HEALTH CHECK
# ============================================================


@app.get("/api/v1/health")
def health_check():

    tables = [
        "companies",
        "profitandloss",
        "balancesheet",
        "cashflow",
        "analysis",
        "documents",
        "prosandcons",
        "sectors",
        "stock_prices",
        "market_cap",
    ]

    db_row_counts = {}

    connection = get_db_connection()

    try:
        for table in tables:
            cursor = connection.execute(f"SELECT COUNT(*) FROM {table}")

            db_row_counts[table] = cursor.fetchone()[0]

    finally:
        connection.close()

    uptime_seconds = time.time() - START_TIME

    return {
        "status": "ok",
        "db_row_counts": db_row_counts,
        "uptime_seconds": round(uptime_seconds, 2),
        "version": API_VERSION,
    }


# ============================================================
# ROUTERS
# ============================================================

from src.api.routers import (
    companies,
    documents,
    health,
    peers,
    portfolio,
    screener,
    sectors,
    valuation,
)

app.include_router(companies.router, prefix="/api/v1")
app.include_router(screener.router, prefix="/api/v1")
app.include_router(sectors.router, prefix="/api/v1")
app.include_router(peers.router, prefix="/api/v1")
app.include_router(valuation.router, prefix="/api/v1")
app.include_router(portfolio.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")
