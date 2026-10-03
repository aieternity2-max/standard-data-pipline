from pathlib import Path

import pandas as pd


output_file = (
    Path(__file__).parent
    / "fixtures"
    / "sample.xlsx"
)

data = {
    "customer_id": list(range(101, 121)),
    "name": [
        "Alice",
        "Bob",
        "Charlie",
        "David",
        "Emma",
        "Frank",
        "Grace",
        "Henry",
        "Ivy",
        "Jack",
        "Karen",
        "Liam",
        "Mia",
        "Noah",
        "Olivia",
        "Peter",
        "Quinn",
        "Rachel",
        "Sam",
        "Sophia",
    ],
    "email": [
        "alice@example.com",
        "bob@example.com",
        "charlie@example.com",
        "david@example.com",
        "emma@example.com",
        "frank@example.com",
        "grace@example.com",
        "henry@example.com",
        "ivy@example.com",
        "jack@example.com",
        "karen@example.com",
        "liam@example.com",
        "mia@example.com",
        "noah@example.com",
        "olivia@example.com",
        "peter@example.com",
        "quinn@example.com",
        "rachel@example.com",
        "sam@example.com",
        "sophia@example.com",
    ],
    "age": [
        31, 27, 45, 38, 29,
        42, 35, 51, 26, 33,
        41, 30, 28, 47, 36,
        39, 25, 44, 32, 37,
    ],
}

df = pd.DataFrame(data)

output_file.parent.mkdir(
    parents=True,
    exist_ok=True,
)

df.to_excel(
    output_file,
    index=False,
    engine="openpyxl",
)

print(f"Created: {output_file}")
print(f"Rows: {len(df)}")