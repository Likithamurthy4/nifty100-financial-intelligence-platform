import pytest

from src.etl.normaliser import normalize_year


@pytest.mark.parametrize(
    "value, expected",
    [
        (2024, 2024),
        (2023, 2023),
        ("2024", 2024),
        ("2023", 2023),
        ("2024-25", 2024),
        ("2023-24", 2023),
        ("2022-23", 2022),
        ("FY2024", 2024),
        ("FY 2024", 2024),
        ("FY2023", 2023),
        ("2024-2025", 2024),
        ("2023-2024", 2023),
        ("Apr 2024", 2024),
        ("March 2024", 2024),
        ("2024/25", 2024),
        ("2023/24", 2023),
        ("2024.0", 2024),
        (2024.0, 2024),
        (None, None),
        ("", None),
    ],
)
def test_normalize_year(value, expected):
    assert normalize_year(value) == expected
