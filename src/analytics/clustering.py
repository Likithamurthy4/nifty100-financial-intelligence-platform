"""
Day 37 - Cluster Profiling & Portfolio Statistics

Generates:

1. Cluster profile statistics
   - Mean and median of the 5 clustering features
2. Correlation heatmap
   - Pearson correlation of 10 latest-year KPIs
3. Outlier report
   - Sector-wise Z-score > 3
4. Portfolio statistics
   - P10, P25, P50, P75, P90, Mean, Std
"""

from pathlib import Path
import sqlite3

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import zscore


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

DB_PATH = ROOT / "db" / "nifty100.db"
OUTPUT_DIR = ROOT / "output"
REPORTS_DIR = ROOT / "reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# CLUSTERING FEATURES
# ============================================================

CLUSTER_FEATURES = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "fcf_cagr_5yr",
    "operating_profit_margin_pct",
]


# ============================================================
# 10 CORE KPIs
# ============================================================

CORE_KPIS = [
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "return_on_equity_pct",
    "debt_to_equity",
    "interest_coverage",
    "asset_turnover",
    "free_cash_flow_cr",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "eps_cagr_5yr",
]


# ============================================================
# DATABASE
# ============================================================

def load_data():
    conn = sqlite3.connect(DB_PATH)

    ratios = pd.read_sql_query(
        """
        SELECT
            company_id,
            year,
            net_profit_margin_pct,
            operating_profit_margin_pct,
            return_on_equity_pct,
            debt_to_equity,
            interest_coverage,
            asset_turnover,
            free_cash_flow_cr,
            revenue_cagr_5yr,
            pat_cagr_5yr,
            eps_cagr_5yr
        FROM financial_ratios
        WHERE year IS NOT NULL
        """,
        conn,
    )

    sectors = pd.read_sql_query(
        """
        SELECT
            company_id,
            broad_sector,
            sub_sector
        FROM sectors
        """,
        conn,
    )

    companies = pd.read_sql_query(
        """
        SELECT
            id AS company_id,
            company_name,
            roe_percentage,
            roce_percentage
        FROM companies
        """,
        conn,
    )

    clusters_path = OUTPUT_DIR / "cluster_labels.csv"

    clusters = pd.read_csv(clusters_path)

    conn.close()

        # Calculate 5-year FCF CAGR from annual free cash flow
    fcf = ratios[
        [
            "company_id",
            "year",
            "free_cash_flow_cr",
        ]
    ].copy()

    fcf = fcf.dropna(
        subset=["company_id", "year"]
    )

    fcf = fcf.sort_values(
        ["company_id", "year"]
    )

    def calculate_fcf_cagr(group):
        group = group.sort_values("year").copy()

        if len(group) < 6:
            return np.nan

        latest = group.iloc[-1]
        five_years_ago = group.iloc[-6]

        start = five_years_ago["free_cash_flow_cr"]
        end = latest["free_cash_flow_cr"]

        # CAGR is not meaningful when either endpoint is
        # zero or negative.
        if pd.isna(start) or pd.isna(end):
            return np.nan

        if start <= 0 or end <= 0:
            return np.nan

        return (
            ((end / start) ** (1 / 5)) - 1
        ) * 100

    fcf_cagr = (
        fcf.groupby("company_id")
        .apply(
            calculate_fcf_cagr,
            include_groups=False,
        )
        .reset_index(
            name="fcf_cagr_5yr"
        )
    )

    ratios = ratios.merge(
        fcf_cagr,
        on="company_id",
        how="left",
    )
    return ratios, sectors, companies, clusters


