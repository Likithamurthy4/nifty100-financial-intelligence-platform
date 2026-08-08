import os
import sqlite3
import pandas as pd
import re

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

# ============================================================
# CONFIG
# ============================================================

DATABASE = "db/nifty100.db"
OUTPUT_DIR = "reports/portfolio"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "portfolio_summary.pdf")

EXPECTED_COMPANIES = 92
TREND_YEARS = 3
STABLE_BAND_PCT = 2.0

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# DATABASE
# ============================================================

def get_connection():
    return sqlite3.connect(DATABASE)


def load_data():
    """
    Load exactly one latest row and one exact 3-years-earlier row
    for every company.

    If the exact year three years earlier is unavailable, the
    comparison values remain NULL and the PDF displays N/A.
    """

    conn = get_connection()

    query = f"""
    WITH latest AS (
        SELECT fr.*
        FROM financial_ratios fr
        INNER JOIN (
            SELECT company_id, MAX(year) AS latest_year
            FROM financial_ratios
            GROUP BY company_id
        ) x
            ON fr.company_id = x.company_id
           AND fr.year = x.latest_year
    ),

    previous AS (
        SELECT fr.*
        FROM financial_ratios fr
        INNER JOIN latest l
            ON fr.company_id = l.company_id
           AND fr.year = l.year - {TREND_YEARS}
    ),

    sector_map AS (
        SELECT
            company_id,
            MAX(broad_sector) AS broad_sector
        FROM sectors
        GROUP BY company_id
    )

    SELECT
        c.id AS company_id,
        c.company_name,
        s.broad_sector,

        latest.year AS latest_year,

        latest.return_on_equity_pct,
        latest.net_profit_margin_pct,
        latest.debt_to_equity,
        latest.revenue_cagr_5yr,
        latest.free_cash_flow_cr,
        latest.composite_quality_score,

        previous.year AS previous_year,

        previous.return_on_equity_pct AS previous_roe,
        previous.net_profit_margin_pct AS previous_npm,
        previous.debt_to_equity AS previous_de,
        previous.revenue_cagr_5yr AS previous_revenue_cagr,
        previous.free_cash_flow_cr AS previous_fcf,
        previous.composite_quality_score AS previous_quality

    FROM companies c

    LEFT JOIN sector_map s
        ON c.id = s.company_id

    LEFT JOIN latest
        ON c.id = latest.company_id

    LEFT JOIN previous
        ON c.id = previous.company_id

    ORDER BY c.id
    """

    df = pd.read_sql(query, conn)
    conn.close()

    # Normalize IDs before any display-name logic.
    df["company_id"] = (
        df["company_id"]
        .astype(str)
        .str.strip()
        .str.rstrip(";")
    )

    return df


# ============================================================
# VALIDATION
# ============================================================

def validate_data(df):
    company_count = df["company_id"].nunique()

    print("Companies:", company_count)

    if company_count != EXPECTED_COMPANIES:
        raise ValueError(
            f"Expected {EXPECTED_COMPANIES} companies, "
            f"found {company_count}"
        )

    duplicate_ids = (
        df["company_id"]
        .value_counts()
    )

    duplicates = duplicate_ids[duplicate_ids > 1]

    if not duplicates.empty:
        raise ValueError(
            "Duplicate company rows detected:\n"
            + duplicates.to_string()
        )

    missing_latest = df["latest_year"].isna().sum()

    if missing_latest:
        print(
            f"Warning: {missing_latest} companies have no "
            "financial-ratio data."
        )

    missing_3yr = df["previous_year"].isna().sum()

    print(
        f"Companies with exact {TREND_YEARS}-year comparison: "
        f"{company_count - missing_3yr}"
    )

    print(
        f"Companies without exact {TREND_YEARS}-year comparison: "
        f"{missing_3yr}"
    )

    # Make sure any available comparison really is exactly 3 years earlier.
    valid = df["previous_year"].notna() & df["latest_year"].notna()

    if valid.any():
        delta = (
            df.loc[valid, "latest_year"].astype(int)
            - df.loc[valid, "previous_year"].astype(int)
        )

        if not (delta == TREND_YEARS).all():
            raise ValueError(
                "Trend comparison contains a year other than "
                f"exactly {TREND_YEARS} years earlier."
            )


# ============================================================
# HELPERS
# ============================================================

def safe_float(value):
    try:
        if pd.isna(value):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def format_value(value, suffix=""):
    value = safe_float(value)

    if value is None:
        return "N/A"

    return f"{value:,.2f}{suffix}"


