import sqlite3

conn = sqlite3.connect("db/nifty100.db")
cursor = conn.cursor()

tables = [
    "balancesheet",
    "cashflow"
]

for table in tables:

    print(f"Cleaning {table}...")

    cursor.execute(f"""
        DELETE FROM {table}
        WHERE rowid NOT IN (
            SELECT MIN(rowid)
            FROM {table}
            GROUP BY company_id, year
        )
    """)

conn.commit()
conn.close()

print("\nSource tables cleaned successfully.")