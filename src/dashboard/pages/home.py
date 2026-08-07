import streamlit as st
import plotly.express as px

from utils.db import get_dashboard_data


def show():

    st.title("🏠 Nifty 100 Dashboard")

    year = st.sidebar.selectbox(

        "Select Year",

        [2024, 2023, 2022, 2021, 2020, 2019]

    )

    df = get_dashboard_data(year)

    ####################################################

    avg_roe = round(df["return_on_equity_pct"].mean(), 2)

    median_pe = round(df["pe_ratio"].median(), 2)

    median_de = round(df["debt_to_equity"].median(), 2)

    total = len(df)

    revenue = round(df["revenue_cagr_5yr"].median(), 2)

    debt_free = len(

        df[df["debt_to_equity"] < 1]

    )

    ####################################################

    c1, c2, c3 = st.columns(3)

    c4, c5, c6 = st.columns(3)

    c1.metric("Average ROE", avg_roe)

    c2.metric("Median P/E", median_pe)

    c3.metric("Median D/E", median_de)

    c4.metric("Companies", total)

    c5.metric("Median Revenue CAGR", revenue)

    c6.metric("Debt-Free", debt_free)

    st.divider()

    ####################################################

    sector = (

        df.groupby("broad_sector")

        .size()

        .reset_index(name="Companies")

    )

    fig = px.pie(

        sector,

        names="broad_sector",

        values="Companies",

        hole=.45,

        title="Sector Breakdown"

    )

    st.plotly_chart(

        fig,

        use_container_width=True

    )

    st.divider()

    ####################################################

    st.subheader("Top 5 Quality Companies")

    top = (

        df.sort_values(

            "composite_quality_score",

            ascending=False

        )

        .head(5)

    )

    st.dataframe(

        top[

            [

                "company_name",

                "broad_sector",

                "return_on_equity_pct",

                "composite_quality_score"

            ]

        ],

        use_container_width=True

    )