# rb-road-network Worker

Cloudflare Python Worker that answers "which counties, and how many people,
are within a road distance of this point" from data stored in D1. It serves
a map page, keeps every analysis run from that page, and runs batches of
sites from a CSV.

## How it works

- Roads and county boundaries are stored as tiles on one national grid
  (EPSG:5070, 250 m cells, 128-cell tiles) in the `raster_tiles` table.
- A request loads the tiles around the start point, runs a shortest-path
  search over road cells up to the distance budget, and counts the reached
  cells in each county.
- County names and population series come from the `counties` and
  `county_population` tables, and are summarised into the report.
- Stored analyses live in the `analyses` table: the request, the full result
  and a coarse (1 km) copy of the reachable area for drawing on a map.
- A batch is a set of `analyses` rows created as `pending` from a sites CSV.
  The page then runs them one request at a time, so a batch of any size
  stays within Worker limits and can be stopped and resumed. It needs the
  page to stay open; nothing runs in the background.

## Layout

- `src/entry.py` — Worker entrypoint; the route list is at the top of the file
- `public/` — the map page (static files, served without running the Worker)
- `src/rbnet/grid.py` — the national grid and projection
- `src/rbnet/reach.py` — the search
- `src/rbnet/analysis.py` — reachability plus the per-county roll-up
- `src/rbnet/report.py` — population report and the legacy LaTeX layout
- `src/rbnet/area.py` — the stored reachable area and its GeoJSON
- `src/rbnet/params.py` — request validation, the sites CSV, the batch summary
- `migrations/` — D1 schema
- `tests/` — run with ordinary pytest; `rbnet` has no Cloudflare imports
- `../tools/ingest/` — local tools that build the SQL loaded into D1

## Build the data

The ingest tools need numpy, pyogrio and shapely, which are the `ingest`
extra of the repo root project. Output goes to `build/d1/`, which is
git-ignored.

```bash
cd ..   # repo root
uv sync --extra ingest
PY=.venv/bin/python
COUNTIES="$RB_DATA"/tl_2016_us_county/tl_2016_us_county.shp
ROADS="$RB_DATA"/gis_osm_roads_2026-11

# Download the roads layer of every state extract from Geofabrik: 50
# archives, about 7 GB fetched and 20 GB on disk. It reads only the roads
# files out of each archive, and can be run again after an interruption.
$PY tools/ingest/fetch_roads.py --out "$ROADS"

# Roads: pass every state extract for one dataset in a single run.
# --counties marks roadless tiles (open water, wilderness) in those states
# as loaded, so the Worker does not warn that data is missing there.
$PY tools/ingest/rasterize_roads.py "$ROADS"/*/gis_osm_roads_free_1.shp \
  --counties "$COUNTIES" --dataset osm-2026-11 --sql build/d1/roads.sql

# County boundaries and attributes (contiguous US).
$PY tools/ingest/rasterize_counties.py "$COUNTIES" \
  --dataset tl-2016 --sql build/d1/counties.sql

# Population. Prints which rows it corrected or could not place.
$PY tools/ingest/load_population.py \
  --counties "$COUNTIES" --csv-dir "$RB_DATA"/county_pop \
  --source county-pop-reconciled-2026-11 --sql build/d1/population.sql
```

The road extracts are the Geofabrik archives of 2026-11-10 and 2026-11-11;
`sources.json` in the download directory lists the exact archive for each
state. California comes as two extracts (`norcal`, `socal`).

### Population figures

The per-state CSVs in `$RB_DATA/county_pop` were reconciled on 2026-11-11
against the figures in the legacy county shapefile and the Census Bureau's
county estimates, using `tools/ingest/reconcile_population.py` (the rule is
described at the top of that file). The originals are in
`$RB_DATA/county_pop_backup_2026-11-11`, and
`$RB_DATA/county_population_reconciled.csv` lists every county with the
chosen figures, which source each came from, and the Census figures they
were checked against.

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

