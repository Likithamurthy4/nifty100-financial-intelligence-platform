import os
import sqlite3

import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

DATABASE = "db/nifty100.db"

OUTPUT_DIR = "reports/tearsheets"
TEMP_DIR = "output/tearsheet_charts"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)


# ============================================================
# Database
# ============================================================


def get_connection():
    return sqlite3.connect(DATABASE)


def get_company(company_id):

    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT
            c.*,
            s.broad_sector,
            s.sub_sector
        FROM companies c
        LEFT JOIN sectors s
            ON c.id = s.company_id
        WHERE c.id = ?
        """,
        conn,
        params=[company_id],
    )

    conn.close()

    return df


def get_sector(company_id):

    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT broad_sector, sub_sector
        FROM sectors
        WHERE company_id = ?
        """,
        conn,
        params=[company_id],
    )

    conn.close()

    return df


def get_ratios(company_id):

    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT *
        FROM financial_ratios
        WHERE company_id = ?
        ORDER BY year
        """,
        conn,
        params=[company_id],
    )

    conn.close()

    return df


def get_profit_loss(company_id):

    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT *
        FROM profitandloss
        WHERE company_id = ?
        ORDER BY year
        """,
        conn,
        params=[company_id],
    )

    conn.close()

    return df


def get_balance_sheet(company_id):

    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT *
        FROM balancesheet
        WHERE company_id = ?
        ORDER BY year
        """,
        conn,
        params=[company_id],
    )

    conn.close()

    return df


def get_cashflow(company_id):

    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT *
        FROM cashflow
        WHERE company_id = ?
        ORDER BY year
        """,
        conn,
        params=[company_id],
    )

    conn.close()

    return df


def get_pros_cons(company_id):

    path = "output/pros_cons_generated.csv"

    if not os.path.exists(path):
        return pd.DataFrame()

    df = pd.read_csv(path)

    return df[df["company_id"] == company_id]


def get_capital_allocation(company_id):

    path = "output/capital_allocation.csv"

    if not os.path.exists(path):
        return pd.DataFrame()

    df = pd.read_csv(path)

    df = df[df["company_id"] == company_id]

    if df.empty:
        return df

    return df.sort_values("year")


# ============================================================
# Helpers
# ============================================================


def clean_value(value, decimals=2):

    if pd.isna(value):
        return "N/A"

    try:
        return f"{float(value):,.{decimals}f}"
    except (ValueError, TypeError):
        return str(value)


def safe_number(value):

    try:

        if pd.isna(value):
            return None

        return float(value)

    except (ValueError, TypeError):

        return None


# ============================================================
# Charts
# ============================================================


def create_revenue_profit_chart(company_id, pl):

    if pl.empty:
        return None

    required = ["year", "sales", "net_profit"]

    if not all(column in pl.columns for column in required):
        return None

    df = pl[required].copy()

    df["sales"] = pd.to_numeric(df["sales"], errors="coerce")

    df["net_profit"] = pd.to_numeric(df["net_profit"], errors="coerce")

    df = df.dropna(subset=["year"])

    if df.empty:
        return None

    df = df.tail(10)

    fig, ax = plt.subplots(figsize=(7.2, 3.0))

    x = range(len(df))

    width = 0.38

    ax.bar(
        [i - width / 2 for i in x], df["sales"].fillna(0), width=width, label="Revenue"
    )

    ax.bar(
        [i + width / 2 for i in x],
        df["net_profit"].fillna(0),
        width=width,
        label="Net Profit",
    )

    ax.set_xticks(list(x))

    ax.set_xticklabels(df["year"].astype(int))

    ax.set_title("Revenue and Net Profit — 10 Years")

    ax.set_ylabel("Amount")

    ax.legend(loc="best")

    ax.grid(axis="y", alpha=0.2)

    fig.tight_layout()

    path = os.path.join(TEMP_DIR, f"{company_id}_revenue_profit.png")

    fig.savefig(path, dpi=150, bbox_inches="tight")

    plt.close(fig)

    return path


