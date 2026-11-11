#!/usr/bin/env python3
"""Rasterize a Geofabrik roads shapefile onto the national analysis grid.

Local-only tool (needs geopandas/pyogrio/shapely). Reads
one or more `gis_osm_roads_free_1.shp` files, drops non-drivable classes,
and writes one zlib-compressed 128x128 uint8 tile per 32 km square, each cell
holding the road-class bit flags from `rbnet.grid`.

Neighbouring extracts share tiles along their borders, so every extract that
belongs to one dataset must be passed in a single run: the tool merges them
before writing, whereas loading them separately would overwrite border tiles.

Output is a SQL file that loads straight into D1:

    rasterize_roads.py ga.shp al.shp --dataset osm-2026-02 --sql out/roads.sql
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


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("shapefiles", type=Path, nargs="+")
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
    write_tile_sql(args.sql, args.dataset, "roads", compressed)

    sizes = np.array([len(b) for _, _, b in compressed])
    print(
        json.dumps(
            {
                "shapefiles": len(args.shapefiles),
                "features_kept": kept,
                "features_skipped_not_drivable": skipped,
                "road_cells": int(len(keys)),
                "tiles": len(compressed),
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
