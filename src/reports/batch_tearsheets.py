import os
import sys
import sqlite3
import pandas as pd


# ---------------------------------------------------------
# Make src importable
# ---------------------------------------------------------

SRC_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


from reports.tearsheet import build_tearsheet


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

DATABASE = "db/nifty100.db"

OUTPUT_DIR = "reports/tearsheets"

SKIPPED_FILE = (
    "output/skipped_tearsheets.csv"
)


os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

os.makedirs(
    "output",
    exist_ok=True
)


# ---------------------------------------------------------
# Database connection
# ---------------------------------------------------------

def get_connection():

    return sqlite3.connect(
        DATABASE
    )


# ---------------------------------------------------------
# Get all companies
# ---------------------------------------------------------

def get_companies():

    conn = get_connection()

    companies = pd.read_sql(
        """
        SELECT
            id AS company_id,
            company_name
        FROM companies
        ORDER BY id
        """,
        conn
    )

    conn.close()

    return companies


# ---------------------------------------------------------
# Count available years
# ---------------------------------------------------------

def get_year_count(
    company_id
):

    conn = get_connection()

    # Use profit and loss as the main
    # historical financial-data check.
    df = pd.read_sql(
        """
        SELECT DISTINCT year
        FROM profitandloss
        WHERE company_id = ?
        ORDER BY year
        """,
        conn,
        params=[company_id]
    )

    conn.close()

    return len(df)


# ---------------------------------------------------------
# Batch generation
# ---------------------------------------------------------

def main():

    companies = get_companies()

    print(
        "Companies found:",
        len(companies)
    )

    generated = []

    skipped = []

    failed = []

    print(
        "\n=== STARTING BATCH TEARSHEET GENERATION ==="
    )

    for index, row in companies.iterrows():

        company_id = row["company_id"]

        company_name = row["company_name"]

        print(
            f"\n[{index + 1}/{len(companies)}] "
            f"{company_id} - {company_name}"
        )

        # -------------------------------------------------
        # Check minimum 3 years
        # -------------------------------------------------

        year_count = get_year_count(
            company_id
        )

        print(
            "Available years:",
            year_count
        )

        if year_count < 3:

            print(
                "SKIPPED — fewer than 3 years of data"
            )

            skipped.append(
                {
                    "company_id": company_id,
                    "company_name": company_name,
                    "years_available": year_count,
                    "reason":
                        "Fewer than 3 years of data"
                }
            )

            continue

        # -------------------------------------------------
        # Output filename
        # -------------------------------------------------

        output_path = os.path.join(
            OUTPUT_DIR,
            f"{company_id}_tearsheet.pdf"
        )

        # -------------------------------------------------
        # Generate PDF
        # -------------------------------------------------

        try:

            build_tearsheet(
                company_id,
                output_path
            )

            if os.path.exists(
                output_path
            ):

                file_size = os.path.getsize(
                    output_path
                )

                print(
                    f"GENERATED — "
                    f"{file_size / 1024:.1f} KB"
                )

                generated.append(
                    {
                        "company_id":
                            company_id,

                        "company_name":
                            company_name,

                        "years_available":
                            year_count,

                        "file":
                            output_path,

                        "size_kb":
                            round(
                                file_size / 1024,
                                2
                            )
                    }
                )

            else:

                print(
                    "FAILED — PDF was not created"
                )

                failed.append(
                    {
                        "company_id":
                            company_id,

                        "company_name":
                            company_name,

                        "reason":
                            "PDF was not created"
                    }
                )

        except Exception as e:

            print(
                "FAILED:",
                str(e)
            )

            failed.append(
                {
                    "company_id":
                        company_id,

                    "company_name":
                        company_name,

                    "reason":
                        str(e)
                }
            )

    # ---------------------------------------------------------
    # Save skipped companies
    # ---------------------------------------------------------

    skipped_df = pd.DataFrame(
        skipped
    )

    skipped_df.to_csv(
        SKIPPED_FILE,
        index=False
    )

    # ---------------------------------------------------------
    # Final report
    # ---------------------------------------------------------

    print(
        "\n========================================"
    )

    print(
        "BATCH TEARSHEET GENERATION COMPLETE"
    )

    print(
        "========================================"
    )

    print(
        "Total companies:",
        len(companies)
    )

    print(
        "Generated:",
        len(generated)
    )

    print(
        "Skipped:",
        len(skipped)
    )

    print(
        "Failed:",
        len(failed)
    )

    print(
        "\nSkipped file:"
    )

    print(
        SKIPPED_FILE
    )

    # ---------------------------------------------------------
    # Show failures
    # ---------------------------------------------------------

    if failed:

        print(
            "\n=== FAILED COMPANIES ==="
        )

        for item in failed:

            print(
                item["company_id"],
                "-",
                item["reason"]
            )

    # ---------------------------------------------------------
    # File count verification
    # ---------------------------------------------------------

    pdf_files = [
        file
        for file in os.listdir(
            OUTPUT_DIR
        )
        if file.lower().endswith(".pdf")
    ]

    print(
        "\nPDF files in tearsheets folder:",
        len(pdf_files)
    )

    # ---------------------------------------------------------
    # 30 KB QA
    # ---------------------------------------------------------

    small_files = []

    for file in pdf_files:

        path = os.path.join(
            OUTPUT_DIR,
            file
        )

        size = os.path.getsize(
            path
        )

        if size < 30 * 1024:

            small_files.append(
                {
                    "file": file,
                    "size_kb":
                        round(
                            size / 1024,
                            2
                        )
                }
            )

    print(
        "PDFs below 30 KB:",
        len(small_files)
    )

    if small_files:

        print(
            "\n=== SMALL PDF FILES ==="
        )

        for item in small_files:

            print(
                item["file"],
                "-",
                item["size_kb"],
                "KB"
            )


if __name__ == "__main__":

    main()