import sqlite3
import pandas as pd


DATABASE = "db/nifty100.db"

CAPITAL_FILE = "output/capital_allocation.csv"
CASHFLOW_FILE = "output/cashflow_intelligence.xlsx"


def main():

    # ---------------------------------------------------------
    # Load capital allocation
    # ---------------------------------------------------------

    capital = pd.read_csv(
        CAPITAL_FILE
    )

    capital = capital.sort_values(
        ["company_id", "year"]
    )

    # ---------------------------------------------------------
    # 1. Verify company/year coverage
    # ---------------------------------------------------------

    print("=== CAPITAL ALLOCATION QA ===")

    print(
        "Rows:",
        len(capital)
    )

    print(
        "Unique companies:",
        capital["company_id"].nunique()
    )

    print(
        "Year range:",
        capital["year"].min(),
        "-",
        capital["year"].max()
    )

    print("\nCompanies per year:")

    print(
        capital.groupby("year")["company_id"]
        .nunique()
        .to_string()
    )

    # ---------------------------------------------------------
    # 2. Latest-year distribution
    # ---------------------------------------------------------

    latest_year = capital["year"].max()

    latest = capital[
        capital["year"] == latest_year
    ]

    print(
        f"\n=== {latest_year} PATTERN DISTRIBUTION ==="
    )

    distribution = (
        latest["pattern_label"]
        .value_counts()
    )

    print(
        distribution.to_string()
    )

    # ---------------------------------------------------------
    # 3. Detect year-over-year pattern changes
    # ---------------------------------------------------------

    capital["previous_pattern"] = (
        capital
        .groupby("company_id")["pattern_label"]
        .shift(1)
    )

    capital["previous_year"] = (
        capital
        .groupby("company_id")["year"]
        .shift(1)
    )

    changes = capital[
        capital["previous_pattern"].notna()
        &
        (
            capital["pattern_label"]
            != capital["previous_pattern"]
        )
    ].copy()

    changes = changes[
        [
            "company_id",
            "previous_year",
            "year",
            "previous_pattern",
            "pattern_label"
        ]
    ]

    changes = changes.rename(
        columns={
            "previous_year":
                "from_year",

            "year":
                "to_year",

            "previous_pattern":
                "from_pattern",

            "pattern_label":
                "to_pattern"
        }
    )

    changes.to_csv(
        "output/pattern_changes.csv",
        index=False
    )

    print(
        "\nPattern changes:",
        len(changes)
    )

    print(
        "Saved: output/pattern_changes.csv"
    )

    # ---------------------------------------------------------
    # 4. Merge latest capital allocation into
    #    cashflow_intelligence.xlsx
    # ---------------------------------------------------------

    intelligence = pd.read_excel(
        CASHFLOW_FILE
    )

    latest_allocation = latest[
        [
            "company_id",
            "pattern_label"
        ]
    ].copy()

    latest_allocation = latest_allocation.rename(
        columns={
            "pattern_label":
                "capital_allocation_label"
        }
    )

    # Remove existing column if rerunning
    if "capital_allocation_label" in intelligence.columns:

        intelligence = intelligence.drop(
            columns=["capital_allocation_label"]
        )

    intelligence = intelligence.merge(
        latest_allocation,
        on="company_id",
        how="left"
    )

    intelligence.to_excel(
        CASHFLOW_FILE,
        index=False
    )

    print(
        "Updated:",
        CASHFLOW_FILE
    )

    # ---------------------------------------------------------
    # 5. Final QA
    # ---------------------------------------------------------

    print("\n=== FINAL QA ===")

    print(
        "Cash-flow intelligence rows:",
        len(intelligence)
    )

    print(
        "Unique companies:",
        intelligence["company_id"].nunique()
    )

    print(
        "Companies without allocation:",
        intelligence[
            "capital_allocation_label"
        ].isna().sum()
    )

    print("\nCompleted Day 32.")


if __name__ == "__main__":
    main()