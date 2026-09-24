"""Download company data from the SEC EDGAR JSON API."""

import argparse
import csv
import html
import io
import json
import re
import sys
import webbrowser
from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


SEC_API_BASE = "https://data.sec.gov"
USER_AGENT = "UniversityStudent your.emal@university.edu"
REQUEST_TIMEOUT = 30
METRIC_TAGS = {
    "revenue": (
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
        "SalesRevenueNet",
    ),
    "net_income": ("NetIncomeLoss",),
    "assets": ("Assets",),
}
DURATION_METRICS = {"revenue", "net_income"}
INSTANT_METRICS = {"assets"}


class InvalidCompanyCIKError(Exception):
    """Raised when the SEC does not recognize the requested company CIK."""


def normalize_cik(cik: str) -> str:
    """Validate and return a CIK as the SEC API's ten-digit string."""
    cik = cik.strip()
    if len(cik) != 10 or not cik.isdigit():
        raise ValueError("CIK must contain exactly 10 numerical characters")
    return cik


def make_session() -> requests.Session:
    """Create a session with the required SEC identity and limited retries."""
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    session.mount("https://", adapter)
    return session


def fetch_json(session: requests.Session, endpoint: str) -> dict:
    """Fetch one EDGAR JSON endpoint and return its decoded object."""
    response = session.get(
        f"{SEC_API_BASE}{endpoint}",
        timeout=REQUEST_TIMEOUT,
    )
    if response.status_code == 404:
        raise InvalidCompanyCIKError
    response.raise_for_status()
    return response.json()


def _filing_rows(document: str, metric: str, filing: dict) -> list[dict]:
    """Extract annual metric rows from a primary 10-K HTML document."""
    soup = BeautifulSoup(document, "html.parser")
    labels = {
        "revenue": ("net revenue", "total revenue", "revenues", "revenue"),
        "net_income": ("net income (loss)", "net income"),
        "assets": ("total assets",),
    }
    candidates = []
    for table in soup.find_all("table"):
        table_rows = table.find_all("tr")
        year_options = []
        for row in table_rows[:10]:
            years = []
            for year in re.findall(r"\b20\d{2}\b", " ".join(row.stripped_strings)):
                if year not in years:
                    years.append(year)
            if len(years) > len(year_options):
                year_options = years
        if len(year_options) < 2:
            continue

        scale = 1
        table_text = " ".join(table.stripped_strings).lower().replace("\xa0", " ")
        if re.search(r"\bin\s+millions\b", table_text):
            scale = 1_000_000
        elif re.search(r"\bin\s+thousands\b", table_text):
            scale = 1_000

        for row in table_rows:
            cells = [" ".join(cell.stripped_strings) for cell in row.find_all(["th", "td"])]
            if len(cells) < 2:
                continue
            label = re.sub(r"\s+", " ", cells[0]).strip().lower()
            if metric == "assets":
                label_rank = 0 if re.fullmatch(r"total assets(?:\s*\(\d+\))?", label) else None
            else:
                label_rank = next(
                    (
                        rank
                        for rank, pattern in enumerate(labels[metric])
                        if label.startswith(pattern)
                    ),
                    None,
                )
            if label_rank is None:
                continue

            values = []
            negative = False
            for cell in cells[1:]:
                if "(" in cell:
                    negative = True
                match = re.search(r"\d[\d,]*", cell)
                if match:
                    value = int(match.group().replace(",", "")) * scale
                    values.append(-value if negative else value)
                    negative = False
            if len(values) >= len(year_options):
                candidates.append((label_rank, len(values), year_options, values))

    if not candidates:
        return []
    _, _, years, values = sorted(candidates, key=lambda item: (item[0], -item[1]))[0]
    records = []
    for year, value in zip(years, values):
        records.append(
            {
                "metric": metric,
                "value": value,
                "start": f"{year}-01-01" if metric in DURATION_METRICS else None,
                "end": f"{year}-12-31",
                "filed": filing["filingDate"],
                "form": filing["form"],
                "accn": filing["accessionNumber"],
                "tag": "filing-table",
                "tag_rank": 0,
                "source_rank": 1,
            }
        )
    return records


