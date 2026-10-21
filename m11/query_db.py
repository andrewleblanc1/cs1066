"""
Interactive query tool for exoplanets.db.
Type any SQL query and see the results printed as a table.
Type 'help' to see example queries. Type 'quit' to exit.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "exoplanets.db")

HELP_TEXT = """
Available tables:
  stars          -- hostname, sy_vmag, st_teff, sy_dist, ra, dec
  planets        -- pl_name, hostname, pl_rade, pl_bmasse, pl_orbper,
                    pl_eqt, discoverymethod, disc_facility, tran_flag, pl_refname
  retrieval_runs -- retrieved_at, source_table, query, response_hash, transformations

Example queries:
  SELECT COUNT(*) FROM planets;
  SELECT COUNT(*) FROM stars;
  SELECT * FROM retrieval_runs;
  SELECT discoverymethod, COUNT(*) AS total FROM planets GROUP BY discoverymethod ORDER BY total DESC;
  SELECT hostname, COUNT(*) AS num_planets FROM planets GROUP BY hostname ORDER BY num_planets DESC LIMIT 10;
  SELECT pl_name, pl_orbper FROM planets WHERE pl_orbper IS NOT NULL ORDER BY pl_orbper DESC LIMIT 10;
  SELECT pl_name, hostname, pl_eqt FROM planets WHERE pl_eqt IS NOT NULL ORDER BY pl_eqt DESC LIMIT 10;
"""


def print_table(cursor):
    """Print query results as a plain text table."""
    rows = cursor.fetchall()
    if not rows:
        print("(no results)")
        return

    headers = [desc[0] for desc in cursor.description]
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val) if val is not None else "NULL"))

    fmt = "  ".join(f"{{:<{w}}}" for w in col_widths)
    divider = "  ".join("-" * w for w in col_widths)

    print(fmt.format(*headers))
    print(divider)
    for row in rows:
        print(fmt.format(*[str(v) if v is not None else "NULL" for v in row]))
    print(f"\n({len(rows)} row{'s' if len(rows) != 1 else ''})")


def print_schema(conn):
    """Print the schema for every table in the database."""
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence' ORDER BY name"
    ).fetchall()
    print("=" * 60)
    print("DATABASE SCHEMA")
    print("=" * 60)
    for (table_name,) in tables:
        print(f"\nTable: {table_name}")
        print("-" * 40)
        columns = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        for col in columns:
            _, name, dtype, notnull, default, pk = col
            flags = []
            if pk:
                flags.append("PRIMARY KEY")
            if notnull:
                flags.append("NOT NULL")
            flag_str = f"  [{', '.join(flags)}]" if flags else ""
            print(f"  {name:<20} {dtype}{flag_str}")
    print("\n" + "=" * 60 + "\n")


def run():
    conn = sqlite3.connect(DB_PATH)
    print(f"Connected to {DB_PATH}\n")
    print_schema(conn)
    print("Type a SQL query and press Enter. Type 'help' for examples, 'quit' to exit.\n")

    while True:
        try:
            query = input("sql> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not query:
            continue
        if query.lower() in ("quit", "exit", "q"):
            print("Exiting.")
            break
        if query.lower() == "help":
            print(HELP_TEXT)
            continue

        try:
            cursor = conn.execute(query)
            if cursor.description:
                print()
                print_table(cursor)
            else:
                print(f"OK ({cursor.rowcount} rows affected)")
            print()
        except sqlite3.Error as e:
            print(f"Error: {e}\n")

    conn.close()


if __name__ == "__main__":
    run()
