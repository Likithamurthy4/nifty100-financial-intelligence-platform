import sqlite3

import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

tables = ["profitandloss", "balancesheet", "cashflow", "financial_ratios"]

for table in tables:
    print("\n" + "=" * 60)
    print(table.upper())
    print("=" * 60)

    df = pd.read_sql(f"SELECT * FROM {table} LIMIT 1", conn)

    for col in df.columns:
        print(col)

conn.close()
