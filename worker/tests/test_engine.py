"""Engine tests. These run under ordinary CPython: the engine has no
Cloudflare imports, so nothing here needs the Workers runtime."""

import heapq
import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rbnet import grid as g  # noqa: E402
from rbnet.reach import (  # noqa: E402
    DIAG,
    ORTHO,
    UNREACHED,
    build_mosaic,
    reach,
    snap_to_road,
)

# Reference values from pyproj (EPSG:4326 -> EPSG:5070), rounded to the metre.
PROJ_CASES = [
    ((-84.4166, 33.732), (1063140, 1249903)),
    ((-122.4, 47.6), (-1973123, 3009861)),
    ((-68.0, 46.9), (2111804, 2969998)),
    ((-81.8, 24.55), (1452937, 277663)),
    ((-96.0, 23.0), (0, 0)),
]


@pytest.mark.parametrize("lonlat,expected", PROJ_CASES)
def test_projection_matches_epsg5070(lonlat, expected):
    x, y = g.lonlat_to_xy(*lonlat)
    assert abs(x - expected[0]) <= 1 and abs(y - expected[1]) <= 1


@pytest.mark.parametrize("lonlat,_", PROJ_CASES)
def test_projection_round_trip(lonlat, _):
    lon, lat = g.xy_to_lonlat(*g.lonlat_to_xy(*lonlat))
    assert abs(lon - lonlat[0]) < 1e-9 and abs(lat - lonlat[1]) < 1e-9


def _random_grid(rng, n, density):
    width = n + 2
    cells = bytearray(width * width)
    for r in range(1, n + 1):
        for c in range(1, n + 1):
            if rng.random() < density:
                cells[r * width + c] = 1
    start = (n // 2 + 1) * width + n // 2 + 1
    cells[start] = 1
    return cells, width, start


def _reference(cells, width, start, budget):
    """Textbook heap Dijkstra, kept deliberately independent of `reach`."""
    dist = {start: 0}
    heap = [(0, start)]
    steps = [(o, ORTHO) for o in (1, -1, width, -width)]
    steps += [(o, DIAG) for o in (width + 1, width - 1, -width + 1, -width - 1)]
    while heap:
        d, i = heapq.heappop(heap)
        if dist.get(i) != d:
            continue
        for off, cost in steps:
            j, nd = i + off, d + cost
            if cells[j] and nd <= budget and nd < dist.get(j, 1 << 30):
                dist[j] = nd
                heapq.heappush(heap, (nd, j))
    return dist


def test_reach_matches_reference_dijkstra():
    rng = random.Random(7)
    for _ in range(20):
        cells, width, start = _random_grid(rng, 40, 0.45)
        budget = rng.randint(5, 150)
        got = {
            i: d
            for i, d in enumerate(reach(cells, width, start, budget))
            if d != UNREACHED
        }
        assert got == _reference(cells, width, start, budget)


def test_reach_does_not_cross_gaps():
    # Two road cells separated by an empty cell are not connected.
    width = 7
    cells = bytearray(width * 3)
    cells[width + 1] = cells[width + 2] = cells[width + 4] = 1
    dist = reach(cells, width, width + 1, 100)
    assert dist[width + 2] == ORTHO
    assert dist[width + 4] == UNREACHED


def test_reach_respects_budget():
    width = 12
    cells = bytearray(width * 3)
    for c in range(1, 11):
        cells[width + c] = 1
    dist = reach(cells, width, width + 1, 3 * ORTHO)
    assert [dist[width + c] for c in range(1, 6)] == [0, 5, 10, 15, UNREACHED]


def test_build_mosaic_places_tiles_with_border():
    tile = 2
    tiles = {(5, 9): bytes([1, 2, 3, 4]), (6, 10): bytes([5, 6, 7, 8])}
    cells, width, height = build_mosaic(tiles, 5, 9, 2, 2, tile)
    assert (width, height) == (6, 6)
    rows = [list(cells[r * width : (r + 1) * width]) for r in range(height)]
    assert rows == [
        [0, 0, 0, 0, 0, 0],
        [0, 1, 2, 0, 0, 0],
        [0, 3, 4, 0, 0, 0],
        [0, 0, 0, 5, 6, 0],
        [0, 0, 0, 7, 8, 0],
        [0, 0, 0, 0, 0, 0],
    ]


def test_snap_to_road_finds_nearest_or_gives_up():
    width, height = 9, 9
    cells = bytearray(width * height)
    centre = 4 * width + 4
    assert snap_to_road(cells, width, height, centre, 3) == -1
    cells[4 * width + 6] = 1  # two cells east
    cells[1 * width + 1] = 1  # further away, diagonal
    assert snap_to_road(cells, width, height, centre, 3) == 4 * width + 6
    assert snap_to_road(cells, width, height, centre, 1) == -1
