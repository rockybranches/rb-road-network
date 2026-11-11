"""Market-area analysis: which counties can be reached by road from a point.

Pure standard library and free of Cloudflare imports. The caller fetches the
tiles named by `plan_window` from storage and hands the decompressed bytes to
`analyze`.
"""

import math
from dataclasses import dataclass, field

from . import grid as g
from .reach import UNITS_PER_CELL, UNREACHED, build_mosaic, reach, snap_to_road

MIN_RADIUS_M = 1_000.0  # the legacy tool's minimum
MAX_RADIUS_M = 300_000.0  # keeps the working grid within Worker memory
SNAP_CELLS = 8  # a start point may be this many cells (2 km) from a road
CELL_KM2 = (g.CELL_M / 1000.0) ** 2


class AnalysisError(ValueError):
    """The request cannot be analysed; the message is safe to show a user."""


@dataclass
class Window:
    """The start cell and the rectangle of tiles an analysis needs."""

    col: int
    row: int
    tx0: int
    ty0: int
    tx1: int
    ty1: int


@dataclass
class Analysis:
    start_lon: float
    start_lat: float
    snapped: bool  # True if the start was moved onto the nearest road cell
    reached_cells: int
    bbox: tuple  # (west, south, east, north) of reached cell centres, degrees
    county_cells: dict = field(default_factory=dict)  # GEOID -> reached cells
    outside_cells: int = 0  # reached cells that lie in no county
    # Land tiles within the radius that have no road data at all. Non-zero
    # means the road dataset stops short of the search area, so the result
    # is cut off there rather than genuinely unreachable.
    uncovered_tiles: int = 0

    @property
    def reached_km2(self):
        return self.reached_cells * CELL_KM2


def plan_window(lat, lon, radius_m):
    if not (MIN_RADIUS_M <= radius_m <= MAX_RADIUS_M):
        raise AnalysisError(
            f"radius_m must be between {MIN_RADIUS_M:.0f} and {MAX_RADIUS_M:.0f}"
        )
    if not (-90.0 < lat < 90.0 and -180.0 <= lon <= 180.0):
        raise AnalysisError("lat/lon out of range")
    col, row = g.xy_to_cell(*g.lonlat_to_xy(lon, lat))
    half = math.ceil(radius_m / g.CELL_M) + 1
    tx0, ty0 = g.cell_to_tile(col - half, row - half)
    tx1, ty1 = g.cell_to_tile(col + half, row + half)
    return Window(col, row, tx0, ty0, tx1, ty1)


def analyze(window, radius_m, road_tiles, county_tiles):
    """Run the reachability search and count reached cells per county.

    `road_tiles` and `county_tiles` map (tx, ty) -> decompressed tile bytes
    for the tiles inside `window`; tiles with no data may be absent.
    """
    if not road_tiles:
        raise AnalysisError("no road data is loaded for this area")
    w = window
    ntx, nty = w.tx1 - w.tx0 + 1, w.ty1 - w.ty0 + 1
    roads, width, height = build_mosaic(road_tiles, w.tx0, w.ty0, ntx, nty, g.TILE)
    counties, _, _ = build_mosaic(county_tiles, w.tx0, w.ty0, ntx, nty, g.TILE, "H")

    col_off = w.tx0 * g.TILE - 1  # mosaic column -> grid column
    row_off = w.ty0 * g.TILE - 1
    origin = (w.row - row_off) * width + (w.col - col_off)
    start = snap_to_road(roads, width, height, origin, SNAP_CELLS)
    if start < 0:
        raise AnalysisError(
            f"no road within {SNAP_CELLS * g.CELL_M / 1000:.0f} km of the start point"
        )

    dist = reach(roads, width, start, int(radius_m / g.CELL_M * UNITS_PER_CELL))

    county_cells = {}
    reached = 0
    cmin = rmin = 1 << 30
    cmax = rmax = -1
    for i, d in enumerate(dist):
        if d == UNREACHED:
            continue
        reached += 1
        geoid = counties[i]
        county_cells[geoid] = county_cells.get(geoid, 0) + 1
        r, c = divmod(i, width)
        if c < cmin:
            cmin = c
        if c > cmax:
            cmax = c
        if r < rmin:
            rmin = r
        if r > rmax:
            rmax = r

    def lonlat(c, r):
        return g.xy_to_lonlat(*g.cell_center_xy(c + col_off, r + row_off))

    west, south = lonlat(cmin, rmin)
    east, north = lonlat(cmax, rmax)
    start_lon, start_lat = lonlat(start % width, start // width)
    outside = county_cells.pop(0, 0)

    radius_cells = radius_m / g.CELL_M
    uncovered = 0
    for key in county_tiles:
        if key in road_tiles:
            continue
        c0, r0 = key[0] * g.TILE, key[1] * g.TILE
        dx = max(c0 - w.col, 0, w.col - (c0 + g.TILE - 1))
        dy = max(r0 - w.row, 0, w.row - (r0 + g.TILE - 1))
        if dx * dx + dy * dy <= radius_cells * radius_cells:
            uncovered += 1

    return Analysis(
        start_lon=start_lon,
        start_lat=start_lat,
        snapped=start != origin,
        reached_cells=reached,
        bbox=(west, south, east, north),
        county_cells=county_cells,
        outside_cells=outside,
        uncovered_tiles=uncovered,
    )
