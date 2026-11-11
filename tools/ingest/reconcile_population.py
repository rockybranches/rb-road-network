#!/usr/bin/env python3
"""Reconcile the two county population sources against Census Bureau data.

Two versions of the county population figures exist: the per-state CSVs
(`county_pop/ga.csv`, ...) and the POPxx columns baked into the legacy county
shapefile. They agree for most states and disagree for some. This tool
decides, county by county and year by year, which figure to keep:

1. If the two agree (within one person, i.e. rounding), keep it.
2. If they differ and the Census Bureau has a figure for that county and
   year, keep whichever is closer to it.
3. If they differ and there is no Census figure (2030 is still a
   projection), keep the figure from the source that was closer to the
   Census in the most recent year where the two differed.

It also repairs wrong `County NS Code` values, using the same name check as
`load_population.py`.

The CSVs are edited in place, changing only the cells that need it, after
the whole directory has been copied to `--backup-dir`. An audit CSV lists
every county with the chosen figures, where each came from, and the Census
figures they were checked against. Without `--apply` nothing is written
except the audit CSV.

Census inputs (from www2.census.gov/programs-surveys/popest/datasets/):
  2010-2020/counties/totals/co-est2020-alldata.csv  (2010 census, 2015)
  2020-2025/counties/totals/co-est2025-alldata.csv  (2020 base, 2025)

    reconcile_population.py --counties tl_2016_us_county.shp \\
        --csv-dir county_pop --census-2010s co-est2020-alldata.csv \\
        --census-2020s co-est2025-alldata.csv --audit reconciled.csv \\
        --backup-dir county_pop_backup --apply
"""

import argparse
import csv
import json
import shutil
import sys
from pathlib import Path

from common import CONUS_STATES
from load_population import match_row, parse_population

YEARS = (2010, 2015, 2020, 2025, 2030)
REVIEW_THRESHOLD = 0.10  # flag chosen figures this far from the Census


def choose(csv_pops, legacy_pops, census):
    """Pick a figure for each year. Returns {year: (population, source)}.

    source is "both" (the sources agree), "csv", "legacy", or "csv-only"
    (the legacy source has no figure). Years missing from the CSV are left
    out: there is no cell to correct.
    """
    chosen = {}
    undecided = []
    track_record = None  # winner in the latest year the Census could judge
    for year in sorted(csv_pops):
        a, b = csv_pops[year], legacy_pops.get(year)
        if b is None:
            chosen[year] = (a, "csv-only")
        elif abs(a - b) <= 1:
            chosen[year] = (a, "both")
        elif year in census:
            truth = census[year]
            source = "legacy" if abs(b - truth) < abs(a - truth) else "csv"
            chosen[year] = (b if source == "legacy" else a, source)
            track_record = source
        else:
            undecided.append(year)
    for year in undecided:
        source = track_record or "csv"
        value = legacy_pops[year] if source == "legacy" else csv_pops[year]
        chosen[year] = (value, source)
    return chosen


def read_census(path_2010s, path_2020s):
    """{geoid: {year: population}} from the two Census estimate files."""
    out = {}
    fields = (
        (path_2010s, {2010: "CENSUS2010POP", 2015: "POPESTIMATE2015"}),
        (path_2020s, {2020: "ESTIMATESBASE2020", 2025: "POPESTIMATE2025"}),
    )
    for path, columns in fields:
        with open(path, newline="", encoding="latin-1") as f:
            for row in csv.DictReader(f):
                if row["SUMLEV"] != "050":
                    continue
                geoid = int(row["STATE"] + row["COUNTY"])
                for year, column in columns.items():
                    if row[column].isdigit():
                        out.setdefault(geoid, {})[year] = int(row[column])
    return out


def read_counties_and_legacy(shp_path):
    import pandas as pd
    import pyogrio

    df = pyogrio.read_dataframe(shp_path, read_geometry=False)
    counties, legacy = [], {}
    for r in df.itertuples(index=False):
        if r.STATEFP not in CONUS_STATES:
            continue
        geoid = int(r.GEOID)
        counties.append(
            {
                "geoid": geoid,
                "countyns": int(r.COUNTYNS),
                "name": r.NAME,
                "namelsad": r.NAMELSAD,
                "stusps": CONUS_STATES[r.STATEFP],
            }
        )
        pops = {y: getattr(r, f"POP{y % 100}") for y in YEARS}
        if not any(pd.isna(v) for v in pops.values()):
            legacy[geoid] = {y: round(v) for y, v in pops.items()}
    return counties, legacy


