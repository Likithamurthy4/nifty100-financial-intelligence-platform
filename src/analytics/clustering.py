"""
Day 36 - KMeans Financial Clustering

Clusters all 92 companies into 5 financial archetypes using:
    - Return on Equity (%)
    - Debt to Equity
    - Revenue CAGR (5Y)
    - Free Cash Flow CAGR (5Y)
    - Operating Profit Margin (%)

Missing values are imputed using broad-sector medians.

Pipeline:
    1. Start from all companies
    2. Build features from available source data
    3. Impute missing values using sector medians
    4. StandardScaler
    5. KMeans with 5 clusters, random_state=42
    6. Generate elbow plot
    7. Generate cluster_labels.csv
"""

import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

DB_PATH = ROOT / "db" / "nifty100.db"
OUTPUT_DIR = ROOT / "output"
REPORTS_DIR = ROOT / "reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


FEATURES = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "fcf_cagr_5yr",
    "operating_profit_margin_pct",
]


# ============================================================
# DATABASE
# ============================================================


def get_connection():
    """Return a SQLite connection to the project database."""
    return sqlite3.connect(DB_PATH)


def load_source_data():
    """Load all source data required for clustering."""

    conn = get_connection()

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

    ratios = pd.read_sql_query(
        """
        SELECT
            company_id,
            year,
            return_on_equity_pct,
            debt_to_equity,
            revenue_cagr_5yr,
            operating_profit_margin_pct,
            free_cash_flow_cr
        FROM financial_ratios
        """,
        conn,
    )

    pnl = pd.read_sql_query(
        """
        SELECT
            company_id,
            year,
            sales,
            operating_profit
        FROM profitandloss
        WHERE year IS NOT NULL
        """,
        conn,
    )

    balance = pd.read_sql_query(
        """
        SELECT
            company_id,
            year,
            equity_capital,
            reserves,
            borrowings
        FROM balancesheet
        WHERE year IS NOT NULL
        """,
        conn,
    )

    cashflow = pd.read_sql_query(
        """
        SELECT
            company_id,
            year,
            operating_activity,
            investing_activity
        FROM cashflow
        WHERE year IS NOT NULL
        """,
        conn,
    )

    conn.close()

    return (
        companies,
        sectors,
        ratios,
        pnl,
        balance,
        cashflow,
    )


# ============================================================
# CAGR HELPERS
# ============================================================


def calculate_cagr(start_value, end_value, years):
    """Calculate CAGR percentage when values support a valid CAGR."""

    if pd.isna(start_value) or pd.isna(end_value):
        return np.nan

    if years <= 0:
        return np.nan

    if start_value <= 0 or end_value <= 0:
        return np.nan

    return ((end_value / start_value) ** (1 / years) - 1) * 100


def calculate_revenue_cagr(pnl):
    """Calculate five-year revenue CAGR from P&L history."""

    results = []

    for company_id, group in pnl.groupby("company_id"):

        group = group[group["sales"].notna() & (group["sales"] > 0)].sort_values("year")

        if len(group) < 2:
            results.append(
                {
                    "company_id": company_id,
                    "revenue_cagr_5yr_derived": np.nan,
                }
            )
            continue

        latest = group.iloc[-1]
        target_year = latest["year"] - 5

        historical = group[group["year"] <= target_year]

        if historical.empty:
            results.append(
                {
                    "company_id": company_id,
                    "revenue_cagr_5yr_derived": np.nan,
                }
            )
            continue

        start = historical.iloc[-1]

        cagr = calculate_cagr(
            start["sales"],
            latest["sales"],
            latest["year"] - start["year"],
        )

        results.append(
            {
                "company_id": company_id,
                "revenue_cagr_5yr_derived": cagr,
            }
        )

    return pd.DataFrame(results)


def calculate_fcf_history(cashflow):
    """Calculate free cash flow from cash-flow history."""

    df = cashflow.copy()

    df["free_cash_flow_cr_derived"] = pd.to_numeric(
        df["operating_activity"],
        errors="coerce",
    ) + pd.to_numeric(
        df["investing_activity"],
        errors="coerce",
    )

    return df


def calculate_fcf_cagr(cashflow):
    """Calculate five-year FCF CAGR from cash-flow history."""

    fcf = calculate_fcf_history(cashflow)

    results = []

    for company_id, group in fcf.groupby("company_id"):

        group = group[group["free_cash_flow_cr_derived"].notna()].sort_values("year")

        if len(group) < 2:
            results.append(
                {
                    "company_id": company_id,
                    "fcf_cagr_5yr_derived": np.nan,
                }
            )
            continue

        latest = group.iloc[-1]
        target_year = latest["year"] - 5

        historical = group[group["year"] <= target_year]

        if historical.empty:
            results.append(
                {
                    "company_id": company_id,
                    "fcf_cagr_5yr_derived": np.nan,
                }
            )
            continue

        start = historical.iloc[-1]

        cagr = calculate_cagr(
            start["free_cash_flow_cr_derived"],
            latest["free_cash_flow_cr_derived"],
            latest["year"] - start["year"],
        )

        results.append(
            {
                "company_id": company_id,
                "fcf_cagr_5yr_derived": cagr,
            }
        )

    return pd.DataFrame(results)


