import sqlite3

import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

query = """
SELECT
    company_id,
    peer_group_name,
    metric,
    value,
    percentile_rank,
    year
FROM peer_percentiles
WHERE peer_group_name='FMCG'
AND metric='return_on_equity_pct'
ORDER BY percentile_rank DESC
"""

df = pd.read_sql(query, conn)

print(df)

conn.close()
