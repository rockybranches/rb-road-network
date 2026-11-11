"""Request parameters for one analysis, and the sites CSV used for batches.

Pure standard library. Everything a user can send is validated here, so the
single-analysis route, the batch route and the tests share one set of rules.
"""

import csv
import io
import math
from dataclasses import asdict, dataclass

from .analysis import MAX_RADIUS_M, MIN_RADIUS_M, AnalysisError
from .report import BASE_YEAR, DEFAULT_TONS_PER_PERSON, TARGET_YEAR

DEFAULT_RADIUS_M = 75_000.0
MAX_LABEL = 120
MAX_BATCH_ROWS = 500

# Accepted CSV headers, compared case-insensitively. `site, lat, lon` is the
# legacy batch format; the rest are optional per-row overrides.
_COLUMNS = {
    "label": ("site", "name", "label"),
    "lat": ("lat", "latitude"),
    "lon": ("lon", "lng", "long", "longitude"),
    "radius_m": ("radius_m", "radius"),
    "tons_per_person": ("tons_per_person",),
    "min_km2": ("min_km2",),
}


@dataclass
class Params:
    lat: float
    lon: float
    radius_m: float = DEFAULT_RADIUS_M
    tons_per_person: float = DEFAULT_TONS_PER_PERSON
    min_km2: float = 0.0
    label: str = ""

    def to_dict(self):
        return asdict(self)


def _number(source, name, default=None):
    value = source.get(name)
    if value is None or value == "":
        if default is None:
            raise AnalysisError(f"missing required parameter: {name}")
        return default
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise AnalysisError(f"{name} must be a number") from None
    if not math.isfinite(number):
        raise AnalysisError(f"{name} must be a number")
    return number


def parse_params(source, defaults=None):
    """Validate a mapping of raw values (strings or numbers) into Params.

    `defaults` supplies radius_m, tons_per_person and min_km2 for values the
    source leaves out; a batch uses it for its batch-wide settings.
    """
    d = defaults or Params(0.0, 0.0)
    p = Params(
        lat=_number(source, "lat"),
        lon=_number(source, "lon"),
        radius_m=_number(source, "radius_m", d.radius_m),
        tons_per_person=_number(source, "tons_per_person", d.tons_per_person),
        min_km2=_number(source, "min_km2", d.min_km2),
        label=str(source.get("label") or "").strip(),
    )
    if not (-90.0 < p.lat < 90.0 and -180.0 <= p.lon <= 180.0):
        raise AnalysisError("lat/lon out of range")
    if not (MIN_RADIUS_M <= p.radius_m <= MAX_RADIUS_M):
        raise AnalysisError(
            f"radius_m must be between {MIN_RADIUS_M:.0f} and {MAX_RADIUS_M:.0f}"
        )
    if p.tons_per_person < 0:
        raise AnalysisError("tons_per_person cannot be negative")
    if p.min_km2 < 0:
        raise AnalysisError("min_km2 cannot be negative")
    if len(p.label) > MAX_LABEL:
        raise AnalysisError(f"label is longer than {MAX_LABEL} characters")
    return p


def parse_sites_csv(text, defaults=None):
    """Parse a sites CSV into a list of Params, one per data row.

    Every row is checked before anything is returned, and all problems are
    reported together with their line numbers, so a batch is never created
    from a file that is only partly usable.
    """
    reader = csv.reader(io.StringIO(text.lstrip("﻿")))
    try:
        header = next(reader)
    except StopIteration:
        raise AnalysisError("the CSV is empty") from None
    index = {}
    for i, name in enumerate(header):
        key = name.strip().casefold()
        for field, aliases in _COLUMNS.items():
            if key in aliases:
                index.setdefault(field, i)
    missing = [f for f in ("lat", "lon") if f not in index]
    if missing:
        raise AnalysisError(
            "the CSV needs a header row with columns: site, lat, lon "
            f"(missing {', '.join(missing)})"
        )

    sites, problems = [], []
    for row in reader:
        if not any(cell.strip() for cell in row):
            continue
        raw = {f: row[i].strip() for f, i in index.items() if i < len(row)}
        try:
            sites.append(parse_params(raw, defaults))
        except AnalysisError as exc:
            problems.append(f"line {reader.line_num}: {exc}")
        if len(sites) > MAX_BATCH_ROWS:
            raise AnalysisError(f"a batch can hold at most {MAX_BATCH_ROWS} sites")
    if problems:
        shown = "; ".join(problems[:10])
        more = f"; and {len(problems) - 10} more" if len(problems) > 10 else ""
        raise AnalysisError(f"the CSV has problems: {shown}{more}")
    if not sites:
        raise AnalysisError("the CSV has no data rows")
    return sites


SUMMARY_COLUMNS = (
    "site",
    "lat",
    "lon",
    "radius_m",
    "status",
    "error",
    "counties",
    "reached_km2",
    f"population_{BASE_YEAR}",
    f"population_{TARGET_YEAR}",
    "population_increase",
    "percent_increase",
    "tons_per_person",
    f"tons_{BASE_YEAR}",
    f"tons_{TARGET_YEAR}",
    "tons_increase",
)


def summary_csv(records):
    """One line per site of a batch, for spreadsheets.

    `records` are stored analysis records (see entry.py); sites that have
    not finished leave the result columns empty.
    """
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(SUMMARY_COLUMNS)
    for r in records:
        req, s = r["request"], r.get("summary")
        line = [
            req["label"],
            req["lat"],
            req["lon"],
            req["radius_m"],
            r["status"],
            r.get("error") or "",
        ]
        if s:
            base, target = s["population_base"], s["population_target"]
            tpp = req["tons_per_person"]
            line += [
                s["counties"],
                s["reached_km2"],
                base,
                target,
                target - base,
                round(100.0 * (target - base) / base, 1) if base else "",
                tpp,
                tpp * base,
                tpp * target,
                tpp * (target - base),
            ]
        else:
            line += [""] * 10
        writer.writerow(line)
    return out.getvalue()
