from screener.engine import ScreenerEngine

engine = ScreenerEngine()

result = engine.apply_filters("quality_compounder")

print("\n")
print("=" * 70)
print("QUALITY COMPOUNDER")
print("=" * 70)

print(
    result[
        [
            "company_name",
            "return_on_equity_pct",
            "debt_to_equity",
            "free_cash_flow_cr",
            "revenue_cagr_5yr",
            "composite_quality_score",
        ]
    ].head(20)
)

print("\nCompanies Returned :", len(result))
