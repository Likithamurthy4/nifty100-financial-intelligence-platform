"""
normaliser.py

Utility functions for cleaning and standardizing
financial datasets before loading into SQLite.
"""

import re
import pandas as pd


def normalize_ticker(ticker):
    """
    Convert company ticker to uppercase and remove spaces.

    Example:
        " tcs " -> "TCS"
        "infy" -> "INFY"
    """
    if pd.isna(ticker):
        return None

    return str(ticker).strip().upper()


def normalize_year(year):
    """
    Convert year values into YYYY format.

    Examples:
        Mar-23 -> 2023
        Mar-2024 -> 2024
        FY2022 -> 2022
        2021 -> 2021
    """

    if pd.isna(year):
        return None

    year = str(year).strip()

    match = re.search(r'(\d{2,4})', year)

    if not match:
        return None

    value = match.group(1)

    if len(value) == 2:
        value = "20" + value

    return int(value)


def clean_text(text):
    """
    Remove unnecessary spaces/newlines.
    """

    if pd.isna(text):
        return None

    return " ".join(str(text).split())


def clean_column_names(df):
    """
    Convert column names into lowercase snake_case.
    """

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    return df