# ============================================================
# FEATURE BUILDING
# ============================================================


def calculate_debt_to_equity(balance):
    """Calculate D/E from balance sheet."""

    df = balance.copy()

    df["equity_base"] = pd.to_numeric(
        df["equity_capital"],
        errors="coerce",
    ) + pd.to_numeric(
        df["reserves"],
        errors="coerce",
    )

    df["debt_to_equity_derived"] = np.where(
        df["equity_base"] > 0,
        df["borrowings"] / df["equity_base"],
        np.nan,
    )

    latest = df.sort_values("year").groupby("company_id", as_index=False).tail(1)

    return latest[
        [
            "company_id",
            "debt_to_equity_derived",
        ]
    ]


def calculate_latest_opm(pnl):
    """Calculate latest operating profit margin from P&L."""

    df = pnl.copy()

    df["sales"] = pd.to_numeric(
        df["sales"],
        errors="coerce",
    )

    df["operating_profit"] = pd.to_numeric(
        df["operating_profit"],
        errors="coerce",
    )

    df["opm_derived"] = np.where(
        df["sales"] != 0,
        (df["operating_profit"] / df["sales"]) * 100,
        np.nan,
    )

    latest = df.sort_values("year").groupby("company_id", as_index=False).tail(1)

    return latest[
        [
            "company_id",
            "opm_derived",
        ]
    ]


