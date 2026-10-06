import csv
import re
from pathlib import Path
from typing import TypedDict

import streamlit as st


class Employee(TypedDict):
    employee_id: str
    name: str
    role: str
    level: str
    department: str
    location: str
    reports_to: str
    comp_usd: int
    evidence: list[str]
    evidence_source_count: int


ROSTER_PATH = (
    Path(__file__).resolve().parents[1]
    / "data_room"
    / "people"
    / "employee_roster.csv"
)
BIOS_PATH = ROSTER_PATH.parent / "key_employee_bios.csv"
NOTES_PATH = ROSTER_PATH.parent / "key_personnel_notes.txt"
EMPLOYEE_ID_PATTERN = re.compile(r"E\d+")
NOTE_PROFILE_PATTERN = re.compile(r"(?m)^[^\n]*\((E\d{3,4})\)(?:\s*⚠️[^\n]*)?$")
WEIGHT_DEFAULTS = {
    "Strategic importance": 15,
    "Unique knowledge / IP": 15,
    "Demonstrated impact": 15,
    "Performance / execution": 10,
    "Replaceability": 10,
    "Customer / revenue dependency": 10,
    "Integration value": 10,
    "Key-person risk": 5,
    "Retention / flight risk": 5,
    "Role-overlap fit": 5,
}
PERSONAL_EVIDENCE = re.compile(
    r"\b(personal situation|family|child(?:ren)?|spouse|marital|pregnan\w*|"
    r"disabilit\w*|medical|religion|gender|ethnicit\w*|nationality)\b",
    re.IGNORECASE,
)
FACTORS = {
    "Strategic importance": {
        "strong": re.compile(
            r"\b(core|critical|key|strategic|proprietary|differentiation|"
            r"acquisition value|M&A value|single point of failure)\b",
            re.IGNORECASE,
        ),
        "support": re.compile(
            r"\b(owns?|leads?|architect|platform|product|customer|revenue|"
            r"enables?|responsible for)\b",
            re.IGNORECASE,
        ),
    },
    "Unique knowledge / IP": {
        "strong": re.compile(
            r"\b(proprietary|single point of failure|tribal knowledge|"
            r"limited documentation|patents?|patent pending|only owner|"
            r"hard to replace|unique expertise)\b",
            re.IGNORECASE,
        ),
        "support": re.compile(
            r"\b(architect|architecture|owns?|speciali[sz]ation|expertise|"
            r"knowledge|intellectual property|IP)\b",
            re.IGNORECASE,
        ),
    },
    "Demonstrated impact": {
        "strong": re.compile(
            r"(\$[\d,.]+\s*[MBK]?\b|\b\d+(?:\.\d+)?\s*%|\b\d+\+?\s*(?:ARR|"
            r"requests|customers|papers|features|deals|users|GB|TB|NPS|"
            r"months|hours|minutes|deploys))",
            re.IGNORECASE,
        ),
        "support": re.compile(
            r"\b(impact|achievement|increased|reduced|saved|grew|generated|"
            r"enabled|improved|launched|uptime|quota|conversion|NPS|attainment)\b",
            re.IGNORECASE,
        ),
    },
    "Performance / execution": {
        "strong": re.compile(
            r"\b(quota attainment|on[- ]time delivery|shipped \d+|"
            r"zero (?:security )?incidents|clean audits|met (?:or )?exceeded)\b",
            re.IGNORECASE,
        ),
        "support": re.compile(
            r"\b(delivered|shipped|built|implemented|launched|led|achieved|"
            r"execution|performance|successful|reduced|improved)\b",
            re.IGNORECASE,
        ),
    },
    "Replaceability": {
        "strong": re.compile(
            r"\b(no (?:formal )?(?:successor|backup)|single point of failure|"
            r"limited documentation|tribal knowledge|hard to replace|"
            r"only (?:owner|expert)|weak succession)\b",
            re.IGNORECASE,
        ),
        "support": re.compile(
            r"\b(succession|successor|backup|cross[- ]train|documentation|"
            r"knowledge transfer|replace)\b",
            re.IGNORECASE,
        ),
    },
    "Customer / revenue dependency": {
        "strong": re.compile(
            r"\b(top \d+ (?:customers|accounts)|\d+% of (?:total )?ARR|"
            r"\$[\d,.]+\s*[MBK]?\s*ARR|owns? (?:the )?(?:top )?\d* ?(?:accounts|"
            r"customer relationships)|pipeline)\b",
            re.IGNORECASE,
        ),
        "support": re.compile(
            r"\b(customer|account|ARR|revenue|sales|quota|deal|client|"
            r"customer-facing)\b",
            re.IGNORECASE,
        ),
    },
    "Integration value": {
        "strong": re.compile(
            r"\b(M&A value|integration|post[- ]acquisition|acquisition|"
            r"fundraising|financial controls|system integration)\b",
            re.IGNORECASE,
        ),
        "support": re.compile(
            r"\b(cross[- ]functional|combined organization|migration|"
            r"transition|compliance|audit|board reporting|unit economics)\b",
            re.IGNORECASE,
        ),
    },
    "Key-person risk": {
        "strong": re.compile(
            r"\b(single point of failure|heavily relies? on|no (?:named )?"
            r"(?:backup|successor)|limited documentation|tribal knowledge|"
            r"critical (?:owner|dependency))\b",
            re.IGNORECASE,
        ),
        "support": re.compile(
            r"\b(criticality|key person|team dependency|only owner|"
            r"succession plan: none)\b",
            re.IGNORECASE,
        ),
    },
}


