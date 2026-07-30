import sqlite3

conn = sqlite3.connect("db/nifty100.db")
cursor = conn.cursor()

try:
    cursor.execute("""
        ALTER TABLE financial_ratios
        ADD COLUMN revenue_cagr_3yr REAL
    """)
    conn.commit()
    print("✅ revenue_cagr_3yr column added.")
except sqlite3.OperationalError as e:
    print(e)

conn.close()