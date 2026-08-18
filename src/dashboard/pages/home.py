import pandas as pd
import plotly.express as px
import streamlit as st
from utils.db import get_screener_data


def apply_home_style():
    """Apply styling used by the dashboard home page."""
    st.markdown(
        """
        <style>
        .home-subtitle {
            color: #788496;
            font-size: 10px;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin-top: 4px;
            margin-bottom: 22px;
        }

        .section-description {
            color: #788496;
            font-size: 10px;
            margin-top: -10px;
            margin-bottom: 10px;
        }

        .market-insight {
            padding: 18px 22px;
            border-radius: 14px;
            background: linear-gradient(
                135deg,
                rgba(27,33,43,0.96),
                rgba(16,20,27,0.96)
            );
            border: 1px solid rgba(255,255,255,0.055);
            color: #8f9aaa;
            font-size: 10px;
            margin-top: 20px;
        }

        .market-highlight {
            color: #43d39a;
            font-weight: 700;
        }

        [data-testid="stMetric"] {
            background: linear-gradient(
                145deg,
                rgba(27,33,43,0.97),
                rgba(15,19,26,0.97)
            );
            border: 1px solid rgba(255,255,255,0.055);
            border-radius: 14px;
            padding: 15px 17px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.20);
        }

        [data-testid="stMetricLabel"] {
            color: #788496 !important;
            font-size: 9px !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        [data-testid="stMetricValue"] {
            color: #eef2f7 !important;
            font-size: 24px !important;
            font-weight: 750 !important;
        }

        [data-testid="stDataFrame"] {
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.05);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def find_column(df, possible_names):
    """Return the first matching column name."""
    for name in possible_names:
        if name in df.columns:
            return name

    return None


def numeric_series(df, column):
    """Return a numeric pandas Series for a column."""
    if column is None:
        return pd.Series(dtype=float)

    return pd.to_numeric(
        df[column],
        errors="coerce",
    )


def format_value(value, decimals=2):
    """Format a numeric value for dashboard display."""
    if pd.isna(value):
        return "N/A"

    return f"{value:,.{decimals}f}"


def show():
    """Display the NIFTY 100 dashboard home screen."""

    apply_home_style()

    # ======================================================
    # LOAD DATA
    # ======================================================

    try:
        df = get_screener_data()

    except Exception as exc:  # noqa: BLE001
        st.error(f"Unable to load dashboard data: {exc}")
        return

    if df is None or df.empty:
        st.warning("No financial data is available.")
        return

    df = df.copy()
    df = df.dropna(how="all")

    # ======================================================
    # FIND COLUMNS
    # ======================================================

    company_column = find_column(
        df,
        [
            "company_name",
            "company",
            "name",
        ],
    )

    ticker_column = find_column(
        df,
        [
            "company_id",
            "ticker",
            "symbol",
        ],
    )

    roe_column = find_column(
        df,
        [
            "return_on_equity_pct",
            "roe_percentage",
            "roe_pct",
            "roe",
        ],
    )

    pe_column = find_column(
        df,
        [
            "pe_ratio",
            "p_e_ratio",
            "pe",
        ],
    )

    debt_column = find_column(
        df,
        [
            "debt_to_equity",
            "de_ratio",
            "debt_equity",
        ],
    )

    revenue_cagr_column = find_column(
        df,
        [
            "revenue_cagr_5yr",
            "revenue_cagr",
            "revenue_growth",
        ],
    )

    quality_column = find_column(
        df,
        [
            "composite_quality_score",
            "quality_score",
        ],
    )

    sector_column = find_column(
        df,
        [
            "broad_sector",
            "sector",
        ],
    )

    # ======================================================
    # NUMERIC DATA
    # ======================================================

    roe = numeric_series(
        df,
        roe_column,
    )

    pe = numeric_series(
        df,
        pe_column,
    )

    debt = numeric_series(
        df,
        debt_column,
    )

    revenue_cagr = numeric_series(
        df,
        revenue_cagr_column,
    )

    _quality = numeric_series(
        df,
        quality_column,
    )

    # ======================================================
    # PAGE TITLE
    # ======================================================

    st.title("🏠 Nifty 100 Dashboard")

    st.markdown(
        """
        <div class="home-subtitle">
            Market overview • fundamentals • valuation • growth
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ======================================================
    # KPI CALCULATIONS
    # ======================================================

    average_roe = roe.mean() if not roe.dropna().empty else None

    median_pe = pe.median() if not pe.dropna().empty else None

    median_debt = debt.median() if not debt.dropna().empty else None

    median_revenue_cagr = (
        revenue_cagr.median() if not revenue_cagr.dropna().empty else None
    )

    if ticker_column:
        companies_count = df[ticker_column].nunique()
    else:
        companies_count = len(df)

    if not debt.dropna().empty:
        debt_free_count = int((debt <= 0.2).sum())
    else:
        debt_free_count = 0

    # ======================================================
    # KPI CARDS
    # ======================================================

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Average ROE",
        format_value(average_roe),
    )

    col2.metric(
        "Median P/E",
        format_value(median_pe),
    )

    col3.metric(
        "Median D/E",
        format_value(median_debt),
    )

    col4, col5, col6 = st.columns(3)

    col4.metric(
        "Companies",
        f"{companies_count:,}",
    )

    col5.metric(
        "Median Revenue CAGR",
        format_value(median_revenue_cagr),
    )

    col6.metric(
        "Debt-Free",
        f"{debt_free_count:,}",
    )

    # ======================================================
    # TWO-COLUMN SECTION
    # ======================================================

    left, right = st.columns([1, 1])

    # ======================================================
    # SECTOR DISTRIBUTION
    # ======================================================

    with left:

        st.subheader("Sector Distribution")

        st.markdown(
            '<div class="section-description">' "Companies by broad sector" "</div>",
            unsafe_allow_html=True,
        )

        if sector_column:

            sector = (
                df.groupby(sector_column)
                .size()
                .reset_index(name="Companies")
                .sort_values(
                    "Companies",
                    ascending=False,
                )
            )

            if not sector.empty:

                fig = px.pie(
                    sector,
                    names=sector_column,
                    values="Companies",
                    hole=0.62,
                )

                fig.update_traces(
                    textposition="inside",
                    textinfo="percent",
                    hovertemplate=(
                        "<b>%{label}</b>"
                        "<br>Companies: %{value}"
                        "<br>Share: %{percent}"
                        "<extra></extra>"
                    ),
                )

                fig.update_layout(
                    height=360,
                    margin={
                        "l": 10,
                        "r": 10,
                        "t": 20,
                        "b": 10,
                    },
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font={
                        "color": "#aab4c2",
                        "size": 10,
                    },
                    legend={
                        "bgcolor": "rgba(0,0,0,0)",
                        "font": {
                            "color": "#9aa5b5",
                            "size": 9,
                        },
                    },
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )

    # ======================================================
    # TOP 5 QUALITY
    # ======================================================

    with right:

        st.subheader("Top 5 Quality Companies")

        st.markdown(
            '<div class="section-description">'
            "Strong fundamentals and financial quality"
            "</div>",
            unsafe_allow_html=True,
        )

        if quality_column and company_column:

            quality_df = df.copy()

            quality_df["_quality"] = numeric_series(
                quality_df,
                quality_column,
            )

            quality_df = (
                quality_df.dropna(subset=["_quality"])
                .sort_values(
                    "_quality",
                    ascending=False,
                )
                .head(5)
            )

            if not quality_df.empty:

                display_columns = [
                    company_column,
                    "_quality",
                ]

                if roe_column:
                    display_columns.append(roe_column)

                if pe_column:
                    display_columns.append(pe_column)

                top5 = quality_df[display_columns].copy()

                rename_map = {
                    company_column: "Company",
                    "_quality": "Quality Score",
                }

                if roe_column:
                    rename_map[roe_column] = "ROE %"

                if pe_column:
                    rename_map[pe_column] = "P/E"

                top5 = top5.rename(columns=rename_map)

                for column in [
                    "Quality Score",
                    "ROE %",
                    "P/E",
                ]:

                    if column in top5.columns:

                        top5[column] = pd.to_numeric(
                            top5[column],
                            errors="coerce",
                        ).round(2)

                st.dataframe(
                    top5,
                    hide_index=True,
                    use_container_width=True,
                )

            else:

                st.info("Quality score data is unavailable.")

        else:

            st.info("Quality ranking data is unavailable.")

    # ======================================================
    # SECTOR INTELLIGENCE
    # ======================================================

    st.subheader("Sector Intelligence")

    st.markdown(
        '<div class="section-description">'
        "Broad sector distribution across the tracked universe"
        "</div>",
        unsafe_allow_html=True,
    )

    if sector_column:

        sector = (
            df.groupby(sector_column)
            .size()
            .reset_index(name="Companies")
            .sort_values(
                "Companies",
                ascending=False,
            )
        )

        if not sector.empty:

            fig = px.bar(
                sector,
                x="Companies",
                y=sector_column,
                orientation="h",
            )

            fig.update_traces(
                hovertemplate=("<b>%{y}</b>" "<br>Companies: %{x}" "<extra></extra>")
            )

            fig.update_layout(
                height=430,
                margin={
                    "l": 10,
                    "r": 20,
                    "t": 20,
                    "b": 10,
                },
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={
                    "color": "#aab4c2",
                    "size": 10,
                },
                xaxis={
                    "title": None,
                    "gridcolor": "rgba(255,255,255,0.05)",
                    "zeroline": False,
                },
                yaxis={
                    "title": None,
                    "categoryorder": "total ascending",
                },
                showlegend=False,
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

    # ======================================================
    # MARKET INSIGHT
    # ======================================================

    if sector_column and not sector.empty:

        largest_sector = str(sector.iloc[0][sector_column])

        largest_count = int(sector.iloc[0]["Companies"])

        st.info(
            f"MARKET INSIGHT  |  "
            f"{largest_sector} is the largest represented "
            f"sector with {largest_count} tracked companies."
        )

    # ======================================================
    # FOOTER
    # ======================================================

    st.caption(
        "NIFTY 100 FINANCIAL INTELLIGENCE  |  "
        "FUNDAMENTALS  |  "
        "VALUATION  |  "
        "RISK  |  "
        "GROWTH"
    )