def fetch_filing_table_facts(
    session: requests.Session, cik: str, submissions: dict
) -> list[dict]:
    """Fetch recent annual filings for values omitted from companyfacts."""
    recent = submissions.get("filings", {}).get("recent", {})
    filings = []
    for index, form in enumerate(recent.get("form", [])):
        if form not in ("10-K", "10-K/A"):
            continue
        filings.append({key: recent[key][index] for key in (
            "accessionNumber", "filingDate", "primaryDocument", "form"
        )})

    records = []
    for filing in filings:
        accession_path = filing["accessionNumber"].replace("-", "")
        archive_url = (
            f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/"
            f"{accession_path}/{filing['primaryDocument']}"
        )
        try:
            response = session.get(archive_url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
        except requests.RequestException:
            continue
        for metric in METRIC_TAGS:
            records.extend(_filing_rows(response.text, metric, filing))
    return records


def scrape_company(cik: str) -> dict[str, dict]:
    """Download submissions and XBRL company facts for one company."""
    normalized_cik = normalize_cik(cik)
    with make_session() as session:
        submissions = fetch_json(
            session, f"/submissions/CIK{normalized_cik}.json"
        )
        company_facts = fetch_json(
            session, f"/api/xbrl/companyfacts/CIK{normalized_cik}.json"
        )
        return {
            "submissions": submissions,
            "company_facts": company_facts,
            "filing_facts": fetch_filing_table_facts(
                session, normalized_cik, submissions
            ),
        }


def save_results(results: dict[str, dict], output_directory: Path, cik: str) -> None:
    """Write each EDGAR response to a readable JSON file."""
    output_directory.mkdir(parents=True, exist_ok=True)
    for name, data in results.items():
        output_path = output_directory / f"{cik}_{name}.json"
        output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"Saved {output_path}")


def _valid_fact(metric: str, fact: dict) -> bool:
    """Keep only annual duration facts or annual instant facts."""
    if fact.get("form") not in ("10-K", "10-K/A"):
        return False
    if "end" not in fact or "filed" not in fact:
        return False
    if metric == "assets" and ("segment" in fact or "dimensions" in fact):
        return False
    if metric in DURATION_METRICS:
        if "start" not in fact:
            return False
        duration_days = (
            date.fromisoformat(fact["end"])
            - date.fromisoformat(fact["start"])
        ).days
        return 300 <= duration_days <= 430
    return metric in INSTANT_METRICS


def _period_key(metric: str, fact: dict) -> tuple[str, ...]:
    """Identify the economic period represented by one fact."""
    if metric in DURATION_METRICS:
        return fact["start"], fact["end"]
    return (fact["end"],)


def select_metric_records(
    company_facts: dict, metric: str, filing_records: list[dict] = ()
) -> list[dict]:
    """Select the latest valid fact for each year, retaining SEC provenance."""
    if metric not in METRIC_TAGS:
        raise ValueError(f"Unknown metric: {metric}")

    us_gaap = company_facts.get("facts", {}).get("us-gaap", {})
    records_by_period: dict[tuple[str, ...], dict] = {}

    for tag_rank, tag in enumerate(METRIC_TAGS[metric]):
        records = us_gaap.get(tag, {}).get("units", {}).get("USD", [])
        for record in records:
            if not _valid_fact(metric, record):
                continue

            candidate = {
                "metric": metric,
                "value": record["val"],
                "start": record.get("start"),
                "end": record["end"],
                "filed": record["filed"],
                "form": record["form"],
                "accn": record.get("accn"),
                "tag": tag,
                "tag_rank": tag_rank,
                "source_rank": 0,
            }
            period = _period_key(metric, record)
            previous = records_by_period.get(period)
            candidate_rank = (
                candidate["filed"],
                candidate["source_rank"],
                -tag_rank,
                candidate["accn"] or "",
            )
            previous_rank = (
                (
                    previous["filed"],
                    previous["source_rank"],
                    -previous["tag_rank"],
                    previous["accn"] or "",
                )
                if previous
                else None
            )
            if previous is None or candidate_rank > previous_rank:
                records_by_period[period] = candidate

    for record in filing_records:
        if record["metric"] != metric:
            continue
        period = _period_key(metric, record)
        previous = records_by_period.get(period)
        if previous is None or (
            record["filed"], record["source_rank"], record["accn"]
        ) > (
            previous["filed"], previous["source_rank"], previous["accn"] or ""
        ):
            records_by_period[period] = record

    records_by_year = {}
    for record in records_by_period.values():
        year = record["end"][:4]
        previous = records_by_year.get(year)
        if previous is None or (
            record["filed"], record["source_rank"], record["accn"] or ""
        ) > (
            previous["filed"], previous["source_rank"], previous["accn"] or ""
        ):
            records_by_year[year] = record

    selected = sorted(records_by_year.values(), key=lambda fact: fact["end"])
    return selected[-10:]


def annual_records(
    company_facts: dict, metric: str, filing_records: list[dict] = ()
) -> list[dict]:
    """Return the public year/value view of selected annual SEC facts."""
    return [
        {"year": int(record["end"][:4]), "value": record["value"]}
        for record in select_metric_records(company_facts, metric, filing_records)
    ]


