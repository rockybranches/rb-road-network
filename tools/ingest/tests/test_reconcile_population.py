import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from reconcile_population import choose  # noqa: E402


def test_agreeing_sources_are_kept():
    # One person apart is rounding, not a disagreement.
    chosen = choose({2010: 100, 2030: 201}, {2010: 100, 2030: 200}, {2010: 150})
    assert chosen == {2010: (100, "both"), 2030: (201, "both")}


def test_census_decides_each_disputed_year():
    csv_pops = {2010: 1000, 2015: 1100}
    legacy = {2010: 900, 2015: 1250}
    census = {2010: 990, 2015: 1240}
    assert choose(csv_pops, legacy, census) == {
        2010: (1000, "csv"),
        2015: (1250, "legacy"),
    }


def test_projection_follows_the_latest_winner():
    # 2030 has no Census figure; the source that was closer in 2025 wins.
    csv_pops = {2015: 1000, 2025: 1300, 2030: 1500}
    legacy = {2015: 1100, 2025: 1200, 2030: 1250}
    census = {2015: 1010, 2025: 1210}
    chosen = choose(csv_pops, legacy, census)
    assert chosen[2015] == (1000, "csv")
    assert chosen[2025] == (1200, "legacy")
    assert chosen[2030] == (1250, "legacy")


def test_csv_is_kept_when_nothing_can_judge():
    assert choose({2030: 500}, {2030: 700}, {}) == {2030: (500, "csv")}
    # An exact tie against the Census also stays with the CSV.
    assert choose({2010: 90}, {2010: 110}, {2010: 100}) == {2010: (90, "csv")}


def test_missing_legacy_figures():
    assert choose({2010: 5}, {}, {2010: 9}) == {2010: (5, "csv-only")}
