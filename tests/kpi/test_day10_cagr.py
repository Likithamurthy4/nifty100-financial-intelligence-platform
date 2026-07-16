from src.analytics.cagr import (
    revenue_cagr,
    pat_cagr,
    eps_cagr
)


def test_normal():

    value, flag = revenue_cagr(
        100,
        200,
        5
    )

    assert flag == "NORMAL"


def test_zero_base():

    value, flag = revenue_cagr(
        0,
        200,
        5
    )

    assert flag == "ZERO_BASE"


def test_turnaround():

    value, flag = revenue_cagr(
        -100,
        200,
        5
    )

    assert flag == "TURNAROUND"


def test_decline():

    value, flag = revenue_cagr(
        200,
        -100,
        5
    )

    assert flag == "DECLINE_TO_LOSS"


def test_both_negative():

    value, flag = revenue_cagr(
        -200,
        -100,
        5
    )

    assert flag == "BOTH_NEGATIVE"


def test_insufficient():

    value, flag = revenue_cagr(
        100,
        200,
        2
    )

    assert flag == "INSUFFICIENT"


def test_pat():

    value, flag = pat_cagr(
        100,
        200,
        5
    )

    assert flag == "NORMAL"


def test_eps():

    value, flag = eps_cagr(
        2,
        6,
        5
    )

    assert flag == "NORMAL"


def test_return_none():

    value, flag = revenue_cagr(
        0,
        0,
        5
    )

    assert value is None


def test_years():

    value, flag = revenue_cagr(
        100,
        500,
        10
    )

    assert flag == "NORMAL"