def load_evidence_sources() -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    with NOTES_PATH.open(encoding="utf-8") as notes_file:
        notes_text = notes_file.read()
    lines = notes_text.splitlines()
    headers = list(NOTE_PROFILE_PATTERN.finditer(notes_text))
    note_evidence: dict[str, list[str]] = {}
    for index, header in enumerate(headers):
        start = notes_text.count("\n", 0, header.start()) + 1
        end = (
            notes_text.count("\n", 0, headers[index + 1].start()) + 1
            if index + 1 < len(headers)
            else len(lines)
        )
        note_evidence[header.group(1)] = [
            line.strip().lstrip("- ").strip()
            for line in lines[start:end]
            if line.strip()
            and not PERSONAL_EVIDENCE.search(line)
            and line.strip().startswith("-")
        ]

    with BIOS_PATH.open(newline="", encoding="utf-8") as bios_file:
        bios_rows = list(csv.DictReader(bios_file))
    roster_rows: list[dict[str, str]] = []
    with ROSTER_PATH.open(newline="", encoding="utf-8") as roster_file:
        roster_rows = [
            row
            for row in csv.DictReader(roster_file)
            if EMPLOYEE_ID_PATTERN.fullmatch((row.get("employee_id") or "").strip())
        ]

    bios_by_id: dict[str, list[str]] = {}
    for bio in bios_rows:
        bio_name = re.sub(r"[^a-z0-9]", "", (bio.get("Name") or "").casefold())
        candidates = [
            row
            for row in roster_rows
            if re.sub(r"[^a-z0-9]", "", (row.get("name") or "").casefold()) == bio_name
        ]
        if len(candidates) > 1:
            bio_title = re.sub(r"[^a-z0-9]", "", (bio.get("Title") or "").casefold())
            candidates = [
                row
                for row in candidates
                if re.sub(r"[^a-z0-9]", "", (row.get("role") or "").casefold())
                == bio_title
            ]
        if len(candidates) != 1:
            continue
        employee_id = candidates[0]["employee_id"]
        metrics = [
            f"Biography metric: {bio[field].strip()}"
            for field in ("Key Metric 1", "Key Metric 2", "Key Metric 3")
            if bio.get(field, "").strip()
            and not PERSONAL_EVIDENCE.search(bio[field])
        ]
        bios_by_id[employee_id] = metrics
    return note_evidence, bios_by_id


