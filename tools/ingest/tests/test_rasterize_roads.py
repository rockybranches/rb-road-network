"""Tests for the roadless-tile coverage in rasterize_roads.

These need numpy, which the ingest extra provides; they are skipped where it
is not installed.
"""

import sys
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("pyogrio")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import rasterize_roads as rr  # noqa: E402
from rbnet.grid import TILE  # noqa: E402

TX0, TY0 = 40, 70


def _keys(cells):
    """Road cell keys from (col, row) offsets within the test grid."""
    return np.array(
        sorted((TY0 * TILE + r) * rr.KEY_COLS + TX0 * TILE + c for c, r in cells),
        dtype=np.int64,
    )


def test_roadless_tiles_are_added_only_for_states_with_roads():
    # Three tiles in a row. State 13 fills the first two, state 1 the third.
    grid = np.zeros((TILE, 3 * TILE), dtype=np.uint16)
    grid[:, : 2 * TILE] = 13001
    grid[:, 2 * TILE :] = 1001
    # State 13 has plenty of roads, all in its first tile. State 1 has only
    # a short stretch crossing its border.
    roads = [(c, r) for c in range(0, TILE, 2) for r in range(0, TILE, 8)]
    roads += [(2 * TILE + c, 5) for c in range(3)]
    tiles, shares = rr.roadless_covered_tiles(_keys(roads), grid, TX0, TY0)

    assert tiles == [(TX0 + 1, TY0)]
    assert shares[13] >= rr.MIN_STATE_ROAD_SHARE > shares[1] > 0


def test_tiles_outside_every_state_are_not_added():
    grid = np.zeros((TILE, 2 * TILE), dtype=np.uint16)
    grid[:, :TILE] = 13001
    roads = [(c, r) for c in range(TILE) for r in range(0, TILE, 8)]
    tiles, _ = rr.roadless_covered_tiles(_keys(roads), grid, TX0, TY0)
    assert tiles == []


def test_a_tile_shared_with_a_loaded_state_is_added():
    # The second tile is half state 13 (loaded) and half state 1 (not).
    grid = np.zeros((TILE, 2 * TILE), dtype=np.uint16)
    grid[:, : TILE + TILE // 2] = 13001
    grid[:, TILE + TILE // 2 :] = 1001
    roads = [(c, r) for c in range(TILE) for r in range(0, TILE, 8)]
    tiles, shares = rr.roadless_covered_tiles(_keys(roads), grid, TX0, TY0)
    assert tiles == [(TX0 + 1, TY0)]
    assert shares[1] == 0


def test_roads_outside_the_county_grid_are_ignored():
    grid = np.full((TILE, TILE), 13001, dtype=np.uint16)
    roads = [(c, r) for c in range(TILE) for r in range(0, TILE, 8)]
    roads += [(-5, 3), (TILE + 9, 3), (4, -2), (4, TILE + 1)]
    tiles, shares = rr.roadless_covered_tiles(_keys(roads), grid, TX0, TY0)
    assert tiles == []
    assert shares == {13: pytest.approx(1 / 8)}
