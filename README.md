# 📈 Nifty 100 Financial Intelligence Platform

A comprehensive Financial Intelligence Platform built using **Python, SQLite, Pandas, Plotly, Streamlit, OpenPyXL, ReportLab, and Pytest** for analyzing Nifty 100 companies.

The platform provides financial KPI analysis, stock screening, peer comparison, valuation analysis, capital allocation analysis, cash flow intelligence, NLP-based financial insights, interactive dashboards, and automated financial report generation.

---

# 🚀 Features

## 📊 ETL Pipeline

- Load financial datasets into SQLite
- Data validation and normalization
- Automated data quality checks
- Excel data ingestion and normalization
- Structured SQLite financial database

## 📈 Financial KPI Engine

- ROE
- ROCE
- Net Profit Margin
- Operating Profit Margin
- Debt-to-Equity
- Interest Coverage
- Asset Turnover
- Free Cash Flow
- Revenue CAGR
- PAT CAGR
- EPS CAGR
- Composite Quality Score
- Earnings Per Share
- Book Value Per Share
- Dividend Payout Ratio

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
- Revenue and Net Profit Trends
- ROE and ROCE Analysis

## 🏭 Sector Analysis

- Sector-level KPIs
- Sector Median Comparison
- Sector Distribution
- Interactive Sector Visualizations

## 🌳 Capital Allocation

- Capital Allocation Classification
- Reinvestor
- Deleverager
- Distress Signal
- Shareholder Returns
- Cash Burner
- Cash Accumulator
- Balanced
- Insufficient Data
- Capital Allocation Visualization
- Year-over-year Pattern Changes

## 💰 Valuation Module

- FCF Yield
- Sector Median P/E
- EV/EBITDA
- P/B Ratio
- Overvaluation Detection
- Discount Detection
- Fair Valuation Classification

## 💵 Cash Flow Intelligence

- CFO Quality Score
- CFO Quality Classification
- CapEx Intensity
- CapEx Classification
- Free Cash Flow CAGR
- Free Cash Flow Conversion
- Distress Signal Detection
- Deleveraging Detection
- Capital Allocation Integration
- Distress Alert Generation

## 🤖 NLP Financial Analysis

- Financial analysis text parsing
- CAGR extraction using regex
- ROE extraction
- Structured analysis output
- Automated financial Pros and Cons
- Rule-based financial signal generation
- Confidence scoring for generated signals

## 📄 Automated Financial Reports

### Company Tearsheet Reports

- Automated two-page company tearsheets
- Company financial KPIs
- Revenue and Net Profit trends
- ROE and ROCE analysis
- Balance Sheet composition
- Cash Flow analysis
- Pros and Cons
- Capital Allocation
- 92 company reports generated

### Sector Reports

- Sector summary
- Sector KPIs
- Company-level metrics
- Automated PDF generation
- Reports generated for every broad sector present in the supplied database

### Portfolio Summary

- One-page summary per company
- Alphabetical ticker ordering
- Six key financial KPIs
- Three-year trend comparison
- Up, down and flat trend indicators
- N/A handling for unavailable historical data

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
- ReportLab
- Pytest
- Regex

---

# 📂 Project Structure

```text
Nifty-100-Financial-Intelligence-Platform/
│
├── config/
├── data/
│   ├── raw/
│   └── processed/
├── db/
│   └── nifty100.db
├── docs/
│   └── sprint5_retrospective.md
├── notebooks/
├── output/
│   ├── screener_output.xlsx
│   ├── peer_comparison.xlsx
│   ├── valuation_summary.xlsx
│   ├── valuation_flags.csv
│   ├── analysis_parsed.csv
│   ├── pros_cons_generated.csv
│   ├── cashflow_intelligence.xlsx
│   ├── distress_alerts.csv
│   └── pattern_changes.csv
├── reports/
│   ├── radar_charts/
│   ├── tearsheets/
│   ├── sector/
│   └── portfolio/
│       └── portfolio_summary.pdf
├── src/
│   ├── analytics/
│   │   └── cashflow_kpis.py
│   ├── dashboard/
│   ├── etl/
│   ├── nlp/
│   │   ├── parser.py
│   │   └── pros_cons_generator.py
│   ├── reports/
│   │   ├── batch_tearsheets.py
│   │   ├── portfolio_summary.py
│   │   ├── sector_report.py
│   │   └── tearsheet.py
│   ├── screener/
│   └── utils/
├── tests/
├── requirements.txt
└── README.md
```

---

# ▶ Installation

## Clone the Repository

```bash
git clone https://github.com/Likithamurthy4/nifty100-financial-intelligence-platform.git
```

## Move into the Project

```bash
cd nifty100-financial-intelligence-platform
```

## Create a Virtual Environment

```bash
python -m venv venv
```

## Activate the Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

## Install Dependencies

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

# ▶ Run NLP Analysis Parser

```bash
python src/demo_day29.py
```

Outputs:

```text
output/analysis_parsed.csv
output/parse_failures.csv
```

---

# ▶ Run Pros & Cons Generator

```bash
python src/nlp/pros_cons_generator.py
```

Output:

```text
output/pros_cons_generated.csv
```

The generated output contains:

- Company ID
- Pro / Con type
- Rule ID
- Financial insight text
- Confidence percentage

---

