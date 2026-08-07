# 📈 Nifty 100 Financial Intelligence Platform

A comprehensive Financial Intelligence Platform built using **Python, SQLite, Pandas, Plotly, Streamlit, and OpenPyXL** for analyzing Nifty 100 companies. The project provides financial KPI analysis, stock screening, peer comparison, valuation analysis, interactive dashboards, and automated report generation.

---

# 🚀 Features

## 📊 ETL Pipeline
- Load financial datasets into SQLite
- Data validation and normalization
- Automated data quality checks

## 📈 Financial KPI Engine
- ROE
- ROCE
- Net Profit Margin
- Debt-to-Equity
- Interest Coverage
- Asset Turnover
- Free Cash Flow
- Revenue CAGR
- PAT CAGR
- EPS CAGR
- Composite Quality Score

## 🔍 Stock Screener
- Interactive financial filters
- Quality Preset
- Value Preset
- Growth Preset
- Dividend Preset
- Debt-Free Preset
- Turnaround Preset
- CSV Export

## 👥 Peer Comparison
- Peer Group Selection
- Company Comparison
- Radar Charts
- Peer Median Analysis
- Peer Comparison Table

## 📈 Trend Analysis
- 10-Year Financial Trends
- Multi-Metric Comparison
- Year-over-Year Growth Analysis

## 🏭 Sector Analysis
- Bubble Charts
- Sector KPIs
- Sector Median Comparison

## 🌳 Capital Allocation
- Treemap Visualization
- Capital Allocation Categories
- Company Distribution

## 📄 Annual Reports
- Company Search
- Annual Report Links
- Report Availability Status

## 💰 Valuation Module
- FCF Yield
- Sector Median P/E
- EV/EBITDA
- P/B Ratio
- Overvaluation Detection
- Discount Detection
- Fair Valuation Classification

---

# 🛠 Tech Stack

- Python 3
- SQLite
- Pandas
- NumPy
- Plotly
- Streamlit
- OpenPyXL
- Matplotlib
- Pytest

---

# 📂 Project Structure

```
Nifty-100-Financial-Intelligence-Platform/

│
├── db/
│   └── nifty100.db
│
├── config/
│
├── data/
│
├── output/
│   ├── screener_output.xlsx
│   ├── peer_comparison.xlsx
│   ├── valuation_summary.xlsx
│   └── valuation_flags.csv
│
├── reports/
│   └── radar_charts/
│
├── src/
│   ├── analytics/
│   ├── dashboard/
│   ├── etl/
│   ├── screener/
│   └── utils/
│
├── tests/
│
├── requirements.txt
│
└── README.md
```

---

# ▶ Installation

Clone the repository

```bash
git clone https://github.com/Likithamurthy4/nifty-100-financial-intelligence-platform.git
```

Move into the project

```bash
cd nifty-100-financial-intelligence-platform
```

Create a virtual environment

```bash
python -m venv venv
```

Activate it

Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# ▶ Run Streamlit Dashboard

```bash
streamlit run src/dashboard/app.py
```

---

# ▶ Run Valuation Module

```bash
python src/demo_day26.py
```

---

# ▶ Run Tests

```bash
pytest
```

---

# 📋 Dashboard Screens

- 🏠 Home Dashboard
- 🏢 Company Profile
- 🔍 Stock Screener
- 👥 Peer Comparison
- 📈 Trend Analysis
- 🏭 Sector Analysis
- 🌳 Capital Allocation
- 📄 Annual Reports

---

# 📊 Generated Reports

The project generates:

- `output/screener_output.xlsx`
- `output/peer_comparison.xlsx`
- `output/valuation_summary.xlsx`
- `output/valuation_flags.csv`

Radar charts are generated in:

```
reports/radar_charts/
```

---

# 🧪 Testing

The project includes automated unit tests for:

- Financial Ratios
- CAGR Calculations
- Cash Flow KPIs
- ETL Normalization
- Data Validation

Run:

```bash
pytest
```

---

# 📸 Screenshots

Add screenshots of:

- Home Dashboard
- Company Profile
- Stock Screener
- Peer Comparison
- Trend Analysis
- Sector Analysis
- Capital Allocation
- Annual Reports

Example:

```
README_Images/
    home.png
    profile.png
    screener.png
    peers.png
    trends.png
    sectors.png
    capital.png
    reports.png
```

---

# 🎯 Future Enhancements

- Live NSE/BSE Data Integration
- AI-based Stock Recommendation
- Portfolio Optimization
- Predictive Financial Analytics
- Cloud Deployment
- User Authentication
- Interactive Watchlist

---

# 👩‍💻 Author

**Likitha Murthy M L**

B.Tech – Information Science & Engineering

M S Ramaiah University of Applied Sciences

---

# ⭐ Acknowledgements

This project was developed as part of a Financial Intelligence Platform internship, focusing on financial analytics, stock screening, peer analysis, valuation modeling, and interactive dashboard development using Python and Streamlit.