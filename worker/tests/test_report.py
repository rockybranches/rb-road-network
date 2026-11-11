from conftest import FIXTURES

from rbnet.report import REPORT_YEARS, build_report, to_latex


def _county(name, state, pops, geoid=1):
    return {
        "geoid": geoid,
        "name": name,
        "state": state,
        "reached_km2": 1.0,
        "population": dict(zip(REPORT_YEARS, pops)) if pops else None,
    }


def test_totals_and_tonnage():
    report = build_report(
        [
            _county("Beta", "GA", [10, 20, 30, 40, 50]),
            _county("Alpha", "GA", [1, 2, 3, 4, 5]),
        ],
        tons_per_person=2.0,
    )
    assert [c["name"] for c in report["counties"]] == ["Alpha", "Beta"]
    assert report["totals"] == [11, 22, 33, 44, 55]
    assert report["population_increase"] == 33  # 2030 minus 2015
    assert report["percent_increase"] == 150.0
    assert (report["tons_base"], report["tons_target"]) == (44.0, 110.0)
    assert report["tons_increase"] == 66.0


def test_county_without_full_series_is_listed_not_counted():
    partial = _county("Gamma", "VA", None)
    partial["population"] = {2010: 5, 2015: 6}
    report = build_report([_county("Alpha", "GA", [1, 2, 3, 4, 5]), partial])
    assert [c["name"] for c in report["counties"]] == ["Alpha"]
    assert [c["name"] for c in report["missing_population"]] == ["Gamma"]
    assert report["totals"] == [1, 2, 3, 4, 5]


def test_empty_report_has_no_percentage():
    report = build_report([])
    assert report["totals"] == [0, 0, 0, 0, 0]
    assert report["percent_increase"] is None
    assert "n/a" in to_latex(report)


def test_latex_escapes_special_characters():
    report = build_report([_county("Lewis & Clark", "MT", [1, 2, 3, 4, 5])])
    assert "Lewis \\& Clark & MT & 1" in to_latex(report)


def test_latex_matches_legacy_output(legacy_table):
    """Feeding the legacy table's own numbers back in reproduces its text."""
    rows = legacy_table("legacy_atlanta.tex")
    assert len(rows) == 27
    report = build_report(
        [_county(n, s, p, geoid=i) for i, (n, s, p) in enumerate(rows)], 4.5
    )
    ours = to_latex(report).splitlines()
    legacy = (FIXTURES / "legacy_atlanta.tex").read_text().splitlines()
    assert len(ours) == len(legacy)
    differing = [(a, b) for a, b in zip(ours, legacy) if a != b]
    # The only difference is a rounding error in the legacy file: it computed
    # 4.5 * 7612020 in 32-bit floats and printed 34254088 instead of 34254090.
    assert differing == [
        (
            " Tons needed by market (2030) & 34254090.000  (4.500 tons/person) \\\\ ",
            " Tons needed by market (2030) & 34254088.000  (4.500 tons/person) \\\\ ",
        )
    ]
