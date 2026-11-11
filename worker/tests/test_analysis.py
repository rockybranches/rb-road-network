import struct

import pytest

from rbnet import grid as g
from rbnet.analysis import CELL_KM2, AnalysisError, Window, analyze, plan_window

T = g.TILE


def _road_tile(cells):
    """A roads tile with the given (col, row) cells set."""
    data = bytearray(T * T)
    for c, r in cells:
        data[r * T + c] = 1
    return bytes(data)


def _county_tile(fn):
    """A counties tile whose cell (col, row) holds fn(col, row)."""
    return struct.pack(f"<{T * T}H", *(fn(c, r) for r in range(T) for c in range(T)))


def _window(col, row, tx=10, ty=20):
    return Window(tx * T + col, ty * T + row, tx, ty, tx, ty)


def test_counts_reached_cells_per_county():
    # A straight east-west road along row 50, crossing from county 13001
    # (columns 0-63) into county 13003 (columns 64-127).
    roads = {(10, 20): _road_tile((c, 50) for c in range(T))}
    counties = {(10, 20): _county_tile(lambda c, r: 13001 if c < 64 else 13003)}
    # Start at column 60; a 2.5 km budget is ten cells each way.
    result = analyze(_window(60, 50), 2500.0, roads, counties)
    assert result.reached_cells == 21
    assert result.county_cells == {13001: 14, 13003: 7}  # cols 50-63, 64-70
    assert result.reached_km2 == 21 * CELL_KM2
    assert not result.snapped
    assert result.uncovered_tiles == 0


def test_cells_outside_any_county_are_counted_separately():
    roads = {(10, 20): _road_tile((c, 50) for c in range(T))}
    counties = {(10, 20): _county_tile(lambda c, r: 13001 if c < 64 else 0)}
    result = analyze(_window(60, 50), 2500.0, roads, counties)
    assert result.county_cells == {13001: 14}
    assert result.outside_cells == 7


def test_start_is_moved_to_nearest_road():
    roads = {(10, 20): _road_tile((c, 50) for c in range(T))}
    counties = {(10, 20): _county_tile(lambda c, r: 13001)}
    result = analyze(_window(60, 53), 2500.0, roads, counties)
    assert result.snapped
    assert result.reached_cells == 21


def test_start_too_far_from_any_road_is_an_error():
    roads = {(10, 20): _road_tile([(5, 5)])}
    counties = {(10, 20): _county_tile(lambda c, r: 13001)}
    with pytest.raises(AnalysisError, match="no road within"):
        analyze(_window(100, 100), 2500.0, roads, counties)


def test_no_road_tiles_is_an_error():
    with pytest.raises(AnalysisError, match="no road data"):
        analyze(_window(60, 50), 2500.0, {}, {})


def test_land_without_road_data_is_flagged():
    # Two tiles of land side by side; only the western one has roads.
    roads = {(10, 20): _road_tile((c, 50) for c in range(T))}
    land = _county_tile(lambda c, r: 13001)
    counties = {(10, 20): land, (11, 20): land}
    window = Window(10 * T + 120, 20 * T + 50, 10, 20, 11, 20)
    assert analyze(window, 5000.0, roads, counties).uncovered_tiles == 1
    # A search that stays clear of the uncovered tile is not flagged.
    far = Window(10 * T + 20, 20 * T + 50, 10, 20, 11, 20)
    assert analyze(far, 5000.0, roads, counties).uncovered_tiles == 0


def test_plan_window_covers_the_radius():
    w = plan_window(33.732, -84.4166, 75000.0)
    assert g.cell_to_tile(w.col, w.row) == (109, 33)
    half = 75000.0 / g.CELL_M
    assert w.tx0 * T <= w.col - half and (w.tx1 + 1) * T > w.col + half
    assert w.ty0 * T <= w.row - half and (w.ty1 + 1) * T > w.row + half


@pytest.mark.parametrize("radius", [999.0, 300_001.0])
def test_plan_window_rejects_radius_out_of_range(radius):
    with pytest.raises(AnalysisError):
        plan_window(33.7, -84.4, radius)
