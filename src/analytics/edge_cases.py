import sqlite3
from pathlib import Path

OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

DATABASE = "db/nifty100.db"


def generate_edge_case_log():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    rows = cursor.execute("""
        SELECT
            c.company_name,
            s.broad_sector,
            c.roe_percentage,
            c.roce_percentage,
            f.return_on_equity_pct
        FROM companies c
        LEFT JOIN sectors s
            ON c.id = s.company_id
        LEFT JOIN financial_ratios f
            ON c.id = f.company_id
    """).fetchall()

    log_path = OUTPUT / "ratio_edge_cases.log"

    with open(log_path, "w", encoding="utf-8") as file:

        file.write("========== RATIO EDGE CASE REPORT ==========\n\n")

        for company, sector, source_roe, source_roce, calc_roe in rows:

            if calc_roe is None:
                continue

            if source_roe is None:
                continue

            difference = abs(calc_roe - source_roe)

            if difference > 5:

                if sector == "Financials":
                    category = "Financial Sector Exception"
                else:
                    category = "Formula / Source Difference"

                file.write(
                    f"{company}\n"
                    f"Sector : {sector}\n"
                    f"Source ROE : {source_roe}\n"
                    f"Calculated ROE : {calc_roe}\n"
                    f"Difference : {round(difference,2)}\n"
                    f"Category : {category}\n\n"
                )

    conn.close()

    print("ratio_edge_cases.log generated.")