# ============================================================
# LATEST YEAR DATA
# ============================================================
def build_latest_year_dataset(ratios, sectors, companies):
    """
    Select latest available ratio year per company and
    attach sector/company information.

    FCF CAGR is calculated from the annual
    free_cash_flow_cr values.
    """

    ratios = ratios.copy()

    # Ensure numeric values
    ratios["year"] = pd.to_numeric(
        ratios["year"],
        errors="coerce",
    )

    ratios["free_cash_flow_cr"] = pd.to_numeric(
        ratios["free_cash_flow_cr"],
        errors="coerce",
    )

    # Sort chronologically
    ratios = ratios.sort_values(
        ["company_id", "year"]
    )

    # --------------------------------------------------------
    # Calculate 5-year FCF CAGR
    # --------------------------------------------------------

    ratios["fcf_5yr_ago"] = (
        ratios
        .groupby("company_id")["free_cash_flow_cr"]
        .shift(5)
    )

    valid_fcf = (
        ratios["free_cash_flow_cr"].notna()
        & ratios["fcf_5yr_ago"].notna()
        & (ratios["free_cash_flow_cr"] > 0)
        & (ratios["fcf_5yr_ago"] > 0)
    )

    ratios["fcf_cagr_5yr"] = np.nan

    ratios.loc[valid_fcf, "fcf_cagr_5yr"] = (
        (
            ratios.loc[valid_fcf, "free_cash_flow_cr"]
            / ratios.loc[valid_fcf, "fcf_5yr_ago"]
        ) ** (1 / 5) - 1
    ) * 100

    # Remove helper column
    ratios = ratios.drop(
        columns=["fcf_5yr_ago"]
    )

    # --------------------------------------------------------
    # Latest available year per company
    # --------------------------------------------------------

    latest = (
        ratios
        .dropna(subset=["year"])
        .groupby(
            "company_id",
            as_index=False,
        )
        .tail(1)
        .copy()
    )

    # --------------------------------------------------------
    # Attach company information
    # --------------------------------------------------------

    latest = latest.merge(
        companies,
        on="company_id",
        how="right",
    )

    # --------------------------------------------------------
    # Attach sector information
    # --------------------------------------------------------

    latest = latest.merge(
        sectors[
            [
                "company_id",
                "broad_sector",
                "sub_sector",
            ]
        ],
        on="company_id",
        how="left",
    )

    return latest
# ============================================================
# SECTOR MEDIAN IMPUTATION
# ============================================================

def sector_median_imputation(df, columns):
    """
    Fill missing values using broad-sector medians.

    Overall median is the final fallback.
    """

    result = df.copy()

    for column in columns:

        result[column] = pd.to_numeric(
            result[column],
            errors="coerce",
        )

        sector_median = (
            result
            .groupby("broad_sector")[column]
            .transform("median")
        )

        result[column] = (
            result[column]
            .fillna(sector_median)
        )

        result[column] = (
            result[column]
            .fillna(result[column].median())
        )

    return result


# ============================================================
# CLUSTER PROFILES
# ============================================================

def generate_cluster_profiles(latest):
    """
    Generate mean and median values for each cluster.

    Uses cluster_labels.csv.
    """

    cluster_path = OUTPUT_DIR / "cluster_labels.csv"

    clusters = pd.read_csv(cluster_path)

    df = latest.merge(
        clusters[
            [
                "company_id",
                "cluster_id",
                "cluster_name",
            ]
        ],
        on="company_id",
        how="left",
    )

    df = sector_median_imputation(
        df,
        CLUSTER_FEATURES,
    )

    mean_profile = (
        df
        .groupby(
            [
                "cluster_id",
                "cluster_name",
            ]
        )[CLUSTER_FEATURES]
        .mean()
        .reset_index()
    )

    median_profile = (
        df
        .groupby(
            [
                "cluster_id",
                "cluster_name",
            ]
        )[CLUSTER_FEATURES]
        .median()
        .reset_index()
    )

    mean_profile["statistic"] = "mean"
    median_profile["statistic"] = "median"

    profile = pd.concat(
        [
            mean_profile,
            median_profile,
        ],
        ignore_index=True,
    )

    profile = profile[
        [
            "cluster_id",
            "cluster_name",
            "statistic",
        ]
        + CLUSTER_FEATURES
    ]

    profile = profile.sort_values(
        [
            "cluster_id",
            "statistic",
        ]
    )

    output_path = (
        OUTPUT_DIR / "cluster_profiles.csv"
    )

    profile.to_csv(
        output_path,
        index=False,
    )

    print(
        f"Saved cluster profiles: {output_path}"
    )

    return df, profile


