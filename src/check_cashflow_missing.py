import sqlite3

import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

companies = pd.read_sql("SELECT id AS company_id, company_name FROM companies", conn)

cashflow = pd.read_sql("SELECT DISTINCT company_id FROM cashflow", conn)

conn.close()

missing = companies[~companies["company_id"].isin(cashflow["company_id"])]

print("Companies in companies table:", len(companies))
print("Companies with cashflow data:", len(cashflow))
print("\nMissing cashflow companies:")
print(missing.to_string(index=False))
