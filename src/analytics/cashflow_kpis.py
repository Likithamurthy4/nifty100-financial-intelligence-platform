import os
import sqlite3
import pandas as pd
import numpy as np


DATABASE = "db/nifty100.db"


class CashFlowIntelligence:

    def __init__(self):

        self.conn = sqlite3.connect(DATABASE)

    # ==========================================================
    # Load data
    # ==========================================================

    def load_data(self):

        cashflow = pd.read_sql(
            """
            SELECT
                company_id,
                year,
                operating_activity,
                investing_activity,
                financing_activity,
                net_cash_flow
            FROM cashflow
            ORDER BY company_id, year
            """,
            self.conn
        )

        pl = pd.read_sql(
            """
            SELECT
                company_id,
                year,
                sales,
                net_profit
            FROM profitandloss
            ORDER BY company_id, year
            """,
            self.conn
        )

        companies = pd.read_sql(
            """
            SELECT
                id AS company_id,
                company_name
            FROM companies
            """,
            self.conn
        )

        sectors = pd.read_sql(
            """
            SELECT *
            FROM sectors
            """,
            self.conn
        )

        return cashflow, pl, companies, sectors

    # ==========================================================
    # CFO Quality
    # ==========================================================

    def cfo_quality(self, company_cashflow, company_pl):

        merged = company_cashflow.merge(
            company_pl[
                [
                    "company_id",
                    "year",
                    "net_profit"
                ]
            ],
            on=["company_id", "year"],
            how="left"
        )

        merged["cfo_pat_ratio"] = np.where(
            merged["net_profit"].abs() > 0,
            merged["operating_activity"] /
            merged["net_profit"].abs(),
            np.nan
        )

        latest_5 = merged.tail(5)

        score = latest_5["cfo_pat_ratio"].mean()

        if pd.isna(score):
            label = "Insufficient Data"

        elif score > 1.0:
            label = "High Quality"

        elif score >= 0.5:
            label = "Moderate"

        else:
            label = "Accrual Risk"

        return score, label, merged

    # ==========================================================
    # CapEx Intensity
    # ==========================================================

    def capex_intensity(
        self,
        company_cashflow,
        company_pl
    ):

        merged = company_cashflow.merge(
            company_pl[
                [
                    "company_id",
                    "year",
                    "sales"
                ]
            ],
            on=["company_id", "year"],
            how="left"
        )

        latest = merged.iloc[-1]

        sales = latest["sales"]
        investing = latest["investing_activity"]

        if (
            pd.isna(sales)
            or sales == 0
        ):
            intensity = np.nan

        else:
            intensity = (
                abs(investing) /
                abs(sales)
            ) * 100

        if pd.isna(intensity):
            label = "Insufficient Data"

        elif intensity < 3:
            label = "Asset Light"

        elif intensity <= 8:
            label = "Moderate"

        else:
            label = "Capital Intensive"

        return intensity, label

    # ==========================================================
    # FCF CAGR
    # ==========================================================

    def fcf_cagr(self, company_cashflow):

        df = company_cashflow.copy()

        df["fcf"] = (
            df["operating_activity"]
            + df["investing_activity"]
        )

        df = df.dropna(
            subset=["fcf"]
        )

        if len(df) < 2:
            return np.nan

        first = df.iloc[0]["fcf"]
        last = df.iloc[-1]["fcf"]

        if (
            first <= 0
            or last <= 0
        ):
            return np.nan

        years = (
            df.iloc[-1]["year"]
            - df.iloc[0]["year"]
        )

        if years <= 0:
            return np.nan

        return (
            (
                last / first
            ) ** (1 / years)
            - 1
        ) * 100

    # ==========================================================
    # FCF Conversion
    # ==========================================================

    def fcf_conversion(
        self,
        company_cashflow,
        company_pl
    ):

        merged = company_cashflow.merge(
            company_pl[
                [
                    "company_id",
                    "year",
                    "net_profit"
                ]
            ],
            on=["company_id", "year"],
            how="left"
        )

        latest = merged.iloc[-1]

        fcf = (
            latest["operating_activity"]
            + latest["investing_activity"]
        )

        pat = latest["net_profit"]

        if (
            pd.isna(pat)
            or pat == 0
        ):
            return np.nan

        return (
            fcf / abs(pat)
        ) * 100

    # ==========================================================
    # Distress signal
    # ==========================================================

    def distress_signal(
        self,
        company_cashflow
    ):

        latest = company_cashflow.iloc[-1]

        cfo = latest[
            "operating_activity"
        ]

        cff = latest[
            "financing_activity"
        ]

        return (
            pd.notna(cfo)
            and pd.notna(cff)
            and cfo < 0
            and cff > 0
        )

    # ==========================================================
    # Capital allocation label
    # ==========================================================

    def capital_allocation(
        self,
        company_cashflow
    ):

        latest = company_cashflow.iloc[-1]

        cfo = latest[
            "operating_activity"
        ]

        cfi = latest[
            "investing_activity"
        ]

        cff = latest[
            "financing_activity"
        ]

        if pd.isna(cfo):
            return "Unknown"

        if cfo < 0 and cff > 0:
            return "Distress Signal"

        if cfo > 0 and cfi < 0 and cff < 0:
            return "Deleverager"

        if cfo > 0 and cfi < 0 and cff > 0:
            return "Reinvestor"

        if cfo > 0 and cfi > 0 and cff < 0:
            return "Cash Returner"

        if cfo > 0 and cfi > 0 and cff > 0:
            return "Cash Accumulator"

        if cfo < 0:
            return "Cash Burner"

        return "Balanced"

    # ==========================================================
    # Generate
    # ==========================================================

    def generate(self):

        (
            cashflow,
            pl,
            companies,
            sectors
        ) = self.load_data()

        results = []

        distress_results = []

        for company_id in companies[
            "company_id"
        ]:

            cf = cashflow[
                cashflow["company_id"]
                == company_id
            ].copy()

            company_pl = pl[
                pl["company_id"]
                == company_id
            ].copy()

            if cf.empty:

                sector_row = sectors[
                    sectors["company_id"] == company_id
                ]

                sector = "Unknown"

                if (
                    not sector_row.empty
                    and "broad_sector" in sector_row.columns
                ):
                    sector = sector_row.iloc[0]["broad_sector"]

                results.append({

                    "company_id": company_id,

                    "sector": sector,

                    "cfo_quality_score": np.nan,

                    "cfo_quality_label": "Insufficient Data",

                    "capex_intensity_pct": np.nan,

                    "capex_label": "Insufficient Data",

                    "fcf_cagr_5yr": np.nan,

                    "fcf_conversion_pct": np.nan,

                    "distress_flag": False,

                    "deleveraging_flag": False,

                    "capital_allocation_label": "Insufficient Data"

                })

                continue

            cf = cf.sort_values("year")

            company_pl = company_pl.sort_values(
                "year"
            )

            latest = cf.iloc[-1]

            (
                cfo_score,
                cfo_label,
                merged
            ) = self.cfo_quality(
                cf,
                company_pl
            )

            (
                capex_pct,
                capex_label
            ) = self.capex_intensity(
                cf,
                company_pl
            )

            fcf_cagr = self.fcf_cagr(
                cf
            )

            fcf_conversion = self.fcf_conversion(
                cf,
                company_pl
            )

            distress = self.distress_signal(
                cf
            )

            allocation = self.capital_allocation(
                cf
            )

            sector_row = sectors[
                sectors["company_id"]
                == company_id
            ]

            sector = "Unknown"

            if (
                not sector_row.empty
                and "broad_sector"
                in sector_row.columns
            ):
                sector = sector_row.iloc[0][
                    "broad_sector"
                ]

            # --------------------------------------------------
            # Deleveraging
            # --------------------------------------------------

            # Your cashflow table doesn't contain borrowings.
            # Therefore we check balancesheet if available.

            deleveraging = False

            try:

                bs = pd.read_sql(
                    """
                    SELECT *
                    FROM balancesheet
                    WHERE company_id = ?
                    ORDER BY year
                    """,
                    self.conn,
                    params=[company_id]
                )

                borrowing_column = None

                for column in [
                    "borrowings",
                    "borrowings_cr",
                    "total_debt",
                    "total_debt_cr"
                ]:

                    if column in bs.columns:
                        borrowing_column = column
                        break

                if (
                    borrowing_column
                    and len(bs) >= 2
                ):

                    previous = pd.to_numeric(
                        bs.iloc[-2][
                            borrowing_column
                        ],
                        errors="coerce"
                    )

                    current = pd.to_numeric(
                        bs.iloc[-1][
                            borrowing_column
                        ],
                        errors="coerce"
                    )

                    cff = latest[
                        "financing_activity"
                    ]

                    deleveraging = (
                        pd.notna(previous)
                        and pd.notna(current)
                        and current < previous
                        and pd.notna(cff)
                        and cff < 0
                    )

            except Exception:
                deleveraging = False

            row = {

                "company_id":
                    company_id,

                "sector":
                    sector,

                "cfo_quality_score":
                    cfo_score,

                "cfo_quality_label":
                    cfo_label,

                "capex_intensity_pct":
                    capex_pct,

                "capex_label":
                    capex_label,

                "fcf_cagr_5yr":
                    fcf_cagr,

                "fcf_conversion_pct":
                    fcf_conversion,

                "distress_flag":
                    distress,

                "deleveraging_flag":
                    deleveraging,

                "capital_allocation_label":
                    allocation

            }

            results.append(row)

            if distress:

                latest_pl = company_pl.iloc[-1]

                distress_results.append({

                    "company_id":
                        company_id,

                    "sector":
                        sector,

                    "cfo":
                        latest[
                            "operating_activity"
                        ],

                    "cff":
                        latest[
                            "financing_activity"
                        ],

                    "latest_net_profit":
                        latest_pl[
                            "net_profit"
                        ]

                })

        result = pd.DataFrame(results)

        distress_df = pd.DataFrame(
            distress_results
        )

        return result, distress_df

    # ==========================================================
    # Export
    # ==========================================================

    def export(self):

        result, distress = self.generate()

        os.makedirs(
            "output",
            exist_ok=True
        )

        result.to_excel(
            "output/cashflow_intelligence.xlsx",
            index=False
        )

        distress.to_csv(
            "output/distress_alerts.csv",
            index=False
        )

        print(
            "Cash Flow Intelligence rows:",
            len(result)
        )

        print(
            "Distress alerts:",
            len(distress)
        )

        print()

        print(
            "Saved:",
            "output/cashflow_intelligence.xlsx"
        )

        print(
            "Saved:",
            "output/distress_alerts.csv"
        )

        return result

    def close(self):

        self.conn.close()


if __name__ == "__main__":

    engine = CashFlowIntelligence()

    result = engine.export()

    engine.close()