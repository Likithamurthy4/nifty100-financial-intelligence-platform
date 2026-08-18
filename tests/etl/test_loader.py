import pytest

from etl.loader import load_all_datasets


@pytest.fixture(scope="module")
def datasets():
    return load_all_datasets()


def test_companies(datasets):
    df = datasets["companies"]

    assert len(df) == 92

    assert list(df.columns) == [
        "id",
        "company_logo",
        "company_name",
        "chart_link",
        "about_company",
        "website",
        "nse_profile",
        "bse_profile",
        "face_value",
        "book_value",
        "roce_percentage",
        "roe_percentage",
    ]


def test_profitandloss(datasets):
    df = datasets["profitandloss"]

    assert len(df) == 1276

    assert list(df.columns) == [
        "id",
        "company_id",
        "year",
        "sales",
        "expenses",
        "operating_profit",
        "opm_percentage",
        "other_income",
        "interest",
        "depreciation",
        "profit_before_tax",
        "tax_percentage",
        "net_profit",
        "eps",
        "dividend_payout",
    ]


def test_balancesheet(datasets):
    df = datasets["balancesheet"]

    assert len(df) == 1312

    assert list(df.columns) == [
        "id",
        "company_id",
        "year",
        "equity_capital",
        "reserves",
        "borrowings",
        "other_liabilities",
        "total_liabilities",
        "fixed_assets",
        "cwip",
        "investments",
        "other_asset",
        "total_assets",
    ]


def test_cashflow(datasets):
    df = datasets["cashflow"]

    assert len(df) == 1187

    assert list(df.columns) == [
        "id",
        "company_id",
        "year",
        "operating_activity",
        "investing_activity",
        "financing_activity",
        "net_cash_flow",
    ]


def test_analysis(datasets):
    df = datasets["analysis"]

    assert len(df) == 20

    assert list(df.columns) == [
        "id",
        "company_id",
        "compounded_sales_growth",
        "compounded_profit_growth",
        "stock_price_cagr",
        "roe",
    ]


def test_documents(datasets):
    df = datasets["documents"]

    assert len(df) == 1585

    assert list(df.columns) == [
        "id",
        "company_id",
        "year",
        "annual_report",
    ]


def test_sectors(datasets):
    df = datasets["sectors"]

    assert len(df) == 92

    assert list(df.columns) == [
        "id",
        "company_id",
        "broad_sector",
        "sub_sector",
        "index_weight_pct",
        "market_cap_category",
    ]


def test_stock_prices(datasets):
    df = datasets["stock_prices"]

    assert len(df) == 5520

    assert list(df.columns) == [
        "id",
        "company_id",
        "date",
        "open_price",
        "high_price",
        "low_price",
        "close_price",
        "volume",
        "adjusted_close",
    ]


def test_market_cap(datasets):
    df = datasets["market_cap"]

    assert len(df) == 552

    assert list(df.columns) == [
        "id",
        "company_id",
        "year",
        "market_cap_crore",
        "enterprise_value_crore",
        "pe_ratio",
        "pb_ratio",
        "ev_ebitda",
        "dividend_yield_pct",
    ]


def test_financial_ratios(datasets):
    df = datasets["financial_ratios"]

    assert len(df) == 1184

    assert list(df.columns) == [
        "id",
        "company_id",
        "year",
        "net_profit_margin_pct",
        "operating_profit_margin_pct",
        "return_on_equity_pct",
        "debt_to_equity",
        "interest_coverage",
        "asset_turnover",
        "free_cash_flow_cr",
        "capex_cr",
        "earnings_per_share",
        "book_value_per_share",
        "dividend_payout_ratio_pct",
        "total_debt_cr",
        "cash_from_operations_cr",
    ]