def create_roe_roce_chart(company_id, ratios, roce_value):

    if ratios.empty:
        return None

    if "year" not in ratios.columns:
        return None

    if "return_on_equity_pct" not in ratios.columns:
        return None

    df = ratios.tail(10).copy()

    df["roe"] = pd.to_numeric(df["return_on_equity_pct"], errors="coerce")

    fig, ax1 = plt.subplots(figsize=(7.2, 3.0))

    # ROE - left axis
    line1 = ax1.plot(df["year"], df["roe"], marker="o", label="ROE %")

    ax1.set_xlabel("Year")
    ax1.set_ylabel("ROE %")

    # ROCE - right axis
    ax2 = ax1.twinx()

    line2 = None

    if roce_value is not None:

        line2 = ax2.plot(
            df["year"],
            [roce_value] * len(df),
            marker="o",
            linestyle="--",
            label="ROCE %",
        )

    ax2.set_ylabel("ROCE %")

    ax1.set_title("ROE and ROCE Trend")

    # Combined legend
    lines = line1

    if line2:
        lines += line2

    labels = [line.get_label() for line in lines]

    ax1.legend(lines, labels, loc="best")

    ax1.grid(alpha=0.2)

    fig.tight_layout()

    path = os.path.join(TEMP_DIR, f"{company_id}_roe_roce.png")

    fig.savefig(path, dpi=150, bbox_inches="tight")

    plt.close(fig)

    return path


def create_balance_chart(company_id, bs):

    if bs.empty:
        return None

    required = ["year", "equity_capital", "reserves", "borrowings", "other_liabilities"]

    if not all(column in bs.columns for column in required):
        return None

    df = bs[required].copy()

    df = df.tail(10)

    for column in required[1:]:

        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)

    fig, ax = plt.subplots(figsize=(7.2, 3.0))

    ax.bar(df["year"], df["equity_capital"], label="Equity")

    ax.bar(df["year"], df["reserves"], bottom=df["equity_capital"], label="Reserves")

    bottom_2 = df["equity_capital"] + df["reserves"]

    ax.bar(df["year"], df["borrowings"], bottom=bottom_2, label="Borrowings")

    bottom_3 = bottom_2 + df["borrowings"]

    ax.bar(
        df["year"], df["other_liabilities"], bottom=bottom_3, label="Other Liabilities"
    )

    ax.set_title("Balance Sheet Composition")

    ax.set_xlabel("Year")

    ax.set_ylabel("Amount")

    ax.legend(fontsize=7)

    ax.grid(axis="y", alpha=0.2)

    fig.tight_layout()

    path = os.path.join(TEMP_DIR, f"{company_id}_balance.png")

    fig.savefig(path, dpi=150, bbox_inches="tight")

    plt.close(fig)

    return path


def create_cashflow_chart(company_id, cf):

    if cf.empty:
        return None

    required = [
        "year",
        "operating_activity",
        "investing_activity",
        "financing_activity",
    ]

    if not all(column in cf.columns for column in required):
        return None

    latest = cf.iloc[-1]

    cfo = safe_number(latest["operating_activity"])

    cfi = safe_number(latest["investing_activity"])

    cff = safe_number(latest["financing_activity"])

    cfo = 0 if cfo is None else cfo
    cfi = 0 if cfi is None else cfi
    cff = 0 if cff is None else cff

    net_cash_flow = cfo + cfi + cff

    labels = ["CFO", "CFI", "CFF", "Net Cash Flow"]

    values = [cfo, cfi, cff, net_cash_flow]

    fig, ax = plt.subplots(figsize=(7.2, 3.0))

    # Waterfall positions
    x = range(len(values))

    running = 0

    for i, value in enumerate(values):

        if i == 0 or i == len(values) - 1:

            bottom = 0

        else:

            if value >= 0:
                bottom = running
            else:
                bottom = running + value

        if i < len(values) - 1:

            ax.bar(i, abs(value), bottom=bottom)

            running += value

        else:

            ax.bar(i, value, bottom=0)

    # Connectors
    running = 0

    for i in range(len(values) - 2):

        running += values[i]

        ax.plot([i + 0.35, i + 0.65], [running, running], linestyle="--", linewidth=0.8)

    ax.axhline(0, linewidth=0.8)

    ax.set_xticks(list(x))

    ax.set_xticklabels(labels)

    ax.set_title(f"Cash Flow Waterfall — {int(latest['year'])}")

    ax.set_ylabel("Amount")

    ax.grid(axis="y", alpha=0.2)

    fig.tight_layout()

    path = os.path.join(TEMP_DIR, f"{company_id}_cashflow.png")

    fig.savefig(path, dpi=150, bbox_inches="tight")

    plt.close(fig)

    return path


