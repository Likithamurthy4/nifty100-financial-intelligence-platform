import numpy as np
import pandas as pd


class CompositeScore:

    @staticmethod
    def normalize(series, inverse=False):
        series = series.fillna(0)

        p10 = np.percentile(series, 10)
        p90 = np.percentile(series, 90)

        series = series.clip(lower=p10, upper=p90)

        if p90 == p10:
            score = pd.Series(100, index=series.index)
        else:
            score = ((series - p10) / (p90 - p10)) * 100

        if inverse:
            score = 100 - score

        return score

    def calculate(self, df):

        # ---------- Profitability ----------
        roe = self.normalize(df["return_on_equity_pct"])
        roce = self.normalize(df["roce_percentage"])
        npm = self.normalize(df["net_profit_margin_pct"])

        profitability = roe * 0.15 + roce * 0.10 + npm * 0.10

        # ---------- Cash Quality ----------
        fcf = self.normalize(df["free_cash_flow_cr"])

        cfo_pat = pd.Series(100, index=df.index)

        fcf_positive = (df["free_cash_flow_cr"] > 0).astype(int) * 100

        cash_quality = fcf * 0.15 + cfo_pat * 0.10 + fcf_positive * 0.05

        # ---------- Growth ----------
        revenue = self.normalize(df["revenue_cagr_5yr"])
        pat = self.normalize(df["pat_cagr_5yr"])

        growth = revenue * 0.10 + pat * 0.10

        # ---------- Leverage ----------
        debt = self.normalize(df["debt_to_equity"], inverse=True)
        icr = self.normalize(df["interest_coverage"])

        leverage = debt * 0.10 + icr * 0.05

        df["composite_quality_score"] = (
            profitability + cash_quality + growth + leverage
        ).round(2)

        return df
