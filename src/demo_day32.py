import os
import sqlite3

import pandas as pd

DATABASE = "db/nifty100.db"


def classify_pattern(cfo, cfi, cff):

    if pd.isna(cfo) or pd.isna(cfi) or pd.isna(cff):
        return "Insufficient Data"

    if cfo < 0 and cff > 0:
        return "Distress Signal"

    if cfo > 0 and cfi < 0 and cff < 0:
        return "Deleverager"

    if cfo > 0 and cfi < 0 and cff > 0:
        return "Reinvestor"

    if cfo > 0 and cfi > 0 and cff < 0:
        return "Shareholder Returns"

    if cfo > 0 and cfi > 0 and cff > 0:
        return "Cash Accumulator"

    if cfo < 0:
        return "Cash Burner"

    return "Balanced"


def main():

    conn = sqlite3.connect(DATABASE)

    cashflow = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            operating_activity,
            investing_activity,
            financing_activity
        FROM cashflow
        ORDER BY company_id, year
        """,
        conn,
    )

    companies = pd.read_sql(
        """
        SELECT id AS company_id
        FROM companies
        """,
        conn,
    )

    conn.close()

    records = []

    for _, row in cashflow.iterrows():

        cfo = row["operating_activity"]
        cfi = row["investing_activity"]
        cff = row["financing_activity"]

        pattern = classify_pattern(cfo, cfi, cff)

        records.append(
            {
                "company_id": row["company_id"],
                "year": row["year"],
                "cfo_sign": "+" if cfo > 0 else "-" if cfo < 0 else "0",
                "cfi_sign": "+" if cfi > 0 else "-" if cfi < 0 else "0",
                "cff_sign": "+" if cff > 0 else "-" if cff < 0 else "0",
                "pattern_label": pattern,
            }
        )

    result = pd.DataFrame(records)
    # ---------------------------------------------------------
    # Add companies with no cash-flow data
    # ---------------------------------------------------------

    existing_companies = set(result["company_id"])

    missing_companies = companies[~companies["company_id"].isin(existing_companies)]

    for company_id in missing_companies["company_id"]:

        result.loc[len(result)] = {
            "company_id": company_id,
            "year": 2024,
            "cfo_sign": "N/A",
            "cfi_sign": "N/A",
            "cff_sign": "N/A",
            "pattern_label": "Insufficient Data",
        }
    os.makedirs("output", exist_ok=True)

    result.to_csv("output/capital_allocation.csv", index=False)

    print("Capital allocation rows:", len(result))

    print("Unique companies:", result["company_id"].nunique())

    print("Years:", result["year"].min(), "to", result["year"].max())

    print("\nPattern distribution:")

    print(result["pattern_label"].value_counts())

    print("\nSaved:", "output/capital_allocation.csv")

    # ---------------------------------------------------------
    # Latest year distribution
    # ---------------------------------------------------------

    latest_year = result["year"].max()

    latest = result[result["year"] == latest_year]

    print(f"\nLatest year ({latest_year}) distribution:")

    print(latest["pattern_label"].value_counts())

    # ---------------------------------------------------------
    # Coverage check
    # ---------------------------------------------------------

    missing = companies[~companies["company_id"].isin(result["company_id"])]

    print("\nCompanies missing capital allocation data:", len(missing))

    if not missing.empty:
        print(missing.to_string(index=False))


if __name__ == "__main__":
    main()
