# rb-road-network Worker

Cloudflare Python Worker that answers road-distance reachability queries from
road tiles stored in D1. This is the spike stage: it proves the data model and
the search, and does not yet produce county or population reports.

## Layout

- `src/entry.py` — Worker entrypoint and routes
- `src/rbnet/grid.py` — the national grid (EPSG:5070, 250 m cells, 128-cell tiles)
- `src/rbnet/reach.py` — the search; pure Python, no Cloudflare imports
- `migrations/` — D1 schema
- `tests/` — engine tests, run with ordinary pytest
- `../tools/ingest/rasterize_roads.py` — local tool that turns road shapefiles into tile SQL

## Run locally

The repo root `.envrc` sets `UV_PYTHON` to a relative path that does not exist
in this directory, so clear it first:

```bash
cd worker
unset UV_PYTHON VIRTUAL_ENV
uv sync
uv run pytest

# build tiles (uses the root project's .venv, which has geopandas)
../.venv/bin/python ../tools/ingest/rasterize_roads.py \
  "$RB_DATA"/gis_osm_roads_extra/*_geom/gis_osm_roads_free_1.shp \
  --dataset spike --sql /tmp/roads.sql

uv run pywrangler d1 migrations apply DB --local
uv run pywrangler d1 execute DB --local --file /tmp/roads.sql
uv run pywrangler dev
```

Then:

```bash
curl "http://localhost:8787/reach?lat=33.732&lon=-84.4166&radius_m=75000"
```

Nothing here has been deployed. Deploying needs a Workers Paid plan, a real D1
database id in `wrangler.jsonc`, and the same two `d1` commands with `--remote`.
