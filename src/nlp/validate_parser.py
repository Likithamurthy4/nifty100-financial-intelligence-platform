import sqlite3
import pandas as pd
import os


DATABASE = "db/nifty100.db"


def main():

    conn = sqlite3.connect(DATABASE)

    parsed = pd.read_csv(
        "output/analysis_parsed.csv"
    )

    # Only 5-year values are useful for
    # comparison with the Ratio Engine.
    parsed_5yr = parsed[
        parsed["period_years"] == 5
    ].copy()

    # Ratio Engine values
    ratios = pd.read_sql(
        """
        SELECT
            company_id,
            revenue_cagr_5yr,
            pat_cagr_5yr,
            return_on_equity_pct
        FROM financial_ratios
        """,
        conn
    )

    conn.close()

    # Keep latest available ratio record per company
    ratios = (
        ratios
        .sort_values("company_id")
        .groupby("company_id")
        .last()
        .reset_index()
    )

    checks = []

    for _, row in parsed_5yr.iterrows():

        company = row["company_id"]
        metric = row["metric_type"]
        parsed_value = row["value_pct"]

        match = ratios[
            ratios["company_id"] == company
        ]

        if match.empty:
            continue

        ratio = match.iloc[0]

        if metric == "compounded_sales_growth":

            engine_value = ratio["revenue_cagr_5yr"]

        elif metric == "compounded_profit_growth":

            engine_value = ratio["pat_cagr_5yr"]

        elif metric == "roe":

            engine_value = ratio["return_on_equity_pct"]

        else:
            # No matching Ratio Engine metric
            # for stock price CAGR.
            continue

        if pd.isna(engine_value):
            continue

        divergence = abs(
            parsed_value - engine_value
        )

        flag = (
            "MANUAL REVIEW"
            if divergence > 5
            else "OK"
        )

        checks.append({

            "company_id": company,

            "metric_type": metric,

            "parsed_value_pct": parsed_value,

            "engine_value_pct": engine_value,

            "divergence_pct_points": divergence,

            "flag": flag

        })

    result = pd.DataFrame(checks)

    os.makedirs(
        "output",
        exist_ok=True
    )

    result.to_csv(
        "output/parser_cross_validation.csv",
        index=False
    )

    print(
        "Cross-validation rows:",
        len(result)
    )

    print(
        "Manual review:",
        (result["flag"] == "MANUAL REVIEW").sum()
        if not result.empty
        else 0
    )

    print(
        "Saved: output/parser_cross_validation.csv"
    )


if __name__ == "__main__":
    main()