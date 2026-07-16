import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

print("=" * 60)
print("SPRINT 2 FINAL VALIDATION")
print("=" * 60)

queries = {

    "Total Financial Ratio Rows":
        "SELECT COUNT(*) FROM financial_ratios",

    "ROE Available":
        """
        SELECT COUNT(*)
        FROM financial_ratios
        WHERE return_on_equity_pct IS NOT NULL
        """,

    "Debt-to-Equity Available":
        """
        SELECT COUNT(*)
        FROM financial_ratios
        WHERE debt_to_equity IS NOT NULL
        """,

    "Revenue CAGR Available":
        """
        SELECT COUNT(*)
        FROM financial_ratios
        WHERE revenue_cagr_5yr IS NOT NULL
        """,

    "Composite Score Available":
        """
        SELECT COUNT(*)
        FROM financial_ratios
        WHERE composite_quality_score IS NOT NULL
        """
}

for title, query in queries.items():

    value = pd.read_sql(query, conn).iloc[0, 0]

    print(f"{title:<35}: {value}")

conn.close()