def reconcile_file(path, state_counties, legacy, census):
    """Work out the corrections for one state CSV.

    Returns (rows, edits, audit): the file's rows with corrections applied,
    how many cells changed, and one audit record per matched county.
    """
    with path.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    header = rows[0]
    year_col = {int(h): i for i, h in enumerate(header) if h.strip().isdigit()}
    edits, audit = 0, []
    for row in rows[1:]:
        if len(row) < 2 or not row[1].strip():
            continue
        try:
            ns = int(float(row[0]))
        except ValueError:
            ns = None
        status, county, note = match_row(ns, row[1], state_counties)
        if status == "rejected":
            audit.append({"state": path.stem.upper(), "county": row[1], "note": note})
            continue
        notes = []
        if status == "fixed":
            row[0] = str(county["countyns"])
            edits += 1
            notes.append(f"NS code corrected ({note})")
        csv_pops = {}
        for year in YEARS:
            i = year_col.get(year)
            pop = parse_population(row[i]) if i is not None and i < len(row) else None
            if pop is not None:
                csv_pops[year] = pop
        truth = census.get(county["geoid"], {})
        chosen = choose(csv_pops, legacy.get(county["geoid"], {}), truth)
        for year, (value, source) in chosen.items():
            if source == "legacy":
                row[year_col[year]] = str(value)
                edits += 1
            if year in truth and truth[year]:
                off = abs(value - truth[year]) / truth[year]
                if off > REVIEW_THRESHOLD:
                    notes.append(f"{year} is {off:.0%} from the Census figure")
        audit.append(
            {
                "geoid": f"{county['geoid']:05d}",
                "state": county["stusps"],
                "county": county["name"],
                "county_ns": county["countyns"],
                **{str(y): chosen[y][0] for y in chosen},
                **{f"source_{y}": chosen[y][1] for y in chosen},
                **{f"census_{y}": truth[y] for y in truth},
                "note": "; ".join(notes),
            }
        )
    return rows, edits, audit


AUDIT_COLUMNS = (
    ["geoid", "state", "county", "county_ns"]
    + [str(y) for y in YEARS]
    + [f"source_{y}" for y in YEARS]
    + [f"census_{y}" for y in YEARS if y != 2030]
    + ["note"]
)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--counties", required=True, type=Path, help="county shapefile")
    ap.add_argument("--csv-dir", required=True, type=Path)
    ap.add_argument("--census-2010s", required=True, type=Path)
    ap.add_argument("--census-2020s", required=True, type=Path)
    ap.add_argument("--audit", required=True, type=Path, help="audit CSV to write")
    ap.add_argument("--backup-dir", type=Path, help="copy --csv-dir here first")
    ap.add_argument("--apply", action="store_true", help="edit the CSVs in place")
    args = ap.parse_args()
    if args.apply and not args.backup_dir:
        ap.error("--apply needs --backup-dir")
    if args.apply and args.backup_dir.exists():
        ap.error(f"{args.backup_dir} already exists; choose a new backup directory")

    counties, legacy = read_counties_and_legacy(args.counties)
    census = read_census(args.census_2010s, args.census_2020s)
    by_state = {}
    for c in counties:
        by_state.setdefault(c["stusps"], []).append(c)

    results, audit = {}, []
    for path in sorted(args.csv_dir.glob("*.csv")):
        state = path.stem.upper()
        if state in by_state:
            rows, edits, file_audit = reconcile_file(path, by_state[state], legacy, census)
            results[path] = (rows, edits)
            audit += file_audit

    args.audit.parent.mkdir(parents=True, exist_ok=True)
    with args.audit.open("w", newline="") as f:
        writer = csv.DictWriter(f, AUDIT_COLUMNS, restval="", lineterminator="\n")
        writer.writeheader()
        writer.writerows(sorted(audit, key=lambda a: a.get("geoid", "")))

    if args.apply:
        shutil.copytree(args.csv_dir, args.backup_dir)
        for path, (rows, edits) in results.items():
            if edits:
                with path.open("w", newline="") as f:
                    csv.writer(f, lineterminator="\n").writerows(rows)

    sources = {}
    for a in audit:
        for y in YEARS:
            s = a.get(f"source_{y}")
            if s:
                sources.setdefault(y, {}).setdefault(s, 0)
                sources[y][s] += 1
    json.dump(
        {
            "applied": args.apply,
            "counties": sum(1 for a in audit if "geoid" in a),
            "files_changed": sorted(p.name for p, (_, e) in results.items() if e),
            "cells_changed": sum(e for _, e in results.values()),
            "sources_by_year": sources,
            "unmatched_rows": [a for a in audit if "geoid" not in a],
            # Projections drifting by 2020/2025 is expected; a 2010 or 2015
            # figure far from the Census points at an error in the data.
            "far_from_census_2010_or_2015": sum(
                1
                for a in audit
                if "2010 is" in a.get("note", "") or "2015 is" in a.get("note", "")
            ),
            "far_from_census_any_year": sum(
                1 for a in audit if "from the Census" in a.get("note", "")
            ),
        },
        sys.stdout,
        indent=2,
    )
    print()


if __name__ == "__main__":
    main()
