"""
Day 09 - Leverage & Efficiency Ratios
"""


def debt_to_equity(borrowings, equity_capital, reserves):
    """
    Debt to Equity = Borrowings / (Equity + Reserves)

    Rule:
    - If borrowings = 0 → return 0
    - If equity + reserves <= 0 → return None
    """

    if borrowings == 0:
        return 0

    denominator = equity_capital + reserves

    if denominator <= 0:
        return None

    return round(borrowings / denominator, 2)


def high_leverage_flag(de_ratio, broad_sector):
    """
    Flag companies with high leverage.

    Financial sector is excluded.
    """

    if de_ratio is None:
        return False

    if broad_sector == "Financials":
        return False

    return de_ratio > 5


def interest_coverage(operating_profit, other_income, interest):
    """
    ICR = (Operating Profit + Other Income) / Interest

    Return None if interest = 0
    """

    if interest == 0:
        return None

    return round(
        (operating_profit + other_income) / interest,
        2
    )


def icr_label(icr):
    """
    Label debt-free companies.
    """

    if icr is None:
        return "Debt Free"

    return ""


def icr_warning(icr):
    """
    Risk if ICR < 1.5
    """

    if icr is None:
        return False

    return icr < 1.5


def net_debt(borrowings, investments):
    """
    Net Debt = Borrowings - Investments
    """

    return round(borrowings - investments, 2)


def asset_turnover(sales, total_assets):
    """
    Asset Turnover = Sales / Total Assets

    Return None if assets = 0
    """

    if total_assets == 0:
        return None

    return round(sales / total_assets, 2)