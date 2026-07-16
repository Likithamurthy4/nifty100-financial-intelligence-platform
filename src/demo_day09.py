from analytics.ratios import *

print("Debt-to-Equity:", debt_to_equity(200, 100, 100))
print("High Leverage:", high_leverage_flag(6, "Technology"))
print("Interest Coverage:", interest_coverage(400, 50, 100))
print("ICR Label:", icr_label(None))
print("ICR Warning:", icr_warning(1.2))
print("Net Debt:", net_debt(500, 150))
print("Asset Turnover:", asset_turnover(1200, 600))