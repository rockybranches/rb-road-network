#!/usr/bin/env python3
"""Rasterize a Geofabrik roads shapefile onto the national analysis grid.

Local-only tool (needs geopandas/pyogrio/shapely). Reads
one or more `gis_osm_roads_free_1.shp` files, drops non-drivable classes,
and writes one zlib-compressed 128x128 uint8 tile per 32 km square, each cell
holding the road-class bit flags from `rbnet.grid`.

Neighbouring extracts share tiles along their borders, so every extract that
belongs to one dataset must be passed in a single run: the tool merges them
before writing, whereas loading them separately would overwrite border tiles.

The Worker reads a missing road tile over a county as "road data is not
loaded here" and warns about it. Open water and wilderness inside a loaded
state have no roads either, so with `--counties` the tool also writes an
empty tile for every roadless tile of each state it has roads for.

Output is a SQL file that loads straight into D1:

    rasterize_roads.py ga.shp al.shp --counties tl_2016_us_county.shp \
        --dataset osm-2026-02 --sql out/roads.sql
    wrangler d1 execute DB --local --file out/roads.sql
"""

import argparse
import json
import sys
import time
import zlib
from pathlib import Path

import numpy as np
import pyogrio
import shapely

from common import write_tile_sql
from rbnet.grid import CELL_M, FCLASS_BITS, TILE, X0, Y0

# Sample spacing along each road. Anything under one cell guarantees that
# consecutive samples land in the same or a touching cell, so a road always
# rasterizes to an 8-connected chain.
SAMPLE_M = CELL_M / 2.0
CHUNK = 250_000
KEY_COLS = 1 << 20  # packs (row, col) into one int64; far wider than CONUS
# A state has road data when at least this share of its cells hold a road.
# The emptiest loaded state is many times above it (0.17); a state that only
# receives the roads crossing in from a neighbour's extract is far below.
MIN_STATE_ROAD_SHARE = 0.01


def rasterize(shp_path: Path):
    """Return (keys, bits): sorted unique cell keys and their class bit flags."""
    info = pyogrio.read_info(shp_path)
    total = info["features"]
    keys_parts, bits_parts = [], []
    kept = skipped = 0
    for start in range(0, total, CHUNK):
        gdf = pyogrio.read_dataframe(
            shp_path, columns=["fclass"], skip_features=start, max_features=CHUNK
        )
        cls = gdf["fclass"].map(FCLASS_BITS)
        skipped += int(cls.isna().sum())
        gdf = gdf[cls.notna()]
        cls = cls[cls.notna()].astype(np.uint8)
        if gdf.empty:
            continue
        kept += len(gdf)
        geoms = shapely.segmentize(gdf.geometry.to_crs(5070).values, SAMPLE_M)
        coords, index = shapely.get_coordinates(geoms, return_index=True)
        col = np.floor((coords[:, 0] - X0) / CELL_M).astype(np.int64)
        row = np.floor((coords[:, 1] - Y0) / CELL_M).astype(np.int64)
        keys_parts.append(row * KEY_COLS + col)
        bits_parts.append(cls.to_numpy()[index])
        print(f"  {min(start + CHUNK, total):>9,}/{total:,} features", file=sys.stderr)

    keys, bits = merge_cells(np.concatenate(keys_parts), np.concatenate(bits_parts))
    return keys, bits, kept, skipped


def merge_cells(keys, bits):
    """Collapse duplicate cell keys, OR-ing their class bits together."""
    order = np.argsort(keys, kind="stable")
    keys, bits = keys[order], bits[order]
    starts = np.flatnonzero(np.r_[True, keys[1:] != keys[:-1]])
    return keys[starts], np.bitwise_or.reduceat(bits, starts)


