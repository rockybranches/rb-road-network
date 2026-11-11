#!/usr/bin/env python3
"""Rasterize county polygons onto the national analysis grid.

Local-only tool (needs geopandas/pyogrio/shapely). Reads a TIGER/Line county
shapefile and writes, as SQL that loads straight into D1:

- the "counties" raster layer: one zlib-compressed 128x128 tile of
  little-endian uint16 per 32 km square, each cell holding the county GEOID
  (state FIPS * 1000 + county FIPS, at most 56045) of the county containing
  the cell centre, or 0 for none;
- the `counties` table: one row of attributes per county.

Only the contiguous US and DC are kept; the grid does not cover the rest.

    rasterize_counties.py tl_2016_us_county.shp --dataset tl-2016 --sql out/counties.sql
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

from common import CONUS_STATES, write_inserts, write_tile_sql
from rbnet.grid import CELL_M, TILE, TILE_M, X0, Y0

COLUMNS = ["STATEFP", "GEOID", "COUNTYNS", "NAME", "NAMELSAD", "INTPTLAT", "INTPTLON"]


def read_counties(shp_path):
    gdf = pyogrio.read_dataframe(shp_path, columns=COLUMNS)
    return gdf[gdf["STATEFP"].isin(CONUS_STATES.keys())].reset_index(drop=True)


def rasterize(gdf):
    """Return (grid, tx0, ty0): a tile-aligned uint16 array of county GEOIDs."""
    geoms = gdf.geometry.to_crs(5070).values
    minx, miny, maxx, maxy = shapely.total_bounds(geoms)
    tx0 = int(np.floor((minx - X0) / TILE_M))
    ty0 = int(np.floor((miny - Y0) / TILE_M))
    tx1 = int(np.floor((maxx - X0) / TILE_M))
    ty1 = int(np.floor((maxy - Y0) / TILE_M))
    col_off, row_off = tx0 * TILE, ty0 * TILE
    grid = np.zeros(((ty1 - ty0 + 1) * TILE, (tx1 - tx0 + 1) * TILE), dtype=np.uint16)

    shapely.prepare(geoms)
    for n, (geoid, geom) in enumerate(zip(gdf["GEOID"].astype(int), geoms), 1):
        bx0, by0, bx1, by1 = geom.bounds
        # Cells whose centre can fall inside the bounding box.
        c0 = int(np.floor((bx0 - X0) / CELL_M - 0.5)) + 1
        c1 = int(np.floor((bx1 - X0) / CELL_M - 0.5))
        r0 = int(np.floor((by0 - Y0) / CELL_M - 0.5)) + 1
        r1 = int(np.floor((by1 - Y0) / CELL_M - 0.5))
        if c1 < c0 or r1 < r0:
            continue  # smaller than one cell and containing no centre
        xs = X0 + (np.arange(c0, c1 + 1) + 0.5) * CELL_M
        ys = Y0 + (np.arange(r0, r1 + 1) + 0.5) * CELL_M
        inside = shapely.contains_xy(geom, *np.meshgrid(xs, ys))
        window = grid[r0 - row_off : r1 - row_off + 1, c0 - col_off : c1 - col_off + 1]
        window[inside] = geoid
        if n % 500 == 0 or n == len(gdf):
            print(f"  {n:>5,}/{len(gdf):,} counties", file=sys.stderr)
    return grid, tx0, ty0


def to_tiles(grid, tx0, ty0):
    """Yield (tx, ty, blob) for every tile that contains any county."""
    for j in range(grid.shape[0] // TILE):
        for i in range(grid.shape[1] // TILE):
            tile = grid[j * TILE : (j + 1) * TILE, i * TILE : (i + 1) * TILE]
            if tile.any():
                data = tile.astype("<u2").tobytes()
                yield tx0 + i, ty0 + j, zlib.compress(data, 9)


def county_rows(gdf):
    for r in gdf.itertuples(index=False):
        yield (
            int(r.GEOID),
            int(r.COUNTYNS),
            r.NAME,
            r.NAMELSAD,
            r.STATEFP,
            CONUS_STATES[r.STATEFP],
            float(r.INTPTLAT),
            float(r.INTPTLON),
        )


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("shapefile", type=Path)
    ap.add_argument("--dataset", required=True, help="dataset version label")
    ap.add_argument("--sql", type=Path, required=True, help="output SQL file")
    args = ap.parse_args()

    t0 = time.time()
    gdf = read_counties(args.shapefile)
    grid, tx0, ty0 = rasterize(gdf)
    tiles = list(to_tiles(grid, tx0, ty0))
    write_tile_sql(args.sql, args.dataset, "counties", tiles)
    with args.sql.open("a") as f:
        f.write("DELETE FROM counties;\n")
        write_inserts(
            f,
            "counties",
            ("geoid", "countyns", "name", "namelsad", "state_fips", "stusps",
             "intpt_lat", "intpt_lon"),
            county_rows(gdf),
        )  # fmt: skip

    present = np.unique(grid)
    sizes = np.array([len(b) for _, _, b in tiles])
    missing = sorted(set(gdf["GEOID"].astype(int)) - set(present.tolist()))
    print(
        json.dumps(
            {
                "counties": len(gdf),
                "counties_with_no_cell": missing,
                "land_cells": int(np.count_nonzero(grid)),
                "tiles": len(tiles),
                "compressed_bytes": int(sizes.sum()),
                "tile_bytes_max": int(sizes.max()),
                "sql_bytes": args.sql.stat().st_size,
                "seconds": round(time.time() - t0, 1),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
