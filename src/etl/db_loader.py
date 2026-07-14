"""
db_loader.py

Professional SQLite Loader
"""

import sqlite3
from pathlib import Path

from src.etl.loader import load_all_datasets
from src.etl.audit import AuditLogger

DATABASE = Path("db/nifty100.db")


class DatabaseLoader:

    def __init__(self):

        self.conn = sqlite3.connect(DATABASE)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.audit = AuditLogger()

    def companies(self):

        df = self.datasets["companies"]

        df.to_sql(
            "companies",
            self.conn,
            if_exists="append",
            index=False
        )

        self.company_ids = set(df["id"])

        self.audit.add(
            "companies",
            len(df),
            0,
            "SUCCESS"
        )

        print(f"companies            Loaded={len(df)} Rejected=0")

    def remove_invalid_fk(self, df):

        if "company_id" not in df.columns:
            return df, 0

        invalid = ~df["company_id"].isin(self.company_ids)

        rejected = invalid.sum()

        cleaned = df[~invalid]

        return cleaned, rejected

    def load_table(self, table_name):

        df = self.datasets[table_name]

        cleaned_df, rejected = self.remove_invalid_fk(df)

        cleaned_df.to_sql(
            table_name,
            self.conn,
            if_exists="append",
            index=False
        )

        self.audit.add(
            table_name,
            len(cleaned_df),
            rejected,
            "SUCCESS"
        )

        print(
            f"{table_name:<20}"
            f" Loaded={len(cleaned_df)} "
            f"Rejected={rejected}"
        )

    def run(self):

        print("\nLoading datasets...\n")

        self.datasets = load_all_datasets()

        self.companies()

        load_order = [
            "sectors",
            "analysis",
            "prosandcons",
            "documents",
            "profitandloss",
            "balancesheet",
            "cashflow",
            "stock_prices",
            "market_cap",
            "financial_ratios",
            "peer_groups"
        ]

        for table in load_order:
            self.load_table(table)

        self.conn.commit()

        self.audit.save()

        self.conn.close()

        print("\nDatabase Loading Completed Successfully!")


if __name__ == "__main__":

    loader = DatabaseLoader()
    loader.run()