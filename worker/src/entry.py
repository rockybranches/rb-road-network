"""Worker entrypoint: road-distance market area analysis backed by D1.

Everything under /api is handled here; all other paths are the static map
page in `public/`, which Cloudflare serves without invoking this code.

Routes
  GET    /api/status                      which datasets are loaded
  GET    /api/analysis                    run an analysis, do not store it
  GET    /api/analysis.tex                the same, as the legacy LaTeX table
  POST   /api/analyses                    run an analysis and store it
  GET    /api/analyses                    recent stand-alone analyses
  GET    /api/analyses/{id}               a stored analysis with its result
  GET    /api/analyses/{id}/report.tex    its report as the legacy LaTeX table
  GET    /api/analyses/{id}/area.geojson  its reachable area, for maps
  POST   /api/analyses/{id}/run           run a pending or failed batch row
  DELETE /api/analyses/{id}
  POST   /api/batches                     create a batch from a sites CSV
  GET    /api/batches                     batches with progress counts
  GET    /api/batches/{id}                a batch and its rows
  GET    /api/batches/{id}/summary.csv    one line per site
  DELETE /api/batches/{id}                the batch and all its rows

Analysis parameters (query string for GET, JSON body for POST)
  lat, lon           start point in decimal degrees (required)
  radius_m           road-distance budget in metres (default 75000)
  tons_per_person    default 4.5
  min_km2            ignore counties with less reachable area than this
                     (default 0: any reachable cell counts, as before)
  label              optional name for a stored analysis

A batch is created with every row 'pending'; the client then calls
/api/analyses/{id}/run for each row. Each run is an ordinary short request,
so a batch of any size stays within Worker limits and can be resumed.
"""

import json
import secrets
import time
import traceback
import zlib
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

from workers import Response, WorkerEntrypoint

from rbnet import area as ar
from rbnet.analysis import CELL_KM2, AnalysisError, analyze, plan_window
from rbnet.params import Params, parse_params, parse_sites_csv, summary_csv
from rbnet.report import BASE_YEAR, REPORT_YEARS, TARGET_YEAR, build_report, to_latex

MAX_BODY_BYTES = 256 * 1024
LIST_LIMIT = 100

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

# Stored rows are read back as one JSON document per row, built by SQLite.
# That keeps SQL NULLs as JSON nulls instead of passing them through the
# JavaScript bridge, and makes the record shape identical on every route.
RECORD = (
    "json_object('id', id, 'batch_id', batch_id, 'seq', seq, 'status', status, "
    "'error', error, 'created_at', created_at, 'completed_at', completed_at, "
    "'request', json_object('label', label, 'lat', lat, 'lon', lon, "
    "'radius_m', radius_m, 'tons_per_person', tons_per_person, 'min_km2', min_km2), "
    "'summary', CASE WHEN status = 'done' THEN json_object('counties', counties, "
    "'reached_km2', reached_km2, 'population_base', population_base, "
    "'population_target', population_target) END"
)
RECORD_SQL = f"SELECT {RECORD}) AS j FROM analyses "
FULL_RECORD_SQL = f"SELECT {RECORD}, 'result', json(result)) AS j FROM analyses WHERE id = ?1"

# Rows are written from one bound JSON array for the same reason: optional
# values arrive as JSON nulls, and a whole batch is a single statement.
INSERT_SQL = (
    "INSERT INTO analyses (id, batch_id, seq, label, lat, lon, radius_m, "
    "tons_per_person, min_km2, status, created_at, completed_at, counties, "
    "reached_km2, population_base, population_target, result, area) "
    "SELECT v->>'id', v->>'batch_id', v->>'seq', v->>'label', v->>'lat', v->>'lon', "
    "v->>'radius_m', v->>'tons_per_person', v->>'min_km2', v->>'status', "
    "v->>'created_at', v->>'completed_at', v->>'counties', v->>'reached_km2', "
    "v->>'population_base', v->>'population_target', v->>'result', "
    "unhex(v->>'area') FROM (SELECT value AS v FROM json_each(?1))"
)
FINISH_SQL = (
    "UPDATE analyses SET status = ?2->>'status', error = ?2->>'error', "
    "completed_at = ?2->>'completed_at', counties = ?2->>'counties', "
    "reached_km2 = ?2->>'reached_km2', population_base = ?2->>'population_base', "
    "population_target = ?2->>'population_target', result = ?2->>'result', "
    "area = unhex(?2->>'area') WHERE id = ?1"
)
BATCHES_SQL = (
    "SELECT json_object('id', b.id, 'label', b.label, 'created_at', b.created_at, "
    "'sites', count(a.id), "
    "'done', coalesce(sum(a.status = 'done'), 0), "
    "'failed', coalesce(sum(a.status = 'failed'), 0)) AS j "
    "FROM batches b LEFT JOIN analyses a ON a.batch_id = b.id "
)