Then open <http://localhost:8787/> for the map page, or use the API:

```bash
curl "http://localhost:8787/api/status"

# Run without storing.
curl "http://localhost:8787/api/analysis?lat=33.732&lon=-84.4166&radius_m=75000"
curl "http://localhost:8787/api/analysis.tex?lat=33.732&lon=-84.4166&tons_per_person=4.5"

# Run and store; the response carries the id used by the other routes.
curl -X POST "http://localhost:8787/api/analyses" -H "content-type: application/json" \
  -d '{"label": "Atlanta", "lat": 33.732, "lon": -84.4166}'
```

Optional parameters: `radius_m` (default 75000), `tons_per_person` (default
4.5) and `min_km2`, which leaves out counties with less reachable area than
the given figure.

A sites CSV for a batch needs a header row with `site, lat, lon` (the legacy
batch format). Optional `radius_m`, `tons_per_person` and `min_km2` columns
override the batch-wide values for a row. A batch holds at most 500 sites.

## Tests

```bash
uv run pytest tests ../tools/ingest/tests
```

`tests/test_golden.py` compares against saved legacy results using the local
D1 database, and is skipped until that database has been built.

## Command-line client

`rb-road-network` in the repo root sends the same requests as the map page
and saves the report files; see the [root README](../README.md).

## Continuous integration

`.github/workflows/ci.yml` runs these tests, the command-line client's tests,
a syntax check of the map page script and a dry-run bundle of the Worker on
every push and pull request. It does not deploy.

## Deploying

State on 2026-11-11:

- **Database: done.** The D1 database `rb-road-network` exists (its id is in
  `wrangler.jsonc`), has the schema, and holds the same data as the local
  build: counties, population and roads (`osm-2026-11`) for the contiguous
  US. The earlier roads dataset `osm-2026-02` (AL, GA, NC, SC and TN only)
  is still in the database but no longer read.
- **Worker: live** at <https://rb-road-network.rockybranches.workers.dev>,
  on Workers Paid, behind Cloudflare Access. Without a sign-in every path,
  including the map page and all of `/api`, redirects to the Access login.

The API has no login of its own: anyone who can reach the Worker can run,
read and delete analyses. The steps below, all done for this deployment,
keep it unreachable until Cloudflare Access is in front of it; follow them
again for a new one.

1. Switch the account to Workers Paid (dashboard: Workers & Pages, Plans).
2. Deploy with `workers_dev` and `preview_urls` set to `false` in
   `wrangler.jsonc`, so the Worker is created with no address:

   ```bash
   uv run pywrangler deploy
   ```

3. Protect it. In the dashboard open Workers & Pages, `rb-road-network`,
   the Access tab, and select "Protect this Worker behind Access". Choose
   "All traffic" and who may sign in. This needs Zero Trust enabled on the
   account, and covers every address of the Worker, including the map page.
4. Give it an address: set `"workers_dev": true` in `wrangler.jsonc` and
   deploy again. The address is printed at the end.
5. Check it: the address should ask you to sign in, then show the map page;
   `/api/status` should list the datasets.

For the command-line client, create a service token (Zero Trust, Access
controls, Service credentials, Service Tokens) and add a policy to the
Worker's Access application with the action "Service Auth" that includes
that token. The client sends it from `RB_ACCESS_CLIENT_ID` and
`RB_ACCESS_CLIENT_SECRET`.

If Access is later switched off for this Worker, the API is open to anyone
with the address; the Worker does not check the sign-in itself.

### Updating a deployment

```bash
uv run pywrangler d1 migrations apply DB --remote                    # schema changes
uv run pywrangler d1 execute DB --remote --file ../build/d1/roads.sql   # new data
uv run pywrangler deploy                                              # code or map page
```

Load new data under a new dataset label and switch `ROADS_DATASET` or
`COUNTIES_DATASET` in `wrangler.jsonc`, so a reload never changes what live
requests read.
