from screener.engine import ScreenerEngine

engine = ScreenerEngine()

presets = [
    "quality_compounder",
    "value_pick",
    "growth_accelerator",
    "dividend_champion",
    "debt_free_blue_chip",
    "turnaround_watch",
]

for preset in presets:

    print("\n" + "=" * 70)
    print(preset.upper())
    print("=" * 70)

    result = engine.apply_filters(preset)

    print(result[["company_name", "year", "composite_quality_score"]].head(10))

    print(f"\nCompanies Returned : {len(result)}")
