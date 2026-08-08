import os
import sqlite3
import pandas as pd
import numpy as np


DATABASE = "db/nifty100.db"


# ============================================================
# Helpers
# ============================================================

def safe_float(value):
    try:
        if pd.isna(value):
            return np.nan
        return float(value)
    except (ValueError, TypeError):
        return np.nan


def latest_row(df):
    if df.empty:
        return pd.Series(dtype="object")

    if "year" in df.columns:
        df = df.sort_values("year")

    return df.iloc[-1]


def consecutive_positive(values, count=3):
    values = pd.Series(values).dropna()

    if len(values) < count:
        return False

    return all(values.iloc[-count:] > 0)


def consecutive_negative(values, count=3):
    values = pd.Series(values).dropna()

    if len(values) < count:
        return False

    return all(values.iloc[-count:] < 0)


def increasing(values, count=3):
    values = pd.Series(values).dropna()

    if len(values) < count:
        return False

    values = values.iloc[-count:].tolist()

    return all(
        values[i] > values[i - 1]
        for i in range(1, len(values))
    )


def decreasing(values, count=3):
    values = pd.Series(values).dropna()

    if len(values) < count:
        return False

    values = values.iloc[-count:].tolist()

    return all(
        values[i] < values[i - 1]
        for i in range(1, len(values))
    )


def get_confidence(signal, threshold, maximum=None):
    """
    Returns a confidence score between 60 and 100.
    Stronger signals receive higher confidence.
    """

    if pd.isna(signal):
        return 0

    signal = abs(float(signal))
    threshold = abs(float(threshold))

    if threshold == 0:
        return 70

    if maximum is None:
        maximum = threshold * 2

    if signal >= maximum:
        return 95

    ratio = signal / threshold

    return min(
        95,
        max(
            61,
            60 + int(ratio * 25)
        )
    )


# ============================================================
# Generator
# ============================================================

