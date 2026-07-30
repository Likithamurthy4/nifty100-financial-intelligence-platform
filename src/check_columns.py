from screener.loader import ScreenerLoader

loader = ScreenerLoader()
df = loader.load_master_dataframe()

print("\nMASTER DATAFRAME COLUMNS:\n")
for col in df.columns:
    print(col)

loader.close()
