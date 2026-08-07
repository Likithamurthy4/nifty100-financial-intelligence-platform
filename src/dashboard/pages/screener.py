import streamlit as st
import pandas as pd

from utils.db import get_screener_data


def show():

    st.title("🔍 Stock Screener")
    st.subheader("Quick Presets")

    c1, c2, c3 = st.columns(3)

    quality = c1.button("🏆 Quality")
    value = c2.button("💰 Value")
    growth = c3.button("📈 Growth")

    c4, c5, c6 = st.columns(3)

    dividend = c4.button("💵 Dividend")
    debtfree = c5.button("🛡 Debt Free")
    turnaround = c6.button("🔄 Turnaround")
    df = get_screener_data()

    st.sidebar.header("Filters")
    
    roe = st.sidebar.slider(
        "Minimum ROE",
        0,
        50,
        15
    )

    debt = st.sidebar.slider(
        "Maximum Debt/Equity",
        0.0,
        5.0,
        1.0
    )

    pe = st.sidebar.slider(
        "Maximum P/E",
        0,
        100,
        40
    )

    revenue = st.sidebar.slider(
        "Minimum Revenue CAGR",
        -20,
        50,
        10
    )

    df = df[
        (df["return_on_equity_pct"] >= roe) &
        (df["debt_to_equity"] <= debt) &
        (df["pe_ratio"] <= pe) &
        (df["revenue_cagr_5yr"] >= revenue)
    ]
    if quality:

        df = get_screener_data()

        df = df[
            (df["return_on_equity_pct"] >= 15) &
            (df["debt_to_equity"] <= 1)
        ]

    elif value:

        df = get_screener_data()

        df = df[
            (df["pe_ratio"] <= 30)
        ]

    elif growth:

        df = get_screener_data()

        df = df[
            (df["revenue_cagr_5yr"] >= 15) &
            (df["pat_cagr_5yr"] >= 15)
        ]

    elif dividend:

        df = get_screener_data()

        df = df[
            df["dividend_yield_pct"] >= 2
        ]

    elif debtfree:

        df = get_screener_data()

        df = df[
            df["debt_to_equity"] <= 0.2
        ]

    elif turnaround:

        df = get_screener_data()

        df = df[
            (df["free_cash_flow_cr"] > 0) &
            (df["net_profit_margin_pct"] > 0)
        ]
    st.write(df[["company_name", "pe_ratio", "pb_ratio"]].head(20))
    st.success(f"{len(df)} companies match your filters")

    st.dataframe(
        df,
        use_container_width=True
    )
    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "📥 Download CSV",
        csv,
        file_name="screener_results.csv",
        mime="text/csv"
    )