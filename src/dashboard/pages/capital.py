import plotly.express as px
import streamlit as st
from utils.db import get_capital_allocation


def show():

    st.title("🌳 Capital Allocation")

    df = get_capital_allocation()

    fig = px.treemap(
        df,
        path=["capital_pattern", "company_name"],
        values="composite_quality_score",
        color="composite_quality_score",
        color_continuous_scale="Viridis",
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    pattern = st.selectbox(
        "Capital Allocation Pattern", sorted(df["capital_pattern"].unique())
    )

    st.subheader("Companies")

    st.dataframe(df[df["capital_pattern"] == pattern], use_container_width=True)