def trend_arrow(current, previous, higher_is_better=True):
    """
    Compare latest value against the exact value from 3 years earlier.

    Returns:
        ↑ = improved by more than 2%
        ↓ = declined by more than 2%
        → = within ±2%
        N/A = comparison unavailable
    """

    current = safe_float(current)
    previous = safe_float(previous)

    if current is None or previous is None:
        return "N/A"

    if previous == 0:
        if current == 0:
            return "→"

        if higher_is_better:
            return "↑" if current > 0 else "↓"

        return "↑" if current < 0 else "↓"

    change_pct = ((current - previous) / abs(previous)) * 100

    if abs(change_pct) <= STABLE_BAND_PCT:
        return "→"

    if higher_is_better:
        return "↑" if change_pct > STABLE_BAND_PCT else "↓"

    # Debt / Equity: lower is better.
    return "↑" if change_pct < -STABLE_BAND_PCT else "↓"


# ============================================================
# COMPANY NAME CLEANING
# ============================================================

DISPLAY_NAME_ALIASES = {
    "ASIANPAINT": "Asian Paints",
    "APOLLOHOSP": "Apollo Hospitals",
}


def clean_ticker(value):
    if pd.isna(value):
        return "N/A"

    return (
        str(value)
        .strip()
        .rstrip(";")
    )


def clean_company_name(value, ticker=None):
    """
    Clean display-only company names.

    The SQLite database is never modified.
    """

    if pd.isna(value):
        name = "N/A"
    else:
        name = re.sub(
            r"\s+",
            " ",
            str(value).replace("\n", " ")
        ).strip()

    ticker = clean_ticker(ticker)

    # Known source-name issues observed in the portfolio PDF.
    if ticker in DISPLAY_NAME_ALIASES:
        return DISPLAY_NAME_ALIASES[ticker]

    # Remove clearly descriptive text accidentally appended to names.
    removable_suffixes = [
        r"\s+Chain of Indian private hospitals$",
        r"\s+Indian Multi-National Paint and Coating Manufacturing Company$",
    ]

    for pattern in removable_suffixes:
        name = re.sub(
            pattern,
            "",
            name,
            flags=re.IGNORECASE
        ).strip()

    return name


# ============================================================
# STYLES
# ============================================================

styles = getSampleStyleSheet()

header_style = ParagraphStyle(
    "Header",
    parent=styles["Title"],
    fontSize=18,
    leading=21,
    textColor=colors.white,
    alignment=TA_LEFT,
)

sector_style = ParagraphStyle(
    "Sector",
    parent=styles["BodyText"],
    fontSize=9,
    leading=11,
    textColor=colors.white,
)

section_style = ParagraphStyle(
    "Section",
    parent=styles["Heading2"],
    fontSize=11,
    leading=14,
    spaceBefore=4,
    spaceAfter=5,
)

cell_style = ParagraphStyle(
    "Cell",
    parent=styles["BodyText"],
    fontSize=8,
    leading=10,
)

small_style = ParagraphStyle(
    "Small",
    parent=styles["BodyText"],
    fontSize=7,
    leading=9,
)


# ============================================================
# HEADER
# ============================================================

def create_header(row):
    ticker = clean_ticker(row["company_id"])
    company_name = clean_company_name(
        row["company_name"],
        ticker
    )

    sector = row["broad_sector"]

    if pd.isna(sector) or not str(sector).strip():
        sector = "N/A"
    else:
        sector = str(sector).strip()

    data = [
        [
            Paragraph(
                f"<b>{company_name}</b>",
                header_style
            )
        ],
        [
            Paragraph(
                f"{ticker}  |  {sector}",
                sector_style
            )
        ],
    ]

    table = Table(
        data,
        colWidths=[184 * mm],
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                colors.HexColor("#172554"),
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                8,
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                8,
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5,
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5,
            ),
        ])
    )

    return table


# ============================================================
# KPI TABLE
# ============================================================

def create_kpi_table(row):
    metrics = [
        (
            "ROE",
            row["return_on_equity_pct"],
            row["previous_roe"],
            "%",
            True,
        ),
        (
            "Net Profit Margin",
            row["net_profit_margin_pct"],
            row["previous_npm"],
            "%",
            True,
        ),
        (
            "Debt / Equity",
            row["debt_to_equity"],
            row["previous_de"],
            "",
            False,
        ),
        (
            "Revenue CAGR 5Y",
            row["revenue_cagr_5yr"],
            row["previous_revenue_cagr"],
            "%",
            True,
        ),
        (
            "Free Cash Flow",
            row["free_cash_flow_cr"],
            row["previous_fcf"],
            " Cr",
            True,
        ),
        (
            "Quality Score",
            row["composite_quality_score"],
            row["previous_quality"],
            "",
            True,
        ),
    ]

    data = [
        [
            Paragraph("<b>KPI</b>", cell_style),
            Paragraph("<b>Latest</b>", cell_style),
            Paragraph("<b>Trend</b>", cell_style),
        ]
    ]

    for name, current, previous, suffix, higher_is_better in metrics:
        arrow = trend_arrow(
            current,
            previous,
            higher_is_better=higher_is_better,
        )

        value = format_value(current, suffix)

        # Use plain N/A for unavailable comparisons.
        if arrow == "N/A":
            trend_text = "N/A"
        else:
            trend_text = (
                f'<font size="13"><b>{arrow}</b></font>'
            )

        data.append(
            [
                Paragraph(name, cell_style),
                Paragraph(value, cell_style),
                Paragraph(trend_text, cell_style),
            ]
        )

    table = Table(
        data,
        colWidths=[
            75 * mm,
            70 * mm,
            39 * mm,
        ],
        repeatRows=1,
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#dbeafe"),
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey,
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                6,
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                6,
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                6,
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                6,
            ),
        ])
    )

    return table


