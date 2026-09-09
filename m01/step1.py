import json
from urllib.request import Request, urlopen


CIK = "0000002488"
URL = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json"


def main():
    request = Request(
        URL,
        headers={"User-Agent": "CS1066 student"},
    )

    with urlopen(request) as response:
        company_data = json.load(response)

    with open("amd_data.json", "w", encoding="utf-8") as output_file:
        json.dump(company_data, output_file, indent=2)


if __name__ == "__main__":
    main()