# ▶ Run Cash Flow Intelligence

```bash
python src/analytics/cashflow_kpis.py
```

Outputs:

```text
output/cashflow_intelligence.xlsx
output/distress_alerts.csv
```

---

# ▶ Generate Capital Allocation

```bash
python src/demo_day32_part2.py
```

Outputs:

```text
output/capital_allocation.csv
output/pattern_changes.csv
```

---

# ▶ Generate Company Tearsheet Reports

```bash
python src/reports/batch_tearsheets.py
```

Output:

```text
reports/tearsheets/
```

Final validation:

- 92 companies
- 92 PDFs
- 0 skipped
- 0 failed
- 0 PDFs below 30 KB

---

# ▶ Generate Sector Reports

```bash
python src/reports/sector_report.py
```

Output:

```text
reports/sector/
```

The supplied database contains **10 distinct broad sectors**, and reports are generated for all sectors available in the source data.

---

# ▶ Generate Portfolio Summary

```bash
python src/reports/portfolio_summary.py
```

Output:

```text
reports/portfolio/portfolio_summary.pdf
```

The Portfolio Summary contains:

- 92 company pages
- Alphabetical ordering by ticker
- Company name
- Sector
- Six key financial KPIs
- Three-year trend comparison
- Up arrow for improvement
- Down arrow for decline
- Right arrow for changes within ±2%
- N/A for unavailable comparison data

---

# ▶ Run Tests

```bash
pytest
```

The project includes tests for:

- Financial Ratios
- CAGR Calculations
- Cash Flow KPIs
- ETL Normalization
- Data Validation

---

# 📊 Generated Outputs

## Financial Analysis

```text
output/screener_output.xlsx
output/peer_comparison.xlsx
output/valuation_summary.xlsx
output/valuation_flags.csv
```

## NLP

```text
output/analysis_parsed.csv
output/pros_cons_generated.csv
```

## Cash Flow Intelligence

```text
output/cashflow_intelligence.xlsx
output/distress_alerts.csv
output/pattern_changes.csv
```

## Reports

```text
reports/tearsheets/
reports/sector/
reports/portfolio/portfolio_summary.pdf
```

---

# 📋 Dashboard Screens

The Streamlit dashboard contains:

- 🏠 Home Dashboard
- 🏢 Company Profile
- 🔍 Stock Screener
- 👥 Peer Comparison
- 📈 Trend Analysis
- 🏭 Sector Analysis
- 🌳 Capital Allocation
- 📄 Annual Reports

---

# 🧪 Sprint 5 Validation

The Sprint 5 implementation was validated with the following results:

### Pros & Cons

- 455 generated records
- 92 unique companies
- 0 companies missing a Pro
- 0 companies missing a Con

### Cash Flow Intelligence

- 92 rows
- 92 unique companies
- Required KPI and classification columns present

### Distress Alerts

- 13 companies flagged
- CFO, CFF and latest Net Profit included

### Company Tearsheet Reports

- 92 PDFs generated
- 0 skipped
- 0 failed
- 0 PDFs below 30 KB

### Portfolio Summary

- 92 pages
- One page per company
- Alphabetical ticker ordering
- Three-year trend comparison
- ±2% flat threshold
- Missing historical comparison data handled as N/A

### Sector Reports

The Sprint specification expected 11 sector reports.

The supplied database contains 10 distinct broad sectors:

1. Communication Services
2. Consumer Discretionary
3. Consumer Staples
4. Energy
5. Financials
6. Healthcare
7. Industrials
8. Information Technology
9. Materials
10. Real Estate

Reports were generated for all 10 sectors present in the database.

---

# 📝 Sprint 5 Retrospective

Sprint 5 focused on Cash Flow Intelligence, NLP-based financial analysis,
capital allocation, automated financial reporting, and portfolio-level
summarization.

The sprint successfully delivered:

- Analysis text parsing
- Automated financial Pros and Cons
- CFO quality analysis
- CapEx intensity analysis
- Distress signal detection
- Deleveraging detection
- Capital allocation classification
- Company tearsheet generation
- Sector report generation
- Portfolio Summary generation

The final outputs were validated for company coverage, report counts,
file sizes, missing-data handling, and PDF generation.

### Key Data Considerations

ATGL has insufficient historical financial data for some cash-flow and
ratio calculations. The platform handles these cases using
`Insufficient Data` or `N/A` rather than generating fabricated values.

The supplied database contains 10 broad sectors even though the Sprint
specification expected 11. All available sectors were therefore reported.

---

# 🔮 Future Enhancements

- Live NSE/BSE Data Integration
- AI-based Stock Recommendation
- Portfolio Optimization
- Predictive Financial Analytics
- Cloud Deployment
- User Authentication
- Interactive Watchlist
- Automated PDF visual regression testing
- Expanded historical financial data coverage
- Advanced NLP-based financial sentiment analysis

---

# 👩‍💻 Author

**Likitha Murthy M L**

B.Tech – Information Science & Engineering

M S Ramaiah University of Applied Sciences

---

# ⭐ Acknowledgements

This project was developed as part of a Financial Intelligence Platform
internship, focusing on financial analytics, stock screening, peer
analysis, valuation modeling, cash flow intelligence, NLP-based
financial insights, automated reporting, and interactive dashboard
development using Python and Streamlit.
