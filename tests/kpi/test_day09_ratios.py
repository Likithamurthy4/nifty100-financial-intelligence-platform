import pytest

from src.analytics.ratios import (
    debt_to_equity,
    high_leverage_flag,
    interest_coverage,
    icr_label,
    icr_warning,
    net_debt,
    asset_turnover
)


def test_de_ratio_normal():
    assert debt_to_equity(200, 100, 100) == 1.0


def test_de_ratio_debt_free():
    assert debt_to_equity(0, 100, 100) == 0


def test_de_ratio_negative_equity():
    assert debt_to_equity(100, -100, 50) is None


def test_high_leverage():
    assert high_leverage_flag(6, "Technology") is True


def test_financial_sector():
    assert high_leverage_flag(8, "Financials") is False


def test_interest_zero():
    assert interest_coverage(100, 20, 0) is None


def test_icr_label():
    assert icr_label(None) == "Debt Free"


def test_icr_warning():
    assert icr_warning(1.2) is True


def test_net_debt():
    assert net_debt(500, 120) == 380


def test_asset_turnover():
    assert asset_turnover(1000, 500) == 2.0