import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

tables = [
    "financial_ratios",
    "profitandloss",
    "market_cap"
]

for table in tables:
    print(f"\n===== {table} =====")

    query = f"""
    SELECT company_id, year, COUNT(*) AS cnt
    FROM {table}
    GROUP BY company_id, year
    HAVING COUNT(*) > 1
    """

    df = pd.read_sql(query, conn)

    if df.empty:
        print("No duplicates")
    else:
        print(df.head(10))

conn.close()