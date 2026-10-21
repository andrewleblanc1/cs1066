"""
Web interface for finding the top 5 most Earth-like exoplanets
within user-specified ranges for:
  pl_rade   -- planet radius (Earth radii)
  pl_orbper -- orbital period (days)
  pl_eqt    -- equilibrium temperature (K)

Earth reference values used for ranking:
  pl_rade   = 1.0
  pl_orbper = 365.25
  pl_eqt    = 255
"""

import sqlite3
import json
import os
import math
from flask import Flask, request, render_template_string

app = Flask(__name__)

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "exoplanets.db")
RESULTS_DIR = os.path.join(BASE_DIR, "viewlist_results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# Earth reference values for scoring
EARTH = {"pl_rade": 1.0, "pl_orbper": 365.25, "pl_eqt": 255.0}

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Exoplanet View List</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; }
    h1   { color: #1a1a2e; }
    h2   { color: #16213e; margin-top: 30px; }
    .field-group { display: flex; gap: 16px; align-items: center; margin-bottom: 12px; }
    .field-group label { width: 260px; font-weight: bold; }
    .field-group input { width: 100px; padding: 4px 8px; font-size: 14px; }
    button { margin-top: 16px; padding: 10px 24px; font-size: 16px;
             background: #0f3460; color: white; border: none; cursor: pointer; border-radius: 4px; }
    button:hover { background: #16213e; }
    table  { border-collapse: collapse; width: 100%; margin-top: 16px; }
    th, td { border: 1px solid #ccc; padding: 8px 12px; text-align: left; }
    th     { background: #0f3460; color: white; }
    tr:nth-child(even) { background: #f2f2f2; }
    .score { color: #555; font-size: 13px; }
    .saved { color: green; margin-top: 10px; font-size: 14px; }
    .error { color: red; }
    .none  { color: #888; font-style: italic; }
  </style>
</head>
<body>
  <h1>Exoplanet View List</h1>
  <p>Enter a range for each field. The top 5 planets most similar to Earth
     within those ranges will be shown.</p>
  <p class="score">Earth reference: radius = 1.0 R⊕ &nbsp;|&nbsp;
     period = 365.25 days &nbsp;|&nbsp; eq. temp = 255 K</p>
  <p><strong>Earth-likeness score:</strong> measures how closely a planet resembles Earth
     across the three fields. A score of <strong>0.0</strong> would mean a perfect match to Earth.
     <strong>Lower scores</strong> indicate planets more similar to Earth;
     <strong>higher scores</strong> indicate planets that differ more from Earth.</p>

  <form method="POST">
    <h2>Planet Radius (Earth radii)</h2>
    <div class="field-group">
      <label>Min pl_rade</label>
      <input type="number" step="any" name="rade_min" value="{{ rade_min }}"
             min="{{ bounds.rade_db_min }}" max="{{ bounds.rade_db_max }}">
      <label>Max pl_rade</label>
      <input type="number" step="any" name="rade_max" value="{{ rade_max }}"
             min="{{ bounds.rade_db_min }}" max="{{ bounds.rade_db_max }}">
    </div>
    <p class="score">Valid range: {{ bounds.rade_db_min }} – {{ bounds.rade_db_max }} R⊕</p>

    <h2>Orbital Period (days)</h2>
    <div class="field-group">
      <label>Min pl_orbper</label>
      <input type="number" step="any" name="orbper_min" value="{{ orbper_min }}"
             min="{{ bounds.orbper_db_min }}" max="{{ bounds.orbper_db_max }}">
      <label>Max pl_orbper</label>
      <input type="number" step="any" name="orbper_max" value="{{ orbper_max }}"
             min="{{ bounds.orbper_db_min }}" max="{{ bounds.orbper_db_max }}">
    </div>
    <p class="score">Valid range: {{ bounds.orbper_db_min }} – {{ bounds.orbper_db_max }} days</p>

    <h2>Equilibrium Temperature (K)</h2>
    <div class="field-group">
      <label>Min pl_eqt</label>
      <input type="number" step="any" name="eqt_min" value="{{ eqt_min }}"
             min="{{ bounds.eqt_db_min }}" max="{{ bounds.eqt_db_max }}">
      <label>Max pl_eqt</label>
      <input type="number" step="any" name="eqt_max" value="{{ eqt_max }}"
             min="{{ bounds.eqt_db_min }}" max="{{ bounds.eqt_db_max }}">
    </div>
    <p class="score">Valid range: {{ bounds.eqt_db_min }} – {{ bounds.eqt_db_max }} K</p>

    <button type="submit">Find Top 5</button>
  </form>

  {% if error %}
    <p class="error">{{ error }}</p>
  {% endif %}

  {% if results is not none %}
    <h2>Top 5 Results</h2>
    {% if results %}
      <table>
        <tr>
          <th>#</th>
          <th>Planet</th>
          <th>Host Star</th>
          <th>Radius (R⊕)</th>
          <th>Period (days)</th>
          <th>Eq. Temp (K)</th>
          <th>Earth-likeness score</th>
        </tr>
        {% for r in results %}
        <tr>
          <td>{{ loop.index }}</td>
          <td>{{ r.pl_name }}</td>
          <td>{{ r.hostname }}</td>
          <td>{{ r.pl_rade if r.pl_rade is not none else '—' }}</td>
          <td>{{ r.pl_orbper if r.pl_orbper is not none else '—' }}</td>
          <td>{{ r.pl_eqt if r.pl_eqt is not none else '—' }}</td>
          <td class="score">{{ r.score }}</td>
        </tr>
        {% endfor %}
      </table>
      {% if saved %}
        <p class="saved">Results saved to {{ saved }}</p>
      {% endif %}
    {% else %}
      <p class="none">No planets found matching those criteria.</p>
    {% endif %}
  {% endif %}
</body>
</html>
"""

DEFAULTS = {
    "rade_min": 0.5, "rade_max": 2.0,
    "orbper_min": 50, "orbper_max": 700,
    "eqt_min": 150,  "eqt_max": 400,
}


def get_field_bounds():
    """Query the database for the actual min/max of each field."""
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("""
        SELECT
            MIN(pl_rade),   MAX(pl_rade),
            MIN(pl_orbper), MAX(pl_orbper),
            MIN(pl_eqt),    MAX(pl_eqt)
        FROM planets
    """).fetchone()
    conn.close()
    return {
        "rade_db_min":   row[0], "rade_db_max":   row[1],
        "orbper_db_min": row[2], "orbper_db_max": row[3],
        "eqt_db_min":    row[4], "eqt_db_max":   row[5],
    }


BOUNDS = get_field_bounds()


def earth_likeness_score(row):
    """
    Normalized Euclidean distance from Earth across the three fields.
    Lower = more Earth-like. Fields are normalized by their Earth reference
    value so each contributes equally regardless of units.
    """
    def term(val, ref):
        return ((val - ref) / ref) ** 2 if val is not None else 0

    dist = math.sqrt(
        term(row["pl_rade"],   EARTH["pl_rade"]) +
        term(row["pl_orbper"], EARTH["pl_orbper"]) +
        term(row["pl_eqt"],    EARTH["pl_eqt"])
    )
    return round(dist, 4)


def query_planets(rade_min, rade_max, orbper_min, orbper_max, eqt_min, eqt_max):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT pl_name, hostname, pl_rade, pl_orbper, pl_eqt
        FROM planets
        WHERE pl_rade   BETWEEN ? AND ?
          AND pl_orbper BETWEEN ? AND ?
          AND pl_eqt    BETWEEN ? AND ?
        """,
        (rade_min, rade_max, orbper_min, orbper_max, eqt_min, eqt_max),
    ).fetchall()
    conn.close()

    scored = []
    seen = set()
    for row in rows:
        key = row["pl_name"]
        if key in seen:
            continue
        seen.add(key)
        rec = dict(row)
        rec["score"] = earth_likeness_score(rec)
        scored.append(rec)

    scored.sort(key=lambda r: r["score"])
    return scored[:5]


@app.route("/", methods=["GET", "POST"])
def index():
    context = {**DEFAULTS, "results": None, "error": None, "saved": None, "bounds": BOUNDS}

    if request.method == "POST":
        try:
            rade_min   = float(request.form["rade_min"])
            rade_max   = float(request.form["rade_max"])
            orbper_min = float(request.form["orbper_min"])
            orbper_max = float(request.form["orbper_max"])
            eqt_min    = float(request.form["eqt_min"])
            eqt_max    = float(request.form["eqt_max"])

            context.update({
                "rade_min": rade_min, "rade_max": rade_max,
                "orbper_min": orbper_min, "orbper_max": orbper_max,
                "eqt_min": eqt_min, "eqt_max": eqt_max,
            })

            errors = []
            if rade_min > rade_max:
                errors.append("Planet radius: min cannot be greater than max.")
            if orbper_min > orbper_max:
                errors.append("Orbital period: min cannot be greater than max.")
            if eqt_min > eqt_max:
                errors.append("Equilibrium temperature: min cannot be greater than max.")
            if errors:
                context["error"] = " ".join(errors)
                return render_template_string(HTML, **context)

            results = query_planets(
                rade_min, rade_max, orbper_min, orbper_max, eqt_min, eqt_max
            )
            context["results"] = results

            if results:
                filename = (
                    f"rade_{rade_min}-{rade_max}_"
                    f"orbper_{orbper_min}-{orbper_max}_"
                    f"eqt_{eqt_min}-{eqt_max}.json"
                )
                filepath = os.path.join(RESULTS_DIR, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=2)
                context["saved"] = filepath

        except ValueError:
            context["error"] = "Please enter valid numbers in all fields."

    return render_template_string(HTML, **context)


if __name__ == "__main__":
    print(f"Database: {DB_PATH}")
    print("Open http://localhost:5000 in your browser.")
    app.run(debug=False)
