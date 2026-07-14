"""
validator.py

Sprint 1 - Day 3

Data Quality Validation Rules
"""

from pathlib import Path
import pandas as pd

OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

validation_errors = []


def add_error(rule, dataset, row, severity, message):

    validation_errors.append(
        {
            "Rule": rule,
            "Dataset": dataset,
            "Row": row,
            "Severity": severity,
            "Message": message
        }
    )


####################################################
# DQ-01
# Primary Key uniqueness
####################################################

def dq01_primary_key(df, dataset):

    if "id" not in df.columns:
        return

    duplicate = df[df.duplicated("id", keep=False)]

    for index in duplicate.index:

        add_error(
            "DQ-01",
            dataset,
            index,
            "CRITICAL",
            "Duplicate Primary Key"
        )


####################################################
# DQ-02
# company_id + year uniqueness
####################################################

def dq02_company_year(df, dataset):

    if "company_id" not in df.columns:
        return

    if "year" not in df.columns:
        return

    duplicate = df[
        df.duplicated(
            ["company_id", "year"],
            keep=False
        )
    ]

    for index in duplicate.index:

        add_error(
            "DQ-02",
            dataset,
            index,
            "CRITICAL",
            "Duplicate Company-Year"
        )


####################################################
# DQ-03
# Foreign Key validation
####################################################

def dq03_foreign_key(df, companies, dataset):

    if "company_id" not in df.columns:
        return

    valid = set(companies["id"])

    invalid = df[
        ~df["company_id"].isin(valid)
    ]

    for index in invalid.index:

        add_error(
            "DQ-03",
            dataset,
            index,
            "CRITICAL",
            "Invalid company_id"
        )


####################################################
# DQ-04
# Balance Sheet equation
####################################################

def dq04_balance_sheet(df):

    required = [

        "total_assets",
        "total_liabilities"

    ]

    if not all(c in df.columns for c in required):
        return

    difference = abs(

        df["total_assets"]
        -
        df["total_liabilities"]

    )

    invalid = df[difference > 1]

    for index in invalid.index:

        add_error(

            "DQ-04",

            "balancesheet",

            index,

            "WARNING",

            "Assets and Liabilities mismatch"

        )


####################################################
# DQ-05
# Operating Profit %
####################################################

def dq05_opm(df):

    required = [

        "sales",
        "operating_profit",
        "opm_percentage"

    ]

    if not all(c in df.columns for c in required):
        return

    valid = df[df["sales"] > 0]

    expected = (

        valid["operating_profit"]

        /

        valid["sales"]

    ) * 100

    difference = abs(

        expected

        -

        valid["opm_percentage"]

    )

    invalid = valid[difference > 2]

    for index in invalid.index:

        add_error(

            "DQ-05",

            "profitandloss",

            index,

            "WARNING",

            "Incorrect OPM %"

        )


####################################################
# DQ-06
# Positive Sales
####################################################

def dq06_sales(df):

    if "sales" not in df.columns:
        return

    invalid = df[df["sales"] <= 0]

    for index in invalid.index:

        add_error(

            "DQ-06",

            "profitandloss",

            index,

            "WARNING",

            "Sales must be positive"

        )


####################################################
# DQ-07
# Net Cash Flow
####################################################

def dq07_cashflow(df):

    required = [

        "operating_activity",

        "investing_activity",

        "financing_activity",

        "net_cash_flow"

    ]

    if not all(c in df.columns for c in required):
        return

    expected = (

        df["operating_activity"]

        +

        df["investing_activity"]

        +

        df["financing_activity"]

    )

    difference = abs(

        expected

        -

        df["net_cash_flow"]

    )

    invalid = df[difference > 2]

    for index in invalid.index:

        add_error(

            "DQ-07",

            "cashflow",

            index,

            "WARNING",

            "Net Cash Flow mismatch"

        )
####################################################
# DQ-08
# Tax Percentage
####################################################

def dq08_tax(df):

    if "tax_percentage" not in df.columns:
        return

    invalid = df[
        (df["tax_percentage"] < 0) |
        (df["tax_percentage"] > 100)
    ]

    for index in invalid.index:

        add_error(
            "DQ-08",
            "profitandloss",
            index,
            "WARNING",
            "Invalid Tax Percentage"
        )


####################################################
# DQ-09
# Dividend Payout
####################################################

def dq09_dividend(df):

    if "dividend_payout" not in df.columns:
        return

    invalid = df[df["dividend_payout"] < 0]

    for index in invalid.index:

        add_error(
            "DQ-09",
            "profitandloss",
            index,
            "WARNING",
            "Negative Dividend Payout"
        )


####################################################
# DQ-10
# EPS Validation
####################################################

def dq10_eps(df):

    required = ["eps", "net_profit"]

    if not all(col in df.columns for col in required):
        return

    invalid = df[
        (df["net_profit"] > 0) &
        (df["eps"] <= 0)
    ]

    for index in invalid.index:

        add_error(
            "DQ-10",
            "profitandloss",
            index,
            "WARNING",
            "EPS inconsistent with Net Profit"
        )


####################################################
# DQ-11
# Annual Report
####################################################

def dq11_document(df):

    if "Annual_Report" not in df.columns:
        return

    invalid = df[
        df["Annual_Report"].isna() |
        (df["Annual_Report"] == "")
    ]

    for index in invalid.index:

        add_error(
            "DQ-11",
            "documents",
            index,
            "WARNING",
            "Missing Annual Report"
        )


####################################################
# DQ-12
# Market Cap
####################################################

def dq12_market_cap(df):

    if "market_cap_crore" not in df.columns:
        return

    invalid = df[df["market_cap_crore"] <= 0]

    for index in invalid.index:

        add_error(
            "DQ-12",
            "market_cap",
            index,
            "WARNING",
            "Market Cap <= 0"
        )


####################################################
# DQ-13
# Debt to Equity
####################################################

def dq13_debt(df):

    if "debt_to_equity" not in df.columns:
        return

    invalid = df[df["debt_to_equity"] < 0]

    for index in invalid.index:

        add_error(
            "DQ-13",
            "financial_ratios",
            index,
            "WARNING",
            "Negative Debt to Equity"
        )


####################################################
# DQ-14
# Missing Mandatory Values
####################################################

def dq14_missing(df, dataset):

    mandatory = [
        "id"
    ]

    if "company_id" in df.columns:
        mandatory.append("company_id")

    for col in mandatory:

        if col not in df.columns:
            continue

        invalid = df[df[col].isna()]

        for index in invalid.index:

            add_error(
                "DQ-14",
                dataset,
                index,
                "CRITICAL",
                f"Missing {col}"
            )


####################################################
# DQ-15
# Empty Dataset
####################################################

def dq15_empty(df, dataset):

    if df.empty:

        add_error(
            "DQ-15",
            dataset,
            "-",
            "CRITICAL",
            "Dataset is Empty"
        )


####################################################
# DQ-16
# Date Validation
####################################################

def dq16_stock_date(df):

    if "date" not in df.columns:
        return

    invalid = pd.to_datetime(
        df["date"],
        errors="coerce"
    ).isna()

    for index in df[invalid].index:

        add_error(
            "DQ-16",
            "stock_prices",
            index,
            "WARNING",
            "Invalid Date"
        )


####################################################
# Save Report
####################################################

def save_validation_report():

    report = pd.DataFrame(validation_errors)

    report.to_csv(
        OUTPUT / "validation_failures.csv",
        index=False
    )

    print("\n" + "="*50)

    print("Validation Complete")

    print(f"Total Issues : {len(report)}")

    print("Saved : output/validation_failures.csv")

    print("="*50)