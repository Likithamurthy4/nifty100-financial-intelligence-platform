import pytest

from src.etl.normaliser import normalize_year, normalize_ticker


# ----------------------------
# normalize_year() Tests
# ----------------------------

@pytest.mark.parametrize(
    "input_year, expected",
    [
        ("Mar-23", 2023),
        ("Mar-24", 2024),
        ("Mar-22", 2022),
        ("FY2024", 2024),
        ("FY2023", 2023),
        ("2022", 2022),
        ("2021", 2021),
        ("2020", 2020),
        ("2019", 2019),
        ("2018", 2018),
        ("17", 2017),
        ("16", 2016),
        ("15", 2015),
        ("14", 2014),
        ("13", 2013),
        ("12", 2012),
        ("11", 2011),
        ("10", 2010),
        (" Mar-23 ", 2023),
        (None, None),
    ]
)
def test_normalize_year(input_year, expected):
    assert normalize_year(input_year) == expected


# ----------------------------
# normalize_ticker() Tests
# ----------------------------

@pytest.mark.parametrize(
    "input_ticker, expected",
    [
        ("tcs", "TCS"),
        ("TCS", "TCS"),
        (" tcs ", "TCS"),
        ("infy", "INFY"),
        ("INFY", "INFY"),
        (" reliance ", "RELIANCE"),
        ("HDFCBANK", "HDFCBANK"),
        ("hdfcbank", "HDFCBANK"),
        (" adaniports ", "ADANIPORTS"),
        ("SBIN", "SBIN"),
        ("sbin", "SBIN"),
        ("lt", "LT"),
        (" LT ", "LT"),
        ("asianpaints", "ASIANPAINTS"),
        (None, None),
    ]
)
def test_normalize_ticker(input_ticker, expected):
    assert normalize_ticker(input_ticker) == expected