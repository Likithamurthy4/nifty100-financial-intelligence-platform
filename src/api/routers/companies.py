import sqlite3
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

router = APIRouter()


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

DB_PATH = BASE_DIR / "db" / "nifty100.db"

TEARSHEET_DIR = BASE_DIR / "reports" / "tearsheets"


# ============================================================
# DATABASE CONNECTION
# ============================================================


def get_db_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


# ============================================================
# HELPERS
# ============================================================


def rows_to_dict(rows):
    """Convert SQLite rows to normal dictionaries."""
    return [dict(row) for row in rows]


def parse_year(value: str | None):
    """
    Convert YYYY-MM query parameter to an integer year.

    Example:
        2024-03 -> 2024
    """

    if value is None:
        return None

    try:
        if len(value) != 7 or value[4] != "-":
            raise ValueError

        year = int(value[:4])
        month = int(value[5:7])

        if month < 1 or month > 12:
            raise ValueError

        return year

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Year must be in YYYY-MM format.",
        )


def validate_year_range(
    from_year: str | None,
    to_year: str | None,
):
    start = parse_year(from_year)
    end = parse_year(to_year)

    if start is not None and end is not None and start > end:
        raise HTTPException(
            status_code=400,
            detail="from_year cannot be greater than to_year.",
        )

    return start, end


def get_company(ticker: str):
    """
    Return company information or None.
    """

    connection = get_db_connection()

    try:
        row = connection.execute(
            """
            SELECT *
            FROM companies
            WHERE UPPER(id) = UPPER(?)
            """,
            (ticker,),
        ).fetchone()

        return dict(row) if row else None

    finally:
        connection.close()


# ============================================================
# GET ALL COMPANIES
# ============================================================


@router.get("/companies")
def get_companies(
    sector: str | None = Query(
        None,
        description="Filter by broad sector",
    ),
    market_cap_category: str | None = Query(
        None,
        description="Filter by market cap category",
    ),
    search: str | None = Query(
        None,
        description="Partial company name or ticker search",
    ),
):
    """
    Return all companies with sector information.

    Optional filters:
    - sector
    - market_cap_category
    - search
    """

    connection = get_db_connection()

    try:
        query = """
            SELECT
                c.id,
                c.company_name,
                s.broad_sector,
                s.sub_sector,
                c.roe_percentage AS roe_pct,
                c.roce_percentage AS roce_pct
            FROM companies c
            LEFT JOIN sectors s
                ON c.id = s.company_id
            WHERE 1 = 1
        """

        parameters = []

        if sector:
            query += """
                AND LOWER(s.broad_sector) = LOWER(?)
            """
            parameters.append(sector)

        if market_cap_category:
            query += """
                AND LOWER(s.market_cap_category) = LOWER(?)
            """
            parameters.append(market_cap_category)

        if search:
            query += """
                AND (
                    LOWER(c.id) LIKE LOWER(?)
                    OR LOWER(c.company_name) LIKE LOWER(?)
                )
            """

            search_value = f"%{search}%"

            parameters.extend([search_value, search_value])

        query += """
            ORDER BY c.id
        """

        rows = connection.execute(
            query,
            parameters,
        ).fetchall()

        return {
            "count": len(rows),
            "companies": rows_to_dict(rows),
        }

    finally:
        connection.close()


# ============================================================
# GET COMPANY PROFILE
# ============================================================


@router.get("/companies/{ticker}")
def get_company_profile(ticker: str):
    """
    Return full company profile including:
    - all company fields
    - sector information
    - latest-year KPIs
    """

    connection = get_db_connection()

    try:
        company = connection.execute(
            """
            SELECT *
            FROM companies
            WHERE UPPER(id) = UPPER(?)
            """,
            (ticker,),
        ).fetchone()

        if company is None:
            raise HTTPException(
                status_code=404,
                detail=f"Company '{ticker}' not found.",
            )

        company_data = dict(company)

        sector = connection.execute(
            """
            SELECT
                broad_sector,
                sub_sector,
                index_weight_pct,
                market_cap_category
            FROM sectors
            WHERE UPPER(company_id) = UPPER(?)
            """,
            (ticker,),
        ).fetchone()

        sector_data = dict(sector) if sector else None

        latest_kpis = connection.execute(
            """
            SELECT *
            FROM financial_ratios
            WHERE UPPER(company_id) = UPPER(?)
              AND year IS NOT NULL
            ORDER BY year DESC
            LIMIT 1
            """,
            (ticker,),
        ).fetchone()

        latest_kpi_data = dict(latest_kpis) if latest_kpis else None

        return {
            "company": company_data,
            "sector": sector_data,
            "latest_year_kpis": latest_kpi_data,
        }

    finally:
        connection.close()


# ============================================================
# GET PROFIT & LOSS HISTORY
# ============================================================


