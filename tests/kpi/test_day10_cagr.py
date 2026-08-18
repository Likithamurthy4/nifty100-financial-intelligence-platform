from src.analytics.cagr import eps_cagr, pat_cagr, revenue_cagr


def test_normal():

    _value, flag = revenue_cagr(100, 200, 5)

    assert flag == "NORMAL"


def test_zero_base():

    _, flag = revenue_cagr(0, 200, 5)

    assert flag == "ZERO_BASE"


def test_turnaround():

    _, flag = revenue_cagr(-100, 200, 5)

    assert flag == "TURNAROUND"


def test_decline():

    _, flag = revenue_cagr(200, -100, 5)

    assert flag == "DECLINE_TO_LOSS"


def test_both_negative():

    _, flag = revenue_cagr(-200, -100, 5)

    assert flag == "BOTH_NEGATIVE"


def test_insufficient():

    _, flag = revenue_cagr(100, 200, 2)

    assert flag == "INSUFFICIENT"


def test_pat():

    _, flag = pat_cagr(100, 200, 5)

    assert flag == "NORMAL"


def test_eps():

    _, flag = eps_cagr(2, 6, 5)

    assert flag == "NORMAL"


def test_return_none():

    value, _flag = revenue_cagr(0, 0, 5)

    assert value is None


def test_years():

    _, flag = revenue_cagr(100, 500, 10)

    assert flag == "NORMAL"
