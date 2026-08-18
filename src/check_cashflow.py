import sqlite3

conn = sqlite3.connect("db/nifty100.db")

cursor = conn.execute("PRAGMA table_info(cashflow)")

print("=== Cash Flow Columns ===")

for row in cursor.fetchall():
    print(row)

conn.close()
