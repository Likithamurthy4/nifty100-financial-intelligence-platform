import sqlite3
import pandas as pd

DATABASE = "db/nifty100.db"


class PeerAnalytics:

    def __init__(self):

        self.conn = sqlite3.connect(DATABASE)

    def load_data(self):

        query = """
        SELECT

            pg.company_id,
            pg.peer_group_name,

            c.company_name,

            fr.year,
            fr.return_on_equity_pct,
            c.roce_percentage,
            fr.net_profit_margin_pct,
            fr.debt_to_equity,
            fr.free_cash_flow_cr,
            fr.pat_cagr_5yr,
            fr.revenue_cagr_5yr,
            fr.eps_cagr_5yr,
            fr.interest_coverage,
            fr.asset_turnover

        FROM peer_groups pg

        LEFT JOIN financial_ratios fr
            ON pg.company_id = fr.company_id

        LEFT JOIN companies c
            ON pg.company_id = c.id
        """

        return pd.read_sql(query, self.conn)
    def compute_percentiles(self, df):

        metrics = [

            "return_on_equity_pct",
            "roce_percentage",
            "net_profit_margin_pct",
            "debt_to_equity",
            "free_cash_flow_cr",
            "pat_cagr_5yr",
            "revenue_cagr_5yr",
            "eps_cagr_5yr",
            "interest_coverage",
            "asset_turnover"

        ]
        if df["peer_group_name"].isna().all():
            print("No peer group assigned.")
            return pd.DataFrame()
        output = []

        for peer_name, group in df.groupby("peer_group_name"):

            for metric in metrics:

                rank = group[metric].rank(pct=True)

                if metric == "debt_to_equity":
                    rank = 1 - rank

                temp = pd.DataFrame({

                    "company_id": group["company_id"],
                    "peer_group_name": peer_name,
                    "metric": metric,
                    "value": group[metric],
                    "percentile_rank": (rank * 100).round(2),
                    "year": group["year"]

                })

                output.append(temp)

        return pd.concat(output, ignore_index=True)
    
    def save(self, df):

        df.to_sql(

            "peer_percentiles",

            self.conn,

            if_exists="replace",

            index=False

        )

        print("peer_percentiles table updated.")

    def close(self):

        self.conn.close()