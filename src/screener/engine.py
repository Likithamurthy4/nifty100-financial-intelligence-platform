import yaml
import pandas as pd

from screener.loader import ScreenerLoader


class ScreenerEngine:

    def __init__(self,
                 config_path="config/screener_config.yaml"):

        with open(config_path, "r") as file:
            self.config = yaml.safe_load(file)

        loader = ScreenerLoader()
        self.df = loader.load_master_dataframe()
        loader.close()
        print(self.df.columns.tolist())

    def apply_filters(self, preset):

        if preset not in self.config:
            raise ValueError(f"Preset '{preset}' not found.")

        rules = self.config[preset]
        df = self.df.copy()

        # -------------------------
        # Generic Column Mapping
        # -------------------------

        column_map = {
            "roe_min": ("return_on_equity_pct", ">="),
            "free_cash_flow_min": ("free_cash_flow_cr", ">="),
            "revenue_cagr_3yr_min": ("revenue_cagr_3yr", ">="),
            "revenue_cagr_5yr_min": ("revenue_cagr_5yr", ">="),
            "pat_cagr_5yr_min": ("pat_cagr_5yr", ">="),
            "sales_min": ("sales", ">="),
            "pe_max": ("pe_ratio", "<="),
            "pb_max": ("pb_ratio", "<="),
            "dividend_yield_min": ("dividend_yield_pct", ">="),
            "dividend_payout_max": ("dividend_payout_ratio_pct", "<=")
        }

        # -------------------------
        # Apply Generic Filters
        # -------------------------

        for rule, value in rules.items():

            if rule in [
                "debt_to_equity_max",
                "debt_to_equity_exact",
                "debt_declining",
                "icr_min"
            ]:
                continue

            if rule not in column_map:
                continue

            column, operator = column_map[rule]

            if operator == ">=":
                df = df[df[column] >= value]
            else:
                df = df[df[column] <= value]

        # -------------------------
        # Debt-to-Equity Max
        # -------------------------

        if "debt_to_equity_max" in rules:

            threshold = rules["debt_to_equity_max"]

            financials = (
                df["broad_sector"]
                .fillna("")
                .str.lower()
                == "financials"
            )

            non_financial = (
                df["debt_to_equity"] <= threshold
            )

            df = df[
                financials | non_financial
            ]

        # -------------------------
        # Debt-to-Equity Exact
        # -------------------------

        if "debt_to_equity_exact" in rules:

            threshold = rules["debt_to_equity_exact"]

            df = df[
                df["debt_to_equity"].fillna(-999).round(2) == threshold
            ]

        # -------------------------
        # Interest Coverage
        # -------------------------

        if "icr_min" in rules:

            threshold = rules["icr_min"]

            df = df[
                (df["interest_coverage"].isna()) |
                (df["interest_coverage"] >= threshold)
            ]

        # -------------------------
        # Latest Year Only
        # -------------------------

        df = df.sort_values(
            by=["company_id", "year"]
        )

        df = df.groupby("company_id").tail(1)

        # -------------------------
        # Final Sort
        # -------------------------

        df = df.sort_values(
            by="composite_quality_score",
            ascending=False
        )

        return df.reset_index(drop=True)
    