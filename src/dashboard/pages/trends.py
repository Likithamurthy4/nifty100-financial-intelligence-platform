import plotly.express as px
import streamlit as st
from utils.db import get_trend_data, run_query, search_company


def show():

    st.title("📈 Trend Analysis")

    keyword = st.text_input("Search Company")

    if keyword == "":
        st.info("Search a company.")
        return

    companies = search_company(keyword)

    if companies.empty:

        st.warning("Company not found.")

        return

    company = st.selectbox("Company", companies["company_name"])

    company_id = companies[companies["company_name"] == company]["id"].iloc[0]

    df = get_trend_data(company_id)

    metrics = st.multiselect(
        "Choose up to 3 Metrics",
        [
            "return_on_equity_pct",
            "net_profit_margin_pct",
            "debt_to_equity",
            "interest_coverage",
            "asset_turnover",
            "free_cash_flow_cr",
            "revenue_cagr_5yr",
            "pat_cagr_5yr",
            "eps_cagr_5yr",
            "composite_quality_score",
        ],
        default=["return_on_equity_pct"],
    )

    if len(metrics) > 3:

        st.error("Maximum 3 metrics.")

        return

    fig = px.line(df, x="year", y=metrics, markers=True)

    st.plotly_chart(fig, use_container_width=True)
    st.divider()

    st.subheader("Year-over-Year Change (%)")

    yoy = df.copy()

    for metric in metrics:

        yoy[metric] = yoy[metric].pct_change() * 100

    st.dataframe(yoy[["year"] + metrics], use_container_width=True)


@st.cache_data(ttl=600)
def get_sector_data(sector):

    return run_query(f"""
        SELECT

            c.company_name,

            s.broad_sector,
            s.sub_sector,

            fr.return_on_equity_pct,
            fr.revenue_cagr_5yr,
            fr.composite_quality_score,

            p.sales,

            m.market_cap_crore

        FROM financial_ratios fr

        JOIN companies c
            ON fr.company_id = c.id

        JOIN sectors s
            ON fr.company_id = s.company_id

        LEFT JOIN profitandloss p
            ON fr.company_id = p.company_id
            AND fr.year = p.year

        LEFT JOIN market_cap m
            ON fr.company_id = m.company_id
            AND fr.year = m.year

        WHERE s.broad_sector='{sector}'

        AND fr.year=(

            SELECT MAX(year)

            FROM financial_ratios f2

            WHERE f2.company_id=fr.company_id

        )

    """)
