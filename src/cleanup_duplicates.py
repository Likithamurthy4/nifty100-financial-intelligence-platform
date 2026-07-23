import sqlite3

conn = sqlite3.connect("db/nifty100.db")
cursor = conn.cursor()

print("Removing duplicate rows...")

# Remove duplicates from financial_ratios
cursor.execute("""
DELETE FROM financial_ratios
WHERE rowid NOT IN (
    SELECT MIN(rowid)
    FROM financial_ratios
    GROUP BY company_id, year
)
""")

# Remove duplicates from profitandloss
cursor.execute("""
DELETE FROM profitandloss
WHERE rowid NOT IN (
    SELECT MIN(rowid)
    FROM profitandloss
    GROUP BY company_id, year
)
""")

conn.commit()

print("Duplicates removed successfully.")

conn.close()
