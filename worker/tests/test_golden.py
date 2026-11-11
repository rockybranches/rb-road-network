"""Compare against the legacy tool's results using the real data in the local
D1 database. Skipped when that database has not been built (see README)."""

import sqlite3
import zlib
from pathlib import Path

import pytest

from rbnet.analysis import analyze, plan_window

STATE = Path(__file__).resolve().parents[1] / ".wrangler" / "state" / "v3" / "d1"
ROADS, COUNTIES = "osm-2026-02", "tl-2016"


@pytest.fixture(scope="module")
def db():
    for path in STATE.rglob("*.sqlite"):
        con = sqlite3.connect(path)
        try:
            n = con.execute(
                "SELECT count(*) FROM raster_tiles WHERE dataset IN (?, ?)",
                (ROADS, COUNTIES),
            ).fetchone()[0]
        except sqlite3.OperationalError:
            n = 0
        if n:
            return con
        con.close()
    pytest.skip("local D1 database with road and county tiles not found")


def reached_counties(db, lat, lon, radius_m):
    w = plan_window(lat, lon, radius_m)
    tiles = {"roads": {}, "counties": {}}
    for layer, tx, ty, data in db.execute(
        "SELECT layer, tx, ty, data FROM raster_tiles "
        "WHERE dataset IN (?, ?) AND ty BETWEEN ? AND ? AND tx BETWEEN ? AND ?",
        (ROADS, COUNTIES, w.ty0, w.ty1, w.tx0, w.tx1),
    ):
        tiles[layer][(tx, ty)] = zlib.decompress(data)
    result = analyze(w, radius_m, tiles["roads"], tiles["counties"])
    ids = ",".join(str(g) for g in result.county_cells)
    names = db.execute(f"SELECT name, stusps FROM counties WHERE geoid IN ({ids})")
    return {f"{n} {s}" for n, s in names}


def test_atlanta_reaches_every_legacy_county(db, legacy_table):
    legacy = {f"{n} {s}" for n, s, _ in legacy_table("legacy_atlanta.tex")}
    ours = reached_counties(db, 33.732, -84.4166, 75000.0)
    assert legacy <= ours
    # The finer grid adds a handful of fringe counties, not a different area.
    assert len(ours - legacy) <= 6


def test_battelle_matches_legacy_within_two_counties(db, legacy_table):
    legacy = {f"{n} {s}" for n, s, _ in legacy_table("legacy_battelle.tex")}
    ours = reached_counties(db, 34.64944, -85.56528, 75000.0)
    assert len(legacy - ours) <= 2
    assert len(ours - legacy) <= 2


def test_population_uses_the_right_county_despite_bad_source_codes(db):
    # The source CSV swaps the codes of DeKalb and Decatur and gives Peach
    # Paulding's code; the legacy join reported DeKalb at 29,392 for 2010.
    pops = dict(
        db.execute(
            "SELECT c.name, p.population FROM counties c "
            "JOIN county_population p USING (geoid) "
            "WHERE c.stusps = 'GA' AND p.year = 2010 "
            "AND c.name IN ('DeKalb', 'Decatur', 'Paulding', 'Peach')"
        )
    )
    assert pops["DeKalb"] > 600_000
    assert pops["Paulding"] > 100_000
    assert pops["Decatur"] < 50_000
    assert pops["Peach"] < 50_000
