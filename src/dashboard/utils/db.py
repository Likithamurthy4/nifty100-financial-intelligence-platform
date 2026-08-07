import sqlite3
import pandas as pd
import streamlit as st

DATABASE = "db/nifty100.db"


@st.cache_data(ttl=600)
def run_query(query):

    conn = sqlite3.connect(DATABASE)

    df = pd.read_sql(query, conn)

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_companies():

    return run_query(
        """
        SELECT *
        FROM companies
        ORDER BY company_name
        """
    )


@st.cache_data(ttl=600)
def get_sectors():

    return run_query(
        """
        SELECT *
        FROM sectors
        """
    )


@st.cache_data(ttl=600)
def get_ratios(company_id):

    return run_query(f"""
        SELECT *
        FROM financial_ratios
        WHERE company_id='{company_id}'
        ORDER BY year
    """)


@st.cache_data(ttl=600)
def get_pl(company_id):

    return run_query(f"""
        SELECT *
        FROM profitandloss
        WHERE company_id='{company_id}'
        ORDER BY year
    """)


@st.cache_data(ttl=600)
def get_bs(company_id):

    return run_query(f"""
        SELECT *
        FROM balancesheet
        WHERE company_id='{company_id}'
        ORDER BY year
    """)


@st.cache_data(ttl=600)
def get_cf(company_id):

    return run_query(f"""
        SELECT *
        FROM cashflow
        WHERE company_id='{company_id}'
        ORDER BY year
    """)


@st.cache_data(ttl=600)
def get_peers(group_name):

    return run_query(f"""
        SELECT *
        FROM peer_groups
        WHERE peer_group_name='{group_name}'
    """)

@st.cache_data(ttl=600)
def get_dashboard_data(year):

    return run_query(f"""
        SELECT

            fr.company_id,
            c.company_name,

            s.broad_sector,

            fr.return_on_equity_pct,
            fr.debt_to_equity,
            fr.revenue_cagr_5yr,
            fr.composite_quality_score,

            m.pe_ratio

        FROM financial_ratios fr

        JOIN companies c
            ON fr.company_id = c.id

        LEFT JOIN sectors s
            ON fr.company_id = s.company_id

        LEFT JOIN market_cap m
            ON fr.company_id = m.company_id
            AND fr.year = m.year

        WHERE fr.year={year}
    """)
@st.cache_data(ttl=600)
def search_company(keyword):

    return run_query(f"""
        SELECT
            id,
            company_name

        FROM companies

        WHERE

            company_name LIKE '%{keyword}%'

            OR

            id LIKE '%{keyword}%'

        ORDER BY company_name
    """)


@st.cache_data(ttl=600)
def get_company_profile(company_id):

    return run_query(f"""
        SELECT

            c.id,
            c.company_name,
            c.about_company,
            c.website,
            c.company_logo,
            c.face_value,
            c.book_value,
            c.roce_percentage,
            c.roe_percentage,

            s.broad_sector,
            s.sub_sector

        FROM companies c

        LEFT JOIN sectors s
            ON c.id = s.company_id

        WHERE c.id='{company_id}'
    """)
@st.cache_data(ttl=600)
def get_screener_data():

    return run_query("""
        SELECT

            fr.company_id,
            c.company_name,

            s.broad_sector,

            fr.return_on_equity_pct,
            fr.debt_to_equity,
            fr.free_cash_flow_cr,
            fr.revenue_cagr_5yr,
            fr.pat_cagr_5yr,
            fr.net_profit_margin_pct,
            fr.interest_coverage,

            m.pe_ratio,
            m.pb_ratio,
            m.dividend_yield_pct,

            fr.composite_quality_score

        FROM financial_ratios fr

        JOIN companies c
            ON fr.company_id = c.id

        LEFT JOIN sectors s
            ON fr.company_id = s.company_id

        LEFT JOIN market_cap m
            ON fr.company_id = m.company_id
            AND fr.year = m.year

        WHERE fr.year = (
            SELECT MAX(f2.year)
            FROM financial_ratios f2
            WHERE f2.company_id = fr.company_id
        )
    """)
