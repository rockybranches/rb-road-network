import pytest

from rbnet import area as ar
from rbnet import grid as g
from rbnet.analysis import Window, analyze

T = g.TILE


def _area(rows, bcol=100, brow=200):
    """An Area from rows of levels, given north-first for readability."""
    rows = rows[::-1]
    return ar.Area(bcol, brow, len(rows[0]), len(rows), bytes(v for r in rows for v in r))


def test_level_spans_the_budget():
    assert ar.level(0, 1500) == 1
    assert ar.level(1500, 1500) == ar.LEVELS
    assert 1 < ar.level(750, 1500) < ar.LEVELS


def test_encode_round_trip():
    area = _area([[0, 5, 250], [1, 0, 7]], bcol=-3, brow=12)
    assert ar.decode(ar.encode(area)) == area
    with pytest.raises(ValueError):
        ar.decode(b"nope" + ar.encode(area)[4:])


def test_rectangles_merge_runs_and_rows():
    # Two identical rows of one band merge into a single 3 x 2 rectangle.
    area = _area([[1, 1, 1, 0], [1, 1, 1, 0]])
    assert ar._rectangles(area, bands=5) == [[0, 0, 3, 0, 2]]
    # A different band, or a different extent, starts a new rectangle.
    area = _area([[1, 1, 250], [1, 1, 1]])
    assert sorted(ar._rectangles(area, bands=5)) == [
        [0, 0, 2, 1, 2],
        [0, 0, 3, 0, 1],
        [4, 2, 3, 1, 2],
    ]


def test_rectangles_are_capped():
    wide = _area([[1] * (ar.MAX_RUN + 5)])
    assert [r[1:3] for r in ar._rectangles(wide, 5)] == [
        [0, ar.MAX_RUN],
        [ar.MAX_RUN, ar.MAX_RUN + 5],
    ]
    tall = _area([[1]] * (ar.MAX_RUN + 5))
    assert [r[3:5] for r in ar._rectangles(tall, 5)] == [
        [0, ar.MAX_RUN],
        [ar.MAX_RUN, ar.MAX_RUN + 5],
    ]


def test_geojson_places_blocks_on_the_grid():
    area = _area([[1, 0], [0, 250]])
    gj = ar.to_geojson(area, radius_m=10_000, bands=5)
    assert gj["type"] == "FeatureCollection"
    props = [f["properties"] for f in gj["features"]]
    assert props == [
        {"band": 0, "from_m": 0.0, "to_m": 2000.0},
        {"band": 4, "from_m": 8000.0, "to_m": 10000.0},
    ]
    # Band 4 is the south-east block: its south-west corner is one block
    # east of the area's origin.
    ring = gj["features"][1]["geometry"]["coordinates"][0][0]
    assert ring[0] == ring[-1] and len(ring) == 5
    lon, lat = g.xy_to_lonlat(g.X0 + 101 * ar.BLOCK_M, g.Y0 + 200 * ar.BLOCK_M)
    assert ring[0] == [round(lon, 5), round(lat, 5)]
    # Rings run counter-clockwise (east first), as GeoJSON expects.
    assert ring[1][0] > ring[0][0]


def test_analysis_produces_an_aligned_area():
    # A straight road along row 50 of tile (10, 20), start at column 60,
    # 2.5 km budget: cells 50..70 are reached, i.e. blocks 12..17 of row 12.
    data = bytearray(T * T)
    for c in range(T):
        data[50 * T + c] = 1
    window = Window(10 * T + 60, 20 * T + 50, 10, 20, 10, 20)
    result = analyze(window, 2500.0, {(10, 20): bytes(data)}, {})
    area = result.area
    per_tile = ar.BLOCKS_PER_TILE
    assert (area.bcol, area.brow) == (10 * per_tile + 12, 20 * per_tile + 12)
    assert (area.width, area.height) == (6, 1)
    levels = list(area.data)
    assert all(levels)
    # The start cell (column 60) is in block 15: nearest, so the lowest level.
    assert levels[3] == 1 and levels[0] > levels[1] > levels[2] > levels[3]
    assert max(levels) <= ar.LEVELS
