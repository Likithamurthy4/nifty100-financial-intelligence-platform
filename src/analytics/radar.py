import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

DATABASE = "db/nifty100.db"


class RadarChart:

    def __init__(self):
        self.conn = sqlite3.connect(DATABASE)

    def load_data(self):

        query = """
        SELECT

            pg.peer_group_name,
            c.company_name,

            fr.return_on_equity_pct,
            c.roce_percentage,
            fr.net_profit_margin_pct,
            fr.debt_to_equity,
            fr.free_cash_flow_cr,
            fr.pat_cagr_5yr,
            fr.revenue_cagr_5yr,
            fr.composite_quality_score

        FROM peer_groups pg

        JOIN companies c
            ON pg.company_id = c.id

        JOIN financial_ratios fr
            ON pg.company_id = fr.company_id
        """

        return pd.read_sql(query, self.conn)
    def create_charts(self, df):

        metrics = [

            "return_on_equity_pct",
            "roce_percentage",
            "net_profit_margin_pct",
            "debt_to_equity",
            "free_cash_flow_cr",
            "pat_cagr_5yr",
            "revenue_cagr_5yr",
            "composite_quality_score"

        ]

        os.makedirs("reports/radar_charts", exist_ok=True)
        for company in df["company_name"].unique():

            # Keep the original value for filtering
            company_df = df[df["company_name"] == company]

            if company_df.empty:
                continue

            # Create a clean name only for the output file
            safe_name = (
                str(company)
                .strip()
                .replace("\n", " ")
                .replace("\r", " ")
                .replace("/", "-")
                .replace("\\", "-")
                .replace(":", "-")
                .replace("*", "")
                .replace("?", "")
                .replace('"', "")
                .replace("<", "")
                .replace(">", "")
                .replace("|", "")
            )
        
            peer = company_df["peer_group_name"].iloc[0]

            peer_avg = (
                df[df.peer_group_name == peer][metrics]
                .mean()
            )

            values = company_df.iloc[0][metrics].tolist()
            averages = peer_avg.tolist()

            labels = [
                "ROE",
                "ROCE",
                "NPM",
                "D/E",
                "FCF",
                "PAT CAGR",
                "Revenue CAGR",
                "Composite"
            ]

            N = len(labels)

            angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()

            values += values[:1]
            averages += averages[:1]
            angles += angles[:1]

            plt.figure(figsize=(7,7))

            ax = plt.subplot(111, polar=True)

            ax.plot(angles, values, linewidth=2, label=company)
            ax.fill(angles, values, alpha=0.20)

            ax.plot(angles, averages, linewidth=2, label="Peer Average")

            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(labels)

            plt.title(safe_name)

            plt.legend(loc="upper right")
            safe_name = " ".join(str(company).split())

            safe_name = (
                safe_name.replace("/", "-")
                        .replace("\\", "-")
                        .replace(":", "-")
                        .replace("*", "")
                        .replace("?", "")
                        .replace('"', "")
                        .replace("<", "")
                        .replace(">", "")
                        .replace("|", "")
            )

            plt.savefig(f"reports/radar_charts/{safe_name}.png")
           
            plt.close()
        print(repr(company))
        print(repr(safe_name))
        print("Radar charts created.")
    def close(self):
        self.conn.close()