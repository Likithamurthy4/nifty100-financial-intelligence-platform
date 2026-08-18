import plotly.graph_objects as go
import streamlit as st
from utils.db import (
    get_peer_companies,
    get_peer_groups,
    get_peer_metrics,
    get_peer_table,
)


def show():

    st.title("👥 Peer Comparison")

    groups = get_peer_groups()

    peer_group = st.selectbox("Peer Group", groups["peer_group_name"])

    companies = get_peer_companies(peer_group)

    company = st.selectbox("Company", companies["company_name"])

    st.success(f"Peer Group : {peer_group}")

    st.info(f"Selected Company : {company}")
    df = get_peer_metrics(peer_group)

    company_df = df[df["company_name"] == company]

    if not company_df.empty:

        company_df = company_df.iloc[0]

        metrics = [
            "return_on_equity_pct",
            "roce_percentage",
            "net_profit_margin_pct",
            "debt_to_equity",
            "free_cash_flow_cr",
            "revenue_cagr_5yr",
            "pat_cagr_5yr",
            "composite_quality_score",
        ]

        peer_avg = df[metrics].mean()

        fig = go.Figure()

        fig.add_trace(
            go.Scatterpolar(
                r=company_df[metrics].values,
                theta=[
                    "ROE",
                    "ROCE",
                    "NPM",
                    "D/E",
                    "FCF",
                    "Revenue CAGR",
                    "PAT CAGR",
                    "Quality Score",
                ],
                fill="toself",
                name=company,
            )
        )

        fig.add_trace(
            go.Scatterpolar(
                r=peer_avg.values,
                theta=[
                    "ROE",
                    "ROCE",
                    "NPM",
                    "D/E",
                    "FCF",
                    "Revenue CAGR",
                    "PAT CAGR",
                    "Quality Score",
                ],
                name="Peer Average",
            )
        )

        fig.update_layout(
            title="Company vs Peer Group",
            polar={
                "radialaxis": {
                    "visible": True,
                }
            },
        )

        st.plotly_chart(fig, use_container_width=True)
    st.divider()

    st.subheader("Peer Comparison Table")

    table = get_peer_table(peer_group)

    def highlight_company(row):

        if row["company_name"] == company:
            return ["background-color: gold"] * len(row)

        return [""] * len(row)

    styled = table.style.apply(highlight_company, axis=1)

    st.dataframe(styled, use_container_width=True)
    st.divider()

    st.subheader("Peer Group Summary")

    summary = table[
        [
            "return_on_equity_pct",
            "roce_percentage",
            "net_profit_margin_pct",
            "debt_to_equity",
            "free_cash_flow_cr",
            "revenue_cagr_5yr",
            "pat_cagr_5yr",
            "composite_quality_score",
        ]
    ].median()

    st.dataframe(summary.to_frame("Median"), use_container_width=True)
