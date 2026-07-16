"""
loader.py

Loads all Excel datasets,
normalizes them,
and prepares them
for SQLite.
"""

from pathlib import Path
import pandas as pd

from etl.normaliser import (
    normalize_ticker,
    normalize_year,
    clean_column_names,
)

# Folder containing datasets
RAW_DATA = Path("data/raw")

# Dataset configuration
DATASETS = {
    "companies": ("companies.xlsx", 1),
    "profitandloss": ("profitandloss.xlsx", 1),
    "balancesheet": ("balancesheet.xlsx", 1),
    "cashflow": ("cashflow.xlsx", 1),
    "analysis": ("analysis.xlsx", 1),
    "documents": ("documents.xlsx", 1),
    "prosandcons": ("prosandcons.xlsx", 1),

    # Supplementary datasets
    "sectors": ("sectors.xlsx", 0),
    "stock_prices": ("stock_prices.xlsx", 0),
    "market_cap": ("market_cap.xlsx", 0),
    "financial_ratios": ("financial_ratios.xlsx", 0),
    "peer_groups": ("peer_groups.xlsx", 0),
}


def load_excel(filename, header=0):
    """
    Load a single Excel file.
    """

    filepath = RAW_DATA / filename

    print(f"\nLoading {filename}...")

    df = pd.read_excel(filepath, header=header)

    df = clean_column_names(df)

    # Normalize ticker columns
    if "company_id" in df.columns:
        df["company_id"] = df["company_id"].apply(normalize_ticker)

    if filename == "companies.xlsx" and "id" in df.columns:
        df["id"] = df["id"].apply(normalize_ticker)

    # Normalize year column
    if "year" in df.columns:
        df["year"] = df["year"].apply(normalize_year)

    print(f"Loaded {len(df)} rows")

    return df


def load_all_datasets():
    """
    Load all datasets.
    """

    datasets = {}

    for name, (filename, header) in DATASETS.items():

        try:

            datasets[name] = load_excel(filename, header)

        except FileNotFoundError:

            print(f"❌ {filename} not found")

        except Exception as e:

            print(f"❌ Error loading {filename}: {e}")

    return datasets


from etl.validator import (
    dq01_primary_key,
    dq02_company_year,
    dq03_foreign_key,
    dq04_balance_sheet,
    dq05_opm,
    dq06_sales,
    dq07_cashflow,
    dq08_tax,
    dq09_dividend,
    dq10_eps,
    dq11_document,
    dq12_market_cap,
    dq13_debt,
    dq14_missing,
    dq15_empty,
    dq16_stock_date,
    save_validation_report,
)
if __name__ == "__main__":

    all_data = load_all_datasets()      # <-- FIRST

    companies_df = all_data["companies"]  # <-- SECOND

    for name, df in all_data.items():

        dq01_primary_key(df, name)
        dq02_company_year(df, name)
        dq03_foreign_key(df, companies_df, name)
        dq04_balance_sheet(df)
        dq05_opm(df)
        dq06_sales(df)
        dq07_cashflow(df)
        dq08_tax(df)
        dq09_dividend(df)
        dq10_eps(df)
        dq11_document(df)
        dq12_market_cap(df)
        dq13_debt(df)
        dq14_missing(df, name)
        dq15_empty(df, name)
        dq16_stock_date(df)

    save_validation_report()

    print("\n========== DATA SUMMARY ==========")

    for name, df in all_data.items():
        print(f"{name:<20} {len(df)} rows")