def score_factor(factor: str, evidence: list[str]) -> tuple[int | None, list[str]]:
    if factor == "Strategic importance":
        return None, []
    if factor == "Role-overlap fit":
        return None, []
    if factor == "Retention / flight risk":
        risk_lines = [line for line in evidence if "retention risk:" in line.casefold()]
        if not risk_lines:
            return None, []
        text = " ".join(risk_lines).casefold()
        if any(term in text for term in ("very high", "critical", "urgent", "offers", "recruiter calls")):
            return 100, risk_lines
        if "medium-high" in text or "medium high" in text:
            return 70, risk_lines
        if "high" in text:
            return 80, risk_lines
        if "medium" in text:
            return 60, risk_lines
        if "low" in text:
            return 20, risk_lines
        return None, risk_lines

    patterns = FACTORS[factor]
    if factor == "Replaceability":
        difficult = [line for line in evidence if patterns["strong"].search(line)]
        clear_coverage = [
            line
            for line in evidence
            if re.search(
                r"\b(well[- ]documented|multiple qualified backups|strong bench|"
                r"credible successor|documented successor)\b",
                line,
                re.IGNORECASE,
            )
        ]
        matched = list(dict.fromkeys(difficult + clear_coverage))
        if difficult:
            return min(100, 60 + 20 * (len(difficult) - 1)), matched
        if clear_coverage:
            return 20, matched
        return None, []
    strong = [line for line in evidence if patterns["strong"].search(line)]
    if factor == "Demonstrated impact":
        strong = [
            line
            for line in strong
            if not re.search(
                r"\b(compensation|salary|base pay|market pay|below market)\b",
                line,
                re.IGNORECASE,
            )
        ]
    supporting = [line for line in evidence if patterns["support"].search(line)]
    matched = list(dict.fromkeys(strong + supporting))
    if not matched:
        return None, []
    if len(strong) >= 3:
        return 100, matched
    if len(strong) == 2:
        return 80, matched
    if len(strong) == 1:
        return 60 if len(supporting) <= 1 else 80, matched
    return (40 if len(supporting) == 1 else 60), matched


def assess_employee(
    person: Employee, weights: dict[str, int]
) -> tuple[float | None, int, dict[str, tuple[int | None, list[str]]]]:
    factors: dict[str, tuple[int | None, list[str]]] = {}
    weighted_score = 0.0
    available_weight = 0
    for factor, weight in weights.items():
        score, evidence = score_factor(factor, person["evidence"])
        factors[factor] = (score, evidence)
        if score is not None and weight > 0:
            weighted_score += score * weight
            available_weight += weight
    overall = weighted_score / available_weight if available_weight else None
    evidence_coverage = round(100 * available_weight / max(sum(weights.values()), 1))
    return overall, evidence_coverage, factors


def load_roster() -> list[Employee]:
    required_columns = {"employee_id", "name", "role", "department", "location", "comp_usd"}
    people: list[Employee] = []
    notes, bios = load_evidence_sources()

    with ROSTER_PATH.open(newline="", encoding="utf-8") as roster_file:
        reader = csv.DictReader(roster_file)
        if not reader.fieldnames or not required_columns.issubset(reader.fieldnames):
            raise ValueError("The roster is missing one or more required columns.")

        seen_ids: set[str] = set()
        for row in reader:
            employee_id = (row.get("employee_id") or "").strip()
            if not EMPLOYEE_ID_PATTERN.fullmatch(employee_id):
                continue

            if employee_id in seen_ids:
                raise ValueError(f"The roster contains duplicate employee ID {employee_id}.")
            seen_ids.add(employee_id)

            raw_compensation = (row.get("comp_usd") or "").strip()
            try:
                compensation = int(raw_compensation)
            except ValueError as error:
                raise ValueError(
                    f"Employee {employee_id} has missing or invalid compensation."
                ) from error
            if compensation < 0:
                raise ValueError(f"Employee {employee_id} has negative compensation.")

            people.append(
                Employee(
                    employee_id=employee_id,
                    name=(row.get("name") or "").strip(),
                    role=(row.get("role") or "").strip(),
                    level=(row.get("level") or "").strip(),
                    department=(row.get("department") or "").strip(),
                    location=(row.get("location") or "").strip(),
                    reports_to=(row.get("reports_to") or "").strip(),
                    comp_usd=compensation,
                    evidence=notes.get(employee_id, []) + bios.get(employee_id, []),
                    evidence_source_count=int(employee_id in notes) + int(employee_id in bios),
                )
            )

    if not people:
        raise ValueError("The roster does not contain any employee records.")

    return sorted(people, key=lambda person: (-person["comp_usd"], person["employee_id"]))


st.set_page_config(page_title="Headcount Scenario Planner", layout="wide")
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --canvas: #f5f6ef;
    --ink: #17231e;
    --muted: #66716b;
    --line: #d9ded6;
    --green: #17684f;
    --green-deep: #145c46;
    --orange: #ed7a3b;
}

