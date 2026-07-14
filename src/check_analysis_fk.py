import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

companies = pd.read_sql("SELECT id FROM companies", conn)

analysis = pd.read_excel(
    "data/raw/analysis.xlsx",
    header=1
)

analysis.columns = (
    analysis.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

invalid = analysis[
    ~analysis["company_id"].isin(companies["id"])
]

print("\nInvalid company_ids:")
print(invalid[["company_id"]])

conn.close()