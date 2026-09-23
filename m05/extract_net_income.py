import json
from datetime import date
from pathlib import Path


def extract_net_income(file_path):
    with Path(file_path).open() as file:
        data = json.load(file)

    records = data["facts"]["us-gaap"]["NetIncomeLoss"]["units"]["USD"]
    yearly_values = {}

    for record in records:
        if record.get("form") != "10-K" or record.get("fp") != "FY":
            continue
        if record.get("fy") != int(record["end"][:4]):
            continue

        start = date.fromisoformat(record["start"])
        end = date.fromisoformat(record["end"])
        if 300 <= (end - start).days <= 380:
            yearly_values[record["fy"]] = record["val"]

    return yearly_values


if __name__ == "__main__":
    for year, value in sorted(extract_net_income("amd_data.json").items()):
        print(f"{year}: ${value:,}")