[data-testid="stAppViewContainer"] {
    background: var(--canvas);
    color: var(--ink);
}
[data-testid="stSidebar"] {
    background: #e9eee7;
    color: var(--ink);
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] summary {
    color: var(--ink);
}
[data-testid="stSidebar"] [data-testid="stExpander"] {
    background: #f8f9f4;
}
[data-testid="stHeader"] {
    background: transparent;
}
[data-testid="stMainBlockContainer"] {
    max-width: 1240px;
    padding-top: 1.5rem;
    padding-bottom: 4rem;
}
html,
body,
[data-testid="stAppViewContainer"],
[data-testid="stSidebar"] {
    font-family: "Space Grotesk", "Aptos", sans-serif;
}
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 0 1.1rem;
    border-bottom: 1px solid var(--line);
    color: var(--muted);
    font-family: "DM Mono", monospace;
    font-size: .85rem;
}
.brand {
    color: var(--ink);
    font-family: "Space Grotesk", sans-serif;
    font-weight: 700;
    letter-spacing: .16em;
}
.brand span {
    color: var(--green);
}
.context {
    display: flex;
    align-items: center;
    gap: .55rem;
}
.status-dot {
    width: .55rem;
    height: .55rem;
    border-radius: 50%;
    background: var(--orange);
}
.hero {
    max-width: 760px;
    margin: 4.2rem 0 3.5rem;
}
.eyebrow {
    margin: 0 0 .9rem;
    color: var(--muted);
    font-family: "DM Mono", monospace;
    font-size: .78rem;
    letter-spacing: .12em;
    text-transform: uppercase;
}
.hero h1 {
    margin: 0;
    color: var(--ink);
    font-size: clamp(3.4rem, 7vw, 6.2rem);
    font-weight: 700;
    letter-spacing: -.075em;
    line-height: .98;
}
.hero h1 em {
    color: var(--green);
    font-style: normal;
}
.hero p:last-child {
    max-width: 620px;
    margin: 1.35rem 0 0;
    color: var(--muted);
    font-size: 1.15rem;
    line-height: 1.6;
}
.st-key-scenario_control {
    margin: 0 0 1.5rem;
    padding: 1.8rem 2rem 1.25rem;
    border-radius: 3px;
    background: var(--green);
    color: #fff;
}
.scenario-heading {
    display: flex;
    align-items: end;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 1rem;
}
.scenario-heading .eyebrow {
    margin-bottom: .45rem;
    color: #cae0d4;
}
.scenario-heading h2 {
    margin: 0;
    color: #fff;
    font-size: 1.55rem;
    letter-spacing: -.04em;
}
.st-key-scenario_control [data-testid="stSlider"] {
    padding-top: .2rem;
}
.st-key-scenario_control [data-testid="stSlider"] label,
.st-key-scenario_control [data-testid="stSlider"] [data-testid="stTickBarMin"],
.st-key-scenario_control [data-testid="stSlider"] [data-testid="stTickBarMax"] {
    color: #fff !important;
}
.st-key-scenario_control [data-testid="stSlider"] label {
    font-size: 1.15rem;
    font-weight: 600;
}
.st-key-scenario_control [data-testid="stSlider"] .react-aria-SliderTrack > div:first-child {
    background: #000 !important;
}
.st-key-scenario_control [data-testid="stSlider"] .react-aria-SliderTrack > div > div:first-child {
    height: 5px !important;
    border-radius: 999px !important;
    background: #000 !important;
    background-image: none !important;
}
.st-key-scenario_control [data-testid="stSlider"] .react-aria-SliderThumb {
    width: 20px !important;
    height: 20px !important;
    border: 3px solid #fff !important;
    border-radius: 50% !important;
    background: #000 !important;
    box-shadow: 0 1px 6px #102d2370 !important;
}
.st-key-scenario_control [data-testid="stSlider"] .react-aria-SliderThumb:focus,
.st-key-scenario_control [data-testid="stSlider"] .react-aria-SliderThumb[data-focus-visible] {
    outline: 3px solid #fff !important;
    outline-offset: 3px !important;
}
.st-key-scenario_control [data-testid="stSlider"] [data-testid="stSliderThumbValue"] {
    color: #fff !important;
}
.st-key-scenario_control [data-testid="stSlider"] [data-testid="stSliderTickBar"] {
    color: #fff !important;
    font-family: "DM Mono", monospace;
    font-weight: 500;
}
.st-key-scenario_control [data-testid="stSlider"] [data-testid="stSliderTickBar"] * {
    color: #fff !important;
}
[data-testid="stAlert"] {
    color: #24312b !important;
}
[data-testid="stAlert"] p,
[data-testid="stAlert"] div,
[data-testid="stAlert"] span {
    color: #24312b !important;
}
.metrics-row {
    display: grid;
    grid-template-columns: 1.6fr 1fr 1fr;
    border-top: 1px solid var(--line);
    border-bottom: 1px solid var(--line);
}
.metric-card {
    min-height: 128px;
    padding: 1.4rem 1.5rem 1.3rem;
    border-right: 1px solid var(--line);
}
.metric-card:first-child {
    padding-left: 0;
}
.metric-card:last-child {
    border-right: 0;
}
.metric-label {
    margin-bottom: .65rem;
    color: var(--muted);
    font-family: "DM Mono", monospace;
    font-size: .76rem;
    letter-spacing: .04em;
    text-transform: uppercase;
}
.metric-value {
    color: var(--ink);
    font-size: clamp(1.8rem, 3.3vw, 2.55rem);
    font-weight: 700;
    letter-spacing: -.065em;
    line-height: 1.1;
}
.metric-card.primary .metric-value {
    color: var(--green);
}
.metric-note {
    margin-top: .35rem;
    color: var(--muted);
    font-size: .88rem;
}
.section-title {
    margin: 2.2rem 0 .4rem;
    color: var(--ink);
    font-size: 1.65rem;
    font-weight: 600;
    letter-spacing: -.045em;
}
.section-note {
    margin: 0 0 1rem;
    color: var(--muted);
}
[data-testid="stSlider"] label {
    line-height: 1.25;
}
[data-testid="stSidebar"] [data-testid="stSlider"] label {
    max-width: calc(100% - 3.2rem);
    overflow-wrap: anywhere;
    font-size: .9rem;
    font-weight: 500;
}
[data-testid="stSidebar"] [data-testid="stSlider"] [data-testid="stMarkdownContainer"] {
    color: var(--ink) !important;
}
[data-testid="stDataFrame"] {
    border: 1px solid var(--line);
    border-radius: 4px;
    overflow: hidden;
    color-scheme: light;
}
[data-testid="stExpander"] {
    border-color: var(--line);
    background: #fffefa;
}
[data-testid="stExpander"],
[data-testid="stExpander"] details,
[data-testid="stExpander"] details > summary,
[data-testid="stExpander"] details[open] > summary,
[data-testid="stExpander"] details > summary:hover,
[data-testid="stExpander"] details > summary:focus,
[data-testid="stExpander"] details > summary:active {
    background-color: #fffefa !important;
    color: var(--ink) !important;
}
[data-testid="stExpander"] details > summary {
    border-radius: 4px;
}
[data-testid="stExpander"] details > summary *,
[data-testid="stExpander"] details > summary svg {
    color: var(--ink) !important;
    fill: currentColor;
}
[data-testid="stExpander"] details[open] > summary {
    border-bottom: 1px solid var(--line);
}
[data-testid="stExpander"] details > summary:focus-visible {
    outline: 2px solid var(--green);
    outline-offset: 2px;
}
@media (max-width: 700px) {
    [data-testid="stMainBlockContainer"] {
        padding: 1rem 1rem 3rem;
    }
    .hero {
        margin: 3rem 0 2.5rem;
    }
    .hero h1 {
        font-size: clamp(3rem, 14vw, 5rem);
    }
    .st-key-scenario_control {
        padding: 1.25rem 1rem .8rem;
    }
    .scenario-heading {
        align-items: start;
        flex-direction: column;
    }
    .metrics-row {
        grid-template-columns: 1fr;
    }
    .metric-card, .metric-card:first-child {
        min-height: auto;
        padding: 1rem 0;
        border-right: 0;
        border-bottom: 1px solid var(--line);
    }
    .metric-card:last-child {
        border-bottom: 0;
    }
}
</style>
<header class="topbar">
  <div class="brand">EXAMPLE <span>AI</span></div>
  <div class="context"><span class="status-dot"></span>People planning / 2026</div>
