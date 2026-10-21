"""
Reads exoplanets.json and exoplanets_metadata.json and loads the data
into a SQLite database (exoplanets.db) using the two-table schema:
  stars          -- one row per host star
  planets        -- one row per planet/reference entry
  retrieval_runs -- one row per program run (provenance)
"""

import sqlite3
import json
import os

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "exoplanets.db")
DATA_JSON = os.path.join(BASE_DIR, "exoplanets.json")
META_JSON = os.path.join(BASE_DIR, "exoplanets_metadata.json")

# ── Star-level columns (shared across planets of the same host) ──────────────
STAR_FIELDS = {"sy_vmag", "st_teff", "sy_dist", "ra", "dec"}


def create_tables(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS stars (
            hostname  TEXT PRIMARY KEY,
            sy_vmag   REAL,
            st_teff   REAL,
            sy_dist   REAL,
            ra        REAL,
            dec       REAL
        );

        CREATE TABLE IF NOT EXISTS planets (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            pl_name         TEXT NOT NULL,
            hostname        TEXT NOT NULL REFERENCES stars(hostname),
            pl_rade         REAL,
            pl_bmasse       REAL,
            pl_orbper       REAL,
            pl_eqt          REAL,
            discoverymethod TEXT,
            disc_facility   TEXT,
            tran_flag       INTEGER,
            pl_refname      TEXT
        );

        CREATE TABLE IF NOT EXISTS retrieval_runs (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            retrieved_at    TEXT NOT NULL,
            source_url      TEXT NOT NULL,
            source_table    TEXT NOT NULL,
            query           TEXT NOT NULL,
            selected_fields TEXT NOT NULL,
            response_hash   TEXT NOT NULL,
            transformations TEXT NOT NULL
        );
    """)
    conn.commit()


def load_records(conn, records):
    """Insert stars (deduplicated) then planets."""
    stars_seen = {}

    for rec in records:
        hostname = rec.get("hostname")
        if hostname and hostname not in stars_seen:
            stars_seen[hostname] = {f: rec.get(f) for f in STAR_FIELDS}

    # Insert stars
    conn.executemany(
        """
        INSERT OR IGNORE INTO stars (hostname, sy_vmag, st_teff, sy_dist, ra, dec)
        VALUES (:hostname, :sy_vmag, :st_teff, :sy_dist, :ra, :dec)
        """,
        [{"hostname": h, **vals} for h, vals in stars_seen.items()],
    )

    # Insert planets
    conn.executemany(
        """
        INSERT INTO planets
            (pl_name, hostname, pl_rade, pl_bmasse, pl_orbper, pl_eqt,
             discoverymethod, disc_facility, tran_flag, pl_refname)
        VALUES
            (:pl_name, :hostname, :pl_rade, :pl_bmasse, :pl_orbper, :pl_eqt,
             :discoverymethod, :disc_facility, :tran_flag, :pl_refname)
        """,
        records,
    )

    conn.commit()
    print(f"Inserted {len(stars_seen)} stars and {len(records)} planet records.")


def load_metadata(conn, meta):
    """Insert one provenance row from the metadata dict."""
    conn.execute(
        """
        INSERT INTO retrieval_runs
            (retrieved_at, source_url, source_table, query,
             selected_fields, response_hash, transformations)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            meta["retrieved_at"],
            meta["source_url"],
            meta["source_table"],
            meta["query"],
            json.dumps(meta["selected_fields"]),
            meta["response_hash"]["value"],
            json.dumps(meta["transformations"]),
        ),
    )
    conn.commit()
    print("Inserted 1 retrieval_run provenance record.")


if __name__ == "__main__":
    # Load source files
    with open(DATA_JSON, encoding="utf-8") as f:
        records = json.load(f)
    with open(META_JSON, encoding="utf-8") as f:
        meta = json.load(f)

    # Connect (creates the file if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    create_tables(conn)
    load_records(conn, records)
    load_metadata(conn, meta)

    conn.close()
    print(f"Database written to: {DB_PATH}")
