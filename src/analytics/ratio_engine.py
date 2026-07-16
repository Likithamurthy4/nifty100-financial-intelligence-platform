"""
Sprint 2
Ratio Engine

Reads SQLite
Calculates Financial KPIs
Writes financial_ratios table
"""

import sqlite3
import pandas as pd

from analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
    debt_to_equity,
    interest_coverage,
    asset_turnover
)

from analytics.cagr import (
    revenue_cagr,
    pat_cagr,
    eps_cagr
)

from analytics.cashflow_kpis import (
    free_cash_flow
)


DATABASE = "db/nifty100.db"


class RatioEngine:

    def __init__(self):

        self.conn = sqlite3.connect(DATABASE)

        self.output = None

        self.data = None


    ##################################################

    def load_tables(self):

        print("Loading SQLite tables...")

        self.pnl = pd.read_sql(
            "SELECT * FROM profitandloss",
            self.conn
        )

        self.bs = pd.read_sql(
            "SELECT * FROM balancesheet",
            self.conn
        )

        self.cf = pd.read_sql(
            "SELECT * FROM cashflow",
            self.conn
        )

        self.market = pd.read_sql(
            "SELECT * FROM market_cap",
            self.conn
        )

        self.companies = pd.read_sql(
            "SELECT * FROM companies",
            self.conn
        )

        self.sectors = pd.read_sql(
            "SELECT * FROM sectors",
            self.conn
        )

        print("Tables Loaded Successfully")


    ##################################################

    def merge_tables(self):

        print("Merging datasets...")

        df = self.pnl.merge(

            self.bs,

            on=["company_id", "year"],

            suffixes=("_pnl", "_bs")

        )

        df = df.merge(

            self.cf,

            on=["company_id", "year"]

        )

        df = df.merge(

            self.sectors,

            on="company_id",

            how="left"

        )

        df = df.merge(

            self.market,

            on=["company_id", "year"],

            how="left"

        )

        df = df.merge(

            self.companies,

            left_on="company_id",

            right_on="id",

            how="left",

            suffixes=("", "_company")

        )

        self.data = df

        print(f"Merged Rows : {len(df)}")
        ##################################################

    def calculate_ratios(self):

        print("Calculating KPIs...")

        records = []

        for _, row in self.data.iterrows():

            # ---------- Profitability ----------

            npm = net_profit_margin(
                row["net_profit"],
                row["sales"]
            )

            opm = operating_profit_margin(
                row["operating_profit"],
                row["sales"]
            )

            roe = return_on_equity(
                row["net_profit"],
                row["equity_capital"],
                row["reserves"]
            )

            roce = return_on_capital_employed(
                row["operating_profit"],
                row["equity_capital"],
                row["reserves"],
                row["borrowings"],
                row["broad_sector"]
            )

            roa = return_on_assets(
                row["net_profit"],
                row["total_assets"]
            )

            # ---------- Leverage ----------

            de = debt_to_equity(
                row["borrowings"],
                row["equity_capital"],
                row["reserves"]
            )

            icr = interest_coverage(
                row["operating_profit"],
                row["other_income"],
                row["interest"]
            )

            turnover = asset_turnover(
                row["sales"],
                row["total_assets"]
            )

            # ---------- Cash Flow ----------

            fcf = free_cash_flow(
                row["operating_activity"],
                row["investing_activity"]
            )

            # ---------- CAGR ----------

            revenue5, _ = revenue_cagr(
                row["sales"],
                row["sales"],
                5
            )

            pat5, _ = pat_cagr(
                row["net_profit"],
                row["net_profit"],
                5
            )

            eps5, _ = eps_cagr(
                row["eps"],
                row["eps"],
                5
            )

            # ---------- Composite Quality ----------

            score = 0

            if roe is not None and roe > 15:
                score += 25

            if de is not None and de < 1:
                score += 25

            if icr is not None and icr > 2:
                score += 25

            if roa is not None and roa > 5:
                score += 25

            records.append({

                "company_id": row["company_id"],

                "year": row["year"],

                "net_profit_margin_pct": npm,

                "operating_profit_margin_pct": opm,

                "return_on_equity_pct": roe,

                "debt_to_equity": de,

                "interest_coverage": icr,

                "asset_turnover": turnover,

                "free_cash_flow_cr": fcf,

                "capex_cr": abs(row["investing_activity"]),

                "earnings_per_share": row["eps"],

                "book_value_per_share": row["book_value"],

                "dividend_payout_ratio_pct": row["dividend_payout"],

                "total_debt_cr": row["borrowings"],

                "cash_from_operations_cr": row["operating_activity"],

                "revenue_cagr_5yr": revenue5,

                "pat_cagr_5yr": pat5,

                "eps_cagr_5yr": eps5,

                "composite_quality_score": score

            })

        self.output = pd.DataFrame(records)

        print()

        print(f"Calculated {len(self.output)} KPI rows")

        ##################################################

    def save_to_database(self):

        print("\nSaving ratios to SQLite...")

        cursor = self.conn.cursor()

        # Remove old calculated rows
        cursor.execute("DELETE FROM financial_ratios")

        self.conn.commit()

        # Write new ratios
        self.output.to_sql(
            "financial_ratios",
            self.conn,
            if_exists="append",
            index=False
        )

        self.conn.commit()

        print("financial_ratios updated successfully.")

    ##################################################

    def verify_database(self):

        print("\nVerifying database...")

        cursor = self.conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM financial_ratios"
        )

        total = cursor.fetchone()[0]

        print(f"Rows in financial_ratios : {total}")

        if total >= 1100:
            print("PASS : Expected row count achieved")
        else:
            print("WARNING : Row count below expected")

        cursor.execute("""
            SELECT COUNT(*)
            FROM financial_ratios
            WHERE return_on_equity_pct IS NOT NULL
        """)

        roe_rows = cursor.fetchone()[0]

        print(f"ROE populated rows : {roe_rows}")

        cursor.execute("""
            SELECT COUNT(*)
            FROM financial_ratios
            WHERE debt_to_equity IS NOT NULL
        """)

        de_rows = cursor.fetchone()[0]

        print(f"Debt-to-Equity populated rows : {de_rows}")

    ##################################################

    def run(self):

        self.load_tables()

        self.merge_tables()

        self.calculate_ratios()

        self.save_to_database()

        self.verify_database()

        self.conn.close()

        print("\n====================================")
        print(" Ratio Engine Completed Successfully")
        print("====================================")