class ProsConsGenerator:

    def __init__(self):

        self.conn = sqlite3.connect(DATABASE)

        self.companies = pd.read_sql(
            """
            SELECT
                id AS company_id,
                company_name
            FROM companies
            """,
            self.conn
        )

        self.ratios = pd.read_sql(
            """
            SELECT *
            FROM financial_ratios
            ORDER BY company_id, year
            """,
            self.conn
        )

        self.pl = pd.read_sql(
            """
            SELECT *
            FROM profitandloss
            ORDER BY company_id, year
            """,
            self.conn
        )

        self.cf = pd.read_sql(
            """
            SELECT *
            FROM cashflow
            ORDER BY company_id, year
            """,
            self.conn
        )

        self.bs = pd.read_sql(
            """
            SELECT *
            FROM balancesheet
            ORDER BY company_id, year
            """,
            self.conn
        )

        self.sectors = pd.read_sql(
            """
            SELECT *
            FROM sectors
            """,
            self.conn
        )

        self.results = []

    # ========================================================
    # Add result
    # ========================================================

    def add_result(
        self,
        company_id,
        result_type,
        rule_id,
        text,
        confidence
    ):

        confidence = float(confidence)

        # Sprint requirement:
        # only include confidence > 60
        if confidence > 60:

            self.results.append({

                "company_id": company_id,

                "type": result_type,

                "rule_id": rule_id,

                "text": text,

                "confidence_pct": round(
                    confidence,
                    2
                )

            })

    # ========================================================
    # Company data
    # ========================================================

    def company_data(self, company_id):

        ratios = self.ratios[
            self.ratios["company_id"] == company_id
        ].copy()

        pl = self.pl[
            self.pl["company_id"] == company_id
        ].copy()

        cf = self.cf[
            self.cf["company_id"] == company_id
        ].copy()

        bs = self.bs[
            self.bs["company_id"] == company_id
        ].copy()

        sector_row = self.sectors[
            self.sectors["company_id"] == company_id
        ]

        sector = "Unknown"

        if not sector_row.empty:

            if "broad_sector" in sector_row.columns:

                sector = sector_row.iloc[0]["broad_sector"]

        return ratios, pl, cf, bs, sector

    # ========================================================
    # Generate
    # ========================================================

    def generate(self):

        for _, company in self.companies.iterrows():

            company_id = company["company_id"]

            ratios, pl, cf, bs, sector = (
                self.company_data(company_id)
            )

            if ratios.empty:
                continue

            latest_ratio = latest_row(ratios)

            latest_pl = latest_row(pl)

            latest_cf = latest_row(cf)

            latest_bs = latest_row(bs)

            # =================================================
            # COMMON METRICS
            # =================================================

            roe = safe_float(
                latest_ratio.get(
                    "return_on_equity_pct"
                )
            )

            roce = safe_float(
                latest_ratio.get(
                    "roce_percentage"
                )
            )

            de = safe_float(
                latest_ratio.get(
                    "debt_to_equity"
                )
            )

            icr = safe_float(
                latest_ratio.get(
                    "interest_coverage"
                )
            )

            fcf = safe_float(
                latest_ratio.get(
                    "free_cash_flow_cr"
                )
            )

            revenue_cagr = safe_float(
                latest_ratio.get(
                    "revenue_cagr_5yr"
                )
            )

            pat_cagr = safe_float(
                latest_ratio.get(
                    "pat_cagr_5yr"
                )
            )

            eps_cagr = safe_float(
                latest_ratio.get(
                    "eps_cagr_5yr"
                )
            )

            dividend_yield = safe_float(
                latest_ratio.get(
                    "dividend_yield_pct"
                )
            )

            opm = safe_float(
                latest_ratio.get(
                    "operating_profit_margin_pct"
                )
            )

            # =================================================
            # PRO 1
            # ROE > 20% sustained for 3+ years
            # =================================================

            roe_history = ratios.get(
                "return_on_equity_pct",
                pd.Series(dtype=float)
            )

            if (
                len(roe_history.dropna()) >= 3
                and all(
                    roe_history.dropna().iloc[-3:] > 20
                )
            ):

                confidence = get_confidence(
                    roe,
                    20,
                    40
                )

                self.add_result(
                    company_id,
                    "pro",
                    "PRO-01",
                    "Consistently high return on equity above 20% demonstrates exceptional capital efficiency",
                    confidence
                )

            # =================================================
            # PRO 2
            # FCF positive for 5 consecutive years
            # =================================================

            fcf_history = ratios.get(
                "free_cash_flow_cr",
                pd.Series(dtype=float)
            )

            if consecutive_positive(
                fcf_history,
                5
            ):

                confidence = 90

                self.add_result(
                    company_id,
                    "pro",
                    "PRO-02",
                    "Strong free cash flow generation over 5 years signals healthy business fundamentals",
                    confidence
                )

            # =================================================
            # PRO 3
            # D/E = 0
            # =================================================

            if not pd.isna(de) and de == 0:

                self.add_result(
                    company_id,
                    "pro",
                    "PRO-03",
                    "Debt-free balance sheet provides financial flexibility and eliminates interest burden",
                    98
                )

            # =================================================
            # PRO 4
            # Revenue CAGR > 15%
            # =================================================

            if not pd.isna(revenue_cagr) and revenue_cagr > 15:

                confidence = get_confidence(
                    revenue_cagr,
                    15,
                    30
                )

                self.add_result(
                    company_id,
                    "pro",
                    "PRO-04",
                    "Revenue growing at above 15% CAGR over 5 years reflects strong business momentum",
                    confidence
                )

            # =================================================
            # PRO 5
            # OPM > 25%
            # =================================================

            if not pd.isna(opm) and opm > 25:

                confidence = get_confidence(
                    opm,
                    25,
                    40
                )

                self.add_result(
                    company_id,
                    "pro",
                    "PRO-05",
                    "Operating profit margin above 25% indicates strong pricing power and cost discipline",
                    confidence
                )

            # =================================================
            # PRO 6
            # PAT CAGR > 20%
            # =================================================

            if not pd.isna(pat_cagr) and pat_cagr > 20:

                confidence = get_confidence(
                    pat_cagr,
                    20,
                    40
                )

                self.add_result(
                    company_id,
                    "pro",
                    "PRO-06",
                    "Net profit compounding at above 20% over 5 years creates significant shareholder value",
                    confidence
                )

            # =================================================
            # PRO 7
            # ICR > 10 OR debt free
            # =================================================

            if (
                (not pd.isna(icr) and icr > 10)
                or
                (not pd.isna(de) and de == 0)
            ):

                confidence = 95

                self.add_result(
                    company_id,
                    "pro",
                    "PRO-07",
                    "Very high interest coverage ratio reflects negligible financial stress from debt servicing",
                    confidence
                )

            # =================================================
            # PRO 8
            # Dividend Yield > 2 + FCF positive
            # =================================================

            if (
                not pd.isna(dividend_yield)
                and dividend_yield > 2
                and not pd.isna(fcf)
                and fcf > 0
            ):

                confidence = 90

                self.add_result(
                    company_id,
                    "pro",
                    "PRO-08",
                    "Consistent dividend yield above 2% backed by positive free cash flow",
                    confidence
                )

            # =================================================
            # PRO 9
            # EPS CAGR > 15%
            # =================================================

            if not pd.isna(eps_cagr) and eps_cagr > 15:

                confidence = get_confidence(
                    eps_cagr,
                    15,
                    30
                )

                self.add_result(
                    company_id,
                    "pro",
                    "PRO-09",
                    "Earnings per share growing above 15% CAGR indicates strong earnings quality and compounding",
                    confidence
                )

            # =================================================
            # PRO 10
            # ROE improving 3 consecutive years
            # =================================================

            if increasing(
                roe_history,
                3
            ):

                self.add_result(
                    company_id,
                    "pro",
                    "PRO-10",
                    "Return on equity improving for 3 consecutive years shows strengthening business quality",
                    85
                )

            # =================================================
            # PRO 11
            # Revenue CAGR > PAT CAGR
            # =================================================

            if (
                not pd.isna(revenue_cagr)
                and not pd.isna(pat_cagr)
                and revenue_cagr > pat_cagr
            ):

                self.add_result(
                    company_id,
                    "pro",
                    "PRO-11",
                    "Revenue growing slower than profits shows improving operating leverage and scale benefits",
                    75
                )

            # =================================================
            # PRO 12
            # Assets growing + debt declining
            # =================================================

            if (
                not bs.empty
                and "total_assets" in bs.columns
            ):

                assets = pd.to_numeric(
                    bs["total_assets"],
                    errors="coerce"
                )

                debt_column = None

                for candidate in [
                    "total_debt",
                    "total_debt_cr",
                    "borrowings",
                    "borrowings_cr"
                ]:

                    if candidate in bs.columns:
                        debt_column = candidate
                        break

                if (
                    debt_column
                    and len(assets.dropna()) >= 2
                ):

                    debt_history = pd.to_numeric(
                        bs[debt_column],
                        errors="coerce"
                    )

                    if (
                        assets.iloc[-1] > assets.iloc[-2]
                        and debt_history.iloc[-1] <
                        debt_history.iloc[-2]
                    ):

                        self.add_result(
                            company_id,
                            "pro",
                            "PRO-12",
                            "Growing asset base funded by internal accruals reflects self-sustaining growth",
                            80
                        )

            # =================================================
            # CON 1
            # D/E > 2 non-financial
            # =================================================

            financial_sectors = {
                "Financials",
                "Banks",
                "Insurance"
            }

            if (
                not pd.isna(de)
                and de > 2
                and sector not in financial_sectors
            ):

                confidence = get_confidence(
                    de,
                    2,
                    4
                )

                self.add_result(
                    company_id,
                    "con",
                    "CON-01",
                    f"Debt-to-equity ratio of {de:.2f} is elevated for a non-financial company and warrants monitoring",
                    confidence
                )

            # =================================================
            # CON 2
            # FCF negative for 3 years
            # =================================================

            if consecutive_negative(
                fcf_history,
                3
            ):

                self.add_result(
                    company_id,
                    "con",
                    "CON-02",
                    "Free cash flow negative for 3 consecutive years raises concern about cash generation quality",
                    90
                )

            # =================================================
            # CON 3
            # OPM declining 3 years
            # =================================================

            opm_history = ratios.get(
                "operating_profit_margin_pct",
                pd.Series(dtype=float)
            )

            if decreasing(
                opm_history,
                3
            ):

                self.add_result(
                    company_id,
                    "con",
                    "CON-03",
                    "Operating margins declining for 3 consecutive years suggest pricing or cost pressure",
                    85
                )

            # =================================================
            # CON 4
            # Net profit negative latest
            # =================================================

            latest_profit = safe_float(
                latest_pl.get(
                    "net_profit"
                )
            )

            if (
                not pd.isna(latest_profit)
                and latest_profit < 0
            ):

                self.add_result(
                    company_id,
                    "con",
                    "CON-04",
                    "Company reported a net loss in the most recent financial year",
                    95
                )

            # =================================================
            # CON 5
            # Revenue declining 2+ years
            # =================================================

            sales_history = pl.get(
                "sales",
                pd.Series(dtype=float)
            )

            if decreasing(
                sales_history,
                2
            ):

                self.add_result(
                    company_id,
                    "con",
                    "CON-05",
                    "Revenue contraction over 2 consecutive years indicates demand weakness or market share loss",
                    85
                )

            # =================================================
            # CON 6
            # ICR < 1.5
            # =================================================

            if (
                not pd.isna(icr)
                and icr < 1.5
            ):

                self.add_result(
                    company_id,
                    "con",
                    "CON-06",
                    "Interest coverage ratio below 1.5x indicates the company is at risk of not meeting its debt obligations",
                    90
                )

            # =================================================
            # CON 7
            # Dividend payout > 100%
            # =================================================

            payout = safe_float(
                latest_ratio.get(
                    "dividend_payout_ratio_pct"
                )
            )

            if (
                not pd.isna(payout)
                and payout > 100
            ):

                self.add_result(
                    company_id,
                    "con",
                    "CON-07",
                    "Dividend payout ratio above 100% means the company is paying dividends from reserves, which is unsustainable",
                    95
                )

            # =================================================
            # CON 8
            # D/E rising 3 years
            # =================================================

            de_history = ratios.get(
                "debt_to_equity",
                pd.Series(dtype=float)
            )

            if increasing(
                de_history,
                3
            ):

                self.add_result(
                    company_id,
                    "con",
                    "CON-08",
                    "Rising debt-to-equity ratio over 3 years suggests increasing financial leverage risk",
                    85
                )

            # =================================================
            # CON 9
            # EPS declining 3 years
            # =================================================

            eps_history = pl.get(
                "eps",
                pd.Series(dtype=float)
            )

            if decreasing(
                eps_history,
                3
            ):

                self.add_result(
                    company_id,
                    "con",
                    "CON-09",
                    "Earnings per share declining for 3 consecutive years reflects deteriorating profitability",
                    85
                )

            # =================================================
            # CON 10
            # ROCE < 10
            # =================================================

            if (
                not pd.isna(roce)
                and roce < 10
            ):

                self.add_result(
                    company_id,
                    "con",
                    "CON-10",
                    "Return on capital employed below 10% suggests the business is not generating sufficient returns on invested capital",
                    90
                )

            # =================================================
            # CON 11
            # Net Debt > 3x EBITDA
            # =================================================

            net_debt = np.nan

            for candidate in [
                "net_debt_cr",
                "net_debt"
            ]:

                if candidate in bs.columns:

                    net_debt = safe_float(
                        latest_bs.get(candidate)
                    )

                    break

            ebitda = np.nan

            if (
                "operating_profit" in latest_pl.index
                and "depreciation" in latest_pl.index
            ):

                operating_profit = safe_float(
                    latest_pl.get(
                        "operating_profit"
                    )
                )

                depreciation = safe_float(
                    latest_pl.get(
                        "depreciation"
                    )
                )

                if (
                    not pd.isna(operating_profit)
                    and not pd.isna(depreciation)
                ):

                    ebitda = (
                        operating_profit
                        + depreciation
                    )

            if (
                not pd.isna(net_debt)
                and not pd.isna(ebitda)
                and ebitda > 0
                and net_debt > 3 * ebitda
            ):

                self.add_result(
                    company_id,
                    "con",
                    "CON-11",
                    "Net debt exceeding 3 times EBITDA is a high leverage ratio and limits financial flexibility",
                    90
                )

            # =================================================
            # CON 12
            # Revenue CAGR < 5%
            # =================================================

            if (
                not pd.isna(revenue_cagr)
                and revenue_cagr < 5
            ):

                confidence = 85

                self.add_result(
                    company_id,
                    "con",
                    "CON-12",
                    "Revenue growing at below 5% over 5 years lags inflation and suggests limited business momentum",
                    confidence
                )

        return pd.DataFrame(self.results)

    # ========================================================
    # Guarantee at least one pro and con per company
    # ========================================================

    def add_fallbacks(self, result):

        for company_id in self.companies["company_id"]:

            company_results = result[
                result["company_id"] == company_id
            ]

            has_pro = (
                company_results["type"]
                .eq("pro")
                .any()
            )

            has_con = (
                company_results["type"]
                .eq("con")
                .any()
            )

            if not has_pro:

                result.loc[len(result)] = {

                    "company_id": company_id,

                    "type": "pro",

                    "rule_id": "PRO-FALLBACK",

                    "text":
                    "No major positive financial signal crossed the defined rule thresholds; company fundamentals require further review.",

                    "confidence_pct": 61.0
                }

            if not has_con:

                result.loc[len(result)] = {

                    "company_id": company_id,

                    "type": "con",

                    "rule_id": "CON-FALLBACK",

                    "text":
                    "No major negative financial signal crossed the defined rule thresholds; continued monitoring is recommended.",

                    "confidence_pct": 61.0
                }

        return result

    # ========================================================
    # Export
    # ========================================================

    def export(self):

        result = self.generate()

        result = self.add_fallbacks(
            result
        )

        os.makedirs(
            "output",
            exist_ok=True
        )

        result.to_csv(
            "output/pros_cons_generated.csv",
            index=False
        )

        print(
            "Pros/Cons rows:",
            len(result)
        )

        print(
            "Companies:",
            result["company_id"].nunique()
        )

        print()

        print(
            "Pro count:",
            (result["type"] == "pro").sum()
        )

        print(
            "Con count:",
            (result["type"] == "con").sum()
        )

        print()

        print(
            "Saved:",
            "output/pros_cons_generated.csv"
        )

        return result

    def close(self):

        self.conn.close()


if __name__ == "__main__":

    generator = ProsConsGenerator()

    result = generator.export()

    generator.close()