def to_tiles(keys, bits):
    """Yield (tx, ty, tile) with tile a (TILE, TILE) uint8 array, row 0 = south."""
    row, col = keys // KEY_COLS, keys % KEY_COLS
    ty, tx = row // TILE, col // TILE
    tkey = ty * KEY_COLS + tx
    order = np.argsort(tkey, kind="stable")
    tkey, row, col, bits = tkey[order], row[order], col[order], bits[order]
    starts = np.flatnonzero(np.r_[True, tkey[1:] != tkey[:-1]])
    ends = np.r_[starts[1:], len(tkey)]
    for s, e in zip(starts, ends):
        tile = np.zeros((TILE, TILE), dtype=np.uint8)
        tile[row[s:e] % TILE, col[s:e] % TILE] = bits[s:e]
        yield int(tkey[s] % KEY_COLS), int(tkey[s] // KEY_COLS), tile


def roadless_covered_tiles(keys, county_grid, tx0, ty0):
    """Find the roadless tiles of every state that has road data.

    `county_grid` is the tile-aligned grid of county GEOIDs from
    `rasterize_counties.rasterize`, whose south-west tile is (tx0, ty0).
    Returns (tiles, shares): the (tx, ty) of each tile that touches a state
    with road data but holds no road cell, and {state FIPS: share of the
    state's cells that hold a road} for every state.
    """
    nty, ntx = county_grid.shape[0] // TILE, county_grid.shape[1] // TILE
    row = keys // KEY_COLS - ty0 * TILE
    col = keys % KEY_COLS - tx0 * TILE
    inside = (row >= 0) & (row < county_grid.shape[0]) & (col >= 0) & (col < county_grid.shape[1])
    row, col = row[inside], col[inside]

    state = (county_grid // 1000).astype(np.uint8)  # GEOID = state * 1000 + county
    cells = np.bincount(state.ravel(), minlength=100)
    roads = np.bincount(state[row, col], minlength=100)
    shares = {int(s): float(roads[s] / cells[s]) for s in np.flatnonzero(cells) if s}
    has_data = np.zeros(len(cells), dtype=bool)
    for s, share in shares.items():
        has_data[s] = share >= MIN_STATE_ROAD_SHARE

    covered = has_data[state].reshape(nty, TILE, ntx, TILE).any(axis=(1, 3))
    covered[row // TILE, col // TILE] = False  # these tiles have roads
    return [(tx0 + int(i), ty0 + int(j)) for j, i in zip(*np.nonzero(covered))], shares


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("shapefiles", type=Path, nargs="+")
    ap.add_argument(
        "--counties", type=Path,
        help="county boundaries shapefile; adds an empty tile for every "
        "roadless tile of each state that has roads",
    )  # fmt: skip
    ap.add_argument("--dataset", required=True, help="dataset version label")
    ap.add_argument("--sql", type=Path, required=True, help="output SQL file")
    args = ap.parse_args()

    t0 = time.time()
    parts, kept, skipped = [], 0, 0
    for shp in args.shapefiles:
        print(f"{shp}", file=sys.stderr)
        k, b, n_kept, n_skipped = rasterize(shp)
        parts.append((k, b))
        kept += n_kept
        skipped += n_skipped
    keys, bits = merge_cells(
        np.concatenate([k for k, _ in parts]), np.concatenate([b for _, b in parts])
    )
    compressed = []
    raw_cells = 0
    for tx, ty, tile in to_tiles(keys, bits):
        compressed.append((tx, ty, zlib.compress(tile.tobytes(), 9)))
        raw_cells += tile.size
    sizes = np.array([len(b) for _, _, b in compressed])

    coverage = {}
    if args.counties:
        import rasterize_counties

        print(f"{args.counties}", file=sys.stderr)
        grid, tx0, ty0 = rasterize_counties.rasterize(
            rasterize_counties.read_counties(args.counties)
        )
        empty, shares = roadless_covered_tiles(keys, grid, tx0, ty0)
        blank = zlib.compress(bytes(TILE * TILE), 9)
        compressed.extend((tx, ty, blank) for tx, ty in empty)
        loaded = {s: v for s, v in shares.items() if v >= MIN_STATE_ROAD_SHARE}
        coverage = {
            "states_with_roads": len(loaded),
            "states_without_roads": sorted(set(shares) - set(loaded)),
            "lowest_road_share": round(min(loaded.values()), 4) if loaded else None,
            "highest_road_share_without": round(
                max((v for s, v in shares.items() if s not in loaded), default=0.0), 4
            ),
            "roadless_tiles_added": len(empty),
        }
    write_tile_sql(args.sql, args.dataset, "roads", compressed)

    print(
        json.dumps(
            {
                "shapefiles": len(args.shapefiles),
                "features_kept": kept,
                "features_skipped_not_drivable": skipped,
                "road_cells": int(len(keys)),
                "tiles": len(compressed),
                **coverage,
                "occupied_fraction": round(len(keys) / raw_cells, 4),
                "raw_bytes": raw_cells,
                "compressed_bytes": int(sizes.sum()),
                "tile_bytes_mean": int(sizes.mean()),
                "tile_bytes_max": int(sizes.max()),
                "sql_bytes": args.sql.stat().st_size,
                "seconds": round(time.time() - t0, 1),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
