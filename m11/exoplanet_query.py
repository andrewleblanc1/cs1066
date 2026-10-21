"""
NASA Exoplanet Archive query using the TAP (Table Access Protocol) service.
Retrieves planet and host-star data and saves it to a CSV file.
"""

import requests
import csv
import json
import os
import hashlib
import argparse
from datetime import datetime, timezone

# NASA Exoplanet Archive TAP endpoint
TAP_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"

# ADQL query template — {top_clause} is filled in at runtime
QUERY_TEMPLATE = """
SELECT {top_clause}
    pl_name,
    hostname,
    pl_rade,
    pl_bmasse,
    pl_orbper,
    pl_eqt,
    sy_vmag,
    st_teff,
    sy_dist,
    ra,
    dec,
    discoverymethod,
    disc_facility,
    tran_flag,
    pl_refname
FROM ps
WHERE pl_name IS NOT NULL
ORDER BY pl_name
"""


def build_query(limit=None):
    """Return the ADQL query string, optionally capped at `limit` rows."""
    top_clause = f"TOP {limit}" if limit else ""
    return QUERY_TEMPLATE.format(top_clause=top_clause).strip()

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "exoplanets.csv")
OUTPUT_JSON = os.path.join(os.path.dirname(__file__), "exoplanets.json")
OUTPUT_META = os.path.join(os.path.dirname(__file__), "exoplanets_metadata.json")

SOURCE_TABLE = "ps"
SELECTED_FIELDS = [
    "pl_name",
    "hostname",
    "pl_rade",
    "pl_bmasse",
    "pl_orbper",
    "pl_eqt",
    "sy_vmag",
    "st_teff",
    "sy_dist",
    "ra",
    "dec",
    "discoverymethod",
    "disc_facility",
    "tran_flag",
    "pl_refname",
]


def fetch_exoplanet_data(limit=None):
    """Query the NASA Exoplanet Archive and return rows, raw bytes, and retrieval timestamp."""
    query = build_query(limit)
    params = {
        "query": query,
        "format": "json",
    }

    limit_msg = f" (limit: {limit})" if limit else " (no limit)"
    print(f"Querying NASA Exoplanet Archive{limit_msg}...")
    retrieved_at = datetime.now(timezone.utc).isoformat()
    response = requests.get(TAP_URL, params=params, timeout=60)
    response.raise_for_status()

    raw_bytes = response.content
    data = response.json()
    print(f"Retrieved {len(data)} records.")
    return data, raw_bytes, retrieved_at, query


def save_to_csv(records, filepath):
    """Save a list of dicts to a CSV file."""
    if not records:
        print("No records to save.")
        return

    fieldnames = list(records[0].keys())
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    print(f"CSV saved to: {filepath}")


def save_to_json(records, filepath):
    """Save a list of dicts to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    print(f"JSON saved to: {filepath}")


def save_metadata(retrieved_at, raw_bytes, transformations, filepath, query=None):
    """Build and save a metadata record describing the retrieval run."""
    response_hash = hashlib.sha256(raw_bytes).hexdigest()

    metadata = {
        "retrieved_at": retrieved_at,
        "source_url": TAP_URL,
        "source_table": SOURCE_TABLE,
        "query": query if query else build_query(),
        "selected_fields": SELECTED_FIELDS,
        "response_hash": {
            "algorithm": "sha256",
            "value": response_hash,
        },
        "transformations": transformations,
        "output_files": {
            "csv": OUTPUT_FILE,
            "json": OUTPUT_JSON,
            "metadata": filepath,
        },
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"Metadata saved to: {filepath}")


def print_sample(records, n=3):
    """Print the first n records to the console."""
    print(f"\n--- Sample ({min(n, len(records))} of {len(records)} records) ---")
    for record in records[:n]:
        print(f"  Planet:        {record.get('pl_name')}")
        print(f"  Host star:     {record.get('hostname')}")
        print(f"  Radius (R⊕):   {record.get('pl_rade')}")
        print(f"  Mass (M⊕):     {record.get('pl_bmasse')}")
        print(f"  Period (days): {record.get('pl_orbper')}")
        print(f"  Eq. Temp (K):  {record.get('pl_eqt')}")
        print(f"  V magnitude:   {record.get('sy_vmag')}")
        print(f"  Stellar Teff:  {record.get('st_teff')}")
        print(f"  Distance (pc): {record.get('sy_dist')}")
        print(f"  RA:            {record.get('ra')}")
        print(f"  Dec:           {record.get('dec')}")
        print(f"  Discovery:     {record.get('discoverymethod')}")
        print(f"  Facility:      {record.get('disc_facility')}")
        print(f"  Transit flag:  {record.get('tran_flag')}")
        print(f"  Reference:     {record.get('pl_refname')}")
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download exoplanet data from NASA.")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of rows to retrieve (default: all rows)",
    )
    args = parser.parse_args()

    records, raw_bytes, retrieved_at, query = fetch_exoplanet_data(limit=args.limit)

    # No transformations are applied: data is stored exactly as received.
    transformations = [
        "none — records written to CSV and JSON exactly as returned by the API"
    ]

    print_sample(records)
    save_to_csv(records, OUTPUT_FILE)
    save_to_json(records, OUTPUT_JSON)
    save_metadata(retrieved_at, raw_bytes, transformations, OUTPUT_META, query=query)
