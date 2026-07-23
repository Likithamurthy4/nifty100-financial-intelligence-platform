import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

tables = [
    "profitandloss",
    "balancesheet",
    "cashflow",
    "market_cap"
]

for table in tables:
    print(f"\n===== {table} =====")

    df = pd.read_sql(f"""
        SELECT company_id,
               year,
               COUNT(*) AS cnt
        FROM {table}
        GROUP BY company_id, year
        HAVING COUNT(*) > 1
    """, conn)

    if df.empty:
        print("No duplicates")
    else:
        print(df.head(20))

conn.close()