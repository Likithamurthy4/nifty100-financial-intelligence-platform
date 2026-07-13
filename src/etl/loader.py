"""
loader.py

Loads all Excel datasets,
normalizes them,
and prepares them
for SQLite.
"""

from pathlib import Path
import pandas as pd

from src.etl.normaliser import (
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


if __name__ == "__main__":

    all_data = load_all_datasets()

    print("\n========== DATA SUMMARY ==========")

    for name, df in all_data.items():

        print(f"{name:<20} {len(df)} rows")