import sqlite3

import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

print("=== Companies Columns ===")
print(pd.read_sql("PRAGMA table_info(companies)", conn))

print("\n=== Sample Data ===")
print(pd.read_sql("SELECT * FROM companies LIMIT 5", conn))

conn.close()
