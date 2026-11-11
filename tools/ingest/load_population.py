#!/usr/bin/env python3
"""Load county population CSVs into the `county_population` table.

Reads one CSV per state (`ga.csv`, `al.csv`, ...) with the columns
`County NS Code, County, <year>, <year>, ...` and writes SQL for D1.

Each row is matched to a county twice: by its NS code and by its name within
the state. The source files contain wrong codes (swapped or duplicated), which
the legacy code-only join turned into wrong populations, so the name is the
tie-breaker: when the code points at a different county but the name
identifies exactly one county in that state, the name wins and the row is
reported as corrected. Rows that cannot be placed are reported and skipped.

    load_population.py --counties tl_2016_us_county.shp --csv-dir county_pop \\
        --source county-pop-2026-02 --sql out/population.sql
"""

import argparse
import csv
import json
import sys
from pathlib import Path

from common import CONUS_STATES, write_inserts

MIN_PREFIX = 8  # shortest truncated name accepted as a prefix match


def normalize(name):
    """Fold case, spacing and the stray quoting found in the source CSVs."""
    s = str(name).strip().strip("'").replace("''", "'")
    return " ".join(s.casefold().split())


def names_agree(csv_name, county):
    """True if a CSV county name refers to this county record."""
    n = normalize(csv_name)
    full = normalize(county["name"])
    if n == full or n == normalize(county["namelsad"]):
        return True
    # Some names are cut short in the source ("Lake Of The Wood").
    return len(n) >= MIN_PREFIX and full.startswith(n)


def match_row(ns, csv_name, state_counties):
    """Place one CSV row. Returns (status, county, note).

    status is "ok" (code and name agree), "fixed" (code wrong, name unique)
    or "rejected".
    """
    by_ns = next((c for c in state_counties if c["countyns"] == ns), None)
    if by_ns is not None and names_agree(csv_name, by_ns):
        return "ok", by_ns, ""
    by_name = [c for c in state_counties if names_agree(csv_name, c)]
    if len(by_name) == 1:
        owner = by_ns["namelsad"] if by_ns else "no county in this state"
        return "fixed", by_name[0], f"code {ns} belongs to {owner}"
    why = "name is ambiguous" if by_name else "name not found"
    return "rejected", None, f"code {ns}; {why}"


def parse_population(value):
    try:
        return round(float(value))
    except (TypeError, ValueError):
        return None


def read_state_csv(path):
    """Yield (ns, name, {year: population}) for each data row."""
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)
        years = {i: int(h) for i, h in enumerate(header) if h.strip().isdigit()}
        for row in reader:
            if len(row) < 2 or not row[1].strip():
                continue
            try:
                ns = int(float(row[0]))
            except ValueError:
                ns = None
            pops = {}
            for i, year in years.items():
                if i < len(row):
                    pop = parse_population(row[i])
                    if pop is not None:
                        pops[year] = pop
            yield ns, row[1], pops


def load(counties, csv_dir):
    """Match every state CSV. Returns (rows, report)."""
    by_state = {}
    for c in counties:
        by_state.setdefault(c["stusps"], []).append(c)

    placed = {}  # geoid -> (status, {year: pop})
    report = {"ok": 0, "fixed": [], "rejected": [], "skipped_files": []}
    for path in sorted(csv_dir.glob("*.csv")):
        state = path.stem.upper()
        if state not in by_state:
            report["skipped_files"].append(path.name)
            continue
        for ns, name, pops in read_state_csv(path):
            status, county, note = match_row(ns, name, by_state[state])
            label = f"{state} {name.strip()}"
            if status == "rejected":
                report["rejected"].append(f"{label}: {note}")
                continue
            prior = placed.get(county["geoid"])
            if prior and prior[0] == "ok" and status == "fixed":
                report["rejected"].append(f"{label}: county already has a clean row")
                continue
            placed[county["geoid"]] = (status, pops)
            if status == "ok":
                report["ok"] += 1
            else:
                report["fixed"].append(f"{label}: {note}")

    rows = [
        (geoid, year, pop)
        for geoid, (_, pops) in sorted(placed.items())
        for year, pop in sorted(pops.items())
    ]
    without = sorted(
        f"{c['stusps']} {c['namelsad']}" for c in counties if c["geoid"] not in placed
    )
    report["counties_with_population"] = len(placed)
    report["counties_without_population"] = without
    return rows, report


def read_counties(shp_path):
    import pyogrio  # local import: the matching logic above needs no GIS stack

    df = pyogrio.read_dataframe(
        shp_path,
        read_geometry=False,
        columns=["STATEFP", "GEOID", "COUNTYNS", "NAME", "NAMELSAD"],
    )
    return [
        {
            "geoid": int(r.GEOID),
            "countyns": int(r.COUNTYNS),
            "name": r.NAME,
            "namelsad": r.NAMELSAD,
            "stusps": CONUS_STATES[r.STATEFP],
        }
        for r in df.itertuples(index=False)
        if r.STATEFP in CONUS_STATES
    ]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--counties", type=Path, required=True, help="TIGER county .shp")
    ap.add_argument("--csv-dir", type=Path, required=True)
    ap.add_argument("--source", required=True, help="label stored with each row")
    ap.add_argument("--sql", type=Path, required=True, help="output SQL file")
    args = ap.parse_args()

    rows, report = load(read_counties(args.counties), args.csv_dir)
    args.sql.parent.mkdir(parents=True, exist_ok=True)
    with args.sql.open("w") as f:
        f.write("DELETE FROM county_population;\n")
        write_inserts(
            f,
            "county_population",
            ("geoid", "year", "population", "source"),
            ((geoid, year, pop, args.source) for geoid, year, pop in rows),
        )
    report["rows"] = len(rows)
    json.dump(report, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
