import streamlit as st
from utils.db import get_reports, search_company


def show():

    st.title("📄 Annual Reports")

    keyword = st.text_input("Search Company")

    if keyword == "":
        st.info("Search a company.")
        return

    companies = search_company(keyword)

    if companies.empty:

        st.warning("Company not found.")

        return

    company = st.selectbox("Select Company", companies["company_name"])

    company_id = companies[companies["company_name"] == company]["id"].iloc[0]

    reports = get_reports(company_id)

    if reports.empty:

        st.error("No reports available.")

        return

    st.subheader(company)

    for _, row in reports.iterrows():

        c1, c2 = st.columns([1, 4])

        c1.write(row["year"])

        if row["annual_report"]:

            c2.link_button("📥 Open Report", row["annual_report"])

        else:

            c2.error("Report Unavailable")
