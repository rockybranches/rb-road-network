"""Spike Worker: proves the D1-backed road grid and the search run in Pyodide.

Routes
  GET /            D1 connectivity check (tile count per dataset)
  GET /bench       search on a synthetic grid: ?n=600&density=0.35&radius_m=75000
  GET /reach       search on real tiles from D1: ?lat=&lon=&radius_m=&dataset=
"""

import json
import math
import random
import time
import zlib
from urllib.parse import parse_qs, urlparse

from workers import Response, WorkerEntrypoint

from rbnet import grid as g
from rbnet.reach import UNITS_PER_CELL, UNREACHED, build_mosaic, reach, snap_to_road

SNAP_CELLS = 8  # how far (in cells) a start point may be from the nearest road


def _json(obj, status=200):
    return Response(
        json.dumps(obj), status=status, headers={"content-type": "application/json"}
    )


def _ms(t0):
    return round((time.perf_counter() - t0) * 1000, 1)


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        url = urlparse(request.url)
        q = {k: v[0] for k, v in parse_qs(url.query).items()}
        try:
            if url.path == "/":
                return await self.status()
            if url.path == "/bench":
                return self.bench(q)
            if url.path == "/reach":
                return await self.reach(q)
        except (KeyError, ValueError) as exc:
            return _json({"error": str(exc)}, 400)
        return _json({"error": "not found"}, 404)

    async def status(self):
        res = await self.env.DB.prepare(
            "SELECT dataset, layer, count(*) AS tiles, sum(length(data)) AS bytes "
            "FROM raster_tiles GROUP BY dataset, layer"
        ).all()
        rows = [
            {"dataset": r.dataset, "layer": r.layer, "tiles": r.tiles, "bytes": r.bytes}
            for r in res.results
        ]
        return _json({"ok": True, "raster_tiles": rows})

    def bench(self, q):
        n = int(q.get("n", 600))
        density = float(q.get("density", 0.35))
        radius_m = float(q.get("radius_m", 75000))
        rng = random.Random(1)
        width = n + 2
        t0 = time.perf_counter()
        cells = bytearray(width * width)
        for r in range(1, n + 1):
            base = r * width
            for c in range(1, n + 1):
                if rng.random() < density:
                    cells[base + c] = 1
        start = (n // 2 + 1) * width + n // 2 + 1
        cells[start] = 1
        build_ms = _ms(t0)
        t0 = time.perf_counter()
        dist = reach(cells, width, start, int(radius_m / g.CELL_M * UNITS_PER_CELL))
        search_ms = _ms(t0)
        reached = sum(1 for d in dist if d != UNREACHED)
        return _json(
            {
                "n": n,
                "density": density,
                "road_cells": sum(cells),
                "reached": reached,
                "build_ms": build_ms,
                "search_ms": search_ms,
            }
        )

    async def reach(self, q):
        lat, lon = float(q["lat"]), float(q["lon"])
        radius_m = float(q.get("radius_m", 75000))
        dataset = q.get("dataset", "spike")

        x, y = g.lonlat_to_xy(lon, lat)
        col, row = g.xy_to_cell(x, y)
        half = math.ceil(radius_m / g.CELL_M) + 1
        tx0, ty0 = g.cell_to_tile(col - half, row - half)
        tx1, ty1 = g.cell_to_tile(col + half, row + half)

        t0 = time.perf_counter()
        res = (
            await self.env.DB.prepare(
                "SELECT tx, ty, hex(data) AS h FROM raster_tiles "
                "WHERE dataset = ?1 AND layer = 'roads' "
                "AND ty BETWEEN ?2 AND ?3 AND tx BETWEEN ?4 AND ?5"
            )
            .bind(dataset, ty0, ty1, tx0, tx1)
            .all()
        )
        tiles = {
            (int(r.tx), int(r.ty)): zlib.decompress(bytes.fromhex(r.h))
            for r in res.results
        }
        fetch_ms = _ms(t0)
        if not tiles:
            return _json({"error": "no road data for this area"}, 404)

        t0 = time.perf_counter()
        cells, width, height = build_mosaic(
            tiles, tx0, ty0, tx1 - tx0 + 1, ty1 - ty0 + 1, g.TILE
        )
        origin = (row - ty0 * g.TILE + 1) * width + (col - tx0 * g.TILE + 1)
        start = snap_to_road(cells, width, height, origin, SNAP_CELLS)
        assemble_ms = _ms(t0)
        if start < 0:
            return _json({"error": "no road near the start point"}, 404)

        t0 = time.perf_counter()
        dist = reach(cells, width, start, int(radius_m / g.CELL_M * UNITS_PER_CELL))
        search_ms = _ms(t0)

        t0 = time.perf_counter()
        reached = 0
        cmin = rmin = 1 << 30
        cmax = rmax = -1
        for i, d in enumerate(dist):
            if d != UNREACHED:
                reached += 1
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
            return g.xy_to_lonlat(
                *g.cell_center_xy(c - 1 + tx0 * g.TILE, r - 1 + ty0 * g.TILE)
            )

        west, south = lonlat(cmin, rmin)
        east, north = lonlat(cmax, rmax)
        summarize_ms = _ms(t0)
        return _json(
            {
                "start": {"lat": lat, "lon": lon, "snapped_cells": start != origin},
                "radius_m": radius_m,
                "tiles": len(tiles),
                "grid": [width, height],
                "road_cells": sum(1 for v in cells if v),
                "reached_cells": reached,
                "reached_km2": round(reached * (g.CELL_M / 1000) ** 2, 1),
                "bbox_approx": [
                    round(west, 4),
                    round(south, 4),
                    round(east, 4),
                    round(north, 4),
                ],
                "ms": {
                    "d1_fetch_decode": fetch_ms,
                    "assemble": assemble_ms,
                    "search": search_ms,
                    "summarize": summarize_ms,
                },
            }
        )