</header>
<section class="hero">
  <p class="eyebrow">Acquisition diligence / workforce scenario</p>
  <h1>Build the team<br><em>that matters.</em></h1>
  <p>Model a retained team from the current roster. Prioritize by compensation or by a transparent, evidence-based score.</p>
</section>
""",
    unsafe_allow_html=True,
)

try:
    roster = load_roster()
except (OSError, csv.Error, ValueError) as error:
    st.error(f"Unable to load the employee roster: {error}")
    st.stop()

if "team_size" not in st.session_state:
    st.session_state["team_size"] = min(10, len(roster))

with st.container(key="scenario_control"):
    st.markdown(
        f"""
<div class="scenario-heading">
  <div><p class="eyebrow">Scenario control</p></div>
</div>
""",
        unsafe_allow_html=True,
    )
    headcount = st.slider(
        "Headcount to bring on",
        min_value=0,
        max_value=len(roster),
        step=1,
        key="team_size",
    )

st.sidebar.header("Scenario settings")
prioritize_by = st.sidebar.radio(
    "Prioritize bringing on by",
    ["Overall score", "Compensation"],
    help="Score ranking uses only job-related evidence found in the supplied company materials.",
)

with st.sidebar.expander("Factor weights", expanded=False):
    st.caption(
        "Weights are starting assumptions. Adjust them for the deal thesis. "
        "Weights for unknown factors are excluded and the remaining weights are normalized."
    )
    compact_factor_labels = {
        "Strategic importance": ("Strategy", "Strategic importance"),
        "Unique knowledge / IP": ("Knowledge / IP", "Unique knowledge and intellectual property"),
        "Demonstrated impact": ("Impact", "Demonstrated technical, product, revenue, cost, or operational impact"),
        "Performance / execution": ("Execution", "Performance and execution"),
        "Replaceability": ("Replaceability", "Replaceability and availability of a credible successor"),
        "Customer / revenue dependency": ("Customer / revenue", "Customer and revenue dependency"),
        "Integration value": ("Integration", "Post-acquisition integration value"),
        "Key-person risk": ("Key-person risk", "Key-person dependency risk"),
        "Retention / flight risk": ("Retention risk", "Retention and flight risk"),
        "Role-overlap fit": ("Role overlap", "Overlap with roles in the acquiring company"),
    }
    factor_weights = {
        factor: st.slider(
            compact_factor_labels[factor][0],
            min_value=0,
            max_value=30,
            value=default,
            step=1,
            key=f"weight-{factor}",
            help=compact_factor_labels[factor][1],
        )
        for factor, default in WEIGHT_DEFAULTS.items()
    }
    st.caption(
        f"Configured weight total: {sum(factor_weights.values())}. "
        "Strategic importance and role overlap are currently unknown because no deal thesis "
        "or acquirer organization data was supplied."
    )

assessed_people = []
for person in roster:
    overall, coverage, factor_results = assess_employee(person, factor_weights)
    scored_factors = sum(
        result[0] is not None for result in factor_results.values()
    )
    confidence = (
        "High"
        if coverage >= 60 and person["evidence_source_count"] >= 2
        else "Medium"
        if coverage >= 30 and person["evidence_source_count"] >= 1
        else "Low"
        if overall is not None
        else "Insufficient evidence"
    )
    assessed_people.append(
        {
            "person": person,
            "overall": overall,
            "coverage": coverage,
            "confidence": confidence,
            "scored_factors": scored_factors,
            "factors": factor_results,
        }
    )

if prioritize_by == "Overall score":
    ranked_people = sorted(
        assessed_people,
        key=lambda item: (
            item["overall"] is None,
            -(item["overall"] or 0),
            -item["coverage"],
            item["person"]["employee_id"],
        ),
    )
else:
    ranked_people = sorted(
        assessed_people,
        key=lambda item: (
            -item["person"]["comp_usd"],
            item["person"]["employee_id"],
        ),
    )

if prioritize_by == "Compensation":
    compensation_caption = (
        f"Showing the top {headcount} highest-paid employees by annual base compensation. "
        "When compensation is tied, employee ID in ascending order determines who ranks first."
    )
else:
    compensation_caption = ""

selected_assessments = ranked_people[:headcount]
selected_people = [item["person"] for item in selected_assessments]
total_cost = sum(person["comp_usd"] for person in selected_people)
average_cost = total_cost / headcount if headcount else 0
roster_share = headcount / len(roster) if roster else 0
mode_label = "overall score" if prioritize_by == "Overall score" else "annual compensation"
st.markdown(
    f"""
