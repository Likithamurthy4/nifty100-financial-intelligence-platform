import sqlite3
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[3]
DB_PATH = BASE_DIR / "db" / "nifty100.db"


def get_db_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


@router.get("/screener")
def screen_companies(
    min_roe: Optional[float] = Query(None),
    max_de: Optional[float] = Query(None),
    min_fcf: Optional[float] = Query(None),
    sector: Optional[str] = Query(None),
    min_rev_cagr_5yr: Optional[float] = Query(None),
    min_pat_cagr_5yr: Optional[float] = Query(None),
    max_pe: Optional[float] = Query(None),
):
    """
    Screen companies using latest financial ratios
    and latest valuation data.
    """

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if min_roe is not None and min_roe < 0:
        raise HTTPException(
            status_code=400,
            detail="min_roe cannot be negative.",
        )

    if max_de is not None and max_de < 0:
        raise HTTPException(
            status_code=400,
            detail="max_de cannot be negative.",
        )

    if min_fcf is not None and min_fcf < 0:
        raise HTTPException(
            status_code=400,
            detail="min_fcf cannot be negative.",
        )

    if min_rev_cagr_5yr is not None and min_rev_cagr_5yr < -100:
        raise HTTPException(
            status_code=400,
            detail="min_rev_cagr_5yr must be at least -100.",
        )

    if min_pat_cagr_5yr is not None and min_pat_cagr_5yr < -100:
        raise HTTPException(
            status_code=400,
            detail="min_pat_cagr_5yr must be at least -100.",
        )

    if max_pe is not None and max_pe <= 0:
        raise HTTPException(
            status_code=400,
            detail="max_pe must be greater than 0.",
        )

    connection = get_db_connection()

    try:
        query = """
            WITH latest_ratios AS (
                SELECT *
                FROM financial_ratios fr
                WHERE fr.year = (
                    SELECT MAX(fr2.year)
                    FROM financial_ratios fr2
                    WHERE fr2.company_id = fr.company_id
                )
            ),
            latest_valuation AS (
                SELECT *
                FROM market_cap mc
                WHERE mc.year = (
                    SELECT MAX(mc2.year)
                    FROM market_cap mc2
                    WHERE mc2.company_id = mc.company_id
                )
            )
            SELECT
                c.id,
                c.company_name,
                s.broad_sector,
                s.sub_sector,
                s.market_cap_category,

                r.year AS ratio_year,
                r.return_on_equity_pct AS roe_pct,
                r.debt_to_equity,
                r.free_cash_flow_cr,
                r.revenue_cagr_5yr,
                r.pat_cagr_5yr,
                r.eps_cagr_5yr,
                r.net_profit_margin_pct,
                r.operating_profit_margin_pct,
                r.interest_coverage,
                r.asset_turnover,

                v.year AS valuation_year,
                v.pe_ratio,
                v.pb_ratio,
                v.ev_ebitda,
                v.dividend_yield_pct,
                v.market_cap_crore,
                v.enterprise_value_crore

            FROM companies c

            LEFT JOIN sectors s
                ON c.id = s.company_id

            LEFT JOIN latest_ratios r
                ON c.id = r.company_id

            LEFT JOIN latest_valuation v
                ON c.id = v.company_id

            WHERE 1 = 1
        """

        parameters = []

        if min_roe is not None:
            query += """
                AND r.return_on_equity_pct >= ?
            """
            parameters.append(min_roe)

        if max_de is not None:
            query += """
                AND r.debt_to_equity <= ?
            """
            parameters.append(max_de)

        if min_fcf is not None:
            query += """
                AND r.free_cash_flow_cr >= ?
            """
            parameters.append(min_fcf)

        if sector:
            query += """
                AND LOWER(s.broad_sector) = LOWER(?)
            """
            parameters.append(sector)

        if min_rev_cagr_5yr is not None:
            query += """
                AND r.revenue_cagr_5yr >= ?
            """
            parameters.append(min_rev_cagr_5yr)

        if min_pat_cagr_5yr is not None:
            query += """
                AND r.pat_cagr_5yr >= ?
            """
            parameters.append(min_pat_cagr_5yr)

        if max_pe is not None:
            query += """
                AND v.pe_ratio <= ?
            """
            parameters.append(max_pe)

        query += """
            ORDER BY
                r.return_on_equity_pct DESC,
                r.revenue_cagr_5yr DESC,
                r.pat_cagr_5yr DESC
        """

        rows = connection.execute(
            query,
            parameters,
        ).fetchall()

        companies = [dict(row) for row in rows]

        return {
            "count": len(companies),
            "filters": {
                "min_roe": min_roe,
                "max_de": max_de,
                "min_fcf": min_fcf,
                "sector": sector,
                "min_rev_cagr_5yr": min_rev_cagr_5yr,
                "min_pat_cagr_5yr": min_pat_cagr_5yr,
                "max_pe": max_pe,
            },
            "companies": companies,
        }

    finally:
        connection.close()
