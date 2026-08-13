import sqlite3
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[3]
DB_PATH = BASE_DIR / "db" / "nifty100.db"


def get_db_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


# ============================================================
# ALL SECTORS
# ============================================================

@router.get("/sectors")
def get_sectors():
    """
    Return all sectors with company count and
    latest-year median ROE, P/E and D/E.
    """

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
            ),

            sector_metrics AS (
                SELECT
                    s.broad_sector,
                    c.id AS company_id,
                    r.return_on_equity_pct AS roe_pct,
                    r.debt_to_equity AS debt_to_equity,
                    v.pe_ratio
                FROM sectors s
                JOIN companies c
                    ON c.id = s.company_id
                LEFT JOIN latest_ratios r
                    ON r.company_id = c.id
                LEFT JOIN latest_valuation v
                    ON v.company_id = c.id
            )

            SELECT
                broad_sector,
                COUNT(DISTINCT company_id) AS company_count,
                ROUND(
                    (
                        SELECT AVG(x.roe_pct)
                        FROM sector_metrics x
                        WHERE x.broad_sector = sm.broad_sector
                        AND x.roe_pct IS NOT NULL
                        AND (
                            SELECT COUNT(*)
                            FROM sector_metrics y
                            WHERE y.broad_sector = sm.broad_sector
                            AND y.roe_pct IS NOT NULL
                            AND y.roe_pct <= x.roe_pct
                        ) IN (
                            (
                                SELECT COUNT(*)
                                FROM sector_metrics z
                                WHERE z.broad_sector = sm.broad_sector
                                AND z.roe_pct IS NOT NULL
                            ) / 2,
                            (
                                SELECT COUNT(*)
                                FROM sector_metrics z
                                WHERE z.broad_sector = sm.broad_sector
                                AND z.roe_pct IS NOT NULL
                            ) / 2 + 1
                        )
                    ),
                    2
                ) AS median_roe,
                ROUND(
                    (
                        SELECT AVG(x.pe_ratio)
                        FROM sector_metrics x
                        WHERE x.broad_sector = sm.broad_sector
                        AND x.pe_ratio IS NOT NULL
                    ),
                    2
                ) AS average_pe,
                ROUND(
                    (
                        SELECT AVG(x.debt_to_equity)
                        FROM sector_metrics x
                        WHERE x.broad_sector = sm.broad_sector
                        AND x.debt_to_equity IS NOT NULL
                    ),
                    2
                ) AS average_de
            FROM sector_metrics sm
            GROUP BY broad_sector
            ORDER BY broad_sector
        """

        rows = connection.execute(query).fetchall()

        # SQLite does not have a native MEDIAN aggregate.
        # Calculate exact medians in Python from the latest data.
        sectors = []

        for row in rows:
            sector = row["broad_sector"]

            roe_values = [
                r[0]
                for r in connection.execute(
                    """
                    SELECT r.return_on_equity_pct
                    FROM sectors s
                    JOIN financial_ratios r
                        ON r.company_id = s.company_id
                    WHERE s.broad_sector = ?
                      AND r.year = (
                          SELECT MAX(r2.year)
                          FROM financial_ratios r2
                          WHERE r2.company_id = r.company_id
                      )
                      AND r.return_on_equity_pct IS NOT NULL
                    """,
                    (sector,),
                ).fetchall()
            ]

            pe_values = [
                r[0]
                for r in connection.execute(
                    """
                    SELECT mc.pe_ratio
                    FROM sectors s
                    JOIN market_cap mc
                        ON mc.company_id = s.company_id
                    WHERE s.broad_sector = ?
                      AND mc.year = (
                          SELECT MAX(mc2.year)
                          FROM market_cap mc2
                          WHERE mc2.company_id = mc.company_id
                      )
                      AND mc.pe_ratio IS NOT NULL
                    """,
                    (sector,),
                ).fetchall()
            ]

            de_values = [
                r[0]
                for r in connection.execute(
                    """
                    SELECT r.debt_to_equity
                    FROM sectors s
                    JOIN financial_ratios r
                        ON r.company_id = s.company_id
                    WHERE s.broad_sector = ?
                      AND r.year = (
                          SELECT MAX(r2.year)
                          FROM financial_ratios r2
                          WHERE r2.company_id = r.company_id
                      )
                      AND r.debt_to_equity IS NOT NULL
                    """,
                    (sector,),
                ).fetchall()
            ]

            def median(values):
                if not values:
                    return None

                values = sorted(values)
                n = len(values)
                middle = n // 2

                if n % 2:
                    return values[middle]

                return (values[middle - 1] + values[middle]) / 2

            sectors.append(
                {
                    "sector": sector,
                    "company_count": row["company_count"],
                    "median_roe": (
                        round(median(roe_values), 2)
                        if roe_values
                        else None
                    ),
                    "median_pe": (
                        round(median(pe_values), 2)
                        if pe_values
                        else None
                    ),
                    "median_de": (
                        round(median(de_values), 2)
                        if de_values
                        else None
                    ),
                }
            )

        return {
            "count": len(sectors),
            "sectors": sectors,
        }

    finally:
        connection.close()


# ============================================================
# COMPANIES IN A SECTOR
# ============================================================

@router.get("/sectors/{sector}/companies")
def get_sector_companies(sector: str):
    """
    Return companies belonging to a sector with
    latest-year financial KPIs.
    """

    connection = get_db_connection()

    try:
        sector_exists = connection.execute(
            """
            SELECT 1
            FROM sectors
            WHERE LOWER(broad_sector) = LOWER(?)
            LIMIT 1
            """,
            (sector,),
        ).fetchone()

        if sector_exists is None:
            raise HTTPException(
                status_code=404,
                detail=f"Unknown sector: {sector}",
            )

        rows = connection.execute(
            """
            WITH latest_ratios AS (
                SELECT *
                FROM financial_ratios fr
                WHERE fr.year = (
                    SELECT MAX(fr2.year)
                    FROM financial_ratios fr2
                    WHERE fr2.company_id = fr.company_id
                )
            )

            SELECT
                c.id,
                c.company_name,

                s.broad_sector,
                s.sub_sector,
                s.market_cap_category,
                s.index_weight_pct,

                r.year,
                r.net_profit_margin_pct,
                r.operating_profit_margin_pct,
                r.return_on_equity_pct AS roe_pct,
                r.debt_to_equity,
                r.interest_coverage,
                r.asset_turnover,
                r.free_cash_flow_cr,
                r.revenue_cagr_5yr,
                r.pat_cagr_5yr,
                r.eps_cagr_5yr,
                r.composite_quality_score

            FROM companies c

            JOIN sectors s
                ON s.company_id = c.id

            LEFT JOIN latest_ratios r
                ON r.company_id = c.id

            WHERE LOWER(s.broad_sector) = LOWER(?)

            ORDER BY
                r.return_on_equity_pct DESC,
                c.company_name
            """,
            (sector,),
        ).fetchall()

        companies = [dict(row) for row in rows]

        return {
            "sector": sector,
            "count": len(companies),
            "companies": companies,
        }

    finally:
        connection.close()