# ============================================================
# CORRELATION HEATMAP
# ============================================================

def generate_correlation_heatmap(latest):
    """
    Generate Pearson correlation matrix for
    10 core KPIs across all 92 companies.
    """

    df = latest.copy()

    df = sector_median_imputation(
        df,
        CORE_KPIS,
    )

    correlation = df[
        CORE_KPIS
    ].corr(
        method="pearson"
    )

    print("\nCorrelation matrix:")
    print(correlation.round(3))

    plt.figure(
        figsize=(14, 11)
    )

    sns.heatmap(
        correlation,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        square=True,
        linewidths=0.5,
        cbar_kws={
            "label": "Pearson Correlation"
        },
    )

    plt.title(
        "Nifty 100 Financial KPI Correlation Matrix"
    )

    plt.tight_layout()

    output_path = (
        REPORTS_DIR
        / "correlation_heatmap.png"
    )

    plt.savefig(
        output_path,
        dpi=180,
        bbox_inches="tight",
    )

    plt.close()

    print(
        f"Saved correlation heatmap: {output_path}"
    )

    return correlation


# ============================================================
# OUTLIER DETECTION
# ============================================================

def generate_outlier_report(latest):
    """
    Calculate sector-wise Z-scores.

    Flag companies where:
        abs(Z-score) > 3
    """

    df = latest.copy()

    records = []

    for metric in CORE_KPIS:

        df[metric] = pd.to_numeric(
            df[metric],
            errors="coerce",
        )

        for sector, group in df.groupby(
            "broad_sector",
            dropna=False,
        ):

            group = group.copy()

            values = group[metric]

            sector_mean = values.mean()
            sector_std = values.std(ddof=0)

            if pd.isna(sector_std) or sector_std == 0:
                continue

            group["z_score"] = (
                values - sector_mean
            ) / sector_std

            outliers = group[
                group["z_score"].abs() > 3
            ]

            for _, row in outliers.iterrows():

                records.append(
                    {
                        "company_id": row[
                            "company_id"
                        ],
                        "metric": metric,
                        "value": row[metric],
                        "z_score": row[
                            "z_score"
                        ],
                        "sector": sector,
                        "sector_mean": sector_mean,
                        "sector_std": sector_std,
                    }
                )

    columns = [
        "company_id",
        "metric",
        "value",
        "z_score",
        "sector",
        "sector_mean",
        "sector_std",
    ]

    report = pd.DataFrame(
        records,
        columns=columns,
    )

    if not report.empty:
        report = report.sort_values(
            "z_score",
            key=lambda x: x.abs(),
            ascending=False,
        )

    output_path = (
        OUTPUT_DIR / "outlier_report.csv"
    )

    report.to_csv(
        output_path,
        index=False,
    )

    print(
        f"\nOutliers detected: {len(report)}"
    )

    print(
        f"Saved outlier report: {output_path}"
    )

    return report


# ============================================================
# PORTFOLIO STATISTICS
# ============================================================

def generate_portfolio_stats(latest):
    """
    Generate P10, P25, P50, P75, P90,
    Mean and Std for all 10 KPIs.
    """

    df = latest.copy()

    df = sector_median_imputation(
        df,
        CORE_KPIS,
    )

    records = []

    for metric in CORE_KPIS:

        values = pd.to_numeric(
            df[metric],
            errors="coerce",
        ).dropna()

        records.append(
            {
                "metric": metric,
                "P10": values.quantile(0.10),
                "P25": values.quantile(0.25),
                "P50": values.quantile(0.50),
                "P75": values.quantile(0.75),
                "P90": values.quantile(0.90),
                "Mean": values.mean(),
                "Std": values.std(),
            }
        )

    stats = pd.DataFrame(
        records
    )

    output_path = (
        OUTPUT_DIR / "portfolio_stats.csv"
    )

    stats.to_csv(
        output_path,
        index=False,
    )

    print(
        f"Saved portfolio statistics: {output_path}"
    )

    return stats