@router.get("/companies/{ticker}/pl")
def get_company_pl(
    ticker: str,
    from_year: str | None = Query(
        None,
        description="Start year in YYYY-MM format",
    ),
    to_year: str | None = Query(
        None,
        description="End year in YYYY-MM format",
    ),
):
    """
    Return Profit & Loss history for a company.
    """

    start, end = validate_year_range(
        from_year,
        to_year,
    )

    connection = get_db_connection()

    try:
        company = get_company(ticker)

        if company is None:
            raise HTTPException(
                status_code=404,
                detail=f"Company '{ticker}' not found.",
            )

        query = """
            SELECT *
            FROM profitandloss
            WHERE UPPER(company_id) = UPPER(?)
              AND year IS NOT NULL
        """

        parameters = [ticker]

        if start is not None:
            query += " AND year >= ?"
            parameters.append(start)

        if end is not None:
            query += " AND year <= ?"
            parameters.append(end)

        query += " ORDER BY year"

        rows = connection.execute(
            query,
            parameters,
        ).fetchall()

        return {
            "ticker": ticker.upper(),
            "history": rows_to_dict(rows),
        }

    finally:
        connection.close()


# ============================================================
# GET BALANCE SHEET HISTORY
# ============================================================


@router.get("/companies/{ticker}/bs")
def get_company_bs(
    ticker: str,
    from_year: str | None = Query(
        None,
        description="Start year in YYYY-MM format",
    ),
    to_year: str | None = Query(
        None,
        description="End year in YYYY-MM format",
    ),
):
    """
    Return Balance Sheet history for a company.
    """

    start, end = validate_year_range(
        from_year,
        to_year,
    )

    connection = get_db_connection()

    try:
        company = get_company(ticker)

        if company is None:
            raise HTTPException(
                status_code=404,
                detail=f"Company '{ticker}' not found.",
            )

        query = """
            SELECT *
            FROM balancesheet
            WHERE UPPER(company_id) = UPPER(?)
              AND year IS NOT NULL
        """

        parameters = [ticker]

        if start is not None:
            query += " AND year >= ?"
            parameters.append(start)

        if end is not None:
            query += " AND year <= ?"
            parameters.append(end)

        query += " ORDER BY year"

        rows = connection.execute(
            query,
            parameters,
        ).fetchall()

        return {
            "ticker": ticker.upper(),
            "history": rows_to_dict(rows),
        }

    finally:
        connection.close()


# ============================================================
# GET CASH FLOW HISTORY
# ============================================================


@router.get("/companies/{ticker}/cashflow")
def get_company_cashflow(
    ticker: str,
    from_year: str | None = Query(
        None,
        description="Start year in YYYY-MM format",
    ),
    to_year: str | None = Query(
        None,
        description="End year in YYYY-MM format",
    ),
):
    """
    Return Cash Flow history for a company.
    """

    start, end = validate_year_range(
        from_year,
        to_year,
    )

    connection = get_db_connection()

    try:
        company = get_company(ticker)

        if company is None:
            raise HTTPException(
                status_code=404,
                detail=f"Company '{ticker}' not found.",
            )

        query = """
            SELECT *
            FROM cashflow
            WHERE UPPER(company_id) = UPPER(?)
              AND year IS NOT NULL
        """

        parameters = [ticker]

        if start is not None:
            query += " AND year >= ?"
            parameters.append(start)

        if end is not None:
            query += " AND year <= ?"
            parameters.append(end)

        query += " ORDER BY year"

        rows = connection.execute(
            query,
            parameters,
        ).fetchall()

        return {
            "ticker": ticker.upper(),
            "history": rows_to_dict(rows),
        }

    finally:
        connection.close()


# ============================================================
# GET FINANCIAL RATIOS
# ============================================================


@router.get("/companies/{ticker}/ratios")
def get_company_ratios(
    ticker: str,
    year: int | None = Query(
        None,
        description="Optional financial year",
    ),
):
    """
    Return computed financial KPIs per year.

    Optional:
        year=2024
    """

    connection = get_db_connection()

    try:
        company = get_company(ticker)

        if company is None:
            raise HTTPException(
                status_code=404,
                detail=f"Company '{ticker}' not found.",
            )

        query = """
            SELECT *
            FROM financial_ratios
            WHERE UPPER(company_id) = UPPER(?)
        """

        parameters = [ticker]

        if year is not None:
            query += " AND year = ?"
            parameters.append(year)

        query += " ORDER BY year"

        rows = connection.execute(
            query,
            parameters,
        ).fetchall()

        return {
            "ticker": ticker.upper(),
            "year": year,
            "ratios": rows_to_dict(rows),
        }

    finally:
        connection.close()


# ============================================================
# GET COMPANY TEARSHEET
# ============================================================


@router.get("/companies/{ticker}/tearsheet")
def get_company_tearsheet(ticker: str):
    """
    Return pre-generated company tearsheet PDF.
    """

    company = get_company(ticker)

    if company is None:
        raise HTTPException(
            status_code=404,
            detail=f"Company '{ticker}' not found.",
        )

    normalized_ticker = ticker.upper()

    pdf_path = TEARSHEET_DIR / f"{normalized_ticker}_tearsheet.pdf"

    if not pdf_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Tearsheet for '{normalized_ticker}' not found.",
        )

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=pdf_path.name,
    )
