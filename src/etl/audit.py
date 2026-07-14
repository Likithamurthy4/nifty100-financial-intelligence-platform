"""
audit.py

Maintains ETL load audit.
"""

from pathlib import Path
import pandas as pd

OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)


class AuditLogger:

    def __init__(self):

        self.records = []

    def add(
        self,
        table,
        loaded,
        rejected,
        status
    ):

        self.records.append({

            "table": table,
            "rows_loaded": loaded,
            "rows_rejected": rejected,
            "status": status

        })

    def save(self):

        pd.DataFrame(

            self.records

        ).to_csv(

            OUTPUT / "load_audit.csv",

            index=False

        )

        print()

        print("=" * 50)

        print("Load Audit Saved")

        print("=" * 50)