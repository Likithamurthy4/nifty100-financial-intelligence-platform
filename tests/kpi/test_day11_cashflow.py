from src.analytics.cashflow_kpis import *


def test_fcf():
    assert free_cash_flow(500, -200) == 300


def test_quality_high():
    assert cfo_quality_score(120, 100) == "High Quality"


def test_quality_moderate():
    assert cfo_quality_score(70, 100) == "Moderate"


def test_quality_risk():
    assert cfo_quality_score(20, 100) == "Accrual Risk"


def test_capex():
    value, label = capex_intensity(-50, 1000)

    assert label == "Moderate"


def test_fcf_conversion():
    assert fcf_conversion(300, 600) == 50


def test_classifier():
    assert classify_capital_allocation(
        100,
        -50,
        -20
    ) == "Reinvestor"


def test_classifier_quality():
    assert classify_capital_allocation(
        100,
        -50,
        -20,
        "High Quality"
    ) == "Shareholder Returns"