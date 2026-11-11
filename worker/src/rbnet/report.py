"""Population report for a market area: the table the legacy tool produced.

Pure standard library. `build_report` turns reached counties and their
population series into totals and tonnage figures; `to_latex` renders the
same LaTeX layout as the legacy `justPop` output so existing documents keep
working.
"""

REPORT_YEARS = (2010, 2015, 2020, 2025, 2030)
BASE_YEAR = 2015
TARGET_YEAR = 2030
DEFAULT_TONS_PER_PERSON = 4.5

_LATEX_ESCAPES = str.maketrans(
    {"&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_"}
)


def build_report(counties, tons_per_person=DEFAULT_TONS_PER_PERSON, years=REPORT_YEARS):
    """Summarise reached counties.

    `counties` is an iterable of dicts with `geoid`, `name`, `state`,
    `reached_km2` and `population` ({year: people}). A county enters the
    table only if it has a figure for every report year; the rest are
    returned under `missing_population` so they are visible, not dropped.
    """
    rows, missing = [], []
    for c in sorted(counties, key=lambda c: (c["name"], c["state"])):
        pops = c.get("population") or {}
        entry = {
            "geoid": c["geoid"],
            "name": c["name"],
            "state": c["state"],
            "reached_km2": c["reached_km2"],
        }
        if all(y in pops for y in years):
            entry["population"] = [pops[y] for y in years]
            rows.append(entry)
        else:
            missing.append(entry)

    totals = [sum(r["population"][i] for r in rows) for i in range(len(years))]
    base = totals[years.index(BASE_YEAR)]
    target = totals[years.index(TARGET_YEAR)]
    increase = target - base
    return {
        "years": list(years),
        "counties": rows,
        "missing_population": missing,
        "totals": totals,
        "base_year": BASE_YEAR,
        "target_year": TARGET_YEAR,
        "population_increase": increase,
        "percent_increase": (100.0 * increase / base) if base else None,
        "tons_per_person": tons_per_person,
        "tons_base": tons_per_person * base,
        "tons_target": tons_per_person * target,
        "tons_increase": tons_per_person * increase,
    }


def to_latex(report):
    """Render a report in the legacy two-table LaTeX layout."""
    years = report["years"]
    base, target = report["base_year"], report["target_year"]
    tpp = report["tons_per_person"]
    pct = report["percent_increase"]
    out = [
        "\\begin{tabular}{r|*{%d}{l}}\n" % (len(years) + 1),
        "County & State & " + " & ".join(str(y) for y in years) + " \\\\ \n",
        "\\hline\n",
    ]
    for row in report["counties"]:
        cells = [row["name"].translate(_LATEX_ESCAPES), row["state"]]
        cells += [str(p) for p in row["population"]]
        out.append(" & ".join(cells) + "\\\\ \n")
    out += [
        "\\\\ \n",
        "\\hline\\hline\n",
        "    Totals = & " + "".join(f" & {t}" for t in report["totals"]) + "\\newline\n",
        "\\end{tabular} \\\\ \n",
        "\\begin{tabular}{l|l}\n\\hline\\hline\n\\newline\n",
        f" Population increase ({base} to {target}) & "
        f"{report['population_increase']} \\\\ \n",
        " Percent population increase & "
        + ("n/a" if pct is None else f"{pct:.1f}")
        + " \\\\ \n",
        f" Tons needed by market ({base}) & {report['tons_base']:.3f}"
        f"  ({tpp:.3f} tons/person) \\\\ \n",
        f" Tons needed by market ({target}) & {report['tons_target']:.3f}"
        f"  ({tpp:.3f} tons/person) \\\\ \n",
        f" Increase in tons needed ({base} to {target}) & "
        f"{report['tons_increase']:.3f} \\\\ \n",
        "\\end{tabular}\n",
    ]
    return "".join(out)