def build_feature_dataset():
    """Build the complete 92-company clustering dataset."""

    (
        companies,
        sectors,
        ratios,
        pnl,
        balance,
        cashflow,
    ) = load_source_data()

    # --------------------------------------------------------
    # Start from ALL companies.
    # This is critical because financial_ratios only has 90.
    # --------------------------------------------------------

    df = companies[
        [
            "company_id",
            "company_name",
            "roe_percentage",
        ]
    ].copy()

    df = df.merge(
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

    # --------------------------------------------------------
    # Latest financial ratio record where available
    # --------------------------------------------------------

    ratios = ratios.sort_values("year")

    latest_ratios = ratios.groupby("company_id", as_index=False).tail(1).copy()

    latest_ratios = latest_ratios[
        [
            "company_id",
            "return_on_equity_pct",
            "debt_to_equity",
            "revenue_cagr_5yr",
            "operating_profit_margin_pct",
        ]
    ]

    df = df.merge(
        latest_ratios,
        on="company_id",
        how="left",
    )

    # --------------------------------------------------------
    # ROE fallback from companies table
    # --------------------------------------------------------

    df["return_on_equity_pct"] = df["return_on_equity_pct"].fillna(df["roe_percentage"])

    # --------------------------------------------------------
    # Derived revenue CAGR
    # --------------------------------------------------------

    revenue_cagr = calculate_revenue_cagr(pnl)

    df = df.merge(
        revenue_cagr,
        on="company_id",
        how="left",
    )

    df["revenue_cagr_5yr"] = df["revenue_cagr_5yr"].fillna(
        df["revenue_cagr_5yr_derived"]
    )

    df.drop(
        columns=["revenue_cagr_5yr_derived"],
        inplace=True,
    )

    # --------------------------------------------------------
    # Derived D/E
    # --------------------------------------------------------

    de = calculate_debt_to_equity(balance)

    df = df.merge(
        de,
        on="company_id",
        how="left",
    )

    df["debt_to_equity"] = df["debt_to_equity"].fillna(df["debt_to_equity_derived"])

    df.drop(
        columns=["debt_to_equity_derived"],
        inplace=True,
    )

    # --------------------------------------------------------
    # Derived OPM
    # --------------------------------------------------------

    opm = calculate_latest_opm(pnl)

    df = df.merge(
        opm,
        on="company_id",
        how="left",
    )

    df["operating_profit_margin_pct"] = df["operating_profit_margin_pct"].fillna(
        df["opm_derived"]
    )

    df.drop(
        columns=["opm_derived"],
        inplace=True,
    )

    # --------------------------------------------------------
    # FCF CAGR
    # --------------------------------------------------------

    existing_fcf = calculate_existing_fcf_cagr(ratios)

    derived_fcf = calculate_fcf_cagr(cashflow)

    df = df.merge(
        existing_fcf,
        on="company_id",
        how="left",
    )

    df = df.merge(
        derived_fcf,
        on="company_id",
        how="left",
    )

    df["fcf_cagr_5yr"] = df["fcf_cagr_5yr_existing"].fillna(df["fcf_cagr_5yr_derived"])

    df.drop(
        columns=[
            "fcf_cagr_5yr_existing",
            "fcf_cagr_5yr_derived",
        ],
        inplace=True,
    )

    return df


def calculate_existing_fcf_cagr(ratios):
    """Calculate FCF CAGR from existing financial-ratio history."""

    results = []

    for company_id, group in ratios.groupby("company_id"):

        group = group[group["free_cash_flow_cr"].notna()].sort_values("year")

        if len(group) < 2:
            results.append(
                {
                    "company_id": company_id,
                    "fcf_cagr_5yr_existing": np.nan,
                }
            )
            continue

        latest = group.iloc[-1]

        target_year = latest["year"] - 5

        historical = group[group["year"] <= target_year]

        if historical.empty:
            results.append(
                {
                    "company_id": company_id,
                    "fcf_cagr_5yr_existing": np.nan,
                }
            )
            continue

        start = historical.iloc[-1]

        cagr = calculate_cagr(
            start["free_cash_flow_cr"],
            latest["free_cash_flow_cr"],
            latest["year"] - start["year"],
        )

        results.append(
            {
                "company_id": company_id,
                "fcf_cagr_5yr_existing": cagr,
            }
        )

    return pd.DataFrame(results)


# ============================================================
# SECTOR MEDIAN IMPUTATION
# ============================================================


def impute_sector_medians(df):
    """Impute missing feature values using broad-sector medians."""

    result = df.copy()

    print("\n=== MISSING VALUES BEFORE IMPUTATION ===")
    print(result[FEATURES].isna().sum())

    for feature in FEATURES:

        result[feature] = pd.to_numeric(
            result[feature],
            errors="coerce",
        )

        sector_median = result.groupby("broad_sector")[feature].transform("median")

        result[feature] = result[feature].fillna(sector_median)

        result[feature] = result[feature].fillna(result[feature].median())

    print("\n=== MISSING VALUES AFTER IMPUTATION ===")
    print(result[FEATURES].isna().sum())

    return result


# ============================================================
# ELBOW PLOT
# ============================================================


def generate_elbow_plot(X_scaled):
    """Generate elbow plot for k=2 through k=10."""

    inertias = []
    k_values = range(2, 11)

    for k in k_values:

        model = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=20,
        )

        model.fit(X_scaled)
        inertias.append(model.inertia_)

    plt.figure(figsize=(9, 6))

    plt.plot(
        list(k_values),
        inertias,
        marker="o",
    )

    plt.xlabel("Number of Clusters (k)")
    plt.ylabel("Inertia")
    plt.title("KMeans Elbow Plot")

    plt.xticks(list(k_values))
    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    output_path = REPORTS_DIR / "elbow_plot.png"

    plt.savefig(
        output_path,
        dpi=160,
        bbox_inches="tight",
    )

    plt.close()

    return output_path


# ============================================================
# CLUSTER NAMING
# ============================================================


def assign_cluster_names(profile):
    """Assign descriptive financial archetype names."""

    p = profile.copy()

    roe_rank = p["return_on_equity_pct"].rank(pct=True)
    opm_rank = p["operating_profit_margin_pct"].rank(pct=True)
    revenue_rank = p["revenue_cagr_5yr"].rank(pct=True)
    fcf_rank = p["fcf_cagr_5yr"].rank(pct=True)

    leverage_rank = 1 - p["debt_to_equity"].rank(pct=True)

    quality = roe_rank + opm_rank + leverage_rank

    growth = revenue_rank + fcf_rank

    overall = quality + growth

    names = {}

    high_quality = overall.idxmax()
    names[high_quality] = "High-Quality Compounders"

    remaining = list(set(p.index) - {high_quality})

    growth_cluster = (
        p.loc[remaining, "revenue_cagr_5yr"].rank(pct=True)
        + p.loc[remaining, "fcf_cagr_5yr"].rank(pct=True)
    ).idxmax()

    names[growth_cluster] = "Emerging Growth"

    remaining.remove(growth_cluster)

    defensive_cluster = (1 - p.loc[remaining, "debt_to_equity"].rank(pct=True)).idxmax()

    names[defensive_cluster] = "Defensive Dividend Payers"

    remaining.remove(defensive_cluster)

    distressed_cluster = overall.loc[remaining].idxmin()

    names[distressed_cluster] = "Distressed or Turnaround"

    remaining.remove(distressed_cluster)

    for cluster_id in remaining:
        names[cluster_id] = "Value Cyclicals"

    return names