@st.cache_data(ttl=600)
def get_peer_groups():

    return run_query("""
        SELECT DISTINCT peer_group_name
        FROM peer_groups
        ORDER BY peer_group_name
    """)


@st.cache_data(ttl=600)
def get_peer_companies(group_name):

    return run_query(f"""
        SELECT

            pg.company_id,
            c.company_name

        FROM peer_groups pg

        JOIN companies c
            ON pg.company_id = c.id

        WHERE pg.peer_group_name='{group_name}'

        ORDER BY c.company_name
    """)
@st.cache_data(ttl=600)
def get_peer_metrics(group_name):

    return run_query(f"""
        SELECT

            pg.peer_group_name,
            c.company_name,

            fr.return_on_equity_pct,
            c.roce_percentage,
            fr.net_profit_margin_pct,
            fr.debt_to_equity,
            fr.free_cash_flow_cr,
            fr.revenue_cagr_5yr,
            fr.pat_cagr_5yr,
            fr.composite_quality_score

        FROM peer_groups pg

        JOIN companies c
            ON pg.company_id = c.id

        JOIN financial_ratios fr
            ON pg.company_id = fr.company_id

        WHERE pg.peer_group_name = '{group_name}'

        AND fr.year = (
            SELECT MAX(year)
            FROM financial_ratios f2
            WHERE f2.company_id = fr.company_id
        )
    """)
@st.cache_data(ttl=600)
def get_peer_table(group_name):

    return run_query(f"""
        SELECT

            pg.company_id,
            c.company_name,

            fr.return_on_equity_pct,
            c.roce_percentage,
            fr.net_profit_margin_pct,
            fr.debt_to_equity,
            fr.free_cash_flow_cr,
            fr.revenue_cagr_5yr,
            fr.pat_cagr_5yr,
            fr.eps_cagr_5yr,
            fr.interest_coverage,
            fr.asset_turnover,
            fr.composite_quality_score

        FROM peer_groups pg

        JOIN companies c
            ON pg.company_id = c.id

        JOIN financial_ratios fr
            ON pg.company_id = fr.company_id

        WHERE pg.peer_group_name = '{group_name}'

        AND fr.year = (
            SELECT MAX(year)
            FROM financial_ratios f2
            WHERE f2.company_id = fr.company_id
        )

        ORDER BY fr.composite_quality_score DESC
    """)
@st.cache_data(ttl=600)
def get_trend_data(company_id):

    return run_query(f"""
        SELECT

            year,

            return_on_equity_pct,
            net_profit_margin_pct,
            debt_to_equity,
            interest_coverage,
            asset_turnover,
            free_cash_flow_cr,
            revenue_cagr_5yr,
            revenue_cagr_3yr,
            pat_cagr_5yr,
            eps_cagr_5yr,
            composite_quality_score

        FROM financial_ratios

        WHERE company_id='{company_id}'

        ORDER BY year
    """)
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
@st.cache_data(ttl=600)
def get_capital_allocation():

    return run_query("""
        SELECT

            c.company_name,

            CASE

                WHEN fr.debt_to_equity < 0.3
                     AND fr.dividend_payout_ratio_pct > 30
                THEN 'Cash Rich'

                WHEN fr.debt_to_equity < 0.5
                     AND fr.revenue_cagr_5yr > 15
                THEN 'Growth'

                WHEN fr.debt_to_equity > 1
                THEN 'Highly Leveraged'

                WHEN fr.free_cash_flow_cr > 0
                THEN 'Strong Cash Flow'

                WHEN fr.return_on_equity_pct > 20
                THEN 'High Return'

                ELSE 'Balanced'

            END AS capital_pattern,

            fr.composite_quality_score

        FROM financial_ratios fr

        JOIN companies c
            ON fr.company_id = c.id

        WHERE fr.year = (

            SELECT MAX(year)

            FROM financial_ratios f2

            WHERE f2.company_id = fr.company_id

        )

    """)
@st.cache_data(ttl=600)
def get_reports(company_id):

    return run_query(f"""
        SELECT

            year,
            annual_report

        FROM documents

        WHERE company_id = '{company_id}'

        ORDER BY year DESC
    """)