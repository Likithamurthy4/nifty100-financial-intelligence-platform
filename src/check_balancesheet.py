import sqlite3

conn = sqlite3.connect("db/nifty100.db")

cursor = conn.execute("PRAGMA table_info(balancesheet)")

print("=== Balance Sheet Columns ===")

for row in cursor.fetchall():
    print(row)

conn.close()
