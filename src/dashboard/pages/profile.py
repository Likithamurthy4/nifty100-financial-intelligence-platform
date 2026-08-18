import pandas as pd
import plotly.express as px
import streamlit as st
from utils.db import get_company_profile, get_pl, get_ratios, search_company


def safe_value(value, decimals=2):

    if pd.isna(value):
        return "N/A"

    if isinstance(value, (int, float)):
        return round(value, decimals)

    return value


def show():

    st.title("🏢 Company Profile")

    keyword = st.text_input("Search Company / Ticker")

    if keyword == "":
        st.info("Start typing a company name.")
        return

    companies = search_company(keyword)

    if companies.empty:

        st.warning("Ticker not found — please try another.")

        return

    choice = st.selectbox("Select Company", companies["company_name"])

    company = companies[companies["company_name"] == choice].iloc[0]

    profile = get_company_profile(company["id"])

    ratios = get_ratios(company["id"])
    pl = get_pl(company["id"])

    if profile.empty:

        st.error("Company not found.")

        return

    profile = profile.iloc[0]
    if profile["company_logo"]:
        st.image(profile["company_logo"], width=150)

    st.divider()

    st.subheader(profile["company_name"])

    st.write(f"**Ticker :** {profile['id']}")

    st.write(f"**Sector :** {profile['broad_sector']}")

    st.write(f"**Sub Sector :** {profile['sub_sector']}")

    st.write(profile["about_company"])
    col1, col2, col3 = st.columns(3)

    col1.metric("ROCE %", safe_value(profile["roce_percentage"]))

    col2.metric("ROE %", safe_value(profile["roe_percentage"]))

    col3.metric("Book Value", safe_value(profile["book_value"]))

    st.metric("Face Value", safe_value(profile["face_value"]))

    st.write("### Website")

    st.write(profile["website"])
    st.divider()

    st.subheader("Revenue & Net Profit (10 Years)")

    if not ratios.empty:

        fig = px.bar(
            pl,
            x="year",
            y=["sales", "net_profit"],
            barmode="group",
            title="Revenue vs Net Profit",
        )

        st.plotly_chart(fig, use_container_width=True)
        st.divider()

    st.subheader("ROE & ROCE Trend")

    if not ratios.empty:

        fig = px.line(ratios, x="year", y=["return_on_equity_pct"], markers=True)

        fig.add_scatter(
            x=ratios["year"], y=[profile["roce_percentage"]] * len(ratios), name="ROCE"
        )

        st.plotly_chart(fig, use_container_width=True)
        st.divider()

    st.subheader("Pros")

    if profile["roe_percentage"] > 15:

        st.success("High ROE")

    if profile["roce_percentage"] > 15:

        st.success("High ROCE")

    if profile["book_value"] > 0:

        st.success("Positive Book Value")

    st.subheader("Cons")

    if profile["roe_percentage"] < 10:

        st.error("Low ROE")

    if profile["roce_percentage"] < 10:

        st.error("Low ROCE")
