import csv
import io

import pytest

from rbnet.analysis import AnalysisError
from rbnet.params import (
    MAX_BATCH_ROWS,
    SUMMARY_COLUMNS,
    Params,
    parse_params,
    parse_sites_csv,
    summary_csv,
)


def test_defaults_and_strings():
    p = parse_params({"lat": "33.7", "lon": "-84.4"})
    assert p == Params(33.7, -84.4, 75000.0, 4.5, 0.0, "")
    p = parse_params({"lat": 33.7, "lon": -84.4, "radius_m": "50000", "label": " A "})
    assert (p.radius_m, p.label) == (50000.0, "A")


@pytest.mark.parametrize(
    "raw, message",
    [
        ({"lon": "1"}, "missing required parameter: lat"),
        ({"lat": "x", "lon": "1"}, "lat must be a number"),
        ({"lat": "nan", "lon": "1"}, "lat must be a number"),
        ({"lat": "95", "lon": "1"}, "lat/lon out of range"),
        ({"lat": "1", "lon": "1", "radius_m": "10"}, "radius_m must be between"),
        ({"lat": "1", "lon": "1", "tons_per_person": "-1"}, "cannot be negative"),
        ({"lat": "1", "lon": "1", "min_km2": "-1"}, "cannot be negative"),
        ({"lat": "1", "lon": "1", "label": "x" * 121}, "label is longer"),
    ],
)
def test_rejects_bad_values(raw, message):
    with pytest.raises(AnalysisError, match=message):
        parse_params(raw)


def test_legacy_sites_csv():
    sites = parse_sites_csv("site,lat,lon\nSavannah,32.066051,-81.095341\n")
    assert sites == [Params(32.066051, -81.095341, label="Savannah")]


def test_csv_headers_defaults_and_overrides():
    defaults = Params(0, 0, radius_m=50000.0, tons_per_person=3.0)
    text = "﻿Name, Latitude ,LNG,radius\r\nA,33,-84,\r\n\r\nB,34,-85,20000\r\n"
    a, b = parse_sites_csv(text, defaults)
    assert (a.label, a.radius_m, a.tons_per_person) == ("A", 50000.0, 3.0)
    assert (b.label, b.radius_m) == ("B", 20000.0)


def test_csv_reports_every_bad_line():
    text = "site,lat,lon\nA,33,-84\nB,abc,-84\nC,33,\n"
    with pytest.raises(AnalysisError) as exc:
        parse_sites_csv(text)
    message = str(exc.value)
    assert "line 3: lat must be a number" in message
    assert "line 4: missing required parameter: lon" in message


@pytest.mark.parametrize(
    "text, message",
    [
        ("", "empty"),
        ("site,lat\nA,1\n", "missing lon"),
        ("site,lat,lon\n", "no data rows"),
        ("site,lat,lon\n" + "A,33,-84\n" * (MAX_BATCH_ROWS + 1), "at most"),
    ],
)
def test_csv_rejects_unusable_files(text, message):
    with pytest.raises(AnalysisError, match=message):
        parse_sites_csv(text)


def test_summary_csv():
    request = Params(33.0, -84.0, label="A, Inc").to_dict()
    records = [
        {
            "status": "done",
            "error": None,
            "request": request,
            "summary": {
                "counties": 3,
                "reached_km2": 12.5,
                "population_base": 1000,
                "population_target": 1250,
            },
        },
        {"status": "failed", "error": "no road nearby", "request": request, "summary": None},
    ]
    rows = list(csv.DictReader(io.StringIO(summary_csv(records))))
    assert list(rows[0]) == list(SUMMARY_COLUMNS)
    assert rows[0]["site"] == "A, Inc"
    assert rows[0]["population_increase"] == "250"
    assert rows[0]["percent_increase"] == "25.0"
    assert rows[0]["tons_2030"] == "5625.0"
    assert rows[1]["status"] == "failed" and rows[1]["error"] == "no road nearby"
    assert rows[1]["counties"] == ""
