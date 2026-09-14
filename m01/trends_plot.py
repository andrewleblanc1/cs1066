import csv

import matplotlib.pyplot as plt


def main():
    regions = []
    interest = []

    with open("scraped_data.csv", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            regions.append(row["region"])
            interest.append(int(row["interest"]))

    plt.figure(figsize=(12, 8))
    plt.bar(regions, interest)
    plt.xlabel("Region")
    plt.ylabel("Interest")
    plt.title('Google Trends Interest in "vibe coding"')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig("interest_trends.png")
    plt.close()


if __name__ == "__main__":
    main()