# ============================================================
# MAIN CLUSTERING PIPELINE
# ============================================================


def run_clustering():
    """Run the complete Day 36 clustering pipeline."""

    print("=" * 60)
    print("DAY 36 - KMEANS FINANCIAL CLUSTERING")
    print("=" * 60)

    # --------------------------------------------------------
    # Build 92-company feature dataset
    # --------------------------------------------------------

    df = build_feature_dataset()

    print(f"Companies prepared: " f"{df['company_id'].nunique()}")

    # --------------------------------------------------------
    # HARD QA: must contain all 92 companies
    # --------------------------------------------------------

    if len(df) != 92:
        raise ValueError(f"Expected 92 companies, found {len(df)}")

    if df["company_id"].nunique() != 92:
        raise ValueError("Company IDs are not unique.")

    # --------------------------------------------------------
    # Sector median imputation
    # --------------------------------------------------------

    df = impute_sector_medians(df)

    if df[FEATURES].isna().any().any():

        missing = df[df[FEATURES].isna().any(axis=1)][["company_id"] + FEATURES]

        print("\nCompanies still containing missing values:")
        print(missing)

        raise ValueError("Missing values remain after imputation.")

    # --------------------------------------------------------
    # Prepare feature matrix
    # --------------------------------------------------------

    X = df[FEATURES].astype(float)

    # --------------------------------------------------------
    # StandardScaler
    # --------------------------------------------------------

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(X)

    print("\nFeatures standardized successfully.")

    # --------------------------------------------------------
    # Elbow plot
    # --------------------------------------------------------

    print("\nGenerating elbow plot...")

    elbow_path = generate_elbow_plot(X_scaled)

    print(f"Saved: {elbow_path}")

    # --------------------------------------------------------
    # KMeans
    # --------------------------------------------------------

    model = KMeans(
        n_clusters=5,
        random_state=42,
        n_init=20,
    )

    cluster_ids = model.fit_predict(X_scaled)

    df["cluster_id"] = cluster_ids

    # --------------------------------------------------------
    # Distance from centroid
    # --------------------------------------------------------

    distances = model.transform(X_scaled)

    df["distance_from_centroid"] = distances[
        np.arange(len(df)),
        cluster_ids,
    ]

    # --------------------------------------------------------
    # Cluster profiles
    # --------------------------------------------------------

    profile = df.groupby("cluster_id")[FEATURES].median()

    # --------------------------------------------------------
    # Cluster names
    # --------------------------------------------------------

    cluster_names = assign_cluster_names(profile)

    df["cluster_name"] = df["cluster_id"].map(cluster_names)

    # --------------------------------------------------------
    # Final output
    # --------------------------------------------------------

    output = df[
        [
            "company_id",
            "cluster_id",
            "cluster_name",
            "distance_from_centroid",
        ]
    ].sort_values("company_id")

    output_path = OUTPUT_DIR / "cluster_labels.csv"

    output.to_csv(
        output_path,
        index=False,
    )

    # --------------------------------------------------------
    # QA
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("CLUSTER DISTRIBUTION")
    print("=" * 60)

    print(output["cluster_name"].value_counts())

    print("\n" + "=" * 60)
    print("CLUSTER PROFILES")
    print("=" * 60)

    print(profile)

    print("\n" + "=" * 60)
    print("FINAL QA")
    print("=" * 60)

    print(f"Rows: {len(output)}")

    print(f"Unique companies: " f"{output['company_id'].nunique()}")

    print(f"Unique clusters: " f"{output['cluster_id'].nunique()}")

    print(
        "Missing cluster IDs:",
        output["cluster_id"].isna().sum(),
    )

    print(
        "Missing cluster names:",
        output["cluster_name"].isna().sum(),
    )

    print(
        "Missing distances:",
        output["distance_from_centroid"].isna().sum(),
    )

    # --------------------------------------------------------
    # Hard acceptance checks
    # --------------------------------------------------------

    if len(output) != 92:
        raise ValueError("Output must contain exactly 92 rows.")

    if output["company_id"].nunique() != 92:
        raise ValueError("Output must contain 92 unique companies.")

    if output["cluster_id"].nunique() != 5:
        raise ValueError("Expected exactly 5 clusters.")

    if output["cluster_id"].isna().any():
        raise ValueError("Some companies have no cluster ID.")

    if output["cluster_name"].isna().any():
        raise ValueError("Some companies have no cluster name.")

    if output["distance_from_centroid"].isna().any():

        raise ValueError("Some companies have no centroid distance.")

    print(f"\nSaved: {output_path}")

    print(f"Saved: {elbow_path}")

    print("\nDay 36 completed successfully.")


if __name__ == "__main__":
    run_clustering()
