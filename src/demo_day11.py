from analytics.cashflow_kpis import *

fcf = free_cash_flow(500, -250)

print("Free Cash Flow :", fcf)

print(
    "Quality :",
    cfo_quality_score(
        120,
        100
    )
)

print(
    "CapEx :",
    capex_intensity(
        -80,
        1000
    )
)

print(
    "FCF Conversion :",
    fcf_conversion(
        fcf,
        600
    )
)

print(
    "Pattern :",
    classify_capital_allocation(
        500,
        -100,
        -50,
        "High Quality"
    )
)

records = [

    {

        "company_id":"ABB",

        "year":2024,

        "cfo_sign":"+",

        "cfi_sign":"-",

        "cff_sign":"-",

        "pattern_label":"Shareholder Returns"

    }

]

save_capital_allocation(records)