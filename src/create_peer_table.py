import sqlite3

conn = sqlite3.connect("db/nifty100.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS peer_percentiles (

    company_id INTEGER,
    peer_group_name TEXT,
    metric TEXT,
    value REAL,
    percentile_rank REAL,
    year INTEGER

)
""")

conn.commit()

print("peer_percentiles table created successfully.")

conn.close()
