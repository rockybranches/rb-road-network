import json
import struct

import pytest

from rbnet import detail as dt
from rbnet import grid as g
from rbnet.analysis import Window, analyze

T = g.TILE
REQUEST = {"label": "Test", "lat": 32.6, "lon": -84.9, "radius_m": 2500.0}
DATASETS = {"roads": "osm-test", "counties": "tl-test"}


def _setup(start_row=50):
    # An east-west road along row 50 of tile (10, 20), starting at column 60:
    # a 2.5 km budget reaches ten cells each way.
    data = bytearray(T * T)
    for c in range(T):
        data[50 * T + c] = 1
    roads = {(10, 20): bytes(data)}
    counties = {(10, 20): struct.pack(f"<{T * T}H", *([13001] * (T * T)))}
    window = Window(10 * T + 60, 20 * T + start_row, 10, 20, 10, 20)
    return window, roads, counties


def test_cells_are_kept_only_when_asked():
    window, roads, counties = _setup()
    assert analyze(window, 2500.0, roads, counties).cells is None
    found = analyze(window, 2500.0, roads, counties, keep_cells=True)
    assert len(found.cells) == found.reached_cells == 21
    assert list(found.cells.cols) == [10 * T + c for c in range(50, 71)]
    assert set(found.cells.rows) == {20 * T + 50}


def test_geojson_has_the_legacy_layout():
    window, roads, counties = _setup()
    found = analyze(window, 2500.0, roads, counties, keep_cells=True)
    doc = json.loads(dt.to_geojson(found, REQUEST, DATASETS, "abc123"))

    assert doc["type"] == "FeatureCollection"
    start, area = doc["features"]
    assert start["geometry"] == {"type": "Point", "coordinates": [-84.9, 32.6]}
    assert start["properties"]["name"] == "StartPoint"
    assert start["properties"]["marker-color"] == "#ff0000"
    assert start["properties"]["marker-size"] == "large"
    assert start["properties"]["analysis_id"] == "abc123"
    assert start["properties"]["moved_to_nearest_road"] is False

    assert area["geometry"]["type"] == "MultiPoint"
    assert area["properties"]["name"] == "AccessibleArea"
    assert area["properties"]["marker-color"] == "#0000ff"
    assert area["properties"]["marker-size"] == "small"
    assert area["properties"]["points"] == 21
    assert area["properties"]["cell_m"] == g.CELL_M
    assert area["properties"]["datasets"] == DATASETS
    coords = area["geometry"]["coordinates"]
    assert len(coords) == 21


def test_points_are_cell_centres():
    window, roads, counties = _setup()
    found = analyze(window, 2500.0, roads, counties, keep_cells=True)
    doc = json.loads(dt.to_geojson(found, REQUEST, DATASETS))
    coords = doc["features"][1]["geometry"]["coordinates"]
    for (lon, lat), c, r in zip(coords, found.cells.cols, found.cells.rows):
        assert g.xy_to_cell(*g.lonlat_to_xy(lon, lat)) == (c, r)
        x, y = g.lonlat_to_xy(lon, lat)
        cx, cy = g.cell_center_xy(c, r)
        assert abs(x - cx) < 2 and abs(y - cy) < 2  # 5 decimals is about 1 m
    # The search start is the start cell's centre.
    assert doc["features"][0]["properties"]["search_start"] == coords[10]


def test_snapped_start_is_reported():
    window, roads, counties = _setup(start_row=53)
    found = analyze(window, 2500.0, roads, counties, keep_cells=True)
    doc = json.loads(dt.to_geojson(found, REQUEST, DATASETS))
    assert doc["features"][0]["properties"]["moved_to_nearest_road"] is True


def test_requires_kept_cells():
    window, roads, counties = _setup()
    with pytest.raises(ValueError):
        dt.to_geojson(analyze(window, 2500.0, roads, counties), REQUEST, DATASETS)


def test_object_key():
    assert dt.object_key("abc123") == "details/abc123.geojson"
