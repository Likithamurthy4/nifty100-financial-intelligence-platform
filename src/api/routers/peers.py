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


@router.get("/peers/{group_name}")
def get_peer_group(group_name: str):
    conn = get_db_connection()

    try:
        group = conn.execute(
            """
            SELECT DISTINCT peer_group_name
            FROM peer_groups
            WHERE LOWER(peer_group_name) = LOWER(?)
            """,
            (group_name,),
        ).fetchone()

        if group is None:
            raise HTTPException(
                status_code=404,
                detail=f"Unknown peer group: {group_name}",
            )

        actual_name = group["peer_group_name"]

        companies = conn.execute(
            """
            SELECT
                pg.company_id,
                c.company_name,
                pg.is_benchmark
            FROM peer_groups pg
            JOIN companies c
                ON c.id = pg.company_id
            WHERE pg.peer_group_name = ?
            ORDER BY pg.is_benchmark DESC, c.company_name
            """,
            (actual_name,),
        ).fetchall()

        result = []

        for company in companies:
            rows = conn.execute(
                """
                SELECT
                    metric,
                    value,
                    percentile_rank,
                    year
                FROM peer_percentiles
                WHERE company_id = ?
                  AND peer_group_name = ?
                ORDER BY year DESC
                """,
                (
                    company["company_id"],
                    actual_name,
                ),
            ).fetchall()

            metrics = {}

            for row in rows:
                metric = row["metric"]

                if metric not in metrics:
                    metrics[metric] = {
                        "value": row["value"],
                        "percentile_rank": row["percentile_rank"],
                        "year": row["year"],
                    }

            result.append(
                {
                    "company_id": company["company_id"],
                    "company_name": company["company_name"],
                    "is_benchmark": bool(company["is_benchmark"]),
                    "metrics": metrics,
                }
            )

        return {
            "peer_group": actual_name,
            "count": len(result),
            "companies": result,
        }

    finally:
        conn.close()


@router.get("/companies/{ticker}/peers/compare")
def compare_company_peers(ticker: str):
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

        peer = conn.execute(
            """
            SELECT peer_group_name
            FROM peer_groups
            WHERE company_id = ?
            LIMIT 1
            """,
            (company["id"],),
        ).fetchone()

        if peer is None:
            raise HTTPException(
                status_code=404,
                detail=f"No peer group found for {ticker}",
            )

        group_name = peer["peer_group_name"]

        metrics = [
            "return_on_equity_pct",
            "debt_to_equity",
            "interest_coverage",
            "asset_turnover",
            "revenue_cagr_5yr",
            "pat_cagr_5yr",
            "eps_cagr_5yr",
            "free_cash_flow_cr",
        ]

        company_rows = conn.execute(
            """
            SELECT metric, value, year
            FROM peer_percentiles
            WHERE company_id = ?
              AND peer_group_name = ?
            ORDER BY year DESC
            """,
            (
                company["id"],
                group_name,
            ),
        ).fetchall()

        company_values = {}

        for row in company_rows:
            if row["metric"] in metrics and row["metric"] not in company_values:
                company_values[row["metric"]] = row["value"]

        peer_rows = conn.execute(
            """
            SELECT
                company_id,
                metric,
                value,
                year
            FROM peer_percentiles
            WHERE peer_group_name = ?
            ORDER BY company_id, metric, year DESC
            """,
            (group_name,),
        ).fetchall()

        latest = {}

        for row in peer_rows:
            key = (
                row["company_id"],
                row["metric"],
            )

            if row["metric"] in metrics and key not in latest:
                latest[key] = row["value"]

        peer_average = {}

        for metric in metrics:
            values = [
                value
                for (company_id, metric_name), value in latest.items()
                if metric_name == metric and value is not None
            ]

            peer_average[metric] = (
                round(sum(values) / len(values), 4) if values else None
            )

        benchmark = conn.execute(
            """
            SELECT
                pg.company_id,
                c.company_name
            FROM peer_groups pg
            JOIN companies c
                ON c.id = pg.company_id
            WHERE pg.peer_group_name = ?
              AND pg.is_benchmark = 1
            LIMIT 1
            """,
            (group_name,),
        ).fetchone()

        benchmark_values = {}

        if benchmark:
            benchmark_rows = conn.execute(
                """
                SELECT metric, value, year
                FROM peer_percentiles
                WHERE company_id = ?
                  AND peer_group_name = ?
                ORDER BY year DESC
                """,
                (
                    benchmark["company_id"],
                    group_name,
                ),
            ).fetchall()

            for row in benchmark_rows:
                if row["metric"] in metrics and row["metric"] not in benchmark_values:
                    benchmark_values[row["metric"]] = row["value"]

        axes = []

        for metric in metrics:
            axes.append(
                {
                    "metric": metric,
                    "company": company_values.get(metric),
                    "peer_group_average": peer_average.get(metric),
                    "benchmark": benchmark_values.get(metric),
                }
            )

        return {
            "company_id": company["id"],
            "company_name": company["company_name"],
            "peer_group": group_name,
            "benchmark_company": (
                {
                    "company_id": benchmark["company_id"],
                    "company_name": benchmark["company_name"],
                }
                if benchmark
                else None
            ),
            "axes": axes,
        }

    finally:
        conn.close()
