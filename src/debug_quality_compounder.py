from screener.loader import ScreenerLoader

loader = ScreenerLoader()
df = loader.load_master_dataframe()
loader.close()

print("Total rows:", len(df))

print("\nROE >= 15")
df1 = df[df["return_on_equity_pct"] >= 15]
print(len(df1))

print("\nROE + D/E")
financials = df1["broad_sector"].fillna("").str.lower() == "financials"
non_financial = df1["debt_to_equity"] <= 1
df2 = df1[financials | non_financial]
print(len(df2))

print("\n+ FCF > 0")
df3 = df2[df2["free_cash_flow_cr"] > 0]
print(len(df3))

print("\n+ Revenue CAGR > 10")
df4 = df3[df3["revenue_cagr_5yr"] > 10]
print(len(df4))

print(
    df4[
        [
            "company_name",
            "return_on_equity_pct",
            "debt_to_equity",
            "free_cash_flow_cr",
            "revenue_cagr_5yr",
        ]
    ].head(20)
)
print("\nRevenue CAGR Statistics")
print(df["revenue_cagr_5yr"].describe())

print("\nUnique Revenue CAGR Values")
print(df["revenue_cagr_5yr"].value_counts(dropna=False).head(20))
