import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

print("=" * 70)
print("      NIFTY 100 FINANCIAL INTELLIGENCE PLATFORM")
print("=" * 70)

print("\nDATABASE TABLES\n")

tables = pd.read_sql(
    "SELECT name FROM sqlite_master WHERE type='table';",
    conn
)

print(tables)

print("\n" + "=" * 70)

print("\nFINANCIAL RATIOS SAMPLE\n")

ratios = pd.read_sql(
    """
    SELECT
        company_id,
        year,
        return_on_equity_pct,
        debt_to_equity,
        interest_coverage,
        revenue_cagr_5yr,
        composite_quality_score
    FROM financial_ratios
    LIMIT 10
    """,
    conn
)

print(ratios)

print("\n" + "=" * 70)

row_count = pd.read_sql(
    "SELECT COUNT(*) AS total FROM financial_ratios",
    conn
)

print("\nTOTAL ROWS\n")
print(row_count)

print("\n" + "=" * 70)
print("Sprint 2 Demo Completed Successfully")
print("=" * 70)

conn.close()