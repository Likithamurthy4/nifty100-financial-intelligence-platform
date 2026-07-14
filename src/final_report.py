import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

tables = [
    "companies",
    "profitandloss",
    "balancesheet",
    "cashflow",
    "analysis",
    "documents",
    "prosandcons",
    "sectors",
    "stock_prices",
    "financial_ratios",
    "peer_groups"
]

print("="*60)
print("SPRINT 1 FINAL REPORT")
print("="*60)

for table in tables:

    rows = pd.read_sql(
        f"SELECT COUNT(*) AS total FROM {table}",
        conn
    )

    print(f"{table:<20} {rows.iloc[0,0]} rows")

print("\nChecking Foreign Keys...")

cursor = conn.cursor()

cursor.execute("PRAGMA foreign_key_check")

fk = cursor.fetchall()

if len(fk)==0:

    print("✅ Foreign Keys OK")

else:

    print(fk)

print("\nDatabase Ready")

conn.close()