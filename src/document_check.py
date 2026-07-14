import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

query = """
SELECT
company_id,
COUNT(*) AS reports
FROM documents
GROUP BY company_id
ORDER BY reports;
"""

df = pd.read_sql(query, conn)

print(df.head(20))

conn.close()