<p class="section-note">Prioritizing by <strong>{mode_label}</strong>. Scenario ranking is
decision support only: unknown factors are not treated as negative evidence, scores are
provisional, and rankings require human review. The overall score is a weighted average
over evidenced factors only. It is a retention-priority signal, not a measure of a person's
overall worth; compare it together with evidence coverage and confidence.</p>
""",
    unsafe_allow_html=True,
)
with st.expander("How the overall score works"):
    st.markdown(
        """
- Each factor is assigned a rule-based evidence signal from the supplied roster, biographies,
  and personnel notes. Ratings are shown from 0–100; a factor with no matching evidence is
  **Unknown**, not zero.
- The overall score is the weighted average of the factors with evidence. Unknown factors
  are omitted from that employee's denominator, so coverage and confidence are shown beside
  the score and scores with sparse evidence need particular caution.
- In score mode, ties are broken by evidence coverage, then employee ID. Profiles with no
  scored factors are shown as unranked and placed after scored profiles. In compensation
  mode, pay is sorted highest first, with employee ID breaking ties.
- Keyword-scored factors use a fixed 20-point evidence-signal scale (20/40/60/80/100);
  the factor evidence panel shows the exact matched source lines. Retention-risk labels
  map LOW/MEDIUM/MEDIUM-HIGH/HIGH/VERY HIGH to 20/60/70/80/100, respectively.
