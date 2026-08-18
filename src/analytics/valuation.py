import os
import sqlite3

import pandas as pd

DATABASE = "db/nifty100.db"


class Valuation:

    def __init__(self):
        self.conn = sqlite3.connect(DATABASE)

    def load_data(self):

        query = """
        SELECT

            fr.company_id,

            c.company_name,

            s.broad_sector,

            fr.free_cash_flow_cr,

            m.market_cap_crore,
            m.enterprise_value_crore,
            m.pe_ratio,
            m.pb_ratio,
            m.ev_ebitda,
            m.dividend_yield_pct,

            fr.year

        FROM financial_ratios fr

        JOIN companies c
            ON fr.company_id = c.id

        LEFT JOIN sectors s
            ON fr.company_id = s.company_id

        LEFT JOIN market_cap m
            ON fr.company_id = m.company_id
            AND fr.year = m.year

        WHERE fr.year = (

            SELECT MAX(f2.year)

            FROM financial_ratios f2

            WHERE f2.company_id = fr.company_id

        )
        """

        return pd.read_sql(query, self.conn)

    def calculate(self):

        df = self.load_data()

        df["fcf_yield_pct"] = (df["free_cash_flow_cr"] / df["market_cap_crore"]) * 100

        sector_pe = (
            df.groupby("broad_sector")["pe_ratio"]
            .median()
            .reset_index()
            .rename(columns={"pe_ratio": "sector_median_pe"})
        )

        df = df.merge(sector_pe, on="broad_sector")

        df["pe_vs_sector_median_pct"] = (df["pe_ratio"] / df["sector_median_pe"]) * 100

        def valuation_flag(row):

            if row["pe_ratio"] > row["sector_median_pe"] * 1.5:
                return "Caution"

            elif row["pe_ratio"] < row["sector_median_pe"] * 0.7:
                return "Discount"

            return "Fair"

        df["flag"] = df.apply(valuation_flag, axis=1)

        return df

    def export(self, df):

        os.makedirs("output", exist_ok=True)

        export = df[
            [
                "company_id",
                "company_name",
                "broad_sector",
                "pe_ratio",
                "pb_ratio",
                "ev_ebitda",
                "fcf_yield_pct",
                "sector_median_pe",
                "pe_vs_sector_median_pct",
                "flag",
            ]
        ]

        export.to_excel("output/valuation_summary.xlsx", index=False)

        export[export["flag"] != "Fair"].to_csv(
            "output/valuation_flags.csv", index=False
        )

        print("Valuation reports exported.")

    def close(self):
        self.conn.close()
