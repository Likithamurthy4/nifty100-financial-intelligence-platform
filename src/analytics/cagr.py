"""
Sprint 2 - Day 10

CAGR Engine
"""

from math import pow


def calculate_cagr(start, end, years):
    """
    CAGR Formula

    ((End / Start)^(1/Years) - 1) * 100
    """

    if years <= 0:
        return None, "INVALID_PERIOD"

    if start == 0:
        return None, "ZERO_BASE"

    if years < 3:
        return None, "INSUFFICIENT"

    # Edge Case 1
    if start > 0 and end > 0:

        cagr = (
            pow(end / start, 1 / years) - 1
        ) * 100

        return round(cagr, 2), "NORMAL"

    # Edge Case 2
    if start > 0 and end < 0:
        return None, "DECLINE_TO_LOSS"

    # Edge Case 3
    if start < 0 and end > 0:
        return None, "TURNAROUND"

    # Edge Case 4
    if start < 0 and end < 0:
        return None, "BOTH_NEGATIVE"

    return None, "UNKNOWN"


def revenue_cagr(start, end, years):
    return calculate_cagr(start, end, years)


def pat_cagr(start, end, years):
    return calculate_cagr(start, end, years)


def eps_cagr(start, end, years):
    return calculate_cagr(start, end, years)