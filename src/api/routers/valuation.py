import sqlite3
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[3]
DB_PATH = BASE_DIR / "db" / "nifty100.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/market-cap/{ticker}")
def get_market_cap_history(ticker: str):
    """
    Return historical valuation multiples from 2019 to 2024.
    """

    conn = get_db_connection()

    try:
        company = conn.execute(
            """
            SELECT id, company_name
            FROM companies
            WHERE UPPER(id) = UPPER(?)
            """,
            (ticker,),
        ).fetchone()

        if company is None:
            raise HTTPException(
                status_code=404,
                detail=f"Company not found: {ticker}",
            )

        rows = conn.execute(
            """
            SELECT
                year,
                market_cap_crore,
                enterprise_value_crore,
                pe_ratio,
                pb_ratio,
                ev_ebitda,
                dividend_yield_pct
            FROM market_cap
            WHERE company_id = ?
              AND year BETWEEN 2019 AND 2024
            ORDER BY year
            """,
            (company["id"],),
        ).fetchall()

        history = [dict(row) for row in rows]

        return {
            "company_id": company["id"],
            "company_name": company["company_name"],
            "count": len(history),
            "history": history,
        }

    finally:
        conn.close()