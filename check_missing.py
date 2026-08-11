import sqlite3

conn = sqlite3.connect("db/nifty100.db")

tables = [
    "profitandloss",
    "balancesheet",
    "cashflow",
]

for table in tables:
    print("\n" + "=" * 70)
    print(table.upper())
    print("=" * 70)

    columns = conn.execute(
        f"PRAGMA table_info({table})"
    ).fetchall()

    print("COLUMNS:")
    print([row[1] for row in columns])

    print("\nATGL:")
    print(
        conn.execute(
            f"SELECT * FROM {table} WHERE company_id='ATGL' ORDER BY year"
        ).fetchall()
    )

    print("\nSBIN:")
    print(
        conn.execute(
            f"SELECT * FROM {table} WHERE company_id='SBIN' ORDER BY year"
        ).fetchall()
    )

conn.close()