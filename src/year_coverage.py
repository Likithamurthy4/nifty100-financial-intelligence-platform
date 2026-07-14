import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

query = """
SELECT
company_id,
COUNT(year) AS total_years
FROM profitandloss
GROUP BY company_id
HAVING COUNT(year)<5
ORDER BY total_years;
"""

df = pd.read_sql(query, conn)

print(df)

conn.close()