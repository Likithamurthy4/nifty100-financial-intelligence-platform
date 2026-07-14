import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

query = """
SELECT
company_id,
year,
total_assets,
total_liabilities
FROM balancesheet
LIMIT 20
"""

df = pd.read_sql(query, conn)

df["difference"] = abs(
    df["total_assets"] -
    df["total_liabilities"]
)

print(df)

conn.close()