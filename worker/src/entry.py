"""Worker entrypoint: road-distance market area analysis backed by D1.

Routes
  GET /                    status: which datasets are loaded
  GET /api/analysis        JSON report
  GET /api/analysis.tex    the same report as the legacy LaTeX table

Query parameters for both analysis routes
  lat, lon           start point in decimal degrees (required)
  radius_m           road-distance budget in metres (default 75000)
  tons_per_person    default 4.5
  min_km2            ignore counties with less reachable area than this
                     (default 0: any reachable cell counts, as before)
"""

import json
import time
import zlib
from urllib.parse import parse_qs, urlparse

from workers import Response, WorkerEntrypoint

from rbnet.analysis import CELL_KM2, AnalysisError, analyze, plan_window
from rbnet.report import DEFAULT_TONS_PER_PERSON, REPORT_YEARS, build_report, to_latex

DEFAULT_RADIUS_M = 75_000.0

TILES_SQL = (
    "SELECT layer, tx, ty, hex(data) AS h FROM raster_tiles "
    "WHERE ((dataset = ?1 AND layer = 'roads') OR (dataset = ?2 AND layer = 'counties')) "
    "AND ty BETWEEN ?3 AND ?4 AND tx BETWEEN ?5 AND ?6"
)
# One bound JSON array instead of one parameter per id: D1 allows only 100
# bound parameters and a wide search can reach more counties than that.
COUNTIES_SQL = (
    "SELECT geoid, name, stusps FROM counties "
    "WHERE geoid IN (SELECT value FROM json_each(?1))"
)
POPULATION_SQL = (
    "SELECT geoid, year, population FROM county_population "
    "WHERE geoid IN (SELECT value FROM json_each(?1)) "
    "AND year IN (SELECT value FROM json_each(?2))"
)


def _json(obj, status=200):
    return Response(
        json.dumps(obj), status=status, headers={"content-type": "application/json"}
    )


def _number(q, name, default=None):
    if name not in q:
        if default is None:
            raise AnalysisError(f"missing required parameter: {name}")
        return default
    try:
        return float(q[name])
    except ValueError:
        raise AnalysisError(f"{name} must be a number") from None


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        url = urlparse(request.url)
        q = {k: v[0] for k, v in parse_qs(url.query).items()}
        try:
            if url.path == "/":
                return await self.status()
            if url.path == "/api/analysis":
                return _json(await self.analysis(q))
            if url.path == "/api/analysis.tex":
                result = await self.analysis(q)
                return Response(
                    to_latex(result["report"]),
                    headers={"content-type": "text/plain; charset=utf-8"},
                )
        except AnalysisError as exc:
            return _json({"error": str(exc)}, 400)
        return _json({"error": "not found"}, 404)

    async def status(self):
        tiles = await self.env.DB.prepare(
            "SELECT dataset, layer, count(*) AS tiles FROM raster_tiles "
            "GROUP BY dataset, layer"
        ).all()
        counts = await self.env.DB.prepare(
            "SELECT (SELECT count(*) FROM counties) AS counties, "
            "(SELECT count(DISTINCT geoid) FROM county_population) AS with_population"
        ).first()
        return _json(
            {
                "ok": True,
                "active": {
                    "roads": self.env.ROADS_DATASET,
                    "counties": self.env.COUNTIES_DATASET,
                },
                "raster_tiles": [
                    {"dataset": r.dataset, "layer": r.layer, "tiles": r.tiles}
                    for r in tiles.results
                ],
                "counties": counts.counties,
                "counties_with_population": counts.with_population,
            }
        )

    async def analysis(self, q):
        lat = _number(q, "lat")
        lon = _number(q, "lon")
        radius_m = _number(q, "radius_m", DEFAULT_RADIUS_M)
        tons_per_person = _number(q, "tons_per_person", DEFAULT_TONS_PER_PERSON)
        min_km2 = _number(q, "min_km2", 0.0)
        window = plan_window(lat, lon, radius_m)
        db = self.env.DB

        t0 = time.perf_counter()
        res = (
            await db.prepare(TILES_SQL)
            .bind(
                self.env.ROADS_DATASET,
                self.env.COUNTIES_DATASET,
                window.ty0,
                window.ty1,
                window.tx0,
                window.tx1,
            )
            .all()
        )
        tiles = {"roads": {}, "counties": {}}
        for r in res.results:
            tiles[r.layer][(int(r.tx), int(r.ty))] = zlib.decompress(
                bytes.fromhex(r.h)
            )
        t1 = time.perf_counter()

        result = analyze(window, radius_m, tiles["roads"], tiles["counties"])
        t2 = time.perf_counter()

        kept = {
            geoid: cells
            for geoid, cells in result.county_cells.items()
            if cells * CELL_KM2 >= min_km2
        }
        ids = json.dumps(sorted(kept))
        county_rows = await db.prepare(COUNTIES_SQL).bind(ids).all()
        pop_rows = (
            await db.prepare(POPULATION_SQL)
            .bind(ids, json.dumps(list(REPORT_YEARS)))
            .all()
        )
        population = {}
        for r in pop_rows.results:
            population.setdefault(int(r.geoid), {})[int(r.year)] = int(r.population)
        counties = [
            {
                "geoid": int(r.geoid),
                "name": r.name,
                "state": r.stusps,
                "reached_km2": round(kept[int(r.geoid)] * CELL_KM2, 2),
                "population": population.get(int(r.geoid)),
            }
            for r in county_rows.results
        ]
        t3 = time.perf_counter()

        warnings = []
        if result.uncovered_tiles:
            warnings.append(
                "Road data is not loaded for part of the search area "
                f"({result.uncovered_tiles} land tiles within the radius), "
                "so the reachable area is cut off there."
            )

        return {
            "request": {
                "lat": lat,
                "lon": lon,
                "radius_m": radius_m,
                "tons_per_person": tons_per_person,
                "min_km2": min_km2,
            },
            "datasets": {
                "roads": self.env.ROADS_DATASET,
                "counties": self.env.COUNTIES_DATASET,
            },
            "start": {
                "lat": round(result.start_lat, 5),
                "lon": round(result.start_lon, 5),
                "moved_to_nearest_road": result.snapped,
            },
            "reachable": {
                "km2": round(result.reached_km2, 1),
                "bbox": [round(v, 4) for v in result.bbox],
                "counties_reached": len(result.county_cells),
                "counties_below_min_km2": len(result.county_cells) - len(kept),
            },
            "warnings": warnings,
            "report": build_report(counties, tons_per_person),
            "timing_ms": {
                "load_tiles": round((t1 - t0) * 1000, 1),
                "search": round((t2 - t1) * 1000, 1),
                "counties": round((t3 - t2) * 1000, 1),
            },
        }