# ============================================================
# PDF
# ============================================================

def build_portfolio_pdf(df):
    doc = SimpleDocTemplate(
        OUTPUT_FILE,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
        title="Nifty 100 Financial Intelligence Platform - Portfolio Summary",
        author="Nifty 100 Financial Intelligence Platform",
    )

    story = []

    # Alphabetical order by ticker/company_id.
    df = df.sort_values(
        "company_id",
        kind="stable",
    ).reset_index(drop=True)

    for index, (_, row) in enumerate(df.iterrows()):

        story.append(create_header(row))
        story.append(Spacer(1, 8))

        story.append(
            Paragraph(
                "Portfolio Snapshot",
                section_style,
            )
        )

        story.append(create_kpi_table(row))
        story.append(Spacer(1, 8))

        latest_year = row["latest_year"]

        if pd.isna(latest_year):
            latest_year_text = "N/A"
        else:
            latest_year_text = str(int(latest_year))

        story.append(
            Paragraph(
                f"<b>Latest Financial Year:</b> {latest_year_text}",
                cell_style,
            )
        )

        story.append(Spacer(1, 6))

        story.append(
            Paragraph(
                "Trend Legend",
                section_style,
            )
        )

        legend_data = [
            [
                Paragraph(
                    f"<b>↑</b> Improved &gt;{STABLE_BAND_PCT:g}% vs "
                    f"{TREND_YEARS} years earlier",
                    small_style,
                ),
                Paragraph(
                    f"<b>↓</b> Declined &gt;{STABLE_BAND_PCT:g}% vs "
                    f"{TREND_YEARS} years earlier",
                    small_style,
                ),
                Paragraph(
                    f"<b>→</b> Within ±{STABLE_BAND_PCT:g}% vs "
                    f"{TREND_YEARS} years earlier",
                    small_style,
                ),
            ]
        ]

        legend = Table(
            legend_data,
            colWidths=[
                60 * mm,
                60 * mm,
                60 * mm,
            ],
        )

        legend.setStyle(
            TableStyle([
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.grey,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
            ])
        )

        story.append(legend)
        story.append(Spacer(1, 10))

        # Explicitly show the comparison basis for transparency.
        previous_year = row["previous_year"]

        if (
            pd.notna(latest_year)
            and pd.notna(previous_year)
        ):
            comparison_text = (
                f"Trend comparison: {int(latest_year)} "
                f"vs {int(previous_year)}"
            )
        else:
            comparison_text = (
                f"Trend comparison: unavailable "
                f"(exact {TREND_YEARS}-year-earlier data not available)"
            )

        story.append(
            Paragraph(
                comparison_text,
                small_style,
            )
        )

        story.append(Spacer(1, 8))

        story.append(
            Paragraph(
                "Nifty 100 Financial Intelligence Platform",
                small_style,
            )
        )

        if index < len(df) - 1:
            story.append(PageBreak())

    doc.build(story)


# ============================================================
# MAIN
# ============================================================

def main():
    print("========================================")
    print("PORTFOLIO SUMMARY GENERATOR")
    print("========================================")

    print("\nLoading database:", DATABASE)

    if not os.path.exists(DATABASE):
        raise FileNotFoundError(
            f"Database not found: {DATABASE}"
        )

    df = load_data()

    validate_data(df)

    print(
        f"\nTrend basis: exact latest year vs "
        f"exactly {TREND_YEARS} years earlier"
    )

    print(
        f"Stable band: ±{STABLE_BAND_PCT:g}%"
    )

    print("\nGenerating PDF...")

    build_portfolio_pdf(df)

    file_size_kb = (
        os.path.getsize(OUTPUT_FILE) / 1024
    )

    print("\n========================================")
    print("PORTFOLIO SUMMARY COMPLETE")
    print("========================================")
    print("Companies:", df["company_id"].nunique())
    print("Pages expected:", df["company_id"].nunique())
    print("Output:", OUTPUT_FILE)
    print(f"File size: {file_size_kb:.1f} KB")

    print("\nName-cleaning checks:")
    for ticker in ["ASIANPAINT", "APOLLOHOSP"]:
        rows = df[df["company_id"] == ticker]
        if not rows.empty:
            print(
                f"  {ticker} -> "
                f"{clean_company_name(rows.iloc[0]['company_name'], ticker)}"
            )

    print("\nN/A trend handling: ENABLED")
    print("3-year comparison validation: ENABLED")


if __name__ == "__main__":
    main()
