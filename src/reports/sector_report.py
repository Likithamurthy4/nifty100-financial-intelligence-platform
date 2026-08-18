import os
import re
import sqlite3

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ============================================================
# PATHS
# ============================================================

DATABASE = "db/nifty100.db"

OUTPUT_DIR = "reports/sector"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# DATABASE
# ============================================================


def get_connection():

    return sqlite3.connect(DATABASE)


def load_sector_data():

    conn = get_connection()

    query = """
    WITH latest_ratios AS (

        SELECT *
        FROM financial_ratios
        WHERE year = (
            SELECT MAX(r2.year)
            FROM financial_ratios r2
            WHERE r2.company_id =
                  financial_ratios.company_id
        )
    ),

    latest_market AS (

        SELECT *
        FROM market_cap
        WHERE year = (
            SELECT MAX(m2.year)
            FROM market_cap m2
            WHERE m2.company_id =
                  market_cap.company_id
        )
    )

    SELECT

        c.id AS company_id,

        c.company_name,

        s.broad_sector,

        s.sub_sector,

        r.return_on_equity_pct,

        r.debt_to_equity,

        r.free_cash_flow_cr,

        r.revenue_cagr_5yr,

        r.pat_cagr_5yr,

        r.operating_profit_margin_pct,

        m.pe_ratio,

        m.pb_ratio,

        m.market_cap_crore

    FROM companies c

    LEFT JOIN sectors s
        ON c.id = s.company_id

    LEFT JOIN latest_ratios r
        ON c.id = r.company_id

    LEFT JOIN latest_market m
        ON c.id = m.company_id

    WHERE s.broad_sector IS NOT NULL

    ORDER BY
        s.broad_sector,
        c.id
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


# ============================================================
# HELPERS
# ============================================================


def clean_number(value):

    if pd.isna(value):
        return "N/A"

    try:

        return f"{float(value):,.2f}"

    except (TypeError, ValueError):

        return str(value)


def clean_integer(value):

    if pd.isna(value):
        return "N/A"

    try:

        return f"{float(value):,.0f}"

    except (TypeError, ValueError):

        return str(value)


def safe_median(series):

    values = pd.to_numeric(series, errors="coerce").dropna()

    if values.empty:
        return "N/A"

    return f"{values.median():,.2f}"


def safe_filename(name):

    name = str(name)

    name = re.sub(r"[^A-Za-z0-9_-]+", "_", name)

    return name.strip("_")


# ============================================================
# STYLES
# ============================================================

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "SectorTitle",
    parent=styles["Title"],
    fontSize=20,
    leading=24,
    alignment=TA_CENTER,
    textColor=colors.white,
)

heading_style = ParagraphStyle(
    "Heading",
    parent=styles["Heading2"],
    fontSize=13,
    leading=16,
    spaceBefore=5,
    spaceAfter=6,
)

body_style = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=8, leading=10)

table_style = ParagraphStyle(
    "TableText", parent=styles["BodyText"], fontSize=6.5, leading=8, wordWrap="CJK"
)


# ============================================================
# SECTOR HEADER
# ============================================================


def create_header(sector, company_count):

    data = [
        [
            Paragraph(
                f"<b>{sector}</b><br/>"
                f"<font size=10>"
                f"{company_count} Companies"
                f"</font>",
                title_style,
            )
        ]
    ]

    table = Table(data, colWidths=[267 * mm], rowHeights=[25 * mm])

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#172554")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]
        )
    )

    return table


# ============================================================
# MEDIAN KPI SUMMARY
# ============================================================


def create_summary_table(sector_df):

    metrics = [
        ("Median ROE %", "return_on_equity_pct"),
        ("Median D/E", "debt_to_equity"),
        ("Median FCF", "free_cash_flow_cr"),
        ("Median Revenue CAGR", "revenue_cagr_5yr"),
        ("Median PAT CAGR", "pat_cagr_5yr"),
        ("Median OPM %", "operating_profit_margin_pct"),
        ("Median P/E", "pe_ratio"),
        ("Median P/B", "pb_ratio"),
    ]

    row1 = []
    row2 = []

    for title, column in metrics:

        value = safe_median(sector_df[column])

        cell = Paragraph(
            f"<b>{title}</b><br/>" f"<font size=12>{value}</font>", body_style
        )

        if len(row1) < 4:
            row1.append(cell)
        else:
            row2.append(cell)

    data = [row1, row2]

    table = Table(
        data,
        colWidths=[66 * mm, 66 * mm, 66 * mm, 66 * mm],
        rowHeights=[20 * mm, 20 * mm],
    )

    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    return table


# ============================================================
# COMPANY TABLE
# ============================================================


def create_company_table(sector_df):

    headers = [
        "Ticker",
        "Company",
        "ROE %",
        "D/E",
        "FCF",
        "Rev CAGR",
        "PAT CAGR",
        "OPM %",
        "P/E",
        "P/B",
    ]

    data = [[Paragraph(f"<b>{header}</b>", table_style) for header in headers]]

    for _, row in sector_df.iterrows():

        data.append(
            [
                Paragraph(str(row["company_id"]), table_style),
                Paragraph(str(row["company_name"]), table_style),
                Paragraph(clean_number(row["return_on_equity_pct"]), table_style),
                Paragraph(clean_number(row["debt_to_equity"]), table_style),
                Paragraph(clean_integer(row["free_cash_flow_cr"]), table_style),
                Paragraph(clean_number(row["revenue_cagr_5yr"]), table_style),
                Paragraph(clean_number(row["pat_cagr_5yr"]), table_style),
                Paragraph(
                    clean_number(row["operating_profit_margin_pct"]), table_style
                ),
                Paragraph(clean_number(row["pe_ratio"]), table_style),
                Paragraph(clean_number(row["pb_ratio"]), table_style),
            ]
        )

    table = Table(
        data,
        colWidths=[
            22 * mm,
            48 * mm,
            21 * mm,
            19 * mm,
            25 * mm,
            23 * mm,
            23 * mm,
            21 * mm,
            20 * mm,
            20 * mm,
        ],
        repeatRows=1,
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#172554")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    return table


# ============================================================
# GENERATE ONE SECTOR REPORT
# ============================================================


def generate_sector_report(sector, sector_df):

    filename = f"{safe_filename(sector)}" f"_report.pdf"

    output_path = os.path.join(OUTPUT_DIR, filename)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(A4),
        rightMargin=10 * mm,
        leftMargin=10 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
        title=f"{sector} Sector Report",
    )

    story = []

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    story.append(create_header(sector, len(sector_df)))

    story.append(Spacer(1, 7))

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    story.append(Paragraph("Sector Median KPIs", heading_style))

    story.append(create_summary_table(sector_df))

    story.append(Spacer(1, 8))

    # --------------------------------------------------------
    # Company list
    # --------------------------------------------------------

    story.append(Paragraph("Companies in Sector", heading_style))

    story.append(create_company_table(sector_df))

    doc.build(story)

    return output_path


# ============================================================
# MAIN
# ============================================================


def main():

    print("Loading sector data...")

    df = load_sector_data()

    print("Total companies:", df["company_id"].nunique())

    print("Sectors found:", df["broad_sector"].nunique())

    print("\nSector distribution:")

    print(df["broad_sector"].value_counts().to_string())

    print("\n=== GENERATING SECTOR REPORTS ===")

    generated = []

    for sector in sorted(df["broad_sector"].dropna().unique()):

        sector_df = df[df["broad_sector"] == sector].copy()

        print(f"\nGenerating: {sector}")

        print("Companies:", len(sector_df))

        try:

            path = generate_sector_report(sector, sector_df)

            size_kb = os.path.getsize(path) / 1024

            print(f"Generated: {path}")

            print(f"Size: {size_kb:.1f} KB")

            generated.append(path)

        except Exception as e:  # noqa: BLE001

            print(f"FAILED: {sector}")

            print(str(e))

    # --------------------------------------------------------
    # Final QA
    # --------------------------------------------------------

    pdf_files = [
        file for file in os.listdir(OUTPUT_DIR) if file.lower().endswith(".pdf")
    ]

    print("\n========================================")

    print("SECTOR REPORT GENERATION COMPLETE")

    print("========================================")

    actual_sector_count = df["broad_sector"].nunique()

    print("Sectors in database:", actual_sector_count)

    print("Generated PDFs:", len(pdf_files))

    print("Generated PDFs:", len(pdf_files))

    print("\nFiles:")

    for file in sorted(pdf_files):

        path = os.path.join(OUTPUT_DIR, file)

        size_kb = os.path.getsize(path) / 1024

        print(f"{file} — {size_kb:.1f} KB")


if __name__ == "__main__":

    main()
