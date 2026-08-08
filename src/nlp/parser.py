import os
import re
import sqlite3
import pandas as pd


DATABASE = "db/nifty100.db"


class AnalysisParser:

    def __init__(self):

        self.conn = sqlite3.connect(DATABASE)

        self.pattern = re.compile(
            r"(?:(\d+)\s*Years?|(\d+)\s*Year|Last\s*Year|TTM)"
            r"\s*:?\s*(-?[\d.]+)%",
            re.IGNORECASE
        )

    def load(self):

        return pd.read_sql(
            "SELECT * FROM analysis",
            self.conn
        )

    def parse(self):

        df = self.load()

        parsed = []

        failures = []

        metrics = [

            "compounded_sales_growth",
            "compounded_profit_growth",
            "stock_price_cagr",
            "roe"

        ]

        for _, row in df.iterrows():

            company = row["company_id"]

            for metric in metrics:

                text = str(row[metric])

                match = self.pattern.search(text)

                if match:

                    period = match.group(1) or match.group(2)

                    if period is None:
                        # Last Year / TTM
                        period = 1

                    parsed.append({
                        "company_id": company,
                        "metric_type": metric,
                        "period_years": int(period),
                        "value_pct": float(match.group(3))
                })

                else:

                    failures.append({

                        "company_id": company,

                        "metric_type": metric,

                        "text": text

                    })

        return (

            pd.DataFrame(parsed),

            pd.DataFrame(failures)

        )
    def export(self):

        parsed, failures = self.parse()

        os.makedirs(
            "output",
            exist_ok=True
        )

        parsed.to_csv(

            "output/analysis_parsed.csv",

            index=False

        )

        failures.to_csv(

            "output/parse_failures.csv",

            index=False

        )

        print()

        print("Parsed Rows :", len(parsed))

        print("Failures :", len(failures))

        return parsed
    def close(self):

        self.conn.close()