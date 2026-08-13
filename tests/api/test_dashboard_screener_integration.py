import requests
import pandas as pd

from src.dashboard.utils.db import get_screener_data


API_URL = "http://127.0.0.1:8000/api/v1/screener"


def test_dashboard_screener_matches_api():
    # Dashboard data
    dashboard_df = get_screener_data()

    # Apply the same default dashboard filters
    dashboard_filtered = dashboard_df[
        (dashboard_df["return_on_equity_pct"] >= 15)
        & (dashboard_df["debt_to_equity"] <= 1)
        & (dashboard_df["pe_ratio"] <= 40)
        & (dashboard_df["revenue_cagr_5yr"] >= 10)
    ]

    # API data with equivalent filters
    response = requests.get(
        API_URL,
        params={
            "min_roe": 15,
            "max_de": 1,
            "max_pe": 40,
            "min_rev_cagr_5yr": 10,
        },
        timeout=10,
    )

    assert response.status_code == 200

    api_data = response.json()

    # Compare company IDs
    dashboard_ids = set(
        dashboard_filtered["company_id"].astype(str)
    )

    api_ids = {
        str(company["id"])
        for company in api_data["companies"]
    }

    assert dashboard_ids == api_ids