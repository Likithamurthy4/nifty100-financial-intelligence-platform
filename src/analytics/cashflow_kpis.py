"""
Sprint 2 - Day 11

Cash Flow KPIs
"""

import pandas as pd
from pathlib import Path

OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)


def free_cash_flow(operating_activity, investing_activity):
    """
    FCF = CFO + CFI
    """
    return operating_activity + investing_activity


def cfo_quality_score(cfo, pat):
    """
    CFO/PAT Quality
    """

    if pat == 0:
        return None

    ratio = cfo / pat

    if ratio > 1:
        return "High Quality"

    if ratio >= 0.5:
        return "Moderate"

    return "Accrual Risk"


def capex_intensity(investing_activity, sales):
    """
    CapEx Intensity
    """

    if sales == 0:
        return None

    value = abs(investing_activity) / sales * 100

    if value < 3:
        label = "Asset Light"

    elif value <= 8:
        label = "Moderate"

    else:
        label = "Capital Intensive"

    return round(value, 2), label


def fcf_conversion(fcf, operating_profit):
    """
    FCF Conversion
    """

    if operating_profit == 0:
        return None

    return round(
        fcf / operating_profit * 100,
        2
    )


def classify_capital_allocation(cfo, cfi, cff, quality=None):

    signs = (

        "+" if cfo >= 0 else "-",

        "+" if cfi >= 0 else "-",

        "+" if cff >= 0 else "-"

    )

    mapping = {

        ("+", "-", "-"): "Reinvestor",

        ("+", "+", "-"): "Liquidating Assets",

        ("-", "+", "+"): "Distress Signal",

        ("-", "-", "+"): "Growth Funded by Debt",

        ("+", "+", "+"): "Cash Accumulator",

        ("-", "-", "-"): "Pre-Revenue",

        ("+", "-", "+"): "Mixed"

    }

    if signs == ("+", "-", "-") and quality == "High Quality":
        return "Shareholder Returns"

    return mapping.get(signs, "Unknown")


def save_capital_allocation(records):

    df = pd.DataFrame(records)

    df.to_csv(

        OUTPUT / "capital_allocation.csv",

        index=False

    )

    print(

        "capital_allocation.csv generated"

    )