# ============================================================
# PDF styles
# ============================================================

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "TitleCustom",
    parent=styles["Title"],
    fontSize=20,
    leading=23,
    alignment=TA_LEFT,
    textColor=colors.white,
)

section_style = ParagraphStyle(
    "Section",
    parent=styles["Heading2"],
    fontSize=12,
    leading=15,
    spaceBefore=5,
    spaceAfter=5,
)

body_style = ParagraphStyle(
    "BodyCustom", parent=styles["BodyText"], fontSize=8.5, leading=11, wordWrap="CJK"
)

small_style = ParagraphStyle("Small", parent=styles["BodyText"], fontSize=7, leading=9)

badge_style = ParagraphStyle(
    "Badge", parent=styles["BodyText"], fontSize=9, leading=12, alignment=TA_CENTER
)


# ============================================================
# KPI tiles
# ============================================================


def create_kpi_table(ratios, latest_ratio, roce_value):

    metrics = [
        ("ROE", latest_ratio.get("return_on_equity_pct"), "%"),
        ("ROCE", roce_value, "%"),
        ("Net Profit Margin", latest_ratio.get("net_profit_margin_pct"), "%"),
        ("D/E", latest_ratio.get("debt_to_equity"), ""),
        ("Revenue CAGR 5Y", latest_ratio.get("revenue_cagr_5yr"), "%"),
        ("FCF", latest_ratio.get("free_cash_flow_cr"), " Cr"),
    ]

    data = []

    row_1 = []
    row_2 = []

    for title, value, suffix in metrics:

        display = clean_value(value)

        if display != "N/A":
            display += suffix

        cell = Paragraph(
            f"<b>{title}</b><br/><font size=14>{display}</font>", body_style
        )

        if len(row_1) < 3:
            row_1.append(cell)
        else:
            row_2.append(cell)

    data.append(row_1)
    data.append(row_2)

    table = Table(
        data, colWidths=[58 * mm, 58 * mm, 58 * mm], rowHeights=[18 * mm, 18 * mm]
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
# Pros / Cons
# ============================================================


def create_bullet_list(df, result_type):

    if df.empty:
        return [Paragraph("No data available.", body_style)]

    rows = df[df["type"] == result_type].sort_values("confidence_pct", ascending=False)

    rows = rows.head(6)

    if rows.empty:
        return [Paragraph("No qualifying signals.", body_style)]

    output = []

    for _, row in rows.iterrows():

        text = str(row["text"])

        confidence = clean_value(row["confidence_pct"], 0)

        output.append(
            Paragraph(
                f"• {text} " f"<font size=7>" f"(confidence {confidence}%)" f"</font>",
                body_style,
            )
        )

        output.append(Spacer(1, 2))

    return output


# ============================================================
# Build PDF
# ============================================================


def build_tearsheet(company_id, output_path):

    company = get_company(company_id)
    sector_data = get_sector(company_id)
    ratios = get_ratios(company_id)

    pl = get_profit_loss(company_id)

    bs = get_balance_sheet(company_id)

    cf = get_cashflow(company_id)

    pros_cons = get_pros_cons(company_id)

    allocation = get_capital_allocation(company_id)

    if company.empty:
        raise ValueError(f"Company not found: {company_id}")

    company = company.iloc[0]
    # Get sector information
    sector_conn = get_connection()

    sector_data = pd.read_sql(
        """
        SELECT broad_sector, sub_sector
        FROM sectors
        WHERE company_id = ?
        """,
        sector_conn,
        params=[company_id],
    )

    sector_conn.close()

    if not sector_data.empty:
        broad_sector = sector_data.iloc[0]["broad_sector"]
    else:
        broad_sector = "N/A"
    latest_ratio = ratios.iloc[-1] if not ratios.empty else pd.Series(dtype="object")

    company_name = company.get("company_name", company_id)

    broad_sector = "N/A"

    if not sector_data.empty:

        broad_sector = sector_data.iloc[0]["broad_sector"]

    ticker = company_id

    # ---------------------------------------------------------
    # PDF
    # ---------------------------------------------------------

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
        title=f"{company_name} — Financial Tearsheet",
    )

    story = []

    # ---------------------------------------------------------
    # Header
    # ---------------------------------------------------------

    header = Table(
        [
            [
                Paragraph(
                    f"<b>{company_name}</b><br/>" f"<font size=10>{ticker}</font>",
                    title_style,
                )
            ]
        ],
        colWidths=[184 * mm],
        rowHeights=[24 * mm],
    )

    header.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#172554")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )

    story.append(header)

    story.append(Spacer(1, 5))

    story.append(Paragraph(f"<b>Sector:</b> {broad_sector}", body_style))

    story.append(Spacer(1, 5))

    # ---------------------------------------------------------
    # KPIs
    # ---------------------------------------------------------

    roce_value = safe_number(company.get("roce_percentage"))

    story.append(create_kpi_table(ratios, latest_ratio, roce_value))

    story.append(Spacer(1, 5))

    # ---------------------------------------------------------
    # Revenue / Profit
    # ---------------------------------------------------------

    story.append(Paragraph("Revenue & Profit Trend", section_style))

    revenue_chart = create_revenue_profit_chart(company_id, pl)

    if revenue_chart:

        story.append(Image(revenue_chart, width=180 * mm, height=75 * mm))

    else:

        story.append(Paragraph("Revenue/profit data unavailable.", body_style))

    # ---------------------------------------------------------
    # ROE / ROCE
    # ---------------------------------------------------------

    story.append(Paragraph("Return Trend", section_style))

    roce_value = safe_number(company.get("roce_percentage"))

    roe_chart = create_roe_roce_chart(company_id, ratios, roce_value)

    if roe_chart:

        story.append(Image(roe_chart, width=180 * mm, height=70 * mm))

    else:

        story.append(Paragraph("ROE/ROCE data unavailable.", body_style))

    # ---------------------------------------------------------
    # Page 2
    # ---------------------------------------------------------

    story.append(PageBreak())

    story.append(Paragraph("Financial Structure & Cash Flow", section_style))

    balance_chart = create_balance_chart(company_id, bs)

    if balance_chart:

        story.append(Image(balance_chart, width=180 * mm, height=68 * mm))

    else:

        story.append(Paragraph("Balance-sheet data unavailable.", body_style))

    story.append(Spacer(1, 3))

    cashflow_chart = create_cashflow_chart(company_id, cf)

    if cashflow_chart:

        story.append(Image(cashflow_chart, width=180 * mm, height=63 * mm))

    else:

        story.append(Paragraph("Cash-flow data unavailable.", body_style))

    # ---------------------------------------------------------
    # Capital allocation
    # ---------------------------------------------------------

    allocation_label = "Insufficient Data"

    if not allocation.empty:

        allocation_label = str(allocation.iloc[-1]["pattern_label"])

    story.append(Spacer(1, 3))

    allocation_table = Table(
        [
            [
                Paragraph("<b>Capital Allocation</b>", badge_style),
                Paragraph(allocation_label, badge_style),
            ]
        ],
        colWidths=[70 * mm, 110 * mm],
    )

    allocation_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    story.append(allocation_table)

    # ---------------------------------------------------------
    # Pros / Cons
    # ---------------------------------------------------------

    story.append(Spacer(1, 4))

    story.append(Paragraph("Pros", section_style))

    story.extend(create_bullet_list(pros_cons, "pro"))

    story.append(Paragraph("Cons", section_style))

    story.extend(create_bullet_list(pros_cons, "con"))

    # ---------------------------------------------------------
    # Build
    # ---------------------------------------------------------

    doc.build(story)

    return output_path


# ============================================================
# Test
# ============================================================

if __name__ == "__main__":

    test_company = "TATASTEEL"

    output = os.path.join(OUTPUT_DIR, f"{test_company}_tearsheet.pdf")

    path = build_tearsheet(test_company, output)

    print("Tearsheet generated:")

    print(path)
