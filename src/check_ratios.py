import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

query = """
SELECT
    company_id,
    year,
    return_on_equity_pct,
    debt_to_equity,
    interest_coverage,
    revenue_cagr_5yr,
    composite_quality_score
FROM financial_ratios
LIMIT 20;
"""

df = pd.read_sql(query, conn)

print("\n===== FINANCIAL RATIOS PREVIEW =====\n")
print(df)

conn.close()