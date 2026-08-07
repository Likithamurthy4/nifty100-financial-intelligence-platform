import streamlit as st
import plotly.express as px

from utils.db import (
    get_sectors,
    get_sector_data
)


def show():

    st.title("🏭 Sector Analysis")

    sectors = get_sectors()

    sector = st.selectbox(

        "Select Sector",

        sorted(

            sectors["broad_sector"].dropna().unique()

        )

    )

    df = get_sector_data(sector)

    if df.empty:

        st.warning("No data available.")

        return

    st.subheader("Sector Bubble Chart")

    fig = px.scatter(

        df,

        x="sales",

        y="return_on_equity_pct",

        size="market_cap_crore",

        color="sub_sector",

        hover_name="company_name",

        size_max=60

    )

    st.plotly_chart(

        fig,

        use_container_width=True

    )

    st.divider()

    st.subheader("Sector Median KPIs")

    median = df[

        [

            "return_on_equity_pct",

            "revenue_cagr_5yr",

            "composite_quality_score"

        ]

    ].median()

    fig = px.bar(

        x=median.index,

        y=median.values,

        labels={

            "x":"Metric",

            "y":"Median"

        }

    )

    st.plotly_chart(

        fig,

        use_container_width=True

    )