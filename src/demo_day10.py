from analytics.cagr import *

print("Revenue CAGR")

cases = [

    (100, 200, 5),
    (0, 200, 5),
    (-100, 200, 5),
    (200, -100, 5),
    (-100, -50, 5),
    (100, 200, 2)

]

for start, end, years in cases:

    value, flag = revenue_cagr(
        start,
        end,
        years
    )

    print(

        f"Start={start} End={end} Years={years}"

    )

    print(

        "CAGR =", value,

        "Flag =", flag

    )

    print()