class NotFound(Exception):
    pass


def _json(obj, status=200):
    return Response(
        json.dumps(obj), status=status, headers={"content-type": "application/json"}
    )


def _text(body, content_type="text/plain; charset=utf-8"):
    return Response(body, headers={"content-type": content_type})


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _new_id():
    return secrets.token_hex(8)


def _stored_fields(result, area):
    """The columns a finished analysis fills in, from its API result."""
    report = result["report"]
    years = report["years"]
    reachable = result["reachable"]
    return {
        "status": "done",
        "error": None,
        "completed_at": _now(),
        "counties": reachable["counties_reached"] - reachable["counties_below_min_km2"],
        "reached_km2": reachable["km2"],
        "population_base": report["totals"][years.index(BASE_YEAR)],
        "population_target": report["totals"][years.index(TARGET_YEAR)],
        "result": json.dumps(result),
        "area": ar.encode(area).hex(),
    }


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        url = urlparse(request.url)
        parts = [p for p in url.path.split("/") if p]
        query = {k: v[0] for k, v in parse_qs(url.query).items()}
        try:
            if parts[:1] == ["api"]:
                return await self.route(request, request.method, parts[1:], query)
            raise NotFound
        except AnalysisError as exc:
            return _json({"error": str(exc)}, 400)
        except NotFound:
            return _json({"error": "not found"}, 404)
        except Exception:
            traceback.print_exc()  # goes to the Worker's logs
            return _json({"error": "internal error"}, 500)

    async def route(self, request, method, parts, query):
        match (method, parts):
            case ("GET", ["status"]):
                return _json(await self.status())
            case ("GET", ["analysis"]):
                result, _ = await self.compute(parse_params(query))
                return _json(result)
            case ("GET", ["analysis.tex"]):
                result, _ = await self.compute(parse_params(query))
                return _text(to_latex(result["report"]))
            case ("POST", ["analyses"]):
                return _json(await self.create_analysis(await self.body(request)), 201)
            case ("GET", ["analyses"]):
                return _json({"analyses": await self.list_analyses()})
            case ("GET", ["analyses", aid]):
                return _json(await self.record(aid))
            case ("GET", ["analyses", aid, "report.tex"]):
                record = await self.record(aid)
                if not record["result"]:
                    raise NotFound
                return _text(to_latex(record["result"]["report"]))
            case ("GET", ["analyses", aid, "area.geojson"]):
                return _text(json.dumps(await self.area(aid)), "application/geo+json")
            case ("POST", ["analyses", aid, "run"]):
                return _json(await self.run_analysis(aid))
            case ("DELETE", ["analyses", aid]):
                await self.record(aid)
                await self.execute("DELETE FROM analyses WHERE id = ?1", aid)
                return _json({"deleted": aid})
            case ("POST", ["batches"]):
                return _json(await self.create_batch(await self.body(request)), 201)
            case ("GET", ["batches"]):
                return _json({"batches": await self.list_batches()})
            case ("GET", ["batches", bid]):
                return _json(await self.batch(bid))
            case ("GET", ["batches", bid, "summary.csv"]):
                batch = await self.batch(bid)
                return _text(summary_csv(batch["analyses"]), "text/csv; charset=utf-8")
            case ("DELETE", ["batches", bid]):
                await self.batch(bid)
                await self.execute("DELETE FROM analyses WHERE batch_id = ?1", bid)
                await self.execute("DELETE FROM batches WHERE id = ?1", bid)
                return _json({"deleted": bid})
        raise NotFound

    # -- storage helpers ---------------------------------------------------

    async def rows(self, sql, *args):
        """Run a query whose single column `j` is a JSON document per row."""
        stmt = self.env.DB.prepare(sql)
        res = await (stmt.bind(*args) if args else stmt).all()
        return [json.loads(r.j) for r in res.results]

    async def execute(self, sql, *args):
        await self.env.DB.prepare(sql).bind(*args).run()

    async def body(self, request):
        text = await request.text()
        if len(text) > MAX_BODY_BYTES:
            raise AnalysisError("request body is too large")
        try:
            data = json.loads(text)
        except ValueError:
            raise AnalysisError("request body must be JSON") from None
        if not isinstance(data, dict):
            raise AnalysisError("request body must be a JSON object")
        return data

    async def record(self, aid):
        found = await self.rows(FULL_RECORD_SQL, aid)
        if not found:
            raise NotFound
        return found[0]

    # -- routes ------------------------------------------------------------

    async def status(self):
        tiles = await self.env.DB.prepare(
            "SELECT dataset, layer, count(*) AS tiles FROM raster_tiles "
            "GROUP BY dataset, layer"
        ).all()
        counts = await self.env.DB.prepare(
            "SELECT (SELECT count(*) FROM counties) AS counties, "
            "(SELECT count(DISTINCT geoid) FROM county_population) AS with_population"
        ).first()
        return {
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

    async def create_analysis(self, data):
        params = parse_params(data)
        result, area = await self.compute(params)
        row = {
            "id": _new_id(),
            "batch_id": None,
            "seq": 0,
            "created_at": _now(),
            **params.to_dict(),
            **_stored_fields(result, area),
        }
        await self.execute(INSERT_SQL, json.dumps([row]))
        return await self.record(row["id"])

    async def list_analyses(self):
        return await self.rows(
            RECORD_SQL
            + f"WHERE batch_id IS NULL ORDER BY created_at DESC, id LIMIT {LIST_LIMIT}"
        )

    async def area(self, aid):
        found = await self.rows(
            "SELECT json_object('h', hex(area), 'radius_m', radius_m) AS j "
            "FROM analyses WHERE id = ?1 AND area IS NOT NULL",
            aid,
        )
        if not found:
            raise NotFound
        stored = ar.decode(bytes.fromhex(found[0]["h"]))
        return ar.to_geojson(stored, found[0]["radius_m"])

    async def run_analysis(self, aid):
        record = await self.record(aid)
        if record["status"] == "done":
            return record
        try:
            result, area = await self.compute(parse_params(record["request"]))
            fields = _stored_fields(result, area)
        except AnalysisError as exc:
            # A site that cannot be analysed (no road nearby, no data loaded)
            # is a result for that row, not a failure of the request.
            fields = {"status": "failed", "error": str(exc), "completed_at": _now()}
        await self.execute(FINISH_SQL, aid, json.dumps(fields))
        return await self.record(aid)

    async def create_batch(self, data):
        defaults = parse_params({**data, "lat": 0, "lon": 0, "label": ""})
        csv_text = data.get("csv")
        if not isinstance(csv_text, str):
            raise AnalysisError("missing required field: csv")
        sites = parse_sites_csv(csv_text, defaults)
        created = _now()
        label = str(data.get("label") or "").strip() or f"Batch {created[:10]}"
        batch_id = _new_id()
        rows = [
            {
                "id": _new_id(),
                "batch_id": batch_id,
                "seq": seq,
                "status": "pending",
                "created_at": created,
                **site.to_dict(),
            }
            for seq, site in enumerate(sites)
        ]
        await self.execute(
            "INSERT INTO batches (id, label, created_at) VALUES (?1, ?2, ?3)",
            batch_id,
            label[:120],
            created,
        )
        await self.execute(INSERT_SQL, json.dumps(rows))
        return await self.batch(batch_id)

    async def list_batches(self):
        return await self.rows(
            BATCHES_SQL
            + f"GROUP BY b.id ORDER BY b.created_at DESC, b.id LIMIT {LIST_LIMIT}"
        )

    async def batch(self, bid):
        found = await self.rows(BATCHES_SQL + "WHERE b.id = ?1 GROUP BY b.id", bid)
        if not found:
            raise NotFound
        batch = found[0]
        batch["analyses"] = await self.rows(
            RECORD_SQL + "WHERE batch_id = ?1 ORDER BY seq", bid
        )
        return batch

    async def compute(self, params):
        """Run one analysis. Returns (API result, reachable-area grid)."""
        p = params
        window = plan_window(p.lat, p.lon, p.radius_m)
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

        found = analyze(window, p.radius_m, tiles["roads"], tiles["counties"])
        t2 = time.perf_counter()

        kept = {
            geoid: cells
            for geoid, cells in found.county_cells.items()
            if cells * CELL_KM2 >= p.min_km2
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
        if found.uncovered_tiles:
            warnings.append(
                "Road data is not loaded for part of the search area "
                f"({found.uncovered_tiles} land tiles within the radius), "
                "so the reachable area is cut off there."
            )

        result = {
            "request": p.to_dict(),
            "datasets": {
                "roads": self.env.ROADS_DATASET,
                "counties": self.env.COUNTIES_DATASET,
            },
            "start": {
                "lat": round(found.start_lat, 5),
                "lon": round(found.start_lon, 5),
                "moved_to_nearest_road": found.snapped,
            },
            "reachable": {
                "km2": round(found.reached_km2, 1),
                "bbox": [round(v, 4) for v in found.bbox],
                "counties_reached": len(found.county_cells),
                "counties_below_min_km2": len(found.county_cells) - len(kept),
            },
            "warnings": warnings,
            "report": build_report(counties, p.tons_per_person),
            "timing_ms": {
                "load_tiles": round((t1 - t0) * 1000, 1),
                "search": round((t2 - t1) * 1000, 1),
                "counties": round((t3 - t2) * 1000, 1),
            },
        }
        return result, found.area