- Confidence is HIGH when at least 60% of configured weight is evidenced across two
  sources, MEDIUM at 30% with at least one source, LOW for a scored profile below that,
  and Insufficient evidence when no factor can be scored. These are triage labels, not
  statistical confidence intervals.
- Current default weights are: strategic importance 15%, unique knowledge/IP 15%,
  demonstrated impact 15%, performance/execution 10%, replaceability 10%,
  customer/revenue dependency 10%, integration value 10%, key-person risk 5%,
  retention/flight risk 5%, and role-overlap fit 5%. Adjust them in the sidebar.
- Higher retention/flight risk raises **retention urgency**, but is not evidence of lower
  employee value. Role-overlap fit is unknown until acquirer roles are supplied.
- Evidence matching is a first-pass screen, not a validated performance assessment.
  Verify the displayed source lines and make no employment decision from the ranking alone.
"""
    )
st.markdown(
    f"""
<section class="metrics-row" aria-label="Scenario summary">
  <div class="metric-card primary">
    <div class="metric-label">Annual base compensation</div>
    <div class="metric-value">${total_cost:,.0f}</div>
    <div class="metric-note">{headcount} of {len(roster)} rostered employees selected</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Average per person</div>
    <div class="metric-value">${average_cost:,.0f}</div>
    <div class="metric-note">Annual base compensation</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Share of current roster</div>
    <div class="metric-value">{roster_share:.0%}</div>
    <div class="metric-note">of {len(roster)} people</div>
  </div>
