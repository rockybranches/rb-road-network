# rb-road-network Worker

Cloudflare Python Worker that answers "which counties, and how many people,
are within a road distance of this point" from data stored in D1.

## How it works

- Roads and county boundaries are stored as tiles on one national grid
  (EPSG:5070, 250 m cells, 128-cell tiles) in the `raster_tiles` table.
- A request loads the tiles around the start point, runs a shortest-path
  search over road cells up to the distance budget, and counts the reached
  cells in each county.
- County names and population series come from the `counties` and
  `county_population` tables, and are summarised into the report.

## Layout

- `src/entry.py` — Worker entrypoint and routes
- `src/rbnet/grid.py` — the national grid and projection
- `src/rbnet/reach.py` — the search
- `src/rbnet/analysis.py` — reachability plus the per-county roll-up
- `src/rbnet/report.py` — population report and the legacy LaTeX layout
- `migrations/` — D1 schema
- `tests/` — run with ordinary pytest; `rbnet` has no Cloudflare imports
- `../tools/ingest/` — local tools that build the SQL loaded into D1

## Build the data

The ingest tools need geopandas, so they run with the repo root's `.venv`.
Output goes to `build/d1/`, which is git-ignored.

```bash
cd ..   # repo root
PY=.venv/bin/python

# Roads: pass every state extract for one dataset in a single run.
$PY tools/ingest/rasterize_roads.py \
  "$RB_DATA"/gis_osm_roads_extra/*_geom/gis_osm_roads_free_1.shp \
  --dataset osm-2026-02 --sql build/d1/roads.sql

# County boundaries and attributes (contiguous US).
$PY tools/ingest/rasterize_counties.py \
  "$RB_DATA"/tl_2016_us_county/tl_2016_us_county.shp \
  --dataset tl-2016 --sql build/d1/counties.sql

# Population. Prints which rows it corrected or could not place.
$PY tools/ingest/load_population.py \
  --counties "$RB_DATA"/tl_2016_us_county/tl_2016_us_county.shp \
  --csv-dir "$RB_DATA"/county_pop \
  --source county-pop-2026-02 --sql build/d1/population.sql
```

The dataset labels must match `ROADS_DATASET` and `COUNTIES_DATASET` in
`wrangler.jsonc`.

## Run locally

The repo root `.envrc` sets `UV_PYTHON` to a relative path that does not exist
in this directory, so clear it first:

```bash
cd worker
unset UV_PYTHON VIRTUAL_ENV
uv sync
uv run pywrangler d1 migrations apply DB --local
for f in roads counties population; do
  uv run pywrangler d1 execute DB --local --file ../build/d1/$f.sql
done
uv run pywrangler dev
```

Then:

```bash
curl "http://localhost:8787/"
curl "http://localhost:8787/api/analysis?lat=33.732&lon=-84.4166&radius_m=75000"
curl "http://localhost:8787/api/analysis.tex?lat=33.732&lon=-84.4166&tons_per_person=4.5"
```

Optional parameters: `radius_m` (default 75000), `tons_per_person` (default
4.5) and `min_km2`, which leaves out counties with less reachable area than
the given figure.

## Tests

```bash
uv run pytest tests ../tools/ingest/tests
```

`tests/test_golden.py` compares against saved legacy results using the local
D1 database, and is skipped until that database has been built.

## Deploying

Nothing here has been deployed. Deploying needs a Workers Paid plan, a real
D1 database id in `wrangler.jsonc`, and the same `d1` commands with `--remote`.
