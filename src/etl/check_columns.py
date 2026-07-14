from pathlib import Path
import pandas as pd

RAW_DATA = Path("data/raw")

datasets = {
    "companies.xlsx": 1,
    "profitandloss.xlsx": 1,
    "balancesheet.xlsx": 1,
    "cashflow.xlsx": 1,
    "analysis.xlsx": 1,
    "documents.xlsx": 1,
    "prosandcons.xlsx": 1,
    "sectors.xlsx": 0,
    "stock_prices.xlsx": 0,
    "market_cap.xlsx": 0,
    "financial_ratios.xlsx": 0,
    "peer_groups.xlsx": 0,
}

for file, header in datasets.items():

    print("\n" + "=" * 80)
    print(file)

    df = pd.read_excel(RAW_DATA / file, header=header)

    print(df.columns.tolist())