</section>
""",
    unsafe_allow_html=True,
)

if selected_people:
    st.markdown(
        '<h2 class="section-title">People in this scenario</h2>'
        +
        (
            f'<p class="section-note">{compensation_caption}</p>'
            if prioritize_by == "Compensation"
            else f'<p class="section-note">Prioritized by {mode_label}; compensation shown separately.</p>'
        ),
        unsafe_allow_html=True,
    )
    if prioritize_by == "Overall score":
        st.caption(
            "Scores summarize only matched, job-related source evidence. "
            "Strategic importance and role overlap remain unknown without the deal thesis "
            "and acquirer organization data."
        )
    low_confidence_selected = [
        item for item in selected_assessments if item["confidence"] != "High"
    ]
    if prioritize_by == "Overall score" and low_confidence_selected:
        st.warning(
            f"{len(low_confidence_selected)} of {len(selected_assessments)} selected "
            "profiles have medium or low evidence confidence. Validate their cited source "
            "evidence before using this scenario."
        )
    unscored_selected = [
        item for item in selected_assessments if item["overall"] is None
    ]
    if prioritize_by == "Overall score" and unscored_selected:
        st.warning(
            f"{len(unscored_selected)} selected profile(s) have no score because the "
            "sources provide insufficient evidence. They are included only because the "
            "chosen headcount extends past all evidence-scored profiles; this is not a "
            "negative employee rating."
        )
    display_rows = []
    for rank, item in enumerate(selected_assessments, start=1):
        supported_factors = sorted(
            (
                (factor, result[0])
                for factor, result in item["factors"].items()
                if result[0] is not None and factor_weights[factor] > 0
            ),
            key=lambda pair: (-pair[1], pair[0]),
        )
        priority_reason = (
            "; ".join(f"{factor}: {score}/100" for factor, score in supported_factors[:2])
            if prioritize_by == "Overall score" and supported_factors
            else "No scored evidence; flagged for review"
            if prioritize_by == "Overall score"
            else f"Highest compensation rank {rank}"
        )
        display_rows.append(
            {
                "Rank": (
                    "—"
                    if prioritize_by == "Overall score" and item["overall"] is None
                    else str(rank)
                ),
                "Employee ID": item["person"]["employee_id"],
                "Name": item["person"]["name"],
                "Role": item["person"]["role"],
                "Department": item["person"]["department"],
                "Overall score": (
                    f"{item['overall']:.0f}/100"
                    if item["overall"] is not None
                    else "Not scored"
                ),
                "Evidence confidence": item["confidence"],
                "Evidence coverage": f"{item['coverage']}%",
                "Annual base compensation": item["person"]["comp_usd"],
                "Why prioritized": priority_reason,
            }
        )
    st.dataframe(
        display_rows,
        column_config={
            "Annual base compensation": st.column_config.NumberColumn(format="$%d")
        },
        hide_index=True,
        width="stretch",
    )
else:
    st.info("Set the team size above zero to see the selected employees.")

with st.expander("All employees — overall scores and factor breakdown"):
    st.caption(
        "A factor is scored only when the supplied materials contain a matching "
        "job-related evidence signal. This keyword-based first pass is not a validated "
        "performance assessment; inspect the cited evidence before relying on it."
    )
    matrix_rows = []
    for rank, item in enumerate(ranked_people, start=1):
        person = item["person"]
        matrix_row = {
            "Rank": (
                "—"
                if prioritize_by == "Overall score" and item["overall"] is None
                else str(rank)
            ),
            "Employee ID": person["employee_id"],
            "Name": person["name"],
            "Role": person["role"],
            "Department": person["department"],
            "Overall score": (
                f"{item['overall']:.0f}/100" if item["overall"] is not None else "Not scored"
            ),
            "Confidence": item["confidence"],
            "Evidence coverage": f"{item['coverage']}%",
        }
        for factor, _ in factor_weights.items():
            score, _evidence = item["factors"][factor]
            matrix_row[factor] = f"{score}/100" if score is not None else "Unknown"
        matrix_rows.append(matrix_row)
    st.dataframe(matrix_rows, hide_index=True, width="stretch")

    selected_id_for_evidence = st.selectbox(
        "Inspect evidence by employee ID",
        options=[item["person"]["employee_id"] for item in ranked_people],
        format_func=lambda employee_id: (
            f"{employee_id} — "
            f"{next(item['person']['name'] for item in ranked_people if item['person']['employee_id'] == employee_id)}"
        ),
    )
    evidence_assessment = next(
        item
        for item in ranked_people
        if item["person"]["employee_id"] == selected_id_for_evidence
    )
    for factor, (score, matched_evidence) in evidence_assessment["factors"].items():
        with st.expander(
            f"{factor}: {f'{score}/100' if score is not None else 'Unknown'}"
        ):
            if matched_evidence:
                for evidence_line in matched_evidence:
                    st.markdown(f"- {evidence_line}")
            elif factor == "Role-overlap fit":
                st.info(
                    "Unknown: no acquiring-company employee/role data was supplied."
                )
            elif factor == "Strategic importance":
                st.info(
                    "Unknown: the acquisition thesis was not supplied, so alignment "
                    "cannot be evaluated."
                )
            else:
                st.info("No matching evidence found; this is unknown, not a zero rating.")
