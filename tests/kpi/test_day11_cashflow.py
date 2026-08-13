import pandas as pd
import pytest

from src.analytics.cashflow_kpis import CashFlowIntelligence


@pytest.fixture
def engine():
    obj = CashFlowIntelligence()
    yield obj
    obj.close()


def make_cashflow(
    operating_activity,
    investing_activity,
    financing_activity,
    years=None,
):
    if years is None:
        years = [2024]

    return pd.DataFrame(
        {
            "company_id": ["TEST"] * len(years),
            "year": years,
            "operating_activity": operating_activity,
            "investing_activity": investing_activity,
            "financing_activity": financing_activity,
            "net_cash_flow": [
                o + i + f
                for o, i, f in zip(
                    operating_activity,
                    investing_activity,
                    financing_activity,
                )
            ],
        }
    )


def make_pl(net_profit, sales=1000, years=None):
    if years is None:
        years = [2024]

    return pd.DataFrame(
        {
            "company_id": ["TEST"] * len(years),
            "year": years,
            "sales": [sales] * len(years),
            "net_profit": net_profit,
        }
    )


# ============================================================
# FCF
# ============================================================

def test_fcf():
    cashflow = make_cashflow(
        [500],
        [-200],
        [0],
    )

    fcf = (
        cashflow.iloc[-1]["operating_activity"]
        + cashflow.iloc[-1]["investing_activity"]
    )

    assert fcf == 300


# ============================================================
# CFO QUALITY
# ============================================================

def test_quality_high(engine):
    cashflow = make_cashflow(
        [120],
        [-20],
        [0],
    )

    pl = make_pl([100])

    score, label, _ = engine.cfo_quality(
        cashflow,
        pl,
    )

    assert score == pytest.approx(1.2)
    assert label == "High Quality"


def test_quality_moderate(engine):
    cashflow = make_cashflow(
        [70],
        [-20],
        [0],
    )

    pl = make_pl([100])

    score, label, _ = engine.cfo_quality(
        cashflow,
        pl,
    )

    assert score == pytest.approx(0.7)
    assert label == "Moderate"


def test_quality_risk(engine):
    cashflow = make_cashflow(
        [20],
        [-20],
        [0],
    )

    pl = make_pl([100])

    score, label, _ = engine.cfo_quality(
        cashflow,
        pl,
    )

    assert score == pytest.approx(0.2)
    assert label == "Accrual Risk"


# ============================================================
# CAPEX INTENSITY
# ============================================================

def test_capex(engine):
    cashflow = make_cashflow(
        [500],
        [-50],
        [0],
    )

    pl = make_pl(
        [100],
        sales=1000,
    )

    value, label = engine.capex_intensity(
        cashflow,
        pl,
    )

    assert value == pytest.approx(5.0)
    assert label == "Moderate"


# ============================================================
# FCF CONVERSION
# ============================================================

def test_fcf_conversion(engine):
    cashflow = make_cashflow(
        [500],
        [-200],
        [0],
    )

    pl = make_pl([600])

    value = engine.fcf_conversion(
        cashflow,
        pl,
    )

    assert value == pytest.approx(50.0)


# ============================================================
# CAPITAL ALLOCATION
# ============================================================

def test_classifier(engine):
    cashflow = make_cashflow(
        [100],
        [-50],
        [20],
    )

    assert engine.capital_allocation(
        cashflow
    ) == "Reinvestor"


def test_classifier_quality(engine):
    cashflow = make_cashflow(
        [100],
        [-50],
        [20],
    )

    # Current implementation's capital_allocation()
    # does not accept a CFO quality argument.
    assert engine.capital_allocation(
        cashflow
    ) == "Reinvestor"