def save_metric_csvs(
    company_facts: dict,
    output_directory: Path,
    cik: str,
    filing_records: list[dict] = (),
) -> None:
    """Write revenue, net income, and assets to separate CSV files."""
    for metric in METRIC_TAGS:
        rows = annual_records(company_facts, metric, filing_records)
        output_path = output_directory / f"{cik}_{metric}.csv"
        with output_path.open("w", newline="", encoding="utf-8") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=("year", "value"))
            writer.writeheader()
            writer.writerows({"year": row["year"], "value": row["value"]} for row in rows)
        print(f"Saved {output_path} ({len(rows)} years)")



def load_metric_csvs(output_directory: Path, cik: str) -> dict[str, dict[int, float]]:
    """Load the generated metric CSVs for plotting."""
    metrics = {}
    for metric in METRIC_TAGS:
        csv_path = output_directory / f"{cik}_{metric}.csv"
        with csv_path.open(newline="", encoding="utf-8") as input_file:
            metrics[metric] = {
                int(row["year"]): float(row["value"])
                for row in csv.DictReader(input_file)
            }
    return metrics


def create_plot_html(
    output_directory: Path,
    cik: str,
    company_name: str,
    open_browser: bool = True,
) -> Path:
    """Create one combined financial plot and display it in a browser."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    metrics = load_metric_csvs(output_directory, cik)
    colors = {
        "revenue": "#176b87",
        "net_income": "#c44536",
        "assets": "#3d7a4a",
    }
    labels = {
        "revenue": "Revenue",
        "net_income": "Net income",
        "assets": "Assets",
    }

    figure, revenue_axis = plt.subplots(figsize=(12, 7), facecolor="#f4f1ea")
    revenue_axis.set_facecolor("#fffdf8")
    axes = {"revenue": revenue_axis}
    axes["net_income"] = revenue_axis.twinx()
    axes["assets"] = revenue_axis.twinx()
    axes["assets"].spines["right"].set_position(("outward", 60))

    for metric, axis in axes.items():
        years = sorted(metrics[metric])
        values = [metrics[metric][year] for year in years]
        axis.plot(
            years,
            values,
            marker="o",
            linewidth=2.5,
            color=colors[metric],
            label=labels[metric],
        )
        axis.set_ylabel(labels[metric] + " (USD)", color=colors[metric])
        axis.tick_params(axis="y", labelcolor=colors[metric])

    revenue_axis.set_xlabel("Fiscal year")
    revenue_axis.set_title(f"{company_name} financial history")
    revenue_axis.grid(axis="y", alpha=0.25)
    revenue_axis.set_xticks(
        sorted(set().union(*(set(values) for values in metrics.values())))
    )
    lines = [axis.get_lines()[0] for axis in axes.values()]
    revenue_axis.legend(lines, [line.get_label() for line in lines], loc="upper left")
    figure.tight_layout()

    plot_path = output_directory / f"{cik}_financial_history.png"
    figure.savefig(plot_path, format="png", dpi=160, bbox_inches="tight")
    svg_buffer = io.StringIO()
    figure.savefig(svg_buffer, format="svg", bbox_inches="tight")
    plt.close(figure)
    svg_markup = re.sub(r"<\?xml.*?\?>", "", svg_buffer.getvalue(), count=1, flags=re.S)
    svg_markup = re.sub(r"<!DOCTYPE.*?>", "", svg_markup, count=1, flags=re.S)
    safe_company_name = html.escape(company_name)
    latest_year = max(max(values) for values in metrics.values())

    def format_value(value: float) -> str:
        if abs(value) >= 1_000_000_000:
            return f"${value / 1_000_000_000:,.2f}B"
        if abs(value) >= 1_000_000:
            return f"${value / 1_000_000:,.1f}M"
        return f"${value:,.0f}"

    cards = "".join(
        f"""
        <article class="metric-card {metric}">
          <span>{labels[metric]}</span>
          <strong>{format_value(metrics[metric][latest_year])}</strong>
          <small>FY {latest_year}</small>
        </article>
        """
        for metric in ("revenue", "net_income", "assets")
    )
    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_company_name} financial history</title>
  <style>
        :root {{
            --ink: #243238;
            --muted: #687579;
            --paper: #fffdf8;
            --line: #ddd8cd;
            --blue: #176b87;
            --red: #c44536;
            --green: #3d7a4a;
        }}
        * {{ box-sizing: border-box; }}
        body {{
            background: #f4f1ea;
            color: var(--ink);
            font-family: Georgia, "Times New Roman", serif;
            margin: 0;
        }}
        main {{ margin: 0 auto; max-width: 1180px; padding: 3rem 1.25rem 4rem; }}
        .hero {{ border-bottom: 1px solid var(--line); padding-bottom: 2rem; }}
        .eyebrow {{ color: var(--blue); font: 700 .75rem/1.2 Arial, sans-serif; letter-spacing: .12em; text-transform: uppercase; }}
        h1 {{ font-size: clamp(2rem, 5vw, 4.25rem); font-weight: 500; letter-spacing: -.03em; line-height: 1; margin: .65rem 0 .8rem; max-width: 850px; }}
        .lede {{ color: var(--muted); font: 1rem/1.6 Arial, sans-serif; margin: 0; }}
        .cards {{ display: grid; gap: 1rem; grid-template-columns: repeat(3, 1fr); margin: 2rem 0; }}
        .metric-card {{ background: var(--paper); border: 1px solid var(--line); border-top: 4px solid var(--blue); padding: 1.25rem; }}
        .metric-card.net_income {{ border-top-color: var(--red); }}
        .metric-card.assets {{ border-top-color: var(--green); }}
        .metric-card span, .metric-card small {{ color: var(--muted); display: block; font: .75rem/1.3 Arial, sans-serif; text-transform: uppercase; }}
        .metric-card strong {{ display: block; font-size: clamp(1.5rem, 3vw, 2.35rem); font-weight: 500; margin: .5rem 0; }}
        .chart {{ background: var(--paper); border: 1px solid var(--line); padding: .75rem; }}
        .chart svg {{ display: block; height: auto; max-width: 100%; width: 100%; }}
        .download {{ color: var(--blue); display: inline-block; font: .8rem/1.5 Arial, sans-serif; margin-top: .75rem; }}
        footer {{ color: var(--muted); font: .8rem/1.5 Arial, sans-serif; padding-top: 1rem; }}
        @media (max-width: 700px) {{
            main {{ padding-top: 2rem; }}
            .cards {{ grid-template-columns: 1fr; }}
        }}
  </style>
</head>
<body>
  <main>
        <header class="hero">
            <div class="eyebrow">SEC EDGAR annual snapshot</div>
            <h1>{safe_company_name}</h1>
            <p class="lede">Revenue, net income, and consolidated assets over the latest available fiscal periods.</p>
        </header>
        <section class="cards" aria-label="Latest financial metrics">{cards}</section>
        <section class="chart">
            {svg_markup}
            <a class="download" href="{plot_path.name}" download>Download PNG chart</a>
        </section>
        <footer>CIK {cik} &middot; Values are reported in U.S. dollars &middot; Source: SEC EDGAR</footer>
  </main>
</body>
</html>
"""
    output_path = output_directory / f"{cik}_financial_history.html"
    output_path.write_text(page, encoding="utf-8")
    print(f"Saved {plot_path}")
    print(f"Saved {output_path}")
    if open_browser:
        webbrowser.open(output_path.resolve().as_uri())
    return output_path


