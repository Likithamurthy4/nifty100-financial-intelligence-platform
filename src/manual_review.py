import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

print("=" * 60)
print("MANUAL DATA REVIEW")
print("=" * 60)

# Random 5 companies
query = """
SELECT id, company_name
FROM companies
ORDER BY RANDOM()
LIMIT 5
"""

companies = pd.read_sql(query, conn)

print("\nRandom Companies:\n")
print(companies)

print("\n" + "=" * 60)

for _, row in companies.iterrows():

    company = row["id"]

    print(f"\nCompany : {company}")

    q = f"""
    SELECT year
    FROM profitandloss
    WHERE company_id='{company}'
    ORDER BY year
    """

    years = pd.read_sql(q, conn)

    print(years)

conn.close()