import sqlite3
import pandas as pd


DATABASE = "db/nifty100.db"


class ScreenerLoader:

    def __init__(self):
        self.conn = sqlite3.connect(DATABASE)

    def load_master_dataframe(self):

        query = """
        SELECT

            fr.company_id,
            fr.year,

            c.company_name,
            c.roce_percentage,

            s.broad_sector,
            s.sub_sector,

            fr.return_on_equity_pct,
            fr.net_profit_margin_pct,
            fr.debt_to_equity,
            fr.interest_coverage,
            fr.asset_turnover,
            fr.free_cash_flow_cr,
            fr.revenue_cagr_3yr,
            fr.revenue_cagr_5yr,
            fr.pat_cagr_5yr,
            fr.eps_cagr_5yr,
            fr.dividend_payout_ratio_pct,
            fr.composite_quality_score,
            

            p.sales,
            p.net_profit,
            p.operating_profit,

            m.market_cap_crore,
            m.pe_ratio,
            m.pb_ratio,
            m.dividend_yield_pct

        FROM financial_ratios fr

        LEFT JOIN companies c
            ON fr.company_id = c.id

        LEFT JOIN sectors s
            ON fr.company_id = s.company_id

        LEFT JOIN profitandloss p
            ON fr.company_id = p.company_id
            AND fr.year = p.year

        LEFT JOIN market_cap m
            ON fr.company_id = m.company_id
            AND fr.year = m.year
        """

        df = pd.read_sql(query, self.conn)

        return df

    def close(self):
        self.conn.close()