# ============================================================
# MAIN
# ============================================================

def run_day37():

    print("=" * 65)
    print("DAY 37 - CLUSTER PROFILING & STATISTICS")
    print("=" * 65)

    ratios, sectors, companies, clusters = (
        load_data()
    )

    print(
        f"Companies in database: "
        f"{companies['company_id'].nunique()}"
    )

    latest = build_latest_year_dataset(
        ratios,
        sectors,
        companies,
    )

    print(
        f"Latest-year company rows: "
        f"{latest['company_id'].nunique()}"
    )

    if latest["company_id"].nunique() != 92:
        raise ValueError(
            "Expected 92 companies in latest-year dataset."
        )

    # --------------------------------------------------------
    # Cluster profiling
    # --------------------------------------------------------

    print("\n" + "=" * 65)
    print("1. CLUSTER PROFILES")
    print("=" * 65)

    cluster_data, profiles = (
        generate_cluster_profiles(
            latest
        )
    )

    print(
        profiles.to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # Correlation heatmap
    # --------------------------------------------------------

    print("\n" + "=" * 65)
    print("2. CORRELATION HEATMAP")
    print("=" * 65)

    correlation = (
        generate_correlation_heatmap(
            latest
        )
    )

    # --------------------------------------------------------
    # Outlier report
    # --------------------------------------------------------

    print("\n" + "=" * 65)
    print("3. OUTLIER DETECTION")
    print("=" * 65)

    outliers = generate_outlier_report(
        latest
    )

    # --------------------------------------------------------
    # Portfolio statistics
    # --------------------------------------------------------

    print("\n" + "=" * 65)
    print("4. PORTFOLIO STATISTICS")
    print("=" * 65)

    stats = generate_portfolio_stats(
        latest
    )

    print("\nPortfolio statistics:")
    print(
        stats.to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # Final QA
    # --------------------------------------------------------

    print("\n" + "=" * 65)
    print("DAY 37 FINAL QA")
    print("=" * 65)

    print(
        "Companies:",
        latest["company_id"].nunique(),
    )

    print(
        "Clusters:",
        cluster_data["cluster_id"]
        .nunique(),
    )

    print(
        "Cluster profiles:",
        len(profiles),
    )

    print(
        "Correlation KPIs:",
        len(CORE_KPIS),
    )

    print(
        "Correlation matrix shape:",
        correlation.shape,
    )

    print(
        "Outlier rows:",
        len(outliers),
    )

    print(
        "Portfolio statistic rows:",
        len(stats),
    )

    # --------------------------------------------------------
    # Hard checks
    # --------------------------------------------------------

    if latest["company_id"].nunique() != 92:
        raise ValueError(
            "Day 37 requires all 92 companies."
        )

    if cluster_data["cluster_id"].nunique() != 5:
        raise ValueError(
            "Expected exactly 5 clusters."
        )

    if len(profiles) != 10:
        raise ValueError(
            "Expected 5 clusters × 2 statistics."
        )

    if correlation.shape != (10, 10):
        raise ValueError(
            "Correlation matrix must be 10 × 10."
        )

    if len(stats) != 10:
        raise ValueError(
            "Expected portfolio statistics for 10 KPIs."
        )

    required_outputs = [
        OUTPUT_DIR / "cluster_profiles.csv",
        OUTPUT_DIR / "outlier_report.csv",
        OUTPUT_DIR / "portfolio_stats.csv",
        REPORTS_DIR / "correlation_heatmap.png",
    ]

    for path in required_outputs:

        if not path.exists():
            raise FileNotFoundError(
                f"Missing required output: {path}"
            )

        if path.stat().st_size == 0:
            raise ValueError(
                f"Output is empty: {path}"
            )

    print("\n" + "=" * 65)
    print("DAY 37 COMPLETED SUCCESSFULLY")
    print("=" * 65)

    for path in required_outputs:
        print(f"PASS: {path}")


if __name__ == "__main__":
    run_day37()