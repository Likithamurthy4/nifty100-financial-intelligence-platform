from analytics.valuation import Valuation

valuation = Valuation()

df = valuation.calculate()

print(df.head())

valuation.export(df)

valuation.close()

print()

print("Day 26 Completed.")