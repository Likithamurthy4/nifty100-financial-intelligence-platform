import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

query = """
SELECT
    company_id,
    year,
    return_on_equity_pct,
    debt_to_equity
FROM financial_ratios
WHERE
    return_on_equity_pct > 15
AND
    debt_to_equity < 1
LIMIT 25
"""

df = pd.read_sql(query, conn)

print("=" * 60)
print("QUALITY STOCK SCREENER")
print("=" * 60)

print(df)

conn.close()