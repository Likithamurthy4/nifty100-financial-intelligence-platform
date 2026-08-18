import pandas as pd

from src.etl.validator import (
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
    validation_errors,
)


def setup_function():
    """Clear global validation errors before every test."""
    validation_errors.clear()


def assert_rule(rule_id, severity):
    matches = [error for error in validation_errors if error["Rule"] == rule_id]

    assert len(matches) > 0
    assert all(error["Severity"] == severity for error in matches)


# ============================================================
# DQ-01 PRIMARY KEY
# ============================================================


def test_dq01_primary_key():
    df = pd.DataFrame(
        {
            "id": [1, 1],
            "company_id": ["ABB", "ABB"],
        }
    )

    dq01_primary_key(df, "companies")

    assert_rule("DQ-01", "CRITICAL")


# ============================================================
# DQ-02 COMPANY + YEAR
# ============================================================


def test_dq02_company_year():
    df = pd.DataFrame(
        {
            "company_id": ["ABB", "ABB"],
            "year": [2024, 2024],
        }
    )

    dq02_company_year(df, "financial_ratios")

    assert_rule("DQ-02", "CRITICAL")


# ============================================================
# DQ-03 FOREIGN KEY
# ============================================================


def test_dq03_foreign_key():
    df = pd.DataFrame(
        {
            "company_id": ["NOTREAL"],
        }
    )

    companies = pd.DataFrame(
        {
            "id": ["ABB", "TCS"],
        }
    )

    dq03_foreign_key(
        df,
        companies,
        "financial_ratios",
    )

    assert_rule("DQ-03", "CRITICAL")


# ============================================================
# DQ-04 BALANCE SHEET
# ============================================================


def test_dq04_balance_sheet():
    df = pd.DataFrame(
        {
            "total_assets": [100],
            "total_liabilities": [50],
        }
    )

    dq04_balance_sheet(df)

    assert_rule("DQ-04", "WARNING")


# ============================================================
# DQ-05 OPM
# ============================================================


def test_dq05_opm():
    df = pd.DataFrame(
        {
            "sales": [100],
            "operating_profit": [50],
            "opm_percentage": [10],
        }
    )

    dq05_opm(df)

    assert_rule("DQ-05", "WARNING")


# ============================================================
# DQ-06 SALES
# ============================================================


def test_dq06_sales():
    df = pd.DataFrame(
        {
            "sales": [-100],
        }
    )

    dq06_sales(df)

    assert_rule("DQ-06", "WARNING")


# ============================================================
# DQ-07 CASH FLOW
# ============================================================


def test_dq07_cashflow():
    df = pd.DataFrame(
        {
            "operating_activity": [100],
            "investing_activity": [50],
            "financing_activity": [25],
            "net_cash_flow": [999],
        }
    )

    dq07_cashflow(df)

    assert_rule("DQ-07", "WARNING")


# ============================================================
# DQ-08 TAX
# ============================================================


def test_dq08_tax():
    df = pd.DataFrame(
        {
            "tax_percentage": [150],
        }
    )

    dq08_tax(df)

    assert_rule("DQ-08", "WARNING")


# ============================================================
# DQ-09 DIVIDEND
# ============================================================


def test_dq09_dividend():
    df = pd.DataFrame(
        {
            "dividend_payout": [-10],
        }
    )

    dq09_dividend(df)

    assert_rule("DQ-09", "WARNING")


# ============================================================
# DQ-10 EPS
# ============================================================


def test_dq10_eps():
    df = pd.DataFrame(
        {
            "net_profit": [100],
            "eps": [0],
        }
    )

    dq10_eps(df)

    assert_rule("DQ-10", "WARNING")


# ============================================================
# DQ-11 DOCUMENT
# ============================================================


def test_dq11_document():
    df = pd.DataFrame(
        {
            "Annual_Report": [""],
        }
    )

    dq11_document(df)

    assert_rule("DQ-11", "WARNING")


# ============================================================
# DQ-12 MARKET CAP
# ============================================================


def test_dq12_market_cap():
    df = pd.DataFrame(
        {
            "market_cap_crore": [0],
        }
    )

    dq12_market_cap(df)

    assert_rule("DQ-12", "WARNING")


# ============================================================
# DQ-13 DEBT
# ============================================================


def test_dq13_debt():
    df = pd.DataFrame(
        {
            "debt_to_equity": [-1],
        }
    )

    dq13_debt(df)

    assert_rule("DQ-13", "WARNING")


# ============================================================
# DQ-14 MISSING MANDATORY VALUES
# ============================================================


def test_dq14_missing():
    df = pd.DataFrame(
        {
            "id": [None],
            "company_id": ["ABB"],
        }
    )

    dq14_missing(df, "companies")

    assert_rule("DQ-14", "CRITICAL")
