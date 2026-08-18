import sqlite3
from pathlib import Path

import requests
from fastapi import APIRouter, HTTPException

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[3]
DB_PATH = BASE_DIR / "db" / "nifty100.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/companies/{ticker}/documents")
def get_company_documents(ticker: str):
    """
    Return annual report links for a company
    with URL validity status.
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
                annual_report
            FROM documents
            WHERE company_id = ?
            ORDER BY year DESC
            """,
            (company["id"],),
        ).fetchall()

        reports = []

        for row in rows:
            url = row["annual_report"]

            is_url_valid = False

            if url:
                try:
                    response = requests.head(
                        url,
                        timeout=5,
                        allow_redirects=True,
                    )

                    is_url_valid = response.status_code < 400

                except requests.RequestException:
                    is_url_valid = False

            reports.append(
                {
                    "year": row["year"],
                    "annual_report": url,
                    "is_url_valid": is_url_valid,
                }
            )

        return {
            "company_id": company["id"],
            "company_name": company["company_name"],
            "count": len(reports),
            "documents": reports,
        }

    finally:
        conn.close()