def confirm_output_directory(output_directory: Path) -> None:
    """Ask before overwriting an existing output directory."""
    if not output_directory.exists():
        return
    answer = input(
        f"Output directory '{output_directory}' already exists. "
        "Overwrite its files? [y/N]: "
    ).strip().lower()
    if answer not in {"y", "yes"}:
        print("Operation cancelled.")
        raise SystemExit(0)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "cik",
        nargs="?",
        help="10-digit SEC Central Index Key (prompted if omitted)",
    )
    parser.add_argument(
        "-o",
        "--output-directory",
        type=Path,
        help="Output directory (default: sec_data_{CIK})",
    )
    args = parser.parse_args()

    cik_input = args.cik or input("Enter the company's 10-digit CIK: ")
    try:
        normalized_cik = normalize_cik(cik_input)
    except ValueError as error:
        print(f"Error: {error}.", file=sys.stderr)
        raise SystemExit(1)

    output_directory = args.output_directory or Path(f"sec_data_{normalized_cik}")
    confirm_output_directory(output_directory)

    try:
        results = scrape_company(normalized_cik)
    except InvalidCompanyCIKError:
        print(
            "Error: this is not a valid company CIK in the SEC EDGAR API.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    save_results(results, output_directory, normalized_cik)
    save_metric_csvs(
        results["company_facts"],
        output_directory,
        normalized_cik,
        results["filing_facts"],
    )
    create_plot_html(
        output_directory,
        normalized_cik,
        results["submissions"].get("name", f"Company {normalized_cik}"),
    )


if __name__ == "__main__":
    main()