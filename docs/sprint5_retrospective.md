# Sprint 5 Retrospective

## Sprint 5
Cash Flow Intelligence + Reports + NLP

## Sprint Goal

The goal of Sprint 5 was to implement NLP-based financial analysis,
cash flow intelligence, capital allocation classification, automated
company and sector reports, and the final portfolio summary.

---

## 1. What Was Completed

### NLP Analysis Parser
- Implemented `src/nlp/parser.py`.
- Parsed structured CAGR and ROE information from `analysis` data.
- Generated `output/analysis_parsed.csv`.
- Generated `output/parse_failures.csv` for unmatched source text.
- Final parser run completed with zero parsing failures.

### Automated Pros and Cons
- Implemented `src/nlp/pros_cons_generator.py`.
- Implemented financial rule-based Pro and Con generation.
- Generated `output/pros_cons_generated.csv`.
- Generated 455 Pro/Con records across 92 companies.
- Every company has at least one Pro and one Con.
- Missing Pro companies: 0.
- Missing Con companies: 0.

### Cash Flow Intelligence
- Implemented CFO quality analysis.
- Implemented CapEx intensity classification.
- Implemented FCF CAGR and FCF conversion metrics.
- Implemented distress signal detection.
- Implemented deleveraging detection.
- Generated:
  - `output/cashflow_intelligence.xlsx`
  - `output/distress_alerts.csv`
- Final cash flow intelligence output contains 92 companies.

### Capital Allocation
- Generated capital allocation classifications across available years.
- Added capital allocation information to cash flow intelligence.
- Generated `output/pattern_changes.csv`.
- Final capital allocation QA confirmed 92 unique companies.

### Company Tearsheet Reports
- Implemented the ReportLab-based company tearsheet.
- Generated 92 company PDF reports.
- All 92 companies were generated successfully.
- No companies were skipped.
- No companies failed.
- All generated tearsheets were above the 30 KB validation threshold.
- Visual QA was performed on multiple companies from different sectors.

### Sector Reports
- Generated sector-level PDF reports for every broad sector present in
  the supplied database.
- The database contains 10 distinct broad sectors, so 10 sector reports
  were generated.
- No actual database sector was missing.

### Portfolio Summary
- Generated `reports/portfolio/portfolio_summary.pdf`.
- Generated 92 pages for 92 companies.
- Companies are ordered alphabetically by ticker.
- Each page contains company name, sector and six KPIs.
- Trend arrows use the exact three-year-earlier comparison where data is
  available.
- A change within ±2% is treated as flat.
- Debt-to-equity uses inverse trend logic because lower debt is better.
- Missing comparison data is displayed as N/A.
- Final PDF contains 92 pages and passed PDF validation.

---

## 2. What Went Well

- All major Sprint 5 modules were successfully implemented.
- The NLP pipeline successfully generated structured output.
- Every company received both positive and negative financial signals.
- Cash flow intelligence was successfully integrated with capital
  allocation information.
- The reporting pipeline successfully generated 92 company tearsheets.
- No tearsheets failed during batch generation.
- Portfolio Summary generation was completed and validated.
- Missing financial data was handled using N/A / Insufficient Data instead
  of fabricated values.
- Final QA confirmed the major output files and company counts.

---

## 3. Challenges and Data Issues

### ATGL Missing Cash Flow Data

ATGL did not have sufficient cash flow data for some calculations.

The system therefore reports:
- Insufficient Data for CFO quality.
- Insufficient Data for CapEx intensity.
- N/A for unavailable derived metrics.

This prevented the system from generating misleading financial values.

### Partial Historical Data

Some companies have incomplete historical financial data.

The reporting logic was designed to avoid crashing when historical
comparison data is unavailable.

### Source Company Names

Some company names in the source company master contained additional
descriptive text.

Display-level cleanup was applied to the Portfolio Summary without
modifying the underlying database.

### Sector Count Difference

The Sprint specification expected 11 sector PDFs.

However, the supplied `sectors` table contains 10 distinct broad sectors.

Therefore, reports were generated for all 10 sectors actually present in
the database rather than creating an artificial 11th sector.

---

## 4. QA and Validation

Final QA results:

- Pros/Cons companies: 92
- Missing Pro companies: 0
- Missing Con companies: 0
- Cash Flow Intelligence rows: 92
- Unique Cash Flow Intelligence companies: 92
- Distress alert records: 13
- Company tearsheets: 92
- Tearsheets below 30 KB: 0
- Portfolio Summary pages: 92
- Required Sprint 5 source files: present
- Required output files: present

---

## 5. What Could Be Improved

For future iterations:

1. Improve source-data completeness for companies with missing historical
   financial information.
2. Standardize company names during the ETL stage instead of only during
   report generation.
3. Add automated PDF page-count and layout validation to the reporting
   pipeline.
4. Add automated alerts for unusually high financial ratios.
5. Add validation between sprint requirements and the actual number of
   sectors present in the database.
6. Expand historical data coverage where possible to improve trend
   analysis.

---

## 6. Sprint Conclusion

Sprint 5 successfully delivered the planned NLP, cash flow intelligence,
capital allocation and reporting functionality.

The major Sprint 5 deliverables were generated and validated, including
the Pros/Cons output, Cash Flow Intelligence workbook, distress alerts,
company tearsheets, sector reports and Portfolio Summary.

The remaining project activity is the Sprint Review and Team Lead
sign-off.