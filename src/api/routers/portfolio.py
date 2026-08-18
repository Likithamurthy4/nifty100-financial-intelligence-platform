import sqlite3
from pathlib import Path

from fastapi import APIRouter

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[3]
DB_PATH = BASE_DIR / "db" / "nifty100.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/portfolio/stats")
def get_portfolio_stats():
    """
    Return P10 through P90 percentile statistics
    for the 10 core financial KPIs.
    """

    conn = get_db_connection()

    try:
        # Latest year for each company
        rows = conn.execute("""
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
                net_profit_margin_pct,
                operating_profit_margin_pct,
                return_on_equity_pct,
                debt_to_equity,
                interest_coverage,
                asset_turnover,
                free_cash_flow_cr,
                revenue_cagr_5yr,
                pat_cagr_5yr,
                eps_cagr_5yr
            FROM latest_ratios
            """).fetchall()

        metrics = [
            "net_profit_margin_pct",
            "operating_profit_margin_pct",
            "return_on_equity_pct",
            "debt_to_equity",
            "interest_coverage",
            "asset_turnover",
            "free_cash_flow_cr",
            "revenue_cagr_5yr",
            "pat_cagr_5yr",
            "eps_cagr_5yr",
        ]

        # Convert SQLite rows into metric arrays
        values = {metric: [] for metric in metrics}

        for row in rows:
            for metric in metrics:
                value = row[metric]

                if value is not None:
                    values[metric].append(float(value))

        def percentile(data, p):
            if not data:
                return None

            data = sorted(data)

            if len(data) == 1:
                return data[0]

            position = (len(data) - 1) * p

            lower = int(position)
            upper = lower + 1

            if upper >= len(data):
                return data[lower]

            fraction = position - lower

            return data[lower] + fraction * (data[upper] - data[lower])

        statistics = []

        for metric in metrics:

            data = values[metric]

            statistics.append(
                {
                    "metric": metric,
                    "P10": round(percentile(data, 0.10), 4) if data else None,
                    "P25": round(percentile(data, 0.25), 4) if data else None,
                    "P50": round(percentile(data, 0.50), 4) if data else None,
                    "P75": round(percentile(data, 0.75), 4) if data else None,
                    "P90": round(percentile(data, 0.90), 4) if data else None,
                }
            )

        return {
            "company_count": len(rows),
            "metric_count": len(statistics),
            "statistics": statistics,
        }

    finally:
        conn.close()
