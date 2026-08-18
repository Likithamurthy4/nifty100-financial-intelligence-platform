import pandas as pd
import pytest

from src.analytics.cagr import calculate_cagr
from src.analytics.cashflow_kpis import CashFlowIntelligence
from src.analytics.ratios import (
    asset_turnover,
    debt_to_equity,
    high_leverage_flag,
    icr_warning,
    interest_coverage,
    net_debt,
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
)


def test_net_profit_margin():
    assert net_profit_margin(20, 100) == 20.0


def test_net_profit_margin_zero_sales():
    assert net_profit_margin(20, 0) is None


def test_operating_profit_margin():
    assert operating_profit_margin(30, 100) == 30.0


def test_roe_positive_equity():
    assert return_on_equity(20, 50, 50) == 20.0


def test_roe_negative_equity_returns_none():
    assert return_on_equity(20, -100, 20) is None


def test_debt_to_equity_debt_free():
    assert debt_to_equity(0, 100, 50) == 0


def test_debt_to_equity_normal():
    assert debt_to_equity(50, 100, 50) == 0.33


def test_debt_to_equity_negative_equity():
    assert debt_to_equity(50, -100, 20) is None


def test_high_leverage_flag_above_5():
    assert high_leverage_flag(6.0, "Industrials") is True


def test_high_leverage_financial_sector_excluded():
    assert high_leverage_flag(8.0, "Financials") is False


def test_interest_coverage_normal():
    assert interest_coverage(100, 20, 10) == 12.0


def test_interest_coverage_zero_interest_returns_none():
    assert interest_coverage(100, 20, 0) is None


def test_interest_coverage_warning():
    assert icr_warning(1.2) is True


def test_interest_coverage_no_warning():
    assert icr_warning(2.0) is False


def test_net_debt():
    assert net_debt(100, 30) == 70


def test_asset_turnover():
    assert asset_turnover(200, 100) == 2.0


def test_normal_cagr():
    value, flag = calculate_cagr(100, 200, 5)

    assert value == pytest.approx(14.87, abs=0.01)
    assert flag == "NORMAL"


def test_cagr_turnaround():
    value, flag = calculate_cagr(-100, 50, 5)

    assert value is None
    assert flag == "TURNAROUND"


def test_cagr_decline_to_loss():
    value, flag = calculate_cagr(100, -50, 5)

    assert value is None
    assert flag == "DECLINE_TO_LOSS"


def test_cfo_quality_high_quality():
    engine = CashFlowIntelligence()

    cashflow = pd.DataFrame(
        {
            "company_id": ["TEST"] * 5,
            "year": [2020, 2021, 2022, 2023, 2024],
            "operating_activity": [120, 130, 140, 150, 160],
        }
    )

    pl = pd.DataFrame(
        {
            "company_id": ["TEST"] * 5,
            "year": [2020, 2021, 2022, 2023, 2024],
            "net_profit": [100, 100, 100, 100, 100],
        }
    )

    score, label, _ = engine.cfo_quality(
        cashflow,
        pl,
    )

    assert score == pytest.approx(1.4)
    assert label == "High Quality"

    engine.conn.close()
