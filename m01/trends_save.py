import csv

from trends_scraper import get_driver, scrape_interest_data


def main():
    date_range = "now%207-d"
    geo = "US"
    query = "vibe coding"
    site = "https://trends.google.com/trends/explore"
    url = f"{site}?date={date_range}&geo={geo}&q={query}&hl=en"

    driver = get_driver()
    if driver is None:
        raise RuntimeError("Could not initialize Chrome driver")

    try:
        interest_data = scrape_interest_data(driver, url)
    finally:
        driver.quit()

    with open("scraped_data.csv", "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["region", "interest"])
        writer.writerows(interest_data.items())


if __name__ == "__main__":
    main()